"""
Service inter-modules : Chat IA → Contexte multi-module.

Le chat IA connaît le contenu du frigo, le planning repas,
les courses en cours, le budget, la météo, les infos de Jules,
et les événements à venir pour fournir des réponses contextuelles.
"""

import logging
from datetime import date, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ChatContexteMultiModuleService:
    """Agrège le contexte de tous les modules pour enrichir le chat IA."""

    @avec_gestion_erreurs(default_return={})
    def collecter_contexte_complet(self) -> dict[str, Any]:
        """Collecte le contexte de tous les modules disponibles.

        Returns:
            Dict structuré avec les données de chaque module
        """
        contexte: dict[str, Any] = {}

        # Collecter chaque module indépendamment (ne pas bloquer si un échoue)
        collecteurs = {
            "inventaire": self._contexte_inventaire,
            "planning_repas": self._contexte_planning,
            "courses": self._contexte_courses,
            "budget": self._contexte_budget,
            "anniversaires": self._contexte_anniversaires,
            "documents_expirants": self._contexte_documents,
            "taches_maison": self._contexte_taches_maison,
        }

        for cle, collecteur in collecteurs.items():
            try:
                resultat = collecteur()
                if resultat:
                    contexte[cle] = resultat
            except Exception as e:
                logger.debug(f"Contexte {cle} non disponible: {e}")

        logger.debug(f"Contexte multi-module collecté: {list(contexte.keys())}")
        return contexte

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_inventaire(self, *, db=None) -> dict[str, Any]:
        """Résumé du contenu du frigo/inventaire."""
        from src.core.models import ArticleInventaire

        articles = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.quantite > 0)
            .all()
        )

        if not articles:
            return {"total": 0, "message": "Inventaire vide"}

        aujourd_hui = date.today()
        expirants = []
        par_emplacement: dict[str, list[str]] = {}

        for a in articles:
            emp = getattr(a, "emplacement", "autre") or "autre"
            par_emplacement.setdefault(emp, []).append(a.nom)

            if a.date_peremption and (a.date_peremption - aujourd_hui).days <= 3:
                expirants.append(
                    f"{a.nom} (expire {a.date_peremption.isoformat()})"
                )

        return {
            "total_articles": len(articles),
            "par_emplacement": {k: v[:10] for k, v in par_emplacement.items()},
            "expirent_bientot": expirants[:5],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_planning(self, *, db=None) -> dict[str, Any]:
        """Résumé du planning repas de la semaine."""
        from src.core.models import Repas
        from src.core.models.planning import Planning

        aujourd_hui = date.today()
        fin_semaine = aujourd_hui + timedelta(days=7)

        repas = (
            db.query(Repas)
            .filter(
                Repas.date_repas >= aujourd_hui,
                Repas.date_repas <= fin_semaine,
            )
            .all()
        )

        if not repas:
            return {"message": "Aucun repas planifié cette semaine"}

        repas_info = []
        for r in repas[:14]:
            repas_info.append({
                "date": r.date_repas.isoformat() if r.date_repas else None,
                "type": getattr(r, "type_repas", ""),
                "recette": getattr(r, "recette_nom", "") or "",
            })

        return {
            "nb_repas_planifies": len(repas),
            "repas_semaine": repas_info,
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_courses(self, *, db=None) -> dict[str, Any]:
        """Résumé de la liste de courses active."""
        from src.core.models.courses import ListeCourses, ArticleCourses

        liste = (
            db.query(ListeCourses)
            .filter(ListeCourses.statut == "active")
            .order_by(ListeCourses.date_creation.desc())
            .first()
        )

        if not liste:
            return {"message": "Aucune liste de courses active"}

        articles = (
            db.query(ArticleCourses)
            .filter(ArticleCourses.liste_id == liste.id)
            .all()
        )

        non_coches = [a.nom for a in articles if not getattr(a, "coche", False)]
        coches = [a.nom for a in articles if getattr(a, "coche", False)]

        return {
            "liste_active": liste.nom if hasattr(liste, "nom") else f"Liste #{liste.id}",
            "articles_restants": non_coches[:15],
            "articles_achetes": len(coches),
            "total_articles": len(articles),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_budget(self, *, db=None) -> dict[str, Any]:
        """Résumé du budget du mois en cours."""
        from sqlalchemy import extract, func
        from src.core.models import BudgetFamille

        aujourd_hui = date.today()

        resultats = (
            db.query(
                BudgetFamille.categorie,
                func.sum(BudgetFamille.montant),
                func.count(BudgetFamille.id),
            )
            .filter(
                extract("month", BudgetFamille.date) == aujourd_hui.month,
                extract("year", BudgetFamille.date) == aujourd_hui.year,
            )
            .group_by(BudgetFamille.categorie)
            .all()
        )

        if not resultats:
            return {"message": "Aucune dépense ce mois-ci"}

        par_categorie = {}
        total = 0.0
        for cat, montant, nb in resultats:
            m = float(montant or 0)
            par_categorie[cat] = {"montant": m, "nb_depenses": nb}
            total += m

        return {
            "total_mois": round(total, 2),
            "par_categorie": par_categorie,
            "mois": aujourd_hui.strftime("%B %Y"),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_anniversaires(self, *, db=None) -> dict[str, Any]:
        """Prochains anniversaires sous 30 jours."""
        from src.core.models import AnniversaireFamille

        tous = db.query(AnniversaireFamille).all()
        prochains = []

        for anniv in tous:
            jours_restants = getattr(anniv, "jours_restants", None)
            if jours_restants is not None and 0 <= jours_restants <= 30:
                prochains.append({
                    "nom": anniv.nom,
                    "jours_restants": jours_restants,
                    "age": getattr(anniv, "age", None),
                })

        if not prochains:
            return {}

        return {
            "prochains_30j": sorted(prochains, key=lambda a: a["jours_restants"]),
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_documents(self, *, db=None) -> dict[str, Any]:
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
            "documents_expirants": [
                {
                    "nom": d.nom,
                    "type": d.type_document,
                    "jours_restants": (d.date_expiration - aujourd_hui).days,
                }
                for d in docs
                if d.date_expiration
            ],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def _contexte_taches_maison(self, *, db=None) -> dict[str, Any]:
        """Tâches d'entretien prévues aujourd'hui/demain."""
        from src.core.models.maison import TacheEntretien

        aujourd_hui = date.today()
        demain = aujourd_hui + timedelta(days=1)

        try:
            taches = (
                db.query(TacheEntretien)
                .filter(
                    TacheEntretien.date_prevue >= aujourd_hui,
                    TacheEntretien.date_prevue <= demain,
                    TacheEntretien.statut != "termine",
                )
                .all()
            )

            if not taches:
                return {}

            return {
                "taches_du_jour": [
                    {
                        "nom": t.nom,
                        "date": t.date_prevue.isoformat() if t.date_prevue else None,
                        "priorite": getattr(t, "priorite", None),
                    }
                    for t in taches[:10]
                ],
            }
        except Exception:
            return {}

    def envoyer_message_avec_contexte(
        self,
        message: str,
        contexte_chat: str = "general",
        historique: list[dict[str, str]] | None = None,
    ) -> str | None:
        """Envoie un message au chat IA avec le contexte multi-module injecté.

        Args:
            message: Message de l'utilisateur
            contexte_chat: Contexte du chat (cuisine, famille, etc.)
            historique: Messages précédents

        Returns:
            Réponse de l'IA
        """
        from src.services.utilitaires.chat.chat_ai import obtenir_chat_ai_service

        contexte_metier = self.collecter_contexte_complet()
        chat = obtenir_chat_ai_service()

        return chat.envoyer_message_contextualise(
            message=message,
            contexte_metier=contexte_metier,
            contexte=contexte_chat,
            historique=historique,
        )


@service_factory("chat_contexte_multi_module", tags={"outils", "ia", "inter_module"})
def obtenir_service_chat_contexte() -> ChatContexteMultiModuleService:
    """Factory pour le service Chat IA multi-module."""
    return ChatContexteMultiModuleService()
