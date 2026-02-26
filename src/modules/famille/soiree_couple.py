"""
Soirée Couple – Suggestions IA pour sorties et soirées romantiques.

Onglets:
  1. Suggestions IA (sortie / maison)
  2. Historique des soirées
  3. Budget soirées
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
_keys = KeyNamespace("soiree_couple")

_service_ai = None


def _get_service_ai():
    global _service_ai
    if _service_ai is None:
        from src.services.famille.soiree_ai import obtenir_service_soiree_ai

        _service_ai = obtenir_service_soiree_ai()
    return _service_ai


# ═══════════════════════════════════════════════════════════
# ONGLET 1 – SUGGESTIONS IA
# ═══════════════════════════════════════════════════════════


def _onglet_suggestions():
    """Suggestions IA de soirées."""
    st.subheader("💡 Suggestions IA pour votre soirée")

    col1, col2 = st.columns(2)

    with col1:
        type_soiree = st.radio(
            "Type de soirée",
            ["🍷 Sortie", "🏠 Maison"],
            key=_keys("type_soiree"),
            horizontal=True,
        )

    with col2:
        budget = st.slider(
            "Budget max (€)", min_value=0, max_value=200, value=50, step=10, key=_keys("budget")
        )

    # Préférences
    with st.expander("⚙️ Préférences", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            ambiance = st.selectbox(
                "Ambiance souhaitée",
                ["Romantique", "Fun", "Détendue", "Aventureuse", "Culturelle"],
                key=_keys("ambiance"),
            )
            garde_dispo = st.checkbox("Garde d'enfant disponible", value=True, key=_keys("garde"))
        with col2:
            duree = st.selectbox(
                "Durée",
                ["1-2h", "2-3h", "Soirée entière", "Nuit complète"],
                key=_keys("duree"),
            )
            restrictions = st.text_input("Restrictions / allergies", key=_keys("restrictions"))

    est_sortie = "Sortie" in type_soiree

    if st.button(
        "✨ Générer des suggestions", type="primary", key=_keys("generer"), use_container_width=True
    ):
        try:
            svc = _get_service_ai()
            contexte = {
                "type": "sortie" if est_sortie else "maison",
                "budget": budget,
                "ambiance": ambiance,
                "duree": duree,
                "garde_disponible": garde_dispo,
                "restrictions": restrictions or None,
            }

            with st.spinner("✨ L'IA prépare vos suggestions..."):
                if est_sortie:
                    suggestions = executer_async(
                        svc.suggerer_soirees(
                            budget=budget,
                            type_soiree=ambiance.lower(),
                        )
                    )
                else:
                    suggestions = executer_async(
                        svc.planifier_soiree_maison(
                            theme=ambiance.lower(),
                            budget=budget,
                        )
                    )

            if suggestions:
                st.session_state[_keys("suggestions")] = suggestions
            else:
                st.warning("Pas de suggestions pour ces critères.")

        except Exception as e:
            logger.error("Erreur suggestions soirée: %s", e)
            st.error(f"Erreur IA : {e}")

    # Afficher les suggestions
    suggestions = st.session_state.get(_keys("suggestions"), [])
    if suggestions:
        st.markdown("---")
        st.markdown("### 🌟 Vos suggestions")

        if isinstance(suggestions, list):
            for i, s in enumerate(suggestions):
                with st.container(border=True):
                    if isinstance(s, dict):
                        st.markdown(f"**{s.get('titre', f'Suggestion {i+1}')}**")
                        st.write(s.get("description", ""))
                        col1, col2 = st.columns(2)
                        with col1:
                            if s.get("budget_estime"):
                                st.metric("Budget estimé", f"{s['budget_estime']}€")
                        with col2:
                            if s.get("duree_estimee"):
                                st.metric("Durée", s["duree_estimee"])
                    else:
                        st.write(str(s))
        elif isinstance(suggestions, str):
            st.markdown(suggestions)


# ═══════════════════════════════════════════════════════════
# ONGLET 2 – HISTORIQUE
# ═══════════════════════════════════════════════════════════


def _onglet_historique():
    """Historique des soirées passées."""
    st.subheader("📜 Historique des soirées")

    # Formulaire d'ajout
    with st.expander("➕ Enregistrer une soirée passée", expanded=False):
        with st.form(_keys("form_soiree")):
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Titre", key=_keys("s_titre"))
                date_soiree = st.date_input("Date", value=date.today(), key=_keys("s_date"))
                type_s = st.selectbox(
                    "Type",
                    ["Sortie restaurant", "Cinéma", "Théâtre", "Soirée maison", "Balade", "Autre"],
                    key=_keys("s_type"),
                )
            with col2:
                note = st.slider("Note (1-5)", 1, 5, 4, key=_keys("s_note"))
                cout = st.number_input("Coût (€)", min_value=0.0, step=5.0, key=_keys("s_cout"))

            commentaire = st.text_area("Commentaire", key=_keys("s_comment"))

            if st.form_submit_button("💾 Enregistrer", type="primary"):
                soiree = {
                    "titre": titre,
                    "date": str(date_soiree),
                    "type": type_s,
                    "note": note,
                    "cout": cout,
                    "commentaire": commentaire,
                }
                historique = st.session_state.get(_keys("historique"), [])
                historique.append(soiree)
                st.session_state[_keys("historique")] = historique
                st.success("✅ Soirée enregistrée !")
                st.rerun()

    # Affichage historique
    historique = st.session_state.get(_keys("historique"), [])
    if not historique:
        etat_vide("Aucune soirée enregistrée", icone="📜")
    else:
        for s in reversed(historique):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{s.get('titre', '?')}** — {s.get('type', '')}")
                    st.caption(f"📅 {s.get('date', '')} • {s.get('commentaire', '')}")
                with col2:
                    st.metric("Note", f"{'⭐' * s.get('note', 0)}")
                    if s.get("cout"):
                        st.caption(f"💰 {s['cout']}€")


# ═══════════════════════════════════════════════════════════
# ONGLET 3 – BUDGET
# ═══════════════════════════════════════════════════════════


def _onglet_budget():
    """Suivi budget soirées couple."""
    st.subheader("💰 Budget Soirées Couple")

    historique = st.session_state.get(_keys("historique"), [])

    if not historique:
        etat_vide("Enregistrez des soirées pour voir le budget", icone="💰")
        return

    total = sum(s.get("cout", 0) for s in historique)
    nb_soirees = len(historique)
    moyenne = total / nb_soirees if nb_soirees > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total dépensé", f"{total:.0f}€")
    with col2:
        st.metric("Nb soirées", str(nb_soirees))
    with col3:
        st.metric("Moyenne / soirée", f"{moyenne:.0f}€")

    # Budget mensuel
    st.markdown("---")
    budget_mensuel = st.number_input(
        "Budget mensuel soirées (€)",
        min_value=0,
        value=150,
        step=25,
        key=_keys("budget_mensuel"),
    )

    mois_courant = [s for s in historique if s.get("date", "").startswith(str(date.today())[:7])]
    depense_mois = sum(s.get("cout", 0) for s in mois_courant)
    reste = budget_mensuel - depense_mois

    st.progress(min(depense_mois / max(budget_mensuel, 1), 1.0))
    if reste >= 0:
        st.success(f"✅ Reste {reste:.0f}€ ce mois-ci")
    else:
        st.warning(f"⚠️ Budget dépassé de {abs(reste):.0f}€")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


@profiler_rerun("soiree_couple")
def app():
    """Point d'entrée Soirée Couple."""
    st.title("💕 Soirée Couple")
    st.caption("Suggestions IA pour vos moments à deux")

    with error_boundary(titre="Erreur soirée couple"):
        TAB_LABELS = ["✨ Suggestions IA", "📜 Historique", "💰 Budget"]
        _tab_index = tabs_with_url(TAB_LABELS, param="tab")

        tabs = st.tabs(TAB_LABELS)
        with tabs[0]:
            _onglet_suggestions()
        with tabs[1]:
            _onglet_historique()
        with tabs[2]:
            _onglet_budget()
