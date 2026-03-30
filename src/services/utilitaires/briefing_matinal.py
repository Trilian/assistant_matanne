"""
Service Briefing Matinal IA — Digest quotidien personnalisé.

IM-P2-5: Chaque matin à 7h → digest personnalisé résumant :
- Météo du jour
- Repas planifiés
- Tâches maison
- Rappels (anniversaires, documents)
- Résumé budget
- Infos Jules

Configurable on/off par utilisateur (ne plaira pas forcément à tout le monde).
"""

import logging
from datetime import date, timedelta
from typing import Any

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BriefingMatinalService(BaseAIService):
    """Service de briefing matinal IA personnalisé."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="briefing_matinal",
            default_ttl=3600,
            service_name="briefing_matinal",
        )

    @avec_gestion_erreurs(default_return={})
    def generer_briefing(self, user_id: str = "matanne") -> dict[str, Any]:
        """Génère le briefing matinal complet.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Dict avec sections du briefing + résumé narratif IA
        """
        sections: dict[str, Any] = {}

        # Collecter les données de chaque section
        collecteurs = [
            ("repas", self._section_repas),
            ("taches_maison", self._section_taches),
            ("anniversaires", self._section_anniversaires),
            ("documents", self._section_documents),
            ("budget", self._section_budget),
            ("inventaire_alertes", self._section_inventaire),
        ]

        for nom, collecteur in collecteurs:
            try:
                resultat = collecteur()
                if resultat:
                    sections[nom] = resultat
            except Exception as e:
                logger.debug(f"Section briefing {nom} non disponible: {e}")

        # Générer le résumé narratif IA
        resume_ia = self._generer_resume_narratif(sections)

        briefing = {
            "date": date.today().isoformat(),
            "sections": sections,
            "resume_narratif": resume_ia,
            "user_id": user_id,
        }

        logger.info(f"✅ Briefing matinal généré: {len(sections)} section(s)")
        return briefing

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_repas(self, *, db=None) -> dict[str, Any]:
        """Repas prévus aujourd'hui."""
        from src.core.models import Repas

        aujourd_hui = date.today()
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas == aujourd_hui)
            .all()
        )

        if not repas:
            return {"message": "Aucun repas planifié aujourd'hui"}

        return {
            "repas_du_jour": [
                {
                    "type": getattr(r, "type_repas", "repas"),
                    "recette": getattr(r, "recette_nom", "") or "Non précisé",
                }
                for r in repas
            ],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_taches(self, *, db=None) -> dict[str, Any]:
        """Tâches d'entretien maison prévues aujourd'hui."""
        from src.core.models.maison import TacheEntretien

        aujourd_hui = date.today()

        try:
            taches = (
                db.query(TacheEntretien)
                .filter(
                    TacheEntretien.date_prevue == aujourd_hui,
                    TacheEntretien.statut != "termine",
                )
                .all()
            )

            if not taches:
                return {}

            return {
                "taches_du_jour": [
                    {"nom": t.nom, "priorite": getattr(t, "priorite", None)}
                    for t in taches[:10]
                ],
            }
        except Exception:
            return {}

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_anniversaires(self, *, db=None) -> dict[str, Any]:
        """Anniversaires dans les 7 prochains jours."""
        from src.core.models import AnniversaireFamille

        tous = db.query(AnniversaireFamille).all()
        prochains = []

        for anniv in tous:
            jours = getattr(anniv, "jours_restants", None)
            if jours is not None and 0 <= jours <= 7:
                prochains.append({
                    "nom": anniv.nom,
                    "jours_restants": jours,
                    "age": getattr(anniv, "age", None),
                })

        if not prochains:
            return {}

        return {
            "anniversaires_proches": sorted(prochains, key=lambda a: a["jours_restants"]),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_documents(self, *, db=None) -> dict[str, Any]:
        """Documents expirant sous 30 jours."""
        from src.core.models import DocumentFamille

        aujourd_hui = date.today()
        limite = aujourd_hui + timedelta(days=30)

        docs = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= limite,
            )
            .all()
        )

        if not docs:
            return {}

        return {
            "documents_a_renouveler": [
                {"nom": d.nom, "jours_restants": (d.date_expiration - aujourd_hui).days}
                for d in docs
                if d.date_expiration
            ],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_budget(self, *, db=None) -> dict[str, Any]:
        """Résumé budget du mois en cours."""
        from sqlalchemy import extract, func
        from src.core.models import BudgetFamille

        aujourd_hui = date.today()

        total = (
            db.query(func.sum(BudgetFamille.montant))
            .filter(
                extract("month", BudgetFamille.date) == aujourd_hui.month,
                extract("year", BudgetFamille.date) == aujourd_hui.year,
            )
            .scalar()
        )

        if not total:
            return {}

        return {
            "total_mois": round(float(total), 2),
            "jour_du_mois": aujourd_hui.day,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _section_inventaire(self, *, db=None) -> dict[str, Any]:
        """Alertes inventaire (péremptions imminentes, stocks bas)."""
        from src.core.models import ArticleInventaire

        aujourd_hui = date.today()
        seuil = aujourd_hui + timedelta(days=2)

        expirants = (
            db.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= seuil,
                ArticleInventaire.date_peremption >= aujourd_hui,
                ArticleInventaire.quantite > 0,
            )
            .all()
        )

        if not expirants:
            return {}

        return {
            "expirent_sous_48h": [
                {"nom": a.nom, "date_peremption": a.date_peremption.isoformat()}
                for a in expirants[:5]
            ],
        }

    def _generer_resume_narratif(self, sections: dict[str, Any]) -> str:
        """Génère un résumé narratif IA à partir des sections collectées."""
        if not sections:
            return "Bonne journée ! Rien de particulier à signaler aujourd'hui. 🌤️"

        prompt = f"""Voici les informations de la journée pour une famille française :

{_formater_sections(sections)}

Génère un briefing matinal chaleureux et concis (3-5 phrases max).
Mentionne les points importants (repas, tâches, anniversaires, alertes).
Utilise un ton amical avec quelques emojis. Reste pratique et actionnable.
Termine par un petit mot d'encouragement."""

        system_prompt = (
            "Tu es un assistant familial bienveillant. Tu rédiges un briefing matinal "
            "concis et chaleureux pour aider une famille à bien organiser sa journée. "
            "Sois pratique : mentionne les actions concrètes à faire."
        )

        try:
            reponse = self.call_with_cache_sync(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=400,
            )
            return reponse or "Bonne journée ! 🌤️"
        except Exception as e:
            logger.warning(f"Génération résumé narratif échouée: {e}")
            return "Bonne journée ! 🌤️"

    def envoyer_briefing_notification(
        self, user_id: str = "matanne"
    ) -> dict[str, Any]:
        """Génère le briefing et l'envoie via notifications.

        Args:
            user_id: ID de l'utilisateur

        Returns:
            Dict avec briefing + résultats d'envoi
        """
        briefing = self.generer_briefing(user_id)
        resume = briefing.get("resume_narratif", "")

        if not resume:
            return {"briefing": briefing, "notification": None}

        try:
            from src.services.core.notifications.notif_dispatcher import (
                get_dispatcher_notifications,
            )

            dispatcher = get_dispatcher_notifications()
            resultats = dispatcher.envoyer(
                user_id=user_id,
                message=resume,
                titre="☀️ Briefing matinal",
                canaux=["push", "ntfy"],
            )

            logger.info(f"✅ Briefing matinal envoyé à {user_id}")
            return {"briefing": briefing, "notification": resultats}

        except Exception as e:
            logger.warning(f"Envoi briefing notification échoué: {e}")
            return {"briefing": briefing, "notification": None}


def _formater_sections(sections: dict[str, Any]) -> str:
    """Formate les sections en texte lisible pour le prompt IA."""
    parties = []

    if "repas" in sections:
        repas = sections["repas"]
        if "repas_du_jour" in repas:
            repas_txt = ", ".join(
                f"{r.get('type', 'repas')}: {r.get('recette', '?')}"
                for r in repas["repas_du_jour"]
            )
            parties.append(f"🍽️ Repas prévus : {repas_txt}")
        elif "message" in repas:
            parties.append(f"🍽️ {repas['message']}")

    if "taches_maison" in sections:
        taches = sections["taches_maison"].get("taches_du_jour", [])
        if taches:
            noms = ", ".join(t["nom"] for t in taches[:5])
            parties.append(f"🏠 Tâches maison : {noms}")

    if "anniversaires" in sections:
        annivs = sections["anniversaires"].get("anniversaires_proches", [])
        for a in annivs:
            if a["jours_restants"] == 0:
                parties.append(f"🎂 Aujourd'hui c'est l'anniversaire de {a['nom']} !")
            else:
                parties.append(f"🎂 Anniversaire de {a['nom']} dans {a['jours_restants']} jour(s)")

    if "documents" in sections:
        docs = sections["documents"].get("documents_a_renouveler", [])
        if docs:
            noms = ", ".join(f"{d['nom']} (J-{d['jours_restants']})" for d in docs[:3])
            parties.append(f"📋 Documents à renouveler : {noms}")

    if "budget" in sections:
        budget = sections["budget"]
        if "total_mois" in budget:
            parties.append(f"💰 Budget du mois : {budget['total_mois']}€ dépensés (jour {budget.get('jour_du_mois', '?')})")

    if "inventaire_alertes" in sections:
        expirants = sections["inventaire_alertes"].get("expirent_sous_48h", [])
        if expirants:
            noms = ", ".join(a["nom"] for a in expirants[:3])
            parties.append(f"⚠️ Produits expirant sous 48h : {noms}")

    return "\n".join(parties) if parties else "Rien de particulier à signaler."


@service_factory("briefing_matinal", tags={"outils", "ia", "notifications", "inter_module"})
def obtenir_service_briefing_matinal() -> BriefingMatinalService:
    """Factory pour le service Briefing Matinal IA."""
    return BriefingMatinalService()
