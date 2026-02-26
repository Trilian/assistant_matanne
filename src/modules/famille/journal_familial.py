"""
Journal Familial IA – Journal automatique enrichi par l'IA.

Onglets:
  1. Résumé de la semaine (généré par IA)
  2. Rétrospective mensuelle
  3. Ajouter une anecdote
"""

from __future__ import annotations

import logging
from datetime import date

import streamlit as st

from src.core.async_utils import executer_async
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.components.atoms import etat_vide
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

logger = logging.getLogger(__name__)
_keys = KeyNamespace("journal_familial")

_service_ia = None


def _get_service_ia():
    global _service_ia
    if _service_ia is None:
        from src.services.famille.journal_ia import obtenir_service_journal_ia

        _service_ia = obtenir_service_journal_ia()
    return _service_ia


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – RÉSUMÉ SEMAINE
# ═══════════════════════════════════════════════════════════


def _onglet_resume_semaine():
    """Résumé hebdomadaire généré par IA."""
    st.subheader("📝 Résumé de la Semaine")

    if st.button(
        "✨ Générer le résumé IA",
        type="primary",
        key=_keys("gen_resume"),
        use_container_width=True,
    ):
        try:
            svc = _get_service_ia()
            with st.spinner("✨ L'IA rédige votre résumé hebdomadaire..."):
                resume = executer_async(
                    svc.generer_resume_semaine(
                        evenements=["Semaine courante"],
                    )
                )

            if resume:
                st.session_state[_keys("resume_semaine")] = resume
            else:
                st.warning("Pas assez de données pour générer un résumé.")
        except Exception as e:
            logger.error("Erreur résumé semaine: %s", e)
            st.error(f"Erreur IA : {e}")

    resume = st.session_state.get(_keys("resume_semaine"))
    if resume:
        st.markdown("---")
        if isinstance(resume, dict):
            st.markdown(f"### 📅 Semaine du {resume.get('periode', '?')}")
            st.markdown(resume.get("resume", ""))

            if resume.get("moments_forts"):
                st.markdown("#### ⭐ Moments forts")
                for m in resume["moments_forts"]:
                    st.write(f"• {m}")

            if resume.get("progres_jules"):
                st.markdown("#### 👶 Progrès de Jules")
                st.write(resume["progres_jules"])

            if resume.get("suggestion_semaine_prochaine"):
                st.markdown("#### 💡 Suggestion pour la semaine prochaine")
                st.info(resume["suggestion_semaine_prochaine"])
        else:
            st.markdown(str(resume))
    else:
        etat_vide("Cliquez sur le bouton pour générer le résumé IA", icone="📝")


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – RÉTROSPECTIVE MENSUELLE
# ═══════════════════════════════════════════════════════════


def _onglet_retrospective():
    """Rétrospective mensuelle IA."""
    st.subheader("🗓️ Rétrospective Mensuelle")

    col1, col2 = st.columns([2, 1])
    with col1:
        mois = st.selectbox(
            "Mois",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: [
                "Janvier",
                "Février",
                "Mars",
                "Avril",
                "Mai",
                "Juin",
                "Juillet",
                "Août",
                "Septembre",
                "Octobre",
                "Novembre",
                "Décembre",
            ][m - 1],
            key=_keys("retro_mois"),
        )
    with col2:
        annee = st.number_input(
            "Année",
            min_value=2024,
            max_value=2030,
            value=date.today().year,
            key=_keys("retro_annee"),
        )

    if st.button(
        "✨ Générer la rétrospective",
        type="primary",
        key=_keys("gen_retro"),
        use_container_width=True,
    ):
        try:
            svc = _get_service_ia()
            with st.spinner("✨ L'IA compile votre mois..."):
                retro = executer_async(
                    svc.generer_retrospective_mensuelle(
                        annee=annee,
                        mois=mois,
                    )
                )

            if retro:
                st.session_state[_keys("retrospective")] = retro
            else:
                st.warning("Pas assez de données pour ce mois.")
        except Exception as e:
            logger.error("Erreur rétrospective: %s", e)
            st.error(f"Erreur IA : {e}")

    retro = st.session_state.get(_keys("retrospective"))
    if retro:
        st.markdown("---")
        if isinstance(retro, dict):
            st.markdown(f"### 📊 Bilan de {retro.get('periode', '?')}")

            if retro.get("statistiques"):
                stats = retro["statistiques"]
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Événements", stats.get("nb_evenements", 0))
                with col2:
                    st.metric("Souvenirs", stats.get("nb_souvenirs", 0))
                with col3:
                    st.metric("RDV médicaux", stats.get("nb_rdv", 0))
                with col4:
                    st.metric("Activités", stats.get("nb_activites", 0))

            st.markdown(retro.get("resume", ""))

            if retro.get("temps_forts"):
                st.markdown("#### 🌟 Temps forts du mois")
                for tf in retro["temps_forts"]:
                    st.write(f"⭐ {tf}")
        else:
            st.markdown(str(retro))
    else:
        etat_vide("Sélectionnez un mois et générez la rétrospective", icone="🗓️")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – ANECDOTES
# ═══════════════════════════════════════════════════════════


def _onglet_anecdotes():
    """Ajouter et embellir des anecdotes familiales."""
    st.subheader("✍️ Anecdotes Familiales")

    with st.form(_keys("form_anecdote")):
        anecdote = st.text_area(
            "Racontez un moment familial...",
            height=150,
            placeholder="Aujourd'hui Jules a fait ses premiers pas au parc...",
            key=_keys("anecdote_texte"),
        )
        col1, col2 = st.columns(2)
        with col1:
            date_anecdote = st.date_input("Date", value=date.today(), key=_keys("anecdote_date"))
        with col2:
            embellir = st.checkbox("✨ Embellir par l'IA", value=True, key=_keys("embellir"))

        submitted = st.form_submit_button("💾 Enregistrer", type="primary")

    if submitted and anecdote:
        texte_final = anecdote

        if embellir:
            try:
                svc = _get_service_ia()
                with st.spinner("✨ L'IA embellit votre anecdote..."):
                    texte_final = executer_async(svc.mettre_en_forme_anecdote(texte_brut=anecdote))
            except Exception as e:
                logger.error("Erreur embellissement: %s", e)
                st.warning("L'IA n'a pas pu embellir l'anecdote, version originale conservée.")

        anecdotes = st.session_state.get(_keys("anecdotes"), [])
        anecdotes.append(
            {
                "texte": texte_final,
                "texte_original": anecdote,
                "date": str(date_anecdote),
                "embelli": embellir,
            }
        )
        st.session_state[_keys("anecdotes")] = anecdotes
        st.success("✅ Anecdote enregistrée !")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📖 Vos anecdotes")

    anecdotes = st.session_state.get(_keys("anecdotes"), [])
    if not anecdotes:
        etat_vide("Racontez votre première anecdote !", icone="✍️")
    else:
        for i, a in enumerate(reversed(anecdotes)):
            with st.container(border=True):
                st.markdown(f"📅 **{a.get('date', '?')}**")
                st.write(a.get("texte", ""))
                if a.get("embelli") and a.get("texte_original") != a.get("texte"):
                    with st.expander("📝 Version originale"):
                        st.write(a["texte_original"])


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("journal_familial")
def app():
    """Point d'entrée Journal Familial IA."""
    st.title("📖 Journal Familial IA")
    st.caption("Votre vie de famille racontée et enrichie par l'IA")

    with error_boundary(titre="Erreur journal familial"):
        TAB_LABELS = ["📝 Résumé semaine", "🗓️ Rétrospective", "✍️ Anecdotes"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_resume_semaine()
        with tabs[1]:
            _onglet_retrospective()
        with tabs[2]:
            _onglet_anecdotes()
