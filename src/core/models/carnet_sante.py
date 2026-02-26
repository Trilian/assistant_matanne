"""
Modèles pour le carnet de santé numérique.

Contient :
- Vaccin : Vaccinations avec calendrier et rappels
- RendezVousMedical : RDV médicaux (pédiatre, généraliste, spécialiste)
- MesureCroissance : Mesures taille/poids/périmètre crânien
- NormeOMS : Données de référence OMS (percentiles poids/taille/PC/IMC)
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreeLeMixin

# ═══════════════════════════════════════════════════════════
# VACCINATIONS
# ═══════════════════════════════════════════════════════════


class Vaccin(CreeLeMixin, Base):
    """Vaccination enregistrée dans le carnet de santé.

    Attributes:
        enfant_id: ID du profil enfant (FK)
        nom_vaccin: Nom du vaccin (DTP, ROR, BCG, etc.)
        type_vaccin: Type (obligatoire, recommandé)
        date_injection: Date de l'injection
        numero_lot: Numéro de lot du vaccin
        rappel_prevu: Date du prochain rappel
        medecin: Nom du médecin vaccinateur
        lieu: Lieu de vaccination
        notes: Notes complémentaires
        fait: Si le vaccin a été effectué
    """

    __tablename__ = "vaccins"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[int] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nom_vaccin: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    type_vaccin: Mapped[str] = mapped_column(
        String(50), nullable=False, default="obligatoire"
    )  # obligatoire, recommandé
    date_injection: Mapped[date | None] = mapped_column(Date)
    numero_lot: Mapped[str | None] = mapped_column(String(100))
    rappel_prevu: Mapped[date | None] = mapped_column(Date, index=True)
    medecin: Mapped[str | None] = mapped_column(String(200))
    lieu: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text)
    fait: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relations
    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(  # noqa: F821
        back_populates="vaccins"
    )

    def __repr__(self) -> str:
        return f"<Vaccin(id={self.id}, nom='{self.nom_vaccin}', fait={self.fait})>"


# ═══════════════════════════════════════════════════════════
# RENDEZ-VOUS MÉDICAUX
# ═══════════════════════════════════════════════════════════


class RendezVousMedical(CreeLeMixin, Base):
    """Rendez-vous médical pour un membre de la famille.

    Attributes:
        enfant_id: ID enfant (nullable, pour adultes)
        membre_famille: Nom du membre (Jules, Anne, Mathieu)
        type_rdv: Type de consultation
        medecin: Nom du médecin
        date_rdv: Date et heure du RDV
        lieu: Lieu / adresse
        motif: Motif de la consultation
        notes_medecin: Notes du médecin après consultation
        ordonnance_url: URL du scan de l'ordonnance
        rappel_jours_avant: Nombre de jours avant pour rappel
        statut: Statut (planifié, effectué, annulé)
    """

    __tablename__ = "rendez_vous_medicaux"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[int | None] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="SET NULL"), index=True
    )
    membre_famille: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    type_rdv: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # pédiatre, généraliste, dentiste, ophtalmo, spécialiste
    medecin: Mapped[str | None] = mapped_column(String(200))
    date_rdv: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    lieu: Mapped[str | None] = mapped_column(String(300))
    motif: Mapped[str | None] = mapped_column(Text)
    notes_medecin: Mapped[str | None] = mapped_column(Text)
    ordonnance_url: Mapped[str | None] = mapped_column(String(500))
    rappel_jours_avant: Mapped[int] = mapped_column(Integer, default=3)
    statut: Mapped[str] = mapped_column(String(50), nullable=False, default="planifié", index=True)

    # Relations
    enfant: Mapped[Optional["ProfilEnfant"]] = relationship(  # noqa: F821
        back_populates="rendez_vous"
    )

    def __repr__(self) -> str:
        return (
            f"<RendezVousMedical(id={self.id}, type='{self.type_rdv}', "
            f"date={self.date_rdv}, membre='{self.membre_famille}')>"
        )


# ═══════════════════════════════════════════════════════════
# MESURES DE CROISSANCE
# ═══════════════════════════════════════════════════════════


class MesureCroissance(CreeLeMixin, Base):
    """Mesure physique d'un enfant (courbe de croissance).

    Attributes:
        enfant_id: ID du profil enfant
        date_mesure: Date de la mesure
        poids_kg: Poids en kilogrammes
        taille_cm: Taille en centimètres
        perimetre_cranien_cm: Périmètre crânien en centimètres
        imc_calcule: IMC calculé automatiquement
        age_mois: Âge en mois au moment de la mesure
        notes: Notes (contexte de la mesure)
    """

    __tablename__ = "mesures_croissance"

    id: Mapped[int] = mapped_column(primary_key=True)
    enfant_id: Mapped[int] = mapped_column(
        ForeignKey("profils_enfants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_mesure: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    poids_kg: Mapped[float | None] = mapped_column(Float)
    taille_cm: Mapped[float | None] = mapped_column(Float)
    perimetre_cranien_cm: Mapped[float | None] = mapped_column(Float)
    imc_calcule: Mapped[float | None] = mapped_column(Float)
    age_mois: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    enfant: Mapped["ProfilEnfant"] = relationship(  # noqa: F821
        back_populates="mesures_croissance"
    )

    __table_args__ = (
        CheckConstraint("poids_kg > 0 OR poids_kg IS NULL", name="ck_mesure_poids_positif"),
        CheckConstraint("taille_cm > 0 OR taille_cm IS NULL", name="ck_mesure_taille_positive"),
        CheckConstraint(
            "perimetre_cranien_cm > 0 OR perimetre_cranien_cm IS NULL",
            name="ck_mesure_pc_positif",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<MesureCroissance(id={self.id}, date={self.date_mesure}, "
            f"poids={self.poids_kg}kg, taille={self.taille_cm}cm)>"
        )


# ═══════════════════════════════════════════════════════════
# NORMES OMS (DONNÉES DE RÉFÉRENCE)
# ═══════════════════════════════════════════════════════════


class NormeOMS(Base):
    """Données de référence OMS pour les courbes de croissance.

    Percentiles P3, P15, P50, P85, P97 par sexe, âge et type de mesure.
    Table pré-remplie avec les données OMS standards (0-36 mois).

    Attributes:
        sexe: M ou F
        age_mois: Âge en mois (0-36)
        type_mesure: Type (poids, taille, perimetre_cranien, imc)
        p3: Percentile 3
        p15: Percentile 15
        p50: Percentile 50 (médiane)
        p85: Percentile 85
        p97: Percentile 97
    """

    __tablename__ = "normes_oms"

    id: Mapped[int] = mapped_column(primary_key=True)
    sexe: Mapped[str] = mapped_column(String(1), nullable=False, index=True)  # M ou F
    age_mois: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    type_mesure: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # poids, taille, perimetre_cranien, imc
    p3: Mapped[float] = mapped_column(Float, nullable=False)
    p15: Mapped[float] = mapped_column(Float, nullable=False)
    p50: Mapped[float] = mapped_column(Float, nullable=False)
    p85: Mapped[float] = mapped_column(Float, nullable=False)
    p97: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("sexe IN ('M', 'F')", name="ck_norme_sexe"),
        CheckConstraint("age_mois >= 0 AND age_mois <= 60", name="ck_norme_age_range"),
        CheckConstraint(
            "type_mesure IN ('poids', 'taille', 'perimetre_cranien', 'imc')",
            name="ck_norme_type_mesure",
        ),
        CheckConstraint(
            "p3 <= p15 AND p15 <= p50 AND p50 <= p85 AND p85 <= p97",
            name="ck_norme_percentiles_ordre",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<NormeOMS(sexe='{self.sexe}', age_mois={self.age_mois}, "
            f"type='{self.type_mesure}', p50={self.p50})>"
        )
