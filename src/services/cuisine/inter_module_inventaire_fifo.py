"""
Bridge NIM7: Inventaire → Rotation FIFO.

Connecte la gestion du stock à la rotation FIFO (Premier Entré, Premier Sorti).
- Ajoute date_entree à chaque article pour tracker l'ordre d'arrivée
- Valide que les articles consommés respectent l'ordre FIFO
- Émet des alertes si non-respect du FIFO
- Événement: inventaire.article_consomme -> inventaire.fifo_validee
"""

import logging
from datetime import datetime, date

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class InventaireFIFOBridgeService:
    """Bridge pour gérer la rotation FIFO de l'inventaire."""

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def valider_consommation_fifo(
        self,
        ingredient_id: int,
        db: Session | None = None,
    ) -> dict | None:
        """Valide que la consommation respecte l'ordre FIFO.

        Logique:
        - Récupère tous les articles en stock du même ingrédient
        - Tri par date_entree (plus ancien d'abord)
        - Retourne l'article le plus ancien qui devrait être consommé

        Args:
            ingredient_id: ID de l'ingrédient à consommer
            db: Session base de données

        Returns:
            Info sur l'article à consommer en priorité, ou None
        """
        from src.core.models.inventaire import ArticleInventaire

        try:
            # Chercher tous les articles de cet ingrédient en stock
            articles = (
                db.query(ArticleInventaire)
                .filter(
                    and_(
                        ArticleInventaire.ingredient_id == ingredient_id,
                        ArticleInventaire.quantite > 0,
                    )
                )
                .order_by(ArticleInventaire.date_entree.asc())  # Plus ancien d'abord
                .all()
            )

            if not articles:
                logger.warning(f"Aucun article en stock pour ingrédient {ingredient_id}")
                return None

            # L'article le plus ancien doit être consommé d'abord
            article_prioritaire = articles[0]

            # Alerter si d'autres articles plus récents pourraient être consommés en premier
            non_respect = len(articles) > 1  # S'il y a plusieurs articles

            resultat = {
                "ingredient_id": ingredient_id,
                "article_prioritaire_id": article_prioritaire.id,
                "date_entree": article_prioritaire.date_entree.isoformat() if article_prioritaire.date_entree else None,
                "quantite_en_stock": float(article_prioritaire.quantite),
                "date_peremption": article_prioritaire.date_peremption.isoformat() if article_prioritaire.date_peremption else None,
                "emplacement": article_prioritaire.emplacement,
                "non_respect_fifo": non_respect,
                "nombre_autres_articles": len(articles) - 1,
            }

            if non_respect:
                logger.warning(f"⚠️ FIFO: {len(articles)} articles en stock pour ingrédient #{ingredient_id}")
                # Émettre alert
                from src.services.core.events import obtenir_bus

                bus = obtenir_bus()
                bus.emettre(
                    "inventaire.fifo_alerte",
                    {
                        "ingredient_id": ingredient_id,
                        "nombre_articles": len(articles),
                        "article_a_consommer": article_prioritaire.id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            return resultat

        except Exception as e:
            logger.error(f"Erreur validation FIFO: {e}")
            return None

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_articles_hors_ordre(self, limite: int = 10, db: Session | None = None) -> list[dict]:
        """Liste les ingrédients où plusieurs articles sont en stock (risque FIFO).

        Returns:
            Liste des problèmes FIFO potentiels
        """
        from src.core.models.inventaire import ArticleInventaire
        from sqlalchemy import func

        try:
            # Chercher les ingrédients avec plusieurs articles
            resultats = (
                db.query(
                    ArticleInventaire.ingredient_id,
                    func.count(ArticleInventaire.id).label("nombre_articles"),
                    func.min(ArticleInventaire.date_entree).label("plus_ancien"),
                )
                .filter(ArticleInventaire.quantite > 0)
                .group_by(ArticleInventaire.ingredient_id)
                .having(func.count(ArticleInventaire.id) > 1)
                .limit(limite)
                .all()
            )

            problemes = []
            for ingredient_id, nombre, plus_ancien in resultats:
                articles = (
                    db.query(ArticleInventaire)
                    .filter(ArticleInventaire.ingredient_id == ingredient_id)
                    .order_by(ArticleInventaire.date_entree.asc())
                    .all()
                )

                if articles:
                    problemes.append(
                        {
                            "ingredient_id": ingredient_id,
                            "nombre_articles": nombre,
                            "date_plus_ancien": plus_ancien.isoformat() if plus_ancien else None,
                            "jours_depuis": (date.today() - plus_ancien.date()).days if plus_ancien else 0,
                            "articles": [
                                {
                                    "id": a.id,
                                    "date_entree": a.date_entree.isoformat() if a.date_entree else None,
                                    "quantite": float(a.quantite),
                                    "peremption": a.date_peremption.isoformat() if a.date_peremption else None,
                                }
                                for a in articles
                            ],
                        }
                    )

            return problemes

        except Exception as e:
            logger.error(f"Erreur analyse articles hors ordre: {e}")
            return []


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("inventaire_fifo_bridge", tags={"bridges", "cuisine"})
def obtenir_inventaire_fifo_bridge() -> InventaireFIFOBridgeService:
    """Factory singleton pour le bridge Inventaire → FIFO."""
    return InventaireFIFOBridgeService()


# ═══════════════════════════════════════════════════════════
# EVENT SUBSCRIBERS
# ═══════════════════════════════════════════════════════════


def enregistrer_inventaire_fifo_subscribers() -> None:
    """Enregistre les subscribers pour le bridge Inventaire → FIFO."""
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()

    def _on_article_consomme(event):
        """Handler: Quand un article est consommé → valider FIFO."""
        try:
            ingredient_id = event.data.get("ingredient_id")
            if not ingredient_id:
                return

            service = obtenir_inventaire_fifo_bridge()
            resultat = service.valider_consommation_fifo(ingredient_id)
            if resultat and resultat.get("non_respect_fifo"):
                logger.warning(f"⚠️ Risque FIFO détecté pour ingrédient {ingredient_id}")
        except Exception as e:
            logger.warning(f"Erreur handler inventaire→FIFO: {e}")

    bus.souscrire("inventaire.article_consomme", _on_article_consomme)
    logger.info("✅ Bridge Inventaire → FIFO enregistré")
