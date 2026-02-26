"""
Schémas Pydantic pour l'API REST.

Centralise tous les schémas de validation et sérialisation.
"""

# Base et mixins
# Auth
from .auth import (
    LoginRequest,
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
    CourseItemBase,
    CourseListCreate,
    ListeCoursesResponse,
    ListeCoursesResume,
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
]
