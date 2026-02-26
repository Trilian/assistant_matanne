"""
Service Album Souvenirs - Albums photos et mémoires familiales.

Opérations:
- CRUD albums et souvenirs
- Liaison avec les jalons (premières fois)
- Timeline de souvenirs
"""

import logging
from datetime import date as date_type
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import AlbumFamille, SouvenirFamille
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServiceAlbum(BaseService[AlbumFamille]):
    """Service de gestion des albums et souvenirs famille.

    Hérite de BaseService[AlbumFamille] pour le CRUD générique sur les albums.
    """

    def __init__(self):
        super().__init__(model=AlbumFamille, cache_ttl=600)

    # ═══════════════════════════════════════════════════════════
    # ALBUMS
    # ═══════════════════════════════════════════════════════════

    @chronometre("album.liste", seuil_alerte_ms=1000)
    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_albums(self, *, db: Session | None = None) -> list[AlbumFamille]:
        """Récupère tous les albums."""
        if db is None:
            return []
        return db.query(AlbumFamille).order_by(AlbumFamille.cree_le.desc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_album(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> AlbumFamille | None:
        """Crée un nouvel album."""
        if db is None:
            return None
        album = AlbumFamille(**data)
        db.add(album)
        db.commit()
        db.refresh(album)
        logger.info("Album créé: %s", album.titre)
        obtenir_bus().emettre(
            "album.cree",
            {"album_id": album.id, "titre": album.titre},
            source="ServiceAlbum",
        )
        return album

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_album(
        self, album_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un album existant."""
        if db is None:
            return False
        album = db.query(AlbumFamille).get(album_id)
        if not album:
            return False
        for key, value in data.items():
            if hasattr(album, key):
                setattr(album, key, value)
        db.commit()
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_album(self, album_id: int, *, db: Session | None = None) -> bool:
        """Supprime un album."""
        if db is None:
            return False
        deleted = db.query(AlbumFamille).filter_by(id=album_id).delete()
        db.commit()
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # SOUVENIRS
    # ═══════════════════════════════════════════════════════════

    @chronometre("album.souvenirs", seuil_alerte_ms=1000)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_souvenirs(
        self,
        *,
        album_id: int | None = None,
        jalon_id: int | None = None,
        db: Session | None = None,
    ) -> list[SouvenirFamille]:
        """Récupère les souvenirs, filtrés optionnellement."""
        if db is None:
            return []
        query = db.query(SouvenirFamille)
        if album_id is not None:
            query = query.filter_by(album_id=album_id)
        if jalon_id is not None:
            query = query.filter_by(jalon_id=jalon_id)
        return query.order_by(SouvenirFamille.date_souvenir.desc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_souvenir(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> SouvenirFamille | None:
        """Ajoute un souvenir."""
        if db is None:
            return None
        souvenir = SouvenirFamille(**data)
        db.add(souvenir)
        db.commit()
        db.refresh(souvenir)
        logger.info("Souvenir ajouté: %s", souvenir.titre)
        obtenir_bus().emettre(
            "album.souvenir_ajoute",
            {"souvenir_id": souvenir.id, "titre": souvenir.titre},
            source="ServiceAlbum",
        )
        return souvenir

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_souvenir(self, souvenir_id: int, *, db: Session | None = None) -> bool:
        """Supprime un souvenir."""
        if db is None:
            return False
        deleted = db.query(SouvenirFamille).filter_by(id=souvenir_id).delete()
        db.commit()
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # TIMELINE
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_timeline(
        self, *, limite: int = 50, db: Session | None = None
    ) -> list[SouvenirFamille]:
        """Récupère les derniers souvenirs pour la timeline."""
        if db is None:
            return []
        return (
            db.query(SouvenirFamille)
            .order_by(SouvenirFamille.date_souvenir.desc())
            .limit(limite)
            .all()
        )

    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=600)
    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def obtenir_stats(self, *, db: Session | None = None) -> dict[str, Any]:
        """Statistiques sur les albums et souvenirs."""
        if db is None:
            return {}
        nb_albums = db.query(func.count(AlbumFamille.id)).scalar() or 0
        nb_souvenirs = db.query(func.count(SouvenirFamille.id)).scalar() or 0
        return {
            "nb_albums": nb_albums,
            "nb_souvenirs": nb_souvenirs,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("album_famille", tags={"famille", "album"})
def obtenir_service_album() -> ServiceAlbum:
    """Factory pour le service album (singleton via ServiceRegistry)."""
    return ServiceAlbum()


# Alias anglais
get_album_service = obtenir_service_album
