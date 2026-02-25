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
    "ReponsePaginee",
    "MessageResponse",
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
