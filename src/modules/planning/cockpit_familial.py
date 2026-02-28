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

from src.core.decorators import avec_session_db
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur

logger = logging.getLogger(__name__)

# Session keys scopées
_keys = KeyNamespace("cockpit_familial")

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

_JOURS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

_COULEURS_TYPE_REPAS = {
    "petit_déjeuner": Couleur.BG_YELLOW_LIGHT,
    "déjeuner": Couleur.BG_LIGHT_GREEN_ALT,
    "goûter": Couleur.BG_METEO_END,
    "dîner": Couleur.BG_JULES_END,
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


@avec_session_db
def _charger_repas(lundi: date, dimanche: date, session=None) -> dict[date, list]:
    """Charge les repas de la semaine groupés par date."""
    try:
        from src.core.models.planning import Repas

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


@avec_session_db
def _charger_evenements(lundi: date, dimanche: date, session=None) -> dict[date, list]:
    """Charge les événements du calendrier de la semaine."""
    try:
        from src.core.models.planning import EvenementPlanning

        lundi_dt = datetime.combine(lundi, datetime.min.time())
        dimanche_dt = datetime.combine(dimanche, datetime.max.time())

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


@avec_session_db
def _charger_activites(lundi: date, dimanche: date, session=None) -> dict[date, list]:
    """Charge les activités familiales prévues."""
    try:
        from src.core.models.famille import ActiviteFamille

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


@avec_session_db
def _charger_taches(lundi: date, dimanche: date, session=None) -> dict[date, list]:
    """Charge les tâches d'entretien planifiées sur la semaine."""
    try:
        from src.core.models.habitat import TacheEntretien

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

    st.markdown(
        f"<div style='min-height:60px;padding:6px;border-radius:8px;"
        f"background:var(--st-surface-alt,#fafafa);{style_border}'>",
        unsafe_allow_html=True,
    )

    st.markdown(f"**{_JOURS_FR[jour.weekday()]} {jour.day}**")

    if est_aujourdhui:
        st.caption("Aujourd'hui")

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
        st.title("Planning familial")
        st.caption("Vue unifiée de votre semaine — repas, événements, activités, tâches")

        # ── Accès rapide aux outils planning ──
        _c1, _c2, _c3 = st.columns(3)
        with _c1:
            if st.button("📅 Calendrier", key=_keys("nav_cal"), use_container_width=True):
                from src.core.state import GestionnaireEtat

                GestionnaireEtat.naviguer_vers("planning.calendrier")
                rerun()
        with _c2:
            if st.button("📋 Templates", key=_keys("nav_tpl"), use_container_width=True):
                from src.core.state import GestionnaireEtat

                GestionnaireEtat.naviguer_vers("planning.templates_ui")
                rerun()
        with _c3:
            if st.button("📊 Timeline", key=_keys("nav_tl"), use_container_width=True):
                from src.core.state import GestionnaireEtat

                GestionnaireEtat.naviguer_vers("planning.timeline_ui")
                rerun()

        # ── Navigation semaine ──
        offset_key = _keys("offset_semaine")
        if offset_key not in st.session_state:
            st.session_state[offset_key] = 0

        col_prev, col_label, col_next = st.columns([1, 4, 1])
        with col_prev:
            if st.button("◀️", key=_keys("prev")):
                st.session_state[offset_key] -= 1
                rerun()
        with col_next:
            if st.button("▶️", key=_keys("next")):
                st.session_state[offset_key] += 1
                rerun()

        lundi, dimanche = _plage_semaine(st.session_state[offset_key])

        with col_label:
            week_label = f"Semaine du {lundi.strftime('%d/%m')} au {dimanche.strftime('%d/%m/%Y')}"
            st.markdown(
                f"<h3 class='planning--no-wrap' style='text-align:center;margin:0.25rem 0;'>{week_label}</h3>",
                unsafe_allow_html=True,
            )

        # Second row: centered Today button
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("📍 Aujourd'hui", key=_keys("today")):
                st.session_state[offset_key] = 0
                rerun()

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
