"""
Schémas Pydantic pour la famille (anniversaires, événements familiaux).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES
# ═══════════════════════════════════════════════════════════


class AnniversaireBase(BaseModel):
    nom_personne: str = Field(..., min_length=1, max_length=200)
    date_naissance: str = Field(..., description="Date au format YYYY-MM-DD")
    relation: str = Field(
        ..., description="parent, enfant, grand_parent, oncle_tante, cousin, ami, collegue"
    )
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = None
    notes: str | None = None


class AnniversaireCreate(AnniversaireBase):
    pass


class AnniversairePatch(BaseModel):
    nom_personne: str | None = Field(None, min_length=1, max_length=200)
    date_naissance: str | None = None
    relation: str | None = None
    rappel_jours_avant: list[int] | None = None
    idees_cadeaux: str | None = None
    notes: str | None = None
    actif: bool | None = None


class AnniversaireResponse(BaseModel):
    id: int
    nom_personne: str
    date_naissance: str
    relation: str
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = None
    historique_cadeaux: list[dict] | None = None
    notes: str | None = None
    actif: bool = True
    age: int | None = None
    jours_restants: int | None = None
    cree_le: str | None = None


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS FAMILIAUX
# ═══════════════════════════════════════════════════════════


class EvenementFamilialBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    date_evenement: str = Field(..., description="Date au format YYYY-MM-DD")
    type_evenement: str = Field(
        ..., description="anniversaire, fete, vacances, rentree, tradition"
    )
    recurrence: str = Field(default="unique", description="annuelle, mensuelle, unique")
    rappel_jours_avant: int = 7
    notes: str | None = None
    participants: list[str] | None = None


class EvenementFamilialCreate(EvenementFamilialBase):
    pass


class EvenementFamilialPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    date_evenement: str | None = None
    type_evenement: str | None = None
    recurrence: str | None = None
    rappel_jours_avant: int | None = None
    notes: str | None = None
    participants: list[str] | None = None
    actif: bool | None = None


class EvenementFamilialResponse(BaseModel):
    id: int
    titre: str
    date_evenement: str
    type_evenement: str
    recurrence: str = "unique"
    rappel_jours_avant: int = 7
    notes: str | None = None
    participants: list[str] | None = None
    actif: bool = True
    cree_le: str | None = None


# ═══════════════════════════════════════════════════════════
# CONTEXTE FAMILIAL (Phase M)
# ═══════════════════════════════════════════════════════════


class MeteoActuelle(BaseModel):
    emoji: str | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    condition: str | None = None
    precipitation_mm: float | None = None
    vent_km_h: float | None = None
    previsions_7j: list[dict] = Field(default_factory=list)


class JourSpecialResponse(BaseModel):
    nom: str
    date: str
    type: str
    jours_restants: int


class JulesContexte(BaseModel):
    age_mois: int
    date_naissance: str
    prochains_jalons: list[str] = Field(default_factory=list)


class DocumentExpirant(BaseModel):
    titre: str
    jours_restants: int
    severite: str = "info"


class AnniversaireContexte(BaseModel):
    id: int
    nom_personne: str
    age: int | None = None
    relation: str
    jours_restants: int
    idees_cadeaux: str | None = None


class RoutineContexte(BaseModel):
    id: int
    nom: str
    categorie: str | None = None


class ActiviteContexte(BaseModel):
    id: int
    titre: str
    date: str | None = None
    type_activite: str | None = None
    lieu: str | None = None


class AchatUrgent(BaseModel):
    id: int
    nom: str
    categorie: str
    priorite: str
    prix_estime: float | None = None
    suggere_par: str | None = None


class ContexteFamilialResponse(BaseModel):
    meteo: MeteoActuelle | None = None
    jours_speciaux: list[JourSpecialResponse] = Field(default_factory=list)
    anniversaires_proches: list[AnniversaireContexte] = Field(default_factory=list)
    jules: JulesContexte | None = None
    documents_expirants: list[DocumentExpirant] = Field(default_factory=list)
    routines_du_moment: list[RoutineContexte] = Field(default_factory=list)
    activites_a_venir: list[ActiviteContexte] = Field(default_factory=list)
    achats_urgents: list[AchatUrgent] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# ACHATS FAMILLE (Phase M4)
# ═══════════════════════════════════════════════════════════


class AchatCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=300)
    categorie: str = Field(..., description="jules_vetements, jules_jouets, nous_jeux, maison, etc.")
    priorite: str = Field(default="moyenne", description="urgent, haute, moyenne, basse, optionnel")
    prix_estime: float | None = None
    taille: str | None = None
    magasin: str | None = None
    url: str | None = None
    description: str | None = None
    age_recommande_mois: int | None = None
    suggere_par: str | None = None


class AchatPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=300)
    categorie: str | None = None
    priorite: str | None = None
    prix_estime: float | None = None
    taille: str | None = None
    magasin: str | None = None
    url: str | None = None
    description: str | None = None
    age_recommande_mois: int | None = None


class AchatResponse(BaseModel):
    id: int
    nom: str
    categorie: str
    priorite: str
    prix_estime: float | None = None
    prix_reel: float | None = None
    taille: str | None = None
    magasin: str | None = None
    url: str | None = None
    description: str | None = None
    age_recommande_mois: int | None = None
    suggere_par: str | None = None
    achete: bool = False
    date_achat: str | None = None


class MarquerAchetePayload(BaseModel):
    prix_reel: float | None = None


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA (Phase M3 + P)
# ═══════════════════════════════════════════════════════════


class SuggestionsWeekendRequest(BaseModel):
    budget: int = Field(default=50, ge=0, le=500)
    region: str = Field(default="Île-de-France")
    nb_suggestions: int = Field(default=3, ge=1, le=10)


class SuggestionsActivitesSimpleRequest(BaseModel):
    budget_max: float = Field(default=50.0, ge=0, le=500)
    duree_max_heures: float = Field(default=3.0, ge=0.5, le=12)
    type_prefere: str = Field(default="les_deux", description="interieur, exterieur, les_deux")


class ResumeSemaineRequest(BaseModel):
    evenements: list[str] = Field(default_factory=list)
    jalons: list[str] | None = None
    humeur_famille: str = Field(default="bonne")


class RetrospectiveRequest(BaseModel):
    mois: str = Field(..., description="Nom du mois, ex: janvier 2025")
    resumes_semaines: list[str] = Field(default_factory=list)
    nb_evenements: int = 0
    nb_jalons: int = 0


class SuggestionsSoireeRequest(BaseModel):
    budget: int = Field(default=80, ge=0, le=500)
    duree_heures: float = Field(default=4.0, ge=1, le=12)
    type_soiree: str = Field(default="variee")
    region: str = Field(default="Île-de-France")


class SuggestionAchatResponse(BaseModel):
    titre: str
    description: str
    fourchette_prix: str | None = None
    ou_acheter: str | None = None
    pertinence: str | None = None


# ═══════════════════════════════════════════════════════════
# RAPPELS (Phase Q)
# ═══════════════════════════════════════════════════════════


class RappelFamilleResponse(BaseModel):
    type: str
    message: str
    priorite: str = "info"
    date_cible: str | None = None
    jours_restants: int | None = None
    click_url: str | None = None


# ═══════════════════════════════════════════════════════════
# CROISSANCE OMS (Phase R)
# ═══════════════════════════════════════════════════════════


class PercentilesOMS(BaseModel):
    P3: float | None = None
    P15: float | None = None
    P50: float | None = None
    P85: float | None = None
    P97: float | None = None


class CroissanceResponse(BaseModel):
    age_mois: int
    normes: dict[str, PercentilesOMS] = Field(
        default_factory=dict,
        description="Normes OMS par mesure (poids, taille, perimetre_cranien)",
    )
