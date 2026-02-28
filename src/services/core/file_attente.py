"""
Service de file d'attente offline — Queue côté serveur pour opérations différées.

Gère les opérations qui échouent (réseau, DB indisponible) en les mettant
en file d'attente pour un retry automatique avec backoff exponentiel.

Architecture:
- File d'attente persistante en mémoire (deque) + fichier JSON (survit aux redémarrages)
- Retry automatique avec backoff exponentiel (1s → 2s → 4s → 8s → max 60s)
- Souscription au bus d'événements pour capturer les échecs
- Traitement batch périodique (manuellement ou via timer)

Usage:
    from src.services.core.file_attente import obtenir_file_attente

    file = obtenir_file_attente()

    # Enqueue une opération échouée
    file.enqueue(
        operation="recette.creer",
        payload={"nom": "Tarte aux pommes", "categorie": "dessert"},
        callback="src.services.cuisine.recettes.service.creer_recette",
    )

    # Traiter la file (retry toutes les opérations en attente)
    resultats = file.traiter()

    # Consulter la file
    print(file.statistiques())
"""

from __future__ import annotations

import importlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum, auto
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class StatutOperation(StrEnum):
    """Statut d'une opération en file."""

    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    ABANDONNE = "abandonne"  # Max retries atteint


class OperationEnAttente(BaseModel):
    """Opération mise en file d'attente pour retry."""

    id: int = 0
    operation: str = ""  # Type d'opération (ex: "recette.creer")
    callback: str = ""  # Chemin importable de la fonction à appeler
    payload: dict[str, Any] = Field(default_factory=dict)
    statut: StatutOperation = StatutOperation.EN_ATTENTE
    tentatives: int = 0
    max_tentatives: int = 5
    derniere_erreur: str = ""
    cree_le: datetime = Field(default_factory=datetime.now)
    prochaine_tentative: datetime = Field(default_factory=datetime.now)
    backoff_secondes: float = 1.0

    class Config:
        use_enum_values = True


class ResultatTraitement(BaseModel):
    """Résultat du traitement d'un batch de la file."""

    traitees: int = 0
    reussies: int = 0
    echouees: int = 0
    abandonnees: int = 0
    restantes: int = 0
    duree_ms: float = 0


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


# Backoff exponentiel : délai = min(base * 2^tentative, max)
BACKOFF_BASE = 1.0  # secondes
BACKOFF_MAX = 60.0  # secondes
MAX_TENTATIVES_DEFAUT = 5
TAILLE_FILE_MAX = 1000

# Fichier de persistance
FICHIER_PERSISTANCE = Path("data/.file_attente.json")


class ServiceFileAttente:
    """Service de file d'attente pour opérations différées.

    Stocke les opérations échouées et les retente avec backoff exponentiel.
    Persiste en fichier JSON pour survivre aux redémarrages.
    """

    def __init__(
        self,
        max_tentatives: int = MAX_TENTATIVES_DEFAUT,
        fichier: Path | None = None,
    ):
        self._file: deque[OperationEnAttente] = deque(maxlen=TAILLE_FILE_MAX)
        self._compteur: int = 0
        self._max_tentatives = max_tentatives
        self._fichier = fichier or FICHIER_PERSISTANCE
        self._stats_globales = {
            "total_enqueue": 0,
            "total_reussies": 0,
            "total_echouees": 0,
            "total_abandonnees": 0,
        }

        # Charger la file persistée au démarrage
        self._charger_persistance()

    # ─── API publique ───

    def enqueue(
        self,
        operation: str,
        payload: dict[str, Any],
        callback: str = "",
        max_tentatives: int | None = None,
    ) -> OperationEnAttente:
        """Ajoute une opération à la file d'attente.

        Args:
            operation: Type d'opération (ex: "recette.creer")
            payload: Données de l'opération
            callback: Chemin importable de la fonction (ex: "module.func")
            max_tentatives: Nombre max de tentatives (défaut: config globale)

        Returns:
            OperationEnAttente créée
        """
        self._compteur += 1
        self._stats_globales["total_enqueue"] += 1

        op = OperationEnAttente(
            id=self._compteur,
            operation=operation,
            callback=callback,
            payload=payload,
            max_tentatives=max_tentatives or self._max_tentatives,
        )

        self._file.append(op)
        self._persister()

        logger.info(
            f"File d'attente: ajout #{op.id} '{operation}' " f"(file: {len(self._file)} éléments)"
        )
        return op

    def traiter(self) -> ResultatTraitement:
        """Traite toutes les opérations en attente (batch).

        Retente les opérations dont la prochaine tentative est passée.
        Applique le backoff exponentiel en cas d'échec.

        Returns:
            ResultatTraitement avec compteurs
        """
        debut = time.monotonic()
        maintenant = datetime.now()

        traitees = 0
        reussies = 0
        echouees = 0
        abandonnees = 0

        # Copier la file pour itération (on modifie en place)
        operations_a_traiter = [
            op
            for op in self._file
            if op.statut == StatutOperation.EN_ATTENTE and op.prochaine_tentative <= maintenant
        ]

        for op in operations_a_traiter:
            traitees += 1
            op.statut = StatutOperation.EN_COURS
            op.tentatives += 1

            succes = self._executer_operation(op)

            if succes:
                op.statut = StatutOperation.REUSSI
                reussies += 1
                self._stats_globales["total_reussies"] += 1
                logger.info(f"File d'attente: #{op.id} '{op.operation}' réussie")
            else:
                if op.tentatives >= op.max_tentatives:
                    op.statut = StatutOperation.ABANDONNE
                    abandonnees += 1
                    self._stats_globales["total_abandonnees"] += 1
                    logger.warning(
                        f"File d'attente: #{op.id} '{op.operation}' abandonnée "
                        f"après {op.tentatives} tentatives"
                    )
                else:
                    # Backoff exponentiel
                    delai = min(
                        BACKOFF_BASE * (2 ** (op.tentatives - 1)),
                        BACKOFF_MAX,
                    )
                    op.backoff_secondes = delai
                    op.prochaine_tentative = datetime.fromtimestamp(time.time() + delai)
                    op.statut = StatutOperation.EN_ATTENTE
                    echouees += 1
                    self._stats_globales["total_echouees"] += 1
                    logger.debug(
                        f"File d'attente: #{op.id} '{op.operation}' échouée, "
                        f"retry dans {delai:.0f}s"
                    )

        # Nettoyer les opérations terminées (réussies ou abandonnées)
        self._file = deque(
            (op for op in self._file if op.statut == StatutOperation.EN_ATTENTE),
            maxlen=TAILLE_FILE_MAX,
        )

        self._persister()

        duree = (time.monotonic() - debut) * 1000

        return ResultatTraitement(
            traitees=traitees,
            reussies=reussies,
            echouees=echouees,
            abandonnees=abandonnees,
            restantes=len(self._file),
            duree_ms=round(duree, 2),
        )

    def consulter(
        self,
        statut: StatutOperation | None = None,
        limite: int = 50,
    ) -> list[OperationEnAttente]:
        """Consulte la file d'attente.

        Args:
            statut: Filtrer par statut (None = tous)
            limite: Nombre max de résultats

        Returns:
            Liste d'opérations
        """
        resultats = list(self._file)
        if statut:
            resultats = [op for op in resultats if op.statut == statut]
        return resultats[:limite]

    def vider(self) -> int:
        """Vide toute la file d'attente.

        Returns:
            Nombre d'opérations supprimées
        """
        n = len(self._file)
        self._file.clear()
        self._persister()
        logger.info(f"File d'attente vidée ({n} opérations)")
        return n

    def supprimer(self, operation_id: int) -> bool:
        """Supprime une opération de la file.

        Args:
            operation_id: ID de l'opération

        Returns:
            True si supprimée
        """
        avant = len(self._file)
        self._file = deque(
            (op for op in self._file if op.id != operation_id),
            maxlen=TAILLE_FILE_MAX,
        )
        if len(self._file) < avant:
            self._persister()
            return True
        return False

    def statistiques(self) -> dict[str, Any]:
        """Retourne les statistiques de la file.

        Returns:
            Dict avec compteurs et état de la file
        """
        en_attente = sum(1 for op in self._file if op.statut == StatutOperation.EN_ATTENTE)

        operations_par_type: dict[str, int] = {}
        for op in self._file:
            operations_par_type[op.operation] = operations_par_type.get(op.operation, 0) + 1

        return {
            "taille_file": len(self._file),
            "en_attente": en_attente,
            "capacite_max": TAILLE_FILE_MAX,
            "par_operation": operations_par_type,
            **self._stats_globales,
        }

    # ─── Exécution ───

    def _executer_operation(self, op: OperationEnAttente) -> bool:
        """Exécute une opération en attente.

        Résout le callback (chemin importable) et l'appelle avec le payload.

        Args:
            op: Opération à exécuter

        Returns:
            True si l'exécution a réussi
        """
        if not op.callback:
            logger.warning(f"Opération #{op.id}: pas de callback défini")
            op.derniere_erreur = "Aucun callback défini"
            return False

        try:
            # Résoudre le callback: "module.path.function_name"
            parts = op.callback.rsplit(".", 1)
            if len(parts) != 2:
                op.derniere_erreur = f"Callback invalide: {op.callback}"
                return False

            module_path, func_name = parts
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)

            # Appeler avec le payload
            func(**op.payload)
            return True

        except ImportError as e:
            op.derniere_erreur = f"Module introuvable: {e}"
            logger.warning(f"Opération #{op.id}: {op.derniere_erreur}")
            return False
        except AttributeError as e:
            op.derniere_erreur = f"Fonction introuvable: {e}"
            logger.warning(f"Opération #{op.id}: {op.derniere_erreur}")
            return False
        except Exception as e:
            op.derniere_erreur = str(e)
            logger.warning(f"Opération #{op.id} échouée: {e}")
            return False

    # ─── Persistance ───

    def _persister(self) -> None:
        """Persiste la file en fichier JSON (best-effort)."""
        try:
            self._fichier.parent.mkdir(parents=True, exist_ok=True)
            donnees = [op.model_dump(mode="json") for op in self._file]
            self._fichier.write_text(
                json.dumps(donnees, default=str, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.debug(f"Persistance file d'attente échouée: {e}")

    def _charger_persistance(self) -> None:
        """Charge la file depuis le fichier JSON (si existant)."""
        try:
            if self._fichier.exists():
                donnees = json.loads(self._fichier.read_text(encoding="utf-8"))
                for d in donnees:
                    try:
                        op = OperationEnAttente(**d)
                        # Re-mettre en attente si elle était en cours
                        if op.statut == StatutOperation.EN_COURS:
                            op.statut = StatutOperation.EN_ATTENTE
                        if op.statut == StatutOperation.EN_ATTENTE:
                            self._file.append(op)
                            self._compteur = max(self._compteur, op.id)
                    except Exception:
                        pass  # Ignorer les entrées corrompues

                if self._file:
                    logger.info(
                        f"File d'attente: {len(self._file)} opérations "
                        f"restaurées depuis le fichier"
                    )
        except Exception as e:
            logger.debug(f"Chargement file d'attente échoué: {e}")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("file_attente", tags={"core", "queue", "offline"})
def obtenir_file_attente() -> ServiceFileAttente:
    """Factory singleton pour le service de file d'attente offline."""
    return ServiceFileAttente()


__all__ = [
    "ServiceFileAttente",
    "OperationEnAttente",
    "ResultatTraitement",
    "StatutOperation",
    "obtenir_file_attente",
]
