"""
Bootstrap - Initialisation simplifiée de l'application.

Point d'entrée unique pour:
1. Validation de la configuration
2. Enregistrement des event subscribers
3. Cleanup automatique (atexit)

Usage::
    from src.core.bootstrap import demarrer_application

    # Au démarrage
    rapport = demarrer_application()
    if not rapport.succes:
        st.error("Erreur d'initialisation")
        for err in rapport.erreurs:
            st.error(err)
        st.stop()
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


def demarrer_application(
    valider_config: bool = True,
    initialiser_eager: bool = False,
    enregistrer_atexit: bool = True,
) -> RapportDemarrage:
    """
    Initialise l'application.

    Args:
        valider_config: Exécuter les validations de config (défaut: True)
        initialiser_eager: Non utilisé (conservé pour compatibilité API)
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

    # ─── Étape 1b: Initialisation Sentry (error tracking) ───
    logger.info("🔍 Initialisation Sentry...")
    try:
        from src.core.monitoring.sentry import initialiser_sentry

        if initialiser_sentry():
            rapport.composants_enregistres.append("Sentry")
        else:
            logger.debug("Sentry désactivé (SENTRY_DSN non configuré)")
    except Exception as e:
        logger.debug(f"Sentry non disponible: {e}")

    # ─── Étape 2: Enregistrement des event subscribers ───
    logger.info("📡 Enregistrement des event subscribers...")
    try:
        from src.services.core.events.subscribers import enregistrer_subscribers

        nb_subs = enregistrer_subscribers()
        if nb_subs:
            rapport.composants_enregistres.append(f"EventSubscribers({nb_subs})")
            logger.info(f"✅ {nb_subs} event subscribers enregistrés")
    except ImportError:
        logger.debug("Module events.subscribers non disponible, skip")
    except Exception as e:
        rapport.avertissements.append(f"Event subscribers: {e}")
        logger.warning(f"⚠ Échec enregistrement subscribers: {e}")

    # ─── Étape 2b: Charger tous les modèles SQLAlchemy (préventif)
    # Certains modules utilisent des relationships entre fichiers modèles
    # qui nécessitent le chargement complet des modules pour que
    # SQLAlchemy résolve correctement les targets de relationship.
    try:
        from src.core.models import charger_tous_modeles

        charger_tous_modeles()
        rapport.composants_enregistres.append("ModelsLoaded")
        logger.debug("✅ Tous les modèles SQLAlchemy ont été chargés")
    except Exception as e:
        # Non bloquant: continuer mais avertir
        rapport.avertissements.append(f"charger_tous_modeles: {e}")
        logger.warning(f"⚠ Impossible de charger tous les modèles: {e}")

    # ─── Étape 2c: Listener invalidation cache (LISTEN/NOTIFY PostgreSQL)
    try:
        from src.core.caching.invalidation_listener import (
            demarrer_listener_invalidation_cache,
        )

        demarrer_listener_invalidation_cache()
        rapport.composants_enregistres.append("CacheInvalidationListener")
    except Exception as e:
        rapport.avertissements.append(f"cache_invalidation_listener: {e}")
        logger.warning(f"⚠ Impossible de démarrer le listener cache: {e}")

    # ─── Étape 3: Enregistrement atexit ───
    if enregistrer_atexit:
        atexit.register(arreter_application)

    # ─── Étape 4: Validation Protocols des services (PEP 544) ───
    try:
        from src.services.core.registry import registre

        violations = registre.valider_protocols()
        if violations:
            for nom, msgs in violations.items():
                rapport.avertissements.append(f"Protocol {nom}: {', '.join(msgs)}")
            logger.warning(f"⚠️ {len(violations)} service(s) ne respectent pas leurs Protocols")
        else:
            logger.debug("✅ Validation Protocols OK")
    except Exception as e:
        logger.debug(f"Validation Protocols ignorée: {e}")

    rapport.duree_totale_ms = (time.perf_counter() - debut) * 1000
    _deja_demarre = True

    logger.info(f"✅ Application démarrée en {rapport.duree_totale_ms:.1f}ms")

    return rapport


def arreter_application() -> None:
    """
    Arrête proprement l'application.

    - Dispose des connexions DB
    """
    global _deja_demarre

    if not _deja_demarre:
        return

    logger.info("🛑 Arrêt de l'application...")

    # Arrêt listener cache
    try:
        from src.core.caching.invalidation_listener import arreter_listener_invalidation_cache

        arreter_listener_invalidation_cache()
    except Exception as e:
        logger.debug(f"Arrêt listener cache ignoré: {e}")

    # Cleanup du moteur DB
    try:
        from .db import obtenir_moteur

        moteur = obtenir_moteur()
        moteur.dispose()
        logger.info("✅ Connexions DB fermées")
    except Exception as e:
        logger.debug(f"Cleanup DB ignoré: {e}")

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
