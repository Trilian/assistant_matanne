"""
Schémas Pydantic — IA Bridges & fonctionnalités avancées.

Couvre prédiction courses, prévision budget, résumé hebdo,
diagnostic maison, planificateur adaptatif, bridges inter-modules,
suggestions IA diverses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# ═══════════════════════════════════════════════════════════
# PRÉDICTION COURSES (B4.1 / B5.4)
# ═══════════════════════════════════════════════════════════


class PredictionArticle(BaseModel):
    """Article prédit par l'IA."""

    nom: str
    categorie: str = "Autre"
    rayon: str = "Autre"
    frequence_jours: int | None = None

    @field_validator("rayon", "categorie", mode="before")
    @classmethod
    def normaliser_str_nulle(cls, v: object) -> str:
        """Convertit None (retourné par l'IA) en valeur par défaut."""
        return v if isinstance(v, str) and v.strip() else "Autre"
    dernier_achat: str | None = None
    prochaine_date_estimee: str | None = None
    jours_retard: int = 0
    confiance: float = 0.5
    nb_achats: int = 0


class PredictionCoursesResponse(BaseModel):
    """Réponse de prédiction de courses."""

    predictions: list[PredictionArticle] = []
    nb_total: int = 0


class HabitudesAchatResponse(BaseModel):
    """Réponse analyse des habitudes d'achat."""

    nb_articles_suivis: int = 0
    nb_avec_frequence: int = 0
    frequence_moyenne_jours: float | None = None
    top_categories: list[dict] = []


class EnregistrerAchatRequest(BaseModel):
    """Requête d'enregistrement d'achat."""

    article_nom: str = Field(..., min_length=1, max_length=200)
    categorie: str | None = Field(None, max_length=100)
    rayon: str | None = Field(None, max_length=100)


# ═══════════════════════════════════════════════════════════
# PRÉVISION BUDGET (B1.3 / B4.9)
# ═══════════════════════════════════════════════════════════


class PrevisionBudgetResponse(BaseModel):
    """Réponse de prévision budget."""

    mois: str
    jours_ecoules: int = 0
    jours_total: int = 0
    depenses_actuelles: float = 0
    moyenne_jour: float = 0
    prevision_fin_mois: float = 0
    depenses_mois_precedent: float = 0
    tendance_pct: float = 0
    par_categorie: list[dict] = []
    anomalies: list[dict] = []


class AnomalieBudget(BaseModel):
    """Anomalie budgétaire détectée."""

    categorie: str
    depense: float
    budget_ref: float
    pourcentage: float
    niveau: str = "attention"


class CategoriserDepenseRequest(BaseModel):
    """Requête de catégorisation de dépense."""

    description: str = Field(..., min_length=1, max_length=500)


class CategorieDepenseResponse(BaseModel):
    """Réponse de catégorisation de dépense."""

    categorie: str
    confiance: float
    source: str = "defaut"


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ HEBDOMADAIRE (B4.3)
# ═══════════════════════════════════════════════════════════


class ResumeHebdoResponse(BaseModel):
    """Réponse du résumé hebdomadaire."""

    resume_texte: str = ""
    points_forts: list[str] = []
    suggestions: list[str] = []
    donnees_brutes: dict | None = None


# ═══════════════════════════════════════════════════════════
# DIAGNOSTIC MAISON (B4.5)
# ═══════════════════════════════════════════════════════════


class DiagnosticPhotoRequest(BaseModel):
    """Requête de diagnostic par photo."""

    image_base64: str = Field(..., min_length=10)
    description: str = Field("", max_length=1000)


class DiagnosticTexteRequest(BaseModel):
    """Requête de diagnostic par texte."""

    description: str = Field(..., min_length=5, max_length=2000)


class DiagnosticResponse(BaseModel):
    """Réponse de diagnostic maison."""

    diagnostic: str = ""
    gravite: str = "inconnue"
    actions_recommandees: list[dict] = []
    cout_estime: dict | None = None
    professionnel_requis: bool = False
    type_professionnel: str | None = None


class DiagnosticMaisonRequest(DiagnosticTexteRequest):
    """Alias rétrocompatibilité pour les anciens imports."""


class DiagnosticMaisonResponse(DiagnosticResponse):
    """Alias rétrocompatibilité pour les anciens imports."""


# ═══════════════════════════════════════════════════════════
# PLANIFICATEUR ADAPTATIF (B4.2)
# ═══════════════════════════════════════════════════════════


class PlanningAdapteResponse(BaseModel):
    """Réponse du planificateur adaptatif."""

    planning: list[dict] = []
    ingredients_a_acheter: list[str] = []
    ingredients_stock_utilises: list[str] = []
    raisons: str = ""
    contexte_utilise: dict = {}


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS IA DIVERSES
# ═══════════════════════════════════════════════════════════


class BatchCookingPlanRequest(BaseModel):
    """Requête batch cooking intelligent."""

    recettes: list[str] = Field(..., min_length=1, max_length=10)
    nb_personnes: int = Field(4, ge=1, le=20)


class BatchCookingPlanResponse(BaseModel):
    """Réponse batch cooking intelligent."""

    temps_total_minutes: int = 0
    etapes: list[dict] = []
    appareils_utilises: list[str] = []
    conseils: list[str] = []
    ordre_optimal: list[str] = []


class ConseilJulesRequest(BaseModel):
    """Requête conseil développement Jules."""

    age_mois: int = Field(..., ge=0, le=240)
    jalons_atteints: list[str] = []


class ConseilJulesResponse(BaseModel):
    """Réponse conseil développement Jules."""

    activites_recommandees: list[dict] = []
    jalons_attendus: list[dict] = []
    points_attention: list[str] = []
    jeux_adaptes: list[str] = []


class ChecklistVoyageRequest(BaseModel):
    """Requête checklist voyage."""

    destination: str = Field(..., min_length=1, max_length=200)
    dates: str = Field(..., min_length=1, max_length=100)
    participants: list[str] = []


class ChecklistVoyageResponse(BaseModel):
    """Réponse checklist voyage."""

    categories: list[dict] = []
    rappels: list[dict] = []
    conseils_destination: list[str] = []


class ScoreEcologiqueRequest(BaseModel):
    """Requête score écologique."""

    ingredients: list[str] = Field(..., min_length=1)
    saison: str = ""


class ScoreEcologiqueResponse(BaseModel):
    """Réponse score écologique."""

    score_global: float | None = None
    score_max: float = 10
    details: dict = {}
    ingredients_problematiques: list[str] = []
    suggestions_amelioration: list[str] = []


class AnalyseNutritionnelleRequest(BaseModel):
    """Requête analyse nutritionnelle."""

    description_repas: str = Field(..., min_length=3, max_length=1000)


class AnalyseNutritionnelleResponse(BaseModel):
    """Réponse analyse nutritionnelle."""

    calories_estimees: int | None = None
    macronutriments: dict = {}
    score_nutritionnel: float | None = None
    points_forts: list[str] = []
    points_faibles: list[str] = []
    suggestion_amelioration: str = ""


class OptimisationEnergieRequest(BaseModel):
    """Requête optimisation énergie."""

    releves: list[dict] = Field(..., min_length=1)
    meteo: dict | None = None


class OptimisationEnergieResponse(BaseModel):
    """Réponse optimisation énergie."""

    prevision_prochaine_facture: dict | None = None
    tendance: str = ""
    variation_pct: float = 0
    conseils_economies: list[str] = []


# ═══════════════════════════════════════════════════════════
# BRIDGES INTER-MODULES (B5)
# ═══════════════════════════════════════════════════════════


class DocumentExpireAlerte(BaseModel):
    """Document expiré ou expirant bientôt."""

    id: int
    titre: str
    categorie: str
    membre_famille: str
    date_expiration: str
    jours_restants: int | None = None
    est_expire: bool = False
    niveau: str = "attention"


class DocumentsExpiresResponse(BaseModel):
    """Réponse documents expirés."""

    alertes: list[DocumentExpireAlerte]
    nb_expires: int = 0
    nb_bientot: int = 0


class PlanningUnifieItem(BaseModel):
    """Élément du planning unifié."""

    id: int
    nom: str
    prochaine_fois: str
    en_retard: bool = False
    jours_restants: int | None = None
    type: str = "entretien"


class PlanningUnifieResponse(BaseModel):
    """Planning unifié multi-modules."""

    taches: list[PlanningUnifieItem]
    nb_total: int = 0
    nb_en_retard: int = 0


class AlerteMeteoEntretien(BaseModel):
    """Alerte météo liée à l'entretien."""

    type: str
    message: str
    priorite: str = "moyenne"
    domaine: str = ""


class FeedbackSemaineRequest(BaseModel):
    """Requête feedback fin de semaine (B7.5)."""

    repas_consommes: list[dict] = []
    commentaires: str = ""
    note_globale: int = Field(5, ge=1, le=10)


# ═══════════════════════════════════════════════════════════
# P3 — BRIDGES INTER-MODULES ENRICHIS
# ═══════════════════════════════════════════════════════════


class BudgetUnifieResponse(BaseModel):
    """Budget unifié charges maison + dépenses famille."""

    mois: int
    annee: int
    total_famille: float = 0
    total_maison: float = 0
    total_unifie: float = 0
    details_famille: list[dict] = []
    details_maison: list[dict] = []
    evolution_pct: float | None = None


class AnnonceImmoResume(BaseModel):
    """Annonce immobilière résumée pour le widget."""

    id: int
    titre: str
    prix: float
    surface_m2: float | None = None
    ville: str
    score_pertinence: float | None = None
    url_source: str | None = None


class WidgetVeilleImmoResponse(BaseModel):
    """Réponse widget veille immobilière."""

    dernieres_annonces: list[AnnonceImmoResume] = []
    nb_annonces_total: int = 0
    prix_moyen: float | None = None
    tendance_prix_pct: float | None = None


class ActiviteJardinSaison(BaseModel):
    """Activité jardin saisonnière."""

    element: str
    type_activite: str
    priorite: str = "normale"
    conseil: str = ""


class WidgetSaisonJardinResponse(BaseModel):
    """Réponse widget saison jardin."""

    saison: str
    activites: list[ActiviteJardinSaison] = []
    nb_plantes_actives: int = 0
    prochaines_recoltes: list[dict] = []


class ImpactDemenagementResponse(BaseModel):
    """Réponse évaluation impact déménagement."""

    scenario_nom: str
    impacts: list[dict] = []
    score_global: float | None = None
    recommandation: str = ""
    details: dict = {}


class TerroirRecettesResponse(BaseModel):
    """Réponse recettes terroir local."""

    localisation: str
    region: str = ""
    recettes_suggerees: list[dict] = []
    nb_recettes: int = 0


class ActiviteJulesPotagerResponse(BaseModel):
    """Réponse activités Jules au potager."""

    activites: list[dict] = []
    plantes_disponibles: list[str] = []
    age_jules_mois: int | None = None


class VerificationStockRecetteResponse(BaseModel):
    """Réponse vérification stock pour une recette."""

    recette_id: int
    recette_nom: str = ""
    ingredients_ok: list[dict] = []
    ingredients_manquants: list[dict] = []
    taux_couverture: float = 0


class HistoriqueModificationItem(BaseModel):
    """Élément de l'historique des modifications."""

    id: int
    entity_type: str
    entity_id: int
    champ_modifie: str
    ancienne_valeur: str | None = None
    nouvelle_valeur: str | None = None
    modifie_par: str = "system"
    modifie_le: str


class HistoriqueModificationsResponse(BaseModel):
    """Réponse historique des modifications."""

    items: list[HistoriqueModificationItem] = []
    nb_total: int = 0


# ═══════════════════════════════════════════════════════════
# PHASE E — BRIDGES INTER-MODULES AVANCÉS
# ═══════════════════════════════════════════════════════════


class RepasConflitItem(BaseModel):
    """Repas en conflit avec des tâches maison."""

    id: int
    type_repas: str
    recette_id: int | None = None
    temps_total: int | None = None
    complexe: bool = False


class ConflitPlanningItem(BaseModel):
    """Conflit détecté entre planning repas et tâches maison."""

    date: str
    repas: RepasConflitItem
    taches_maison: list[dict] = []
    niveau: str = "attention"


class ConflisFplanningResponse(BaseModel):
    """Réponse détection conflits planning."""

    periode: dict
    nb_conflits: int = 0
    conflits: list[ConflitPlanningItem] = []
    suggestions: list[str] = []
    nb_taches_maison_periode: int = 0
    nb_taches_sans_conflit: int = 0
    planning_id: int | None = None


class MeteoConditions(BaseModel):
    """Conditions météo pour la suggestion de recettes."""

    temperature: float = 15.0
    precipitations_mm: float = 0.0
    description: str = ""


class MeteoRecettesResponse(BaseModel):
    """Réponse météo → suggestions recettes."""

    conditions_meteo: dict
    conseil: str = ""
    emoji: str = "🍽️"
    recettes_suggerees: list[dict] = []
    nb_recettes: int = 0


class SuggestionCadeau(BaseModel):
    """Suggestion de cadeau d'anniversaire."""

    nom: str
    budget_estime: float
    categorie: str = "cadeau"


class CadeauAnniversaireResponse(BaseModel):
    """Réponse suggestions cadeaux anniversaire IA."""

    anniversaire: dict
    budget_estime: float = 40.0
    depenses_mois_en_cours: float = 0.0
    idees_existantes: str | None = None
    historique_recents: list[dict] = []
    suggestions_cadeaux: list[SuggestionCadeau] = []
    nb_suggestions: int = 0
    conseil: str = ""
