"""
Schémas Pydantic pour l'API REST.

Centralise tous les schémas de validation et sérialisation.
"""

# Base et mixins
# Auth
from .auth import (
    LoginRequest,
    RegisterRequest,
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
    ArticleResponse,
    CheckoutArticleRequest,
    CheckoutArticleResult,
    CheckoutCoursesRequest,
    CheckoutCoursesResponse,
    CourseItemBase,
    CourseListCreate,
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
    InventaireItemBase,
    InventaireItemCreate,
    InventaireItemResponse,
    InventaireItemUpdate,
)

# Planning
from .planning import (
    PlanningSemaineResponse,
    RepasBase,
    RepasCreate,
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
    "InventaireItemBase",
    "InventaireItemCreate",
    "InventaireItemResponse",
    "InventaireItemUpdate",
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
    "RepasBase",
    "RepasCreate",
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
]
