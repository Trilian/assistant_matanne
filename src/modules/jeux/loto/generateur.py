"""
Module Loto - Génération et gestion des grilles
"""

import streamlit as st

from src.ui import etat_vide
from src.ui.fragments import ui_fragment

from .constants import CHANCE_MAX, CHANCE_MIN, NUMERO_MAX, NUMERO_MIN
from .crud import enregistrer_grille
from .frequences import analyser_patterns_tirages, calculer_frequences_numeros
from .generation import (
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)
from .utils import charger_grilles_utilisateur


@ui_fragment
def afficher_generateur_grilles(tirages: list):
    """Interface de génération de grilles"""

    st.markdown("### 🎲 Générer une grille")

    # Préparer les données si disponibles
    freq_data = calculer_frequences_numeros(tirages) if tirages else {}
    patterns = analyser_patterns_tirages(tirages) if tirages else {}

    col1, col2 = st.columns([1, 1])

    with col1:
        strategie = st.selectbox(
            "Stratégie de génération",
            [
                ("🎲 Aléatoire", "aleatoire"),
                ("🧠 Éviter populaires (32-49)", "eviter_populaires"),
                ("⚖️ Équilibrée (somme moyenne)", "equilibree"),
                ("🔥 Numéros chauds", "chauds"),
                ("❄️ Numéros froids", "froids"),
                ("🔄 Mixte (chauds + froids)", "mixte"),
                ("✏️ Manuelle", "manuel"),
            ],
            format_func=lambda x: x[0],
        )

    grille_generee = None

    if strategie[1] == "manuel":
        with col2:
            st.markdown("**Choisissez vos numéros:**")

        # Sélection manuelle
        numeros_selectionnes = st.multiselect(
            "5 numéros (1-49)", list(range(NUMERO_MIN, NUMERO_MAX + 1)), max_selections=5
        )

        chance = st.selectbox("Numéro Chance (1-10)", list(range(CHANCE_MIN, CHANCE_MAX + 1)))

        if len(numeros_selectionnes) == 5:
            grille_generee = {
                "numeros": sorted(numeros_selectionnes),
                "numero_chance": chance,
                "source": "manuel",
            }
    else:
        with col2:
            if st.button("🎲 Générer!", type="primary", width="stretch"):
                if strategie[1] == "aleatoire":
                    grille_generee = generer_grille_aleatoire()
                elif strategie[1] == "eviter_populaires":
                    grille_generee = generer_grille_eviter_populaires()
                elif strategie[1] == "equilibree":
                    grille_generee = generer_grille_equilibree(patterns)
                elif strategie[1] in ["chauds", "froids", "mixte"]:
                    grille_generee = generer_grille_chauds_froids(
                        freq_data.get("frequences", {}), strategie[1]
                    )

    # Afficher la grille générée
    if grille_generee:
        from src.ui import boule_loto

        st.divider()
        st.markdown("### ⏰ Votre grille")

        with st.container(border=True):
            cols = st.columns(6)
            for i, num in enumerate(grille_generee["numeros"]):
                with cols[i]:
                    boule_loto(num, taille=60)

            with cols[5]:
                boule_loto(grille_generee["numero_chance"], is_chance=True, taille=60)

            if grille_generee.get("note"):
                st.caption(grille_generee["note"])

            # Bouton enregistrer
            col_save, col_empty = st.columns([1, 2])
            with col_save:
                if st.button("💾 Enregistrer (virtuel)", width="stretch"):
                    enregistrer_grille(
                        grille_generee["numeros"],
                        grille_generee["numero_chance"],
                        source=grille_generee.get("source", "ia"),
                        est_virtuelle=True,
                    )
                    rerun()


@ui_fragment
def afficher_mes_grilles():
    """Affiche les grilles de l'utilisateur"""
    grilles = charger_grilles_utilisateur()

    if not grilles:
        etat_vide("Aucune grille enregistrée", "🎫", "Générez-en une !")
        return

    # Stats globales
    total_mise = sum(float(g.get("mise", 0)) for g in grilles)
    total_gain = sum(float(g.get("gain", 0) or 0) for g in grilles if g.get("gain"))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎫 Grilles jouées", len(grilles))
    with col2:
        st.metric("💸 Total misé", f"{total_mise:.2f}€")
    with col3:
        st.metric("💰 Total gagné", f"{total_gain:.2f}€")
    with col4:
        profit = total_gain - total_mise
        st.metric(
            "📝ˆ Bilan", f"{profit:+.2f}€", delta_color="normal" if profit >= 0 else "inverse"
        )

    st.divider()

    # Liste des grilles
    for grille in grilles[:20]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"🎫 {grille['numeros_str']}")
                st.caption(f"Source: {grille['source']} | {grille['date'].strftime('%d/%m/%Y')}")

            with col2:
                if grille.get("rang"):
                    st.success(f"🏆 Rang {grille['rang']}")
                    st.write(f"+{grille['gain']:.2f}€")
                elif grille.get("tirage_id"):
                    st.error("❌ Perdu")
                else:
                    st.warning("⏳ En attente")

            with col3:
                if grille.get("numeros_trouves") is not None:
                    st.write(f"✅ {grille['numeros_trouves']}/5")
                    if grille.get("chance_trouvee"):
                        st.write("+ Chance ✓")
