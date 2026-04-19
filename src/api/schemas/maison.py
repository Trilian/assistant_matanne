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

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Pastilles lave-vaisselle",
                "categorie": "entretien",
                "quantite": 12,
                "unite": "unités",
                "seuil_alerte": 5,
                "emplacement": "cellier",
                "prix_unitaire": 0.18,
            }
        }
    }


class StockPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float | None = Field(None, ge=0)
    unite: str | None = Field(None, max_length=50)
    seuil_alerte: float | None = Field(None, ge=0)
    emplacement: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = Field(None, ge=0)


class StockResponse(IdentifiedResponse):
    nom: str = Field(max_length=200)
    categorie: str | None = Field(None, max_length=100)
    quantite: float = 0
    unite: str | None = Field(None, max_length=50)
    seuil_alerte: float = 0
    emplacement: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = None
    en_alerte: bool = False

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 14,
                "nom": "Pastilles lave-vaisselle",
                "categorie": "entretien",
                "quantite": 12,
                "unite": "unités",
                "seuil_alerte": 5,
                "emplacement": "cellier",
                "prix_unitaire": 0.18,
                "en_alerte": False,
            }
        }
    }


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
    notes: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type_abonnement": "electricite",
                "fournisseur": "EDF",
                "numero_contrat": "AB-2026-001",
                "prix_mensuel": 82.5,
                "date_debut": "2025-11-01",
                "date_fin_engagement": "2026-11-01",
                "meilleur_prix_trouve": 76.9,
                "fournisseur_alternatif": "TotalEnergies",
                "notes": "Comparer au renouvellement annuel.",
            }
        }
    }


class AbonnementPatch(BaseModel):
    type_abonnement: str | None = Field(None, max_length=50)
    fournisseur: str | None = Field(None, max_length=200)
    numero_contrat: str | None = Field(None, max_length=100)
    prix_mensuel: float | None = Field(None, ge=0)
    date_debut: _dt.date | None = None
    date_fin_engagement: _dt.date | None = None
    meilleur_prix_trouve: float | None = Field(None, ge=0)
    fournisseur_alternatif: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, max_length=1000)


class AbonnementResponse(IdentifiedResponse):
    type_abonnement: str = Field(max_length=50)
    fournisseur: str = Field(max_length=200)
    numero_contrat: str | None = Field(None, max_length=100)
    prix_mensuel: float | None = None
    date_debut: _dt.date | None = None
    date_fin_engagement: _dt.date | None = None
    meilleur_prix_trouve: float | None = None
    fournisseur_alternatif: str | None = Field(None, max_length=200)
    notes: str | None = Field(None, max_length=1000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "type_abonnement": "electricite",
                "fournisseur": "EDF",
                "numero_contrat": "AB-2026-001",
                "prix_mensuel": 82.5,
                "date_debut": "2025-11-01",
                "date_fin_engagement": "2026-11-01",
                "meilleur_prix_trouve": 76.9,
                "fournisseur_alternatif": "TotalEnergies",
                "notes": "Comparer au renouvellement annuel.",
            }
        }
    }


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


# ═══════════════════════════════════════════════════════════
# SIMULATIONS RÉNOVATION
# ═══════════════════════════════════════════════════════════


class SimulationCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    description: str | None = None
    type_projet: str = Field(..., max_length=100)
    pieces_concernees: str | None = Field(None, max_length=500)
    zones_terrain: str | None = Field(None, max_length=500)
    projet_id: int | None = None
    plan_id: int | None = None
    tags: str | None = Field(None, max_length=500)
    notes: str | None = None


class SimulationPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    description: str | None = None
    type_projet: str | None = Field(None, max_length=100)
    statut: str | None = Field(None, max_length=30)
    pieces_concernees: str | None = None
    zones_terrain: str | None = None
    projet_id: int | None = None
    plan_id: int | None = None
    tags: str | None = Field(None, max_length=500)
    notes: str | None = None


class SimulationResponse(IdentifiedResponse):
    nom: str
    description: str | None = None
    type_projet: str
    statut: str
    pieces_concernees: str | None = None
    zones_terrain: str | None = None
    projet_id: int | None = None
    plan_id: int | None = None
    tags: str | None = None
    notes: str | None = None
    scenarios_count: int = 0


# Scénarios


class ScenarioCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    description: str | None = None
    est_favori: bool = False
    budget_estime_min: float | None = Field(None, ge=0)
    budget_estime_max: float | None = Field(None, ge=0)
    budget_materiaux: float | None = Field(None, ge=0)
    budget_main_oeuvre: float | None = Field(None, ge=0)
    duree_estimee_jours: int | None = Field(None, ge=1)
    impact_dpe: str | None = Field(None, max_length=10)
    postes_travaux: list[dict] | None = None
    plan_avant_id: int | None = None
    plan_apres_id: int | None = None
    notes: str | None = None


class ScenarioPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    description: str | None = None
    est_favori: bool | None = None
    budget_estime_min: float | None = Field(None, ge=0)
    budget_estime_max: float | None = Field(None, ge=0)
    budget_materiaux: float | None = Field(None, ge=0)
    budget_main_oeuvre: float | None = Field(None, ge=0)
    duree_estimee_jours: int | None = Field(None, ge=1)
    impact_dpe: str | None = Field(None, max_length=10)
    postes_travaux: list[dict] | None = None
    plan_avant_id: int | None = None
    plan_apres_id: int | None = None
    notes: str | None = None


class ScenarioResponse(IdentifiedResponse):
    simulation_id: int
    nom: str
    description: str | None = None
    est_favori: bool = False
    budget_estime_min: float | None = None
    budget_estime_max: float | None = None
    budget_materiaux: float | None = None
    budget_main_oeuvre: float | None = None
    duree_estimee_jours: int | None = None
    score_faisabilite: int | None = None
    analyse_faisabilite: str | None = None
    contraintes_techniques: str | None = None
    recommandations: str | None = None
    impact_dpe: str | None = None
    gain_energetique_pct: float | None = None
    plus_value_estimee: float | None = None
    postes_travaux: list[dict] | None = None
    artisans_necessaires: str | None = None
    plan_avant_id: int | None = None
    plan_apres_id: int | None = None
    notes: str | None = None


class ComparaisonScenariosResponse(BaseModel):
    simulation: SimulationResponse
    scenarios: list[ScenarioResponse]
    meilleur_budget: int | None = None  # ID du scénario le moins cher
    meilleur_faisabilite: int | None = None  # ID du scénario le plus faisable
    meilleur_rapport: int | None = None  # ID du meilleur rapport qualité/prix


# ═══════════════════════════════════════════════════════════
# PLANS MAISON (2D/3D)
# ═══════════════════════════════════════════════════════════


class PlanMaisonCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    description: str | None = None
    type_plan: str = Field("interieur", max_length=50)
    donnees_canvas: dict | None = None
    echelle_px_par_m: float = Field(50.0, gt=0)
    largeur_canvas: int = Field(1200, ge=100, le=10000)
    hauteur_canvas: int = Field(800, ge=100, le=10000)
    etage: int = 0
    notes: str | None = None


class PlanMaisonPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    description: str | None = None
    type_plan: str | None = Field(None, max_length=50)
    donnees_canvas: dict | None = None
    echelle_px_par_m: float | None = Field(None, gt=0)
    largeur_canvas: int | None = Field(None, ge=100, le=10000)
    hauteur_canvas: int | None = Field(None, ge=100, le=10000)
    etage: int | None = None
    est_actif: bool | None = None
    notes: str | None = None


class PlanMaisonResponse(IdentifiedResponse):
    nom: str
    description: str | None = None
    type_plan: str
    version: int = 1
    est_actif: bool = True
    donnees_canvas: dict | None = None
    echelle_px_par_m: float = 50.0
    largeur_canvas: int = 1200
    hauteur_canvas: int = 800
    etage: int = 0
    thumbnail_path: str | None = None
    notes: str | None = None


# ═══════════════════════════════════════════════════════════
# ZONES TERRAIN
# ═══════════════════════════════════════════════════════════


class ZoneTerrainCreate(BaseModel, NomValidatorMixin):
    nom: str = Field(..., max_length=200)
    type_zone: str = Field(..., max_length=50)
    description: str | None = None
    surface_m2: float | None = Field(None, gt=0)
    altitude_min: float | None = None
    altitude_max: float | None = None
    pente_pct: float | None = Field(None, ge=0, le=100)
    exposition: str | None = Field(None, max_length=20)
    geometrie: dict | None = None
    lien_jardin: bool = False
    etat: str = Field("existant", max_length=50)
    date_amenagement: _dt.date | None = None
    cout_amenagement: float | None = Field(None, ge=0)
    notes: str | None = None


class ZoneTerrainPatch(BaseModel):
    nom: str | None = Field(None, max_length=200)
    type_zone: str | None = Field(None, max_length=50)
    description: str | None = None
    surface_m2: float | None = Field(None, gt=0)
    altitude_min: float | None = None
    altitude_max: float | None = None
    pente_pct: float | None = Field(None, ge=0, le=100)
    exposition: str | None = Field(None, max_length=20)
    geometrie: dict | None = None
    lien_jardin: bool | None = None
    etat: str | None = Field(None, max_length=50)
    date_amenagement: _dt.date | None = None
    cout_amenagement: float | None = Field(None, ge=0)
    notes: str | None = None


class ZoneTerrainResponse(IdentifiedResponse):
    nom: str
    type_zone: str
    description: str | None = None
    surface_m2: float | None = None
    altitude_min: float | None = None
    altitude_max: float | None = None
    pente_pct: float | None = None
    exposition: str | None = None
    geometrie: dict | None = None
    lien_jardin: bool = False
    etat: str = "existant"
    date_amenagement: _dt.date | None = None
    cout_amenagement: float | None = None
    notes: str | None = None
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
    type: str = Field(max_length=50)
    niveau: str = Field(max_length=30)
    titre: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    action_suggeree: str | None = Field(None, max_length=300)
    date_limite: _dt.date | None = None
    metadata: dict = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "entretien",
                "niveau": "attention",
                "titre": "Filtre chaudière à vérifier",
                "message": "Le filtre chaudière dépasse la fréquence recommandée.",
                "action_suggeree": "Planifier une vérification ce week-end",
                "date_limite": "2026-04-12",
                "metadata": {"piece": "buanderie"},
            }
        }
    }


class TacheJourResponse(BaseModel):
    nom: str = Field(max_length=200)
    categorie: str = Field("entretien", max_length=50)
    duree_estimee_min: int | None = None
    priorite: str = Field("moyenne", max_length=30)
    source: str = Field("", max_length=100)
    fait: bool = False
    id_source: int | None = None


class MeteoResumeResponse(BaseModel):
    temperature_min: float | None = None
    temperature_max: float | None = None
    description: str = Field("", max_length=300)
    precipitation_mm: float = 0
    impact_jardin: str | None = Field(None, max_length=300)
    impact_menage: str | None = Field(None, max_length=300)


class BriefingMaisonResponse(BaseModel):
    date: _dt.date
    resume: str = Field("", max_length=2000)
    taches_jour: list[str] = Field(default_factory=list)
    taches_jour_detail: list[TacheJourResponse] = Field(default_factory=list)
    alertes: list[AlerteMaisonResponse] = Field(default_factory=list)
    meteo_impact: str | None = Field(None, max_length=500)
    meteo: MeteoResumeResponse | None = None
    projets_actifs: list[str] = Field(default_factory=list)
    priorites: list[str] = Field(default_factory=list)
    eco_score_jour: int | None = None
    entretiens_saisonniers: list[dict] = Field(default_factory=list)
    jardin: list[dict] = Field(default_factory=list)
    cellier_alertes: list[dict] = Field(default_factory=list)
    energie_anomalies: list[dict] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2026-04-03",
                "resume": "Journée calme avec un point entretien et une alerte stock.",
                "taches_jour": ["Sortir les poubelles", "Vérifier le filtre chaudière"],
                "taches_jour_detail": [
                    {
                        "nom": "Vérifier le filtre chaudière",
                        "categorie": "entretien",
                        "duree_estimee_min": 20,
                        "priorite": "haute",
                        "source": "routine",
                        "fait": False,
                        "id_source": 8,
                    }
                ],
                "alertes": [
                    {
                        "type": "entretien",
                        "niveau": "attention",
                        "titre": "Filtre chaudière à vérifier",
                        "message": "Le filtre chaudière dépasse la fréquence recommandée.",
                        "action_suggeree": "Planifier une vérification ce week-end",
                        "date_limite": "2026-04-12",
                        "metadata": {"piece": "buanderie"},
                    }
                ],
                "meteo_impact": "Temps sec, bon créneau pour arroser le jardin en soirée.",
                "meteo": {
                    "temperature_min": 8,
                    "temperature_max": 17,
                    "description": "éclaircies",
                    "precipitation_mm": 0,
                    "impact_jardin": "Arrosage utile",
                    "impact_menage": None,
                },
                "projets_actifs": ["Réaménagement chambre Jules"],
                "priorites": ["Racheter du liquide vaisselle"],
                "eco_score_jour": 78,
                "entretiens_saisonniers": [],
                "jardin": [],
                "cellier_alertes": [],
                "energie_anomalies": [],
            }
        }
    }


class PreferencesMenageRequest(BaseModel):
    jours_off: list[str] = Field(default_factory=list)
    creneau_horaire: str | None = Field(None, max_length=50)
    intensite: str = Field("normal", pattern="^(leger|normal|intensif)$", max_length=20)
    responsables: list[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "jours_off": ["samedi"],
                "creneau_horaire": "18:00-19:00",
                "intensite": "normal",
                "responsables": ["Anne", "Mathieu"],
            }
        }
    }


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
