"""
Schémas Pydantic pour la famille (anniversaires, événements familiaux).
"""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES
# ═══════════════════════════════════════════════════════════


class AnniversaireBase(BaseModel):
    nom_personne: str = Field(..., min_length=1, max_length=200)
    date_naissance: str = Field(..., description="Date au format YYYY-MM-DD")
    relation: str = Field(
        ...,
        description="parent, enfant, grand_parent, oncle_tante, cousin, ami, collegue",
        max_length=50,
    )
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = Field(None, max_length=1000)
    notes: str | None = Field(None, max_length=2000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom_personne": "Jules",
                "date_naissance": "2024-10-12",
                "relation": "enfant",
                "rappel_jours_avant": [30, 7, 1],
                "idees_cadeaux": "Livres, puzzles, dînette",
                "notes": "Privilégier les cadeaux adaptés 18-24 mois.",
            }
        }
    }


class AnniversaireCreate(AnniversaireBase):
    """Création d'un anniversaire — hérite tous les champs d'AnniversaireBase."""


class AnniversairePatch(BaseModel):
    nom_personne: str | None = Field(None, min_length=1, max_length=200)
    date_naissance: str | None = None
    relation: str | None = Field(None, max_length=50)
    rappel_jours_avant: list[int] | None = None
    idees_cadeaux: str | None = Field(None, max_length=1000)
    notes: str | None = Field(None, max_length=2000)
    actif: bool | None = None


class AnniversaireResponse(BaseModel):
    id: int
    nom_personne: str
    date_naissance: str
    relation: str = Field(max_length=50)
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = Field(None, max_length=1000)
    historique_cadeaux: list[dict[str, Any]] | None = None
    notes: str | None = Field(None, max_length=2000)
    actif: bool = True
    age: int | None = None
    jours_restants: int | None = None
    cree_le: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 5,
                "nom_personne": "Jules",
                "date_naissance": "2024-10-12",
                "relation": "enfant",
                "rappel_jours_avant": [30, 7, 1],
                "idees_cadeaux": "Livres, puzzles, dînette",
                "historique_cadeaux": [{"annee": 2025, "cadeau": "Porteur"}],
                "notes": "Anniversaire à la maison avec les grands-parents.",
                "actif": True,
                "age": 2,
                "jours_restants": 192,
                "cree_le": "2026-03-01T10:00:00",
            }
        }
    }


class AnniversairesListeResponse(BaseModel):
    """Réponse pour la liste des anniversaires."""

    items: list[AnniversaireResponse]


class ChecklistAnniversaireSyncRequest(BaseModel):
    force_recalcul_budget: bool = False


class ChecklistAnniversaireItemCreate(BaseModel):
    categorie: str = Field(..., min_length=1, max_length=50)
    libelle: str = Field(..., min_length=1, max_length=300)
    budget_estime: float | None = Field(default=None, ge=0)
    priorite: str = Field(default="moyenne", max_length=30)
    responsable: str | None = Field(default=None, max_length=50)
    quand: str | None = Field(default=None, max_length=20)
    ordre: int = Field(default=1000, ge=0)
    notes: str | None = Field(None, max_length=1000)


class ChecklistAnniversaireItemPatch(BaseModel):
    fait: bool | None = None
    budget_reel: float | None = Field(default=None, ge=0)
    budget_estime: float | None = Field(default=None, ge=0)
    priorite: str | None = Field(None, max_length=30)
    responsable: str | None = Field(default=None, max_length=50)
    quand: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(None, max_length=1000)
    libelle: str | None = Field(default=None, min_length=1, max_length=300)
    categorie: str | None = Field(default=None, min_length=1, max_length=50)


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS FAMILIAUX
# ═══════════════════════════════════════════════════════════


class EvenementFamilialBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    date_evenement: str = Field(..., description="Date au format YYYY-MM-DD")
    type_evenement: str = Field(
        ..., description="anniversaire, fete, vacances, rentree, tradition", max_length=50
    )
    recurrence: str = Field(
        default="unique", description="annuelle, mensuelle, unique", max_length=30
    )
    rappel_jours_avant: int = 7
    notes: str | None = Field(None, max_length=1000)
    participants: list[str] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "titre": "Vacances Bretagne",
                "date_evenement": "2026-07-20",
                "type_evenement": "vacances",
                "recurrence": "unique",
                "rappel_jours_avant": 14,
                "notes": "Réserver le logement avant fin avril.",
                "participants": ["Anne", "Mathieu", "Jules"],
            }
        }
    }


class EvenementFamilialCreate(EvenementFamilialBase):
    """Création d'un événement familial — hérite tous les champs d'EvenementFamilialBase."""


class EvenementFamilialPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    date_evenement: str | None = None
    type_evenement: str | None = Field(None, max_length=50)
    recurrence: str | None = Field(None, max_length=30)
    rappel_jours_avant: int | None = None
    notes: str | None = Field(None, max_length=1000)
    participants: list[str] | None = None
    actif: bool | None = None


class EvenementFamilialResponse(BaseModel):
    id: int
    titre: str
    date_evenement: str
    type_evenement: str = Field(max_length=50)
    recurrence: str = Field("unique", max_length=30)
    rappel_jours_avant: int = 7
    notes: str | None = Field(None, max_length=1000)
    participants: list[str] | None = None
    actif: bool = True
    cree_le: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 8,
                "titre": "Vacances Bretagne",
                "date_evenement": "2026-07-20",
                "type_evenement": "vacances",
                "recurrence": "unique",
                "rappel_jours_avant": 14,
                "notes": "Réserver le logement avant fin avril.",
                "participants": ["Anne", "Mathieu", "Jules"],
                "actif": True,
                "cree_le": "2026-04-01T09:30:00",
            }
        }
    }


class EvenementsListeResponse(BaseModel):
    """Réponse pour la liste des événements familiaux."""

    items: list[EvenementFamilialResponse]


# ═══════════════════════════════════════════════════════════
# CONTEXTE FAMILIAL
# ═══════════════════════════════════════════════════════════


class MeteoActuelle(BaseModel):
    emoji: str | None = None
    temperature_min: float | None = None
    temperature_max: float | None = None
    condition: str | None = None
    precipitation_mm: float | None = None
    vent_km_h: float | None = None
    previsions_7j: list[dict[str, Any]] = Field(
        default_factory=lambda: cast(list[dict[str, Any]], [])
    )


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
    jours_speciaux: list[JourSpecialResponse] = Field(
        default_factory=lambda: cast(list[JourSpecialResponse], [])
    )
    anniversaires_proches: list[AnniversaireContexte] = Field(
        default_factory=lambda: cast(list[AnniversaireContexte], [])
    )
    jules: JulesContexte | None = None
    documents_expirants: list[DocumentExpirant] = Field(
        default_factory=lambda: cast(list[DocumentExpirant], [])
    )
    routines_du_moment: list[RoutineContexte] = Field(
        default_factory=lambda: cast(list[RoutineContexte], [])
    )
    activites_a_venir: list[ActiviteContexte] = Field(
        default_factory=lambda: cast(list[ActiviteContexte], [])
    )
    achats_urgents: list[AchatUrgent] = Field(default_factory=lambda: cast(list[AchatUrgent], []))


# ═══════════════════════════════════════════════════════════
# ACHATS FAMILLE
# ═══════════════════════════════════════════════════════════


class AchatCreate(BaseModel):
    nom: str = Field(..., min_length=1, max_length=300)
    categorie: str = Field(
        ..., description="jules_vetements, jules_jouets, nous_jeux, maison, etc.", max_length=100
    )
    priorite: str = Field(
        default="moyenne", description="urgent, haute, moyenne, basse, optionnel", max_length=30
    )
    prix_estime: float | None = None
    taille: str | None = Field(None, max_length=40)
    magasin: str | None = Field(None, max_length=200)
    url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=1000)
    age_recommande_mois: int | None = None
    suggere_par: str | None = Field(None, max_length=100)
    pour_qui: str = Field(
        default="famille", description="famille, jules, anne, mathieu", max_length=30
    )
    a_revendre: bool = False
    prix_revente_estime: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Bottes de pluie Jules",
                "categorie": "jules_vetements",
                "priorite": "haute",
                "prix_estime": 28.0,
                "taille": "24",
                "magasin": "Decathlon",
                "url": "https://example.com/bottes-jules",
                "description": "Bottes légères pour sorties pluvieuses.",
                "age_recommande_mois": 24,
                "suggere_par": "saison",
                "pour_qui": "jules",
                "a_revendre": True,
                "prix_revente_estime": 10.0,
            }
        }
    }


class AchatPatch(BaseModel):
    nom: str | None = Field(None, min_length=1, max_length=300)
    categorie: str | None = Field(None, max_length=100)
    priorite: str | None = Field(None, max_length=30)
    prix_estime: float | None = None
    taille: str | None = Field(None, max_length=40)
    magasin: str | None = Field(None, max_length=200)
    url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=1000)
    age_recommande_mois: int | None = None
    pour_qui: str | None = Field(None, max_length=30)
    a_revendre: bool | None = None
    prix_revente_estime: float | None = None


class AchatResponse(BaseModel):
    id: int
    nom: str
    categorie: str = Field(max_length=100)
    priorite: str = Field(max_length=30)
    prix_estime: float | None = None
    prix_reel: float | None = None
    taille: str | None = Field(None, max_length=40)
    magasin: str | None = Field(None, max_length=200)
    url: str | None = Field(None, max_length=500)
    description: str | None = Field(None, max_length=1000)
    age_recommande_mois: int | None = None
    suggere_par: str | None = Field(None, max_length=100)
    achete: bool = False
    date_achat: str | None = None
    pour_qui: str = Field("famille", max_length=30)
    a_revendre: bool = False
    prix_revente_estime: float | None = None
    vendu_le: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 14,
                "nom": "Bottes de pluie Jules",
                "categorie": "jules_vetements",
                "priorite": "haute",
                "prix_estime": 28.0,
                "prix_reel": None,
                "taille": "24",
                "magasin": "Decathlon",
                "url": "https://example.com/bottes-jules",
                "description": "Bottes légères pour sorties pluvieuses.",
                "age_recommande_mois": 24,
                "suggere_par": "saison",
                "achete": False,
                "date_achat": None,
                "pour_qui": "jules",
                "a_revendre": True,
                "prix_revente_estime": 10.0,
                "vendu_le": None,
            }
        }
    }


class MarquerAchetePayload(BaseModel):
    prix_reel: float | None = None


class AchatsListeResponse(BaseModel):
    """Réponse pour la liste des achats famille."""

    items: list[AchatResponse]
    total: int


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA
# ═══════════════════════════════════════════════════════════


class SuggestionsWeekendRequest(BaseModel):
    budget: int = Field(default=50, ge=0, le=500)
    region: str = Field(default="Île-de-France", max_length=100)
    nb_suggestions: int = Field(default=3, ge=1, le=10)

    model_config = {
        "json_schema_extra": {
            "example": {"budget": 60, "region": "Île-de-France", "nb_suggestions": 4}
        }
    }


class SuggestionsActivitesSimpleRequest(BaseModel):
    budget_max: float = Field(default=50.0, ge=0, le=500)
    duree_max_heures: float = Field(default=3.0, ge=0.5, le=12)
    type_prefere: str = Field(
        default="les_deux", description="interieur, exterieur, les_deux", max_length=30
    )

    model_config = {
        "json_schema_extra": {
            "example": {"budget_max": 40, "duree_max_heures": 2.5, "type_prefere": "exterieur"}
        }
    }


class ResumeSemaineRequest(BaseModel):
    evenements: list[str] = Field(default_factory=list)
    jalons: list[str] | None = None
    humeur_famille: str = Field(default="bonne", max_length=30)

    model_config = {
        "json_schema_extra": {
            "example": {
                "evenements": ["Sortie au parc", "Repas en famille dimanche"],
                "jalons": ["Jules a commencé les puzzles 12 pièces"],
                "humeur_famille": "bonne",
            }
        }
    }


class RetrospectiveRequest(BaseModel):
    mois: str = Field(..., description="Nom du mois, ex: janvier 2025", max_length=50)
    resumes_semaines: list[str] = Field(default_factory=list)
    nb_evenements: int = 0
    nb_jalons: int = 0


class SuggestionsSoireeRequest(BaseModel):
    budget: int = Field(default=80, ge=0, le=500)
    duree_heures: float = Field(default=4.0, ge=1, le=12)
    type_soiree: str = Field(default="variee", max_length=30)
    region: str = Field(default="Île-de-France", max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "budget": 90,
                "duree_heures": 4.0,
                "type_soiree": "cocooning",
                "region": "Île-de-France",
            }
        }
    }


class SuggestionAchatResponse(BaseModel):
    titre: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    fourchette_prix: str | None = Field(None, max_length=100)
    ou_acheter: str | None = Field(None, max_length=200)
    pertinence: str | None = Field(None, max_length=300)


# ═══════════════════════════════════════════════════════════
# RAPPELS
# ═══════════════════════════════════════════════════════════


class RappelFamilleResponse(BaseModel):
    type: str = Field(max_length=50)
    message: str = Field(max_length=500)
    priorite: str = Field("info", max_length=30)
    date_cible: str | None = None
    jours_restants: int | None = None
    click_url: str | None = Field(None, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "anniversaire",
                "message": "Anniversaire de Jules dans 7 jours.",
                "priorite": "haute",
                "date_cible": "2026-10-12",
                "jours_restants": 7,
                "click_url": "/famille/anniversaires",
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# CONFIG GARDE
# ═══════════════════════════════════════════════════════════


class SemainesFermetureCreche(BaseModel):
    debut: str = Field(..., description="Date de début YYYY-MM-DD")
    fin: str = Field(..., description="Date de fin YYYY-MM-DD")
    label: str = Field(default="", description="Libellé (ex: Vacances Toussaint)", max_length=200)


class ConfigGardeRequest(BaseModel):
    semaines_fermeture: list[SemainesFermetureCreche] = Field(
        default_factory=lambda: cast(list[SemainesFermetureCreche], [])
    )
    nom_creche: str = Field(default="", max_length=200)
    zone_academique: str = Field(default="B", description="Zone A, B ou C", max_length=1)

    model_config = {
        "json_schema_extra": {
            "example": {
                "semaines_fermeture": [
                    {"debut": "2026-08-03", "fin": "2026-08-21", "label": "Fermeture été"}
                ],
                "nom_creche": "Les Petits Nuages",
                "zone_academique": "B",
            }
        }
    }


class ConfigGardeResponse(BaseModel):
    semaines_fermeture: list[dict[str, Any]] = Field(
        default_factory=lambda: cast(list[dict[str, Any]], [])
    )
    nom_creche: str = ""
    zone_academique: str = "B"
    annee_courante: int | None = None


class PreferencesFamilleRequest(BaseModel):
    """Préférences personnelles des adultes (tailles, style, intérêts)."""

    taille_vetements_anne: dict[str, Any] = Field(
        default_factory=dict, description="Ex: {tee_shirt: 'M', pantalon: '38', pointure: '39'}"
    )
    taille_vetements_mathieu: dict[str, Any] = Field(default_factory=dict)
    style_achats_anne: dict[str, Any] = Field(
        default_factory=dict,
        description="Ex: {prefere_made_france: true, prefere_qualite: true, budget_piece_max: 80}",
    )
    style_achats_mathieu: dict[str, Any] = Field(default_factory=dict)
    interets_gaming: list[str] = Field(
        default_factory=list, description="Ex: ['Nintendo Switch', 'jeux de société']"
    )
    interets_culture: list[str] = Field(
        default_factory=list, description="Ex: ['cinéma', 'expositions', 'concerts']"
    )
    equipement_activites: dict[str, Any] = Field(
        default_factory=dict, description="Équipements sportifs disponibles"
    )


class PreferencesFamilleResponse(PreferencesFamilleRequest):
    """Réponse des préférences famille — hérite tous les champs de la requête."""


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS ACHATS ENRICHIES
# ═══════════════════════════════════════════════════════════


class SuggestionsAchatsEnrichiesRequest(BaseModel):
    pour_qui: str | None = Field(None, description="famille, jules, anne, mathieu", max_length=30)
    triggers: list[str] = Field(
        ...,
        min_length=1,
        description="liste de contextes: vetements_qualite, sejour, culture, gaming, etc.",
    )
    age_jules_mois: int | None = None
    destination: str | None = Field(None, max_length=200)
    ville: str | None = Field(None, max_length=100)
    budget: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "pour_qui": "jules",
                "triggers": ["vetements_qualite", "culture"],
                "age_jules_mois": 18,
                "destination": "Bretagne",
                "ville": "Rennes",
                "budget": 120.0,
            }
        }
    }


class AnnonceIBCRequest(BaseModel):
    nom: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    etat_usage: str = Field(
        default="bon", description="neuf, excellent, bon, correct, usage", max_length=30
    )
    prix_cible: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "nom": "Chaise haute bébé",
                "description": "Très bon état, housse lavée, utilisée 6 mois.",
                "etat_usage": "bon",
                "prix_cible": 35.0,
            }
        }
    }


class AnnonceIBCResponse(BaseModel):
    annonce: str = Field(..., description="Texte de l'annonce LBC en markdown")


class PrefillReventeResponse(BaseModel):
    """Données pré-remplies pour l'annonce de revente d'un achat."""

    achat_id: int
    plateforme: str = Field(..., description="plateforme de revente recommandée", max_length=30)
    plateforme_libelle: str = Field(
        ..., description="Libellé lisible pour la plateforme recommandée", max_length=50
    )
    marque: str | None = Field(None, max_length=80)
    taille: str | None = Field(None, max_length=40)
    prix_suggere: float | None = None
    pour_qui: str = Field("famille", max_length=30)
    raisons: list[str] = Field(
        default_factory=list, description="Explications du choix de plateforme et des préfills"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "achat_id": 14,
                "plateforme": "lbc",
                "plateforme_libelle": "LeBonCoin",
                "marque": "Petit Bateau",
                "taille": "18 mois",
                "prix_suggere": 18.0,
                "pour_qui": "jules",
                "raisons": ["revente familiale locale privilégiée", "marque recherchée"],
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# JOURS SANS CRECHE
# ═══════════════════════════════════════════════════════════


class JourSansCrecheResponse(BaseModel):
    date: str
    label: str | None = Field(None, max_length=200)
    suggestions_activites: str | None = Field(None, max_length=2000)


# ═══════════════════════════════════════════════════════════
# SEJOUR
# ═══════════════════════════════════════════════════════════


class SuggestionsSejourRequest(BaseModel):
    destination: str = Field(..., min_length=1, max_length=200)
    nb_jours: int = Field(default=7, ge=1, le=30)
    age_jules_mois: int | None = Field(None, ge=0, le=72)
    nb_suggestions: int = Field(default=4, ge=1, le=10)

    model_config = {
        "json_schema_extra": {
            "example": {
                "destination": "Bretagne",
                "nb_jours": 5,
                "age_jules_mois": 18,
                "nb_suggestions": 4,
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# BUDGET RÉSUMÉ
# ═══════════════════════════════════════════════════════════


class ResumeBudgetMoisResponse(BaseModel):
    mois_courant: str = Field(max_length=20)
    total_courant: float
    total_precedent: float | None = None
    variation_pct: float | None = None
    achats_par_categorie: dict[str, float] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "example": {
                "mois_courant": "2026-04",
                "total_courant": 184.5,
                "total_precedent": 132.0,
                "variation_pct": 39.77,
                "achats_par_categorie": {"jules_vetements": 64.0, "maison": 120.5},
            }
        }
    }


# ═══════════════════════════════════════════════════════════
# ROUTINES
# ═══════════════════════════════════════════════════════════


class EtapeRoutineResponse(BaseModel):
    id: int
    titre: str
    duree_minutes: int | None = None
    ordre: int = 0
    est_terminee: bool = False


class RoutineResponse(BaseModel):
    id: int
    nom: str
    type: str = ""
    est_active: bool = True
    etapes: list[EtapeRoutineResponse] = Field(default_factory=list)


class RoutineCompletionResponse(BaseModel):
    id: int
    nom: str
    derniere_completion: str | None = None


# ═══════════════════════════════════════════════════════════
# SHOPPING FAMILLE
# ═══════════════════════════════════════════════════════════


class ShoppingItemResponse(BaseModel):
    id: int
    titre: str
    categorie: str = ""
    quantite: float = 1.0
    prix_estime: float | None = None
    liste: str = ""
    actif: bool = True
    date_ajout: str | None = None


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ HEBDO
# ═══════════════════════════════════════════════════════════


class ResumeHebdoResponse(BaseModel):
    synthese: str = ""
    semaine: str = ""
    recommandations: list[str] = Field(default_factory=list)
    metriques: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# JOURS SANS CRÈCHE
# ═══════════════════════════════════════════════════════════


class JourSansCrecheItem(BaseModel):
    date: str
    label: str = ""


class PlanningJoursSansCrecheResponse(BaseModel):
    mois: str
    jours: list[JourSansCrecheItem] = Field(default_factory=list)
    total: int = 0
