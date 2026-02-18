"""
Service de synchronisation temps réel pour les listes de courses.

Utilise Supabase Realtime pour synchroniser les modifications
entre plusieurs utilisateurs connectés simultanément.

Fonctionnalités:
- Broadcast des modifications de listes
- Présence utilisateurs connectés
- Résolution de conflits
- Indicateurs de frappe en cours
"""

import logging
from collections.abc import Callable, MutableMapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

import streamlit as st
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class SyncEventType(StrEnum):
    """Types d'événements de synchronisation."""

    ITEM_ADDED = "item_added"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    ITEM_CHECKED = "item_checked"
    ITEM_UNCHECKED = "item_unchecked"
    LIST_CLEARED = "list_cleared"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USER_TYPING = "user_typing"


class SyncEvent(BaseModel):
    """Événement de synchronisation."""

    event_type: SyncEventType
    liste_id: int
    user_id: str
    user_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    data: dict = Field(default_factory=dict)


class PresenceInfo(BaseModel):
    """Information de présence d'un utilisateur."""

    user_id: str
    user_name: str
    avatar_url: str | None = None
    joined_at: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    is_typing: bool = False
    current_item: str | None = None


@dataclass
class SyncState:
    """État de synchronisation local."""

    liste_id: int | None = None
    connected: bool = False
    users_present: dict[str, PresenceInfo] = field(default_factory=dict)
    pending_events: list[SyncEvent] = field(default_factory=list)
    last_sync: datetime | None = None
    conflict_count: int = 0


# ═══════════════════════════════════════════════════════════
# SERVICE DE SYNCHRONISATION
# ═══════════════════════════════════════════════════════════


class RealtimeSyncService:
    """
    Service de synchronisation temps réel pour les listes de courses.

    Utilise Supabase Realtime pour:
    - Broadcast des modifications
    - Tracking de la présence
    - Résolution des conflits optimiste
    """

    CHANNEL_PREFIX = "shopping_list_"
    STATE_KEY = "_realtime_sync_state"

    def __init__(
        self,
        storage: MutableMapping[str, Any] | None = None,
        on_rerun: Callable[[], None] | None = None,
    ):
        """Initialise le service de synchronisation.

        Args:
            storage: Stockage clé-valeur mutable (défaut: st.session_state).
            on_rerun: Callback pour déclencher un rerun (défaut: st.rerun).
        """
        self._storage = storage if storage is not None else self._get_default_storage()
        self._on_rerun = on_rerun if on_rerun is not None else self._get_default_rerun()
        self._client = None
        self._channel = None
        self._callbacks: dict[SyncEventType, list[Callable]] = {}
        self._init_client()

    @staticmethod
    def _get_default_storage() -> MutableMapping[str, Any]:
        """Retourne le stockage par défaut (st.session_state)."""
        return st.session_state

    @staticmethod
    def _get_default_rerun() -> Callable[[], None]:
        """Retourne le callback rerun par défaut (st.rerun)."""
        return st.rerun

    def _init_client(self):
        """Initialise le client Supabase Realtime."""
        try:
            from supabase import create_client

            from src.core.config import obtenir_parametres

            params = obtenir_parametres()
            supabase_url = getattr(params, "SUPABASE_URL", None)
            supabase_key = getattr(params, "SUPABASE_ANON_KEY", None)

            if supabase_url and supabase_key:
                self._client = create_client(supabase_url, supabase_key)
                logger.info("✅ Client Supabase Realtime initialisé")
            else:
                logger.warning("Variables Supabase non configurées")

        except ImportError:
            logger.warning("Package supabase non installé")
        except Exception as e:
            logger.error(f"Erreur initialisation Realtime: {e}")

    @property
    def is_configured(self) -> bool:
        """Vérifie si le service est configuré."""
        return self._client is not None

    @property
    def state(self) -> SyncState:
        """Retourne l'état de synchronisation."""
        if self.STATE_KEY not in self._storage:
            self._storage[self.STATE_KEY] = SyncState()
        return self._storage[self.STATE_KEY]

    # ═══════════════════════════════════════════════════════════
    # CONNEXION AU CHANNEL
    # ═══════════════════════════════════════════════════════════

    def join_list(self, liste_id: int, user_id: str, user_name: str) -> bool:
        """
        Rejoint un channel de liste de courses.

        Args:
            liste_id: ID de la liste
            user_id: ID de l'utilisateur
            user_name: Nom affiché de l'utilisateur

        Returns:
            True si connecté avec succès
        """
        if not self.is_configured:
            logger.warning("Service non configuré, mode local uniquement")
            return False

        try:
            channel_name = f"{self.CHANNEL_PREFIX}{liste_id}"

            # Créer le channel avec présence
            self._channel = self._client.channel(
                channel_name,
                {
                    "config": {
                        "presence": {"key": user_id},
                        "broadcast": {"self": True},
                    }
                },
            )

            # Configurer les handlers
            self._channel.on_broadcast("sync_event", self._handle_broadcast)

            self._channel.on_presence_sync(self._handle_presence_sync)
            self._channel.on_presence_join(self._handle_presence_join)
            self._channel.on_presence_leave(self._handle_presence_leave)

            # Souscrire
            self._channel.subscribe()

            # Tracker la présence
            self._channel.track(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "online_at": datetime.now().isoformat(),
                }
            )

            # Mettre à jour l'état
            self.state.liste_id = liste_id
            self.state.connected = True
            self.state.last_sync = datetime.now()

            logger.info(f"✅ Connecté au channel {channel_name}")

            # Notifier les autres
            self.broadcast_event(
                SyncEvent(
                    event_type=SyncEventType.USER_JOINED,
                    liste_id=liste_id,
                    user_id=user_id,
                    user_name=user_name,
                )
            )

            return True

        except Exception as e:
            logger.error(f"Erreur connexion channel: {e}")
            return False

    def leave_list(self):
        """Quitte le channel actuel."""
        if self._channel:
            try:
                user_id = self._get_current_user_id()

                # Notifier les autres
                if self.state.liste_id:
                    self.broadcast_event(
                        SyncEvent(
                            event_type=SyncEventType.USER_LEFT,
                            liste_id=self.state.liste_id,
                            user_id=user_id,
                            user_name=self._get_current_user_name(),
                        )
                    )

                self._channel.unsubscribe()
                self._channel = None

                self.state.connected = False
                self.state.liste_id = None
                self.state.users_present.clear()

                logger.info("Déconnecté du channel")

            except Exception as e:
                logger.error(f"Erreur déconnexion: {e}")

    # ═══════════════════════════════════════════════════════════
    # BROADCAST D'ÉVÉNEMENTS
    # ═══════════════════════════════════════════════════════════

    def broadcast_event(self, event: SyncEvent):
        """
        Diffuse un événement à tous les utilisateurs connectés.

        Args:
            event: Événement à diffuser
        """
        if not self._channel:
            # Mode hors ligne - stocker pour sync ultérieur
            self.state.pending_events.append(event)
            logger.debug(f"Événement stocké localement: {event.event_type}")
            return

        try:
            self._channel.send_broadcast("sync_event", event.model_dump(mode="json"))
            logger.debug(f"Événement diffusé: {event.event_type}")

        except Exception as e:
            logger.error(f"Erreur broadcast: {e}")
            self.state.pending_events.append(event)

    def broadcast_item_added(self, liste_id: int, item_data: dict):
        """Diffuse l'ajout d'un article."""
        self.broadcast_event(
            SyncEvent(
                event_type=SyncEventType.ITEM_ADDED,
                liste_id=liste_id,
                user_id=self._get_current_user_id(),
                user_name=self._get_current_user_name(),
                data=item_data,
            )
        )

    def broadcast_item_checked(self, liste_id: int, item_id: int, checked: bool):
        """Diffuse le cochage/décochage d'un article."""
        event_type = SyncEventType.ITEM_CHECKED if checked else SyncEventType.ITEM_UNCHECKED
        self.broadcast_event(
            SyncEvent(
                event_type=event_type,
                liste_id=liste_id,
                user_id=self._get_current_user_id(),
                user_name=self._get_current_user_name(),
                data={"item_id": item_id, "checked": checked},
            )
        )

    def broadcast_item_deleted(self, liste_id: int, item_id: int):
        """Diffuse la suppression d'un article."""
        self.broadcast_event(
            SyncEvent(
                event_type=SyncEventType.ITEM_DELETED,
                liste_id=liste_id,
                user_id=self._get_current_user_id(),
                user_name=self._get_current_user_name(),
                data={"item_id": item_id},
            )
        )

    def broadcast_typing(self, liste_id: int, is_typing: bool, item_name: str = ""):
        """Diffuse l'indicateur de frappe."""
        self.broadcast_event(
            SyncEvent(
                event_type=SyncEventType.USER_TYPING,
                liste_id=liste_id,
                user_id=self._get_current_user_id(),
                user_name=self._get_current_user_name(),
                data={"is_typing": is_typing, "item_name": item_name},
            )
        )

    # ═══════════════════════════════════════════════════════════
    # HANDLERS D'ÉVÉNEMENTS
    # ═══════════════════════════════════════════════════════════

    def _handle_broadcast(self, payload: dict):
        """Gère les événements broadcast reçus."""
        try:
            event = SyncEvent(**payload)

            # Ignorer nos propres événements
            if event.user_id == self._get_current_user_id():
                return

            logger.debug(f"Événement reçu: {event.event_type} de {event.user_name}")

            # Appeler les callbacks enregistrés
            for callback in self._callbacks.get(event.event_type, []):
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Erreur callback: {e}")

            # Déclencher un rerun Streamlit
            self._on_rerun()

        except Exception as e:
            logger.error(f"Erreur traitement broadcast: {e}")

    def _handle_presence_sync(self, payload: dict):
        """Synchronise l'état de présence."""
        try:
            presences = payload.get("presences", {})

            self.state.users_present.clear()
            for user_id, data in presences.items():
                if data:
                    info = data[0] if isinstance(data, list) else data
                    self.state.users_present[user_id] = PresenceInfo(
                        user_id=user_id,
                        user_name=info.get("user_name", "Anonyme"),
                    )

            logger.debug(f"Présence sync: {len(self.state.users_present)} utilisateurs")

        except Exception as e:
            logger.error(f"Erreur sync présence: {e}")

    def _handle_presence_join(self, payload: dict):
        """Gère l'arrivée d'un utilisateur."""
        try:
            key = payload.get("key")
            new_presences = payload.get("newPresences", [])

            for presence in new_presences:
                user_id = presence.get("user_id", key)
                self.state.users_present[user_id] = PresenceInfo(
                    user_id=user_id,
                    user_name=presence.get("user_name", "Anonyme"),
                )

            logger.info(f"Utilisateur rejoint: {key}")

        except Exception as e:
            logger.error(f"Erreur presence join: {e}")

    def _handle_presence_leave(self, payload: dict):
        """Gère le départ d'un utilisateur."""
        try:
            key = payload.get("key")

            if key in self.state.users_present:
                del self.state.users_present[key]

            logger.info(f"Utilisateur parti: {key}")

        except Exception as e:
            logger.error(f"Erreur presence leave: {e}")

    # ═══════════════════════════════════════════════════════════
    # ENREGISTREMENT DE CALLBACKS
    # ═══════════════════════════════════════════════════════════

    def on_event(self, event_type: SyncEventType, callback: Callable[[SyncEvent], None]):
        """
        Enregistre un callback pour un type d'événement.

        Args:
            event_type: Type d'événement à écouter
            callback: Fonction à appeler
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    def on_item_added(self, callback: Callable[[SyncEvent], None]):
        """Enregistre un callback pour l'ajout d'articles."""
        self.on_event(SyncEventType.ITEM_ADDED, callback)

    def on_item_checked(self, callback: Callable[[SyncEvent], None]):
        """Enregistre un callback pour le cochage d'articles."""
        self.on_event(SyncEventType.ITEM_CHECKED, callback)
        self.on_event(SyncEventType.ITEM_UNCHECKED, callback)

    # ═══════════════════════════════════════════════════════════
    # RÉSOLUTION DE CONFLITS
    # ═══════════════════════════════════════════════════════════

    def resolve_conflict(self, local_version: dict, remote_version: dict) -> dict:
        """
        Résout un conflit entre versions locale et distante.

        Stratégie: Last-Write-Wins avec merge des champs non conflictuels.

        Args:
            local_version: Version locale de l'article
            remote_version: Version distante de l'article

        Returns:
            Version fusionnée
        """
        local_ts = local_version.get("updated_at", "")
        remote_ts = remote_version.get("updated_at", "")

        # Last-Write-Wins pour les champs en conflit
        if remote_ts > local_ts:
            winner = remote_version.copy()
            loser = local_version
        else:
            winner = local_version.copy()
            loser = remote_version

        # Merge les champs non conflictuels
        for key in loser:
            if key not in winner or winner[key] is None:
                winner[key] = loser[key]

        self.state.conflict_count += 1
        logger.info(f"Conflit résolu (total: {self.state.conflict_count})")

        return winner

    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════

    def _get_current_user_id(self) -> str:
        """Retourne l'ID de l'utilisateur courant."""
        from src.services.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.get_current_user()
        return user.id if user else "anonymous"

    def _get_current_user_name(self) -> str:
        """Retourne le nom de l'utilisateur courant."""
        from src.services.utilisateur import get_auth_service

        auth = get_auth_service()
        user = auth.get_current_user()
        return user.display_name if user else "Anonyme"

    def get_connected_users(self) -> list[PresenceInfo]:
        """Retourne la liste des utilisateurs connectés."""
        return list(self.state.users_present.values())

    def sync_pending_events(self):
        """Synchronise les événements en attente."""
        if not self._channel or not self.state.pending_events:
            return

        events = self.state.pending_events.copy()
        self.state.pending_events.clear()

        for event in events:
            self.broadcast_event(event)

        logger.info(f"Synchronisé {len(events)} événements en attente")


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI (rétrocompatibilité — implémentation dans src.ui.views.synchronisation)
# ═══════════════════════════════════════════════════════════


def render_presence_indicator():
    """Rétrocompatibilité — délègue à src.ui.views.synchronisation."""
    from src.ui.views.synchronisation import afficher_indicateur_presence

    return afficher_indicateur_presence()


def render_typing_indicator():
    """Rétrocompatibilité — délègue à src.ui.views.synchronisation."""
    from src.ui.views.synchronisation import afficher_indicateur_frappe

    return afficher_indicateur_frappe()


def render_sync_status():
    """Rétrocompatibilité — délègue à src.ui.views.synchronisation."""
    from src.ui.views.synchronisation import afficher_statut_synchronisation

    return afficher_statut_synchronisation()


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_sync_service: RealtimeSyncService | None = None


def obtenir_service_synchronisation_temps_reel() -> RealtimeSyncService:
    """Factory pour le service de synchronisation (convention française)."""
    global _sync_service
    if _sync_service is None:
        _sync_service = RealtimeSyncService()
    return _sync_service


def get_realtime_sync_service() -> RealtimeSyncService:
    """Factory pour le service de synchronisation (alias anglais)."""
    return obtenir_service_synchronisation_temps_reel()


__all__ = [
    "RealtimeSyncService",
    "obtenir_service_synchronisation_temps_reel",
    "get_realtime_sync_service",
    "SyncEvent",
    "SyncEventType",
    "PresenceInfo",
    "render_presence_indicator",
    "render_typing_indicator",
    "render_sync_status",
]
