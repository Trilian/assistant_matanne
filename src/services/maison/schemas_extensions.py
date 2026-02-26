"""
Schemas Pydantic pour les nouvelles fonctionnalités Maison.

Contient les schemas pour:
- Contrats
- Artisans & interventions
- Garanties & SAV
- Cellier
- Diagnostics (DPE)
- Estimations immobilières
- Checklists vacances
- Traitements nuisibles
- Devis comparatifs
- Entretiens saisonniers
- Relevés compteurs
"""

from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════
# CONTRATS
# ═══════════════════════════════════════════════════════════


class ContratCreate(BaseModel):
    """Création d'un contrat maison."""

    nom: str
    type_contrat: str
    fournisseur: str
    numero_contrat: str | None = None
    numero_client: str | None = None
    date_debut: date_type
    date_fin: date_type | None = None
    date_renouvellement: date_type | None = None
    duree_engagement_mois: int | None = None
    tacite_reconduction: bool = True
    preavis_resiliation_jours: int | None = None
    date_limite_resiliation: date_type | None = None
    montant_mensuel: Decimal | None = None
    montant_annuel: Decimal | None = None
    telephone: str | None = None
    email: str | None = None
    espace_client_url: str | None = None
    alerte_jours_avant: int = 30
    notes: str | None = None


class ContratResume(BaseModel):
    """Résumé d'un contrat pour l'affichage."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    type_contrat: str
    fournisseur: str
    montant_mensuel: Decimal | None = None
    date_renouvellement: date_type | None = None
    statut: str = "actif"
    jours_avant_renouvellement: int | None = None


class AlerteContrat(BaseModel):
    """Alerte d'un contrat à renouveler/résilier."""

    contrat_id: int
    nom: str
    type_contrat: str
    date_echeance: date_type
    jours_restants: int
    action: str  # renouveler, résilier, vérifier


# ═══════════════════════════════════════════════════════════
# ARTISANS
# ═══════════════════════════════════════════════════════════


class ArtisanCreate(BaseModel):
    """Création d'un artisan."""

    nom: str
    entreprise: str | None = None
    metier: str
    specialite: str | None = None
    telephone: str | None = None
    telephone2: str | None = None
    email: str | None = None
    adresse: str | None = None
    zone_intervention: str | None = None
    note: int | None = None
    recommande: bool = True
    site_web: str | None = None
    siret: str | None = None
    assurance_decennale: bool = False
    qualifications: str | None = None
    notes: str | None = None


class InterventionCreate(BaseModel):
    """Création d'une intervention artisan."""

    artisan_id: int
    date_intervention: date_type
    description: str
    piece: str | None = None
    montant_devis: Decimal | None = None
    montant_facture: Decimal | None = None
    paye: bool = False
    satisfaction: int | None = None
    commentaire: str | None = None


# ═══════════════════════════════════════════════════════════
# GARANTIES & SAV
# ═══════════════════════════════════════════════════════════


class GarantieCreate(BaseModel):
    """Création d'une garantie."""

    nom_appareil: str
    marque: str | None = None
    modele: str | None = None
    numero_serie: str | None = None
    piece: str | None = None
    date_achat: date_type
    lieu_achat: str | None = None
    prix_achat: Decimal | None = None
    duree_garantie_mois: int = 24
    date_fin_garantie: date_type
    garantie_etendue: bool = False
    date_fin_garantie_etendue: date_type | None = None
    cout_remplacement: Decimal | None = None
    notes: str | None = None


class IncidentCreate(BaseModel):
    """Création d'un incident SAV."""

    garantie_id: int
    date_incident: date_type
    description: str
    sous_garantie: bool = True
    reparateur: str | None = None
    artisan_id: int | None = None
    cout_reparation: Decimal | None = None
    notes: str | None = None


class AlerteGarantie(BaseModel):
    """Alerte de fin de garantie."""

    garantie_id: int
    nom_appareil: str
    date_fin_garantie: date_type
    jours_restants: int
    garantie_etendue: bool


# ═══════════════════════════════════════════════════════════
# CELLIER
# ═══════════════════════════════════════════════════════════


class ArticleCellierCreate(BaseModel):
    """Création d'un article cellier."""

    nom: str
    categorie: str
    sous_categorie: str | None = None
    marque: str | None = None
    code_barres: str | None = None
    quantite: int = 1
    unite: str = "unité"
    seuil_alerte: int = 1
    date_achat: date_type | None = None
    dlc: date_type | None = None
    dluo: date_type | None = None
    emplacement: str | None = None
    prix_unitaire: Decimal | None = None
    notes: str | None = None


class AlertePeremption(BaseModel):
    """Alerte péremption d'article du cellier."""

    article_id: int
    nom: str
    dlc: date_type
    jours_restants: int
    quantite: int


# ═══════════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════════


class DiagnosticCreate(BaseModel):
    """Création d'un diagnostic immobilier."""

    type_diagnostic: str
    resultat: str | None = None
    resultat_detail: str | None = None
    diagnostiqueur: str | None = None
    numero_certification: str | None = None
    date_realisation: date_type
    date_validite: date_type | None = None
    duree_validite_ans: int | None = None
    score_energie: str | None = None
    score_ges: str | None = None
    consommation_kwh_m2: float | None = None
    emission_co2_m2: float | None = None
    surface_m2: float | None = None
    recommandations: str | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# ESTIMATIONS IMMOBILIÈRES
# ═══════════════════════════════════════════════════════════


class EstimationCreate(BaseModel):
    """Création d'une estimation immobilière."""

    source: str
    date_estimation: date_type
    valeur_moyenne: Decimal
    valeur_basse: Decimal | None = None
    valeur_haute: Decimal | None = None
    prix_m2: Decimal | None = None
    surface_m2: float | None = None
    nb_pieces: int | None = None
    code_postal: str | None = None
    commune: str | None = None
    notes: str | None = None


class TransactionDVF(BaseModel):
    """Transaction DVF pour comparaison."""

    date_mutation: date_type
    valeur_fonciere: Decimal
    surface_m2: float | None = None
    prix_m2: Decimal | None = None
    type_bien: str | None = None
    nb_pieces: int | None = None
    code_postal: str
    commune: str
    adresse: str | None = None


# ═══════════════════════════════════════════════════════════
# CHECKLISTS VACANCES
# ═══════════════════════════════════════════════════════════


class ChecklistCreate(BaseModel):
    """Création d'une checklist vacances."""

    nom: str
    type_voyage: str
    destination: str | None = None
    duree_jours: int | None = None
    date_depart: date_type | None = None
    date_retour: date_type | None = None
    notes: str | None = None


class ItemChecklistCreate(BaseModel):
    """Création d'un item de checklist."""

    checklist_id: int
    libelle: str
    categorie: str
    ordre: int = 0
    responsable: str | None = None
    quand: str | None = None
    notes: str | None = None


class TemplateChecklist(BaseModel):
    """Template de checklist prédéfini."""

    nom: str
    type_voyage: str
    items: list[dict] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# TRAITEMENTS NUISIBLES
# ═══════════════════════════════════════════════════════════


class TraitementCreate(BaseModel):
    """Création d'un traitement nuisible."""

    type_nuisible: str
    zone: str | None = None
    est_preventif: bool = False
    produit: str | None = None
    methode: str | None = None
    est_bio: bool = False
    date_traitement: date_type
    date_prochain_traitement: date_type | None = None
    frequence_jours: int | None = None
    fait_par: str | None = None
    artisan_id: int | None = None
    cout: Decimal | None = None
    fiche_securite: str | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# DEVIS COMPARATIFS
# ═══════════════════════════════════════════════════════════


class DevisCreate(BaseModel):
    """Création d'un devis comparatif."""

    projet_id: int | None = None
    artisan_id: int | None = None
    reference: str | None = None
    description: str
    date_demande: date_type | None = None
    date_reception: date_type | None = None
    date_validite: date_type | None = None
    montant_ht: Decimal | None = None
    montant_ttc: Decimal
    tva_pct: float | None = None
    delai_travaux_jours: int | None = None
    notes: str | None = None


class LigneDevisCreate(BaseModel):
    """Création d'une ligne de devis."""

    devis_id: int
    description: str
    quantite: float = 1.0
    unite: str | None = None
    prix_unitaire_ht: Decimal
    montant_ht: Decimal
    type_ligne: str = "fourniture"


# ═══════════════════════════════════════════════════════════
# RELEVÉS COMPTEURS
# ═══════════════════════════════════════════════════════════


class ReleveCompteurCreate(BaseModel):
    """Création d'un relevé de compteur."""

    type_compteur: str
    numero_compteur: str | None = None
    date_releve: date_type
    valeur: float
    unite: str = "m³"
    objectif_jour: float | None = None
    notes: str | None = None
