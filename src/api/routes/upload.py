"""
Routes API pour l'upload de fichiers.

Upload vers Supabase Storage pour documents, photos, etc.
Note: En production, préférer l'upload direct depuis le frontend
vers Supabase Storage via le SDK client (évite de surcharger le backend).
Ce endpoint sert de fallback pour les cas où l'upload côté client n'est
pas possible.
"""

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_AUTH, REPONSES_CRUD_CREATION
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/upload", tags=["Upload"])

# Taille max: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "application/pdf",
    "text/csv",
}


@router.post("", responses={**REPONSES_AUTH, **REPONSES_CRUD_CREATION})
@gerer_exception_api
async def upload_fichier(
    file: UploadFile,
    bucket: str = "documents",
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Upload un fichier vers Supabase Storage.

    Buckets supportés: documents, photos, exports.
    Types autorisés: JPEG, PNG, WebP, GIF, PDF, CSV.
    Taille maximale: 10 MB.
    """
    if not file.filename:
        raise HTTPException(status_code=422, detail="Nom de fichier requis")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Type de fichier non autorisé: {file.content_type}. "
            f"Autorisés: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    if bucket not in {"documents", "photos", "exports"}:
        raise HTTPException(
            status_code=422,
            detail="Bucket non autorisé. Utilisez: documents, photos, exports",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Fichier trop volumineux ({len(content)} bytes). Maximum: {MAX_FILE_SIZE} bytes",
        )

    try:
        from supabase import create_client

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_url or not supabase_key:
            raise HTTPException(
                status_code=503,
                detail="Supabase Storage non configuré",
            )

        client = create_client(supabase_url, supabase_key)

        # Chemin sécurisé: user_id/timestamp_filename
        import time

        safe_filename = file.filename.replace("/", "_").replace("\\", "_")
        path = f"{user['id']}/{int(time.time())}_{safe_filename}"

        result = client.storage.from_(bucket).upload(
            path,
            content,
            {"content-type": file.content_type},
        )

        public_url = client.storage.from_(bucket).get_public_url(path)

        logger.info(f"Fichier uploadé: {bucket}/{path} ({len(content)} bytes)")

        return {
            "url": public_url,
            "path": path,
            "bucket": bucket,
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
        }

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="SDK Supabase non disponible",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'upload du fichier",
        )


# ─── Album photos (Supabase Storage) ──────────────────────


def _get_supabase_client():
    """Crée et retourne un client Supabase, ou lève 503."""
    try:
        from supabase import create_client
    except ImportError:
        raise HTTPException(status_code=503, detail="SDK Supabase non disponible")

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        raise HTTPException(status_code=503, detail="Supabase Storage non configuré")
    return create_client(supabase_url, supabase_key)


@router.get(
    "/photos",
    responses=REPONSES_AUTH,
    summary="Lister les photos de l'album famille",
)
@gerer_exception_api
async def lister_photos(
    categorie: str | None = None,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les photos uploadées dans le bucket photos pour l'utilisateur."""
    try:
        client = _get_supabase_client()
        prefix = f"{user['id']}/"
        if categorie:
            prefix = f"{user['id']}/{categorie}/"

        result = client.storage.from_("photos").list(prefix)
        photos = []
        for item in result or []:
            name = item.get("name", "")
            if not name or name.startswith("."):
                continue
            path = f"{prefix}{name}"
            photos.append(
                {
                    "id": name,
                    "nom": name,
                    "url": client.storage.from_("photos").get_public_url(path),
                    "path": path,
                    "taille": item.get("metadata", {}).get("size", 0),
                    "date_upload": item.get("created_at", ""),
                }
            )
        return {"items": photos, "total": len(photos)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur listing photos: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du listing des photos")


@router.delete(
    "/photos/{path:path}",
    responses=REPONSES_AUTH,
    summary="Supprimer une photo de l'album",
)
@gerer_exception_api
async def supprimer_photo(
    path: str,
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, str]:
    """Supprime une photo du bucket Supabase Storage."""
    # Sécurité: vérifier que le path appartient à l'utilisateur
    if not path.startswith(f"{user['id']}/"):
        raise HTTPException(status_code=403, detail="Accès refusé")

    try:
        client = _get_supabase_client()
        client.storage.from_("photos").remove([path])
        logger.info(f"Photo supprimée: photos/{path}")
        return {"message": "Photo supprimée"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression photo: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
