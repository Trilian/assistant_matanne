"""
DTO (Data Transfer Objects) — Couche de transfert entre services et modules.

Les DTOs sont des Pydantic models immuables qui découplent la couche ORM
(SQLAlchemy) de la couche présentation (Streamlit modules).

Avantages:
- Pas de ``DetachedInstanceError`` (objets plain dict-like, pas lazy-loaded)
- Contrat API explicite entre services et UI
- Sérialisation facile (JSON, dict)
- Validation intégrée via Pydantic

Architecture:
    Service → retourne DTO → Module UI consomme DTO
    Module UI → envoie Command DTO → Service écrit

Règle: ``model_config = {"from_attributes": True}`` permet la conversion
depuis un modèle ORM: ``RecetteDTO.model_validate(recette_orm)``

Usage:
    from src.core.dto import RecetteDTO, RecetteResumeDTO

    # Depuis un service
    def get_recette(id: int) -> RecetteDTO | None:
        orm_obj = db.query(Recette).get(id)
        return RecetteDTO.model_validate(orm_obj) if orm_obj else None

    # Depuis un module
    recette = get_recette_service().get_recette(42)
    st.write(recette.nom)  # Accès direct, pas de lazy loading
"""

# Re-exports pour accès rapide
from .base import (
    BaseDTO,
    IdentifiedDTO,
    PaginatedResult,
    ResultatAction,
    TimestampedDTO,
)
from .courses import ArticleCoursesDTO, ListeCoursesDTO
from .famille import (
    ActiviteFamilleDTO,
    ActiviteWeekendDTO,
    ProfilEnfantDTO,
    RoutineFamilleDTO,
    TacheRoutineDTO,
)
from .inventaire import ArticleInventaireDTO, ArticleInventaireResumeDTO
from .maison import (
    DepenseDTO,
    ElementJardinDTO,
    ProjetDTO,
    RoutineEntretienDTO,
    TacheProjetDTO,
)
from .planning import PlanningResumeDTO, RepasDTO
from .recettes import (
    EtapeRecetteDTO,
    IngredientDTO,
    RecetteDTO,
    RecetteResumeDTO,
)

__all__ = [
    # Base
    "BaseDTO",
    "TimestampedDTO",
    "IdentifiedDTO",
    "ResultatAction",
    "PaginatedResult",
    # Recettes
    "RecetteDTO",
    "RecetteResumeDTO",
    "IngredientDTO",
    "EtapeRecetteDTO",
    # Inventaire
    "ArticleInventaireDTO",
    "ArticleInventaireResumeDTO",
    # Courses
    "ArticleCoursesDTO",
    "ListeCoursesDTO",
    # Famille
    "ProfilEnfantDTO",
    "ActiviteFamilleDTO",
    "ActiviteWeekendDTO",
    "RoutineFamilleDTO",
    "TacheRoutineDTO",
    # Maison
    "ProjetDTO",
    "TacheProjetDTO",
    "ElementJardinDTO",
    "RoutineEntretienDTO",
    "DepenseDTO",
    # Planning
    "PlanningResumeDTO",
    "RepasDTO",
]
