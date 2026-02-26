"""
Modèles pour les documents familiaux.

Contient :
- DocumentFamille : Documents scannés et fichiers (carnet de santé, assurance, etc.)
"""

from datetime import date

from sqlalchemy import Boolean, Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# DOCUMENTS FAMILLE
# ═══════════════════════════════════════════════════════════


class DocumentFamille(TimestampMixin, Base):
    """Document familial stocké (PDF, image, scan).

    Attributes:
        titre: Titre du document
        categorie: Catégorie (administratif, medical, scolaire, assurance, finance)
        membre_famille: Membre concerné (Jules, Anne, Mathieu, Famille)
        fichier_url: Chemin ou URL du fichier
        fichier_nom: Nom original du fichier
        date_document: Date du document
        date_expiration: Date d'expiration
        notes: Notes complémentaires
        tags: Tags pour la recherche (JSONB)
        rappel_expiration_jours: Jours avant expiration pour rappel
        actif: Si le document est actif
    """

    __tablename__ = "documents_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # administratif, medical, scolaire, assurance, finance, autre
    membre_famille: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # Jules, Anne, Mathieu, Famille
    fichier_url: Mapped[str | None] = mapped_column(String(500))
    fichier_nom: Mapped[str | None] = mapped_column(String(200))
    date_document: Mapped[date | None] = mapped_column(Date)
    date_expiration: Mapped[date | None] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSONB)
    rappel_expiration_jours: Mapped[int | None] = mapped_column(Integer, default=30)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    @property
    def est_expire(self) -> bool:
        """Vérifie si le document est expiré."""
        if not self.date_expiration:
            return False
        return self.date_expiration < date.today()

    @property
    def jours_avant_expiration(self) -> int | None:
        """Nombre de jours avant expiration (négatif si expiré)."""
        if not self.date_expiration:
            return None
        return (self.date_expiration - date.today()).days

    def __repr__(self) -> str:
        return (
            f"<DocumentFamille(id={self.id}, titre='{self.titre}', "
            f"categorie='{self.categorie}', membre='{self.membre_famille}')>"
        )
