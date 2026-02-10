"""
Mode Offline - Gestion de la connectivité et synchronisation.

Fonctionnalités :
- Détection de la connectivité DB
- Queue d'opérations en attente (offline)
- Synchronisation automatique au retour en ligne
- Cache local pour lecture offline
- Indicateur de statut de connexion
"""

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET CONFIGURATION
# ═══════════════════════════════════════════════════════════


class ConnectionStatus(str, Enum):
    """Statut de connexion."""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"


class OperationType(str, Enum):
    """Type d'opération en queue."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


@dataclass
class PendingOperation:
    """Opération en attente de synchronisation."""
    
    id: str = field(default_factory=lambda: str(uuid4())[:12])
    operation_type: OperationType = OperationType.CREATE
    model_name: str = ""
    data: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    last_error: str | None = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operation_type": self.operation_type.value,
            "model_name": self.model_name,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "retry_count": self.retry_count,
            "last_error": self.last_error,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PendingOperation":
        return cls(
            id=data.get("id", str(uuid4())[:12]),
            operation_type=OperationType(data.get("operation_type", "create")),
            model_name=data.get("model_name", ""),
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            retry_count=data.get("retry_count", 0),
            last_error=data.get("last_error"),
        )


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE DE CONNEXION
# ═══════════════════════════════════════════════════════════


class ConnectionManager:
    """
    Gestionnaire de l'état de connexion à la base de données.
    
    Vérifie périodiquement la connexion et met à jour le statut.
    """
    
    SESSION_KEY = "_connection_status"
    LAST_CHECK_KEY = "_connection_last_check"
    CHECK_INTERVAL = 30  # secondes
    
    @classmethod
    def get_status(cls) -> ConnectionStatus:
        """Retourne le statut de connexion actuel."""
        return st.session_state.get(cls.SESSION_KEY, ConnectionStatus.ONLINE)
    
    @classmethod
    def set_status(cls, status: ConnectionStatus) -> None:
        """Met à jour le statut."""
        st.session_state[cls.SESSION_KEY] = status
    
    @classmethod
    def is_online(cls) -> bool:
        """Vérifie si on est en ligne."""
        return cls.get_status() == ConnectionStatus.ONLINE
    
    @classmethod
    def check_connection(cls, force: bool = False) -> bool:
        """
        Vérifie la connexion à la base de données.
        
        Args:
            force: Forcer la vérification même si récente
            
        Returns:
            True si connecté
        """
        # Vérifier si check récent
        last_check = st.session_state.get(cls.LAST_CHECK_KEY)
        now = time.time()
        
        if not force and last_check:
            if now - last_check < cls.CHECK_INTERVAL:
                return cls.is_online()
        
        # Effectuer la vérification
        cls.set_status(ConnectionStatus.CONNECTING)
        
        try:
            from src.core.database import verifier_connexion
            
            if verifier_connexion():
                cls.set_status(ConnectionStatus.ONLINE)
                st.session_state[cls.LAST_CHECK_KEY] = now
                logger.debug("Connexion DB OK")
                return True
            else:
                cls.set_status(ConnectionStatus.OFFLINE)
                logger.warning("Connexion DB échouée")
                return False
                
        except Exception as e:
            cls.set_status(ConnectionStatus.ERROR)
            logger.error(f"Erreur vérification connexion: {e}")
            return False
    
    @classmethod
    def handle_connection_error(cls, error: Exception) -> None:
        """Gère une erreur de connexion."""
        cls.set_status(ConnectionStatus.OFFLINE)
        logger.error(f"Erreur de connexion: {error}")


# ═══════════════════════════════════════════════════════════
# QUEUE D'OPÉRATIONS OFFLINE
# ═══════════════════════════════════════════════════════════


class OfflineQueue:
    """
    Queue d'opérations en attente de synchronisation.
    
    Stocke les opérations localement quand offline.
    """
    
    QUEUE_FILE = Path(".cache/offline_queue.json")
    SESSION_KEY = "_offline_queue"
    MAX_RETRIES = 3
    
    @classmethod
    def _ensure_cache_dir(cls) -> None:
        """Crée le dossier cache si nécessaire."""
        cls.QUEUE_FILE.parent.mkdir(exist_ok=True)
    
    @classmethod
    def _load_from_file(cls) -> list[dict]:
        """Charge la queue depuis le fichier."""
        try:
            if cls.QUEUE_FILE.exists():
                with open(cls.QUEUE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erreur chargement queue offline: {e}")
        return []
    
    @classmethod
    def _save_to_file(cls, queue: list[dict]) -> None:
        """Sauvegarde la queue dans le fichier."""
        try:
            cls._ensure_cache_dir()
            with open(cls.QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(queue, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erreur sauvegarde queue offline: {e}")
    
    @classmethod
    def _get_queue(cls) -> list[dict]:
        """Récupère la queue (session + fichier)."""
        # Essayer session d'abord
        if cls.SESSION_KEY in st.session_state:
            return st.session_state[cls.SESSION_KEY]
        
        # Sinon charger depuis fichier
        queue = cls._load_from_file()
        st.session_state[cls.SESSION_KEY] = queue
        return queue
    
    @classmethod
    def _set_queue(cls, queue: list[dict]) -> None:
        """Met à jour la queue."""
        st.session_state[cls.SESSION_KEY] = queue
        cls._save_to_file(queue)
    
    @classmethod
    def add(
        cls,
        operation_type: OperationType,
        model_name: str,
        data: dict,
    ) -> PendingOperation:
        """
        Ajoute une opération à la queue.
        
        Args:
            operation_type: Type d'opération
            model_name: Nom du modèle
            data: Données de l'opération
            
        Returns:
            Opération créée
        """
        op = PendingOperation(
            operation_type=operation_type,
            model_name=model_name,
            data=data,
        )
        
        queue = cls._get_queue()
        queue.append(op.to_dict())
        cls._set_queue(queue)
        
        logger.info(f"Opération ajoutée à la queue offline: {operation_type.value} {model_name}")
        return op
    
    @classmethod
    def get_pending(cls) -> list[PendingOperation]:
        """Retourne les opérations en attente."""
        queue = cls._get_queue()
        return [PendingOperation.from_dict(d) for d in queue]
    
    @classmethod
    def get_count(cls) -> int:
        """Compte les opérations en attente."""
        return len(cls._get_queue())
    
    @classmethod
    def remove(cls, operation_id: str) -> bool:
        """Supprime une opération de la queue."""
        queue = cls._get_queue()
        new_queue = [d for d in queue if d.get("id") != operation_id]
        
        if len(new_queue) < len(queue):
            cls._set_queue(new_queue)
            return True
        return False
    
    @classmethod
    def update_retry(cls, operation_id: str, error: str) -> None:
        """Met à jour le compteur de retry."""
        queue = cls._get_queue()
        
        for op in queue:
            if op.get("id") == operation_id:
                op["retry_count"] = op.get("retry_count", 0) + 1
                op["last_error"] = error
                break
        
        cls._set_queue(queue)
    
    @classmethod
    def clear(cls) -> int:
        """Vide la queue."""
        count = cls.get_count()
        cls._set_queue([])
        return count


# ═══════════════════════════════════════════════════════════
# SYNCHRONISEUR
# ═══════════════════════════════════════════════════════════


class OfflineSynchronizer:
    """
    Synchronise les opérations en attente avec la base de données.
    """
    
    @classmethod
    def sync_all(cls, progress_callback: Callable[[int, int], None] | None = None) -> dict:
        """
        Synchronise toutes les opérations en attente.
        
        Args:
            progress_callback: Callback (current, total)
            
        Returns:
            Dict avec résultats {success: int, failed: int, errors: list}
        """
        if not ConnectionManager.is_online():
            return {"success": 0, "failed": 0, "errors": ["Pas de connexion"]}
        
        operations = OfflineQueue.get_pending()
        results = {"success": 0, "failed": 0, "errors": []}
        
        for i, op in enumerate(operations):
            if progress_callback:
                progress_callback(i + 1, len(operations))
            
            try:
                success = cls._sync_operation(op)
                
                if success:
                    OfflineQueue.remove(op.id)
                    results["success"] += 1
                else:
                    OfflineQueue.update_retry(op.id, "Échec synchronisation")
                    results["failed"] += 1
                    
            except Exception as e:
                error_msg = f"{op.model_name}/{op.operation_type.value}: {str(e)}"
                results["errors"].append(error_msg)
                OfflineQueue.update_retry(op.id, str(e))
                results["failed"] += 1
                
                logger.error(f"Erreur sync opération {op.id}: {e}")
        
        logger.info(f"Synchronisation terminée: {results['success']} OK, {results['failed']} échecs")
        return results
    
    @classmethod
    def _sync_operation(cls, op: PendingOperation) -> bool:
        """
        Synchronise une opération individuelle.
        
        Args:
            op: Opération à synchroniser
            
        Returns:
            True si succès
        """
        from src.core.database import get_db_context
        
        # Mapping des modèles vers les services
        service_map = {
            "recette": "src.services.recettes.get_recette_service",
            "inventaire": "src.services.inventaire.get_inventaire_service",
            "courses": "src.services.courses.get_courses_service",
        }
        
        service_path = service_map.get(op.model_name.lower())
        if not service_path:
            logger.warning(f"Modèle non supporté pour sync offline: {op.model_name}")
            return False
        
        # Importer dynamiquement le service
        try:
            module_path, func_name = service_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            get_service = getattr(module, func_name)
            service = get_service()
        except Exception as e:
            logger.error(f"Erreur import service: {e}")
            return False
        
        # Exécuter l'opération
        with get_db_context() as db:
            if op.operation_type == OperationType.CREATE:
                result = service.create(op.data, db=db)
                return result is not None
                
            elif op.operation_type == OperationType.UPDATE:
                item_id = op.data.pop("id", None)
                if item_id:
                    result = service.update(item_id, op.data, db=db)
                    return result is not None
                return False
                
            elif op.operation_type == OperationType.DELETE:
                item_id = op.data.get("id")
                if item_id:
                    return service.delete(item_id, db=db)
                return False
        
        return False


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR OFFLINE-AWARE
# ═══════════════════════════════════════════════════════════


def offline_aware(model_name: str, operation_type: OperationType = OperationType.CREATE):
    """
    Décorateur qui gère automatiquement le mode offline.
    
    Si offline, met l'opération en queue.
    Si online, exécute normalement.
    
    Args:
        model_name: Nom du modèle
        operation_type: Type d'opération
        
    Example:
        >>> @offline_aware("recette", OperationType.CREATE)
        >>> def creer_recette(data: dict, db: Session) -> Recette:
        >>>     return Recette(**data)
    """
    def decorator(func: Callable):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Vérifier connexion
            if ConnectionManager.is_online():
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Si erreur de connexion, passer en offline
                    if "connection" in str(e).lower() or "timeout" in str(e).lower():
                        ConnectionManager.handle_connection_error(e)
                    else:
                        raise
            
            # Mode offline - mettre en queue
            data = kwargs.get("data", args[0] if args else {})
            OfflineQueue.add(operation_type, model_name, data)
            
            # Retourner un objet mock avec les données
            return {"_offline": True, **data}
        
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_connection_status():
    """Affiche l'indicateur de connexion."""
    
    status = ConnectionManager.get_status()
    pending = OfflineQueue.get_count()
    
    status_config = {
        ConnectionStatus.ONLINE: ("🟢", "En ligne", "#4CAF50"),
        ConnectionStatus.OFFLINE: ("🔴", "Hors ligne", "#F44336"),
        ConnectionStatus.CONNECTING: ("🟡", "Connexion...", "#FF9800"),
        ConnectionStatus.ERROR: ("🔴", "Erreur", "#F44336"),
    }
    
    icon, label, color = status_config.get(status, ("⚪", "Inconnu", "#9E9E9E"))
    
    # Badge avec compteur si opérations en attente
    badge = ""
    if pending > 0:
        badge = f' <span style="background: #FF9800; color: white; padding: 1px 6px; border-radius: 10px; font-size: 0.7rem;">{pending}</span>'
    
    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; '
        f'background: {color}15; border-radius: 8px; border-left: 3px solid {color};">'
        f'<span>{icon}</span>'
        f'<span style="font-weight: 500;">{label}</span>'
        f'{badge}'
        f'</div>',
        unsafe_allow_html=True
    )


def render_sync_panel():
    """Affiche le panneau de synchronisation."""
    
    pending = OfflineQueue.get_count()
    
    with st.expander(f"🔄 Synchronisation ({pending} en attente)", expanded=pending > 0):
        
        if pending == 0:
            st.success("[OK] Tout est synchronisé")
            return
        
        st.warning(f"[!] {pending} opération(s) en attente de synchronisation")
        
        # Liste des opérations
        operations = OfflineQueue.get_pending()
        for op in operations[:5]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"• {op.operation_type.value.upper()} {op.model_name}")
                if op.retry_count > 0:
                    st.caption(f"  ↳ {op.retry_count} tentative(s), erreur: {op.last_error}")
            with col2:
                if st.button("🗑️", key=f"del_op_{op.id}", help="Annuler"):
                    OfflineQueue.remove(op.id)
                    st.rerun()
        
        if len(operations) > 5:
            st.caption(f"... et {len(operations) - 5} autre(s)")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Synchroniser", key="sync_now", use_container_width=True, type="primary"):
                if ConnectionManager.check_connection(force=True):
                    with st.spinner("Synchronisation en cours..."):
                        results = OfflineSynchronizer.sync_all()
                    
                    if results["success"] > 0:
                        st.success(f"[OK] {results['success']} opération(s) synchronisée(s)")
                    if results["failed"] > 0:
                        st.warning(f"[!] {results['failed']} échec(s)")
                    
                    st.rerun()
                else:
                    st.error("[ERROR] Pas de connexion disponible")
        
        with col2:
            if st.button("🗑️ Tout annuler", key="clear_queue", use_container_width=True):
                OfflineQueue.clear()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    "ConnectionStatus",
    "ConnectionManager",
    "OperationType",
    "PendingOperation",
    "OfflineQueue",
    "OfflineSynchronizer",
    "OfflineSync",  # Alias pour compatibilité tests
    "offline_aware",
    "render_connection_status",
    "render_sync_panel",
]

# Alias de compatibilité pour les tests
OfflineSync = OfflineSynchronizer
