"""
Tableau de bord Central - Interface utilisateur
Vue d'ensemble de l'application avec stats, alertes et raccourcis

Structure:
  - alerts.py: Alertes critiques (stock bas, péremption, ménage)
  - stats.py: Statistiques globales et graphiques Plotly
  - summaries.py: Cartes résumé par module (cuisine, inventaire, courses, planning)
  - resume_hebdo.py: Résumé hebdomadaire IA
  - resume_matinal.py: Résumé matinal IA personnalisé
  - widget_meteo.py: Météo du jour + impact activités
  - widget_ce_soir.py: Widget "Ce soir on mange..."
  - rappels_contextuels.py: Rappels contextuels enrichis
  - mini_calendrier.py: Mini-calendrier de la semaine
  - widget_economies.py: Économies réalisées ce mois
  - widget_photo.py: Photo souvenir du jour
  - widget_sante.py: Santé/fitness Garmin
  - widget_conseil_jules.py: Conseil Jules IA du jour
  - widget_gamification.py: Gamification / streaks
  - widget_jardin.py: Mini-widget jardin
  - widget_maison.py: Résumé maison / entretien
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
    from src.core.state import obtenir_etat, rerun
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
        # RÉSUMÉ MATINAL IA PERSONNALISÉ 🌅
        # ═══════════════════════════════════════════════════════════

        try:
            from src.modules.accueil.resume_matinal import afficher_resume_matinal

            afficher_resume_matinal()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Résumé matinal indisponible: {e}")

        # ═══════════════════════════════════════════════════════════
        # LIGNE 1: MÉTÉO + CE SOIR ON MANGE
        # ═══════════════════════════════════════════════════════════

        col_meteo, col_diner = st.columns(2)

        with col_meteo:
            try:
                from src.modules.accueil.widget_meteo import afficher_widget_meteo

                afficher_widget_meteo()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget météo indisponible: {e}")

        with col_diner:
            try:
                from src.modules.accueil.widget_ce_soir import afficher_widget_ce_soir

                afficher_widget_ce_soir()
            except ImportError:
                # Fallback vers l'ancien widget QCOM
                try:
                    from src.ui.components import widget_quest_ce_quon_mange

                    widget_quest_ce_quon_mange()
                except ImportError:
                    pass
            except Exception as e:
                logger.debug(f"Widget dîner indisponible: {e}")

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # RAPPELS CONTEXTUELS 🔔
        # ═══════════════════════════════════════════════════════════

        try:
            from src.modules.accueil.rappels_contextuels import afficher_rappels_contextuels

            afficher_rappels_contextuels()
        except ImportError:
            # Fallback vers les alertes classiques
            afficher_critical_alerts()
        except Exception as e:
            logger.debug(f"Rappels contextuels indisponibles: {e}")
            afficher_critical_alerts()

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # MINI-CALENDRIER SEMAINE 📅
        # ═══════════════════════════════════════════════════════════

        try:
            from src.modules.accueil.mini_calendrier import afficher_mini_calendrier

            afficher_mini_calendrier()
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"Mini-calendrier indisponible: {e}")

        st.markdown("---")

        # Stats globales
        afficher_global_stats()

        st.markdown("---")

        # Raccourcis rapides
        afficher_quick_actions()

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # LIGNE 2: ÉCONOMIES + SANTÉ/FITNESS
        # ═══════════════════════════════════════════════════════════

        col_eco, col_sante = st.columns(2)

        with col_eco:
            try:
                from src.modules.accueil.widget_economies import afficher_widget_economies

                afficher_widget_economies()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget économies indisponible: {e}")

        with col_sante:
            try:
                from src.modules.accueil.widget_sante import afficher_widget_sante

                afficher_widget_sante()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget santé indisponible: {e}")

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # LIGNE 3: CONSEIL JULES + GAMIFICATION
        # ═══════════════════════════════════════════════════════════

        col_jules, col_gamif = st.columns(2)

        with col_jules:
            try:
                from src.modules.accueil.widget_conseil_jules import afficher_conseil_jules

                afficher_conseil_jules()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Conseil Jules indisponible: {e}")

        with col_gamif:
            try:
                from src.modules.accueil.widget_gamification import afficher_widget_gamification

                afficher_widget_gamification()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget gamification indisponible: {e}")

        st.markdown("---")

        # ═══════════════════════════════════════════════════════════
        # LIGNE 4: JARDIN + MAISON
        # ═══════════════════════════════════════════════════════════

        col_jardin, col_maison = st.columns(2)

        with col_jardin:
            try:
                from src.modules.accueil.widget_jardin import afficher_widget_jardin

                afficher_widget_jardin()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget jardin indisponible: {e}")

        with col_maison:
            try:
                from src.modules.accueil.widget_maison import afficher_widget_maison

                afficher_widget_maison()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Widget maison indisponible: {e}")

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
        # MODULES — Vue synthétique 4 colonnes 📊
        # ═══════════════════════════════════════════════════════════

        st.markdown("### 📊 Vue d'ensemble des modules")
        col_rec, col_inv, col_crs, col_pln = st.columns(4)
        with col_rec:
            afficher_cuisine_summary()
        with col_inv:
            afficher_inventaire_summary()
        with col_crs:
            afficher_courses_summary()
        with col_pln:
            afficher_planning_summary()

        st.markdown("---")

        # Photo souvenir + Jules
        col_photo, col_jules = st.columns([1, 1])
        with col_photo:
            try:
                from src.modules.accueil.widget_photo import afficher_photo_souvenir

                afficher_photo_souvenir()
            except ImportError:
                pass
            except Exception as e:
                logger.debug(f"Photo souvenir indisponible: {e}")

        with col_jules:
            if WIDGETS_DISPONIBLES:
                widget_jules_apercu()
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
        # SANTÉ SYSTÈME — Expander discret en pied de page
        # ═══════════════════════════════════════════════════════════
        if WIDGETS_DISPONIBLES:
            st.markdown("---")
            afficher_sante_systeme()


# ═══════════════════════════════════════════════════════════
# RACCOURCIS RAPIDES
# ═══════════════════════════════════════════════════════════


@ui_fragment
def afficher_quick_actions():
    """Raccourcis d'actions rapides"""
    from src.core.state import GestionnaireEtat, rerun

    st.markdown("### ⚡ Actions Rapides")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "➕ Ajouter Recette",
            key=_keys("quick_add_recette"),
            use_container_width=True,
            type="primary",
            help="Ajouter une nouvelle recette à la bibliothèque",
        ):
            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            rerun()

    with col2:
        if st.button(
            "🛒 Voir Courses",
            key=_keys("quick_view_courses"),
            use_container_width=True,
            help="Voir et modifier la liste de courses",
        ):
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            rerun()

    with col3:
        if st.button(
            "📦 Gérer Inventaire",
            key=_keys("quick_view_inventaire"),
            use_container_width=True,
            help="Consulter et mettre à jour les stocks",
        ):
            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            rerun()

    with col4:
        if st.button(
            "👨‍👩‍👦 Planning Jules",
            key=_keys("quick_view_planning"),
            use_container_width=True,
            help="Planning des repas et activités de la semaine",
        ):
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            rerun()
