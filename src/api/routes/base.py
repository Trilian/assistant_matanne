"""
Classes de base pour les routes CRUD.

Fournit un router générique avec les opérations CRUD standard.
"""

from typing import Any, Generic, Sequence, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.api.dependencies import require_auth
from src.api.schemas import MessageResponse
from src.api.utils import construire_reponse_paginee, executer_avec_session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class CRUDRouter(Generic[ModelType, CreateSchemaType, ResponseSchemaType]):
    """
    Router générique pour les opérations CRUD.

    Usage:
        from src.core.models import Recette
        from src.api.schemas import RecetteCreate, RecetteResponse

        crud = CRUDRouter(
            model=Recette,
            create_schema=RecetteCreate,
            response_schema=RecetteResponse,
            prefix="/api/v1/recettes",
            tags=["Recettes"],
        )
        router = crud.router
    """

    def __init__(
        self,
        model: type[ModelType],
        create_schema: type[CreateSchemaType],
        response_schema: type[ResponseSchemaType],
        prefix: str,
        tags: Sequence[str],
        id_field: str = "id",
        order_by: str | None = None,
        name_singular: str = "élément",
        name_plural: str = "éléments",
    ):
        self.model = model
        self.create_schema = create_schema
        self.response_schema = response_schema
        self.id_field = id_field
        self.order_by = order_by
        self.name_singular = name_singular
        self.name_plural = name_plural

        self.router = APIRouter(prefix=prefix, tags=list(tags))
        self._register_routes()

    def _register_routes(self):
        """Enregistre les routes CRUD standard."""

        @self.router.get("")
        async def list_items(
            page: int = Query(1, ge=1),
            page_size: int = Query(20, ge=1, le=100),
        ) -> dict[str, Any]:
            """Liste les éléments avec pagination."""
            return self._list(page, page_size)

        @self.router.get("/{item_id}", response_model=self.response_schema)
        async def get_item(item_id: int) -> Any:
            """Récupère un élément par son ID."""
            return self._get_by_id(item_id)

        @self.router.post("", response_model=self.response_schema)
        async def create_item(
            data: self.create_schema,  # type: ignore[valid-type]
            user: dict[str, Any] = Depends(require_auth),
        ) -> Any:
            """Crée un nouvel élément."""
            return self._create(data)

        @self.router.put("/{item_id}", response_model=self.response_schema)
        async def update_item(
            item_id: int,
            data: self.create_schema,  # type: ignore[valid-type]
            user: dict[str, Any] = Depends(require_auth),
        ) -> Any:
            """Met à jour un élément."""
            return self._update(item_id, data)

        @self.router.delete("/{item_id}", response_model=MessageResponse)
        async def delete_item(
            item_id: int,
            user: dict[str, Any] = Depends(require_auth),
        ) -> MessageResponse:
            """Supprime un élément."""
            return self._delete(item_id)

    def _list(
        self, page: int, page_size: int, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Liste les éléments avec pagination."""
        with executer_avec_session() as session:
            query = session.query(self.model)

            if filters:
                for field, value in filters.items():
                    if value is not None and hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)

            total = query.count()

            if self.order_by and hasattr(self.model, self.order_by):
                query = query.order_by(getattr(self.model, self.order_by))

            items = query.offset((page - 1) * page_size).limit(page_size).all()

            return construire_reponse_paginee(items, total, page, page_size, self.response_schema)

    def _get_by_id(self, item_id: int) -> Any:
        """Récupère un élément par ID."""
        with executer_avec_session() as session:
            id_col = getattr(self.model, self.id_field)
            item = session.query(self.model).filter(id_col == item_id).first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"{self.name_singular.capitalize()} non trouvé(e)",
                )

            return self.response_schema.model_validate(item)

    def _create(self, data: CreateSchemaType) -> Any:
        """Crée un nouvel élément."""
        with executer_avec_session() as session:
            db_item = self.model(**data.model_dump(exclude_unset=True))
            session.add(db_item)
            session.commit()
            session.refresh(db_item)

            return self.response_schema.model_validate(db_item)

    def _update(self, item_id: int, data: CreateSchemaType) -> Any:
        """Met à jour un élément."""
        with executer_avec_session() as session:
            id_col = getattr(self.model, self.id_field)
            db_item = session.query(self.model).filter(id_col == item_id).first()

            if not db_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"{self.name_singular.capitalize()} non trouvé(e)",
                )

            for key, value in data.model_dump(exclude_unset=True).items():
                if hasattr(db_item, key):
                    setattr(db_item, key, value)

            session.commit()
            session.refresh(db_item)

            return self.response_schema.model_validate(db_item)

    def _delete(self, item_id: int) -> MessageResponse:
        """Supprime un élément."""
        with executer_avec_session() as session:
            id_col = getattr(self.model, self.id_field)
            db_item = session.query(self.model).filter(id_col == item_id).first()

            if not db_item:
                raise HTTPException(
                    status_code=404,
                    detail=f"{self.name_singular.capitalize()} non trouvé(e)",
                )

            session.delete(db_item)
            session.commit()

            return MessageResponse(
                message=f"{self.name_singular.capitalize()} supprimé(e)",
                id=item_id,
            )
