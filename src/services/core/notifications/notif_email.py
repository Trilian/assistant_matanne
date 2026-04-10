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

import base64
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Any

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape

    JINJA2_DISPONIBLE = True
except ImportError:
    Environment = None  # type: ignore[assignment]
    FileSystemLoader = None  # type: ignore[assignment]
    JINJA2_DISPONIBLE = False

    def select_autoescape(*_args: Any, **_kwargs: Any) -> bool:
        """Fallback minimal quand Jinja2 n'est pas disponible."""
        return False


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
        self._jinja_env: Any | None = None

        if JINJA2_DISPONIBLE and Environment is not None and FileSystemLoader is not None:
            self._jinja_env = Environment(
                loader=FileSystemLoader(str(_TEMPLATES_DIR)),
                autoescape=select_autoescape(["html"]),
            )
        else:
            logger.warning("Jinja2 non installé : fallback HTML minimal activé pour les emails.")

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

    def _envoyer(
        self,
        to: str,
        subject: str,
        html: str,
        attachments: list[dict[str, str]] | None = None,
    ) -> bool:
        """Envoie un email et retourne True si succès."""
        try:
            client = self._client()
            payload: dict[str, Any] = {
                "from": self._from_addr,
                "to": [to],
                "subject": subject,
                "html": html,
            }
            if attachments:
                payload["attachments"] = attachments

            client.Emails.send(payload)
            logger.info("Email '%s' envoyé à %s", subject, to)
            return True
        except RuntimeError as e:
            logger.warning("Email non envoyé (config manquante) : %s", e)
            return False
        except Exception as e:
            logger.error("Erreur envoi email '%s' à %s : %s", subject, to, e)
            return False

    def _render_fallback_html(self, **kwargs: Any) -> str:
        """Construit un HTML minimal si Jinja2 n'est pas disponible."""
        sujet = str(kwargs.get("sujet", "Notification Matanne"))
        lignes: list[str] = []
        for cle, valeur in kwargs.items():
            if cle == "sujet" or valeur in (None, "", [], {}):
                continue
            libelle = cle.replace("_", " ").capitalize()
            lignes.append(f"<li><strong>{libelle} :</strong> {valeur}</li>")

        contenu = "\n".join(lignes) if lignes else "<li>Aucun détail supplémentaire.</li>"
        return f"""
        <html>
          <body style=\"font-family: Arial, sans-serif; line-height: 1.5;\">
            <h2>{sujet}</h2>
            <ul>{contenu}</ul>
          </body>
        </html>
        """

    def _render(self, template_name: str, **kwargs: Any) -> str:
        """Rend un template Jinja2 avec les variables données."""
        if self._jinja_env is None:
            logger.warning(
                "Template %s rendu sans Jinja2 ; utilisation du fallback HTML minimal.",
                template_name,
            )
            return self._render_fallback_html(**kwargs)

        try:
            template = self._jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as exc:
            logger.warning(
                "Impossible de rendre le template %s (%s) ; fallback HTML utilisé.",
                template_name,
                exc,
            )
            return self._render_fallback_html(**kwargs)

    def _render_mjml(self, template_name: str, fallback_html_template: str, **kwargs: Any) -> str:
        """Rend un template MJML puis le compile en HTML.

        Si le compilateur MJML n'est pas disponible, fallback sur un template HTML.
        """
        try:
            mjml_source = self._render(template_name, **kwargs)
            try:
                from mjml import mjml2html  # type: ignore

                result = mjml2html(mjml_source)
                if isinstance(result, dict):
                    html = str(result.get("html", "")).strip()
                else:
                    html = str(result).strip()

                if html:
                    return html
            except Exception:
                logger.warning(
                    "Compilation MJML indisponible, fallback HTML pour %s", template_name
                )
        except Exception:
            logger.warning("Template MJML introuvable ou invalide: %s", template_name)

        return self._render(fallback_html_template, **kwargs)

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
        """Envoie le résumé hebdomadaire famille (MJML avec fallback HTML)."""
        semaine = resume.get("semaine", "")
        ctx = dict(
            sujet=f"Résumé semaine {semaine}",
            semaine=semaine,
            recettes_cuisinees=resume.get("recettes_cuisinees"),
            budget_depense=resume.get("budget_depense"),
            activites_jules=resume.get("activites_jules"),
            taches_maison=resume.get("taches_maison"),
            resume_ia=resume.get("resume_ia", ""),
            app_url=self._app_url,
        )
        html = self._render_mjml(
            "resume_hebdo.mjml",
            fallback_html_template="resume_hebdo.html",
            **ctx,
        )
        return self._envoyer(email, f"📋 Résumé de la semaine {semaine} — Matanne", html)

    def envoyer_rapport_mensuel(self, email: str, rapport: dict[str, Any]) -> bool:
        """Envoie le rapport mensuel budget."""
        mois = rapport.get("mois", "")
        total = rapport.get("total_depenses", 0)
        budget = rapport.get("budget_prevu", 0)
        ecart = total - budget
        html = self._render_mjml(
            "rapport_mensuel.mjml",
            fallback_html_template="rapport_mensuel.html",
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

    def _generer_pdf_simple(self, titre: str, sections: list[tuple[str, str]]) -> bytes:
        """Génère un PDF textuel léger en mémoire pour les rapports email."""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        largeur, hauteur = A4
        y = hauteur - 2 * cm

        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, y, titre)
        y -= 1.0 * cm

        c.setFont("Helvetica", 10)
        for nom_section, contenu in sections:
            if y < 3 * cm:
                c.showPage()
                y = hauteur - 2 * cm
                c.setFont("Helvetica", 10)

            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y, nom_section)
            y -= 0.6 * cm

            c.setFont("Helvetica", 10)
            for ligne in (contenu or "").split("\n")[:25]:
                if y < 2.5 * cm:
                    c.showPage()
                    y = hauteur - 2 * cm
                    c.setFont("Helvetica", 10)
                c.drawString(2.3 * cm, y, ligne[:110])
                y -= 0.45 * cm
            y -= 0.4 * cm

        c.save()
        return buffer.getvalue()

    def envoyer_rapport_famille_mensuel_complet(self, email: str, rapport: dict[str, Any]) -> bool:
        """Rapport famille — Email mensuel famille avec PDF joint."""
        mois = str(rapport.get("mois", ""))
        html = self._render(
            "rapport_famille_mensuel_complet.html",
            sujet=f"Rapport famille complet {mois}",
            mois=mois,
            budget=rapport.get("budget", "Non disponible"),
            nutrition=rapport.get("nutrition", "Non disponible"),
            maison=rapport.get("maison", "Non disponible"),
            jardin=rapport.get("jardin", "Non disponible"),
            jules=rapport.get("jules", "Non disponible"),
        )

        pdf_bytes = self._generer_pdf_simple(
            titre=f"Rapport famille mensuel — {mois}",
            sections=[
                ("Budget", str(rapport.get("budget", "Non disponible"))),
                ("Nutrition", str(rapport.get("nutrition", "Non disponible"))),
                ("Maison", str(rapport.get("maison", "Non disponible"))),
                ("Jardin", str(rapport.get("jardin", "Non disponible"))),
                ("Jules", str(rapport.get("jules", "Non disponible"))),
            ],
        )
        attachment = {
            "filename": f"rapport-famille-{mois or 'mensuel'}.pdf",
            "content": base64.b64encode(pdf_bytes).decode("ascii"),
        }
        return self._envoyer(
            email,
            f"📦 Rapport famille complet {mois} — Matanne",
            html,
            attachments=[attachment],
        )

    def envoyer_rapport_maison_trimestriel(self, email: str, rapport: dict[str, Any]) -> bool:
        """Rapport maison — Email trimestriel maison avec PDF joint."""
        trimestre = str(rapport.get("trimestre", ""))
        html = self._render(
            "rapport_maison_trimestriel.html",
            sujet=f"Rapport maison trimestriel {trimestre}",
            trimestre=trimestre,
            projets=rapport.get("projets", "Non disponible"),
            energie=rapport.get("energie", "Non disponible"),
            jardin=rapport.get("jardin", "Non disponible"),
            entretien=rapport.get("entretien", "Non disponible"),
        )

        pdf_bytes = self._generer_pdf_simple(
            titre=f"Rapport maison trimestriel — {trimestre}",
            sections=[
                ("Projets", str(rapport.get("projets", "Non disponible"))),
                ("Energie", str(rapport.get("energie", "Non disponible"))),
                ("Jardin", str(rapport.get("jardin", "Non disponible"))),
                ("Entretien", str(rapport.get("entretien", "Non disponible"))),
            ],
        )
        attachment = {
            "filename": f"rapport-maison-{trimestre or 'trimestriel'}.pdf",
            "content": base64.b64encode(pdf_bytes).decode("ascii"),
        }
        return self._envoyer(
            email,
            f"🏡 Rapport maison trimestriel {trimestre} — Matanne",
            html,
            attachments=[attachment],
        )

    def envoyer_confirmation_backup(self, email: str, backup: dict[str, Any]) -> bool:
        """Envoie un email de confirmation après un backup automatique réussi."""
        date_backup = str(backup.get("date", ""))
        filename = str(backup.get("filename", ""))
        total_rows = backup.get("total_rows", 0)
        tables_sauvegardees = backup.get("tables_count", 0)
        taille_fichier = str(backup.get("taille_fichier", ""))

        html = self._render(
            "confirmation_backup.html",
            sujet="Confirmation backup automatique",
            date_backup=date_backup,
            filename=filename,
            total_rows=total_rows,
            tables_sauvegardees=tables_sauvegardees,
            taille_fichier=taille_fichier,
        )
        return self._envoyer(email, f"💾 Backup confirmé {date_backup} — Matanne", html)

    def envoyer_rapport_mensuel_unifie(self, email: str, rapport: dict[str, Any]) -> bool:
        """Rapport unifié — Envoie le PDF mensuel unifié généré par le service innovations."""
        mois_reference = str(rapport.get("mois_reference", ""))
        filename = str(rapport.get("filename", f"rapport_mensuel_{mois_reference or 'unifie'}.pdf"))
        contenu_base64 = str(rapport.get("contenu_base64", ""))

        if not contenu_base64:
            logger.warning("Rapport mensuel unifié: contenu_base64 manquant")
            return False

        html = f"""
        <html>
          <body style=\"font-family: Arial, sans-serif; line-height: 1.5;\">
            <h2>Rapport mensuel unifié {mois_reference}</h2>
            <p>Votre rapport mensuel consolidé (famille, budget, nutrition, maison, jardin, Jules) est prêt.</p>
            <p>Le PDF est joint à cet email.</p>
          </body>
        </html>
        """

        attachment = {
            "filename": filename,
            "content": contenu_base64,
        }
        return self._envoyer(
            email,
            f"📘 Rapport mensuel unifié {mois_reference} — Matanne",
            html,
            attachments=[attachment],
        )


# ─── Factory ───────────────────────────────────────────────────────────────────


@service_factory("service_email", tags={"notifications", "email"})
def get_service_email() -> ServiceEmail:
    """Retourne le singleton ServiceEmail."""
    return ServiceEmail()
