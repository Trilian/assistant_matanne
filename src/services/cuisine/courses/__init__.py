"""
Package courses - Services de gestion des listes de courses.

Ce package regroupe:
- types.py: Schemas Pydantic (SuggestionCourses, ArticleCourse, etc.)
- constantes.py: Mappings rayons et priorites
- service.py: ServiceCourses - CRUD et suggestions IA
- intelligentes.py: ServiceCoursesIntelligentes - Generation depuis planning

Exemple d'utilisation:
    from src.services.cuisine.courses import obtenir_service_courses, obtenir_service_courses_intelligentes

    # Service de base
    service = obtenir_service_courses()
    liste = service.obtenir_liste_courses()

    # Service intelligent
    service_intel = obtenir_service_courses_intelligentes()
    liste_smart = service_intel.generer_liste_courses()
"""

# Types et schemas
# Constantes
from .constantes import MAPPING_RAYONS, PRIORITES

# Service de base
from .service import (
    CoursesService,
    ServiceCourses,
    courses_service,
    get_courses_service,
    obtenir_service_courses,
)

# Service intelligent
from .suggestion import (
    CoursesIntelligentesService,
    ServiceCoursesIntelligentes,
    get_courses_intelligentes_service,
    obtenir_service_courses_intelligentes,
)
from .types import (
    ArticleCourse,
    ListeCoursesIntelligente,
    SuggestionCourses,
    SuggestionSubstitution,
)

__all__ = [
    # ═══════════════════════════════════════════════════════════
    # TYPES (NOMS FRANCAIS)
    # ═══════════════════════════════════════════════════════════
    "SuggestionCourses",
    "ArticleCourse",
    "ListeCoursesIntelligente",
    "SuggestionSubstitution",
    # ═══════════════════════════════════════════════════════════
    # CONSTANTES
    # ═══════════════════════════════════════════════════════════
    "MAPPING_RAYONS",
    "PRIORITES",
    # ═══════════════════════════════════════════════════════════
    # SERVICE DE BASE (NOMS FRANCAIS)
    # ═══════════════════════════════════════════════════════════
    "ServiceCourses",
    "obtenir_service_courses",
    # ═══════════════════════════════════════════════════════════
    # SERVICE INTELLIGENT (NOMS FRANCAIS)
    # ═══════════════════════════════════════════════════════════
    "ServiceCoursesIntelligentes",
    "obtenir_service_courses_intelligentes",
    # ═══════════════════════════════════════════════════════════
    # ALIASES UTILISÉS (COMPATIBILITÉ)
    # ═══════════════════════════════════════════════════════════
    # Service base
    "CoursesService",
    "get_courses_service",
    "courses_service",
    # Service intelligent
    "CoursesIntelligentesService",
    "get_courses_intelligentes_service",
]
