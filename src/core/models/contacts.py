"""
Modèles pour les contacts familiaux.

Contient :
- ContactFamille : Carnet de contacts famille (médecin, nounou, école, urgences)
"""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# CONTACTS FAMILLE
# ═══════════════════════════════════════════════════════════


class ContactFamille(TimestampMixin, Base):
    """Contact familial (médecin, nounou, école, urgences, famille élargie).

    Attributes:
        nom: Nom de famille ou raison sociale
        prenom: Prénom (optionnel pour organisations)
        categorie: Catégorie du contact
        sous_categorie: Sous-catégorie (pédiatre, dentiste, etc.)
        telephone: Numéro principal
        telephone_2: Numéro secondaire
        email: Adresse email
        adresse: Adresse postale
        code_postal: Code postal
        ville: Ville
        horaires: Horaires d'ouverture / disponibilité
        notes: Notes complémentaires
        lien_maps: Lien Google Maps
        est_urgence: Si c'est un contact d'urgence
        actif: Si le contact est actif
    """

    __tablename__ = "contacts_famille"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    prenom: Mapped[str | None] = mapped_column(String(200))
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # medical, garde, education, administration, famille, urgence
    sous_categorie: Mapped[str | None] = mapped_column(
        String(100)
    )  # pédiatre, généraliste, dentiste, etc.
    telephone: Mapped[str | None] = mapped_column(String(20))
    telephone_2: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(200))
    adresse: Mapped[str | None] = mapped_column(String(300))
    code_postal: Mapped[str | None] = mapped_column(String(10))
    ville: Mapped[str | None] = mapped_column(String(100))
    horaires: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    lien_maps: Mapped[str | None] = mapped_column(String(500))
    est_urgence: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    @property
    def nom_complet(self) -> str:
        """Retourne le nom complet du contact."""
        if self.prenom:
            return f"{self.prenom} {self.nom}"
        return self.nom

    def __repr__(self) -> str:
        return (
            f"<ContactFamille(id={self.id}, nom='{self.nom_complet}', "
            f"categorie='{self.categorie}')>"
        )
