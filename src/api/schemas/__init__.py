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
    CursorPaginationParams,
    ErreurResponse,
    MessageResponse,
    PaginationParams,
    ReponseCurseur,
    ReponsePaginee,
    decode_cursor,
    encode_cursor,
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
)

# Planning
from .planning import (
    PlanningSemaineResponse,
    RepasBase,
    RepasCreate,
    RepasResponse,
)

# Recettes
from .recettes import (
    RecetteBase,
    RecetteCreate,
    RecetteResponse,
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
    "PaginationParams",
    "ReponsePaginee",
    "MessageResponse",
    "ErreurResponse",
    "CursorPaginationParams",
    "ReponseCurseur",
    "encode_cursor",
    "decode_cursor",
    # Auth
    "LoginRequest",
    "UserInfoResponse",
    # Recettes
    "RecetteBase",
    "RecetteCreate",
    "RecetteResponse",
    # Inventaire
    "InventaireItemBase",
    "InventaireItemCreate",
    "InventaireItemResponse",
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
]
