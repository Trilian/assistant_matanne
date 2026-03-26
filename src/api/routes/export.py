"""
Routes API pour l'export PDF et l'export/import de données.

Génération de documents PDF via le service ServiceExportPDF.
Export JSON multi-domaine et restauration via ExportService.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_CRUD_LECTURE, REPONSES_CRUD_CREATION
from src.api.utils import executer_async, gerer_exception_api
from src.services.rapports.export import obtenir_service_export_pdf

router = APIRouter(prefix="/api/v1/export", tags=["Export"])

TYPES_EXPORT = {"courses", "planning", "recette", "budget"}


@router.post("/pdf", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def exporter_pdf(
    type_export: str = Query(
        ...,
        description="Type d'export: courses, planning, recette, budget",
    ),
    id_ressource: int | None = Query(None, description="ID optionnel de la ressource"),
    user: dict[str, Any] = Depends(require_auth),
):
    """
    Génère un export PDF.

    Types supportés:
    - courses: Liste de courses active
    - planning: Planning de la semaine (id_ressource requis)
    - recette: Fiche recette détaillée (id_ressource requis)
    - budget: Résumé budget mensuel (id_ressource = période en jours, défaut: 30)
    """
    if type_export not in TYPES_EXPORT:
        raise HTTPException(
            status_code=422,
            detail=f"Type d'export non supporté: {type_export}",
        )

    if type_export in ("recette", "planning") and not id_ressource:
        raise HTTPException(
            status_code=422,
            detail=f"id_ressource requis pour {type_export}",
        )

    def _generate():
        service = obtenir_service_export_pdf()

        if type_export == "courses":
            return service.exporter_liste_courses(), "liste_courses"

        elif type_export == "planning":
            return service.exporter_planning_semaine(id_ressource), "planning_semaine"

        elif type_export == "recette":
            return service.exporter_recette(id_ressource), "recette"

        elif type_export == "budget":
            periode = id_ressource if id_ressource else 30  # Période en jours (défaut: 30)
            return service.exporter_budget(periode), "budget_familial"

    buffer, nom_fichier = await executer_async(_generate)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nom_fichier}.pdf"',
        },
    )


# ═══════════════════════════════════════════════════════════
# EXPORT / IMPORT DONNÉES (BACKUP)
# ═══════════════════════════════════════════════════════════

_DOMAINES_EXPORT = {
    "recettes": "🍽️ Recettes",
    "ingredients": "🥕 Ingrédients",
    "courses": "🛒 Listes de courses",
    "articles_courses": "📝 Articles courses",
    "inventaire": "🥫 Inventaire",
    "depenses": "💰 Dépenses",
    "planning": "📅 Planning",
    "notes": "📝 Notes",
    "journal": "📓 Journal de bord",
    "contacts": "📇 Contacts",
}


@router.get("/domaines", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def lister_domaines_export(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Liste les domaines de données disponibles pour l'export."""
    return {
        "domaines": [
            {"id": k, "label": v} for k, v in _DOMAINES_EXPORT.items()
        ]
    }


@router.get("/json", responses=REPONSES_CRUD_LECTURE)
@gerer_exception_api
async def exporter_json(
    domaines: str = Query(
        "recettes,courses,inventaire,planning,notes",
        description="Domaines séparés par virgule",
    ),
    mot_de_passe: str | None = Query(
        None,
        description="Si fourni, le fichier est chiffré (Fernet+PBKDF2). Extension .json.enc",
    ),
    user: dict[str, Any] = Depends(require_auth),
):
    """
    Exporte les données sélectionnées en JSON (téléchargement).

    Retourne un fichier JSON avec toutes les données des domaines demandés.
    Utile comme backup avant migration ou pour archivage.

    **Domaines disponibles**: recettes, ingredients, courses, articles_courses,
    inventaire, depenses, planning, notes, journal, contacts
    """
    domaines_list = [d.strip() for d in domaines.split(",") if d.strip()]
    invalides = [d for d in domaines_list if d not in _DOMAINES_EXPORT]
    if invalides:
        raise HTTPException(
            status_code=422,
            detail=f"Domaines inconnus: {invalides}. Disponibles: {list(_DOMAINES_EXPORT.keys())}",
        )

    from datetime import datetime

    def _export():
        from src.services.utilitaires.export_service import ExportService
        service = ExportService()
        if mot_de_passe:
            return service.exporter_json_chiffre(domaines_list, mot_de_passe)
        return service.exporter_json(domaines_list)

    resultat = await executer_async(_export)

    from fastapi.responses import Response
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if mot_de_passe:
        return Response(
            content=resultat,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="matanne_backup_{timestamp}.json.enc"',
            },
        )
    return Response(
        content=resultat.encode("utf-8") if isinstance(resultat, str) else resultat,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="matanne_backup_{timestamp}.json"',
        },
    )


@router.post("/restaurer", responses=REPONSES_CRUD_CREATION)
@gerer_exception_api
async def restaurer_depuis_json(
    file: UploadFile,
    domaines: str | None = Query(
        None,
        description="Domaines à restaurer (séparés par virgule, défaut = tous)",
    ),
    effacer_existant: bool = Query(
        False,
        description="Supprimer les données existantes avant restauration (DANGEREUX)",
    ),
    mot_de_passe: str | None = Query(
        None,
        description="Mot de passe si le fichier est chiffré (.json.enc)",
    ),
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """
    Restaure des données depuis un fichier JSON exporté.

    ⚠️ **Opération irréversible si `effacer_existant=true`.**

    - Accepte les fichiers `.json` et `.json.gz` (compressés)
    - Valide la structure avant import
    - Retourne un rapport détaillé (tables restaurées, erreurs)

    **Usage recommandé** : restaurer sur une instance vierge ou après backup.
    """
    if file.content_type not in ("application/json", "application/gzip", "application/octet-stream"):
        # Accept permissive — browsers send varying content-types for JSON files
        pass

    contenu = await file.read()
    if len(contenu) > 100 * 1024 * 1024:  # 100 Mo max
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (max 100 Mo)")

    # Déchiffrer si nécessaire
    if mot_de_passe:
        def _dechiffrer():
            from src.services.utilitaires.export_service import ExportService
            try:
                return ExportService.dechiffrer_json(contenu, mot_de_passe).encode("utf-8")
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        contenu = await executer_async(_dechiffrer)

    domaines_list = [d.strip() for d in domaines.split(",") if d.strip()] if domaines else None

    import io

    def _restore():
        from src.services.core.backup import obtenir_service_backup

        service = obtenir_service_backup()

        # Écrire dans un fichier temporaire car ServiceBackup travaille avec des paths
        import tempfile, os
        suffix = ".json.gz" if contenu[:2] == b"\x1f\x8b" else ".json"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contenu)
            tmp_path = tmp.name

        try:
            result = service.restore_backup(
                file_path=tmp_path,
                tables=domaines_list,
                clear_existing=effacer_existant,
            )
            return result
        finally:
            os.unlink(tmp_path)

    result = await executer_async(_restore)

    if result is None:
        raise HTTPException(status_code=422, detail="Échec de la restauration. Vérifiez le format du fichier.")

    return {
        "success": result.success,
        "message": result.message,
        "tables_restaurees": getattr(result, "tables_restored", []),
        "total_enregistrements": getattr(result, "records_restored", 0),
    }

