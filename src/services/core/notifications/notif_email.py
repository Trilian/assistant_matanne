"""
Service d'envoi d'emails transactionnels via Resend.

Fonctionnalités :
- Reset de mot de passe
- Vérification d'email à l'inscription
- Résumé hebdomadaire famille
- Rapport mensuel budget
- Alerte critique (stock nul, péremption urgente)
- Invitation d'un autre membre famille

Dépendance : `pip install resend` + `RESEND_API_KEY` dans `.env.local`
"""

import logging
import os
from typing import Any

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# ───── Constantes ──────────────────────────────────────────────────────────────

_FROM_DEFAULT = "matanne@noreply.exemple.fr"
_APP_URL_DEFAULT = "http://localhost:3000"


# ───── Service ─────────────────────────────────────────────────────────────────


class ServiceEmail:
    """Envoi d'emails transactionnels via Resend."""

    def __init__(self) -> None:
        self._api_key = os.getenv("RESEND_API_KEY", "")
        self._from_addr = os.getenv("EMAIL_FROM", _FROM_DEFAULT)
        self._app_url = os.getenv("NEXT_PUBLIC_API_URL", _APP_URL_DEFAULT).rstrip("/")
        # Remplacer l'URL backend par le frontend si nécessaire
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self._app_url = frontend_url

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def _client(self):
        """Retourne le module resend initialisé (lazy import)."""
        try:
            import resend  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Le package 'resend' n'est pas installé. Exécutez : pip install resend"
            ) from exc

        if not self._api_key:
            raise RuntimeError(
                "Variable d'environnement RESEND_API_KEY manquante. "
                "Ajoutez-la dans .env.local pour activer l'envoi d'emails."
            )

        resend.api_key = self._api_key
        return resend

    def _envoyer(self, to: str, subject: str, html: str) -> bool:
        """Envoie un email et retourne True si succès."""
        try:
            client = self._client()
            client.Emails.send({
                "from": self._from_addr,
                "to": [to],
                "subject": subject,
                "html": html,
            })
            logger.info("Email '%s' envoyé à %s", subject, to)
            return True
        except RuntimeError as e:
            logger.warning("Email non envoyé (config manquante) : %s", e)
            return False
        except Exception as e:
            logger.error("Erreur envoi email '%s' à %s : %s", subject, to, e)
            return False

    # ─── Méthodes publiques ────────────────────────────────────────────────────

    def envoyer_reset_password(self, email: str, token: str) -> bool:
        """Envoie un lien de réinitialisation de mot de passe."""
        lien = f"{self._app_url}/auth/reset-password?token={token}"
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto">
          <h2>Réinitialisation de votre mot de passe</h2>
          <p>Vous avez demandé à réinitialiser votre mot de passe pour Assistant Matanne.</p>
          <p>
            <a href="{lien}" style="background:#2563eb;color:#fff;padding:10px 20px;
               border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0">
              Réinitialiser mon mot de passe
            </a>
          </p>
          <p style="color:#666;font-size:13px">
            Ce lien expire dans 30 minutes. Si vous n'avez pas fait cette demande, ignorez cet email.
          </p>
          <p style="color:#666;font-size:12px">Lien : {lien}</p>
        </div>
        """
        return self._envoyer(email, "Réinitialisation de votre mot de passe — Matanne", html)

    def envoyer_verification_email(self, email: str, token: str) -> bool:
        """Envoie un email de vérification à l'inscription."""
        lien = f"{self._app_url}/auth/verify-email?token={token}"
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto">
          <h2>Vérifiez votre adresse email</h2>
          <p>Bienvenue sur Assistant Matanne ! Cliquez sur le lien ci-dessous pour confirmer votre email.</p>
          <p>
            <a href="{lien}" style="background:#16a34a;color:#fff;padding:10px 20px;
               border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0">
              Vérifier mon email
            </a>
          </p>
          <p style="color:#666;font-size:13px">Ce lien expire dans 24 heures.</p>
        </div>
        """
        return self._envoyer(email, "Vérifiez votre email — Matanne", html)

    def envoyer_resume_hebdo(self, email: str, resume: dict[str, Any]) -> bool:
        """Envoie le résumé hebdomadaire famille."""
        semaine = resume.get("semaine", "")
        lignes = []
        if resume.get("recettes_cuisinees"):
            lignes.append(f"<li>🍽️ {resume['recettes_cuisinees']} recettes cuisinées</li>")
        if resume.get("budget_depense") is not None:
            lignes.append(f"<li>💰 Budget dépensé : {resume['budget_depense']:.2f} €</li>")
        if resume.get("activites_jules"):
            lignes.append(f"<li>👶 {resume['activites_jules']} activités avec Jules</li>")
        if resume.get("taches_maison"):
            lignes.append(f"<li>🏡 {resume['taches_maison']} tâches maison effectuées</li>")
        contenu_liste = "".join(lignes) or "<li>Aucune donnée cette semaine</li>"
        texte_ia = resume.get("resume_ia", "")

        html = f"""
        <div style="font-family:sans-serif;max-width:560px;margin:auto">
          <h2>📋 Résumé de la semaine {semaine}</h2>
          <ul style="line-height:1.8">{contenu_liste}</ul>
          {f'<blockquote style="border-left:3px solid #2563eb;padding-left:12px;color:#444">{texte_ia}</blockquote>' if texte_ia else ""}
          <p style="color:#999;font-size:12px;margin-top:24px">
            Vous recevez cet email car vous êtes abonné aux résumés hebdo sur Matanne.
          </p>
        </div>
        """
        return self._envoyer(email, f"📋 Résumé de la semaine {semaine} — Matanne", html)

    def envoyer_rapport_mensuel(self, email: str, rapport: dict[str, Any]) -> bool:
        """Envoie le rapport mensuel budget."""
        mois = rapport.get("mois", "")
        total = rapport.get("total_depenses", 0)
        budget = rapport.get("budget_prevu", 0)
        ecart = total - budget
        couleur_ecart = "#dc2626" if ecart > 0 else "#16a34a"

        html = f"""
        <div style="font-family:sans-serif;max-width:560px;margin:auto">
          <h2>📊 Rapport mensuel — {mois}</h2>
          <table style="width:100%;border-collapse:collapse;margin:16px 0">
            <tr style="background:#f3f4f6">
              <td style="padding:8px">Budget prévu</td>
              <td style="padding:8px;text-align:right"><b>{budget:.2f} €</b></td>
            </tr>
            <tr>
              <td style="padding:8px">Total dépensé</td>
              <td style="padding:8px;text-align:right"><b>{total:.2f} €</b></td>
            </tr>
            <tr style="background:#f3f4f6">
              <td style="padding:8px">Écart</td>
              <td style="padding:8px;text-align:right;color:{couleur_ecart}">
                <b>{"+" if ecart >= 0 else ""}{ecart:.2f} €</b>
              </td>
            </tr>
          </table>
          <p style="color:#999;font-size:12px">Rapport généré automatiquement par Matanne.</p>
        </div>
        """
        return self._envoyer(email, f"📊 Rapport mensuel {mois} — Matanne", html)

    def envoyer_alerte_critique(self, email: str, alerte: dict[str, Any]) -> bool:
        """Envoie une alerte critique (stock nul, péremption urgente, garantie expirée)."""
        titre = alerte.get("titre", "Alerte importante")
        message = alerte.get("message", "")
        lien = alerte.get("lien", self._app_url)

        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto">
          <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:16px;margin-bottom:16px">
            <h2 style="color:#dc2626;margin:0 0 8px">⚠️ {titre}</h2>
            <p style="margin:0;color:#7f1d1d">{message}</p>
          </div>
          <a href="{lien}" style="background:#dc2626;color:#fff;padding:10px 20px;
             border-radius:6px;text-decoration:none;display:inline-block">
            Voir les détails
          </a>
          <p style="color:#999;font-size:12px;margin-top:16px">Alerte automatique Matanne.</p>
        </div>
        """
        return self._envoyer(email, f"⚠️ {titre} — Matanne", html)

    def envoyer_invitation_famille(self, email: str, invitant: str) -> bool:
        """Envoie une invitation à rejoindre le compte famille."""
        lien = f"{self._app_url}/auth/register?ref=invitation"
        html = f"""
        <div style="font-family:sans-serif;max-width:480px;margin:auto">
          <h2>👨‍👩‍👧 Invitation à rejoindre Matanne</h2>
          <p><b>{invitant}</b> vous invite à rejoindre son espace famille sur Assistant Matanne.</p>
          <p>
            <a href="{lien}" style="background:#7c3aed;color:#fff;padding:10px 20px;
               border-radius:6px;text-decoration:none;display:inline-block;margin:16px 0">
              Accepter l'invitation
            </a>
          </p>
          <p style="color:#666;font-size:13px">
            Si vous ne connaissez pas {invitant}, vous pouvez ignorer cet email.
          </p>
        </div>
        """
        return self._envoyer(email, f"Invitation de {invitant} — Matanne", html)


# ─── Factory ───────────────────────────────────────────────────────────────────


@service_factory("service_email", tags={"notifications", "email"})
def get_service_email() -> ServiceEmail:
    """Retourne le singleton ServiceEmail."""
    return ServiceEmail()
