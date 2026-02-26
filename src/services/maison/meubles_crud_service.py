"""
Service CRUD Meubles (Wishlist).

Centralise tous les accès base de données pour la wishlist meubles.
Pattern: BaseService[Meuble] pour CRUD générique.
"""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import Meuble
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class MeublesCrudService(BaseService[Meuble]):
    """Service CRUD pour les meubles (wishlist achats).

    Hérite de BaseService[Meuble] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=Meuble, cache_ttl=300)

    @chronometre("maison.meubles.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_meubles(
        self,
        filtre_statut: str | None = None,
        filtre_piece: str | None = None,
        db: Session | None = None,
    ) -> list[Meuble]:
        """Récupère tous les meubles avec filtres optionnels.

        Args:
            filtre_statut: Filtrer par statut (souhaite, commande, achete).
            filtre_piece: Filtrer par pièce.
            db: Session DB optionnelle.

        Returns:
            Liste d'objets Meuble.
        """
        query = db.query(Meuble)
        if filtre_statut:
            query = query.filter(Meuble.statut == filtre_statut)
        if filtre_piece:
            query = query.filter(Meuble.piece == filtre_piece)
        return query.order_by(Meuble.id).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_meuble_by_id(self, meuble_id: int, db: Session | None = None) -> Meuble | None:
        """Récupère un meuble par son ID.

        Args:
            meuble_id: ID du meuble.
            db: Session DB optionnelle.

        Returns:
            Objet Meuble ou None.
        """
        return db.query(Meuble).filter(Meuble.id == meuble_id).first()

    @avec_session_db
    def create_meuble(self, data: dict, db: Session | None = None) -> Meuble:
        """Crée un nouveau meuble.

        Args:
            data: Dict avec les champs du meuble.
            db: Session DB optionnelle.

        Returns:
            Objet Meuble créé.
        """
        meuble = Meuble(**data)
        db.add(meuble)
        db.commit()
        db.refresh(meuble)
        logger.info(f"Meuble créé: {meuble.id} - {meuble.nom}")
        return meuble

    @avec_session_db
    def update_meuble(self, meuble_id: int, data: dict, db: Session | None = None) -> Meuble | None:
        """Met à jour un meuble existant.

        Args:
            meuble_id: ID du meuble.
            data: Dict des champs à mettre à jour.
            db: Session DB optionnelle.

        Returns:
            Objet Meuble mis à jour ou None si non trouvé.
        """
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return None
        for key, value in data.items():
            setattr(meuble, key, value)
        db.commit()
        db.refresh(meuble)
        logger.info(f"Meuble {meuble_id} mis à jour")
        return meuble

    @avec_session_db
    def delete_meuble(self, meuble_id: int, db: Session | None = None) -> bool:
        """Supprime un meuble.

        Args:
            meuble_id: ID du meuble.
            db: Session DB optionnelle.

        Returns:
            True si supprimé, False si non trouvé.
        """
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return False
        db.delete(meuble)
        db.commit()
        logger.info(f"Meuble {meuble_id} supprimé")
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_budget_resume(self, db: Session | None = None) -> dict:
        """Calcule le résumé budget des meubles souhaités.

        Args:
            db: Session DB optionnelle.

        Returns:
            Dict avec nb_articles, total_estime, total_max, par_piece.
        """
        meubles = db.query(Meuble).filter(Meuble.statut != "achete").all()

        if not meubles:
            return {
                "nb_articles": 0,
                "total_estime": 0.0,
                "total_max": 0.0,
                "par_piece": {},
            }

        total_estime = 0.0
        total_max = 0.0
        par_piece: dict = {}

        for m in meubles:
            prix_e = float(m.prix_estime) if m.prix_estime else 0.0
            prix_m = float(m.prix_max) if m.prix_max else 0.0
            total_estime += prix_e
            total_max += prix_m

            piece = getattr(m, "piece", "autre")
            if piece not in par_piece:
                par_piece[piece] = {"count": 0, "total_estime": 0.0, "total_max": 0.0}
            par_piece[piece]["count"] += 1
            par_piece[piece]["total_estime"] += prix_e
            par_piece[piece]["total_max"] += prix_m

        return {
            "nb_articles": len(meubles),
            "total_estime": total_estime,
            "total_max": total_max,
            "par_piece": par_piece,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("meubles_crud", tags={"maison", "crud", "meubles"})
def get_meubles_crud_service() -> MeublesCrudService:
    """Factory singleton pour le service CRUD meubles."""
    return MeublesCrudService()


def obtenir_service_meubles_crud() -> MeublesCrudService:
    """Factory française pour le service CRUD meubles."""
    return get_meubles_crud_service()
