"""
Service Inventaire Unifié.

✅ Utilise @avec_session_db et @avec_cache
✅ Validation Pydantic centralisée
✅ Type hints complets pour meilleur IDE support
✅ Services testables sans Streamlit
"""

import logging
from datetime import date
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ArticleInventaire
from src.core.monitoring import chronometre
from src.services.core.base import BaseAIService, BaseService, InventoryAIMixin

from .inventaire_io import InventaireIOMixin
from .inventaire_operations import InventaireOperationsMixin
from .inventaire_stats import InventaireStatsMixin
from .inventaire_stock import InventaireStockMixin

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

CATEGORIES = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Autre",
]

EMPLACEMENTS = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE UNIFIÉ
# ═══════════════════════════════════════════════════════════


class ServiceInventaire(
    BaseService[ArticleInventaire],
    BaseAIService,
    InventoryAIMixin,
    InventaireIOMixin,
    InventaireStatsMixin,
    InventaireStockMixin,
    InventaireOperationsMixin,
):
    """
    Service complet pour l'inventaire.

    ✅ Héritage multiple :
    - BaseService → CRUD optimisé
    - BaseAIService → IA avec rate limiting auto
    - InventoryAIMixin → Contextes métier inventaire
    - InventaireIOMixin → Import/export d'articles
    - InventaireStatsMixin → Statistiques et alertes
    - InventaireStockMixin → Gestion de stock et historique
    - InventaireOperationsMixin → CRUD articles, photos, suggestions IA

    Fonctionnalités:
    - CRUD optimisé avec cache
    - Alertes stock et péremption
    - Suggestions IA pour courses
    """

    def __init__(self):
        # MRO coopératif: tous les arguments passés via kwargs
        super().__init__(
            # Arguments pour BaseService
            model=ArticleInventaire,
            cache_ttl=1800,
            # Arguments pour BaseAIService
            client=obtenir_client_ia(),
            cache_prefix="inventaire",
            default_ttl=1800,
            default_temperature=0.7,
            service_name="inventaire",
        )

    # ═══════════════════════════════════════════════════════════
    # REQUÊTE INVENTAIRE COMPLET
    # ═══════════════════════════════════════════════════════════

    @chronometre("inventaire.chargement_complet", seuil_alerte_ms=2000)
    @avec_cache(
        ttl=1800,
        key_func=lambda self, emplacement, categorie, include_ok: (
            f"inventaire_{emplacement}_{categorie}_{include_ok}"
        ),
    )
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_inventaire_complet(
        self,
        emplacement: str | None = None,
        categorie: str | None = None,
        include_ok: bool = True,
        db: Session | None = None,
    ) -> list[dict[str, Any]]:
        """Récupère l'inventaire complet avec statuts calculés.

        Retrieves complete inventory with calculated statuses.
        Results are cached for 30 minutes.

        Args:
            emplacement: Optional location filter (Frigo, Congélateur, etc.)
            categorie: Optional category filter
            include_ok: Include items with OK status
            db: Database session (injected by @avec_session_db)

        Returns:
            List of dict with article data and calculated status
        """
        query = db.query(ArticleInventaire).options(joinedload(ArticleInventaire.ingredient))

        if emplacement:
            query = query.filter(ArticleInventaire.emplacement == emplacement)

        articles = query.all()

        result = []
        today = date.today()

        for article in articles:
            statut = self._calculer_statut(article, today)

            if not include_ok and statut == "ok":
                continue

            if categorie and article.ingredient.categorie != categorie:
                continue

            result.append(
                {
                    "id": article.id,
                    "ingredient_id": article.ingredient_id,
                    "ingredient_nom": article.ingredient.nom,
                    "ingredient_categorie": article.ingredient.categorie,
                    "quantite": article.quantite,
                    "quantite_min": article.quantite_min,
                    "unite": article.ingredient.unite,
                    "emplacement": article.emplacement,
                    "date_peremption": article.date_peremption,
                    "statut": statut,
                    "jours_avant_peremption": self._jours_avant_peremption(article, today),
                }
            )

        logger.info(f"✅ Retrieved complete inventory: {len(result)} items")
        return result

    # ═══════════════════════════════════════════════════════════
    # NOTE: Gestion stock & historique → InventaireStockMixin
    #   → get_alertes, _calculer_statut, _jours_avant_peremption
    #   → _enregistrer_modification, get_historique
    #   Voir: inventaire_stock.py
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # NOTE: CRUD articles, photos & suggestions IA → InventaireOperationsMixin
    #   → ajouter_article, mettre_a_jour_article, supprimer_article
    #   → ajouter_photo, supprimer_photo, obtenir_photo
    #   → suggerer_courses_ia
    #   Voir: inventaire_operations.py
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # NOTE: Notifications & alertes déléguées à InventaireStatsMixin
    #   → generer_notifications_alertes, obtenir_alertes_actives
    #   → get_statistiques, get_stats_par_categorie, get_articles_a_prelever
    #   Voir: inventaire_stats.py
    # ═══════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════
    # NOTE: Import/export avancé délégué à InventaireIOMixin
    #   → importer_articles, exporter_inventaire
    #   → _exporter_csv, _exporter_json, valider_fichier_import
    #   Voir: inventaire_io.py
    # ═══════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════
# INSTANCE SINGLETON — Via ServiceRegistry (thread-safe)
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("inventaire", tags={"cuisine", "ia", "crud", "stock"})
def obtenir_service_inventaire() -> ServiceInventaire:
    """Obtient ou crée l'instance ServiceInventaire (via registre, thread-safe)."""
    return ServiceInventaire()


def get_inventory_service() -> ServiceInventaire:
    """Factory for inventory service (English alias)."""
    return obtenir_service_inventaire()


__all__ = [
    # Service principal
    "ServiceInventaire",
    "obtenir_service_inventaire",
    "get_inventory_service",
    # Constantes
    "CATEGORIES",
    "EMPLACEMENTS",
    # Variable globale
    "inventaire_service",
]
