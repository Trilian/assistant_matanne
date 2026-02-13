"""
Package web - Services web unifiés (synchronisation temps réel + PWA).

Ce package fournit:

## Synchronisation temps réel (anciennement sync/)
- RealtimeSyncService: Synchronisation temps réel des listes de courses
- Types: SyncEventType, SyncEvent, PresenceInfo, SyncState
- Composants UI: render_presence_indicator, render_typing_indicator, render_sync_status

## PWA - Progressive Web App (anciennement pwa/)
- Configuration PWA (manifest.json, service worker, icônes)
- Injection des meta tags PWA
- Détection d'installation PWA

Utilisation:
    # Synchronisation
    from src.services.web import get_realtime_sync_service, RealtimeSyncService

    service = get_realtime_sync_service()
    service.broadcast_change(event)

    # PWA
    from src.services.web import generate_pwa_files, inject_pwa_meta

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
    # Injection et rendu
    inject_pwa_meta,
    # Utilitaires
    is_pwa_installed,
    render_install_prompt,
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
    # Composants UI
    render_presence_indicator,
    render_sync_status,
    render_typing_indicator,
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
    # UI
    "render_presence_indicator",
    "render_typing_indicator",
    "render_sync_status",
    # === PWA ===
    # Configuration
    "PWA_CONFIG",
    # Génération
    "generate_manifest",
    "generate_service_worker",
    "generate_offline_page",
    "generate_pwa_files",
    "generate_icon_svg",
    # Injection
    "inject_pwa_meta",
    "render_install_prompt",
    # Utilitaires
    "is_pwa_installed",
]
