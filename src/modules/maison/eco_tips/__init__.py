"""
Module Éco-Tips - Conseils écologiques pour la maison.

Conseils éco-gestes, astuces économies d'énergie et alternatives durables
avec suggestions IA personnalisées selon le profil du foyer.
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = ["app"]

_keys = KeyNamespace("eco_tips")

# ═══════════════════════════════════════════════════════════
# DONNÉES STATIQUES
# ═══════════════════════════════════════════════════════════

ECO_TIPS_DATA = {
    "🔌 Énergie": [
        {"tip": "Baisser le chauffage de 1°C = 7% d'économies", "impact": "haute", "difficulte": "facile"},
        {"tip": "Éteindre les appareils en veille = 10% d'économies", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Utiliser des multiprises à interrupteur", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Privilégier les LED (80% moins gourmandes)", "impact": "haute", "difficulte": "facile"},
        {"tip": "Programmer le chauffage (17°C la nuit, 19°C le jour)", "impact": "haute", "difficulte": "moyen"},
        {"tip": "Installer un thermostat connecté", "impact": "haute", "difficulte": "moyen"},
    ],
    "💧 Eau": [
        {"tip": "Douche de 5 min max = 60L vs 150L pour un bain", "impact": "haute", "difficulte": "facile"},
        {"tip": "Installer des mousseurs (40% d'économie d'eau)", "impact": "haute", "difficulte": "facile"},
        {"tip": "Récupérer l'eau de pluie pour le jardin", "impact": "moyenne", "difficulte": "moyen"},
        {"tip": "Lancer le lave-vaisselle uniquement plein", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Réparer les fuites (10L/jour pour un robinet)", "impact": "haute", "difficulte": "moyen"},
    ],
    "🍽️ Cuisine": [
        {"tip": "Couvrir les casseroles (4x plus rapide)", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Décongeler au frigo plutôt qu'au micro-ondes", "impact": "basse", "difficulte": "facile"},
        {"tip": "Utiliser une bouilloire vs casserole pour l'eau", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Batch cooking = moins de cuissons par semaine", "impact": "moyenne", "difficulte": "moyen"},
        {"tip": "Composter les déchets organiques", "impact": "haute", "difficulte": "moyen"},
    ],
    "♻️ Déchets": [
        {"tip": "Privilégier les produits en vrac", "impact": "haute", "difficulte": "moyen"},
        {"tip": "Utiliser des sacs réutilisables", "impact": "moyenne", "difficulte": "facile"},
        {"tip": "Faire ses produits ménagers (vinaigre + bicarbonate)", "impact": "moyenne", "difficulte": "moyen"},
        {"tip": "Donner/vendre plutôt que jeter (Leboncoin, Vinted)", "impact": "haute", "difficulte": "facile"},
        {"tip": "Trier rigoureusement (verre, plastique, papier, bio)", "impact": "haute", "difficulte": "facile"},
    ],
    "🌿 Jardin": [
        {"tip": "Arroser tôt le matin ou tard le soir", "impact": "haute", "difficulte": "facile"},
        {"tip": "Pailler pour conserver l'humidité", "impact": "haute", "difficulte": "facile"},
        {"tip": "Planter des espèces locales résistantes", "impact": "moyenne", "difficulte": "moyen"},
        {"tip": "Installer un récupérateur d'eau de pluie", "impact": "haute", "difficulte": "moyen"},
    ],
}

IMPACT_COLORS = {
    "haute": "#2e7d32",
    "moyenne": "#e65100",
    "basse": "#616161",
}


@profiler_rerun("eco_tips")
def app():
    """Point d'entrée du module Éco-Tips."""
    st.title("🌍 Éco-Tips Maison")
    st.caption("Adoptez des gestes simples pour réduire votre impact et vos factures.")

    TAB_LABELS = [
        "🏠 Tous les tips",
        "📊 Mon éco-score",
        "🤖 Conseils IA",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tab1, tab2, tab3 = st.tabs(TAB_LABELS)

    with tab1:
        with error_boundary(titre="Erreur éco-tips"):
            _onglet_tips()

    with tab2:
        with error_boundary(titre="Erreur éco-score"):
            _onglet_eco_score()

    with tab3:
        with error_boundary(titre="Erreur conseils IA"):
            _onglet_conseils_ia()


def _onglet_tips():
    """Affiche tous les éco-tips par catégorie."""
    # Filtre de difficulté
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
                        f'{tip["impact"]}</span>',
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.caption(tip["difficulte"])


def _onglet_eco_score():
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


def _onglet_conseils_ia():
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
