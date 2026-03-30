"""
Service d'envoi d'emails transactionnels via Resend.

Fonctionnalités :
- Reset de mot de passe
- Vérification d'email à l'inscription
- Résumé hebdomadaire famille
- Rapport mensuel budget
- Alerte critique (stock nul, péremption urgente)
- Invitation d'un autre membre famille
- Digest de notifications

Templates Jinja2 dans le dossier templates/ adjacent.

Dépendance : `pip install resend` + `RESEND_API_KEY` dans `.env.local`
"""

import logging
import os
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# ───── Constantes ──────────────────────────────────────────────────────────────

_FROM_DEFAULT = "matanne@noreply.exemple.fr"
_APP_URL_DEFAULT = "http://localhost:3000"
_TEMPLATES_DIR = Path(__file__).parent / "templates"


# ───── Service ─────────────────────────────────────────────────────────────────


class ServiceEmail:
    """Envoi d'emails transactionnels via Resend avec templates Jinja2."""

    def __init__(self) -> None:
        self._api_key = os.getenv("RESEND_API_KEY", "")
        self._from_addr = os.getenv("EMAIL_FROM", _FROM_DEFAULT)
        self._app_url = os.getenv("NEXT_PUBLIC_API_URL", _APP_URL_DEFAULT).rstrip("/")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self._app_url = frontend_url
        self._jinja_env = Environment(
            loader=FileSystemLoader(str(_TEMPLATES_DIR)),
            autoescape=select_autoescape(["html"]),
        )

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

    def _render(self, template_name: str, **kwargs: Any) -> str:
        """Rend un template Jinja2 avec les variables données."""
        template = self._jinja_env.get_template(template_name)
        return template.render(**kwargs)

    # ─── Méthodes publiques ────────────────────────────────────────────────────

    def envoyer_reset_password(self, email: str, token: str) -> bool:
        """Envoie un lien de réinitialisation de mot de passe."""
        lien = f"{self._app_url}/auth/reset-password?token={token}"
        html = self._render(
            "reset_password.html",
            sujet="Réinitialisation mot de passe",
            lien=lien,
        )
        return self._envoyer(email, "Réinitialisation de votre mot de passe — Matanne", html)

    def envoyer_verification_email(self, email: str, token: str) -> bool:
        """Envoie un email de vérification à l'inscription."""
        lien = f"{self._app_url}/auth/verify-email?token={token}"
        html = self._render(
            "verification_email.html",
            sujet="Vérification email",
            lien=lien,
        )
        return self._envoyer(email, "Vérifiez votre email — Matanne", html)

    def envoyer_resume_hebdo(self, email: str, resume: dict[str, Any]) -> bool:
        """Envoie le résumé hebdomadaire famille."""
        semaine = resume.get("semaine", "")
        html = self._render(
            "resume_hebdo.html",
            sujet=f"Résumé semaine {semaine}",
            semaine=semaine,
            recettes_cuisinees=resume.get("recettes_cuisinees"),
            budget_depense=resume.get("budget_depense"),
            activites_jules=resume.get("activites_jules"),
            taches_maison=resume.get("taches_maison"),
            resume_ia=resume.get("resume_ia", ""),
        )
        return self._envoyer(email, f"📋 Résumé de la semaine {semaine} — Matanne", html)

    def envoyer_rapport_mensuel(self, email: str, rapport: dict[str, Any]) -> bool:
        """Envoie le rapport mensuel budget."""
        mois = rapport.get("mois", "")
        total = rapport.get("total_depenses", 0)
        budget = rapport.get("budget_prevu", 0)
        ecart = total - budget
        html = self._render(
            "rapport_mensuel.html",
            sujet=f"Rapport mensuel {mois}",
            mois=mois,
            total_depenses=total,
            budget_prevu=budget,
            ecart=ecart,
            categories=rapport.get("categories", []),
        )
        return self._envoyer(email, f"📊 Rapport mensuel {mois} — Matanne", html)

    def envoyer_alerte_critique(self, email: str, alerte: dict[str, Any]) -> bool:
        """Envoie une alerte critique (stock nul, péremption urgente, garantie expirée)."""
        titre = alerte.get("titre", "Alerte importante")
        message = alerte.get("message", "")
        lien = alerte.get("lien", self._app_url)
        html = self._render(
            "alerte_critique.html",
            sujet=titre,
            titre=titre,
            message=message,
            lien=lien,
        )
        return self._envoyer(email, f"⚠️ {titre} — Matanne", html)

    def envoyer_invitation_famille(self, email: str, invitant: str) -> bool:
        """Envoie une invitation à rejoindre le compte famille."""
        lien = f"{self._app_url}/auth/register?ref=invitation"
        html = self._render(
            "invitation_famille.html",
            sujet="Invitation famille",
            invitant=invitant,
            lien=lien,
        )
        return self._envoyer(email, f"Invitation de {invitant} — Matanne", html)

    def envoyer_digest(self, email: str, notifications: list[dict[str, Any]]) -> bool:
        """Envoie un digest de notifications groupées."""
        html = self._render(
            "digest.html",
            sujet="Digest notifications",
            notifications=notifications,
        )
        return self._envoyer(email, "🔔 Vos notifications — Matanne", html)


# ─── Factory ───────────────────────────────────────────────────────────────────


@service_factory("service_email", tags={"notifications", "email"})
def get_service_email() -> ServiceEmail:
    """Retourne le singleton ServiceEmail."""
    return ServiceEmail()
