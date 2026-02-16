"""Tab Dashboard Temps - Statistiques du temps d'entretien."""

from datetime import date, timedelta

import streamlit as st
from sqlalchemy import extract, func

from src.core.database import obtenir_contexte_db


def tab_temps():
    """Affiche le dashboard temps passé."""
    try:
        from src.core.models import SessionTravail
        from src.ui.maison.temps_ui import dashboard_temps

        today = date.today()
        debut_semaine = today - timedelta(days=today.weekday())

        with obtenir_contexte_db() as db:
            sessions_semaine = (
                db.query(SessionTravail)
                .filter(
                    SessionTravail.debut >= debut_semaine,
                    SessionTravail.fin.isnot(None),
                )
                .all()
            )

            temps_jardin = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite
                in ["arrosage", "tonte", "taille", "desherbage", "plantation", "recolte"]
            )
            temps_menage = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite
                in ["menage_general", "aspirateur", "lavage_sol", "poussiere", "vitres", "lessive"]
            )
            temps_bricolage = sum(
                s.duree_minutes or 0
                for s in sessions_semaine
                if s.type_activite in ["bricolage", "peinture", "plomberie", "electricite"]
            )
            temps_total = sum(s.duree_minutes or 0 for s in sessions_semaine)

            resume_semaine = {
                "temps_total_minutes": temps_total,
                "temps_jardin_minutes": temps_jardin,
                "temps_menage_minutes": temps_menage,
                "temps_bricolage_minutes": temps_bricolage,
            }

            stats_par_activite = (
                db.query(
                    SessionTravail.type_activite,
                    func.count(SessionTravail.id).label("nb_sessions"),
                    func.sum(SessionTravail.duree_minutes).label("total_minutes"),
                )
                .filter(
                    SessionTravail.debut >= debut_semaine,
                    SessionTravail.fin.isnot(None),
                )
                .group_by(SessionTravail.type_activite)
                .all()
            )

            stats_activites = [
                {
                    "type_activite": stat.type_activite,
                    "nb_sessions": stat.nb_sessions,
                    "total_minutes": stat.total_minutes or 0,
                }
                for stat in stats_par_activite
            ]

        dashboard_temps(
            resume_semaine=resume_semaine,
            stats_activites=stats_activites,
        )

    except ImportError:
        st.warning("Module Dashboard Temps non disponible")
        _afficher_fallback_temps()
    except Exception as e:
        st.error(f"Erreur dashboard: {e}")
        _afficher_fallback_temps()


def _afficher_fallback_temps():
    """Dashboard temps simplifié."""
    st.subheader("📊 Temps d'Entretien")

    try:
        from src.core.models import SessionTravail

        today = date.today()

        with obtenir_contexte_db() as db:
            stats_mois = (
                db.query(
                    SessionTravail.type_activite,
                    func.count(SessionTravail.id).label("nb_sessions"),
                    func.sum(SessionTravail.duree_minutes).label("total_minutes"),
                )
                .filter(
                    extract("month", SessionTravail.debut) == today.month,
                    extract("year", SessionTravail.debut) == today.year,
                    SessionTravail.fin.isnot(None),
                )
                .group_by(SessionTravail.type_activite)
                .all()
            )

        if not stats_mois:
            st.info("Aucune session enregistrée ce mois.")
            return

        total_heures = 0
        for stat in stats_mois:
            heures = (stat.total_minutes or 0) / 60
            total_heures += heures

            st.markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    padding: 0.8rem 1rem;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin-bottom: 0.5rem;
                ">
                    <span><strong>{stat.type_activite}</strong></span>
                    <span>{stat.nb_sessions} sessions • {heures:.1f}h</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.metric("**Total du mois**", f"{total_heures:.1f} heures")

    except Exception as e:
        st.error(f"Erreur chargement stats: {e}")
