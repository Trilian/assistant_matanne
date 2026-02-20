"""
Modèles SQLAlchemy pour le suivi du temps d'entretien et jardinage.

Contient :
- SessionTravail : Sessions de travail avec chronomètre
- VersionPiece : Historique des modifications de pièces
- CoutTravaux : Coûts des travaux par pièce
- LogStatutObjet : Historique des changements de statut d'objets
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, utc_now

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class TypeActiviteEntretien(StrEnum):
    """Types d'activités d'entretien/jardinage."""

    # Jardin
    ARROSAGE = "arrosage"
    TONTE = "tonte"
    TAILLE = "taille"
    DESHERBAGE = "desherbage"
    PLANTATION = "plantation"
    RECOLTE = "recolte"
    COMPOST = "compost"
    TRAITEMENT = "traitement"

    # Ménage intérieur
    MENAGE_GENERAL = "menage_general"
    ASPIRATEUR = "aspirateur"
    LAVAGE_SOL = "lavage_sol"
    POUSSIERE = "poussiere"
    VITRES = "vitres"
    LESSIVE = "lessive"
    REPASSAGE = "repassage"

    # Entretien maison
    BRICOLAGE = "bricolage"
    PEINTURE = "peinture"
    PLOMBERIE = "plomberie"
    ELECTRICITE = "electricite"
    NETTOYAGE_EXTERIEUR = "nettoyage_exterieur"

    # Autres
    RANGEMENT = "rangement"
    ADMINISTRATIF = "administratif"
    AUTRE = "autre"


class TypeModificationPiece(StrEnum):
    """Types de modifications de pièce."""

    AJOUT_MEUBLE = "ajout_meuble"
    RETRAIT_MEUBLE = "retrait_meuble"
    DEPLACEMENT = "deplacement"
    RENOVATION = "renovation"
    PEINTURE = "peinture"
    AMENAGEMENT = "amenagement"
    REPARATION = "reparation"


class StatutObjet(StrEnum):
    """Statut d'un objet dans l'inventaire."""

    FONCTIONNE = "fonctionne"
    A_REPARER = "a_reparer"
    A_CHANGER = "a_changer"
    A_ACHETER = "a_acheter"
    EN_COMMANDE = "en_commande"
    HORS_SERVICE = "hors_service"
    A_DONNER = "a_donner"
    ARCHIVE = "archive"


class PrioriteRemplacement(StrEnum):
    """Priorité pour remplacement d'objet."""

    URGENTE = "urgente"
    HAUTE = "haute"
    NORMALE = "normale"
    BASSE = "basse"
    FUTURE = "future"


# ═══════════════════════════════════════════════════════════
# SESSION DE TRAVAIL (CHRONOMÈTRE)
# ═══════════════════════════════════════════════════════════


class SessionTravail(Base):
    """Session de travail avec chronomètre.

    Permet de tracker le temps passé sur chaque activité
    d'entretien ou de jardinage.

    Attributes:
        type_activite: Type d'activité (tonte, ménage, etc.)
        zone_jardin_id: Zone jardin concernée (optionnel)
        piece_id: Pièce concernée (optionnel)
        description: Description libre
        debut: Date/heure de début
        fin: Date/heure de fin
        duree_minutes: Durée calculée en minutes
        notes: Notes après session
        difficulte: Niveau de difficulté ressenti (1-5)
        satisfaction: Niveau de satisfaction (1-5)
    """

    __tablename__ = "sessions_travail"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Type et contexte
    type_activite: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    zone_jardin_id: Mapped[int | None] = mapped_column(Integer, index=True)
    piece_id: Mapped[int | None] = mapped_column(Integer, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Temps
    debut: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fin: Mapped[datetime | None] = mapped_column(DateTime)
    duree_minutes: Mapped[int | None] = mapped_column(Integer)

    # Feedback
    notes: Mapped[str | None] = mapped_column(Text)
    difficulte: Mapped[int | None] = mapped_column(Integer)
    satisfaction: Mapped[int | None] = mapped_column(Integer)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    __table_args__ = (
        CheckConstraint(
            "difficulte IS NULL OR (difficulte >= 1 AND difficulte <= 5)", name="ck_difficulte_1_5"
        ),
        CheckConstraint(
            "satisfaction IS NULL OR (satisfaction >= 1 AND satisfaction <= 5)",
            name="ck_satisfaction_1_5",
        ),
        CheckConstraint("duree_minutes IS NULL OR duree_minutes >= 0", name="ck_duree_positive"),
    )

    def __repr__(self) -> str:
        return f"<SessionTravail(id={self.id}, type='{self.type_activite}', duree={self.duree_minutes}min)>"


# ═══════════════════════════════════════════════════════════
# VERSIONING PIÈCES
# ═══════════════════════════════════════════════════════════


class VersionPiece(Base):
    """Historique des versions/modifications d'une pièce.

    Permet de garder un historique des réorganisations,
    rénovations et modifications d'une pièce.

    Attributes:
        piece_id: ID de la pièce concernée
        version: Numéro de version
        type_modification: Type de modification effectuée
        titre: Titre de la version
        description: Description des changements
        date_modification: Date de la modification
        cout_total: Coût total de la modification
        photo_avant_url: URL photo avant travaux
        photo_apres_url: URL photo après travaux
    """

    __tablename__ = "versions_pieces"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Pièce et version
    piece_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    type_modification: Mapped[str] = mapped_column(String(50), nullable=False)

    # Détails
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    date_modification: Mapped[date] = mapped_column(Date, nullable=False)

    # Coûts
    cout_total: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Photos
    photo_avant_url: Mapped[str | None] = mapped_column(String(500))
    photo_apres_url: Mapped[str | None] = mapped_column(String(500))

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    cree_par: Mapped[str | None] = mapped_column(String(100))

    # Relations
    couts: Mapped[list["CoutTravaux"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<VersionPiece(piece={self.piece_id}, v{self.version}, titre='{self.titre}')>"


class CoutTravaux(Base):
    """Détail des coûts pour une version de pièce.

    Permet de détailler les coûts entre main d'œuvre
    et matériaux pour chaque modification.

    Attributes:
        version_id: ID de la version de pièce
        categorie: Catégorie de coût (main_oeuvre, materiaux, etc.)
        libelle: Libellé du coût
        montant: Montant en euros
        fournisseur: Fournisseur/prestataire
        facture_ref: Référence facture
    """

    __tablename__ = "couts_travaux"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Lien version
    version_id: Mapped[int] = mapped_column(
        ForeignKey("versions_pieces.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Détails coût
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)  # main_oeuvre, materiaux
    libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    montant: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Infos complémentaires
    fournisseur: Mapped[str | None] = mapped_column(String(200))
    facture_ref: Mapped[str | None] = mapped_column(String(100))
    date_paiement: Mapped[date | None] = mapped_column(Date)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Relations
    version: Mapped["VersionPiece"] = relationship(back_populates="couts")

    __table_args__ = (CheckConstraint("montant >= 0", name="ck_montant_positif"),)

    def __repr__(self) -> str:
        return f"<CoutTravaux(id={self.id}, libelle='{self.libelle}', montant={self.montant}€)>"


# ═══════════════════════════════════════════════════════════
# LOG STATUT OBJETS
# ═══════════════════════════════════════════════════════════


class LogStatutObjet(Base):
    """Historique des changements de statut d'un objet.

    Permet de tracer l'évolution des objets (fonctionnel → à changer → acheté).

    Attributes:
        objet_id: ID de l'objet concerné
        ancien_statut: Statut avant changement
        nouveau_statut: Nouveau statut
        raison: Raison du changement
        prix_estime: Prix estimé de remplacement
        priorite: Priorité de remplacement
        ajoute_courses: Si ajouté à la liste de courses
        ajoute_budget: Si ajouté au budget
    """

    __tablename__ = "logs_statut_objets"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Objet concerné
    objet_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Changement de statut
    ancien_statut: Mapped[str | None] = mapped_column(String(50))
    nouveau_statut: Mapped[str] = mapped_column(String(50), nullable=False)
    raison: Mapped[str | None] = mapped_column(Text)

    # Infos remplacement
    prix_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    priorite: Mapped[str | None] = mapped_column(String(20))

    # Actions déclenchées
    ajoute_courses: Mapped[bool | None] = mapped_column(default=False)
    ajoute_budget: Mapped[bool | None] = mapped_column(default=False)

    # Métadonnées
    date_changement: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    change_par: Mapped[str | None] = mapped_column(String(100))

    def __repr__(self) -> str:
        return (
            f"<LogStatutObjet(objet={self.objet_id}, {self.ancien_statut}→{self.nouveau_statut})>"
        )


# ═══════════════════════════════════════════════════════════
# PIÈCES ET OBJETS MAISON (compléments)
# ═══════════════════════════════════════════════════════════


class PieceMaison(Base):
    """Pièce de la maison avec ses caractéristiques.

    Attributes:
        nom: Nom de la pièce
        etage: Étage (0=RDC, 1=1er, etc.)
        superficie_m2: Surface en m²
        type_piece: Type (chambre, salon, etc.)
        description: Description
    """

    __tablename__ = "pieces_maison"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    etage: Mapped[int] = mapped_column(Integer, default=0)
    superficie_m2: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    type_piece: Mapped[str | None] = mapped_column(String(50), index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relations
    objets: Mapped[list["ObjetMaison"]] = relationship(
        back_populates="piece", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PieceMaison(id={self.id}, nom='{self.nom}', etage={self.etage})>"


class ObjetMaison(Base):
    """Objet/équipement dans une pièce.

    Attributes:
        piece_id: Pièce contenant l'objet
        nom: Nom de l'objet
        categorie: Catégorie (électroménager, meuble, etc.)
        statut: Statut actuel (fonctionne, à_changer, etc.)
        priorite_remplacement: Priorité si à remplacer
        date_achat: Date d'achat
        prix_achat: Prix d'achat
        prix_remplacement_estime: Prix estimé de remplacement
        marque: Marque
        modele: Modèle
        notes: Notes
    """

    __tablename__ = "objets_maison"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Localisation
    piece_id: Mapped[int] = mapped_column(
        ForeignKey("pieces_maison.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str | None] = mapped_column(String(50), index=True)

    # Statut
    statut: Mapped[str] = mapped_column(String(50), default="fonctionne", index=True)
    priorite_remplacement: Mapped[str | None] = mapped_column(String(20))

    # Infos achat
    date_achat: Mapped[date | None] = mapped_column(Date)
    prix_achat: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    prix_remplacement_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Détails produit
    marque: Mapped[str | None] = mapped_column(String(100))
    modele: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relations
    piece: Mapped["PieceMaison"] = relationship(back_populates="objets")

    def __repr__(self) -> str:
        return f"<ObjetMaison(id={self.id}, nom='{self.nom}', statut='{self.statut}')>"


# ═══════════════════════════════════════════════════════════
# ZONES JARDIN
# ═══════════════════════════════════════════════════════════


class ZoneJardin(Base):
    """Zone du jardin (potager, pelouse, massif, etc.).

    Attributes:
        nom: Nom de la zone
        type_zone: Type (potager, pelouse, massif, verger...)
        superficie_m2: Surface en m²
        exposition: Exposition (N, S, E, O)
        type_sol: Type de sol
        arrosage_auto: Si arrosage automatique installé
        etat_note: État actuel (1=catastrophe, 5=parfait)
        etat_description: Description de l'état actuel
        objectif: Objectif de remise en état
        budget_estime: Budget estimé pour travaux
        prochaine_action: Prochaine action à effectuer
        date_prochaine_action: Date prévue
        photos_url: URLs des photos avant/après
    """

    __tablename__ = "zones_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Lien avec le plan jardin (optionnel)
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("plans_jardin.id", ondelete="SET NULL"), index=True
    )

    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    type_zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    superficie_m2: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    exposition: Mapped[str | None] = mapped_column(String(10))
    type_sol: Mapped[str | None] = mapped_column(String(50))
    arrosage_auto: Mapped[bool] = mapped_column(default=False)

    description: Mapped[str | None] = mapped_column(Text)

    # État et suivi (champs migrés de GardenZone)
    etat_note: Mapped[int] = mapped_column(Integer, default=3)  # 1=catastrophe, 5=parfait
    etat_description: Mapped[str | None] = mapped_column(Text)  # "Herbe jaune, pas entretenu"
    objectif: Mapped[str | None] = mapped_column(Text)  # "Pelouse verte et tondue"
    budget_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    prochaine_action: Mapped[str | None] = mapped_column(String(200))
    date_prochaine_action: Mapped[date | None] = mapped_column(Date)
    photos_url: Mapped[list[str] | None] = mapped_column(
        JSON, default=list
    )  # ["avant:url", "apres:url"]

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relations
    plantes: Mapped[list["PlanteJardin"]] = relationship(
        back_populates="zone", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ZoneJardin(id={self.id}, nom='{self.nom}', type='{self.type_zone}', etat={self.etat_note}/5)>"


class PlanteJardin(Base):
    """Plante dans une zone du jardin.

    Attributes:
        zone_id: Zone contenant la plante
        nom: Nom de la plante
        variete: Variété spécifique
        etat: État de santé (excellent, bon, attention, probleme)
        date_plantation: Date de plantation
        mois_semis: Mois de semis (JSON array)
        mois_recolte: Mois de récolte (JSON array)
        arrosage: Fréquence d'arrosage
    """

    __tablename__ = "plantes_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Localisation
    zone_id: Mapped[int] = mapped_column(
        ForeignKey("zones_jardin.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identification
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    variete: Mapped[str | None] = mapped_column(String(100))

    # État
    etat: Mapped[str] = mapped_column(String(20), default="bon")

    # Position sur le plan (optionnel, pour affichage 2D)
    position_x: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    position_y: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

    # Dates
    date_plantation: Mapped[date | None] = mapped_column(Date)
    mois_semis: Mapped[str | None] = mapped_column(String(100))  # JSON array: "[3,4,5]"
    mois_recolte: Mapped[str | None] = mapped_column(String(100))  # JSON array: "[7,8,9]"

    # Entretien
    arrosage: Mapped[str | None] = mapped_column(String(50))  # quotidien, hebdo, etc.
    notes: Mapped[str | None] = mapped_column(Text)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relations
    zone: Mapped["ZoneJardin"] = relationship(back_populates="plantes")
    actions: Mapped[list["ActionPlante"]] = relationship(
        back_populates="plante", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PlanteJardin(id={self.id}, nom='{self.nom}', etat='{self.etat}')>"


# ═══════════════════════════════════════════════════════════
# PLAN JARDIN
# ═══════════════════════════════════════════════════════════


class PlanJardin(Base):
    """Plan 2D du jardin avec ses dimensions.

    Attributes:
        nom: Nom du plan
        largeur: Largeur en mètres
        hauteur: Hauteur en mètres
        description: Description du plan
    """

    __tablename__ = "plans_jardin"

    id: Mapped[int] = mapped_column(primary_key=True)

    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    largeur: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    hauteur: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)

    # Relations
    zones: Mapped[list["ZoneJardin"]] = relationship(
        foreign_keys="ZoneJardin.plan_id",
        backref="plan",
    )

    def __repr__(self) -> str:
        return f"<PlanJardin(id={self.id}, nom='{self.nom}', {self.largeur}x{self.hauteur}m)>"


# ═══════════════════════════════════════════════════════════
# ACTIONS PLANTES
# ═══════════════════════════════════════════════════════════


class ActionPlante(Base):
    """Historique des actions effectuées sur une plante.

    Attributes:
        plante_id: Plante concernée
        type_action: Type d'action (arrosage, taille, récolte, traitement...)
        date_action: Date de l'action
        quantite: Quantité (pour récoltes)
        notes: Notes supplémentaires
    """

    __tablename__ = "actions_plantes"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Lien plante
    plante_id: Mapped[int] = mapped_column(
        ForeignKey("plantes_jardin.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Détails action
    type_action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date_action: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    quantite: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    # Relations
    plante: Mapped["PlanteJardin"] = relationship(back_populates="actions")

    def __repr__(self) -> str:
        return f"<ActionPlante(id={self.id}, plante={self.plante_id}, type='{self.type_action}')>"
