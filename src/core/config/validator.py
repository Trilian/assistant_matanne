"""
Validator - Validation stricte de la configuration au démarrage.

Vérifie que toutes les dépendances (DB, API keys, etc.) sont
correctement configurées avant de démarrer l'application.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

logger = logging.getLogger(__name__)


class NiveauValidation(Enum):
    """Niveau de sévérité d'une validation."""

    CRITIQUE = auto()  # Bloque le démarrage
    AVERTISSEMENT = auto()  # Log un warning mais continue
    INFO = auto()  # Information seulement


@dataclass
class ResultatValidation:
    """Résultat d'une validation individuelle."""

    nom: str
    niveau: NiveauValidation
    succes: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    duree_ms: float = 0.0


@dataclass
class RapportValidation:
    """Rapport complet de validation."""

    resultats: list[ResultatValidation] = field(default_factory=list)
    duree_totale_ms: float = 0.0

    @property
    def valide(self) -> bool:
        """True si aucune erreur critique."""
        return not any(
            r.niveau == NiveauValidation.CRITIQUE and not r.succes for r in self.resultats
        )

    @property
    def erreurs_critiques(self) -> list[ResultatValidation]:
        """Liste des erreurs critiques."""
        return [r for r in self.resultats if r.niveau == NiveauValidation.CRITIQUE and not r.succes]

    @property
    def avertissements(self) -> list[ResultatValidation]:
        """Liste des avertissements (non bloquants)."""
        return [
            r for r in self.resultats if r.niveau == NiveauValidation.AVERTISSEMENT and not r.succes
        ]

    @property
    def succes(self) -> list[ResultatValidation]:
        """Liste des validations réussies."""
        return [r for r in self.resultats if r.succes]

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "valide": self.valide,
            "duree_totale_ms": self.duree_totale_ms,
            "erreurs_critiques": len(self.erreurs_critiques),
            "avertissements": len(self.avertissements),
            "succes": len(self.succes),
            "resultats": [
                {
                    "nom": r.nom,
                    "niveau": r.niveau.name,
                    "succes": r.succes,
                    "message": r.message,
                    "duree_ms": r.duree_ms,
                }
                for r in self.resultats
            ],
        }


class ValidateurConfiguration:
    """
    Validateur de configuration modulaire et extensible.

    Usage::
        validateur = ValidateurConfiguration()
        validateur.ajouter(
            "database",
            NiveauValidation.CRITIQUE,
            verifier_connexion_db,
            "Connexion DB impossible"
        )

        rapport = validateur.executer()
        if not rapport.valide:
            raise RuntimeError(f"Config invalide: {rapport.erreurs_critiques}")
    """

    def __init__(self) -> None:
        self._validations: list[tuple[str, NiveauValidation, Callable[[], bool], str]] = []

    def ajouter(
        self,
        nom: str,
        niveau: NiveauValidation,
        verificateur: Callable[[], bool],
        message_erreur: str = "",
    ) -> ValidateurConfiguration:
        """
        Ajoute une validation.

        Args:
            nom: Nom unique de la validation
            niveau: Sévérité (CRITIQUE, AVERTISSEMENT, INFO)
            verificateur: Fonction retournant True si valide
            message_erreur: Message si échec

        Returns:
            Self (fluent API)
        """
        self._validations.append((nom, niveau, verificateur, message_erreur))
        return self

    def executer(self) -> RapportValidation:
        """
        Exécute toutes les validations.

        Returns:
            RapportValidation avec tous les résultats
        """
        debut_total = time.perf_counter()
        rapport = RapportValidation()

        for nom, niveau, verificateur, message_erreur in self._validations:
            debut = time.perf_counter()
            try:
                succes = verificateur()
                message = "OK" if succes else (message_erreur or f"Validation '{nom}' échouée")
            except Exception as e:
                succes = False
                message = f"Exception: {e}"

            duree = (time.perf_counter() - debut) * 1000

            resultat = ResultatValidation(
                nom=nom,
                niveau=niveau,
                succes=succes,
                message=message,
                duree_ms=duree,
            )
            rapport.resultats.append(resultat)

            # Log approprié selon niveau
            if succes:
                logger.info(f"✓ [{nom}] OK ({duree:.1f}ms)")
            elif niveau == NiveauValidation.CRITIQUE:
                logger.error(f"✗ [{nom}] CRITIQUE: {message} ({duree:.1f}ms)")
            elif niveau == NiveauValidation.AVERTISSEMENT:
                logger.warning(f"⚠ [{nom}] AVERTISSEMENT: {message} ({duree:.1f}ms)")
            else:
                logger.info(f"ℹ [{nom}] INFO: {message} ({duree:.1f}ms)")

        rapport.duree_totale_ms = (time.perf_counter() - debut_total) * 1000
        return rapport


# ═══════════════════════════════════════════════════════════
# VALIDATIONS BUILT-IN
# ═══════════════════════════════════════════════════════════


def _verifier_database_url() -> bool:
    """Vérifie que DATABASE_URL est configurée."""
    try:
        from . import obtenir_parametres

        return bool(obtenir_parametres().DATABASE_URL)
    except Exception:
        return False


def _verifier_mistral_key() -> bool:
    """Vérifie que MISTRAL_API_KEY est configurée."""
    try:
        from . import obtenir_parametres

        key = obtenir_parametres().MISTRAL_API_KEY
        return bool(key and len(key) > 10)
    except Exception:
        return False


def _tester_connexion_db() -> bool:
    """Teste la connexion à la base de données."""
    try:
        from ..db import verifier_connexion

        ok, _ = verifier_connexion()
        return ok
    except Exception:
        return False


def _verifier_dossier_cache() -> bool:
    """Vérifie que le dossier de cache est accessible."""
    try:
        from pathlib import Path

        cache_dir = Path(".cache")
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir.is_dir()
    except Exception:
        return False


def creer_validateur_defaut() -> ValidateurConfiguration:
    """
    Crée un validateur avec les vérifications par défaut.

    Inclut:
    - DATABASE_URL (critique)
    - Connexion DB (critique)
    - MISTRAL_API_KEY (avertissement)
    - Dossier cache (info)
    """
    validateur = ValidateurConfiguration()

    # Base de données
    validateur.ajouter(
        "database_url",
        NiveauValidation.CRITIQUE,
        _verifier_database_url,
        "DATABASE_URL non configurée dans .env.local ou secrets Streamlit",
    )

    validateur.ajouter(
        "database_connexion",
        NiveauValidation.CRITIQUE,
        _tester_connexion_db,
        "Impossible de se connecter à la base de données",
    )

    # Clé API Mistral (optionnelle)
    validateur.ajouter(
        "mistral_api_key",
        NiveauValidation.AVERTISSEMENT,
        _verifier_mistral_key,
        "MISTRAL_API_KEY non configurée (fonctionnalités IA désactivées)",
    )

    # Cache
    validateur.ajouter(
        "dossier_cache",
        NiveauValidation.INFO,
        _verifier_dossier_cache,
        "Dossier .cache non accessible",
    )

    return validateur


__all__ = [
    "ValidateurConfiguration",
    "NiveauValidation",
    "ResultatValidation",
    "RapportValidation",
    "creer_validateur_defaut",
]
