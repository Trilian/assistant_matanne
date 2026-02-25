"""
Fonctions CRUD pour le module Meubles.
"""

import logging

from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)


def _get_meuble_model():
    """Retourne le modèle Meuble (import différé)."""
    try:
        from src.core.models import Meuble

        return Meuble
    except ImportError:
        from decimal import Decimal

        from sqlalchemy import Boolean, Numeric, String
        from sqlalchemy.orm import Mapped, mapped_column

        from src.core.models.base import Base

        class Meuble(Base):
            """Modèle Meuble (wishlist achats)."""

            __tablename__ = "meubles_wishlist"

            id: Mapped[int] = mapped_column(primary_key=True)
            nom: Mapped[str] = mapped_column(String(200))
            piece: Mapped[str] = mapped_column(String(50))
            description: Mapped[str | None] = mapped_column(String(500), nullable=True)
            priorite: Mapped[str] = mapped_column(String(20), default="normale")
            statut: Mapped[str] = mapped_column(String(20), default="souhaite")
            prix_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
            prix_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
            magasin: Mapped[str | None] = mapped_column(String(200), nullable=True)
            url: Mapped[str | None] = mapped_column(String(500), nullable=True)
            dimensions: Mapped[str | None] = mapped_column(String(100), nullable=True)
            actif: Mapped[bool] = mapped_column(Boolean, default=True)

        return Meuble


def get_all_meubles(filtre_statut: str | None = None, filtre_piece: str | None = None) -> list:
    """Récupère tous les meubles avec filtres optionnels.

    Args:
        filtre_statut: Filtrer par statut.
        filtre_piece: Filtrer par pièce.

    Returns:
        Liste d'objets Meuble.
    """
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        query = db.query(Meuble)
        if filtre_statut:
            query = query.filter(Meuble.statut == filtre_statut)
        if filtre_piece:
            query = query.filter(Meuble.piece == filtre_piece)
        return query.order_by(Meuble.id).all()


def get_meuble_by_id(meuble_id: int):
    """Récupère un meuble par son ID."""
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        return db.query(Meuble).filter(Meuble.id == meuble_id).first()


def create_meuble(data: dict) -> None:
    """Crée un nouveau meuble."""
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        meuble = Meuble(**data)
        db.add(meuble)
        db.commit()
        db.refresh(meuble)


def update_meuble(meuble_id: int, data: dict):
    """Met à jour un meuble existant."""
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return None
        for key, value in data.items():
            setattr(meuble, key, value)
        db.commit()
        db.refresh(meuble)
        return meuble


def delete_meuble(meuble_id: int) -> bool:
    """Supprime un meuble."""
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        meuble = db.query(Meuble).filter(Meuble.id == meuble_id).first()
        if meuble is None:
            return False
        db.delete(meuble)
        db.commit()
        return True


def get_budget_resume() -> dict:
    """Calcule le résumé budget des meubles souhaités.

    Returns:
        Dict avec nb_articles, total_estime, total_max, par_piece.
    """
    Meuble = _get_meuble_model()

    with obtenir_contexte_db() as db:
        meubles = db.query(Meuble).filter(Meuble.statut != "achete").all()

    if not meubles:
        return {
            "nb_articles": 0,
            "total_estime": 0,
            "total_max": 0,
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
