"""
Widget Runner — Système d'isolation robuste des widgets globaux.

Remplace le pattern try/except inline fragile par un runner configuré
avec fallback UI, logging structuré, et métriques de fiabilité.

Chaque widget est déclaré via ``WidgetConfig`` et exécuté de manière
isolée : l'échec de l'un ne compromet jamais les autres.

Usage:
    from src.ui.components.widget_runner import afficher_widgets_globaux

    # Dans app.py, après page.run()
    afficher_widgets_globaux()

Architecture:
    WidgetConfig → executer_widget_isole() → afficher_widgets_globaux()
    Chaque widget : lazy import → exécution → fallback si erreur
"""

from __future__ import annotations

import importlib
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True)
class WidgetConfig:
    """Configuration d'un widget global isolé.

    Attributes:
        nom: Identifiant unique du widget (pour logs et métriques).
        module: Chemin d'import complet du module.
        fonction: Nom de la fonction à appeler dans le module.
        actif: Si False, le widget est ignoré (feature flag).
        icone: Icône affichée dans le fallback en cas d'erreur.
        label_fallback: Texte du placeholder si le widget est indisponible.
        timeout_warning_s: Seuil (secondes) pour log warning de lenteur.
    """

    nom: str
    module: str
    fonction: str
    actif: bool = True
    icone: str = "⚙️"
    label_fallback: str = ""
    timeout_warning_s: float = 2.0


# ── Registre des widgets globaux ──────────────────────────

WIDGETS_GLOBAUX: list[WidgetConfig] = [
    WidgetConfig(
        nom="chat_global",
        module="src.ui.components.chat_global",
        fonction="afficher_chat_global",
        icone="💬",
        label_fallback="Chat IA",
    ),
    WidgetConfig(
        nom="notifications_live",
        module="src.ui.components.notifications_live",
        fonction="widget_notifications_live",
        icone="🔔",
        label_fallback="Notifications",
    ),
    WidgetConfig(
        nom="gamification",
        module="src.ui.components.gamification_widget",
        fonction="afficher_gamification_sidebar",
        icone="🏆",
        label_fallback="Gamification",
    ),
]


# ═══════════════════════════════════════════════════════════
# MÉTRIQUES DE FIABILITÉ
# ═══════════════════════════════════════════════════════════


@dataclass
class _WidgetMetrics:
    """Compteurs de fiabilité par widget (durée de vie session)."""

    succes: int = 0
    erreurs: int = 0
    imports_manquants: int = 0
    duree_totale_ms: float = 0.0
    derniere_erreur: str = ""


# Stockage en session_state pour persistance inter-reruns
_METRICS_KEY = "_widget_runner_metrics"


def _obtenir_metriques() -> dict[str, _WidgetMetrics]:
    """Retourne le dictionnaire de métriques (créé si absent)."""
    if _METRICS_KEY not in st.session_state:
        st.session_state[_METRICS_KEY] = {}
    return st.session_state[_METRICS_KEY]


def obtenir_stats_widgets() -> dict[str, dict[str, Any]]:
    """Retourne une copie lisible des métriques de tous les widgets.

    Utile pour le monitoring et les pages de paramètres/debug.

    Returns:
        Dict ``{nom_widget: {succes, erreurs, imports_manquants, ...}}``.
    """
    metriques = _obtenir_metriques()
    return {
        nom: {
            "succes": m.succes,
            "erreurs": m.erreurs,
            "imports_manquants": m.imports_manquants,
            "duree_moyenne_ms": round(m.duree_totale_ms / max(m.succes, 1), 1),
            "derniere_erreur": m.derniere_erreur,
        }
        for nom, m in metriques.items()
    }


# ═══════════════════════════════════════════════════════════
# EXÉCUTION ISOLÉE
# ═══════════════════════════════════════════════════════════


def _afficher_fallback(config: WidgetConfig, erreur: str | None = None) -> None:
    """Affiche un placeholder discret quand un widget est indisponible.

    Ne génère aucune exception — purement cosmétique.
    """
    label = config.label_fallback or config.nom
    if erreur:
        st.caption(f"{config.icone} {label} — indisponible")
    # Sinon : rien (widget manquant = silencieux)


def executer_widget_isole(config: WidgetConfig) -> bool:
    """Exécute un widget global de manière isolée.

    L'import est différé (lazy) pour que les modules absents ne bloquent
    pas l'ensemble. Les erreurs d'exécution sont capturées et loguées
    sans impacter les autres widgets.

    Args:
        config: Configuration du widget à exécuter.

    Returns:
        True si le widget s'est exécuté avec succès, False sinon.
    """
    if not config.actif:
        return False

    metriques = _obtenir_metriques()
    if config.nom not in metriques:
        metriques[config.nom] = _WidgetMetrics()
    m = metriques[config.nom]

    t0 = time.perf_counter()

    # ── Phase 1 : Import différé ──────────────────────────
    try:
        module = importlib.import_module(config.module)
        fn: Callable[[], Any] = getattr(module, config.fonction)
    except ImportError:
        m.imports_manquants += 1
        logger.debug(
            "Widget '%s' non disponible (module '%s' absent)",
            config.nom,
            config.module,
        )
        return False
    except AttributeError:
        m.erreurs += 1
        m.derniere_erreur = f"Fonction '{config.fonction}' absente du module '{config.module}'"
        logger.warning(
            "Widget '%s': fonction '%s' introuvable dans '%s'",
            config.nom,
            config.fonction,
            config.module,
        )
        _afficher_fallback(config, erreur=m.derniere_erreur)
        return False

    # ── Phase 2 : Exécution isolée ────────────────────────
    try:
        fn()
        duree = (time.perf_counter() - t0) * 1000
        m.succes += 1
        m.duree_totale_ms += duree

        if duree / 1000 > config.timeout_warning_s:
            logger.warning(
                "⏱️ Widget '%s' lent : %.0fms (seuil %.1fs)",
                config.nom,
                duree,
                config.timeout_warning_s,
            )
        return True

    except Exception as e:
        duree = (time.perf_counter() - t0) * 1000
        m.erreurs += 1
        m.duree_totale_ms += duree
        m.derniere_erreur = str(e)

        logger.warning(
            "Widget '%s' en erreur après %.0fms: %s",
            config.nom,
            duree,
            e,
            exc_info=True,
        )
        _afficher_fallback(config, erreur=str(e))
        return False


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE GLOBAL
# ═══════════════════════════════════════════════════════════


def afficher_widgets_globaux(
    widgets: list[WidgetConfig] | None = None,
) -> dict[str, bool]:
    """Exécute tous les widgets globaux de manière isolée.

    Chaque widget est placé dans sa propre colonne et son propre
    try/except. L'échec de l'un n'impacte pas les autres.

    Args:
        widgets: Liste de configs à afficher. Si None, utilise
            ``WIDGETS_GLOBAUX`` (registre par défaut).

    Returns:
        Dict ``{nom_widget: succès_bool}`` pour diagnostic.
    """
    configs = widgets or WIDGETS_GLOBAUX
    actifs = [c for c in configs if c.actif]

    if not actifs:
        return {}

    resultats: dict[str, bool] = {}
    colonnes = st.columns(len(actifs))

    for col, config in zip(colonnes, actifs, strict=False):
        with col:
            resultats[config.nom] = executer_widget_isole(config)

    return resultats


__all__ = [
    "WidgetConfig",
    "WIDGETS_GLOBAUX",
    "afficher_widgets_globaux",
    "executer_widget_isole",
    "obtenir_stats_widgets",
]
