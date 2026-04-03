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

import html
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
            ("meteo", self._section_meteo),
            ("repas", self._section_repas),
            ("taches_maison", self._section_taches),
            ("jules", self._section_jules),
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
    def _section_meteo(self) -> dict[str, Any]:
        """Météo du jour avec suggestion principale."""
        from src.services.utilitaires.meteo_service import obtenir_meteo_service

        meteo = obtenir_meteo_service().obtenir_meteo()
        actuelle = getattr(meteo, "actuelle", None)
        if not actuelle:
            return {}

        suggestion = None
        suggestions = getattr(meteo, "suggestions", None) or []
        if suggestions:
            suggestion = suggestions[0]

        return {
            "ville": getattr(meteo, "ville", None),
            "temperature": getattr(actuelle, "temperature", None),
            "condition": getattr(actuelle, "condition", None),
            "emoji": getattr(actuelle, "emoji", None),
            "suggestion": suggestion,
        }

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
                    "recette": (
                        getattr(getattr(r, "recette", None), "nom", None)
                        or getattr(r, "recette_nom", "")
                        or "Non précisé"
                    ),
                }
                for r in repas
            ],
        }

    @avec_gestion_erreurs(default_return={})
    def _section_jules(self) -> dict[str, Any]:
        """Résumé rapide Jules: âge et prochains jalons."""
        from src.services.famille.contexte import ContexteFamilleService
        from src.services.famille.jules import obtenir_service_jules

        service = obtenir_service_jules()
        date_naissance = service.get_date_naissance_jules()
        if not date_naissance:
            return {}

        age_mois = service.get_age_mois()
        prochains_jalons = ContexteFamilleService()._prochains_jalons_oms(age_mois)

        return {
            "age_mois": age_mois,
            "date_naissance": date_naissance.isoformat(),
            "prochains_jalons": prochains_jalons,
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

        expirant_aujourdhui = (
            db.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption == aujourd_hui,
                ArticleInventaire.quantite > 0,
            )
            .all()
        )

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
            "expirent_aujourd_hui": [
                {"nom": a.nom, "date_peremption": a.date_peremption.isoformat()}
                for a in expirant_aujourdhui[:5]
            ],
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
            resultats_push = dispatcher.envoyer(
                user_id=user_id,
                message=resume,
                titre="☀️ Briefing matinal",
                canaux=["push", "ntfy"],
            )

            message_telegram = _formater_briefing_telegram(briefing)
            resultat_telegram = dispatcher.envoyer(
                user_id=user_id,
                message=message_telegram,
                titre="☀️ Briefing matinal",
                canaux=["telegram"],
            )

            logger.info(f"✅ Briefing matinal envoyé à {user_id}")
            return {
                "briefing": briefing,
                "notification": {
                    "push_ntfy": resultats_push,
                    "telegram": resultat_telegram,
                },
            }

        except Exception as e:
            logger.warning(f"Envoi briefing notification échoué: {e}")
            return {"briefing": briefing, "notification": None}


def _formater_sections(sections: dict[str, Any]) -> str:
    """Formate les sections en texte lisible pour le prompt IA."""
    parties = []

    if "meteo" in sections:
        meteo = sections["meteo"]
        condition = meteo.get("condition") or "variable"
        temperature = meteo.get("temperature")
        emoji = meteo.get("emoji") or "🌤️"
        if temperature is not None:
            parties.append(f"{emoji} Météo du jour : {condition}, {temperature}°C")
        else:
            parties.append(f"{emoji} Météo du jour : {condition}")

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

    if "jules" in sections:
        jules = sections["jules"]
        age_mois = jules.get("age_mois")
        jalons = jules.get("prochains_jalons") or []
        if age_mois is not None and jalons:
            parties.append(f"👶 Jules : {age_mois} mois, prochain jalon probable — {jalons[0]}")
        elif age_mois is not None:
            parties.append(f"👶 Jules : {age_mois} mois")

    if "inventaire_alertes" in sections:
        aujourd_hui = sections["inventaire_alertes"].get("expirent_aujourd_hui", [])
        expirants = sections["inventaire_alertes"].get("expirent_sous_48h", [])
        if aujourd_hui:
            noms = ", ".join(a["nom"] for a in aujourd_hui[:4])
            parties.append(f"🥕 À consommer aujourd'hui : {noms}")
        elif expirants:
            noms = ", ".join(a["nom"] for a in expirants[:3])
            parties.append(f"⚠️ Produits expirant sous 48h : {noms}")

    return "\n".join(parties) if parties else "Rien de particulier à signaler."


def _formater_briefing_telegram(briefing: dict[str, Any]) -> str:
    """Construit un message Telegram structuré à partir du briefing."""
    sections = briefing.get("sections", {})
    resume = str(briefing.get("resume_narratif", "") or "").strip()
    corps = _formater_sections(sections)

    lignes = ["☀️ <b>Briefing matinal</b>"]
    if corps:
        lignes.append("")
        lignes.append(html.escape(corps))
    if resume:
        lignes.append("")
        lignes.append(f"<i>{html.escape(resume)}</i>")

    return "\n".join(lignes)


@service_factory("briefing_matinal", tags={"outils", "ia", "notifications", "inter_module"})
def obtenir_service_briefing_matinal() -> BriefingMatinalService:
    """Factory pour le service Briefing Matinal IA."""
    return BriefingMatinalService()
