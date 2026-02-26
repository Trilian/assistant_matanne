"""
Mixin Gestion de Stock pour le service inventaire.

Contient les méthodes de gestion de stock et historique:
- Calcul de statut des articles (stock bas, critique, péremption)
- Génération des alertes d'inventaire
- Enregistrement et consultation de l'historique des modifications
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session, joinedload

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.event_bus_mixin import emettre_evenement_simple

if TYPE_CHECKING:
    from src.core.models import ArticleInventaire

logger = logging.getLogger(__name__)


class InventaireStockMixin:
    """Mixin pour la gestion de stock et l'historique de l'inventaire.

    Méthodes déléguées depuis ServiceInventaire:
    - get_alertes: alertes de stock et péremption
    - _calculer_statut: calcul du statut d'un article
    - _jours_avant_peremption: jours avant expiration
    - _enregistrer_modification: enregistrement dans l'historique
    - get_historique: consultation de l'historique

    Utilise self.get_inventaire_complet() du service principal
    (cooperative mixin pattern).
    """

    # ═══════════════════════════════════════════════════════════
    # ALERTES & STATUT
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return={})
    def get_alertes(self) -> dict[str, list[dict[str, Any]]]:
        """Récupère toutes les alertes d'inventaire.

        Gets all inventory alerts grouped by type.

        Returns:
            Dict with keys: stock_bas, critique, peremption_proche
        """
        inventaire = self.get_inventaire_complet(include_ok=False)

        alertes = {
            "stock_bas": [],
            "critique": [],
            "peremption_proche": [],
        }

        for article in inventaire:
            statut = article["statut"]
            if statut in alertes:
                alertes[statut].append(article)

        logger.info(f"⚠️ Inventory alerts: {sum(len(v) for v in alertes.values())} items")
        return alertes

    def _calculer_statut(self, article: ArticleInventaire, today: date) -> str:
        """Calcule le statut d'un article.

        Args:
            article: ArticleInventaire object
            today: Current date for calculations

        Returns:
            Status string: 'critique', 'stock_bas', 'peremption_proche', or 'ok'
        """
        if article.date_peremption:
            days_left = (article.date_peremption - today).days
            if days_left <= 7:
                return "peremption_proche"

        if article.quantite < (article.quantite_min * 0.5):
            return "critique"

        if article.quantite < article.quantite_min:
            return "stock_bas"

        return "ok"

    def _jours_avant_peremption(self, article: ArticleInventaire, today: date) -> int | None:
        """Calcule jours avant péremption.

        Args:
            article: ArticleInventaire object
            today: Current date

        Returns:
            Days until expiration or None if no expiration date
        """
        if not article.date_peremption:
            return None
        return (article.date_peremption - today).days

    # ═══════════════════════════════════════════════════════════
    # HISTORIQUE (Tracking modifications)
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=True)
    @avec_session_db
    def _enregistrer_modification(
        self,
        article: ArticleInventaire,
        type_modification: str,
        quantite_avant: float | None = None,
        quantite_apres: float | None = None,
        quantite_min_avant: float | None = None,
        quantite_min_apres: float | None = None,
        date_peremption_avant: date | None = None,
        date_peremption_apres: date | None = None,
        emplacement_avant: str | None = None,
        emplacement_apres: str | None = None,
        notes: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Enregistre une modification dans l'historique.

        Args:
            article: Article modifié
            type_modification: "ajout", "modification", "suppression"
            quantite_avant/apres: Quantités avant/après
            ... (autres champs avant/après)
            notes: Notes additionnelles
            db: Database session

        Returns:
            True if recorded successfully
        """
        from src.core.models import HistoriqueInventaire

        historique = HistoriqueInventaire(
            article_id=article.id,
            ingredient_id=article.ingredient_id,
            type_modification=type_modification,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres,
            quantite_min_avant=quantite_min_avant,
            quantite_min_apres=quantite_min_apres,
            date_peremption_avant=date_peremption_avant,
            date_peremption_apres=date_peremption_apres,
            emplacement_avant=emplacement_avant,
            emplacement_apres=emplacement_apres,
            notes=notes,
        )

        db.add(historique)
        db.commit()

        emettre_evenement_simple(
            "stock.modifie",
            {"article_id": article.id, "ingredient_nom": "", "raison": type_modification},
            source="inventaire_stock",
        )

        logger.info(f"📝 Historique enregistré: {type_modification} article #{article.id}")
        return True

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_historique(
        self,
        article_id: int | None = None,
        ingredient_id: int | None = None,
        days: int = 30,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'historique des modifications.

        Args:
            article_id: Filtrer par article (optionnel)
            ingredient_id: Filtrer par ingrédient (optionnel)
            days: Historique des N derniers jours
            db: Database session

        Returns:
            List of modifications with details
        """

        from src.core.models import HistoriqueInventaire

        query = (
            db.query(HistoriqueInventaire)
            .options(
                joinedload(HistoriqueInventaire.ingredient),
            )
            .filter(HistoriqueInventaire.date_modification >= (date.today() - timedelta(days=days)))
        )

        if article_id:
            query = query.filter(HistoriqueInventaire.article_id == article_id)

        if ingredient_id:
            query = query.filter(HistoriqueInventaire.ingredient_id == ingredient_id)

        historique = query.order_by(HistoriqueInventaire.date_modification.desc()).all()

        result = []
        for h in historique:
            result.append(
                {
                    "id": h.id,
                    "article_id": h.article_id,
                    "ingredient_nom": h.ingredient.nom,
                    "type": h.type_modification,
                    "quantite_avant": h.quantite_avant,
                    "quantite_apres": h.quantite_apres,
                    "emplacement_avant": h.emplacement_avant,
                    "emplacement_apres": h.emplacement_apres,
                    "date_peremption_avant": h.date_peremption_avant,
                    "date_peremption_apres": h.date_peremption_apres,
                    "date_modification": h.date_modification,
                    "notes": h.notes,
                }
            )

        logger.info(f"📜 Retrieved {len(result)} historique entries")
        return result
