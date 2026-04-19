"""
Modèles pour le Batch Cooking.

Contient :
- SessionBatchCooking : Session de batch cooking planifiée
- EtapeBatchCooking : Étape d'une session avec timer et robots
- PreparationBatch : Plat préparé stocké (frigo/congélateur)
- ConfigBatchCooking : Configuration utilisateur batch cooking
- RobotCuisine : Robots/appareils disponibles
"""

import enum
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampMixin

# ═══════════════════════════════════════════════════════════
# ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════


class StatutSessionEnum(enum.StrEnum):
    """Statut d'une session batch cooking."""

    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class StatutEtapeEnum(enum.StrEnum):
    """Statut d'une étape batch cooking."""

    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    PASSEE = "passee"  # Sautée


class TypeRobotEnum(enum.StrEnum):
    """Types de robots/appareils de cuisine."""

    COOKEO = "cookeo"
    MONSIEUR_CUISINE = "monsieur_cuisine"
    AIRFRYER = "airfryer"
    MULTICOOKER = "multicooker"
    FOUR = "four"
    PLAQUES = "plaques"
    ROBOT_PATISSIER = "robot_patissier"
    MIXEUR = "mixeur"
    HACHOIR = "hachoir"


class LocalisationStockageEnum(enum.StrEnum):
    """Localisation du stockage des préparations."""

    FRIGO = "frigo"
    CONGELATEUR = "congelateur"
    TEMPERATURE_AMBIANTE = "temperature_ambiante"


# ═══════════════════════════════════════════════════════════
# CONFIGURATION BATCH COOKING
# ═══════════════════════════════════════════════════════════


class ConfigBatchCooking(TimestampMixin, Base):
    """Configuration utilisateur pour le batch cooking.

    Attributes:
        jours_batch: Jours de la semaine pour le batch (0=lundi...6=dimanche)
        heure_debut_preferee: Heure de début habituelle
        duree_max_session: Durée maximale souhaitée (minutes)
        avec_jules: Si Jules (bébé) participe par défaut
        robots_disponibles: Liste des robots disponibles (JSON)
        preferences_stockage: Préférences de stockage (JSON)
        notes: Notes personnelles
    """

    __tablename__ = "config_batch_cooking"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Jours préférés (stockés en JSON: [2, 6] pour mercredi=2 et dimanche=6)
    jours_batch: Mapped[list[int]] = mapped_column(
        JSONB, default=lambda: [2, 6]
    )  # Mercredi + Dimanche par défaut
    heure_debut_preferee: Mapped[time | None] = mapped_column(Time, default=time(10, 0))
    duree_max_session: Mapped[int] = mapped_column(Integer, default=180)  # 3h par défaut

    # Mode famille
    avec_jules_par_defaut: Mapped[bool] = mapped_column(Boolean, default=True)

    # Équipement (JSON: ["cookeo", "airfryer", ...])
    robots_disponibles: Mapped[list[str]] = mapped_column(
        JSONB, default=lambda: ["four", "plaques"]
    )

    # Préférences stockage (frigo / congélateur / ambiant)
    preferences_stockage: Mapped[dict | None] = mapped_column(JSONB)

    # Couverture jours par session (ex: {"2": [2, 3, 4], "6": [6, 0, 1, 2]})
    # Mercredi (2) couvre mer+jeu+ven, Dimanche (6) couvre dim+lun+mar+mer_midi
    couverture_jours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Personnalisation
    objectif_portions_semaine: Mapped[int] = mapped_column(Integer, default=20)
    notes: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        CheckConstraint("duree_max_session > 0", name="ck_config_batch_duree_positive"),
        CheckConstraint("objectif_portions_semaine > 0", name="ck_config_batch_objectif_positif"),
    )

    def __repr__(self) -> str:
        return f"<ConfigBatchCooking(id={self.id}, jours={self.jours_batch})>"


# ═══════════════════════════════════════════════════════════
# SESSION BATCH COOKING
# ═══════════════════════════════════════════════════════════


class SessionBatchCooking(TimestampMixin, Base):
    """Session de batch cooking planifiée ou en cours.

    Attributes:
        nom: Nom de la session (ex: "Batch Dimanche 12/01")
        date_session: Date de la session
        heure_debut: Heure de début planifiée/réelle
        heure_fin: Heure de fin (réelle)
        duree_estimee: Durée estimée en minutes
        duree_reelle: Durée réelle en minutes
        statut: Statut de la session
        avec_jules: Si Jules participe à cette session
        planning_id: Lien vers le planning de la semaine (optionnel)
        recettes_selectionnees: IDs des recettes à préparer (JSON)
        robots_utilises: Robots utilisés pour cette session (JSON)
        notes_avant: Notes de préparation
        notes_apres: Retour d'expérience
        genere_par_ia: Si le plan a été généré par l'IA
    """

    __tablename__ = "sessions_batch_cooking"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)

    # Planning temporel
    date_session: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    heure_debut: Mapped[time | None] = mapped_column(Time)
    heure_fin: Mapped[time | None] = mapped_column(Time)
    duree_estimee: Mapped[int] = mapped_column(Integer, default=120)  # minutes
    duree_reelle: Mapped[int | None] = mapped_column(Integer)

    # Statut
    statut: Mapped[str] = mapped_column(
        String(20), default=StatutSessionEnum.PLANIFIEE.value, index=True
    )

    # Mode famille
    avec_jules: Mapped[bool] = mapped_column(Boolean, default=False)

    # Liens
    planning_id: Mapped[int | None] = mapped_column(
        ForeignKey("plannings.id", ondelete="SET NULL"), index=True
    )

    # Données session (JSON)
    recettes_selectionnees: Mapped[list[int] | None] = mapped_column(JSONB)
    robots_utilises: Mapped[list[str] | None] = mapped_column(JSONB)
    preparations_simples: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    # Notes
    notes_avant: Mapped[str | None] = mapped_column(Text)
    notes_apres: Mapped[str | None] = mapped_column(Text)

    # IA
    genere_par_ia: Mapped[bool] = mapped_column(Boolean, default=False)

    # Métriques
    nb_portions_preparees: Mapped[int] = mapped_column(Integer, default=0)
    nb_recettes_completees: Mapped[int] = mapped_column(Integer, default=0)

    # Relations
    etapes: Mapped[list["EtapeBatchCooking"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="EtapeBatchCooking.ordre"
    )
    preparations: Mapped[list["PreparationBatch"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_session_date_statut", "date_session", "statut"),
        CheckConstraint("duree_estimee > 0", name="ck_session_duree_estimee_positive"),
        CheckConstraint(
            "duree_reelle IS NULL OR duree_reelle > 0",
            name="ck_session_duree_reelle_positive",
        ),
        CheckConstraint("nb_portions_preparees >= 0", name="ck_session_portions_positive"),
        CheckConstraint("nb_recettes_completees >= 0", name="ck_session_recettes_positive"),
    )

    @property
    def est_en_cours(self) -> bool:
        """Vérifie si la session est en cours."""
        return self.statut == StatutSessionEnum.EN_COURS.value

    @property
    def progression(self) -> float:
        """Calcule le pourcentage de progression (0-100)."""
        if not self.etapes:
            return 0.0
        terminees = sum(1 for e in self.etapes if e.statut == StatutEtapeEnum.TERMINEE.value)
        return (terminees / len(self.etapes)) * 100

    def __repr__(self) -> str:
        return f"<SessionBatchCooking(id={self.id}, nom='{self.nom}', statut={self.statut})>"


# ═══════════════════════════════════════════════════════════
# ÉTAPES BATCH COOKING
# ═══════════════════════════════════════════════════════════


class EtapeBatchCooking(Base):
    """Étape d'une session de batch cooking.

    Chaque étape peut utiliser un ou plusieurs robots.
    Les étapes peuvent être parallélisées si elles utilisent des robots différents.

    Attributes:
        session_id: ID de la session parent
        recette_id: ID de la recette concernée (optionnel)
        ordre: Numéro d'ordre de l'étape
        groupe_parallele: Groupe pour parallélisation (même groupe = simultané)
        titre: Titre court de l'étape
        description: Description détaillée
        duree_minutes: Durée estimée en minutes
        duree_reelle: Durée réelle en minutes
        robots_requis: Liste des robots nécessaires (JSON)
        est_supervision: Étape de surveillance passive (ex: cuisson four)
        alerte_bruit: Si l'étape fait du bruit (important si Jules dort)
        temperature: Température requise (°C, optionnel)
        statut: Statut de l'étape
        heure_debut: Heure de début réelle
        heure_fin: Heure de fin réelle
        notes: Notes utilisateur
    """

    __tablename__ = "etapes_batch_cooking"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions_batch_cooking.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )

    # Ordre et parallélisation
    ordre: Mapped[int] = mapped_column(Integer, nullable=False)
    groupe_parallele: Mapped[int] = mapped_column(Integer, default=0)

    # Contenu
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Timing
    duree_minutes: Mapped[int] = mapped_column(Integer, default=10)
    duree_reelle: Mapped[int | None] = mapped_column(Integer)

    # Équipement (JSON: ["cookeo", "four"])
    robots_requis: Mapped[list[str] | None] = mapped_column(JSONB)

    # Caractéristiques
    est_supervision: Mapped[bool] = mapped_column(Boolean, default=False)
    alerte_bruit: Mapped[bool] = mapped_column(Boolean, default=False)
    temperature: Mapped[int | None] = mapped_column(Integer)  # °C

    # Statut et timing réel
    statut: Mapped[str] = mapped_column(String(20), default=StatutEtapeEnum.A_FAIRE.value)
    heure_debut: Mapped[datetime | None] = mapped_column(DateTime)
    heure_fin: Mapped[datetime | None] = mapped_column(DateTime)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timer actif
    timer_actif: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    session: Mapped["SessionBatchCooking"] = relationship(back_populates="etapes")

    __table_args__ = (
        Index("idx_etape_session_ordre", "session_id", "ordre"),
        CheckConstraint("ordre > 0", name="ck_etape_batch_ordre_positif"),
        CheckConstraint("duree_minutes > 0", name="ck_etape_batch_duree_positive"),
        CheckConstraint(
            "duree_reelle IS NULL OR duree_reelle > 0",
            name="ck_etape_batch_duree_reelle_positive",
        ),
    )

    @property
    def est_terminee(self) -> bool:
        """Vérifie si l'étape est terminée."""
        return self.statut == StatutEtapeEnum.TERMINEE.value

    @property
    def robots_liste(self) -> list[str]:
        """Retourne la liste des robots requis."""
        return self.robots_requis or []

    def __repr__(self) -> str:
        return f"<EtapeBatchCooking(id={self.id}, ordre={self.ordre}, titre='{self.titre}')>"


# ═══════════════════════════════════════════════════════════
# PRÉPARATIONS STOCKÉES
# ═══════════════════════════════════════════════════════════


class PreparationBatch(TimestampMixin, Base):
    """Préparation issue d'une session batch cooking.

    Suit les plats préparés avec leur localisation et péremption.

    Attributes:
        session_id: ID de la session d'origine
        recette_id: ID de la recette (optionnel)
        nom: Nom de la préparation
        description: Description
        portions_initiales: Nombre de portions créées
        portions_restantes: Nombre de portions restantes
        date_preparation: Date de préparation
        date_peremption: Date limite de consommation
        localisation: Où est stocké (frigo/congélateur)
        container: Description du container (ex: "Boîte bleue large")
        etagere: Position dans le frigo/congélateur
        repas_attribues: IDs des repas auxquels c'est attribué (JSON)
        notes: Notes utilisateur
        photo_url: URL de la photo (optionnel)
        consomme: Entièrement consommé
    """

    __tablename__ = "preparations_batch"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions_batch_cooking.id", ondelete="SET NULL"), index=True
    )
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Portions
    portions_initiales: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    portions_restantes: Mapped[int] = mapped_column(Integer, nullable=False, default=4)

    # Dates
    date_preparation: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_peremption: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Stockage
    localisation: Mapped[str] = mapped_column(
        String(50), default=LocalisationStockageEnum.FRIGO.value, index=True
    )
    container: Mapped[str | None] = mapped_column(String(100))
    etagere: Mapped[str | None] = mapped_column(String(50))

    # Utilisation planifiée (JSON: [repas_id, repas_id, ...])
    repas_attribues: Mapped[list[int] | None] = mapped_column(JSONB)

    # Métadonnées
    notes: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(500))

    # Statut
    consomme: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Relations
    session: Mapped[Optional["SessionBatchCooking"]] = relationship(back_populates="preparations")

    __table_args__ = (
        Index("idx_prep_localisation_peremption", "localisation", "date_peremption"),
        Index("idx_prep_consomme_peremption", "consomme", "date_peremption"),
        CheckConstraint("portions_initiales > 0", name="ck_prep_portions_initiales_positive"),
        CheckConstraint("portions_restantes >= 0", name="ck_prep_portions_restantes_positive"),
    )

    @property
    def jours_avant_peremption(self) -> int:
        """Nombre de jours avant péremption."""
        return (self.date_peremption - date.today()).days

    @property
    def est_perime(self) -> bool:
        """Vérifie si la préparation est périmée."""
        return date.today() > self.date_peremption

    @property
    def alerte_peremption(self) -> bool:
        """Alerte si péremption dans moins de 2 jours."""
        return self.jours_avant_peremption <= 2 and not self.consomme

    def consommer_portion(self, nb: int = 1) -> int:
        """Consomme des portions et retourne le reste."""
        self.portions_restantes = max(0, self.portions_restantes - nb)
        if self.portions_restantes == 0:
            self.consomme = True
        return self.portions_restantes

    def __repr__(self) -> str:
        return f"<PreparationBatch(id={self.id}, nom='{self.nom}', portions={self.portions_restantes})>"


# ═══════════════════════════════════════════════════════════
# ARTICLES CONGELÉS (stock congélateur)
# ═══════════════════════════════════════════════════════════


class CategorieCongelationEnum(enum.StrEnum):
    """Catégories d'articles congelés."""

    PLAT_CUISINE = "plat cuisine"
    PLAT = "plat"
    VIANDE_CRUE = "viande crue"
    VIANDE_CUITE = "viande cuite"
    VOLAILLE_CRUE = "volaille crue"
    VOLAILLE_CUITE = "volaille cuite"
    POISSON_CRU = "poisson cru"
    POISSON_CUIT = "poisson cuit"
    LEGUME_BLANCHI = "légume blanchi"
    LEGUME_CRU = "légume cru"
    FRUIT = "fruit"
    SAUCE = "sauce"
    BOUILLON = "bouillon"
    PAIN = "pain"
    PATE = "pâte"
    DESSERT = "dessert"
    FROMAGE = "fromage"
    BEURRE = "beurre"
    HERBES = "herbes"
    AUTRE = "autre"


class BatchCookingCongelation(TimestampMixin, Base):
    """Article stocké au congélateur.

    Table SQL: batch_cooking_congelation
    Remplace le stockage en mémoire de congelation.py.

    Attributes:
        nom: Nom de l'article congelé
        date_congelation: Date de mise au congélateur
        date_limite: Date limite de conservation
        portions: Nombre de portions
        categorie: Catégorie de l'article
        recette_id: Lien vers la recette d'origine
        session_id: Lien vers la session batch cooking
        notes: Notes additionnelles
        consomme: Si l'article a été entièrement consommé
        meta_donnees: Métadonnées additionnelles (JSON)
    """

    __tablename__ = "batch_cooking_congelation"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    date_congelation: Mapped[date] = mapped_column(Date, nullable=False)
    date_limite: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    portions: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    categorie: Mapped[str] = mapped_column(String(50), default="autre")
    recette_id: Mapped[int | None] = mapped_column(
        ForeignKey("recettes.id", ondelete="SET NULL"), index=True
    )
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions_batch_cooking.id", ondelete="SET NULL"), index=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    consomme: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    meta_donnees: Mapped[dict | None] = mapped_column("metadata", JSONB)

    __table_args__ = (
        Index("idx_congelation_date_limite", "date_limite"),
        Index("idx_congelation_categorie", "categorie"),
        Index("idx_congelation_consomme_date", "consomme", "date_limite"),
        CheckConstraint("portions > 0", name="ck_congelation_portions_positive"),
    )

    @property
    def jours_restants(self) -> int:
        """Nombre de jours avant expiration."""
        return (self.date_limite - date.today()).days

    @property
    def urgence(self) -> int:
        """0=expiré, 1=urgent (<7j), 2=bientôt (<30j), 3=ok."""
        j = self.jours_restants
        if j < 0:
            return 0
        if j < 7:
            return 1
        if j < 30:
            return 2
        return 3

    def __repr__(self) -> str:
        return f"<BatchCookingCongelation(id={self.id}, nom='{self.nom}', urgence={self.urgence})>"
