"""
Composants UI pour le module Éco-Tips.
"""

from datetime import date as date_type
from decimal import Decimal

import streamlit as st

from src.core.state import rerun
from src.ui.keys import KeyNamespace

from .constants import ECO_TIPS_DATA, IDEES_ACTIONS, IMPACT_COLORS, TYPE_LABELS
from .crud import create_action, delete_action, get_all_actions, update_action
from .stats import calculate_stats

_keys = KeyNamespace("eco_tips")


def afficher_stats_dashboard() -> None:
    """Affiche le dashboard de statistiques des éco-actions."""
    st.subheader("📊 Vos économies")
    stats = calculate_stats()
    cols = st.columns(4)
    with cols[0]:
        st.metric("Actions actives", stats["nb_actions"])
    with cols[1]:
        st.metric("Économie/mois", f"{stats['economie_mensuelle']:.0f}€")
    with cols[2]:
        st.metric("Économie/an", f"{stats['economie_annuelle']:.0f}€")
    with cols[3]:
        st.metric("ROI", f"{stats['roi_mois']:.1f} mois")


def afficher_action_card(action) -> None:
    """Affiche une carte pour une action écologique.

    Args:
        action: Objet ActionEcologique.
    """
    type_label = TYPE_LABELS.get(getattr(action, "type_action", ""), "")
    with st.container(border=True):
        cols = st.columns(3)
        with cols[0]:
            st.markdown(f"**{action.nom}**")
            st.caption(type_label)
        with cols[1]:
            eco = getattr(action, "economie_mensuelle", None)
            st.metric("Économie/mois", f"{float(eco):.0f}€" if eco else "—")
        with cols[2]:
            actif = getattr(action, "actif", True)
            new_actif = st.checkbox("Actif", value=actif, key=f"actif_{action.id}")
            if new_actif != actif:
                update_action(action.id, {"actif": new_actif})

        cols2 = st.columns(2)
        with cols2[0]:
            if st.button("✏️ Modifier", key=f"edit_{action.id}"):
                st.session_state[_keys("edit_id")] = action.id
                rerun()
        with cols2[1]:
            if st.button("🗑️ Supprimer", key=f"del_{action.id}"):
                delete_action(action.id)
                rerun()


def afficher_formulaire(action=None) -> None:
    """Affiche le formulaire de création/édition d'une action.

    Args:
        action: Objet ActionEcologique existant pour édition, ou None pour création.
    """
    with st.form(key=_keys("form_action")):
        nom = st.text_input("Nom", value=getattr(action, "nom", ""))
        type_action = st.selectbox(
            "Type",
            list(TYPE_LABELS.keys()),
            format_func=lambda x: TYPE_LABELS[x],
            index=list(TYPE_LABELS.keys()).index(getattr(action, "type_action", "lavable"))
            if action and hasattr(action, "type_action")
            else 0,
        )
        description = st.text_area("Description", value=getattr(action, "description", ""))
        eco = st.number_input(
            "Économie mensuelle (€)",
            min_value=0.0,
            value=float(getattr(action, "economie_mensuelle", 0) or 0),
        )
        cout = st.number_input(
            "Coût initial (€)",
            min_value=0.0,
            value=float(getattr(action, "cout_nouveau_initial", 0) or 0),
        )

        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted and nom:
        data = {
            "nom": nom,
            "type_action": type_action,
            "description": description,
            "economie_mensuelle": Decimal(str(eco)),
            "cout_nouveau_initial": Decimal(str(cout)),
            "date_debut": date_type.today(),
            "actif": True,
        }
        if action:
            update_action(action.id, data)
            st.success("✅ Action mise à jour !")
        else:
            create_action(data)
            st.success("✅ Action créée !")
        rerun()


def afficher_idees() -> None:
    """Affiche les idées d'actions prédéfinies."""
    st.subheader("💡 Idées d'actions")
    existantes = get_all_actions()
    noms_existants = {a.nom for a in existantes} if existantes else set()

    cols = st.columns(3)
    for i, idee in enumerate(IDEES_ACTIONS):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{idee['nom']}**")
                st.caption(idee["description"])
                st.caption(f"💰 ~{idee['economie_estimee']:.0f}€/mois")
                if idee["nom"] not in noms_existants:
                    if st.button("➕ Adopter", key=f"adopt_{i}"):
                        create_action(
                            {
                                "nom": idee["nom"],
                                "type_action": idee["type"],
                                "description": idee["description"],
                                "economie_mensuelle": Decimal(str(idee["economie_estimee"])),
                                "cout_nouveau_initial": Decimal(str(idee["cout_nouveau_initial"])),
                                "actif": True,
                            }
                        )
                        rerun()
                else:
                    st.success("✅ Déjà adoptée")


def afficher_onglet_mes_actions() -> None:
    """Affiche l'onglet 'Mes actions'."""
    actions = get_all_actions()
    if not actions:
        st.info("Aucune action éco-responsable. Ajoutez-en une ou consultez les idées !")
        return

    filtre = st.radio("Filtrer", ["Toutes", "Actives", "Inactives"], horizontal=True)

    for action in actions:
        if filtre == "Actives" and not action.actif:
            continue
        if filtre == "Inactives" and action.actif:
            continue
        afficher_action_card(action)


def afficher_onglet_ajouter() -> None:
    """Affiche l'onglet 'Ajouter une action'."""
    st.subheader("➕ Nouvelle action")
    afficher_formulaire(None)


def afficher_onglet_tips() -> None:
    """Affiche tous les éco-tips par catégorie."""
    filtre = st.selectbox(
        "Filtrer par difficulté",
        ["Tous", "facile", "moyen"],
        key=_keys("filtre_difficulte"),
    )

    for categorie, tips in ECO_TIPS_DATA.items():
        with st.expander(f"{categorie} ({len(tips)} tips)", expanded=True):
            for tip in tips:
                if filtre != "Tous" and tip["difficulte"] != filtre:
                    continue

                impact_color = IMPACT_COLORS.get(tip["impact"], "#616161")
                col1, col2, col3 = st.columns([5, 1, 1])
                with col1:
                    st.markdown(f"• {tip['tip']}")
                with col2:
                    st.markdown(
                        f'<span style="color: {impact_color}; font-weight: 600; font-size: 0.8rem;">'
                        f"{tip['impact']}</span>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.caption(tip["difficulte"])


def afficher_onglet_eco_score() -> None:
    """Calcule un éco-score basé sur les habitudes du foyer."""
    st.subheader("📊 Votre éco-score")
    st.caption("Répondez à ces questions pour évaluer vos pratiques écologiques.")

    with st.form(key=_keys("form_eco_score")):
        score = 0

        st.markdown("**🔌 Énergie**")
        if st.checkbox("J'éteins les appareils en veille", key=_keys("veille")):
            score += 10
        if st.checkbox("J'utilise des LED", key=_keys("led")):
            score += 10
        if st.checkbox("Mon chauffage est programmé", key=_keys("chauffage")):
            score += 15

        st.markdown("**💧 Eau**")
        if st.checkbox("Douches courtes (< 5 min)", key=_keys("douche")):
            score += 10
        if st.checkbox("Mousseurs installés", key=_keys("mousseur")):
            score += 10

        st.markdown("**♻️ Déchets**")
        if st.checkbox("Je trie mes déchets", key=_keys("tri")):
            score += 10
        if st.checkbox("Je composte", key=_keys("compost")):
            score += 15
        if st.checkbox("J'achète en vrac", key=_keys("vrac")):
            score += 10

        st.markdown("**🍽️ Cuisine**")
        if st.checkbox("Je pratique le batch cooking", key=_keys("batch")):
            score += 10

        submitted = st.form_submit_button("📊 Calculer mon score", use_container_width=True)

    if submitted:
        st.divider()
        pct = score

        if pct >= 80:
            emoji, label, color = "🌟", "Excellent !", "#2e7d32"
        elif pct >= 60:
            emoji, label, color = "👍", "Bien !", "#1565c0"
        elif pct >= 40:
            emoji, label, color = "🔧", "Peut mieux faire", "#e65100"
        else:
            emoji, label, color = "⚠️", "À améliorer", "#c62828"

        st.markdown(
            f'<div style="text-align:center; padding:1.5rem; border-radius:10px; '
            f'background: linear-gradient(135deg, {color}22 0%, {color}11 100%);">'
            f'<h1 style="color: {color};">{emoji} {pct}/100</h1>'
            f'<p style="font-size: 1.2rem; color: {color};">{label}</p></div>',
            unsafe_allow_html=True,
        )

        if pct < 80:
            st.info("💡 Consultez l'onglet 'Tous les tips' pour découvrir de nouveaux éco-gestes !")


def afficher_onglet_conseils_ia() -> None:
    """Conseils personnalisés par l'IA."""
    st.subheader("🤖 Conseils IA personnalisés")
    st.caption("Décrivez votre situation pour recevoir des conseils adaptés.")

    situation = st.text_area(
        "Décrivez votre logement et vos habitudes",
        placeholder="ex: Appartement 60m², 2 personnes + 1 bébé, chauffage gaz, "
        "pas encore de compost, machine à laver tous les jours...",
        key=_keys("situation"),
    )

    if st.button("🤖 Obtenir des conseils", key=_keys("btn_conseils"), use_container_width=True):
        if not situation:
            st.warning("Veuillez décrire votre situation d'abord.")
            return

        try:
            from src.core.ai import obtenir_client_ia

            client = obtenir_client_ia()

            with st.spinner("🤖 Analyse de votre situation..."):
                import asyncio

                prompt = (
                    f"Analyse cette situation de foyer et donne 5-7 conseils écologiques "
                    f"concrets et personnalisés, classés par impact:\n\n{situation}\n\n"
                    f"Pour chaque conseil, indique l'économie potentielle en €/an."
                )

                response = asyncio.run(
                    client.generer(
                        prompt=prompt,
                        system_prompt="Tu es un expert en transition écologique et économies "
                        "d'énergie domestique en France.",
                        max_tokens=800,
                    )
                )

                st.markdown("---")
                st.markdown(response)

        except Exception as e:
            st.warning(f"Service IA indisponible: {e}")
            st.info("En attendant, consultez nos éco-tips dans l'onglet principal !")
