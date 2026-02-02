"""
Modèles étendus pour la maison - Meubles, Dépenses, Éco-Tips.

Nouveaux modèles (refonte 2026-02):
- Furniture: Wishlist meubles par pièce
- HouseExpense: Suivi dépenses (gaz, eau, électricité, etc.)
- EcoAction: Actions écologiques avec économies
- GardenZone: Zones du jardin (2600m²)
- MaintenanceTask: Tâches entretien planifiées
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════

class FurnitureStatus(str, Enum):
    """Statut d'un meuble dans la wishlist"""
    SOUHAITE = "souhaite"      # On le veut
    RECHERCHE = "recherche"    # On cherche activement
    TROUVE = "trouve"          # Trouvé, à acheter
    COMMANDE = "commande"      # Commandé
    ACHETE = "achete"          # Acheté
    ANNULE = "annule"          # Annulé


class FurniturePriority(str, Enum):
    """Priorité d'achat"""
    URGENT = "urgent"          # Besoin immédiat
    HAUTE = "haute"            # Important
    NORMALE = "normale"        # Quand on peut
    BASSE = "basse"            # Pas pressé
    PLUS_TARD = "plus_tard"    # Un jour...


class ExpenseCategory(str, Enum):
    """Catégorie de dépense maison"""
    GAZ = "gaz"
    ELECTRICITE = "electricite"
    EAU = "eau"
    INTERNET = "internet"
    LOYER = "loyer"
    ASSURANCE = "assurance"
    TAXE_FONCIERE = "taxe_fonciere"
    TAXE_HABITATION = "taxe_habitation"
    CRECHE = "creche"
    NOURRITURE = "nourriture"
    TRAVAUX = "travaux"
    JARDIN = "jardin"
    AUTRE = "autre"


class GardenZoneType(str, Enum):
    """Type de zone jardin"""
    PELOUSE = "pelouse"
    POTAGER = "potager"
    ARBRES = "arbres"
    PISCINE = "piscine"
    TERRAIN_BOULES = "terrain_boules"
    TERRASSE = "terrasse"
    ALLEE = "allee"
    AUTRE = "autre"


class EcoActionType(str, Enum):
    """Type d'action écologique"""
    LAVABLE = "lavable"        # Passage au lavable (essuie-tout, serviettes)
    ENERGIE = "energie"        # Économie énergie
    EAU = "eau"                # Économie eau
    DECHETS = "dechets"        # Réduction déchets
    ALIMENTATION = "alimentation"  # Bio, local, etc.
    AUTRE = "autre"


class RoomType(str, Enum):
    """Pièces de la maison"""
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
    description: Mapped[Optional[str]] = mapped_column(Text)
    piece: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # RoomType
    categorie: Mapped[Optional[str]] = mapped_column(String(100))  # Rangement, Assise, Table, Lit, etc.
    
    # Budget
    prix_estime: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    prix_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    prix_reel: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Statut et priorité
    statut: Mapped[str] = mapped_column(String(20), default="souhaite", index=True)
    priorite: Mapped[str] = mapped_column(String(20), default="normale", index=True)
    
    # Où acheter
    magasin: Mapped[Optional[str]] = mapped_column(String(200))  # IKEA, Maisons du Monde, etc.
    url: Mapped[Optional[str]] = mapped_column(String(500))
    reference: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Dimensions (optionnel)
    largeur_cm: Mapped[Optional[int]] = mapped_column(Integer)
    hauteur_cm: Mapped[Optional[int]] = mapped_column(Integer)
    profondeur_cm: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Dates
    date_souhait: Mapped[date] = mapped_column(Date, default=date.today)
    date_achat: Mapped[Optional[date]] = mapped_column(Date)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Furniture(id={self.id}, nom='{self.nom}', piece='{self.piece}')>"


# ═══════════════════════════════════════════════════════════
# DÉPENSES MAISON
# ═══════════════════════════════════════════════════════════

class HouseExpense(Base):
    """Dépense récurrente ou ponctuelle de la maison.
    
    Pour suivre gaz, eau, électricité, loyer, crèche, etc.
    """
    __tablename__ = "house_expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Catégorie et période
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    mois: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    annee: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Montant
    montant: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Consommation (pour gaz, eau, électricité)
    consommation: Mapped[Optional[float]] = mapped_column(Float)  # kWh, m³, litres
    unite_consommation: Mapped[Optional[str]] = mapped_column(String(20))  # kWh, m³, L
    
    # Fournisseur
    fournisseur: Mapped[Optional[str]] = mapped_column(String(200))
    numero_contrat: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HouseExpense(id={self.id}, cat='{self.categorie}', montant={self.montant})>"


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
    description: Mapped[Optional[str]] = mapped_column(Text)
    type_action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Ce qu'on remplace
    ancien_produit: Mapped[Optional[str]] = mapped_column(String(200))  # Ex: "Essuie-tout jetable"
    nouveau_produit: Mapped[Optional[str]] = mapped_column(String(200))  # Ex: "Essuie-tout lavable"
    
    # Économies estimées
    cout_ancien_mensuel: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))  # Coût mensuel ancien
    cout_nouveau_initial: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))  # Investissement initial
    economie_mensuelle: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))  # Économie/mois
    
    # Dates
    date_debut: Mapped[date] = mapped_column(Date, default=date.today)
    
    # Statut
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<EcoAction(id={self.id}, nom='{self.nom}', type='{self.type_action}')>"


# ═══════════════════════════════════════════════════════════
# ZONES JARDIN (pour 2600m²)
# ═══════════════════════════════════════════════════════════

class GardenZone(Base):
    """Zone du jardin avec état et plan d'action.
    
    Pour gérer un grand jardin (2600m²) par zones.
    """
    __tablename__ = "garden_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Infos zone
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    surface_m2: Mapped[Optional[int]] = mapped_column(Integer)
    
    # État actuel (1-5)
    etat_note: Mapped[int] = mapped_column(Integer, default=1)  # 1=catastrophe, 5=parfait
    etat_description: Mapped[Optional[str]] = mapped_column(Text)  # "Herbe jaune, pas entretenu"
    
    # Plan de remise en état
    objectif: Mapped[Optional[str]] = mapped_column(Text)  # "Pelouse verte et tondue"
    budget_estime: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Prochaine action
    prochaine_action: Mapped[Optional[str]] = mapped_column(String(200))
    date_prochaine_action: Mapped[Optional[date]] = mapped_column(Date)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GardenZone(id={self.id}, nom='{self.nom}', etat={self.etat_note}/5)>"


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
    description: Mapped[Optional[str]] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: menage, rangement, maintenance, reparation, tri, vitres, garage, securite, entretien
    
    piece: Mapped[Optional[str]] = mapped_column(String(50))  # RoomType
    
    # Fréquence (jours) - NULL = ponctuel
    frequence_jours: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Dates
    derniere_fois: Mapped[Optional[date]] = mapped_column(Date)
    prochaine_fois: Mapped[Optional[date]] = mapped_column(Date, index=True)
    
    # Durée estimée (minutes) pour planning
    duree_minutes: Mapped[int] = mapped_column(Integer, default=30)
    
    # Responsable
    responsable: Mapped[Optional[str]] = mapped_column(String(50))  # anne, mathieu, tous
    
    # Priorité et statut
    priorite: Mapped[str] = mapped_column(String(20), default="normale")
    fait: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Intégration planning
    integrer_planning: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MaintenanceTask(id={self.id}, nom='{self.nom}', fait={self.fait})>"


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
    emplacement: Mapped[Optional[str]] = mapped_column(String(200))  # "Garage étagère 2"
    
    # Prix moyen (pour budget)
    prix_unitaire: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<HouseStock(id={self.id}, nom='{self.nom}', qte={self.quantite})>"
