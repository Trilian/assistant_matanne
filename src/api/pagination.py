"""
Pagination cursor-based pour l'API REST.

Fournit une pagination par curseur (keyset pagination) en alternative
à la pagination offset qui pose des problèmes de performance sur grandes collections:
- Offset: O(n) - doit scanner toutes les lignes jusqu'à l'offset
- Cursor: O(1) - utilise un index pour sauter directement au curseur

⚠️ BUG B12 FIX: Tri stable requis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pagination par curseur requiert que:
1️⃣  Le cursor_field DOIT être le premier champ d'ordre (ou au minimum inclus dans order_by)
2️⃣  Le secondary_field doit être unique (généralement 'id') pour garantir stabilité
3️⃣  Si order_by != cursor_field, les suppressions concurrentes causent des sauts

EXEMPLE CORRECT:
    query = session.query(Activite).order_by(Activite.date_prevue.desc(), Activite.id.desc())
    return construire_reponse_cursor(
        items, limit,
        cursor_field="date_prevue",         ← Match l'ordre principal
        secondary_field="id",               ← Tie-breaker unique (stable sort)
    )

EXEMPLE INCORRECT (BUG):
    query = session.query(Activite).order_by(Activite.date_prevue.desc())  # ❌
    return construire_reponse_cursor(
        items, limit,
        cursor_field="id",                  # ← Mismatch! ordre ≠ cursor_field
    )
    # ↑ Suppressions concurrentes = sauts d'enregistrements

Usage:
    from src.api.pagination import (
        CursorParams,
        ReponseCursorPaginee,
        construire_reponse_cursor,
        decoder_cursor,
        appliquer_cursor_filter,
    )

    @router.get("/items")
    async def list_items(
        cursor: str | None = Query(None, description="Curseur de pagination"),
        limit: int = Query(20, ge=1, le=100),
    ):
        decoded = decoder_cursor(cursor) if cursor else None

        with executer_avec_session() as session:
            # ✅ Tri stable: cursor_field + secondary unique
            query = session.query(Item).order_by(Item.cree_le.desc(), Item.id.desc())

            if decoded:
                query = appliquer_cursor_filter(query, decoded, Item,
                                               cursor_field="cree_le",
                                               secondary_field="id")

            items = query.limit(limit + 1).all()

        return construire_reponse_cursor(items, limit,
                                        cursor_field="cree_le",
                                        secondary_field="id")
"""

import base64
import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PAGINÉS
# ═══════════════════════════════════════════════════════════


class CursorInfo(BaseModel):
    """Information du curseur pour la réponse."""

    next_cursor: str | None = Field(None, description="Curseur pour la page suivante")
    prev_cursor: str | None = Field(None, description="Curseur pour la page précédente")
    has_more: bool = Field(description="Indique s'il y a plus de résultats")


class ReponseCursorPaginee[T](BaseModel):
    """Réponse paginée avec curseur.

    Alternative à ReponsePaginee pour les grandes collections.

    Example:
        ```json
        {
            "items": [...],
            "cursor": {
                "next_cursor": "eyJpZCI6MTAwfQ==",
                "prev_cursor": null,
                "has_more": true
            },
            "limit": 20
        }
        ```
    """

    items: list[T]
    cursor: CursorInfo
    limit: int = Field(description="Nombre d'éléments demandés")


class CursorParams(BaseModel):
    """Paramètres de curseur décodés."""

    id: int | None = None
    created_at: datetime | None = None
    sort_value: Any = None
    direction: str = "forward"  # forward | backward


# ═══════════════════════════════════════════════════════════
# ENCODAGE / DÉCODAGE CURSEUR
# ═══════════════════════════════════════════════════════════


def encoder_cursor(
    values: dict[str, Any],
    direction: str = "forward",
) -> str:
    """
    Encode les valeurs de curseur en string base64.

    Utilise un format JSON compact encodé en base64 URL-safe.

    Args:
        values: Dict des valeurs (ex: {"id": 100, "created_at": "2026-02-25T..."})
        direction: Direction de pagination

    Returns:
        String base64 URL-safe
    """
    # Sérialiser les datetime
    serialized = {}
    for key, value in values.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value

    serialized["_dir"] = direction

    # Encoder en JSON puis base64
    json_str = json.dumps(serialized, separators=(",", ":"), sort_keys=True)
    return base64.urlsafe_b64encode(json_str.encode()).decode().rstrip("=")


def decoder_cursor(cursor: str) -> CursorParams:
    """
    Décode un curseur base64 en paramètres.

    Args:
        cursor: String base64 URL-safe

    Returns:
        CursorParams avec les valeurs décodées

    Raises:
        ValueError: Si le curseur est invalide
    """
    try:
        # Ajouter le padding manquant
        padding = 4 - len(cursor) % 4
        if padding != 4:
            cursor += "=" * padding

        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        data = json.loads(json_str)

        # Parser les datetime
        created_at = None
        if "created_at" in data:
            try:
                created_at = datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                pass

        return CursorParams(
            id=data.get("id"),
            created_at=created_at,
            sort_value=data.get("sort_value"),
            direction=data.get("_dir", "forward"),
        )

    except Exception as e:
        logger.warning(f"Curseur invalide: {e}")
        raise ValueError(f"Curseur invalide: {cursor}") from e


# ═══════════════════════════════════════════════════════════
# CONSTRUCTION DE RÉPONSE
# ═══════════════════════════════════════════════════════════


def construire_reponse_cursor(
    items: list[Any],
    limit: int,
    cursor_field: str = "id",
    secondary_field: str | None = "cree_le",
    serializer: type | None = None,
    direction: str = "forward",
) -> dict[str, Any]:
    """
    Construit une réponse paginée par curseur.

    IMPORTANT: La requête doit demander `limit + 1` éléments pour
    détecter s'il y a une page suivante.

    Args:
        items: Liste d'éléments (jusqu'à limit + 1)
        limit: Limite demandée
        cursor_field: Champ principal pour le curseur (généralement "id")
        secondary_field: Champ secondaire optionnel (pour tri multi-colonnes)
        serializer: Schéma Pydantic optionnel pour sérialiser les items
        direction: Direction de pagination ("forward" ou "backward")

    Returns:
        Dict compatible avec ReponseCursorPaginee
    """
    has_more = len(items) > limit
    result_items = items[:limit]

    # Pour backward, inverser l'ordre pour l'affichage naturel
    if direction == "backward":
        result_items = list(reversed(result_items))

    # Sérialiser si demandé
    if serializer and result_items:
        result_items = [serializer.model_validate(item).model_dump() for item in result_items]

    # Construire les curseurs
    next_cursor = None
    prev_cursor = None

    if result_items:
        # Curseur suivant (forward)
        if (direction == "forward" and has_more) or direction == "backward":
            last_item = result_items[-1]
            cursor_values = {cursor_field: _get_attr(last_item, cursor_field)}
            if secondary_field:
                secondary_value = _get_attr(last_item, secondary_field)
                if secondary_value is not None:
                    cursor_values[secondary_field] = secondary_value
            next_cursor = encoder_cursor(cursor_values, "forward")

        # Curseur précédent (backward)
        if direction == "forward":
            first_item = result_items[0]
            cursor_values = {cursor_field: _get_attr(first_item, cursor_field)}
            if secondary_field:
                secondary_value = _get_attr(first_item, secondary_field)
                if secondary_value is not None:
                    cursor_values[secondary_field] = secondary_value
            prev_cursor = encoder_cursor(cursor_values, "backward")
        elif direction == "backward" and has_more:
            first_item = result_items[0]
            cursor_values = {cursor_field: _get_attr(first_item, cursor_field)}
            if secondary_field:
                secondary_value = _get_attr(first_item, secondary_field)
                if secondary_value is not None:
                    cursor_values[secondary_field] = secondary_value
            prev_cursor = encoder_cursor(cursor_values, "backward")

    return {
        "items": result_items,
        "cursor": {
            "next_cursor": next_cursor,
            "prev_cursor": prev_cursor,
            "has_more": has_more if direction == "forward" else True,
        },
        "limit": limit,
    }


def _get_attr(obj: Any, name: str) -> Any:
    """Récupère un attribut d'un objet ou d'un dict."""
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


# ═══════════════════════════════════════════════════════════
# HELPERS SQLALCHEMY
# ═══════════════════════════════════════════════════════════


def appliquer_cursor_filter(
    query,
    cursor: CursorParams | None,
    model_class,
    cursor_field: str = "id",
    secondary_field: str | None = None,
):
    """
    Applique le filtre de curseur à une requête SQLAlchemy.

    Args:
        query: Requête SQLAlchemy de base
        cursor: Paramètres de curseur décodés (ou None)
        model_class: Classe du modèle SQLAlchemy
        cursor_field: Champ principal du curseur
        secondary_field: Champ secondaire optionnel

    Returns:
        Requête modifiée avec le filtre de curseur

    Example:
        cursor_params = decoder_cursor(cursor) if cursor else None
        query = session.query(Recette).order_by(Recette.id)
        query = appliquer_cursor_filter(query, cursor_params, Recette)
        items = query.limit(limit + 1).all()
    """
    if not cursor:
        return query

    primary_col = getattr(model_class, cursor_field)

    if cursor.direction == "forward":
        if cursor.id is not None:
            query = query.filter(primary_col > cursor.id)
        elif cursor.sort_value is not None:
            query = query.filter(primary_col > cursor.sort_value)
    else:  # backward
        if cursor.id is not None:
            query = query.filter(primary_col < cursor.id)
        elif cursor.sort_value is not None:
            query = query.filter(primary_col < cursor.sort_value)

    return query


# ═══════════════════════════════════════════════════════════
# VALIDATION ET HELPERS - BUG B12 FIX
# ═══════════════════════════════════════════════════════════


def valider_cursor_config(
    cursor_field: str,
    secondary_field: str | None,
    model_class: Any,
    route_name: str = "",
) -> None:
    """
    Valide et log un averissement si la configuration du curseur est potentiellement instable.

    IMPORTANT: Cette fonction aide à détecter les problèmes B12 (tri instable).
    - cursor_field doit être única (généralement "id" ou "cree_le")
    - secondary_field doit être différent et unique (généralement "id" si cursor_field != "id")

    Args:
        cursor_field: Le champ utilisé pour le curseur
        secondary_field: Le champ de départ (doit être unique)
        model_class: La classe du modèle SQLAlchemy
        route_name: Nom optionnel de la route pour le log

    Example:
        valider_cursor_config("date_prevue", "id", ActiviteFamille, "/api/v1/activites")
    """
    if not secondary_field or secondary_field == cursor_field:
        msg = (
            f"⚠️  POTENTIEL BUG B12 (tri instable) détecté"
            f"{f' sur {route_name}' if route_name else ''}:\n"
            f"   cursor_field='{cursor_field}', secondary_field='{secondary_field}'\n"
            f"   → Suppressions concurrentes peuvent sauter des enregistrements!\n"
            f"   → FIX: Passer secondary_field='id' (ou autre champ unique)"
        )
        logger.warning(msg)


def appliquer_cursor_filter_avec_tri_stable(
    query,
    cursor: CursorParams | None,
    model_class,
    cursor_field: str = "id",
    secondary_field: str | None = "id",
    log_warnings: bool = True,
) -> tuple:
    """
    Applique le filtre de curseur et valide que le tri est stable.

    Version améliorée de appliquer_cursor_filter qui:
    1. Valide la configuration du curseur (detecte B12)
    2. Log un averissement si le secondaire_field n'est pas passé
    3. Retourne (query_modifiee, validation_ok: bool)

    Args:
        query: Requête SQLAlchemy
        cursor: Paramètres du curseur (optionnel)
        model_class: Classe du modèle
        cursor_field: Champ principal du curseur
        secondary_field: Champ unique pour tri stable (généralement 'id')
        log_warnings: Si True, log les averissements B12

    Returns:
        Tuple (query_modifiee, validation_ok)

    Example:
        query = session.query(Activite).order_by(
            Activite.date_prevue.desc(),
            Activite.id.desc()  ← Important pour stabilité!
        )
        query, is_valid = appliquer_cursor_filter_avec_tri_stable(
            query,
            cursor_params,
            Activite,
            cursor_field="date_prevue",
            secondary_field="id"
        )
    """
    # Valider la configuration
    if log_warnings and (not secondary_field or secondary_field == cursor_field):
        valider_cursor_config(cursor_field, secondary_field, model_class)
        return appliquer_cursor_filter(
            query, cursor, model_class, cursor_field, secondary_field
        ), False

    # Appliquer le filtre normal
    query = appliquer_cursor_filter(query, cursor, model_class, cursor_field, secondary_field)
    return query, True
