"""
Services Courses - Point d'Entrée Module

Regroupe tous les services liés aux courses :
- CRUD courses
- IA (suggestions intelligentes)
- Import/Export
- Constantes métier (magasins)
"""

# Service CRUD principal
from .courses_service import (
    CoursesService,
    courses_service,
    MAGASINS_CONFIG,
)

# Service IA
from .courses_ai_service import (
    CoursesAIService,
    create_courses_ai_service,
)

# Service Import/Export
from .courses_io_service import (
    CoursesExporter,
    CoursesImporter,
)

__all__ = [
    # Classes
    "CoursesService",
    "CoursesAIService",
    "CoursesExporter",
    "CoursesImporter",

    # Instances (singletons)
    "courses_service",
    "create_courses_ai_service",

    # Constantes métier
    "MAGASINS_CONFIG",
]