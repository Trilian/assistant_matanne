"""Tab Chronomètre - Suivi du temps d'entretien."""

from datetime import datetime

import streamlit as st

from src.core.database import obtenir_contexte_db


def tab_chrono():
    """Affiche le chronomètre d'entretien."""
    try:
        from src.core.models import SessionTravail
        from src.ui.maison.temps_ui import chronometre_widget

        session_active = None
        with obtenir_contexte_db() as db:
            session_en_cours = (
                db.query(SessionTravail)
                .filter(SessionTravail.fin.is_(None))
                .order_by(SessionTravail.debut.desc())
                .first()
            )
            if session_en_cours:
                session_active = {
                    "id": session_en_cours.id,
                    "type_activite": session_en_cours.type_activite,
                    "debut": session_en_cours.debut,
                }

        def on_start(type_activite: str):
            """Callback démarrage session."""
            with obtenir_contexte_db() as db:
                nouvelle_session = SessionTravail(
                    type_activite=type_activite,
                    debut=datetime.now(),
                )
                db.add(nouvelle_session)
                db.commit()
            st.rerun()

        def on_stop(session_id: int):
            """Callback arrêt session."""
            with obtenir_contexte_db() as db:
                session = db.query(SessionTravail).filter(SessionTravail.id == session_id).first()
                if session:
                    session.fin = datetime.now()
                    duree = session.fin - session.debut
                    session.duree_minutes = int(duree.total_seconds() / 60)
                    db.commit()
            st.success("Session terminée!")
            st.rerun()

        def on_cancel(session_id: int):
            """Callback annulation session."""
            with obtenir_contexte_db() as db:
                db.query(SessionTravail).filter(SessionTravail.id == session_id).delete()
                db.commit()
            st.info("Session annulée")
            st.rerun()

        chronometre_widget(
            session_active=session_active,
            on_start=on_start,
            on_stop=on_stop,
            on_cancel=on_cancel,
        )

    except ImportError:
        st.warning("Module Chronomètre non disponible")
        _afficher_fallback_chrono()
    except Exception as e:
        st.error(f"Erreur chronomètre: {e}")
        _afficher_fallback_chrono()


def _afficher_fallback_chrono():
    """Chronomètre simplifié."""
    st.subheader("⏱️ Chronomètre Entretien")

    if "chrono_debut" not in st.session_state:
        st.session_state.chrono_debut = None
        st.session_state.chrono_type = None

    types_activite = [
        "Ménage général",
        "Aspirateur",
        "Tonte",
        "Arrosage",
        "Taille",
        "Bricolage",
        "Autre",
    ]

    col1, col2 = st.columns([2, 1])

    with col1:
        type_activite = st.selectbox(
            "Type d'activité",
            types_activite,
            key="chrono_type_select",
            disabled=st.session_state.chrono_debut is not None,
        )

    with col2:
        if st.session_state.chrono_debut is None:
            if st.button("▶️ Démarrer", type="primary", use_container_width=True):
                st.session_state.chrono_debut = datetime.now()
                st.session_state.chrono_type = type_activite
                st.rerun()
        else:
            if st.button("⏹️ Arrêter", type="secondary", use_container_width=True):
                duree = datetime.now() - st.session_state.chrono_debut
                minutes = int(duree.total_seconds() / 60)
                st.success(f"Session terminée : {minutes} minutes")

                _enregistrer_session(
                    st.session_state.chrono_type,
                    st.session_state.chrono_debut,
                    datetime.now(),
                    minutes,
                )

                st.session_state.chrono_debut = None
                st.session_state.chrono_type = None
                st.rerun()

    if st.session_state.chrono_debut:
        duree = datetime.now() - st.session_state.chrono_debut
        minutes = int(duree.total_seconds() / 60)
        secondes = int(duree.total_seconds() % 60)

        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #27ae60, #2ecc71);
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                margin: 1rem 0;
            ">
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    En cours : {st.session_state.chrono_type}
                </div>
                <div style="font-size: 3rem; font-weight: bold;">
                    {minutes:02d}:{secondes:02d}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _enregistrer_session(type_activite: str, debut, fin, duree_minutes: int):
    """Enregistre une session de travail en BD."""
    try:
        from src.core.models import SessionTravail

        with obtenir_contexte_db() as db:
            session = SessionTravail(
                type_activite=type_activite.lower().replace(" ", "_"),
                debut=debut,
                fin=fin,
                duree_minutes=duree_minutes,
            )
            db.add(session)
            db.commit()
    except Exception as e:
        st.error(f"Erreur enregistrement: {e}")
