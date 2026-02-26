"""
UI Feedback - Point d'entrée (PEP 562 lazy imports).

Feedback temps réel pour l'utilisateur.
"""

from __future__ import annotations

import importlib
from typing import Any

# ═══════════════════════════════════════════════════════════
# Mapping paresseux : nom → (module relatif, attribut)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Progress (st.status — Streamlit 1.25+)
    "EtapeProgression": (".progress_v2", "EtapeProgression"),
    "EtatChargement": (".progress_v2", "EtatChargement"),
    "EtatProgression": (".progress_v2", "EtatProgression"),
    "SuiviProgression": (".progress_v2", "SuiviProgression"),
    "avec_progression": (".progress_v2", "avec_progression"),
    "suivi_operation": (".progress_v2", "suivi_operation"),
    # Result → Streamlit
    "afficher_resultat": (".results", "afficher_resultat"),
    "afficher_resultat_toast": (".results", "afficher_resultat_toast"),
    "result_avec_spinner": (".results", "result_avec_spinner"),
    "result_ou_none": (".results", "result_ou_none"),
    "result_ou_vide": (".results", "result_ou_vide"),
    # Spinners
    "chargeur_squelette": (".spinners", "chargeur_squelette"),
    "indicateur_chargement": (".spinners", "indicateur_chargement"),
    "spinner_intelligent": (".spinners", "spinner_intelligent"),
    # Notifications / Toasts
    "GestionnaireNotifications": (".toasts", "GestionnaireNotifications"),
    "afficher_avertissement": (".toasts", "afficher_avertissement"),
    "afficher_erreur": (".toasts", "afficher_erreur"),
    "afficher_info": (".toasts", "afficher_info"),
    "afficher_succes": (".toasts", "afficher_succes"),
}


def __getattr__(name: str) -> Any:
    """PEP 562 — import paresseux à la première utilisation."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __package__)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Spinners
    "spinner_intelligent",
    "indicateur_chargement",
    "chargeur_squelette",
    # Progress (st.status)
    "SuiviProgression",
    "EtatChargement",
    "EtatProgression",
    "EtapeProgression",
    "suivi_operation",
    "avec_progression",
    # Notifications
    "GestionnaireNotifications",
    "afficher_succes",
    "afficher_erreur",
    "afficher_avertissement",
    "afficher_info",
    # Result → Streamlit
    "afficher_resultat",
    "afficher_resultat_toast",
    "result_ou_vide",
    "result_ou_none",
    "result_avec_spinner",
]
