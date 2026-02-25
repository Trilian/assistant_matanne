"""
Mixins de timestamps pour les modèles SQLAlchemy.

Fournit des mixins réutilisables pour les colonnes de date de création
et de modification en convention française (cree_le/modifie_le).

Usage:
    # Convention française — création seule
    class MonModele(CreeLeMixin, Base):
        __tablename__ = "mon_modele"
        ...

    # Convention française — création + modification
    class MonModele(TimestampMixin, Base):
        __tablename__ = "mon_modele"
        ...

Phase 4 Audit, item 20.
"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import utc_now

# ═══════════════════════════════════════════════════════════
# CONVENTION FRANÇAISE (cree_le / modifie_le)
# ═══════════════════════════════════════════════════════════


class CreeLeMixin:
    """Mixin ajoutant une colonne `cree_le` (datetime UTC, auto-remplie)."""

    cree_le: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )


class TimestampMixin(CreeLeMixin):
    """Mixin ajoutant `cree_le` + `modifie_le` (auto-update)."""

    modifie_le: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
