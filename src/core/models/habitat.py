"""
Modèles SQLAlchemy pour l'habitat et l'équipement maison.

Contient :
- Furniture : Wishlist meubles par pièce
- HouseStock : Stock consommables maison (ampoules, piles, produits)
- MaintenanceTask : Tâches entretien planifiées
- EcoAction : Actions écologiques avec économies
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class FurnitureStatus(str, Enum):
    """Statut d'un meuble dans la wishlist."""

    SOUHAITE = "souhaite"  # On le veut
    RECHERCHE = "recherche"  # On cherche activement
    TROUVE = "trouve"  # Trouvé, à acheter
    COMMANDE = "commande"  # Commandé
    ACHETE = "achete"  # Acheté
    ANNULE = "annule"  # Annulé


class FurniturePriority(str, Enum):
    """Priorité d'achat."""

    URGENT = "urgent"  # Besoin immédiat
    HAUTE = "haute"  # Important
    NORMALE = "normale"  # Quand on peut
    BASSE = "basse"  # Pas pressé
    PLUS_TARD = "plus_tard"  # Un jour...


class EcoActionType(str, Enum):
    """Type d'action écologique."""

    LAVABLE = "lavable"  # Passage au lavable (essuie-tout, serviettes)
    ENERGIE = "energie"  # Économie énergie
    EAU = "eau"  # Économie eau
    DECHETS = "dechets"  # Réduction déchets
    ALIMENTATION = "alimentation"  # Bio, local, etc.
    AUTRE = "autre"


class RoomType(str, Enum):
    """Pièces de la maison."""

    SALON = "salon"
    CUISINE = "cuisine"
    CHAMBRE_PARENTALE = "chambre_parentale"
    CHAMBRE_JULES = "chambre_jules"
    CHAMBRE_AMIS = "chambre_amis"
    SALLE_DE_BAIN = "salle_de_bain"
    WC = "wc"
    ENTREE = "entree"
    COULOIR = "couloir"
    GARAGE = "garage"
    BUANDERIE = "buanderie"
    BUREAU = "bureau"
    TERRASSE = "terrasse"
    JARDIN = "jardin"
    AUTRE = "autre"


# ═══════════════════════════════════════════════════════════
# MEUBLES - WISHLIST
# ═══════════════════════════════════════════════════════════


class Furniture(Base):
    """Meuble dans la wishlist.

    Pour gérer les achats progressifs de meubles avec budget.
    """

    __tablename__ = "furniture"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Infos meuble
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    piece: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # RoomType
    categorie: Mapped[str | None] = mapped_column(
        String(100)
    )  # Rangement, Assise, Table, Lit, etc.

    # Budget
    prix_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    prix_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    prix_reel: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Statut et priorité
    statut: Mapped[str] = mapped_column(String(20), default="souhaite", index=True)
    priorite: Mapped[str] = mapped_column(String(20), default="normale", index=True)

    # Où acheter
    magasin: Mapped[str | None] = mapped_column(String(200))  # IKEA, Maisons du Monde, etc.
    url: Mapped[str | None] = mapped_column(String(500))
    reference: Mapped[str | None] = mapped_column(String(100))

    # Dimensions (optionnel)
    largeur_cm: Mapped[int | None] = mapped_column(Integer)
    hauteur_cm: Mapped[int | None] = mapped_column(Integer)
    profondeur_cm: Mapped[int | None] = mapped_column(Integer)

    # Dates
    date_souhait: Mapped[date] = mapped_column(Date, default=date.today)
    date_achat: Mapped[date | None] = mapped_column(Date)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Furniture(id={self.id}, nom='{self.nom}', piece='{self.piece}')>"


# ═══════════════════════════════════════════════════════════
# STOCK CONSOMMABLES MAISON
# ═══════════════════════════════════════════════════════════


class HouseStock(Base):
    """Stock de consommables maison (ampoules, piles, produits ménagers).

    Pour ne plus être à court et éviter les doublons avec courses.
    """

    __tablename__ = "house_stocks"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Infos produit
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # Categories: electricite (ampoules, piles), menage (produits), bricolage, jardin, autre

    # Stock
    quantite: Mapped[int] = mapped_column(Integer, default=0)
    unite: Mapped[str] = mapped_column(String(20), default="unité")
    seuil_alerte: Mapped[int] = mapped_column(Integer, default=1)  # Alerte si <= seuil

    # Où c'est rangé
    emplacement: Mapped[str | None] = mapped_column(String(200))  # "Garage étagère 2"

    # Prix moyen (pour budget)
    prix_unitaire: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<HouseStock(id={self.id}, nom='{self.nom}', qte={self.quantite})>"


# ═══════════════════════════════════════════════════════════
# TÂCHES ENTRETIEN PLANIFIÉES
# ═══════════════════════════════════════════════════════════


class MaintenanceTask(Base):
    """Tâche d'entretien planifiée (ménage, maintenance, rangement).

    Pour gérer le bordel : vitres, tri caisses, garage, médicaments...
    Intégration possible avec le planning général.
    """

    __tablename__ = "maintenance_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Infos tâche
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: menage, rangement, maintenance, reparation, tri, vitres, garage, securite, entretien

    piece: Mapped[str | None] = mapped_column(String(50))  # RoomType

    # Fréquence (jours) - NULL = ponctuel
    frequence_jours: Mapped[int | None] = mapped_column(Integer)

    # Dates
    derniere_fois: Mapped[date | None] = mapped_column(Date)
    prochaine_fois: Mapped[date | None] = mapped_column(Date, index=True)

    # Durée estimée (minutes) pour planning
    duree_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # Responsable
    responsable: Mapped[str | None] = mapped_column(String(50))  # anne, mathieu, tous

    # Priorité et statut
    priorite: Mapped[str] = mapped_column(String(20), default="normale")
    fait: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Intégration planning
    integrer_planning: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<MaintenanceTask(id={self.id}, nom='{self.nom}', fait={self.fait})>"


# ═══════════════════════════════════════════════════════════
# ACTIONS ÉCOLOGIQUES
# ═══════════════════════════════════════════════════════════


class EcoAction(Base):
    """Action écologique avec suivi des économies.

    Pour tracker le passage au lavable, économies d'énergie, etc.
    """

    __tablename__ = "eco_actions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Infos action
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Ce qu'on remplace
    ancien_produit: Mapped[str | None] = mapped_column(String(200))  # Ex: "Essuie-tout jetable"
    nouveau_produit: Mapped[str | None] = mapped_column(String(200))  # Ex: "Essuie-tout lavable"

    # Économies estimées
    cout_ancien_mensuel: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )  # Coût mensuel ancien
    cout_nouveau_initial: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )  # Investissement initial
    economie_mensuelle: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))  # Économie/mois

    # Dates
    date_debut: Mapped[date] = mapped_column(Date, default=date.today)

    # Statut
    actif: Mapped[bool] = mapped_column(Boolean, default=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Propriété de compatibilité (UI utilise cout_initial)
    @property
    def cout_initial(self) -> Decimal | None:
        """Alias pour cout_nouveau_initial (compatibilité UI)."""
        return self.cout_nouveau_initial

    @cout_initial.setter
    def cout_initial(self, value: Decimal | None) -> None:
        """Setter pour cout_nouveau_initial via alias."""
        self.cout_nouveau_initial = value

    def __repr__(self) -> str:
        return f"<EcoAction(id={self.id}, nom='{self.nom}', type='{self.type_action}')>"
