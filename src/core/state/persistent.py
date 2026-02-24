"""
PersistentState - Synchronisation session_state ↔ DB automatique.

Résout le problème critique des données perdues en session_state
en synchronisant automatiquement vers la base de données.

Usage:
    from src.core.state.persistent import PersistentState, persistent_state

    # Décorateur pour synchronisation automatique
    @persistent_state(model=PreferenceUtilisateur, key="foyer_config", sync_interval=30)
    def obtenir_config_foyer():
        return {"nb_adultes": 2, "jules_present": True}

    # Classe pour gestion manuelle
    pstate = PersistentState("preferences_utilisateurs", user_id="anne")
    pstate.set("theme", "dark")
    pstate.commit()  # Sauvegarde en DB

Architecture:
- Lecture: session_state (cache rapide) → DB (fallback)
- Écriture: session_state (immédiat) → DB (commit batch)
- Sync: Background ou explicite
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

from src.core.storage import obtenir_storage

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class PersistentStateConfig:
    """Configuration pour un état persistant."""

    key: str
    user_id: str = "default"
    sync_interval: int = 30  # Secondes
    auto_commit: bool = True
    model_name: str | None = None  # Nom du modèle SQLAlchemy


@dataclass
class _SyncStatus:
    """État de synchronisation interne."""

    last_sync: datetime | None = None
    dirty: bool = False
    pending_changes: dict[str, Any] = field(default_factory=dict)
    sync_count: int = 0
    error_count: int = 0


# ═══════════════════════════════════════════════════════════
# PERSISTENT STATE
# ═══════════════════════════════════════════════════════════


class PersistentState:
    """
    Gestionnaire d'état persistant avec sync session_state ↔ DB.

    Fonctionne comme un dict amélioré qui:
    - Lit d'abord depuis session_state (cache)
    - Fallback vers la DB si pas en cache
    - Écrit simultanément en session_state et marque dirty
    - Commit vers DB selon l'intervalle ou explicitement
    """

    _PREFIX = "pstate_"
    _instances: dict[str, PersistentState] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        namespace: str,
        *,
        user_id: str = "default",
        sync_interval: int = 30,
        auto_commit: bool = True,
    ):
        """
        Initialise un état persistant.

        Args:
            namespace: Nom unique de l'espace de stockage (ex: "foyer_config")
            user_id: Identifiant utilisateur
            sync_interval: Intervalle de sync auto (secondes). 0 = désactivé.
            auto_commit: Commit automatique après chaque set()
        """
        self.namespace = namespace
        self.user_id = user_id
        self.sync_interval = sync_interval
        self.auto_commit = auto_commit
        self._status = _SyncStatus()
        self._storage = obtenir_storage()
        self._storage_key = f"{self._PREFIX}{namespace}_{user_id}"

        # Charger depuis DB au premier accès si pas en session
        self._ensure_loaded()

    @classmethod
    def get_instance(
        cls,
        namespace: str,
        **kwargs: Any,
    ) -> PersistentState:
        """Obtient ou crée une instance singleton par namespace."""
        key = f"{namespace}_{kwargs.get('user_id', 'default')}"

        with cls._lock:
            if key not in cls._instances:
                cls._instances[key] = cls(namespace, **kwargs)
            return cls._instances[key]

    # ── Lecture ──

    def _ensure_loaded(self) -> None:
        """Charge depuis DB si pas encore en session_state."""
        if self._storage.contains(self._storage_key):
            return  # Déjà chargé

        # Charger depuis DB
        try:
            data = self._load_from_db()
            if data:
                self._storage.set(self._storage_key, data)
                logger.debug(f"✅ PersistentState '{self.namespace}' chargé depuis DB")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger '{self.namespace}' depuis DB: {e}")
            # Initialiser avec dict vide
            self._storage.set(self._storage_key, {})

    def _load_from_db(self) -> dict[str, Any] | None:
        """Charge l'état depuis la base de données."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtatPersistantDB

            with obtenir_contexte_db() as db:
                entry = (
                    db.query(EtatPersistantDB)
                    .filter_by(namespace=self.namespace, user_id=self.user_id)
                    .first()
                )
                if entry:
                    return entry.data or {}
        except ImportError:
            # Modèle pas encore créé — fallback silencieux
            logger.debug("EtatPersistantDB non disponible")
        except Exception as e:
            logger.warning(f"Erreur lecture DB: {e}")

        return None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur.

        Ordre de lecture:
        1. session_state (cache rapide)
        2. DB (si pas en cache)
        """
        self._ensure_loaded()
        data = self._storage.get(self._storage_key, {})
        return data.get(key, default)

    def get_all(self) -> dict[str, Any]:
        """Récupère tout l'état."""
        self._ensure_loaded()
        return dict(self._storage.get(self._storage_key, {}))

    # ── Écriture ──

    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur.

        Écrit immédiatement en session_state et marque dirty
        pour la prochaine sync DB.
        """
        self._ensure_loaded()
        data = self._storage.get(self._storage_key, {})
        data[key] = value
        self._storage.set(self._storage_key, data)

        # Marquer dirty
        self._status.dirty = True
        self._status.pending_changes[key] = value

        logger.debug(f"PersistentState '{self.namespace}': {key} = {value}")

        # Auto-commit si activé
        if self.auto_commit:
            self._maybe_sync()

    def update(self, updates: dict[str, Any]) -> None:
        """Met à jour plusieurs valeurs d'un coup."""
        for key, value in updates.items():
            self.set(key, value)

    def delete(self, key: str) -> None:
        """Supprime une clé."""
        self._ensure_loaded()
        data = self._storage.get(self._storage_key, {})
        if key in data:
            del data[key]
            self._storage.set(self._storage_key, data)
            self._status.dirty = True

    def clear(self) -> None:
        """Efface tout l'état."""
        self._storage.set(self._storage_key, {})
        self._status.dirty = True

    # ── Synchronisation ──

    def _maybe_sync(self) -> None:
        """Synchronise si l'intervalle est dépassé."""
        if not self._status.dirty:
            return

        if self.sync_interval <= 0:
            return  # Sync désactivé

        now = datetime.now()
        if self._status.last_sync:
            elapsed = (now - self._status.last_sync).total_seconds()
            if elapsed < self.sync_interval:
                return  # Pas encore le moment

        self.commit()

    def commit(self) -> bool:
        """
        Force la sauvegarde en base de données.

        Returns:
            True si succès, False si échec
        """
        if not self._status.dirty:
            return True  # Rien à faire

        try:
            data = self.get_all()
            success = self._save_to_db(data)

            if success:
                self._status.dirty = False
                self._status.pending_changes.clear()
                self._status.last_sync = datetime.now()
                self._status.sync_count += 1
                logger.info(f"✅ PersistentState '{self.namespace}' sauvegardé en DB")
                return True
            else:
                self._status.error_count += 1
                return False

        except Exception as e:
            logger.error(f"❌ Erreur commit '{self.namespace}': {e}")
            self._status.error_count += 1
            return False

    def _save_to_db(self, data: dict[str, Any]) -> bool:
        """Sauvegarde l'état en base de données."""
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import EtatPersistantDB

            with obtenir_contexte_db() as db:
                entry = (
                    db.query(EtatPersistantDB)
                    .filter_by(namespace=self.namespace, user_id=self.user_id)
                    .first()
                )

                if entry:
                    entry.data = data
                    entry.updated_at = datetime.now()
                else:
                    entry = EtatPersistantDB(
                        namespace=self.namespace,
                        user_id=self.user_id,
                        data=data,
                    )
                    db.add(entry)

                db.commit()
                return True

        except ImportError:
            logger.debug("EtatPersistantDB non disponible — sauvegarde différée")
            return True  # Pas d'erreur, juste pas de DB
        except Exception as e:
            logger.error(f"Erreur sauvegarde DB: {e}")
            return False

    def flush(self) -> None:
        """Alias pour commit() — force la sauvegarde immédiate."""
        self.commit()

    # ── Utilitaires ──

    def is_dirty(self) -> bool:
        """Vérifie si des changements sont en attente."""
        return self._status.dirty

    def get_sync_status(self) -> dict[str, Any]:
        """Retourne le statut de synchronisation."""
        return {
            "namespace": self.namespace,
            "user_id": self.user_id,
            "dirty": self._status.dirty,
            "last_sync": self._status.last_sync,
            "sync_count": self._status.sync_count,
            "error_count": self._status.error_count,
            "pending_changes": len(self._status.pending_changes),
        }

    def __contains__(self, key: str) -> bool:
        """Support pour 'key in pstate'."""
        return key in self.get_all()

    def __getitem__(self, key: str) -> Any:
        """Support pour pstate[key]."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Support pour pstate[key] = value."""
        self.set(key, value)

    def __repr__(self) -> str:
        return f"<PersistentState('{self.namespace}', user='{self.user_id}', dirty={self._status.dirty})>"


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR
# ═══════════════════════════════════════════════════════════


def persistent_state(
    key: str,
    *,
    user_id: str = "default",
    sync_interval: int = 30,
    auto_commit: bool = True,
):
    """
    Décorateur pour rendre une fonction factory persistante.

    La fonction décorée sera appelée une seule fois pour obtenir
    la valeur par défaut. Les modifications seront persistées
    automatiquement en DB.

    Args:
        key: Clé de stockage unique
        user_id: Identifiant utilisateur
        sync_interval: Intervalle de sync (secondes)
        auto_commit: Commit auto après chaque modification

    Usage:
        @persistent_state(key="foyer_config", sync_interval=30)
        def obtenir_config_foyer():
            return {"nb_adultes": 2, "jules_present": True}

        config = obtenir_config_foyer()  # Dict persistant
        config["nb_adultes"] = 3  # Auto-sauvegardé
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pstate = PersistentState.get_instance(
                key,
                user_id=user_id,
                sync_interval=sync_interval,
                auto_commit=auto_commit,
            )

            # Si vide, initialiser avec la factory
            if not pstate.get_all():
                default = func(*args, **kwargs)
                if isinstance(default, dict):
                    pstate.update(default)

            return pstate

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def obtenir_etat_persistant(
    namespace: str,
    user_id: str = "default",
) -> PersistentState:
    """
    Helper pour obtenir un état persistant.

    Args:
        namespace: Nom de l'espace (ex: "foyer_config", "preferences_ui")
        user_id: Identifiant utilisateur

    Returns:
        Instance PersistentState
    """
    return PersistentState.get_instance(namespace, user_id=user_id)


def forcer_sync_tous() -> dict[str, bool]:
    """Force la synchronisation de tous les états persistants."""
    results = {}
    for key, pstate in PersistentState._instances.items():
        results[key] = pstate.commit()
    return results


__all__ = [
    "PersistentState",
    "PersistentStateConfig",
    "persistent_state",
    "obtenir_etat_persistant",
    "forcer_sync_tous",
]
