"""
Modèles pour l'album photos / souvenirs famille.

Contient :
- AlbumFamille : Albums photo organisés
- SouvenirFamille : Souvenirs individuels avec photos et contexte
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# ALBUM FAMILLE
# ═══════════════════════════════════════════════════════════


class AlbumFamille(TimestampMixin, Base):
    """Album photo familial.

    Attributes:
        titre: Titre de l'album
        description: Description
        type_album: Type (mensuel, evenement, vacances, premieres_fois, quotidien)
        date_debut: Date de début de la période couverte
        date_fin: Date de fin de la période
        couverture_url: URL de la photo de couverture
    """

    __tablename__ = "albums_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_album: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # mensuel, evenement, vacances, premieres_fois, quotidien
    date_debut: Mapped[date | None] = mapped_column(Date)
    date_fin: Mapped[date | None] = mapped_column(Date)
    couverture_url: Mapped[str | None] = mapped_column(String(500))

    # Relations
    souvenirs: Mapped[list["SouvenirFamille"]] = relationship(
        back_populates="album", cascade="all, delete-orphan"
    )

    @property
    def nombre_souvenirs(self) -> int:
        """Nombre de souvenirs dans l'album."""
        return len(self.souvenirs) if self.souvenirs else 0

    def __repr__(self) -> str:
        return f"<AlbumFamille(id={self.id}, titre='{self.titre}', " f"type='{self.type_album}')>"


# ═══════════════════════════════════════════════════════════
# SOUVENIRS
# ═══════════════════════════════════════════════════════════


class SouvenirFamille(TimestampMixin, Base):
    """Souvenir familial avec photo et contexte émotionnel.

    Attributes:
        album_id: ID de l'album (nullable)
        jalon_id: ID du jalon lié (nullable — premières fois de Jules)
        titre: Titre du souvenir
        description: Description narrative
        photo_url: URL de la photo
        video_url: URL de la vidéo (optionnel)
        date_souvenir: Date du souvenir
        lieu: Lieu du souvenir
        personnes_presentes: Personnes présentes (JSONB)
        emotion: Émotion principale (joie, fierté, émotion, rire, surprise)
        tags: Tags pour organisation (JSONB)
    """

    __tablename__ = "souvenirs_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int | None] = mapped_column(
        ForeignKey("albums_famille.id", ondelete="SET NULL"), index=True
    )
    jalon_id: Mapped[int | None] = mapped_column(
        ForeignKey("jalons.id", ondelete="SET NULL"), index=True
    )
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(500))
    video_url: Mapped[str | None] = mapped_column(String(500))
    date_souvenir: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    lieu: Mapped[str | None] = mapped_column(String(200))
    personnes_presentes: Mapped[list[str] | None] = mapped_column(JSONB)
    emotion: Mapped[str | None] = mapped_column(String(50))
    tags: Mapped[list[str] | None] = mapped_column(JSONB)

    # Relations
    album: Mapped["AlbumFamille | None"] = relationship(back_populates="souvenirs")
    jalon: Mapped["Jalon | None"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<SouvenirFamille(id={self.id}, titre='{self.titre}', " f"date={self.date_souvenir})>"
        )
