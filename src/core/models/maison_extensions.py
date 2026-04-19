"""
Modèles SQLAlchemy pour cellier, diagnostics, checklists, nuisibles et devis.

Contient :
- ArticleCellier : Inventaire cellier (conserves, vins, congelés)
- DiagnosticMaison : Diagnostics immobiliers (DPE, amiante, etc.)
- EstimationImmobiliere : Estimation valeur du bien
- ChecklistVacances : Templates de checklists vacances
- ItemChecklist : Items d'une checklist
- TraitementNuisible : Suivi traitements nuisibles
- DevisComparatif : Devis artisans comparés
- LigneDevis : Lignes détaillées d'un devis
- EntretienSaisonnier : Catalogue entretiens saisonniers
- ReleveCompteur : Relevés de compteurs eau/énergie
- SimulationRenovation : Simulation de rénovation multi-scénarios
- ScenarioSimulation : Scénario d'une simulation (variante)
- PlanMaison : Plan 2D/3D sauvegardé (données canvas JSON)
- ZoneTerrain : Zone du terrain extérieur
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import CreeLeMixin, TimestampMixin

# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class CategorieCellier(StrEnum):
    """Catégorie d'article du cellier."""

    CONSERVE = "conserve"
    VIN = "vin"
    BIERE = "biere"
    SPIRITUEUX = "spiritueux"
    CONDIMENT = "condiment"
    EPICE = "epice"
    FARINE_CEREALE = "farine_cereale"
    LEGUMINEUSE = "legumineuse"
    PATE_RIZ = "pate_riz"
    HUILE = "huile"
    CONFITURE = "confiture"
    SURGELE = "surgele"
    BOISSON = "boisson"
    SNACK = "snack"
    BEBE = "bebe"
    AUTRE = "autre"


class TypeDiagnostic(StrEnum):
    """Type de diagnostic immobilier."""

    DPE = "dpe"
    AMIANTE = "amiante"
    PLOMB = "plomb"
    TERMITES = "termites"
    ELECTRICITE = "electricite"
    GAZ = "gaz"
    ERP = "erp"  # État des Risques et Pollutions
    ASSAINISSEMENT = "assainissement"
    SURFACE_CARREZ = "surface_carrez"
    AUDIT_ENERGETIQUE = "audit_energetique"
    AUTRE = "autre"


class SaisonEntretien(StrEnum):
    """Saison pour l'entretien saisonnier."""

    PRINTEMPS = "printemps"
    ETE = "ete"
    AUTOMNE = "automne"
    HIVER = "hiver"
    TOUTE_ANNEE = "toute_annee"


class TypeNuisible(StrEnum):
    """Type de nuisible."""

    FOURMIS = "fourmis"
    MOUSTIQUES = "moustiques"
    GUEPES = "guepes"
    SOURIS = "souris"
    RATS = "rats"
    CAFARDS = "cafards"
    PUCES = "puces"
    MITES = "mites"
    TERMITES = "termites"
    PUNAISES = "punaises"
    LIMACES = "limaces"
    TAUPES = "taupes"
    AUTRE = "autre"


class StatutDevis(StrEnum):
    """Statut d'un devis."""

    DEMANDE = "demande"
    RECU = "recu"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    EXPIRE = "expire"


# ═══════════════════════════════════════════════════════════
# CELLIER
# ═══════════════════════════════════════════════════════════


class ArticleCellier(TimestampMixin, Base):
    """Article stocké dans le cellier.

    Conserves, vins, produits secs, congelés avec DLC/DLUO.
    Intégration possible avec scan code-barres.
    """

    __tablename__ = "articles_cellier"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sous_categorie: Mapped[str | None] = mapped_column(String(100))
    marque: Mapped[str | None] = mapped_column(String(100))
    code_barres: Mapped[str | None] = mapped_column(String(50), index=True)

    # Stock
    quantite: Mapped[int] = mapped_column(Integer, default=1)
    unite: Mapped[str] = mapped_column(String(20), default="unité")
    seuil_alerte: Mapped[int] = mapped_column(Integer, default=1)

    # Dates
    date_achat: Mapped[date | None] = mapped_column(Date)
    dlc: Mapped[date | None] = mapped_column(Date, index=True)  # Date Limite de Consommation
    dluo: Mapped[date | None] = mapped_column(Date)  # Date Limite d'Utilisation Optimale

    # Emplacement
    emplacement: Mapped[str | None] = mapped_column(String(100))  # Étagère 1, Congélateur, etc.

    # Prix
    prix_unitaire: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ArticleCellier(id={self.id}, nom='{self.nom}', qte={self.quantite})>"


# ═══════════════════════════════════════════════════════════
# DIAGNOSTICS IMMOBILIERS (DPE)
# ═══════════════════════════════════════════════════════════


class DiagnosticMaison(TimestampMixin, Base):
    """Diagnostic immobilier (DPE, amiante, plomb, etc.).

    Carnet de santé de la maison avec alertes renouvellement.
    """

    __tablename__ = "diagnostics_maison"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Type et résultat
    type_diagnostic: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    resultat: Mapped[str | None] = mapped_column(String(100))  # Ex: "B" pour DPE
    resultat_detail: Mapped[str | None] = mapped_column(Text)  # Détails complets

    # Diagnostiqueur
    diagnostiqueur: Mapped[str | None] = mapped_column(String(200))
    numero_certification: Mapped[str | None] = mapped_column(String(100))

    # Dates
    date_realisation: Mapped[date] = mapped_column(Date, nullable=False)
    date_validite: Mapped[date | None] = mapped_column(Date, index=True)
    duree_validite_ans: Mapped[int | None] = mapped_column(Integer)  # En années

    # Scores (spécifique DPE)
    score_energie: Mapped[str | None] = mapped_column(String(5))  # A à G
    score_ges: Mapped[str | None] = mapped_column(String(5))  # A à G
    consommation_kwh_m2: Mapped[float | None] = mapped_column(Float)
    emission_co2_m2: Mapped[float | None] = mapped_column(Float)

    # Surface
    surface_m2: Mapped[float | None] = mapped_column(Float)

    # Documents
    document_path: Mapped[str | None] = mapped_column(String(500))

    # Alertes
    alerte_active: Mapped[bool] = mapped_column(Boolean, default=True)
    alerte_jours_avant: Mapped[int] = mapped_column(Integer, default=60)

    # Notes et recommandations
    recommandations: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<DiagnosticMaison(id={self.id}, type='{self.type_diagnostic}')>"


# ═══════════════════════════════════════════════════════════
# ESTIMATION IMMOBILIÈRE
# ═══════════════════════════════════════════════════════════


class EstimationImmobiliere(TimestampMixin, Base):
    """Estimation de la valeur immobilière du bien.

    Basée sur DVF, comparaisons locales, plus-values travaux.
    """

    __tablename__ = "estimations_immobilieres"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # dvf, agent, notaire, ia
    date_estimation: Mapped[date] = mapped_column(Date, nullable=False)

    # Valeurs
    valeur_basse: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    valeur_moyenne: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    valeur_haute: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    prix_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Contexte
    surface_m2: Mapped[float | None] = mapped_column(Float)
    nb_pieces: Mapped[int | None] = mapped_column(Integer)
    code_postal: Mapped[str | None] = mapped_column(String(10))
    commune: Mapped[str | None] = mapped_column(String(100))

    # Comparaison DVF
    nb_transactions_comparees: Mapped[int | None] = mapped_column(Integer)
    prix_m2_quartier: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    evolution_annuelle_pct: Mapped[float | None] = mapped_column(Float)

    # Plus-value travaux
    investissement_travaux: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    plus_value_estimee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<EstimationImmobiliere(id={self.id}, valeur={self.valeur_moyenne})>"


# ═══════════════════════════════════════════════════════════
# CHECKLISTS VACANCES
# ═══════════════════════════════════════════════════════════


class ChecklistVacances(TimestampMixin, Base):
    """Template de checklist pour vacances/weekend."""

    __tablename__ = "checklists_vacances"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_voyage: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # weekend, vacances_ete, vacances_hiver, camping, etc.
    destination: Mapped[str | None] = mapped_column(String(200))
    duree_jours: Mapped[int | None] = mapped_column(Integer)

    # Dates
    date_depart: Mapped[date | None] = mapped_column(Date)
    date_retour: Mapped[date | None] = mapped_column(Date)

    # Statut
    terminee: Mapped[bool] = mapped_column(Boolean, default=False)
    archivee: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    items: Mapped[list["ItemChecklist"]] = relationship(
        back_populates="checklist", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChecklistVacances(id={self.id}, nom='{self.nom}')>"


class ItemChecklist(TimestampMixin, Base):
    """Item d'une checklist vacances."""

    __tablename__ = "items_checklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    checklist_id: Mapped[int] = mapped_column(
        ForeignKey("checklists_vacances.id"), nullable=False, index=True
    )

    # Détails
    libelle: Mapped[str] = mapped_column(String(300), nullable=False)
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # maison, bagages, administratif, jules, animaux, vehicule
    ordre: Mapped[int] = mapped_column(Integer, default=0)

    # Statut
    fait: Mapped[bool] = mapped_column(Boolean, default=False)
    responsable: Mapped[str | None] = mapped_column(String(50))  # anne, mathieu

    # Timing
    quand: Mapped[str | None] = mapped_column(String(20))  # j-7, j-3, j-1, jour_j, retour

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relation
    checklist: Mapped["ChecklistVacances"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"<ItemChecklist(id={self.id}, libelle='{self.libelle}')>"


# ═══════════════════════════════════════════════════════════
# TRAITEMENTS NUISIBLES
# ═══════════════════════════════════════════════════════════


class TraitementNuisible(TimestampMixin, Base):
    """Suivi des traitements contre nuisibles.

    Calendrier traitements préventifs et curatifs.
    """

    __tablename__ = "traitements_nuisibles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    type_nuisible: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    zone: Mapped[str | None] = mapped_column(String(100))  # Pièce ou zone extérieure
    est_preventif: Mapped[bool] = mapped_column(Boolean, default=False)

    # Traitement
    produit: Mapped[str | None] = mapped_column(String(200))
    methode: Mapped[str | None] = mapped_column(String(200))  # Piège, spray, appât, professionnel
    est_bio: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    date_traitement: Mapped[date] = mapped_column(Date, nullable=False)
    date_prochain_traitement: Mapped[date | None] = mapped_column(Date, index=True)
    frequence_jours: Mapped[int | None] = mapped_column(Integer)  # Renouvellement

    # Efficacité
    efficacite: Mapped[int | None] = mapped_column(Integer)  # 1-5
    probleme_resolu: Mapped[bool] = mapped_column(Boolean, default=False)

    # Intervenant
    fait_par: Mapped[str | None] = mapped_column(String(100))  # nous ou professionnel
    artisan_id: Mapped[int | None] = mapped_column(ForeignKey("artisans.id"))
    cout: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # Sécurité
    fiche_securite: Mapped[str | None] = mapped_column(Text)  # Précautions

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<TraitementNuisible(id={self.id}, type='{self.type_nuisible}')>"


# ═══════════════════════════════════════════════════════════
# DEVIS COMPARATIFS
# ═══════════════════════════════════════════════════════════


class DevisComparatif(TimestampMixin, Base):
    """Devis d'artisan pour un projet/travaux.

    Permet de comparer plusieurs devis côte à côte.
    """

    __tablename__ = "devis_comparatifs"

    id: Mapped[int] = mapped_column(primary_key=True)
    projet_id: Mapped[int | None] = mapped_column(ForeignKey("projets.id"), index=True)
    artisan_id: Mapped[int | None] = mapped_column(ForeignKey("artisans.id"), index=True)

    # Identification
    reference: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Dates
    date_demande: Mapped[date | None] = mapped_column(Date)
    date_reception: Mapped[date | None] = mapped_column(Date)
    date_validite: Mapped[date | None] = mapped_column(Date)

    # Montants
    montant_ht: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    montant_ttc: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tva_pct: Mapped[float | None] = mapped_column(Float)

    # Délais
    delai_travaux_jours: Mapped[int | None] = mapped_column(Integer)
    date_debut_prevue: Mapped[date | None] = mapped_column(Date)

    # Statut
    statut: Mapped[str] = mapped_column(String(20), default="demande", index=True)
    choisi: Mapped[bool] = mapped_column(Boolean, default=False)

    # Évaluation
    note_globale: Mapped[int | None] = mapped_column(Integer)  # 1-5
    commentaire: Mapped[str | None] = mapped_column(Text)

    # Documents
    document_path: Mapped[str | None] = mapped_column(String(500))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    lignes: Mapped[list["LigneDevis"]] = relationship(
        back_populates="devis", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DevisComparatif(id={self.id}, montant_ttc={self.montant_ttc})>"


class LigneDevis(CreeLeMixin, Base):
    """Ligne détaillée d'un devis."""

    __tablename__ = "lignes_devis"

    id: Mapped[int] = mapped_column(primary_key=True)
    devis_id: Mapped[int] = mapped_column(
        ForeignKey("devis_comparatifs.id"), nullable=False, index=True
    )

    # Détails
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantite: Mapped[float] = mapped_column(Float, default=1.0)
    unite: Mapped[str | None] = mapped_column(String(20))
    prix_unitaire_ht: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    montant_ht: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Type
    type_ligne: Mapped[str] = mapped_column(
        String(30), default="fourniture"
    )  # fourniture, main_oeuvre, divers

    # Relation
    devis: Mapped["DevisComparatif"] = relationship(back_populates="lignes")

    def __repr__(self) -> str:
        return f"<LigneDevis(id={self.id}, desc='{self.description[:30]}')>"


# ═══════════════════════════════════════════════════════════
# ENTRETIEN SAISONNIER
# ═══════════════════════════════════════════════════════════


class EntretienSaisonnier(TimestampMixin, Base):
    """Tâche d'entretien saisonnier prédéfinie.

    Catalogue de ~40 tâches récurrentes (chaudière, ramonage, gouttières...).
    """

    __tablename__ = "entretiens_saisonniers"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # chauffage, plomberie, toiture, jardin, piscine, securite
    saison: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    # Mois recommandé (1-12)
    mois_recommande: Mapped[int | None] = mapped_column(Integer)
    mois_rappel: Mapped[int | None] = mapped_column(Integer)  # Mois de l'alerte

    # Fréquence
    frequence: Mapped[str] = mapped_column(
        String(30), default="annuel"
    )  # annuel, semestriel, trimestriel

    # Statut pour cette année
    fait_cette_annee: Mapped[bool] = mapped_column(Boolean, default=False)
    date_derniere_realisation: Mapped[date | None] = mapped_column(Date)
    date_prochaine: Mapped[date | None] = mapped_column(Date, index=True)

    # Qui fait ?
    professionnel_requis: Mapped[bool] = mapped_column(Boolean, default=False)
    artisan_id: Mapped[int | None] = mapped_column(ForeignKey("artisans.id"))
    cout_estime: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    duree_minutes: Mapped[int | None] = mapped_column(Integer)

    # Obligatoire ?
    obligatoire: Mapped[bool] = mapped_column(Boolean, default=False)
    reglementation: Mapped[str | None] = mapped_column(Text)  # Texte de loi si applicable

    # Alerte
    alerte_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<EntretienSaisonnier(id={self.id}, nom='{self.nom}', saison='{self.saison}')>"


# ═══════════════════════════════════════════════════════════
# RELEVÉS COMPTEURS
# ═══════════════════════════════════════════════════════════


class ReleveCompteur(CreeLeMixin, Base):
    """Relevé de compteur eau/énergie.

    Pour suivi détaillé conso eau avec détection fuites.
    """

    __tablename__ = "releves_compteurs"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Type
    type_compteur: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # eau, electricite, gaz
    numero_compteur: Mapped[str | None] = mapped_column(String(50))

    # Relevé
    date_releve: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    valeur: Mapped[float] = mapped_column(Float, nullable=False)  # m3, kWh, etc.
    unite: Mapped[str] = mapped_column(String(10), default="m³")

    # Calculs (remplis automatiquement)
    consommation_periode: Mapped[float | None] = mapped_column(Float)
    nb_jours_periode: Mapped[int | None] = mapped_column(Integer)
    consommation_jour: Mapped[float | None] = mapped_column(Float)

    # Objectif
    objectif_jour: Mapped[float | None] = mapped_column(Float)  # Objectif conso/jour

    # Anomalie
    anomalie_detectee: Mapped[bool] = mapped_column(Boolean, default=False)
    commentaire_anomalie: Mapped[str | None] = mapped_column(Text)

    # Photo (OCR compteur)
    photo_path: Mapped[str | None] = mapped_column(String(500))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ReleveCompteur(id={self.id}, type='{self.type_compteur}', valeur={self.valeur})>"


# ═══════════════════════════════════════════════════════════
# SIMULATION RÉNOVATION
# ═══════════════════════════════════════════════════════════


class StatutSimulation(StrEnum):
    """Statut d'une simulation de rénovation."""

    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ARCHIVE = "archive"


class SimulationRenovation(TimestampMixin, Base):
    """Simulation de rénovation multi-scénarios.

    Chaque simulation représente un projet de rénovation générique
    (conversion pièce, isolation, aménagement terrain, déco, chauffage, etc.)
    et peut contenir plusieurs scénarios à comparer.
    """

    __tablename__ = "simulations_renovation"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_projet: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # conversion_piece, isolation, amenagement_terrain, deco, chauffage, ouverture_mur, etc.

    # Statut
    statut: Mapped[str] = mapped_column(String(30), default="brouillon", index=True)

    # Localisation
    pieces_concernees: Mapped[str | None] = mapped_column(Text)  # IDs pièces séparés par virgule
    zones_terrain: Mapped[str | None] = mapped_column(Text)  # IDs zones séparés par virgule

    # Lien projet existant (optionnel)
    projet_id: Mapped[int | None] = mapped_column(ForeignKey("projets.id"), index=True)

    # Lien plan (optionnel)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey("plans_maison.id"), index=True)

    # Métadonnées
    tags: Mapped[str | None] = mapped_column(String(500))  # Tags séparés par virgule
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    scenarios: Mapped[list["ScenarioSimulation"]] = relationship(
        back_populates="simulation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SimulationRenovation(id={self.id}, nom='{self.nom}', type='{self.type_projet}')>"


class ScenarioSimulation(TimestampMixin, Base):
    """Scénario d'une simulation de rénovation.

    Chaque simulation peut contenir N scénarios (variantes)
    avec leurs propres budget, durée, faisabilité.
    """

    __tablename__ = "scenarios_simulation"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations_renovation.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    est_favori: Mapped[bool] = mapped_column(Boolean, default=False)

    # Budget
    budget_estime_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    budget_estime_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    budget_materiaux: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    budget_main_oeuvre: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Durée
    duree_estimee_jours: Mapped[int | None] = mapped_column(Integer)

    # Faisabilité IA
    score_faisabilite: Mapped[int | None] = mapped_column(Integer)  # 0-100
    analyse_faisabilite: Mapped[str | None] = mapped_column(Text)  # JSON rapport IA
    contraintes_techniques: Mapped[str | None] = mapped_column(Text)  # JSON liste contraintes
    recommandations: Mapped[str | None] = mapped_column(Text)  # JSON recommandations

    # Impact
    impact_dpe: Mapped[str | None] = mapped_column(String(10))  # ex: "D→B"
    gain_energetique_pct: Mapped[float | None] = mapped_column(Float)
    plus_value_estimee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Postes détaillés (JSON)
    postes_travaux: Mapped[dict | None] = mapped_column(JSON)  # [{poste, budget_min, budget_max, diy}]

    # Artisans nécessaires
    artisans_necessaires: Mapped[str | None] = mapped_column(Text)  # JSON [{type, optionnel}]

    # Plan avant/après
    plan_avant_id: Mapped[int | None] = mapped_column(ForeignKey("plans_maison.id"))
    plan_apres_id: Mapped[int | None] = mapped_column(ForeignKey("plans_maison.id"))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Relations
    simulation: Mapped["SimulationRenovation"] = relationship(back_populates="scenarios")

    def __repr__(self) -> str:
        return f"<ScenarioSimulation(id={self.id}, nom='{self.nom}', score={self.score_faisabilite})>"


# ═══════════════════════════════════════════════════════════
# PLANS MAISON (2D/3D)
# ═══════════════════════════════════════════════════════════


class PlanMaison(TimestampMixin, Base):
    """Plan 2D/3D de la maison sauvegardé.

    Stocke les données du canvas (react-konva) en JSON
    pour permettre l'édition et le rendu.
    """

    __tablename__ = "plans_maison"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type_plan: Mapped[str] = mapped_column(
        String(50), nullable=False, default="interieur", index=True
    )  # interieur, terrain, etage_0, etage_1, etc.

    # Version
    version: Mapped[int] = mapped_column(Integer, default=1)
    est_actif: Mapped[bool] = mapped_column(Boolean, default=True)

    # Données canvas (JSON sérialisé complet)
    donnees_canvas: Mapped[dict | None] = mapped_column(JSON)  # Murs, portes, fenêtres, meubles, annotations

    # Métadonnées plan
    echelle_px_par_m: Mapped[float] = mapped_column(Float, default=50.0)  # Pixels par mètre
    largeur_canvas: Mapped[int] = mapped_column(Integer, default=1200)
    hauteur_canvas: Mapped[int] = mapped_column(Integer, default=800)
    etage: Mapped[int] = mapped_column(Integer, default=0)

    # Thumbnail
    thumbnail_path: Mapped[str | None] = mapped_column(String(500))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<PlanMaison(id={self.id}, nom='{self.nom}', type='{self.type_plan}', v{self.version})>"


# ═══════════════════════════════════════════════════════════
# ZONES TERRAIN
# ═══════════════════════════════════════════════════════════


class ZoneTerrain(TimestampMixin, Base):
    """Zone délimitée du terrain extérieur.

    Permet de modéliser le terrain 2600m² avec ses différentes zones
    (potager, pelouse, terrasse, abri, allée, etc.) et la topographie.
    """

    __tablename__ = "zones_terrain"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identification
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_zone: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # potager, pelouse, terrasse, abri, allee, parking, piscine, bois, friche, autre
    description: Mapped[str | None] = mapped_column(Text)

    # Dimensions
    surface_m2: Mapped[float | None] = mapped_column(Float)

    # Topographie
    altitude_min: Mapped[float | None] = mapped_column(Float)  # Mètres
    altitude_max: Mapped[float | None] = mapped_column(Float)
    pente_pct: Mapped[float | None] = mapped_column(Float)  # Pourcentage de pente
    exposition: Mapped[str | None] = mapped_column(String(20))  # nord, sud, est, ouest

    # Position sur le plan terrain (JSON polygone)
    geometrie: Mapped[dict | None] = mapped_column(JSON)  # [{x, y}, ...] points du polygone

    # Lien jardin (optionnel — zone potager = éléments jardin)
    lien_jardin: Mapped[bool] = mapped_column(Boolean, default=False)

    # État actuel
    etat: Mapped[str] = mapped_column(String(50), default="existant")  # existant, a_amenager, en_travaux
    date_amenagement: Mapped[date | None] = mapped_column(Date)
    cout_amenagement: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ZoneTerrain(id={self.id}, nom='{self.nom}', type='{self.type_zone}')>"
