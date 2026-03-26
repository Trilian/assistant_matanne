"""
Schémas Pydantic pour l'API REST.

Centralise tous les schémas de validation et sérialisation.
"""

# Base et mixins
# Auth
from .auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TwoFactorEnableResponse,
    TwoFactorLoginRequest,
    TwoFactorStatusResponse,
    TwoFactorVerifyRequest,
    UserInfoResponse,
)
from .base import (
    IdentifiedResponse,
    NomValidatorMixin,
    QuantiteStricteValidatorMixin,
    QuantiteValidatorMixin,
    TimestampedResponse,
    TypeRepasValidator,
)

# Common
from .common import (
    ErrorResponse,
    MessageResponse,
    ReponsePaginee,
)

# Courses
from .courses import (
    ArticleGenereResume,
    ArticleResponse,
    CheckoutArticleRequest,
    CheckoutArticleResult,
    CheckoutCoursesRequest,
    CheckoutCoursesResponse,
    CourseItemBase,
    CourseListCreate,
    GenererCoursesRequest,
    GenererCoursesResponse,
    ListeCoursesResponse,
    ListeCoursesResume,
    ScanBarcodeCheckoutRequest,
    ScanBarcodeCheckoutResponse,
)

# Error responses OpenAPI
from .errors import (
    REPONSE_401,
    REPONSE_403,
    REPONSE_404,
    REPONSE_422,
    REPONSE_429,
    REPONSE_500,
    REPONSE_503,
    REPONSES_AUTH,
    REPONSES_AUTH_ADMIN,
    REPONSES_AUTH_LOGIN,
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_IA,
    REPONSES_LISTE,
    combiner_reponses,
)

# Inventaire
from .inventaire import (
    ArticleBatchTrouve,
    InventaireItemBase,
    InventaireItemCreate,
    InventaireItemResponse,
    InventaireItemUpdate,
    ScanBatchRequest,
    ScanBatchResponse,
)

# Planning
from .planning import (
    GenererPlanningRequest,
    PlanningSemaineResponse,
    RepasBase,
    RepasCreate,
    RepasRapideSuggestion,
    RepasResponse,
)

# Push
from .push import (
    PushStatusResponse,
    PushSubscriptionKeys,
    PushSubscriptionRequest,
    PushSubscriptionResponse,
    PushUnsubscribeRequest,
)

# Recettes
from .recettes import (
    RecetteBase,
    RecetteCreate,
    RecettePatch,
    RecetteResponse,
)

# Suggestions IA
from .suggestions import (
    SuggestionRecetteItem,
    SuggestionsPlanningResponse,
    SuggestionsRecettesResponse,
)

# Anti-Gaspillage
from .anti_gaspillage import (
    ArticlePerissable,
    ReponseAntiGaspillage,
    ScoreAntiGaspillage,
)

# Batch Cooking
from .batch_cooking import (
    ConfigBatchResponse,
    EtapeBatchResponse,
    GenererSessionDepuisPlanningRequest,
    GenererSessionDepuisPlanningResponse,
    PreparationBatchResponse,
    SessionBatchCreate,
    SessionBatchPatch,
    SessionBatchResponse,
)

# Dashboard
from .dashboard import (
    DonneesTableauBord,
    ResumeBudget,
    StatistiquesRapides,
)

# Documents
from .documents import (
    DocumentCreate,
    DocumentPatch,
    DocumentResponse,
)

# Préférences
from .preferences import (
    PreferencesCreate,
    PreferencesPatch,
    PreferencesResponse,
)

# Utilitaires
from .utilitaires import (
    ContactCreate,
    ContactPatch,
    ContactResponse,
    EnergieCreate,
    EnergiePatch,
    EnergieResponse,
    JournalCreate,
    JournalPatch,
    JournalResponse,
    LienCreate,
    LienPatch,
    LienResponse,
    MotDePasseCreate,
    MotDePassePatch,
    MotDePasseResponse,
    NoteCreate,
    NotePatch,
    NoteResponse,
)

# Calendriers
from .calendriers import (
    CalendrierDetailResponse,
    CalendrierResponse,
    EvenementDetailResponse,
    EvenementJourResponse,
    EvenementResponse,
    EvenementsAujourdhuiResponse,
    EvenementsSemaineResponse,
)

# Export
from .export import (
    ExportPDFRequest,
    ExportPDFResponse,
    TYPES_EXPORT_VALIDES,
)

# Jeux
from .jeux import (
    CotesMatch,
    EquipeDetailResponse,
    EquipeResponse,
    GrilleLotoResponse,
    MatchDetailResponse,
    MatchEquipeRef,
    MatchResponse,
    PariCreate,
    PariPatch,
    PariResume,
    PariResponse,
    PredictionMatch,
    StatistiquesParis,
    TirageLotoResponse,
)

# Maison
from .maison import (
    ActionEcoCreate,
    ActionEcoPatch,
    ActionEcoResponse,
    AlerteContratResponse,
    AlerteGarantieResponse,
    AlertePeremptionResponse,
    ArticleCellierCreate,
    ArticleCellierPatch,
    ArticleCellierResponse,
    ArtisanCreate,
    ArtisanPatch,
    ArtisanResponse,
    BudgetMeublesResponse,
    ContratCreate,
    ContratPatch,
    ContratResponse,
    DepenseMaisonCreate,
    DepenseMaisonPatch,
    DepenseMaisonResponse,
    DevisCreate,
    DevisPatch,
    DevisResponse,
    DiagnosticCreate,
    DiagnosticPatch,
    DiagnosticResponse,
    ElementJardinCreate,
    ElementJardinPatch,
    ElementJardinResponse,
    EntretienSaisonnierCreate,
    EntretienSaisonnierPatch,
    EntretienSaisonnierResponse,
    EstimationCreate,
    EstimationPatch,
    EstimationResponse,
    GarantieCreate,
    GarantiePatch,
    GarantieResponse,
    IncidentSAVCreate,
    IncidentSAVPatch,
    IncidentSAVResponse,
    InterventionCreate,
    InterventionPatch,
    InterventionResponse,
    MeubleCreate,
    MeublePatch,
    MeubleResponse,
    ObjetCreate,
    ObjetPatch,
    ObjetResponse,
    PieceCreate,
    PiecePatch,
    PieceResponse,
    ProjetCreate,
    ProjetPatch,
    ProjetResponse,
    ReleveCompteurCreate,
    ReleveCompteurPatch,
    ReleveCompteurResponse,
    ResumeFinancierContratsResponse,
    StatsArtisansResponse,
    StatsCellierResponse,
    StatsDepensesResponse,
    StatsGarantiesResponse,
    StatsHubMaisonResponse,
    StockCreate,
    StockPatch,
    StockResponse,
    TacheEntretienCreate,
    TacheEntretienPatch,
    TacheEntretienResponse,
    TraitementNuisibleCreate,
    TraitementNuisiblePatch,
    TraitementNuisibleResponse,
)

__all__ = [
    # Base
    "NomValidatorMixin",
    "QuantiteValidatorMixin",
    "QuantiteStricteValidatorMixin",
    "TimestampedResponse",
    "IdentifiedResponse",
    "TypeRepasValidator",
    # Common
    "ErrorResponse",
    "ReponsePaginee",
    "MessageResponse",
    # Error responses
    "REPONSE_401",
    "REPONSE_403",
    "REPONSE_404",
    "REPONSE_422",
    "REPONSE_429",
    "REPONSE_500",
    "REPONSE_503",
    "REPONSES_AUTH",
    "REPONSES_AUTH_ADMIN",
    "REPONSES_AUTH_LOGIN",
    "REPONSES_CRUD_CREATION",
    "REPONSES_CRUD_ECRITURE",
    "REPONSES_CRUD_LECTURE",
    "REPONSES_CRUD_SUPPRESSION",
    "REPONSES_IA",
    "REPONSES_LISTE",
    "combiner_reponses",
    # Auth
    "LoginRequest",
    "RegisterRequest",
    "UserInfoResponse",
    # Recettes
    "RecetteBase",
    "RecetteCreate",
    "RecettePatch",
    "RecetteResponse",
    # Inventaire
    "ArticleBatchTrouve",
    "InventaireItemBase",
    "InventaireItemCreate",
    "InventaireItemResponse",
    "InventaireItemUpdate",
    "ScanBatchRequest",
    "ScanBatchResponse",
    # Courses
    "CourseItemBase",
    "CourseListCreate",
    "ListeCoursesResume",
    "ArticleResponse",
    "ListeCoursesResponse",
    "CheckoutArticleRequest",
    "CheckoutCoursesRequest",
    "CheckoutArticleResult",
    "CheckoutCoursesResponse",
    "ScanBarcodeCheckoutRequest",
    "ScanBarcodeCheckoutResponse",
    # Planning
    "GenererPlanningRequest",
    "RepasBase",
    "RepasCreate",
    "RepasRapideSuggestion",
    "RepasResponse",
    "PlanningSemaineResponse",
    # Push
    "PushSubscriptionKeys",
    "PushSubscriptionRequest",
    "PushUnsubscribeRequest",
    "PushSubscriptionResponse",
    "PushStatusResponse",
    # Suggestions IA
    "SuggestionRecetteItem",
    "SuggestionsRecettesResponse",
    "SuggestionsPlanningResponse",
    # Anti-Gaspillage
    "ArticlePerissable",
    "ScoreAntiGaspillage",
    "ReponseAntiGaspillage",
    # Batch Cooking
    "SessionBatchCreate",
    "SessionBatchPatch",
    "SessionBatchResponse",
    "EtapeBatchResponse",
    "PreparationBatchResponse",
    "ConfigBatchResponse",
    # Dashboard
    "StatistiquesRapides",
    "ResumeBudget",
    "DonneesTableauBord",
    # Documents
    "DocumentCreate",
    "DocumentPatch",
    "DocumentResponse",
    # Préférences
    "PreferencesCreate",
    "PreferencesPatch",
    "PreferencesResponse",
    # Utilitaires
    "NoteCreate",
    "NotePatch",
    "NoteResponse",
    "JournalCreate",
    "JournalPatch",
    "JournalResponse",
    "ContactCreate",
    "ContactPatch",
    "ContactResponse",
    "LienCreate",
    "LienPatch",
    "LienResponse",
    "MotDePasseCreate",
    "MotDePassePatch",
    "MotDePasseResponse",
    "EnergieCreate",
    "EnergiePatch",
    "EnergieResponse",
    # Maison
    "ProjetCreate",
    "ProjetPatch",
    "ProjetResponse",
    "TacheEntretienCreate",
    "TacheEntretienPatch",
    "TacheEntretienResponse",
    "ElementJardinCreate",
    "ElementJardinPatch",
    "ElementJardinResponse",
    "StockCreate",
    "StockPatch",
    "StockResponse",
    "MeubleCreate",
    "MeublePatch",
    "MeubleResponse",
    "BudgetMeublesResponse",
    "ArticleCellierCreate",
    "ArticleCellierPatch",
    "ArticleCellierResponse",
    "AlertePeremptionResponse",
    "StatsCellierResponse",
    "ArtisanCreate",
    "ArtisanPatch",
    "ArtisanResponse",
    "InterventionCreate",
    "InterventionPatch",
    "InterventionResponse",
    "StatsArtisansResponse",
    "ContratCreate",
    "ContratPatch",
    "ContratResponse",
    "AlerteContratResponse",
    "ResumeFinancierContratsResponse",
    "GarantieCreate",
    "GarantiePatch",
    "GarantieResponse",
    "IncidentSAVCreate",
    "IncidentSAVPatch",
    "IncidentSAVResponse",
    "AlerteGarantieResponse",
    "StatsGarantiesResponse",
    "DiagnosticCreate",
    "DiagnosticPatch",
    "DiagnosticResponse",
    "EstimationCreate",
    "EstimationPatch",
    "EstimationResponse",
    "ActionEcoCreate",
    "ActionEcoPatch",
    "ActionEcoResponse",
    "DepenseMaisonCreate",
    "DepenseMaisonPatch",
    "DepenseMaisonResponse",
    "StatsDepensesResponse",
    "TraitementNuisibleCreate",
    "TraitementNuisiblePatch",
    "TraitementNuisibleResponse",
    "DevisCreate",
    "DevisPatch",
    "DevisResponse",
    "EntretienSaisonnierCreate",
    "EntretienSaisonnierPatch",
    "EntretienSaisonnierResponse",
    "ReleveCompteurCreate",
    "ReleveCompteurPatch",
    "ReleveCompteurResponse",
    "PieceCreate",
    "PiecePatch",
    "PieceResponse",
    "ObjetCreate",
    "ObjetPatch",
    "ObjetResponse",
    "StatsHubMaisonResponse",
    # Calendriers
    "CalendrierResponse",
    "CalendrierDetailResponse",
    "EvenementResponse",
    "EvenementDetailResponse",
    "EvenementJourResponse",
    "EvenementsAujourdhuiResponse",
    "EvenementsSemaineResponse",
    # Export
    "ExportPDFRequest",
    "ExportPDFResponse",
    "TYPES_EXPORT_VALIDES",
    # Jeux
    "EquipeResponse",
    "EquipeDetailResponse",
    "MatchResponse",
    "MatchDetailResponse",
    "MatchEquipeRef",
    "CotesMatch",
    "PredictionMatch",
    "PariResume",
    "PariCreate",
    "PariPatch",
    "PariResponse",
    "StatistiquesParis",
    "TirageLotoResponse",
    "GrilleLotoResponse",
]
