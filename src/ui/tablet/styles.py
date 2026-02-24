"""
Styles CSS pour le mode tablette et cuisine.

Fournit les feuilles de style pour:
- Mode tablette (interface tactile)
- Mode cuisine (gros boutons, navigation simplifiée)
- Responsive media queries

Les couleurs utilisent des CSS custom properties (``var(--sem-*)``)
pour le support dark mode automatique via les tokens sémantiques.
"""

import streamlit.components.v1 as components

from src.ui.engine import CSSManager

from .config import ModeTablette, obtenir_mode_tablette

# ═══════════════════════════════════════════════════════════
# CSS TABLETTE — tokens sémantiques avec fallbacks
# ═══════════════════════════════════════════════════════════


CSS_TABLETTE = """
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
    /* Couleurs kitchen timer/step — adaptables dark mode */
    --kitchen-accent: var(--sem-danger, #FF6B6B);
    --kitchen-accent-dark: var(--sem-danger, #ee5a5a);
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
    background: linear-gradient(135deg,
        var(--sem-interactive, #4CAF50),
        var(--sem-interactive-hover, #45a049)) !important;
    color: var(--sem-on-interactive, white) !important;
    box-shadow: var(--sem-shadow-md, 0 4px 12px rgba(76, 175, 80, 0.3)) !important;
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
    background: linear-gradient(135deg, var(--kitchen-accent), var(--kitchen-accent-dark));
    color: var(--sem-on-interactive, white);
    font-size: 1.8rem;
    font-weight: 700;
    margin-right: 16px;
    box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

/* Mode cuisine: carte d'étape */
.kitchen-step-card {
    background: var(--sem-surface, white);
    border-radius: 20px;
    padding: 24px;
    margin: 20px 0;
    box-shadow: var(--sem-shadow-md, 0 4px 20px rgba(0,0,0,0.08));
    border-left: 6px solid var(--sem-interactive, #4CAF50);
}

/* Mode cuisine: navigation bas de page */
.kitchen-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--sem-surface, white);
    padding: 16px 24px;
    box-shadow: var(--sem-shadow-lg, 0 -4px 20px rgba(0,0,0,0.1));
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
    background: linear-gradient(135deg, var(--kitchen-accent), var(--kitchen-accent-dark));
    color: var(--sem-on-interactive, white);
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
    background: var(--sem-success-subtle, #E8F5E9);
    color: var(--sem-on-success, #2E7D32);
}

.tablet-badge.warning {
    background: var(--sem-warning-subtle, #FFF3E0);
    color: var(--sem-on-warning, #E65100);
}

.tablet-badge.danger {
    background: var(--sem-danger-subtle, #FFEBEE);
    color: var(--sem-on-danger, #C62828);
}

/* Grille tactile pour sélection */
.tablet-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    padding: 16px 0;
}

.tablet-grid-item {
    background: var(--sem-surface, white);
    border: 2px solid var(--sem-border, #e0e0e0);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tablet-grid-item:active,
.tablet-grid-item.selected {
    border-color: var(--sem-interactive, #4CAF50);
    background: var(--sem-success-subtle, #E8F5E9);
}

.tablet-grid-item .icon {
    font-size: 2.5rem;
    margin-bottom: 8px;
}

/* Swipe indicator */
.swipe-indicator {
    text-align: center;
    padding: 12px;
    color: var(--sem-on-surface-muted, #9e9e9e);
    font-size: 0.9rem;
}

.swipe-indicator::before {
    content: "← swipe →";
}
"""


CSS_MODE_CUISINE = """
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
    background: var(--sem-surface-alt, #f5f5f5);
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
"""


# ═══════════════════════════════════════════════════════════
# FONCTIONS D'APPLICATION DU MODE
# ═══════════════════════════════════════════════════════════


def appliquer_mode_tablette():
    """
    Applique le mode tablette à la page courante.

    Enregistre le CSS dans le ``CSSManager`` et ajoute la classe
    appropriée sur le body via un script inline.
    """
    mode = obtenir_mode_tablette()

    # Toujours enregistrer le CSS tablette de base (class-guarded, zéro coût si inactif)
    CSSManager.register("tablet-base", CSS_TABLETTE)

    if mode == ModeTablette.TABLETTE:
        components.html(
            "<script>document.body.classList.add('tablet-mode');</script>",
            height=0,
        )
    elif mode == ModeTablette.CUISINE:
        CSSManager.register("tablet-kitchen", CSS_MODE_CUISINE)
        components.html(
            "<script>document.body.classList.add('tablet-mode', 'kitchen-mode');</script>",
            height=0,
        )

    # Réinjecter le CSS si de nouveaux blocs ont été ajoutés
    CSSManager.inject_all()


def fermer_mode_tablette():
    """Retire les classes CSS du mode tablette."""
    mode = obtenir_mode_tablette()

    if mode in [ModeTablette.TABLETTE, ModeTablette.CUISINE]:
        components.html(
            "<script>document.body.classList.remove('tablet-mode', 'kitchen-mode');</script>",
            height=0,
        )
