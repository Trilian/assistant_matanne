# src/ui/recette_components.py
"""
Composants UI Spécifiques aux Recettes
Widgets réutilisables pour le module recettes
"""
import streamlit as st
from typing import List, Dict, Optional, Callable


# ===================================
# MODE D'AFFICHAGE
# ===================================

def render_display_mode_toggle(key: str = "display_mode") -> str:
    """
    Toggle entre mode Liste et Grille

    Returns:
        "liste" ou "grille"
    """
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("📋 Liste", key=f"{key}_liste", use_container_width=True):
            st.session_state[key] = "liste"
            st.rerun()

    with col2:
        if st.button("🎴 Grille", key=f"{key}_grille", use_container_width=True):
            st.session_state[key] = "grille"
            st.rerun()

    return st.session_state.get(key, "liste")


# ===================================
# CARTE RECETTE GRILLE
# ===================================

def render_recipe_card_grid(recette: Dict, key: str, on_click: Callable):
    """
    Carte recette pour mode grille (compact)

    Args:
        recette: Dict recette
        key: Clé unique
        on_click: Callback au clic
    """
    with st.container():
        # Image
        if recette.get('url_image'):
            st.image(recette['url_image'], use_container_width=True)
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        height: 150px; border-radius: 8px; display: flex;
                        align-items: center; justify-content: center; color: white;
                        font-size: 3rem;'>
                🍽️
            </div>
            """, unsafe_allow_html=True)

        # Nom
        st.markdown(f"**{recette['nom']}**")

        # Badges compacts
        badges = []
        if recette.get('est_rapide'):
            badges.append("⚡")
        if recette.get('compatible_bebe'):
            badges.append("👶")
        if recette.get('genere_par_ia'):
            badges.append("🤖")

        if badges:
            st.caption(" ".join(badges))

        # Métadonnées
        st.caption(f"⏱️ {recette['temps_total']}min • {recette['difficulte']}")

        # Bouton
        if st.button("👁️ Voir", key=key, use_container_width=True):
            on_click()


# ===================================
# FORMULAIRE INGRÉDIENTS
# ===================================

def render_ingredients_form(
        initial_ingredients: Optional[List[Dict]] = None,
        key_prefix: str = "ing"
) -> List[Dict]:
    """
    Formulaire interactif pour gérer les ingrédients

    Returns:
        Liste d'ingrédients
    """
    # Initialiser session state
    session_key = f"{key_prefix}_list"
    if session_key not in st.session_state:
        st.session_state[session_key] = initial_ingredients or []

    st.markdown("### 🥕 Ingrédients")

    # Formulaire d'ajout
    with st.expander("➕ Ajouter un ingrédient", expanded=len(st.session_state[session_key]) == 0):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            nom = st.text_input("Nom", key=f"{key_prefix}_nom", placeholder="Ex: Tomates")
        with col2:
            qty = st.number_input("Quantité", 0.0, 10000.0, 1.0, 0.1, key=f"{key_prefix}_qty")
        with col3:
            unit = st.text_input("Unité", key=f"{key_prefix}_unit", value="g")
        with col4:
            opt = st.checkbox("Opt.", key=f"{key_prefix}_opt")

        if st.button("➕ Ajouter", key=f"{key_prefix}_add"):
            if nom:
                st.session_state[session_key].append({
                    "nom": nom,
                    "quantite": qty,
                    "unite": unit,
                    "optionnel": opt
                })
                st.rerun()

    # Liste des ingrédients
    if st.session_state[session_key]:
        for idx, ing in enumerate(st.session_state[session_key]):
            col1, col2, col3 = st.columns([4, 1, 1])

            with col1:
                optional_tag = " (optionnel)" if ing["optionnel"] else ""
                st.write(f"• {ing['quantite']} {ing['unite']} de {ing['nom']}{optional_tag}")

            with col2:
                if st.button("✏️", key=f"{key_prefix}_edit_{idx}"):
                    st.info("Édition inline à venir")

            with col3:
                if st.button("❌", key=f"{key_prefix}_del_{idx}"):
                    st.session_state[session_key].pop(idx)
                    st.rerun()
    else:
        st.info("Aucun ingrédient ajouté")

    return st.session_state[session_key]


# ===================================
# FORMULAIRE ÉTAPES
# ===================================

def render_etapes_form(
        initial_etapes: Optional[List[Dict]] = None,
        key_prefix: str = "step"
) -> List[Dict]:
    """
    Formulaire interactif pour gérer les étapes

    Returns:
        Liste d'étapes ordonnées
    """
    session_key = f"{key_prefix}_list"
    if session_key not in st.session_state:
        st.session_state[session_key] = initial_etapes or []

    st.markdown("### 📝 Étapes de Préparation")

    # Formulaire d'ajout
    with st.expander("➕ Ajouter une étape", expanded=len(st.session_state[session_key]) == 0):
        desc = st.text_area("Description", key=f"{key_prefix}_desc", height=100)
        duree = st.number_input("Durée (min) - optionnel", 0, 300, 0, 5, key=f"{key_prefix}_duree")

        if st.button("➕ Ajouter étape", key=f"{key_prefix}_add"):
            if desc:
                st.session_state[session_key].append({
                    "ordre": len(st.session_state[session_key]) + 1,
                    "description": desc,
                    "duree": duree if duree > 0 else None
                })
                st.rerun()

    # Liste des étapes
    if st.session_state[session_key]:
        for idx, etape in enumerate(st.session_state[session_key]):
            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                duree_str = f" ({etape['duree']}min)" if etape.get('duree') else ""
                st.write(f"**{etape['ordre']}.** {etape['description']}{duree_str}")

            with col2:
                # Monter/Descendre
                if idx > 0:
                    if st.button("⬆️", key=f"{key_prefix}_up_{idx}"):
                        st.session_state[session_key][idx], st.session_state[session_key][idx-1] = \
                            st.session_state[session_key][idx-1], st.session_state[session_key][idx]
                        # Réordonner
                        for i, s in enumerate(st.session_state[session_key]):
                            s['ordre'] = i + 1
                        st.rerun()

                if idx < len(st.session_state[session_key]) - 1:
                    if st.button("⬇️", key=f"{key_prefix}_down_{idx}"):
                        st.session_state[session_key][idx], st.session_state[session_key][idx+1] = \
                            st.session_state[session_key][idx+1], st.session_state[session_key][idx]
                        for i, s in enumerate(st.session_state[session_key]):
                            s['ordre'] = i + 1
                        st.rerun()

            with col3:
                if st.button("❌", key=f"{key_prefix}_del_{idx}"):
                    st.session_state[session_key].pop(idx)
                    # Réordonner
                    for i, s in enumerate(st.session_state[session_key]):
                        s['ordre'] = i + 1
                    st.rerun()
    else:
        st.info("Aucune étape ajoutée")

    return st.session_state[session_key]


# ===================================
# PREVIEW RECETTE
# ===================================

def render_recipe_preview(recette_data: Dict, ingredients: List[Dict], etapes: List[Dict]):
    """
    Prévisualisation d'une recette avant sauvegarde

    Args:
        recette_data: Données de la recette
        ingredients: Liste ingrédients
        etapes: Liste étapes
    """
    st.markdown("### 👁️ Prévisualisation")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown(f"**⏱️ Temps total:** {recette_data.get('temps_preparation', 0) + recette_data.get('temps_cuisson', 0)}min")
        st.markdown(f"**🍽️ Portions:** {recette_data.get('portions', 4)}")
        st.markdown(f"**Difficulté:** {recette_data.get('difficulte', 'moyen').capitalize()}")

    with col2:
        tags = []
        if recette_data.get('temps_preparation', 0) + recette_data.get('temps_cuisson', 0) < 30:
            tags.append("⚡ Rapide")
        if recette_data.get('est_equilibre'):
            tags.append("🥗 Équilibré")
        if tags:
            st.caption(" • ".join(tags))

    st.markdown("---")

    col_prev1, col_prev2 = st.columns(2)

    with col_prev1:
        st.markdown("**🥕 Ingrédients**")
        for ing in ingredients:
            st.write(f"• {ing['quantite']} {ing['unite']} {ing['nom']}")

    with col_prev2:
        st.markdown("**📝 Étapes**")
        for etape in etapes:
            st.write(f"{etape['ordre']}. {etape['description'][:50]}...")