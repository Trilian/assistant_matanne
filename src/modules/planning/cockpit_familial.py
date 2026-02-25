"""
D.5 — Cockpit Familial Hebdomadaire.

Vue unifiée de la semaine : repas, événements, activités familiales,
tâches d'entretien. Navigation semaine par semaine.

Point d'entrée: ``app()``
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

# Session keys scopées
_keys = KeyNamespace("cockpit_familial")

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

_JOURS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

_COULEURS_TYPE_REPAS = {
    "petit_déjeuner": "#FFF9C4",
    "déjeuner": "#C8E6C9",
    "goûter": "#FFECB3",
    "dîner": "#BBDEFB",
}

_ICONES_TYPE_EVENT = {
    "rdv": "📍",
    "activité": "⚽",
    "fête": "🎉",
    "autre": "📌",
}


def _lundi_semaine(d: date) -> date:
    """Retourne le lundi de la semaine contenant *d*."""
    return d - timedelta(days=d.weekday())


def _plage_semaine(offset: int = 0) -> tuple[date, date]:
    """Retourne (lundi, dimanche) de la semaine avec décalage *offset*."""
    lundi = _lundi_semaine(date.today()) + timedelta(weeks=offset)
    dimanche = lundi + timedelta(days=6)
    return lundi, dimanche


# ═══════════════════════════════════════════════════════════
# DATA LOADERS
# ═══════════════════════════════════════════════════════════


def _charger_repas(lundi: date, dimanche: date) -> dict[date, list]:
    """Charge les repas de la semaine groupés par date."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.planning import Repas

        with obtenir_contexte_db() as session:
            repas_list = (
                session.query(Repas)
                .filter(Repas.date_repas >= lundi, Repas.date_repas <= dimanche)
                .order_by(Repas.date_repas, Repas.type_repas)
                .all()
            )
            # Grouper par date
            par_date: dict[date, list] = {}
            for r in repas_list:
                info = {
                    "type": r.type_repas,
                    "recette": r.recette.nom if r.recette else None,
                    "prepare": r.prepare,
                    "notes": r.notes,
                }
                par_date.setdefault(r.date_repas, []).append(info)
            return par_date
    except Exception as e:
        logger.debug(f"Chargement repas échoué: {e}")
        return {}


def _charger_evenements(lundi: date, dimanche: date) -> dict[date, list]:
    """Charge les événements du calendrier de la semaine."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.planning import EvenementPlanning

        lundi_dt = datetime.combine(lundi, datetime.min.time())
        dimanche_dt = datetime.combine(dimanche, datetime.max.time())

        with obtenir_contexte_db() as session:
            events = (
                session.query(EvenementPlanning)
                .filter(
                    EvenementPlanning.date_debut >= lundi_dt,
                    EvenementPlanning.date_debut <= dimanche_dt,
                )
                .order_by(EvenementPlanning.date_debut)
                .all()
            )
            par_date: dict[date, list] = {}
            for ev in events:
                info = {
                    "titre": ev.titre,
                    "type": ev.type_event,
                    "heure": ev.date_debut.strftime("%H:%M") if ev.date_debut else "",
                    "lieu": ev.lieu,
                }
                jour = ev.date_debut.date()
                par_date.setdefault(jour, []).append(info)
            return par_date
    except Exception as e:
        logger.debug(f"Chargement événements échoué: {e}")
        return {}


def _charger_activites(lundi: date, dimanche: date) -> dict[date, list]:
    """Charge les activités familiales prévues."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.famille import ActiviteFamille

        with obtenir_contexte_db() as session:
            activites = (
                session.query(ActiviteFamille)
                .filter(
                    ActiviteFamille.date_prevue >= lundi,
                    ActiviteFamille.date_prevue <= dimanche,
                    ActiviteFamille.statut != "annulé",
                )
                .order_by(ActiviteFamille.date_prevue)
                .all()
            )
            par_date: dict[date, list] = {}
            for act in activites:
                info = {
                    "titre": act.titre,
                    "type": act.type_activite,
                    "lieu": act.lieu,
                    "duree": act.duree_heures,
                    "statut": act.statut,
                }
                par_date.setdefault(act.date_prevue, []).append(info)
            return par_date
    except Exception as e:
        logger.debug(f"Chargement activités échoué: {e}")
        return {}


def _charger_taches(lundi: date, dimanche: date) -> dict[date, list]:
    """Charge les tâches d'entretien planifiées sur la semaine."""
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.habitat import TacheEntretien

        with obtenir_contexte_db() as session:
            taches = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.prochaine_fois >= lundi,
                    TacheEntretien.prochaine_fois <= dimanche,
                    TacheEntretien.fait.is_(False),
                )
                .order_by(TacheEntretien.prochaine_fois, TacheEntretien.priorite)
                .all()
            )
            par_date: dict[date, list] = {}
            for t in taches:
                info = {
                    "nom": t.nom,
                    "categorie": t.categorie,
                    "duree": t.duree_minutes,
                    "priorite": t.priorite,
                    "responsable": t.responsable,
                }
                par_date.setdefault(t.prochaine_fois, []).append(info)  # type: ignore[arg-type]
            return par_date
    except Exception as e:
        logger.debug(f"Chargement tâches échoué: {e}")
        return {}


# ═══════════════════════════════════════════════════════════
# AFFICHAGE D'UN JOUR
# ═══════════════════════════════════════════════════════════


def _afficher_jour(
    jour: date,
    repas: list,
    evenements: list,
    activites: list,
    taches: list,
) -> None:
    """Affiche le contenu d'un jour dans une colonne."""
    est_aujourdhui = jour == date.today()
    style_border = "border: 2px solid var(--st-primary, #1976d2);" if est_aujourdhui else ""
    label_aujourdhui = " · **Auj.**" if est_aujourdhui else ""

    st.markdown(
        f"<div style='min-height:60px;padding:6px;border-radius:8px;"
        f"background:var(--st-surface-alt,#fafafa);{style_border}'>",
        unsafe_allow_html=True,
    )

    st.markdown(f"**{_JOURS_FR[jour.weekday()]} {jour.day}**{label_aujourdhui}")

    # Repas
    if repas:
        for r in repas:
            emoji = "✅" if r["prepare"] else "🍽️"
            nom = r["recette"] or r["notes"] or r["type"]
            st.caption(f"{emoji} {r['type'][:3].capitalize()}: {nom}")

    # Événements
    if evenements:
        for ev in evenements:
            icone = _ICONES_TYPE_EVENT.get(ev["type"], "📌")
            heure = f" {ev['heure']}" if ev["heure"] else ""
            st.caption(f"{icone}{heure} {ev['titre']}")

    # Activités famille
    if activites:
        for act in activites:
            st.caption(f"👨‍👩‍👦 {act['titre']}")

    # Tâches entretien
    if taches:
        for t in taches:
            prio_emoji = (
                "🔴" if t["priorite"] == "haute" else "🟡" if t["priorite"] == "moyenne" else "⚪"
            )
            st.caption(f"{prio_emoji} {t['nom']} ({t['duree']}min)")

    # Jour vide
    if not (repas or evenements or activites or taches):
        st.caption("_Rien de prévu_")

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# BARRE DE RÉSUMÉ
# ═══════════════════════════════════════════════════════════


def _afficher_resume(repas: dict, evenements: dict, activites: dict, taches: dict) -> None:
    """Barre de métriques résumé de la semaine."""
    nb_repas = sum(len(v) for v in repas.values())
    nb_events = sum(len(v) for v in evenements.values())
    nb_activites = sum(len(v) for v in activites.values())
    nb_taches = sum(len(v) for v in taches.values())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🍽️ Repas planifiés", nb_repas)
    with c2:
        st.metric("📅 Événements", nb_events)
    with c3:
        st.metric("👨‍👩‍👦 Activités", nb_activites)
    with c4:
        st.metric("🏠 Tâches", nb_taches)


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("cockpit_familial")
def app() -> None:
    """Point d'entrée du cockpit familial."""

    with error_boundary("cockpit_familial"):
        st.title("🎯 Cockpit Familial")
        st.caption("Vue unifiée de votre semaine — repas, événements, activités, tâches")

        # ── Navigation semaine ──
        offset_key = _keys("offset_semaine")
        if offset_key not in st.session_state:
            st.session_state[offset_key] = 0

        col_prev, col_label, col_next, col_today = st.columns([1, 4, 1, 1])
        with col_prev:
            if st.button("◀️ Semaine préc.", key=_keys("prev")):
                st.session_state[offset_key] -= 1
                st.rerun()
        with col_next:
            if st.button("Semaine suiv. ▶️", key=_keys("next")):
                st.session_state[offset_key] += 1
                st.rerun()
        with col_today:
            if st.button("📍 Aujourd'hui", key=_keys("today")):
                st.session_state[offset_key] = 0
                st.rerun()

        lundi, dimanche = _plage_semaine(st.session_state[offset_key])

        with col_label:
            st.subheader(f"Semaine du {lundi.strftime('%d/%m')} au {dimanche.strftime('%d/%m/%Y')}")

        st.markdown("---")

        # ── Charger les données ──
        repas = _charger_repas(lundi, dimanche)
        evenements = _charger_evenements(lundi, dimanche)
        activites = _charger_activites(lundi, dimanche)
        taches = _charger_taches(lundi, dimanche)

        # ── Résumé ──
        _afficher_resume(repas, evenements, activites, taches)

        st.markdown("---")

        # ── Grille 7 jours ──
        cols = st.columns(7)
        for i in range(7):
            jour = lundi + timedelta(days=i)
            with cols[i]:
                _afficher_jour(
                    jour,
                    repas.get(jour, []),
                    evenements.get(jour, []),
                    activites.get(jour, []),
                    taches.get(jour, []),
                )

        # ── Légende ──
        with st.expander("ℹ️ Légende"):
            st.markdown(
                "- 🍽️ Repas planifié · ✅ Repas préparé\n"
                "- 📍 RDV · ⚽ Activité · 🎉 Fête · 📌 Autre\n"
                "- 👨‍👩‍👦 Activité famille\n"
                "- 🔴 Tâche haute priorité · 🟡 Moyenne · ⚪ Normale"
            )
