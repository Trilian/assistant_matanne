"""
Service inter-modules : Jardin → Inventaire.

Phase 4.1 : synchroniser automatiquement les récoltes validées
vers l'inventaire cuisine, avec création d'ingrédient si besoin.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class JardinInventaireInteractionService:
    """Bridge récoltes jardin → inventaire cuisine."""

    @staticmethod
    def _determiner_categorie(type_element: str | None) -> str:
        """Déduit une catégorie d'ingrédient à partir du type jardin."""
        type_normalise = (type_element or "").lower()
        if "fruit" in type_normalise:
            return "Fruits"
        if any(mot in type_normalise for mot in ("legume", "légume", "potager")):
            return "Légumes"
        if any(mot in type_normalise for mot in ("aromate", "herbe", "epice", "épice")):
            return "Herbes"
        return "Jardin"

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_recolte_vers_inventaire(
        self,
        element_id: int,
        quantite: float = 1.0,
        emplacement: str = "jardin",
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Ajoute une récolte jardin à l'inventaire cuisine."""
        from src.core.models import ArticleInventaire, ElementJardin, JournalJardin
        from src.core.models.recettes import Ingredient

        if db is None:
            return {"ok": False, "message": "Session DB indisponible"}

        element = db.query(ElementJardin).filter(ElementJardin.id == element_id).first()
        if element is None:
            return {"ok": False, "message": f"Élément jardin {element_id} introuvable"}

        deja_sync = (
            db.query(JournalJardin.id)
            .filter(
                JournalJardin.garden_item_id == element.id,
                JournalJardin.action == "sync_inventaire",
            )
            .first()
        )
        if deja_sync:
            return {
                "ok": True,
                "element_id": element.id,
                "element_nom": element.nom,
                "action": "deja_sync",
                "message": "Récolte déjà synchronisée vers l'inventaire",
            }

        ingredient = (
            db.query(Ingredient)
            .filter(func.lower(Ingredient.nom) == (element.nom or "").lower())
            .first()
        )
        if ingredient is None:
            ingredient = Ingredient(
                nom=element.nom,
                categorie=self._determiner_categorie(element.type),
                unite="pcs",
            )
            db.add(ingredient)
            db.flush()

        article = (
            db.query(ArticleInventaire)
            .filter(ArticleInventaire.ingredient_id == ingredient.id)
            .first()
        )

        quantite_ajoutee = round(max(0.1, float(quantite or 0)), 2)
        action = "mise_a_jour"
        if article is not None:
            article.quantite = round(float(article.quantite or 0) + quantite_ajoutee, 2)
            article.emplacement = article.emplacement or emplacement
            article.date_peremption = article.date_peremption or (date.today() + timedelta(days=5))
        else:
            article = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=quantite_ajoutee,
                quantite_min=1.0,
                emplacement=emplacement,
                date_peremption=date.today() + timedelta(days=5),
            )
            db.add(article)
            db.flush()
            action = "creation"

        db.add(
            JournalJardin(
                garden_item_id=element.id,
                date=date.today(),
                action="sync_inventaire",
                notes=(
                    f"Synchronisation automatique vers inventaire : +{quantite_ajoutee} "
                    f"{ingredient.unite} ({action})"
                ),
            )
        )
        db.commit()
        db.refresh(article)

        resultat = {
            "ok": True,
            "element_id": element.id,
            "element_nom": element.nom,
            "ingredient_id": ingredient.id,
            "article_inventaire_id": article.id,
            "quantite_ajoutee": quantite_ajoutee,
            "quantite_totale": float(article.quantite or 0),
            "emplacement": article.emplacement,
            "action": action,
            "message": f"Récolte {element.nom} synchronisée vers l'inventaire",
        }
        logger.info(
            "✅ Jardin→Inventaire élément=%s article=%s action=%s qte=%.2f",
            element.id,
            article.id,
            action,
            quantite_ajoutee,
        )
        return resultat

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_recoltes_a_venir(
        self,
        horizon_jours: int = 0,
        quantite_par_defaut: float = 1.0,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Synchronise toutes les récoltes dues jusqu'à l'horizon donné."""
        from src.core.models import ElementJardin, JournalJardin

        if db is None:
            return {"ok": False, "message": "Session DB indisponible"}

        date_limite = date.today() + timedelta(days=max(0, horizon_jours))
        recoltes = (
            db.query(ElementJardin)
            .filter(
                ElementJardin.statut == "actif",
                ElementJardin.date_recolte_prevue.isnot(None),
                ElementJardin.date_recolte_prevue <= date_limite,
            )
            .all()
        )

        resultats: list[dict[str, Any]] = []
        for element in recoltes:
            deja_sync = (
                db.query(JournalJardin.id)
                .filter(
                    JournalJardin.garden_item_id == element.id,
                    JournalJardin.action == "sync_inventaire",
                )
                .first()
            )
            if deja_sync:
                continue

            resultat = self.synchroniser_recolte_vers_inventaire(
                element_id=element.id,
                quantite=quantite_par_defaut,
                db=db,
            )
            if resultat:
                resultats.append(resultat)

        return {
            "ok": True,
            "nb_recoltes_sync": len([r for r in resultats if r.get("ok")]),
            "recoltes": resultats,
            "message": f"{len(resultats)} récolte(s) synchronisée(s)",
        }


@service_factory(
    "jardin_inventaire_interaction",
    tags={"cuisine", "jardin", "inventaire", "bridge"},
)
def obtenir_service_jardin_inventaire_interaction() -> JardinInventaireInteractionService:
    """Factory pour le bridge Jardin → Inventaire."""
    return JardinInventaireInteractionService()
