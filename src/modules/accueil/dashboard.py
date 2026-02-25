"""
Dashboard Central - Interface utilisateur
Vue d'ensemble de l'application avec stats, alertes et raccourcis

Structure:
  - alerts.py: Alertes critiques (stock bas, péremption, ménage)
  - stats.py: Statistiques globales et graphiques Plotly
  - summaries.py: Cartes résumé par module (cuisine, inventaire, courses, planning)
  - resume_hebdo.py: Résumé hebdomadaire IA
"""

import logging
from datetime import date

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.fragments import ui_fragment
from src.ui.keys import KeyNamespace
from src.ui.tokens_semantic import Sem

logger = logging.getLogger(__name__)

from .alerts import afficher_critical_alerts
from .stats import afficher_global_stats, afficher_graphiques_enrichis
from .summaries import (
    afficher_courses_summary,
    afficher_cuisine_summary,
    afficher_inventaire_summary,
    afficher_planning_summary,
)

_keys = KeyNamespace("accueil")

# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════


@profiler_rerun("accueil")
def app():
    """Point d'entree module accueil"""
    from src.core.state import obtenir_etat
    from src.ui import etat_vide

    with error_boundary("accueil_dashboard"):
        # Dashboard widgets enrichis
        try:
            from src.ui.components import (
                afficher_sante_systeme,
                widget_jules_apercu,
            )

            WIDGETS_DISPONIBLES = True
        except ImportError:
            WIDGETS_DISPONIBLES = False

        # Header
        state = obtenir_etat()

        st.markdown(
            f"<h1 style='text-align: center;'>🤖 Bienvenue {state.nom_utilisateur} !</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<p style='text-align: center; color: {Sem.ON_SURFACE_SECONDARY}; font-size: 1.1rem;'>"
            "Ton assistant familial intelligent"
            "</p>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # WIDGET "QU'EST-CE QU'ON MANGE ?" 🍽️
        # ═══════════════════════════════════════════════════════════

        try:
            from src.ui.components import widget_quest_ce_quon_mange

            widget_quest_ce_quon_mange()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Widget qcom indisponible: {e}")

        st.markdown("---")

        # Alertes critiques en haut
        afficher_critical_alerts()

        st.markdown("---")

        # Stats globales
        afficher_global_stats()

        st.markdown("---")

        # Raccourcis rapides
        afficher_quick_actions()

        st.markdown("---")

        # Graphiques enrichis (si widgets disponibles)
        if WIDGETS_DISPONIBLES:
            afficher_graphiques_enrichis()
            st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # RÉSUMÉ HEBDOMADAIRE IA
        # ═══════════════════════════════════════════════════════════

        try:
            from src.modules.accueil.resume_hebdo import afficher_resume_hebdomadaire

            afficher_resume_hebdomadaire()
            st.markdown("---")
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Résumé hebdo indisponible: {e}")

        # ═══════════════════════════════════════════════════════════
        # TIMELINE ÉVÉNEMENTS À VENIR
        # ═══════════════════════════════════════════════════════════

        st.subheader("📅 Prochains événements")

        try:
            from datetime import timedelta

            from src.modules.planning.timeline_ui import charger_events_periode

            # Charger les événements des 7 prochains jours
            aujourd_hui = date.today()
            events = charger_events_periode(aujourd_hui, aujourd_hui + timedelta(days=7))

            if events:
                # Afficher les 5 prochains
                events_tries = sorted(events, key=lambda e: e["date_debut"])[:5]

                for event in events_tries:
                    jour = event["date_debut"].strftime("%a %d/%m")
                    heure = event["date_debut"].strftime("%H:%M")
                    couleur = event.get("couleur", "#757575")
                    lieu = f" • 📍 {event['lieu']}" if event.get("lieu") else ""

                    st.markdown(
                        f'<div style="padding:8px;margin:4px 0;background:{Sem.SURFACE_ALT};'
                        f'border-left:4px solid {couleur};border-radius:4px;">'
                        f"<strong>{jour} {heure}</strong> - {event['titre']}"
                        f'<span style="color:{Sem.ON_SURFACE_SECONDARY};">{lieu}</span></div>',
                        unsafe_allow_html=True,
                    )

                # Lien vers le calendrier complet
                if len(events) > 5:
                    st.caption(f"... et {len(events) - 5} autres événements cette semaine")
            else:
                etat_vide("Aucun événement prévu cette semaine", "📅")

        except ImportError:
            st.caption("Module timeline non disponible")
        except Exception as e:
            st.warning(f"Erreur chargement événements: {e}")

        # Section rappels (si disponible)
        try:
            from src.services.cuisine.planning.rappels import verifier_et_envoyer_rappels

            rappels_info = verifier_et_envoyer_rappels()

            if rappels_info["prochains"]:
                with st.expander(
                    f"🔔 {len(rappels_info['prochains'])} rappel(s) à venir", expanded=False
                ):
                    for rappel in rappels_info["prochains"]:
                        st.markdown(
                            f"- **{rappel['titre']}** - {rappel['date_debut'].strftime('%H:%M')}"
                        )
        except ImportError:
            pass
        except Exception:
            pass

        st.markdown("---")

        # Vue par module
        col1, col2 = st.columns(2)

        with col1:
            afficher_cuisine_summary()
            st.markdown("")
            afficher_planning_summary()

        with col2:
            afficher_inventaire_summary()
            st.markdown("")
            afficher_courses_summary()

        # Footer avec sante système
        st.markdown("---")
        if WIDGETS_DISPONIBLES:
            col_footer1, col_footer2 = st.columns([3, 1])
            with col_footer1:
                afficher_sante_systeme()
            with col_footer2:
                widget_jules_apercu()

        # ═══════════════════════════════════════════════════════════
        # JULES AUJOURD'HUI — Résumé quotidien
        # ═══════════════════════════════════════════════════════════

        st.markdown("---")
        try:
            from src.ui.components import carte_resume_jules

            carte_resume_jules()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Carte Jules indisponible: {e}")

        # Section activité récente
        st.markdown("---")
        with st.expander("📝 Activité récente", expanded=False):
            try:
                from src.ui.views.historique import afficher_timeline_activite

                afficher_timeline_activite(limit=5)
            except Exception as e:
                st.caption(f"Timeline indisponible: {e}")


# ═══════════════════════════════════════════════════════════
# RACCOURCIS RAPIDES
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_quick_actions():
    """Raccourcis d'actions rapides"""
    from src.core.state import GestionnaireEtat

    st.markdown("### ⚡ Actions Rapides")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "➕ Ajouter Recette", key=_keys("quick_add_recette"), width="stretch", type="primary"
        ):
            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            st.rerun()

    with col2:
        if st.button("📅 Voir Courses", key=_keys("quick_view_courses"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            st.rerun()

    with col3:
        if st.button("📦 Gerer Inventaire", key=_keys("quick_view_inventaire"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            st.rerun()

    with col4:
        if st.button("🧹 Planning Semaine", key=_keys("quick_view_planning"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            st.rerun()
