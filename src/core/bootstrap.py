"""
Bootstrap - Initialisation complète et unifiée de l'application.

Point d'entrée unique pour:
1. Validation de la configuration
2. Enregistrement des composants dans le container IoC
3. Initialisation des singletons
4. Vérification de santé

Usage::
    from src.core.bootstrap import demarrer_application, arreter_application

    # Au démarrage
    rapport = demarrer_application()
    if not rapport.succes:
        st.error("Erreur d'initialisation")
        for err in rapport.erreurs:
            st.error(err)
        st.stop()

    # À l'arrêt (optionnel, cleanup)
    arreter_application()
"""

from __future__ import annotations

import atexit
import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RapportDemarrage:
    """Rapport de démarrage de l'application."""

    succes: bool = True
    composants_enregistres: list[str] = field(default_factory=list)
    erreurs: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)
    duree_totale_ms: float = 0.0
    validation_ok: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "succes": self.succes,
            "validation_ok": self.validation_ok,
            "composants": self.composants_enregistres,
            "erreurs": self.erreurs,
            "avertissements": self.avertissements,
            "duree_ms": self.duree_totale_ms,
        }


_deja_demarre = False


def _enregistrer_composants() -> list[str]:
    """Enregistre les composants dans le container IoC."""
    from .container import conteneur

    composants: list[str] = []

    # 1. Configuration
    try:
        from .config import Parametres, obtenir_parametres

        conteneur.singleton(
            Parametres,
            factory=lambda: obtenir_parametres(),
            alias="config",
        )
        composants.append("Parametres")
    except Exception as e:
        logger.warning(f"Échec enregistrement Parametres: {e}")

    # 2. Database Engine
    try:
        from sqlalchemy import Engine

        from .db import obtenir_moteur

        conteneur.singleton(
            Engine,
            factory=lambda: obtenir_moteur(),
            cleanup=lambda e: e.dispose(),
            alias="db_engine",
        )
        composants.append("Engine")
    except Exception as e:
        logger.warning(f"Échec enregistrement Engine: {e}")

    # 3. Cache Multi-Niveaux
    try:
        from .caching import CacheMultiNiveau

        conteneur.singleton(
            CacheMultiNiveau,
            factory=lambda: CacheMultiNiveau(),
            alias="cache",
        )
        composants.append("CacheMultiNiveau")
    except Exception as e:
        logger.warning(f"Échec enregistrement Cache: {e}")

    # 4. Client IA
    try:
        from .ai import ClientIA

        conteneur.singleton(
            ClientIA,
            factory=lambda: ClientIA(),
            alias="ia_client",
        )
        composants.append("ClientIA")
    except Exception as e:
        logger.warning(f"Échec enregistrement ClientIA: {e}")

    # 5. Métriques
    try:
        from .monitoring import CollecteurMetriques

        conteneur.singleton(
            CollecteurMetriques,
            factory=lambda: CollecteurMetriques(),
            alias="metriques",
        )
        composants.append("CollecteurMetriques")
    except Exception as e:
        logger.warning(f"Échec enregistrement Métriques: {e}")

    return composants


def demarrer_application(
    valider_config: bool = True,
    initialiser_eager: bool = False,
    enregistrer_atexit: bool = True,
) -> RapportDemarrage:
    """
    Initialise complètement l'application.

    Args:
        valider_config: Exécuter les validations de config (défaut: True)
        initialiser_eager: Créer tous les singletons immédiatement (défaut: False)
        enregistrer_atexit: Enregistrer cleanup automatique à l'arrêt (défaut: True)

    Returns:
        RapportDemarrage avec statut et détails
    """
    global _deja_demarre

    if _deja_demarre:
        logger.debug("Application déjà démarrée, skip")
        return RapportDemarrage(succes=True)

    debut = time.perf_counter()
    rapport = RapportDemarrage()

    logger.info("🚀 Démarrage de l'application...")

    # ─── Étape 1: Validation de la configuration ───
    if valider_config:
        logger.info("🔍 Validation de la configuration...")
        try:
            from .config.validator import creer_validateur_defaut

            validateur = creer_validateur_defaut()
            rapport_validation = validateur.executer()

            rapport.validation_ok = rapport_validation.valide

            if not rapport_validation.valide:
                rapport.succes = False
                rapport.erreurs = [
                    f"{r.nom}: {r.message}" for r in rapport_validation.erreurs_critiques
                ]
                logger.error(f"❌ Validation échouée: {len(rapport.erreurs)} erreur(s)")
                return rapport

            # Avertissements non bloquants
            for r in rapport_validation.avertissements:
                rapport.avertissements.append(f"{r.nom}: {r.message}")

            logger.info("✅ Configuration validée")

        except Exception as e:
            logger.warning(f"⚠ Validation skippée (module non disponible): {e}")

    # ─── Étape 2: Enregistrement des composants ───
    logger.info("📦 Enregistrement des composants...")
    try:
        rapport.composants_enregistres = _enregistrer_composants()
        logger.info(f"✅ {len(rapport.composants_enregistres)} composants enregistrés")
    except Exception as e:
        rapport.succes = False
        rapport.erreurs.append(f"Enregistrement composants: {e}")
        logger.error(f"❌ Erreur enregistrement: {e}")
        return rapport

    # ─── Étape 3: Initialisation eager (optionnel) ───
    if initialiser_eager:
        logger.info("⚡ Initialisation des singletons...")
        try:
            from .container import conteneur

            conteneur.initialiser()
            logger.info("✅ Singletons initialisés")
        except Exception as e:
            # Non bloquant
            rapport.avertissements.append(f"Initialisation partielle: {e}")
            logger.warning(f"⚠ Initialisation partielle: {e}")

    # ─── Étape 4: Enregistrement atexit ───
    if enregistrer_atexit:
        atexit.register(arreter_application)

    rapport.duree_totale_ms = (time.perf_counter() - debut) * 1000
    _deja_demarre = True

    logger.info(f"✅ Application démarrée en {rapport.duree_totale_ms:.1f}ms")

    return rapport


def arreter_application() -> None:
    """
    Arrête proprement l'application.

    - Ferme le container IoC (cleanup des ressources)
    - Dispose des connexions DB
    - Vide les caches
    """
    global _deja_demarre

    if not _deja_demarre:
        return

    logger.info("🛑 Arrêt de l'application...")

    try:
        from .container import conteneur

        conteneur.fermer()
        logger.info("✅ Container fermé")
    except Exception as e:
        logger.error(f"Erreur fermeture container: {e}")

    _deja_demarre = False
    logger.info("✅ Application arrêtée")


def est_demarree() -> bool:
    """Retourne True si l'application est démarrée."""
    return _deja_demarre


__all__ = [
    "demarrer_application",
    "arreter_application",
    "est_demarree",
    "RapportDemarrage",
]
