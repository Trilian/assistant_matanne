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
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, synonym

from .base import utc_now

# ═══════════════════════════════════════════════════════════
# CONVENTION FRANÇAISE (cree_le / modifie_le)
# ═══════════════════════════════════════════════════════════


class CreeLeMixin:
    """Mixin ajoutant une colonne `created_at` puis un alias `cree_le`.

    Si la classe fille définit déjà `created_at`, la colonne existante est
    réutilisée et `cree_le` devient un `synonym` pointant vers elle.
    """

    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=utc_now, nullable=False)

    @declared_attr
    def cree_le(cls):
        return synonym("created_at")


class TimestampMixin(CreeLeMixin):
    """Mixin ajoutant `created_at/updated_at` + alias `cree_le/modifie_le`."""

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    @declared_attr
    def modifie_le(cls):
        return synonym("updated_at")
