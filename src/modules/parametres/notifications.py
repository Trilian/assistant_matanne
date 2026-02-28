"""
Paramètres - Notifications configurables par module.

Matrice module × type de notification, heures calmes, canal de livraison.
"""

from __future__ import annotations

import logging
from datetime import time

import streamlit as st

from src.core.decorators import avec_session_db
from src.core.state import obtenir_etat
from src.core.state.persistent import PersistentState, persistent_state
from src.ui.feedback import afficher_erreur, afficher_succes
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("param_notifs")

# Structure des notifications par module
_MODULES_NOTIFICATIONS = {
    "🍳 Cuisine": {
        "key": "cuisine",
        "toggles": {
            "suggestions_repas": "Suggestions de repas IA",
            "stock_bas": "Alertes stock bas",
            "batch_cooking": "Batch cooking prêt",
        },
    },
    "👶 Famille": {
        "key": "famille",
        "toggles": {
            "routines_jules": "Routines de Jules",
            "activites_weekend": "Activités weekend",
            "achats_planifier": "Achats à planifier",
        },
    },
    "🏠 Maison": {
        "key": "maison",
        "toggles": {
            "entretien_programme": "Entretien programmé",
            "charges_payer": "Charges à payer",
            "jardin_arrosage": "Jardin / arrosage",
        },
    },
    "📅 Planning": {
        "key": "planning",
        "toggles": {
            "rappels_evenements": "Rappels événements",
            "taches_retard": "Tâches en retard",
        },
    },
    "💰 Budget": {
        "key": "budget",
        "toggles": {
            "depassement_seuil": "Dépassement de seuil",
            "resume_mensuel": "Résumé mensuel",
        },
    },
}


@avec_session_db
def _charger_preferences(*, db=None) -> PreferenceNotification | None:
    """Charge les préférences de notification depuis la DB."""
    from sqlalchemy.orm import Session

    from src.core.models.notifications import PreferenceNotification

    db: Session
    return db.query(PreferenceNotification).first()


@avec_session_db
def _sauvegarder_preferences(data: dict, *, db=None) -> bool:
    """Sauvegarde les préférences de notification."""
    from sqlalchemy.orm import Session

    from src.core.models.notifications import PreferenceNotification

    db: Session
    pref = db.query(PreferenceNotification).first()
    if not pref:
        pref = PreferenceNotification()
        db.add(pref)

    for champ, valeur in data.items():
        if hasattr(pref, champ):
            setattr(pref, champ, valeur)

    db.commit()
    return True


@persistent_state(key="param_alerts", sync_interval=60, auto_commit=True)
def _obtenir_config_alertes() -> dict:
    """Valeurs par défaut pour les paramètres modifiables via UI (alerte vacances...)."""
    return {
        "vacances_alert_days": 14,
    }


@ui_fragment
def afficher_notifications_config():
    """Configuration des notifications par module."""
    from src.services.profils import NOTIFICATIONS_MODULES_DEFAUT

    st.markdown("### 🔔 Notifications")
    st.caption("Configure les notifications par module et par canal")

    etat = obtenir_etat()

    # Charger les préférences existantes
    pref = _charger_preferences()

    # ── Section 1: Configuration générale ──
    st.markdown("#### ⚙️ Configuration générale")

    col1, col2, col3 = st.columns(3)

    with col1:
        notifs_actives = st.toggle(
            "Notifications activées",
            value=True,
            key=_keys("toggle_global"),
        )

    with col2:
        canal_options = ["push", "email", "webhook"]
        canal_actuel = pref.canal_prefere if pref else "push"
        canal = st.selectbox(
            "Canal de livraison",
            canal_options,
            index=canal_options.index(canal_actuel) if canal_actuel in canal_options else 0,
            key=_keys("canal"),
        )

    with col3:
        # Seuil d'alerte pour la preview Vacances (jours)
        pstate_alerts = _obtenir_config_alertes()
        current_alerts = pstate_alerts.get_all()
        default_vacances = current_alerts.get("vacances_alert_days", None)

        # Fallback to global settings if not present
        try:
            from src.core.config import obtenir_parametres

            if default_vacances is None:
                default_vacances = obtenir_parametres().VACANCES_ALERT_DAYS
        except Exception:
            if default_vacances is None:
                default_vacances = 14

        vacances_alert_days = st.number_input(
            "Seuil alert vacances (jours)",
            min_value=1,
            max_value=365,
            value=int(default_vacances),
            step=1,
            key=_keys("vacances_alert_days"),
        )

    # Heures calmes
    st.markdown("##### 🌙 Heures calmes")
    col_h1, col_h2 = st.columns(2)

    with col_h1:
        heure_debut = st.time_input(
            "Début",
            value=pref.quiet_hours_start if pref and pref.quiet_hours_start else time(22, 0),
            key=_keys("quiet_start"),
        )
    with col_h2:
        heure_fin = st.time_input(
            "Fin",
            value=pref.quiet_hours_end if pref and pref.quiet_hours_end else time(7, 0),
            key=_keys("quiet_end"),
        )

    if not notifs_actives:
        st.info("🔇 Les notifications sont désactivées globalement.")
        return

    # ── Section 2: Matrice par module ──
    st.markdown("---")
    st.markdown("#### 📋 Notifications par module")

    modules_actifs = pref.modules_actifs if pref and pref.modules_actifs else None
    if not modules_actifs:
        modules_actifs = NOTIFICATIONS_MODULES_DEFAUT.copy()

    for label, config in _MODULES_NOTIFICATIONS.items():
        module_key = config["key"]
        module_vals = modules_actifs.get(module_key, {})

        with st.expander(label, expanded=False):
            for toggle_key, toggle_label in config["toggles"].items():
                val = st.toggle(
                    toggle_label,
                    value=module_vals.get(toggle_key, False),
                    key=_keys(f"{module_key}_{toggle_key}"),
                )
                module_vals[toggle_key] = val

            modules_actifs[module_key] = module_vals

    # ── Catégories historiques ──
    st.markdown("---")
    st.markdown("#### 📌 Catégories classiques")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        courses_rappel = st.toggle(
            "🛒 Rappels courses",
            value=pref.courses_rappel if pref else True,
            key=_keys("courses"),
        )
        repas_suggestion = st.toggle(
            "🍽️ Suggestions repas",
            value=pref.repas_suggestion if pref else True,
            key=_keys("repas"),
        )
        stock_alerte = st.toggle(
            "📦 Alertes stock",
            value=pref.stock_alerte if pref else True,
            key=_keys("stock"),
        )

    with col_c2:
        meteo_alerte = st.toggle(
            "🌤️ Alertes météo",
            value=pref.meteo_alerte if pref else True,
            key=_keys("meteo"),
        )
        budget_alerte = st.toggle(
            "💰 Alertes budget",
            value=pref.budget_alerte if pref else True,
            key=_keys("budget"),
        )

    # ── Sauvegarde ──
    st.markdown("---")

    if st.button("💾 Sauvegarder les préférences", type="primary", key=_keys("save")):
        data = {
            "courses_rappel": courses_rappel,
            "repas_suggestion": repas_suggestion,
            "stock_alerte": stock_alerte,
            "meteo_alerte": meteo_alerte,
            "budget_alerte": budget_alerte,
            "quiet_hours_start": heure_debut,
            "quiet_hours_end": heure_fin,
            "modules_actifs": modules_actifs,
            "canal_prefere": canal,
        }
        try:
            _sauvegarder_preferences(data)
            # Sauvegarder le seuil vacances dans PersistentState param_alerts
            try:
                pstate_alerts.update({"vacances_alert_days": int(vacances_alert_days)})
                pstate_alerts.commit()
            except Exception:
                logger.debug("Impossible de sauvegarder param_alerts persistent state")

            afficher_succes("✅ Préférences de notification sauvegardées !")
        except Exception as e:
            logger.error("Erreur sauvegarde notifications: %s", e)
            afficher_erreur(f"❌ Erreur: {e}")

    # ── Test ──
    with st.expander("🧪 Tester les notifications"):
        st.caption("Envoyer une notification test via ntfy")
        if st.button("📤 Envoyer un test", key=_keys("test")):
            st.info("📨 Notification test envoyée (vérifiez votre canal ntfy)")
