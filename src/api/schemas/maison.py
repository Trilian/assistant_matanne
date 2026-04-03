"""
Sch\u00e9mas Pydantic pour les routes Maison.

Couvre : projets, routines, entretien, jardin, stocks, meubles,
cellier, artisans, diagnostics, estimations,
\u00e9co-tips, d\u00e9penses, nuisibles, devis, entretien saisonnier, relev\u00e9s,
visualisation plan, hub stats.
"""

import datetime as _dt

from pydantic import BaseModel, Field, field_validator

from .base import IdentifiedResponse, NomValidatorMixin


# Projets

class ProjetCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    description: str | None = None
    statut: str = Field("planifi\u00e9", max_length=50)
    priorite: str | None = Field(None, max_length=50)
    date_debut: _dt.date | None = None
    date_fin_prevue: _dt.date | None = None

class ProjetPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    description: str | None = None
    statut: str | None = Field(None, max_length=50)
    priorite: str | None = Field(None, max_length=50)
    date_debut: _dt.date | None = None
    date_fin_prevue: _dt.date | None = None
    date_fin_reelle: _dt.date | None = None

class ProjetResponse(IdentifiedResponse):
    nom: str
    description: str | None = None
    statut: str
    priorite: str | None = None
    date_debut: _dt.date | None = None
    date_fin_prevue: _dt.date | None = None
    date_fin_reelle: _dt.date | None = None
    taches_count: int = 0

# Entretien

class TacheEntretienCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    description: str | None = None
    categorie: str | None = Field(None, max_length=100)
    piece: str | None = Field(None, max_length=100)
    frequence_jours: int | None = Field(None, ge=1)
    duree_minutes: int | None = Field(None, ge=1)
    responsable: str | None = Field(None, max_length=100)
    priorite: str | None = Field(None, max_length=50)

class TacheEntretienPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    description: str | None = None
    categorie: str | None = Field(None, max_length=100)
    piece: str | None = Field(None, max_length=100)
    frequence_jours: int | None = Field(None, ge=1)
    duree_minutes: int | None = Field(None, ge=1)
    responsable: str | None = Field(None, max_length=100)
    priorite: str | None = Field(None, max_length=50)
    fait: bool | None = None

class TacheEntretienResponse(IdentifiedResponse):
    nom: str
    description: str | None = None
    categorie: str | None = None
    piece: str | None = None
    frequence_jours: int | None = None
    derniere_fois: _dt.date | None = None
    prochaine_fois: _dt.date | None = None
    duree_minutes: int | None = None
    responsable: str | None = None
    priorite: str | None = None
    fait: bool = False

# Jardin

class ElementJardinCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    type: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=200)
    statut: str | None = Field(None, max_length=50)
    date_plantation: _dt.date | None = None
    date_recolte_prevue: _dt.date | None = None
    notes: str | None = None

class ElementJardinPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    type: str | None = Field(None, max_length=100)
    location: str | None = Field(None, max_length=200)
    statut: str | None = Field(None, max_length=50)
    date_plantation: _dt.date | None = None
    date_recolte_prevue: _dt.date | None = None
    notes: str | None = None

class ElementJardinResponse(IdentifiedResponse):
    nom: str
    type: str | None = None
    location: str | None = None
    statut: str | None = None
    date_plantation: _dt.date | None = None
    date_recolte_prevue: _dt.date | None = None
    notes: str | None = None

# Stocks

class StockCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float = Field(0, ge=0)
    unite: str | None = Field(None, max_length=50)
    seuil_alerte: float = Field(0, ge=0)
    emplacement: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = Field(None, ge=0)

class StockPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float | None = Field(None, ge=0)
    unite: str | None = Field(None, max_length=50)
    seuil_alerte: float | None = Field(None, ge=0)
    emplacement: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = Field(None, ge=0)

class StockResponse(IdentifiedResponse):
    nom: str
    categorie: str | None = None
    quantite: float = 0
    unite: str | None = None
    seuil_alerte: float = 0
    emplacement: str | None = None
    prix_unitaire: float | None = None
    en_alerte: bool = False

# Meubles

class MeubleCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    piece: str | None = Field(None, max_length=100)
    categorie: str | None = Field(None, max_length=100)
    prix_estime: float | None = Field(None, ge=0)
    url_reference: str | None = Field(None, max_length=500)
    priorite: str | None = Field(None, max_length=50)
    statut: str | None = Field(None, max_length=50)
    notes: str | None = None

class MeublePatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    piece: str | None = Field(None, max_length=100)
    categorie: str | None = Field(None, max_length=100)
    prix_estime: float | None = Field(None, ge=0)
    url_reference: str | None = Field(None, max_length=500)
    priorite: str | None = Field(None, max_length=50)
    statut: str | None = Field(None, max_length=50)
    notes: str | None = None

class MeubleResponse(IdentifiedResponse):
    nom: str
    piece: str | None = None
    categorie: str | None = None
    prix_estime: float | None = None
    url_reference: str | None = None
    priorite: str | None = None
    statut: str | None = None
    notes: str | None = None

class BudgetMeublesResponse(BaseModel):
    total_estime: float = 0
    prix_max: float = 0
    par_piece: dict[str, float] = {}
    nb_meubles: int = 0

# Cellier

class ArticleCellierCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float = Field(1, ge=0)
    unite: str | None = Field(None, max_length=50)
    emplacement: str | None = Field(None, max_length=200)
    date_peremption: _dt.date | None = None
    seuil_alerte: int | None = Field(None, ge=0)
    prix_unitaire: float | None = Field(None, ge=0)
    code_barre: str | None = Field(None, max_length=50)
    notes: str | None = None

class ArticleCellierPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float | None = Field(None, ge=0)
    unite: str | None = Field(None, max_length=50)
    emplacement: str | None = Field(None, max_length=200)
    date_peremption: _dt.date | None = None
    seuil_alerte: int | None = Field(None, ge=0)
    prix_unitaire: float | None = Field(None, ge=0)
    code_barre: str | None = Field(None, max_length=50)
    notes: str | None = None

class ArticleCellierResponse(IdentifiedResponse):
    nom: str
    categorie: str | None = None
    quantite: float = 0
    unite: str | None = None
    emplacement: str | None = None
    date_peremption: _dt.date | None = None
    seuil_alerte: int | None = None
    prix_unitaire: float | None = None
    code_barre: str | None = None
    notes: str | None = None

class AlertePeremptionResponse(BaseModel):
    id: int
    nom: str
    date_peremption: _dt.date
    jours_restants: int
    quantite: float

class StatsCellierResponse(BaseModel):
    total_articles: int = 0
    par_categorie: dict[str, int] = {}
    valeur_totale: float = 0
    articles_perimes: int = 0
    articles_bientot_perimes: int = 0

# Abonnements

class AbonnementCreate(BaseModel):
    type_abonnement: str = Field(..., max_length=50)
    fournisseur: str = Field(..., max_length=200)
    numero_contrat: str | None = Field(None, max_length=100)
    prix_mensuel: float | None = Field(None, ge=0)
    date_debut: _dt.date | None = None
    date_fin_engagement: _dt.date | None = None
    meilleur_prix_trouve: float | None = Field(None, ge=0)
    fournisseur_alternatif: str | None = Field(None, max_length=200)
    notes: str | None = None

class AbonnementPatch(BaseModel):
    type_abonnement: str | None = Field(None, max_length=50)
    fournisseur: str | None = Field(None, max_length=200)
    numero_contrat: str | None = Field(None, max_length=100)
    prix_mensuel: float | None = Field(None, ge=0)
    date_debut: _dt.date | None = None
    date_fin_engagement: _dt.date | None = None
    meilleur_prix_trouve: float | None = Field(None, ge=0)
    fournisseur_alternatif: str | None = Field(None, max_length=200)
    notes: str | None = None

class AbonnementResponse(IdentifiedResponse):
    type_abonnement: str
    fournisseur: str
    numero_contrat: str | None = None
    prix_mensuel: float | None = None
    date_debut: _dt.date | None = None
    date_fin_engagement: _dt.date | None = None
    meilleur_prix_trouve: float | None = None
    fournisseur_alternatif: str | None = None
    notes: str | None = None

class ResumeAbonnements(BaseModel):
    total_mensuel: float = 0
    total_annuel: float = 0
    par_type: dict[str, float] = {}

# Artisans

class ArtisanCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    metier: str = Field(..., max_length=100)
    telephone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = None
    note_satisfaction: int | None = Field(None, ge=1, le=5)
    commentaire: str | None = None

class ArtisanPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    metier: str | None = Field(None, max_length=100)
    telephone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=200)
    adresse: str | None = None
    note_satisfaction: int | None = Field(None, ge=1, le=5)
    commentaire: str | None = None

class ArtisanResponse(IdentifiedResponse):
    nom: str
    metier: str
    telephone: str | None = None
    email: str | None = None
    adresse: str | None = None
    note_satisfaction: int | None = None
    commentaire: str | None = None
    dernier_passage: _dt.date | None = None

class InterventionCreate(BaseModel):
    artisan_id: int
    date: _dt.date
    description: str = Field(..., max_length=500)
    cout: float | None = Field(None, ge=0)
    etat: str | None = Field(None, max_length=50)
    notes: str | None = None

class InterventionPatch(BaseModel):
    date: _dt.date | None = None
    description: str | None = Field(None, max_length=500)
    cout: float | None = Field(None, ge=0)
    etat: str | None = Field(None, max_length=50)
    notes: str | None = None

class InterventionResponse(IdentifiedResponse):
    artisan_id: int
    date: _dt.date
    description: str
    cout: float | None = None
    etat: str | None = None
    notes: str | None = None

class StatsArtisansResponse(BaseModel):
    total_artisans: int = 0
    par_metier: dict[str, int] = {}
    depenses_totales: float = 0
    total_interventions: int = 0

# Diagnostics & Estimations

class DiagnosticCreate(BaseModel):
    type_diagnostic: str = Field(..., max_length=100)
    date_realisation: _dt.date
    date_expiration: _dt.date | None = None
    diagnostiqueur: str | None = Field(None, max_length=200)
    resultat: str | None = None
    document_url: str | None = Field(None, max_length=500)
    notes: str | None = None

class DiagnosticPatch(BaseModel):
    type_diagnostic: str | None = Field(None, max_length=100)
    date_realisation: _dt.date | None = None
    date_expiration: _dt.date | None = None
    diagnostiqueur: str | None = Field(None, max_length=200)
    resultat: str | None = None
    document_url: str | None = Field(None, max_length=500)
    notes: str | None = None

class DiagnosticResponse(IdentifiedResponse):
    type_diagnostic: str
    date_realisation: _dt.date
    date_expiration: _dt.date | None = None
    diagnostiqueur: str | None = None
    resultat: str | None = None
    document_url: str | None = None
    notes: str | None = None

class EstimationCreate(BaseModel):
    date: _dt.date
    valeur_estimee: float = Field(..., gt=0)
    source: str | None = Field(None, max_length=200)
    surface_m2: float | None = Field(None, gt=0)
    prix_m2: float | None = Field(None, gt=0)
    notes: str | None = None

class EstimationPatch(BaseModel):
    date: _dt.date | None = None
    valeur_estimee: float | None = Field(None, gt=0)
    source: str | None = Field(None, max_length=200)
    surface_m2: float | None = Field(None, gt=0)
    prix_m2: float | None = Field(None, gt=0)
    notes: str | None = None

class EstimationResponse(IdentifiedResponse):
    date: _dt.date
    valeur_estimee: float
    source: str | None = None
    surface_m2: float | None = None
    prix_m2: float | None = None
    notes: str | None = None

# Eco-Tips

class ActionEcoCreate(BaseModel):
    titre: str = Field(..., max_length=200)
    description: str | None = None
    categorie: str | None = Field(None, max_length=100)
    impact: str | None = Field(None, max_length=50)
    economie_estimee: float | None = Field(None, ge=0)
    date_debut: _dt.date | None = None

    @field_validator("titre")
    @classmethod
    def validate_titre(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le titre ne peut pas \u00eatre vide")
        return v.strip()

class ActionEcoPatch(BaseModel):
    titre: str | None = Field(None, max_length=200)
    description: str | None = None
    categorie: str | None = Field(None, max_length=100)
    impact: str | None = Field(None, max_length=50)
    economie_estimee: float | None = Field(None, ge=0)
    actif: bool | None = None
    date_debut: _dt.date | None = None

class ActionEcoResponse(IdentifiedResponse):
    titre: str
    description: str | None = None
    categorie: str | None = None
    impact: str | None = None
    economie_estimee: float | None = None
    actif: bool = True
    date_debut: _dt.date | None = None

# Depenses Maison

class DepenseMaisonCreate(BaseModel):
    libelle: str = Field(..., max_length=200)
    montant: float = Field(..., gt=0)
    categorie: str = Field(..., max_length=100)
    date: _dt.date
    fournisseur: str | None = Field(None, max_length=200)
    recurrence: str | None = Field(None, max_length=50)
    notes: str | None = None

    @field_validator("libelle")
    @classmethod
    def validate_libelle(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Le libell\u00e9 ne peut pas \u00eatre vide")
        return v.strip()

class DepenseMaisonPatch(BaseModel):
    libelle: str | None = Field(None, max_length=200)
    montant: float | None = Field(None, gt=0)
    categorie: str | None = Field(None, max_length=100)
    date: _dt.date | None = None
    fournisseur: str | None = Field(None, max_length=200)
    recurrence: str | None = Field(None, max_length=50)
    notes: str | None = None

class DepenseMaisonResponse(IdentifiedResponse):
    libelle: str
    montant: float
    categorie: str
    date: _dt.date
    fournisseur: str | None = None
    recurrence: str | None = None
    notes: str | None = None

class StatsDepensesResponse(BaseModel):
    total_mois: float = 0
    total_annee: float = 0
    moyenne_mensuelle: float = 0
    delta_mois_precedent: float = 0
    par_categorie: dict[str, float] = {}

# Nuisibles

class TraitementNuisibleCreate(BaseModel):
    type_nuisible: str = Field(..., max_length=100)
    zone: str | None = Field(None, max_length=200)
    produit_utilise: str | None = Field(None, max_length=200)
    date_traitement: _dt.date
    date_prochain: _dt.date | None = None
    efficacite: str | None = Field(None, max_length=50)
    notes: str | None = None

class TraitementNuisiblePatch(BaseModel):
    type_nuisible: str | None = Field(None, max_length=100)
    zone: str | None = Field(None, max_length=200)
    produit_utilise: str | None = Field(None, max_length=200)
    date_traitement: _dt.date | None = None
    date_prochain: _dt.date | None = None
    efficacite: str | None = Field(None, max_length=50)
    notes: str | None = None

class TraitementNuisibleResponse(IdentifiedResponse):
    type_nuisible: str
    zone: str | None = None
    produit_utilise: str | None = None
    date_traitement: _dt.date
    date_prochain: _dt.date | None = None
    efficacite: str | None = None
    notes: str | None = None

# Devis

class LigneDevisCreate(BaseModel):
    description: str = Field(..., max_length=500)
    quantite: float = Field(..., gt=0)
    prix_unitaire: float = Field(..., ge=0)

class LigneDevisResponse(BaseModel):
    id: int
    devis_id: int
    description: str
    quantite: float
    prix_unitaire: float
    total: float

class DevisCreate(BaseModel):
    projet_id: int | None = None
    artisan_nom: str = Field(..., max_length=200)
    montant_ht: float = Field(..., ge=0)
    montant_ttc: float = Field(..., ge=0)
    date_devis: _dt.date
    date_validite: _dt.date | None = None
    statut: str = Field("en_attente", max_length=50)
    fichier_url: str | None = Field(None, max_length=500)
    notes: str | None = None
    lignes: list[LigneDevisCreate] | None = None

class DevisPatch(BaseModel):
    artisan_nom: str | None = Field(None, max_length=200)
    montant_ht: float | None = Field(None, ge=0)
    montant_ttc: float | None = Field(None, ge=0)
    date_devis: _dt.date | None = None
    date_validite: _dt.date | None = None
    statut: str | None = Field(None, max_length=50)
    fichier_url: str | None = Field(None, max_length=500)
    notes: str | None = None

class DevisResponse(IdentifiedResponse):
    projet_id: int | None = None
    artisan_nom: str
    montant_ht: float
    montant_ttc: float
    date_devis: _dt.date
    date_validite: _dt.date | None = None
    statut: str
    fichier_url: str | None = None
    notes: str | None = None
    lignes: list[LigneDevisResponse] | None = None

# Entretien saisonnier

class EntretienSaisonnierCreate(BaseModel):
    tache: str = Field(..., max_length=200)
    saison: str = Field(..., max_length=50)
    mois_recommande: int | None = Field(None, ge=1, le=12)
    notes: str | None = None

    @field_validator("tache")
    @classmethod
    def validate_tache(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("La t\u00e2che ne peut pas \u00eatre vide")
        return v.strip()

class EntretienSaisonnierPatch(BaseModel):
    tache: str | None = Field(None, max_length=200)
    saison: str | None = Field(None, max_length=50)
    mois_recommande: int | None = Field(None, ge=1, le=12)
    fait: bool | None = None
    date_realisation: _dt.date | None = None
    notes: str | None = None

class EntretienSaisonnierResponse(IdentifiedResponse):
    tache: str
    saison: str
    mois_recommande: int | None = None
    fait: bool = False
    date_realisation: _dt.date | None = None
    notes: str | None = None

# Releves compteurs

class ReleveCompteurCreate(BaseModel):
    type_compteur: str = Field(..., max_length=100)
    valeur: float
    date_releve: _dt.date
    notes: str | None = None

class ReleveCompteurPatch(BaseModel):
    type_compteur: str | None = Field(None, max_length=100)
    valeur: float | None = None
    date_releve: _dt.date | None = None
    notes: str | None = None

class ReleveCompteurResponse(IdentifiedResponse):
    type_compteur: str
    valeur: float
    date_releve: _dt.date
    notes: str | None = None

# Visualisation plan

class PieceCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=100)
    etage: int = 0
    surface_m2: float | None = Field(None, gt=0)
    couleur: str | None = Field(None, max_length=7)
    position_x: float | None = None
    position_y: float | None = None
    largeur: float | None = Field(None, gt=0)
    hauteur: float | None = Field(None, gt=0)

class PiecePatch(BaseModel):
    nom: str | None = Field(None, max_length=100)
    etage: int | None = None
    surface_m2: float | None = Field(None, gt=0)
    couleur: str | None = Field(None, max_length=7)
    position_x: float | None = None
    position_y: float | None = None
    largeur: float | None = Field(None, gt=0)
    hauteur: float | None = Field(None, gt=0)

class ObjetCreate(BaseModel, NomValidatorMixin):
    piece_id: int
    nom: str = Field(..., max_length=200)
    type: str | None = Field(None, max_length=100)
    position_x: float | None = None
    position_y: float | None = None
    date_achat: _dt.date | None = None
    duree_garantie_mois: int | None = Field(None, ge=0, le=120)
    marque: str | None = Field(None, max_length=100)
    modele: str | None = Field(None, max_length=100)

class ObjetPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    type: str | None = Field(None, max_length=100)
    position_x: float | None = None
    position_y: float | None = None
    date_achat: _dt.date | None = None
    duree_garantie_mois: int | None = Field(None, ge=0, le=120)
    marque: str | None = Field(None, max_length=100)
    modele: str | None = Field(None, max_length=100)

class PieceResponse(IdentifiedResponse):
    nom: str
    etage: int = 0
    surface_m2: float | None = None
    couleur: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    largeur: float | None = None
    hauteur: float | None = None

class ObjetResponse(IdentifiedResponse):
    piece_id: int
    nom: str
    type: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    date_achat: _dt.date | None = None
    duree_garantie_mois: int | None = None
    marque: str | None = None
    modele: str | None = None
    sous_garantie: bool | None = None

# Hub Stats

class StatsHubMaisonResponse(BaseModel):
    projets_en_cours: int = 0
    taches_en_retard: int = 0
    depenses_mois: float = 0
    stocks_en_alerte: int = 0
    articles_perimes: int = 0
    diagnostics_expirant: int = 0

# Briefing Maison (contexte quotidien)

class AlerteMaisonResponse(BaseModel):
    type: str
    niveau: str
    titre: str
    message: str
    action_suggeree: str | None = None
    date_limite: _dt.date | None = None
    metadata: dict = Field(default_factory=dict)

class TacheJourResponse(BaseModel):
    nom: str
    categorie: str = "entretien"
    duree_estimee_min: int | None = None
    priorite: str = "moyenne"
    source: str = ""
    fait: bool = False
    id_source: int | None = None

class MeteoResumeResponse(BaseModel):
    temperature_min: float | None = None
    temperature_max: float | None = None
    description: str = ""
    precipitation_mm: float = 0
    impact_jardin: str | None = None
    impact_menage: str | None = None

class BriefingMaisonResponse(BaseModel):
    date: _dt.date
    resume: str = ""
    taches_jour: list[str] = Field(default_factory=list)
    taches_jour_detail: list[TacheJourResponse] = Field(default_factory=list)
    alertes: list[AlerteMaisonResponse] = Field(default_factory=list)
    meteo_impact: str | None = None
    meteo: MeteoResumeResponse | None = None
    projets_actifs: list[str] = Field(default_factory=list)
    priorites: list[str] = Field(default_factory=list)
    eco_score_jour: int | None = None
    entretiens_saisonniers: list[dict] = Field(default_factory=list)
    jardin: list[dict] = Field(default_factory=list)
    cellier_alertes: list[dict] = Field(default_factory=list)
    energie_anomalies: list[dict] = Field(default_factory=list)

class PreferencesMenageRequest(BaseModel):
    jours_off: list[str] = Field(default_factory=list)
    creneau_horaire: str | None = None
    intensite: str = Field("normal", pattern="^(leger|normal|intensif)$")
    responsables: list[str] = Field(default_factory=list)

class PlanningSemaineResponse(BaseModel):
    date_debut: _dt.date
    jours: dict[str, list[TacheJourResponse]] = Field(default_factory=dict)
    duree_totale_min: int = 0

class FicheTacheResponse(BaseModel):
    nom: str
    categorie: str = ""
    duree_estimee_min: int | None = None
    difficulte: str | None = None
    etapes: list[str] = Field(default_factory=list)
    produits: list[dict] = Field(default_factory=list)
    outils: list[str] = Field(default_factory=list)
    astuce_connectee: str | None = None
    video_recherche: str | None = None