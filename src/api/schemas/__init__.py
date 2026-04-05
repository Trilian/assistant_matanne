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
    ArticleDriveResponse,
    CheckoutArticleRequest,
    CheckoutArticleResult,
    CheckoutCoursesRequest,
    CheckoutCoursesResponse,
    CorrespondanceDriveCreate,
    CorrespondanceDriveResponse,
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
    ArticleConsolideResponse,
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
    AdaptationRecetteResponse,
    SuggestionRecetteItem,
    SuggestionsPlanningResponse,
    SuggestionsRecettesResponse,
    SubstitutionIngredientResponse,
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
    AlertePeremptionResponse,
    ArticleCellierCreate,
    ArticleCellierPatch,
    ArticleCellierResponse,
    ArtisanCreate,
    ArtisanPatch,
    ArtisanResponse,
    BudgetMeublesResponse,
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
    StatsArtisansResponse,
    StatsCellierResponse,
    StatsDepensesResponse,
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

# Admin
from .admin import (
    AdminAuditLogsResponse,
    AdminAuditStatsResponse,
    AdminBridgesStatusResponse,
    AdminConfigExportResponse,
    AdminCoherenceDBResponse,
    AdminDryRunCompareResponse,
    AdminEventResponse,
    AdminEventsListResponse,
    AdminExportDBResponse,
    AdminHistoriqueNotificationsResponse,
    AdminImportDBResponse,
    AdminJobHealthResponse,
    AdminJobHistoriqueResponse,
    AdminJobLogsResponse,
    AdminJobResume,
    AdminJobScheduleModifie,
    AdminJobsRunAllResponse,
    AdminNotificationTestAllResponse,
    AdminNotificationTestResponse,
    AdminPreviewTemplateResponse,
    AdminQueueNotificationsResponse,
    AdminSanteServicesResponse,
    AdminSchemaDiffResponse,
    AdminSimulerNotificationResponse,
    AdminSimulationJourneeResponse,
    AdminTemplatesNotificationsResponse,
)

# Voyages
from .voyages import (
    VoyageCreateResponse,
    VoyageDetailResponse,
    VoyageGenererCoursesResponse,
    VoyagePlanifieIAResponse,
    VoyageResume,
    VoyageTemplateItem,
    VoyageToggleChecklistResponse,
)

# Garmin
from .garmin import (
    GarminConnectCompleteResponse,
    GarminConnectUrlResponse,
    GarminDisconnectResponse,
    GarminRecommandationDinerResponse,
    GarminStatsResponse,
    GarminStatusResponse,
    GarminSyncResponse,
)

# Assistant
from .assistant import (
    ChatIAResponse,
    CommandeVocaleResponse,
    ExecIntentGoogleAssistantResponse,
    ExemplesCommandeVocaleResponse,
    IntentsGoogleAssistantResponse,
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
    "ArticleConsolideResponse",
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
    "CorrespondanceDriveCreate",
    "CorrespondanceDriveResponse",
    "ArticleDriveResponse",
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
    # Admin
    "AdminJobResume",
    "AdminJobsRunAllResponse",
    "AdminJobScheduleModifie",
    "AdminJobLogsResponse",
    "AdminJobHistoriqueResponse",
    "AdminDryRunCompareResponse",
    "AdminSimulationJourneeResponse",
    "AdminBridgesStatusResponse",
    "AdminSanteServicesResponse",
    "AdminSchemaDiffResponse",
    "AdminNotificationTestResponse",
    "AdminNotificationTestAllResponse",
    "AdminTemplatesNotificationsResponse",
    "AdminPreviewTemplateResponse",
    "AdminSimulerNotificationResponse",
    "AdminHistoriqueNotificationsResponse",
    "AdminQueueNotificationsResponse",
    "AdminConfigExportResponse",
    "AdminAuditLogsResponse",
    "AdminAuditStatsResponse",
    "AdminEventResponse",
    "AdminEventsListResponse",
    "AdminCoherenceDBResponse",
    "AdminExportDBResponse",
    "AdminImportDBResponse",
    "AdminJobHealthResponse",
    # Voyages
    "VoyageResume",
    "VoyageDetailResponse",
    "VoyageCreateResponse",
    "VoyageTemplateItem",
    "VoyagePlanifieIAResponse",
    "VoyageGenererCoursesResponse",
    "VoyageToggleChecklistResponse",
    # Garmin
    "GarminStatusResponse",
    "GarminConnectUrlResponse",
    "GarminConnectCompleteResponse",
    "GarminSyncResponse",
    "GarminStatsResponse",
    "GarminDisconnectResponse",
    "GarminRecommandationDinerResponse",
    # Assistant
    "CommandeVocaleResponse",
    "IntentsGoogleAssistantResponse",
    "ExecIntentGoogleAssistantResponse",
    "ChatIAResponse",
    "ExemplesCommandeVocaleResponse",
]
