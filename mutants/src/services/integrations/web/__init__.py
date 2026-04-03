"""
Package web - Services web unifiés (synchronisation temps réel + PWA).

Ce package fournit:

## Synchronisation temps réel (anciennement sync/)
- RealtimeSyncService: Synchronisation temps réel des listes de courses
- Types: SyncEventType, SyncEvent, PresenceInfo, SyncState
- Composants UI: afficher_indicateur_presence, afficher_indicateur_frappe, afficher_statut_synchronisation

## PWA - Progressive Web App (anciennement pwa/)
- Configuration PWA (manifest.json, service worker, icônes)
- Injection des meta tags PWA
- Détection d'installation PWA

Utilisation:
    # Synchronisation
    from src.services.integrations.web import get_realtime_sync_service, RealtimeSyncService

    service = get_realtime_sync_service()
    service.broadcast_change(event)

    # PWA
    from src.services.integrations.web import generate_pwa_files, inject_pwa_meta

    generate_pwa_files("static/")
    inject_pwa_meta()
"""

# ═══════════════════════════════════════════════════════════
# SYNCHRONISATION TEMPS RÉEL
# ═══════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════
# PWA - PROGRESSIVE WEB APP
# ═══════════════════════════════════════════════════════════
from .pwa import (
    # Configuration
    PWA_CONFIG,
    generate_icon_svg,
    # Génération de fichiers
    generate_manifest,
    generate_offline_page,
    generate_pwa_files,
    generate_service_worker,
    # Utilitaires
    is_pwa_installed,
)
from .synchronisation import (
    PresenceInfo,
    # Service principal
    RealtimeSyncService,
    SyncEvent,
    # Types et énumérations
    SyncEventType,
    SyncState,
    get_realtime_sync_service,
    obtenir_service_synchronisation_temps_reel,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # === Synchronisation ===
    # Types
    "SyncEventType",
    "SyncEvent",
    "PresenceInfo",
    "SyncState",
    # Service
    "RealtimeSyncService",
    "get_realtime_sync_service",
    "obtenir_service_synchronisation_temps_reel",
    # === PWA ===
    # Configuration
    "PWA_CONFIG",
    # Génération
    "generate_manifest",
    "generate_service_worker",
    "generate_offline_page",
    "generate_pwa_files",
    "generate_icon_svg",
    # Utilitaires
    "is_pwa_installed",
]
