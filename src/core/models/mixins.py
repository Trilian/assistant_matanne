"""
Mixins de timestamps pour les modèles SQLAlchemy.

Fournit des mixins réutilisables pour les colonnes de date de création
et de modification en convention française (cree_le/modifie_le).

Les colonnes DB portent directement les noms français — aucun alias.

Usage:
    # Convention française — création seule
    class MonModele(CreeLeMixin, Base):
        __tablename__ = "mon_modele"
        ...

    # Convention française — création + modification
    class MonModele(TimestampMixin, Base):
        __tablename__ = "mon_modele"
        ...

Audit qualité — mixin modèles.
"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from .base import utc_now

# ═══════════════════════════════════════════════════════════
# CONVENTION FRANÇAISE (cree_le / modifie_le)
# ═══════════════════════════════════════════════════════════


class CreeLeMixin:
    """Mixin ajoutant une colonne `cree_le` (nom DB direct, sans alias)."""

    @declared_attr
    def cree_le(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=utc_now, nullable=False)


class TimestampMixin(CreeLeMixin):
    """Mixin ajoutant `cree_le` + `modifie_le` comme colonnes DB directes."""

    @declared_attr
    def modifie_le(cls) -> Mapped[datetime]:
        return mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
