"""
Routes API pour les documents famille.

CRUD pour les documents familiaux (carnet de santé, assurance, etc.)
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.documents import DocumentCreate, DocumentPatch, DocumentResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


@router.get("", responses=REPONSES_LISTE)
@gerer_exception_api
async def lister_documents(
    categorie: str | None = Query(None, description="Filtrer par catégorie"),
    membre: str | None = Query(None, description="Filtrer par membre de famille"),
    expire: bool | None = Query(None, description="Filtrer par statut expiration"),
    search: str | None = Query(None, description="Recherche dans le titre"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les documents familiaux avec filtres et pagination."""
    from src.core.models import DocumentFamille

    def _query():
        with executer_avec_session() as session:
            query = session.query(DocumentFamille).filter(
                DocumentFamille.actif.is_(True)
            )

            if categorie:
                query = query.filter(DocumentFamille.categorie == categorie)
            if membre:
                query = query.filter(DocumentFamille.membre_famille == membre)
            if search:
                safe = search.replace("%", "\\%").replace("_", "\\_")
                query = query.filter(DocumentFamille.titre.ilike(f"%{safe}%"))
            if expire is True:
                query = query.filter(
                    DocumentFamille.date_expiration.isnot(None),
                    DocumentFamille.date_expiration < date.today(),
                )
            elif expire is False:
                query = query.filter(
                    (DocumentFamille.date_expiration.is_(None))
                    | (DocumentFamille.date_expiration >= date.today())
                )

            total = query.count()
            items = (
                query.order_by(DocumentFamille.cree_le.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            return {
                "items": [
                    {
                        "id": d.id,
                        "titre": d.titre,
                        "categorie": d.categorie,
                        "membre_famille": d.membre_famille,
                        "fichier_url": d.fichier_url,
                        "fichier_nom": d.fichier_nom,
                        "date_document": d.date_document.isoformat()
                        if d.date_document
                        else None,
                        "date_expiration": d.date_expiration.isoformat()
                        if d.date_expiration
                        else None,
                        "notes": d.notes,
                        "tags": d.tags or [],
                        "actif": d.actif,
                        "est_expire": d.est_expire,
                        "jours_avant_expiration": d.jours_avant_expiration
                        if hasattr(d, "jours_avant_expiration")
                        else None,
                    }
                    for d in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }

    return await executer_async(_query)


@router.get("/{document_id}", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def obtenir_document(
    document_id: int, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    """Récupère un document familial par son ID."""
    from src.core.models import DocumentFamille

    def _query():
        with executer_avec_session() as session:
            doc = (
                session.query(DocumentFamille)
                .filter(DocumentFamille.id == document_id)
                .first()
            )
            if not doc:
                raise HTTPException(status_code=404, detail="Document non trouvé")

            return {
                "id": doc.id,
                "titre": doc.titre,
                "categorie": doc.categorie,
                "membre_famille": doc.membre_famille,
                "fichier_url": doc.fichier_url,
                "fichier_nom": doc.fichier_nom,
                "date_document": doc.date_document.isoformat()
                if doc.date_document
                else None,
                "date_expiration": doc.date_expiration.isoformat()
                if doc.date_expiration
                else None,
                "notes": doc.notes,
                "tags": doc.tags or [],
                "actif": doc.actif,
                "est_expire": doc.est_expire,
            }

    return await executer_async(_query)


@router.post("", status_code=201, responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def creer_document(
    donnees: DocumentCreate, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    """Crée un nouveau document familial."""
    from src.core.models import DocumentFamille

    def _create():
        with executer_avec_session() as session:
            doc = DocumentFamille(
                titre=donnees.titre,
                categorie=donnees.categorie,
                membre_famille=donnees.membre_famille,
                fichier_url=donnees.fichier_url,
                fichier_nom=donnees.fichier_nom,
                date_document=donnees.date_document,
                date_expiration=donnees.date_expiration,
                notes=donnees.notes,
                tags=donnees.tags,
                rappel_expiration_jours=donnees.rappel_expiration_jours,
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)

            return {"message": "Document créé", "id": doc.id}

    return await executer_async(_create)


@router.patch("/{document_id}", responses=REPONSES_CRUD_ECRITURE)
@gerer_exception_api
async def modifier_document(
    document_id: int,
    donnees: DocumentPatch,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Modifie un document familial existant."""
    from src.core.models import DocumentFamille

    def _update():
        with executer_avec_session() as session:
            doc = (
                session.query(DocumentFamille)
                .filter(DocumentFamille.id == document_id)
                .first()
            )
            if not doc:
                raise HTTPException(status_code=404, detail="Document non trouvé")

            for key, value in donnees.model_dump(exclude_unset=True).items():
                setattr(doc, key, value)

            session.commit()
            session.refresh(doc)

            return {"message": "Document modifié", "id": doc.id}

    return await executer_async(_update)


@router.delete("/{document_id}", responses=REPONSES_CRUD_SUPPRESSION)
@gerer_exception_api
async def supprimer_document(
    document_id: int, user: dict[str, Any] = Depends(require_auth)
) -> dict[str, Any]:
    """Supprime un document (soft delete via actif=False)."""
    from src.core.models import DocumentFamille

    def _delete():
        with executer_avec_session() as session:
            doc = (
                session.query(DocumentFamille)
                .filter(DocumentFamille.id == document_id)
                .first()
            )
            if not doc:
                raise HTTPException(status_code=404, detail="Document non trouvé")

            doc.actif = False
            session.commit()

            return {"message": "Document supprimé"}

    return await executer_async(_delete)
