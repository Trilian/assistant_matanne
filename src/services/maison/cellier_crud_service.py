"""
Service CRUD Cellier.

Inventaire du cellier avec alertes péremption et scan code-barres.
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.maison_extensions import ArticleCellier
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class CellierCrudService(EventBusMixin, BaseService[ArticleCellier]):
    """Service CRUD pour l'inventaire du cellier."""

    _event_source = "cellier"

    def __init__(self):
        super().__init__(model=ArticleCellier, cache_ttl=300)

    @chronometre("maison.cellier.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_articles(
        self,
        filtre_categorie: str | None = None,
        filtre_emplacement: str | None = None,
        db: Session | None = None,
    ) -> list[ArticleCellier]:
        """Récupère tous les articles du cellier."""
        query = db.query(ArticleCellier)
        if filtre_categorie:
            query = query.filter(ArticleCellier.categorie == filtre_categorie)
        if filtre_emplacement:
            query = query.filter(ArticleCellier.emplacement == filtre_emplacement)
        return query.order_by(ArticleCellier.dlc, ArticleCellier.nom).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_article_by_id(
        self, article_id: int, db: Session | None = None
    ) -> ArticleCellier | None:
        """Récupère un article par son ID."""
        return db.query(ArticleCellier).filter(ArticleCellier.id == article_id).first()

    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_article_by_barcode(
        self, code_barres: str, db: Session | None = None
    ) -> ArticleCellier | None:
        """Récupère un article par code-barres."""
        return db.query(ArticleCellier).filter(ArticleCellier.code_barres == code_barres).first()

    @avec_session_db
    def create_article(self, data: dict, db: Session | None = None) -> ArticleCellier:
        """Crée un nouvel article au cellier."""
        article = ArticleCellier(**data)
        db.add(article)
        db.commit()
        db.refresh(article)
        logger.info(f"Article cellier créé: {article.id} - {article.nom}")
        self._emettre_evenement(
            "cellier.modifie",
            {"article_id": article.id, "nom": article.nom, "action": "cree"},
        )
        return article

    @avec_session_db
    def update_article(
        self, article_id: int, data: dict, db: Session | None = None
    ) -> ArticleCellier | None:
        """Met à jour un article."""
        article = db.query(ArticleCellier).filter(ArticleCellier.id == article_id).first()
        if article is None:
            return None
        for key, value in data.items():
            setattr(article, key, value)
        db.commit()
        db.refresh(article)
        logger.info(f"Article cellier {article_id} mis à jour")
        self._emettre_evenement(
            "cellier.modifie",
            {"article_id": article_id, "nom": article.nom, "action": "modifie"},
        )
        return article

    @avec_session_db
    def delete_article(self, article_id: int, db: Session | None = None) -> bool:
        """Supprime un article du cellier."""
        article = db.query(ArticleCellier).filter(ArticleCellier.id == article_id).first()
        if article is None:
            return False
        nom = article.nom
        db.delete(article)
        db.commit()
        logger.info(f"Article cellier {article_id} supprimé")
        self._emettre_evenement(
            "cellier.modifie",
            {"article_id": article_id, "nom": nom, "action": "supprime"},
        )
        return True

    @avec_session_db
    def ajuster_quantite(
        self, article_id: int, delta: int, db: Session | None = None
    ) -> ArticleCellier | None:
        """Ajuste la quantité d'un article (+/-)."""
        article = db.query(ArticleCellier).filter(ArticleCellier.id == article_id).first()
        if article is None:
            return None
        article.quantite = max(0, article.quantite + delta)
        db.commit()
        db.refresh(article)
        return article

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_peremption(
        self, jours_horizon: int = 14, db: Session | None = None
    ) -> list[dict]:
        """Récupère les articles proches de la péremption."""
        date_limite = date.today() + timedelta(days=jours_horizon)
        articles = (
            db.query(ArticleCellier)
            .filter(
                ArticleCellier.dlc.isnot(None),
                ArticleCellier.dlc <= date_limite,
                ArticleCellier.quantite > 0,
            )
            .order_by(ArticleCellier.dlc)
            .all()
        )
        return [
            {
                "article_id": a.id,
                "nom": a.nom,
                "dlc": a.dlc,
                "jours_restants": (a.dlc - date.today()).days,
                "quantite": a.quantite,
            }
            for a in articles
        ]

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_stock(self, db: Session | None = None) -> list[dict]:
        """Récupère les articles en rupture de stock."""
        articles = (
            db.query(ArticleCellier)
            .filter(ArticleCellier.quantite <= ArticleCellier.seuil_alerte)
            .order_by(ArticleCellier.nom)
            .all()
        )
        return [
            {
                "article_id": a.id,
                "nom": a.nom,
                "quantite": a.quantite,
                "seuil": a.seuil_alerte,
            }
            for a in articles
        ]

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_stats_cellier(self, db: Session | None = None) -> dict:
        """Statistiques du cellier."""
        articles = db.query(ArticleCellier).all()
        total_articles = sum(a.quantite for a in articles)
        total_valeur = sum(float(a.prix_unitaire or 0) * a.quantite for a in articles)
        par_categorie: dict = {}
        for a in articles:
            cat = a.categorie
            if cat not in par_categorie:
                par_categorie[cat] = {"count": 0, "quantite": 0}
            par_categorie[cat]["count"] += 1
            par_categorie[cat]["quantite"] += a.quantite
        return {
            "nb_references": len(articles),
            "total_articles": total_articles,
            "total_valeur_estimee": total_valeur,
            "par_categorie": par_categorie,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("cellier_crud", tags={"maison", "crud", "cellier"})
def get_cellier_crud_service() -> CellierCrudService:
    """Factory singleton pour le service CRUD cellier."""
    return CellierCrudService()


def obtenir_service_cellier_crud() -> CellierCrudService:
    """Factory française pour le service CRUD cellier."""
    return get_cellier_crud_service()
