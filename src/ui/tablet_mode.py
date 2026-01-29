"""
Mode Tablette / Cuisine pour l'application.

Fournit:
- CSS adapté aux écrans tactiles
- Interface simplifiée
- Gros boutons
- Navigation par gestes
- Mode cuisine (recettes step-by-step)
"""

import streamlit as st
from typing import Callable, Any
from enum import Enum


# ═══════════════════════════════════════════════════════════
# CONFIGURATION MODE TABLETTE
# ═══════════════════════════════════════════════════════════


class TabletMode(str, Enum):
    """Modes d'affichage tablette."""
    NORMAL = "normal"
    TABLET = "tablet"
    KITCHEN = "kitchen"  # Mode cuisine (très gros, tactile)


def get_tablet_mode() -> TabletMode:
    """Retourne le mode tablette actuel."""
    mode = st.session_state.get("tablet_mode", TabletMode.NORMAL)
    return TabletMode(mode) if isinstance(mode, str) else mode


def set_tablet_mode(mode: TabletMode):
    """Définit le mode tablette."""
    st.session_state["tablet_mode"] = mode


# ═══════════════════════════════════════════════════════════
# CSS TABLETTE
# ═══════════════════════════════════════════════════════════


TABLET_CSS = """
<style>
/* ═══════════════════════════════════════════════════════════
   MODE TABLETTE - CSS RESPONSIVE
   ═══════════════════════════════════════════════════════════ */

/* Variables CSS pour le mode tablette */
:root {
    --tablet-font-size-base: 1.2rem;
    --tablet-button-min-height: 60px;
    --tablet-spacing: 1.5rem;
    --tablet-border-radius: 12px;
    --tablet-touch-target: 48px;
}

/* Appliquer le mode tablette */
[data-tablet-mode="tablet"],
[data-tablet-mode="kitchen"] {
    font-size: var(--tablet-font-size-base);
}

/* Mode tablette: texte plus grand */
.tablet-mode .stMarkdown,
.tablet-mode p,
.tablet-mode span,
.tablet-mode label {
    font-size: 1.2rem !important;
    line-height: 1.6 !important;
}

/* Mode tablette: titres */
.tablet-mode h1 { font-size: 2.5rem !important; }
.tablet-mode h2 { font-size: 2rem !important; }
.tablet-mode h3 { font-size: 1.7rem !important; }

/* Mode tablette: boutons tactiles */
.tablet-mode .stButton > button {
    min-height: var(--tablet-button-min-height) !important;
    font-size: 1.3rem !important;
    padding: 16px 24px !important;
    border-radius: var(--tablet-border-radius) !important;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

/* Boutons de la sidebar en mode tablette */
.tablet-mode [data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    margin-bottom: 8px !important;
}

/* Mode tablette: inputs plus grands */
.tablet-mode input,
.tablet-mode textarea,
.tablet-mode select {
    font-size: 1.2rem !important;
    padding: 14px !important;
    min-height: var(--tablet-touch-target) !important;
}

.tablet-mode [data-baseweb="input"] input {
    font-size: 1.2rem !important;
}

.tablet-mode [data-baseweb="select"] {
    min-height: 56px !important;
}

/* Mode tablette: espacement augmenté */
.tablet-mode .stVerticalBlock > div {
    margin-bottom: var(--tablet-spacing) !important;
}

/* Mode tablette: cartes avec padding augmenté */
.tablet-mode .stExpander {
    padding: 16px !important;
}

/* Mode tablette: checkbox/radio plus grands */
.tablet-mode .stCheckbox label,
.tablet-mode .stRadio label {
    font-size: 1.2rem !important;
    padding: 12px 0 !important;
}

.tablet-mode .stCheckbox input[type="checkbox"],
.tablet-mode .stRadio input[type="radio"] {
    width: 24px !important;
    height: 24px !important;
}

/* Mode tablette: slider plus grand */
.tablet-mode [data-baseweb="slider"] {
    padding: 20px 0 !important;
}

.tablet-mode [data-baseweb="slider"] [role="slider"] {
    width: 28px !important;
    height: 28px !important;
}

/* ═══════════════════════════════════════════════════════════
   MODE CUISINE - CSS EXTRA LARGE
   ═══════════════════════════════════════════════════════════ */

/* Variables mode cuisine */
:root {
    --kitchen-font-size-base: 1.5rem;
    --kitchen-button-min-height: 80px;
    --kitchen-spacing: 2rem;
}

/* Mode cuisine: texte très grand */
.kitchen-mode .stMarkdown,
.kitchen-mode p,
.kitchen-mode span,
.kitchen-mode label {
    font-size: 1.5rem !important;
    line-height: 1.8 !important;
}

/* Mode cuisine: titres */
.kitchen-mode h1 { font-size: 3rem !important; }
.kitchen-mode h2 { font-size: 2.5rem !important; }
.kitchen-mode h3 { font-size: 2rem !important; }

/* Mode cuisine: boutons extra larges */
.kitchen-mode .stButton > button {
    min-height: var(--kitchen-button-min-height) !important;
    font-size: 1.6rem !important;
    padding: 20px 32px !important;
    border-radius: 16px !important;
    font-weight: 600 !important;
}

/* Mode cuisine: boutons primaires colorés */
.kitchen-mode .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4CAF50, #45a049) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
}

/* Mode cuisine: inputs très grands */
.kitchen-mode input,
.kitchen-mode textarea,
.kitchen-mode select {
    font-size: 1.5rem !important;
    padding: 18px !important;
    min-height: 60px !important;
}

/* Mode cuisine: numéros d'étapes */
.kitchen-step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF6B6B, #ee5a5a);
    color: white;
    font-size: 1.8rem;
    font-weight: 700;
    margin-right: 16px;
    box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

/* Mode cuisine: carte d'étape */
.kitchen-step-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    margin: 20px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-left: 6px solid #4CAF50;
}

/* Mode cuisine: navigation bas de page */
.kitchen-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 16px 24px;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    gap: 16px;
    z-index: 1000;
}

.kitchen-nav button {
    flex: 1;
    min-height: 70px;
    font-size: 1.4rem !important;
}

/* Mode cuisine: timer flottant */
.kitchen-timer {
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #FF6B6B, #ee5a5a);
    color: white;
    padding: 16px 24px;
    border-radius: 50px;
    font-size: 2rem;
    font-weight: 700;
    box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
    z-index: 1001;
    display: flex;
    align-items: center;
    gap: 12px;
}

/* Animation pulse pour le timer */
.kitchen-timer.active {
    animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE MEDIA QUERIES
   ═══════════════════════════════════════════════════════════ */

/* Tablettes portrait (768px - 1024px) */
@media (min-width: 768px) and (max-width: 1024px) {
    .stApp {
        font-size: 1.1rem;
    }
    
    .stButton > button {
        min-height: 54px;
        font-size: 1.1rem;
    }
}

/* Tablettes paysage (1024px+) */
@media (min-width: 1024px) and (max-height: 800px) {
    /* Probablement une tablette en mode paysage */
    .stButton > button {
        min-height: 50px;
    }
}

/* Touch devices */
@media (hover: none) and (pointer: coarse) {
    /* Appareils tactiles */
    .stButton > button {
        min-height: 48px;
        padding: 12px 20px;
    }
    
    /* Supprimer les effets hover sur tactile */
    .stButton > button:hover {
        transform: none;
    }
    
    /* Active state pour tactile */
    .stButton > button:active {
        transform: scale(0.98);
        opacity: 0.9;
    }
}

/* ═══════════════════════════════════════════════════════════
   COMPOSANTS UTILITAIRES
   ═══════════════════════════════════════════════════════════ */

/* Gros badge de statut */
.tablet-badge {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
}

.tablet-badge.success {
    background: #E8F5E9;
    color: #2E7D32;
}

.tablet-badge.warning {
    background: #FFF3E0;
    color: #E65100;
}

.tablet-badge.danger {
    background: #FFEBEE;
    color: #C62828;
}

/* Grille tactile pour sélection */
.tablet-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    padding: 16px 0;
}

.tablet-grid-item {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tablet-grid-item:active,
.tablet-grid-item.selected {
    border-color: #4CAF50;
    background: #E8F5E9;
}

.tablet-grid-item .icon {
    font-size: 2.5rem;
    margin-bottom: 8px;
}

/* Swipe indicator */
.swipe-indicator {
    text-align: center;
    padding: 12px;
    color: #9e9e9e;
    font-size: 0.9rem;
}

.swipe-indicator::before {
    content: "← swipe →";
}
</style>
"""


KITCHEN_MODE_CSS = """
<style>
/* CSS spécifique au mode cuisine (superpose tablet CSS) */

/* Corps principal avec padding pour nav fixe */
.kitchen-mode .main .block-container {
    padding-bottom: 120px !important;
}

/* Cacher la sidebar en mode cuisine */
.kitchen-mode [data-testid="stSidebar"] {
    display: none !important;
}

/* Agrandir le contenu principal */
.kitchen-mode .main {
    max-width: 100% !important;
    padding: 24px !important;
}

/* Ingrédients en liste tactile */
.kitchen-ingredient {
    display: flex;
    align-items: center;
    padding: 16px;
    background: #f5f5f5;
    border-radius: 12px;
    margin: 8px 0;
    font-size: 1.3rem;
}

.kitchen-ingredient input[type="checkbox"] {
    width: 28px;
    height: 28px;
    margin-right: 16px;
}

.kitchen-ingredient.checked {
    opacity: 0.6;
    text-decoration: line-through;
}

/* Animation de transition entre étapes */
.kitchen-step-transition {
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS D'APPLICATION DU MODE
# ═══════════════════════════════════════════════════════════


def apply_tablet_mode():
    """
    Applique le mode tablette à la page courante.
    
    À appeler au début de chaque page/module.
    """
    mode = get_tablet_mode()
    
    # Toujours inclure le CSS de base
    st.markdown(TABLET_CSS, unsafe_allow_html=True)
    
    if mode == TabletMode.TABLET:
        st.markdown('<div class="tablet-mode">', unsafe_allow_html=True)
    elif mode == TabletMode.KITCHEN:
        st.markdown(KITCHEN_MODE_CSS, unsafe_allow_html=True)
        st.markdown('<div class="tablet-mode kitchen-mode">', unsafe_allow_html=True)


def close_tablet_mode():
    """Ferme les balises du mode tablette."""
    mode = get_tablet_mode()
    
    if mode in [TabletMode.TABLET, TabletMode.KITCHEN]:
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI TABLETTE
# ═══════════════════════════════════════════════════════════


def tablet_button(
    label: str,
    key: str | None = None,
    icon: str = "",
    type: str = "secondary",
    on_click: Callable | None = None,
    **kwargs
) -> bool:
    """
    Bouton optimisé pour tablette.
    
    Args:
        label: Texte du bouton
        key: Clé unique
        icon: Emoji/icône à afficher
        type: "primary", "secondary", "danger"
        on_click: Callback au clic
        
    Returns:
        True si cliqué
    """
    full_label = f"{icon} {label}" if icon else label
    
    # Styles selon le type
    if type == "primary":
        kwargs["type"] = "primary"
    elif type == "danger":
        kwargs["help"] = "⚠️ Action irréversible"
    
    return st.button(full_label, key=key, on_click=on_click, **kwargs)


def tablet_select_grid(
    options: list[dict[str, Any]],
    key: str,
    columns: int = 3,
) -> str | None:
    """
    Grille de sélection tactile.
    
    Args:
        options: Liste de {"value": str, "label": str, "icon": str}
        key: Clé unique
        columns: Nombre de colonnes
        
    Returns:
        Valeur sélectionnée ou None
    """
    selected = st.session_state.get(f"{key}_selected")
    
    cols = st.columns(columns)
    
    for i, opt in enumerate(options):
        with cols[i % columns]:
            is_selected = selected == opt.get("value")
            
            btn_label = f"{opt.get('icon', '')} {opt.get('label', opt.get('value', ''))}"
            
            if st.button(
                btn_label,
                key=f"{key}_{i}",
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state[f"{key}_selected"] = opt.get("value")
                st.rerun()
    
    return selected


def tablet_number_input(
    label: str,
    key: str,
    min_value: int = 0,
    max_value: int = 100,
    default: int = 1,
    step: int = 1,
) -> int:
    """
    Input numérique avec boutons +/- tactiles.
    
    Args:
        label: Label du champ
        key: Clé unique
        min_value: Valeur minimale
        max_value: Valeur maximale
        default: Valeur par défaut
        step: Incrément
        
    Returns:
        Valeur actuelle
    """
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = default
    
    current = st.session_state[f"{key}_value"]
    
    st.write(f"**{label}**")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("➖", key=f"{key}_minus", use_container_width=True):
            new_val = max(min_value, current - step)
            st.session_state[f"{key}_value"] = new_val
            st.rerun()
    
    with col2:
        st.markdown(
            f"<div style='text-align: center; font-size: 2rem; font-weight: bold;'>{current}</div>",
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("➕", key=f"{key}_plus", use_container_width=True):
            new_val = min(max_value, current + step)
            st.session_state[f"{key}_value"] = new_val
            st.rerun()
    
    return current


def tablet_checklist(
    items: list[str],
    key: str,
    on_check: Callable[[str, bool], None] | None = None,
) -> dict[str, bool]:
    """
    Liste de cases à cocher tactile.
    
    Args:
        items: Liste des éléments
        key: Clé unique
        on_check: Callback (item, checked)
        
    Returns:
        Dict {item: checked}
    """
    if f"{key}_checked" not in st.session_state:
        st.session_state[f"{key}_checked"] = {item: False for item in items}
    
    checked = st.session_state[f"{key}_checked"]
    
    for item in items:
        is_checked = checked.get(item, False)
        icon = "✅" if is_checked else "⬜"
        
        if st.button(
            f"{icon} {item}",
            key=f"{key}_{item}",
            use_container_width=True,
        ):
            new_state = not is_checked
            st.session_state[f"{key}_checked"][item] = new_state
            
            if on_check:
                on_check(item, new_state)
            
            st.rerun()
    
    return checked


# ═══════════════════════════════════════════════════════════
# MODE CUISINE - RECETTE STEP BY STEP
# ═══════════════════════════════════════════════════════════


def render_kitchen_recipe_view(
    recette: dict[str, Any],
    key: str = "kitchen_recipe",
):
    """
    Affiche une recette en mode cuisine (step-by-step).
    
    Args:
        recette: Dict avec nom, ingredients, instructions
        key: Clé unique
    """
    # État
    if f"{key}_step" not in st.session_state:
        st.session_state[f"{key}_step"] = 0
    
    current_step = st.session_state[f"{key}_step"]
    instructions = recette.get("instructions", [])
    total_steps = len(instructions)
    
    # Timer (si défini)
    if f"{key}_timer" in st.session_state and st.session_state[f"{key}_timer"] > 0:
        st.markdown(
            f"""
            <div class="kitchen-timer active">
                ⏱️ {st.session_state[f"{key}_timer"]} min
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Titre de la recette
    st.markdown(f"## 👨‍🍳 {recette.get('nom', 'Recette')}")
    
    # Navigation par onglets
    tab1, tab2 = st.tabs(["📝 Étapes", "🥕 Ingrédients"])
    
    with tab1:
        if current_step == 0:
            # Écran d'accueil
            st.markdown("### 🚀 Prêt à cuisiner ?")
            st.markdown(f"**{total_steps} étapes** à suivre")
            
            # Temps
            temps_prep = recette.get("temps_preparation", 0)
            temps_cuisson = recette.get("temps_cuisson", 0)
            if temps_prep or temps_cuisson:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("⏱️ Préparation", f"{temps_prep} min")
                with col2:
                    st.metric("🔥 Cuisson", f"{temps_cuisson} min")
            
            if st.button("▶️ Commencer", key=f"{key}_start", type="primary", use_container_width=True):
                st.session_state[f"{key}_step"] = 1
                st.rerun()
        
        elif current_step > total_steps:
            # Fin de la recette
            st.markdown("### 🎉 Bravo !")
            st.markdown("Votre plat est prêt. Bon appétit !")
            st.balloons()
            
            if st.button("🔄 Recommencer", key=f"{key}_restart", use_container_width=True):
                st.session_state[f"{key}_step"] = 0
                st.rerun()
        
        else:
            # Étape courante
            instruction = instructions[current_step - 1]
            
            st.markdown(
                f"""
                <div class="kitchen-step-card kitchen-step-transition">
                    <span class="kitchen-step-number">{current_step}</span>
                    <span style="font-size: 1.4rem;">{instruction}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Barre de progression
            progress = current_step / total_steps
            st.progress(progress, text=f"Étape {current_step}/{total_steps}")
            
            # Timer rapide
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⏱️ 1 min", key=f"{key}_timer_1"):
                    st.session_state[f"{key}_timer"] = 1
            with col2:
                if st.button("⏱️ 5 min", key=f"{key}_timer_5"):
                    st.session_state[f"{key}_timer"] = 5
            with col3:
                if st.button("⏱️ 10 min", key=f"{key}_timer_10"):
                    st.session_state[f"{key}_timer"] = 10
    
    with tab2:
        # Liste des ingrédients
        ingredients = recette.get("ingredients", [])
        
        st.markdown("### 🥕 Ingrédients")
        
        for i, ing in enumerate(ingredients):
            if isinstance(ing, dict):
                quantite = ing.get("quantite", "")
                unite = ing.get("unite", "")
                nom = ing.get("nom", ing.get("ingredient", ""))
                label = f"{quantite} {unite} {nom}".strip()
            else:
                label = str(ing)
            
            st.checkbox(label, key=f"{key}_ing_{i}")
    
    # Navigation fixe en bas
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_step > 1:
            if st.button("◀️ Précédent", key=f"{key}_prev", use_container_width=True):
                st.session_state[f"{key}_step"] = current_step - 1
                st.rerun()
    
    with col2:
        if st.button("❌ Quitter", key=f"{key}_quit", use_container_width=True):
            st.session_state[f"{key}_step"] = 0
    
    with col3:
        if current_step >= 1 and current_step <= total_steps:
            btn_label = "✅ Terminé" if current_step == total_steps else "Suivant ▶️"
            if st.button(btn_label, key=f"{key}_next", type="primary", use_container_width=True):
                st.session_state[f"{key}_step"] = current_step + 1
                st.rerun()


# ═══════════════════════════════════════════════════════════
# SÉLECTEUR DE MODE
# ═══════════════════════════════════════════════════════════


def render_mode_selector():
    """Affiche le sélecteur de mode dans la sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📱 Mode d'affichage")
        
        mode = get_tablet_mode()
        
        options = {
            TabletMode.NORMAL: "🖥️ Normal",
            TabletMode.TABLET: "📱 Tablette",
            TabletMode.KITCHEN: "👨‍🍳 Cuisine",
        }
        
        selected = st.selectbox(
            "Choisir le mode",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            index=list(options.keys()).index(mode),
            key="mode_selector",
            label_visibility="collapsed",
        )
        
        if selected != mode:
            set_tablet_mode(selected)
            st.rerun()
        
        if mode == TabletMode.KITCHEN:
            st.info("🍳 Mode cuisine activé:\n- Interface simplifiée\n- Gros boutons tactiles\n- Navigation par étapes")
