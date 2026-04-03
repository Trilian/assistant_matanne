"""
Service de synchronisation offline — File d'attente côté serveur.

Complète le Service Worker (client-side) avec un mécanisme serveur pour:
- Enregistrer les opérations en attente lors de déconnexions
- Rejouer automatiquement les actions en file à la reconnexion
- Gérer les conflits de synchronisation
- Persister la queue sur disque (survit aux redémarrages)

Architecture:
- Queue FIFO persistante (JSON file-backed)
- Retry avec backoff exponentiel
- Dead-letter queue pour les erreurs non-récupérables
- Intégration event bus pour notification de sync

Usage:
    from src.services.core.offline_queue import obtenir_service_file_attente

    queue = obtenir_service_file_attente()

    # En mode offline : enregistrer une opération
    queue.ajouter(
        operation="recette.creer",
        payload={"nom": "Tarte", "ingredients": [...]},
        priorite=1,
    )

    # À la reconnexion : rejouer la queue
    resultats = queue.traiter_file()

    # Voir le statut
    statut = queue.statut()
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import deque
from datetime import datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class StatutOperation(StrEnum):
    """Statut d'une opération en file."""

    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ECHOUEE = "echouee"
    DEAD_LETTER = "dead_letter"  # Erreur non-récupérable


class OperationFile(BaseModel):
    """Une opération dans la file d'attente."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    operation: str  # Type d'opération (ex: "recette.creer")
    payload: dict[str, Any] = Field(default_factory=dict)
    priorite: int = 0  # 0 = normal, 1 = haute, 2 = critique
    statut: StatutOperation = StatutOperation.EN_ATTENTE
    tentatives: int = 0
    max_tentatives: int = 3
    cree_le: datetime = Field(default_factory=datetime.now)
    derniere_tentative: datetime | None = None
    erreur: str | None = None
    resultat: dict[str, Any] | None = None


class StatutFile(BaseModel):
    """Statut global de la file d'attente."""

    en_attente: int = 0
    en_cours: int = 0
    terminees: int = 0
    echouees: int = 0
    dead_letter: int = 0
    total: int = 0
    derniere_sync: datetime | None = None
    est_en_ligne: bool = True


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════

# Fichier de persistance
QUEUE_DIR = Path("data/offline_queue")
QUEUE_FILE = QUEUE_DIR / "queue.json"
DEAD_LETTER_FILE = QUEUE_DIR / "dead_letter.json"


class ServiceFileAttente:
    """File d'attente côté serveur pour synchronisation offline.

    - Persiste sur disque (JSON)
    - Retry avec backoff exponentiel
    - Dead-letter queue
    - Handlers d'opérations enregistrables
    """

    def __init__(self):
        self._file: deque[OperationFile] = deque()
        self._dead_letter: list[OperationFile] = []
        self._handlers: dict[str, Callable] = {}
        self._terminees: int = 0
        self._derniere_sync: datetime | None = None
        self._est_en_ligne: bool = True

        # Créer le répertoire
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)

        # Charger la queue persistée
        self._charger()

    # ─── Persistance ───

    def _charger(self) -> None:
        """Charge la queue depuis le fichier JSON."""
        if QUEUE_FILE.exists():
            try:
                data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
                for item in data:
                    self._file.append(OperationFile(**item))
                logger.info(f"Queue offline chargée: {len(self._file)} opérations")
            except Exception as e:
                logger.warning(f"Erreur chargement queue: {e}")

        if DEAD_LETTER_FILE.exists():
            try:
                data = json.loads(DEAD_LETTER_FILE.read_text(encoding="utf-8"))
                self._dead_letter = [OperationFile(**item) for item in data]
            except Exception:
                pass

    def _sauvegarder(self) -> None:
        """Sauvegarde la queue sur disque."""
        try:
            data = [op.model_dump(mode="json") for op in self._file]
            QUEUE_FILE.write_text(
                json.dumps(data, default=str, ensure_ascii=False), encoding="utf-8"
            )

            if self._dead_letter:
                dl_data = [op.model_dump(mode="json") for op in self._dead_letter]
                DEAD_LETTER_FILE.write_text(
                    json.dumps(dl_data, default=str, ensure_ascii=False), encoding="utf-8"
                )
        except Exception as e:
            logger.warning(f"Erreur sauvegarde queue: {e}")

    # ─── Enregistrement de handlers ───

    def enregistrer_handler(self, operation: str, handler: Callable) -> None:
        """Enregistre un handler pour un type d'opération.

        Args:
            operation: Type d'opération (ex: "recette.creer")
            handler: Callable qui prend (payload: dict) et retourne dict | None
        """
        self._handlers[operation] = handler
        logger.debug(f"Handler enregistré pour '{operation}'")

    # ─── API publique ───

    def ajouter(
        self,
        operation: str,
        payload: dict[str, Any] | None = None,
        priorite: int = 0,
        max_tentatives: int = 3,
    ) -> OperationFile:
        """Ajoute une opération à la file d'attente.

        Args:
            operation: Type d'opération
            payload: Données de l'opération
            priorite: 0=normal, 1=haute, 2=critique
            max_tentatives: Nombre max de tentatives

        Returns:
            OperationFile créée
        """
        op = OperationFile(
            operation=operation,
            payload=payload or {},
            priorite=priorite,
            max_tentatives=max_tentatives,
        )
        self._file.append(op)
        self._sauvegarder()
        logger.info(f"Opération ajoutée: {operation} (priorité={priorite})")
        return op

    def traiter_file(self, limite: int | None = None) -> list[OperationFile]:
        """Traite les opérations en attente dans la file.

        Args:
            limite: Nombre max d'opérations à traiter (None = toutes)

        Returns:
            Liste des opérations traitées
        """
        traitees: list[OperationFile] = []

        # Trier par priorité (décroissante) puis date (croissante)
        ops_a_traiter = sorted(
            [op for op in self._file if op.statut == StatutOperation.EN_ATTENTE],
            key=lambda o: (-o.priorite, o.cree_le),
        )

        if limite:
            ops_a_traiter = ops_a_traiter[:limite]

        for op in ops_a_traiter:
            resultat = self._executer_operation(op)
            traitees.append(resultat)

        # Nettoyer les opérations terminées de la file
        self._file = deque(
            op
            for op in self._file
            if op.statut not in (StatutOperation.TERMINEE, StatutOperation.DEAD_LETTER)
        )

        self._derniere_sync = datetime.now()
        self._sauvegarder()

        # Émettre événement de sync
        self._emettre_sync_terminee(traitees)

        return traitees

    def _executer_operation(self, op: OperationFile) -> OperationFile:
        """Exécute une opération avec retry."""
        handler = self._handlers.get(op.operation)

        if not handler:
            logger.warning(f"Pas de handler pour '{op.operation}'")
            op.statut = StatutOperation.DEAD_LETTER
            op.erreur = f"Handler non trouvé pour '{op.operation}'"
            self._dead_letter.append(op)
            return op

        op.statut = StatutOperation.EN_COURS
        op.tentatives += 1
        op.derniere_tentative = datetime.now()

        try:
            resultat = handler(op.payload)
            op.statut = StatutOperation.TERMINEE
            op.resultat = resultat if isinstance(resultat, dict) else {"ok": True}
            self._terminees += 1
            logger.info(f"Opération {op.id} ({op.operation}) terminée")

        except Exception as e:
            logger.error(f"Erreur opération {op.id}: {e}")
            op.erreur = str(e)

            if op.tentatives >= op.max_tentatives:
                op.statut = StatutOperation.DEAD_LETTER
                self._dead_letter.append(op)
                logger.warning(f"Opération {op.id} en dead-letter après {op.tentatives} tentatives")
            else:
                op.statut = StatutOperation.EN_ATTENTE
                # Backoff exponentiel: 2^tentatives secondes
                time.sleep(min(2**op.tentatives, 30))

        return op

    def statut(self) -> StatutFile:
        """Retourne le statut global de la file."""
        ops = list(self._file)
        return StatutFile(
            en_attente=sum(1 for o in ops if o.statut == StatutOperation.EN_ATTENTE),
            en_cours=sum(1 for o in ops if o.statut == StatutOperation.EN_COURS),
            terminees=self._terminees,
            echouees=sum(1 for o in ops if o.statut == StatutOperation.ECHOUEE),
            dead_letter=len(self._dead_letter),
            total=len(ops) + self._terminees + len(self._dead_letter),
            derniere_sync=self._derniere_sync,
            est_en_ligne=self._est_en_ligne,
        )

    def marquer_en_ligne(self, en_ligne: bool = True) -> None:
        """Met à jour le statut de connectivité.

        Args:
            en_ligne: True si connecté, False si offline
        """
        ancien = self._est_en_ligne
        self._est_en_ligne = en_ligne

        if not ancien and en_ligne:
            logger.info("Connexion rétablie — traitement de la file en attente")
            self.traiter_file()
        elif ancien and not en_ligne:
            logger.info("Passage en mode offline")

    def consulter_dead_letter(self) -> list[OperationFile]:
        """Consulte les opérations en dead-letter.

        Returns:
            Liste des opérations non-récupérables
        """
        return list(self._dead_letter)

    def rejouer_dead_letter(self, operation_id: str) -> OperationFile | None:
        """Rejoue une opération depuis la dead-letter queue.

        Args:
            operation_id: ID de l'opération à rejouer

        Returns:
            OperationFile rejouée ou None si non trouvée
        """
        for i, op in enumerate(self._dead_letter):
            if op.id == operation_id:
                # Remettre en file avec tentatives remises à zéro
                op.statut = StatutOperation.EN_ATTENTE
                op.tentatives = 0
                op.erreur = None
                self._file.append(op)
                self._dead_letter.pop(i)
                self._sauvegarder()
                logger.info(f"Opération {operation_id} remise en file depuis dead-letter")
                return op
        return None

    def vider(self) -> int:
        """Vide la file d'attente (pour maintenance).

        Returns:
            Nombre d'opérations supprimées
        """
        n = len(self._file)
        self._file.clear()
        self._sauvegarder()
        logger.info(f"File d'attente vidée ({n} opérations)")
        return n

    def _emettre_sync_terminee(self, traitees: list[OperationFile]) -> None:
        """Émet un événement de synchronisation terminée."""
        try:
            from src.services.core.events import obtenir_bus

            nb_ok = sum(1 for o in traitees if o.statut == StatutOperation.TERMINEE)
            nb_err = sum(
                1
                for o in traitees
                if o.statut in (StatutOperation.ECHOUEE, StatutOperation.DEAD_LETTER)
            )

            obtenir_bus().emettre(
                "sync.file_traitee",
                {
                    "nb_traitees": len(traitees),
                    "nb_ok": nb_ok,
                    "nb_erreurs": nb_err,
                },
                source="offline_queue",
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("file_attente", tags={"core", "sync", "offline"})
def obtenir_service_file_attente() -> ServiceFileAttente:
    """Factory singleton pour le service de file d'attente offline."""
    return ServiceFileAttente()


__all__ = [
    "ServiceFileAttente",
    "OperationFile",
    "StatutOperation",
    "StatutFile",
    "obtenir_service_file_attente",
]
