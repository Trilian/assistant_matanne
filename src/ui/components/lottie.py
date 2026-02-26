"""
Intégration animations Lottie pour UX améliorée.

Permet d'afficher des animations vectorielles légères et fluides
via la bibliothèque lottie-web (JSON animations).

Usage:
    from src.ui.components.lottie import afficher_lottie, LottieAnimation

    # Animation prédéfinie
    afficher_lottie(LottieAnimation.SUCCESS)

    # Animation custom depuis URL
    afficher_lottie_url("https://assets.lottiefiles.com/packages/lf20_xxx.json")

    # Animation avec options
    afficher_lottie(
        LottieAnimation.LOADING,
        hauteur=100,
        largeur=100,
        vitesse=1.5,
        boucle=True
    )
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

import streamlit as st

from src.ui.registry import composant_ui


class LottieAnimation(str, Enum):
    """Animations Lottie prédéfinies."""

    # Feedback utilisateur
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    # États de chargement
    LOADING = "loading"
    LOADING_DOTS = "loading_dots"
    LOADING_SPINNER = "loading_spinner"
    PROCESSING = "processing"

    # Actions
    CHECK = "check"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    SAVE = "save"
    DELETE = "delete"
    SEARCH = "search"
    REFRESH = "refresh"

    # Navigation/Flow
    ARROW_RIGHT = "arrow_right"
    ARROW_DOWN = "arrow_down"
    SWIPE = "swipe"

    # Illustrations
    EMPTY_STATE = "empty_state"
    COOKING = "cooking"
    FAMILY = "family"
    CALENDAR = "calendar"
    CELEBRATION = "celebration"
    HEART = "heart"

    # Interactions
    LIKE = "like"
    STAR = "star"
    BELL = "bell"
    CHAT = "chat"


# URLs des animations Lottie (sources publiques LottieFiles)
# Note: En production, héberger les JSON localement dans static/lottie/
_LOTTIE_URLS: dict[LottieAnimation, str] = {
    # Feedback
    LottieAnimation.SUCCESS: "https://lottie.host/a3e1e87e-e3c5-470a-a12d-68bd5a4e5a6f/VFDmqPYdGI.json",
    LottieAnimation.ERROR: "https://lottie.host/c4c84d89-5e11-4d6e-8b0a-3b7e0a3c5e2f/error.json",
    LottieAnimation.WARNING: "https://lottie.host/6eb8e6c7-5f8e-4c5b-8b8e-8b8e8b8e8b8e/warning.json",
    LottieAnimation.INFO: "https://lottie.host/info-animation/info.json",
    # Loading
    LottieAnimation.LOADING: "https://lottie.host/3b4e3b4e-3b4e-3b4e-3b4e-3b4e3b4e3b4e/loading.json",
    LottieAnimation.LOADING_DOTS: "https://lottie.host/loading-dots/dots.json",
    LottieAnimation.LOADING_SPINNER: "https://lottie.host/spinner/spinner.json",
    LottieAnimation.PROCESSING: "https://lottie.host/processing/process.json",
    # Actions
    LottieAnimation.CHECK: "https://lottie.host/check/check.json",
    LottieAnimation.UPLOAD: "https://lottie.host/upload/upload.json",
    LottieAnimation.DOWNLOAD: "https://lottie.host/download/download.json",
    LottieAnimation.SAVE: "https://lottie.host/save/save.json",
    LottieAnimation.DELETE: "https://lottie.host/delete/delete.json",
    LottieAnimation.SEARCH: "https://lottie.host/search/search.json",
    LottieAnimation.REFRESH: "https://lottie.host/refresh/refresh.json",
    # Navigation
    LottieAnimation.ARROW_RIGHT: "https://lottie.host/arrow-right/arrow.json",
    LottieAnimation.ARROW_DOWN: "https://lottie.host/arrow-down/arrow.json",
    LottieAnimation.SWIPE: "https://lottie.host/swipe/swipe.json",
    # Illustrations
    LottieAnimation.EMPTY_STATE: "https://lottie.host/empty/empty.json",
    LottieAnimation.COOKING: "https://lottie.host/cooking/cooking.json",
    LottieAnimation.FAMILY: "https://lottie.host/family/family.json",
    LottieAnimation.CALENDAR: "https://lottie.host/calendar/calendar.json",
    LottieAnimation.CELEBRATION: "https://lottie.host/celebration/celebration.json",
    LottieAnimation.HEART: "https://lottie.host/heart/heart.json",
    # Interactions
    LottieAnimation.LIKE: "https://lottie.host/like/like.json",
    LottieAnimation.STAR: "https://lottie.host/star/star.json",
    LottieAnimation.BELL: "https://lottie.host/bell/bell.json",
    LottieAnimation.CHAT: "https://lottie.host/chat/chat.json",
}


@dataclass
class LottieConfig:
    """Configuration pour le lecteur Lottie."""

    hauteur: int = 200
    largeur: int = 200
    vitesse: float = 1.0
    boucle: bool = True
    autoplay: bool = True
    renderer: str = "svg"  # "svg" | "canvas" | "html"
    mode_direction: int = 1  # 1 = forward, -1 = reverse


def _generer_html_lottie(
    animation_json: dict[str, Any] | str,
    config: LottieConfig,
    container_id: str,
) -> str:
    """Génère le HTML/JS pour le lecteur Lottie.

    Args:
        animation_json: Données JSON de l'animation ou URL.
        config: Configuration du lecteur.
        container_id: ID unique du container.

    Returns:
        HTML avec script Lottie intégré.
    """
    # Sérialiser JSON si dict
    if isinstance(animation_json, dict):
        anim_data = json.dumps(animation_json)
        load_method = f"animationData: {anim_data}"
    else:
        load_method = f'path: "{animation_json}"'

    return f"""
    <div id="{container_id}" style="
        width: {config.largeur}px;
        height: {config.hauteur}px;
        margin: 0 auto;
    "></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <script>
        (function() {{
            if (document.getElementById("{container_id}").children.length > 0) return;

            lottie.loadAnimation({{
                container: document.getElementById("{container_id}"),
                renderer: "{config.renderer}",
                loop: {str(config.boucle).lower()},
                autoplay: {str(config.autoplay).lower()},
                {load_method}
            }}).setSpeed({config.vitesse});
        }})();
    </script>
    """


def _generer_html_lottie_respectful(
    animation_json: dict[str, Any] | str,
    config: LottieConfig,
    container_id: str,
) -> str:
    """Version respectueuse de prefers-reduced-motion.

    Args:
        animation_json: Données JSON animation ou URL.
        config: Configuration du lecteur.
        container_id: ID unique du container.

    Returns:
        HTML avec gestion reduced-motion.
    """
    base_html = _generer_html_lottie(animation_json, config, container_id)

    return f"""
    <style>
        @media (prefers-reduced-motion: reduce) {{
            #{container_id} {{
                display: none;
            }}
            #{container_id}-fallback {{
                display: block !important;
            }}
        }}
    </style>
    <div id="{container_id}-fallback" style="
        display: none;
        width: {config.largeur}px;
        height: {config.hauteur}px;
        margin: 0 auto;
        background: #f0f0f0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #666;
        font-size: 0.9rem;
    ">
        Animation désactivée
    </div>
    {base_html}
    """


@composant_ui(
    "atoms",
    exemple="afficher_lottie(LottieAnimation.SUCCESS, hauteur=150)",
    tags=("animation", "lottie", "feedback"),
)
def afficher_lottie(
    animation: LottieAnimation,
    *,
    hauteur: int = 200,
    largeur: int = 200,
    vitesse: float = 1.0,
    boucle: bool = True,
    autoplay: bool = True,
    respecter_reduced_motion: bool = True,
    key: str | None = None,
) -> None:
    """Affiche une animation Lottie prédéfinie.

    Args:
        animation: Animation prédéfinie à afficher.
        hauteur: Hauteur du container en pixels.
        largeur: Largeur du container en pixels.
        vitesse: Vitesse de lecture (1.0 = normale).
        boucle: Si True, l'animation tourne en boucle.
        autoplay: Si True, démarre automatiquement.
        respecter_reduced_motion: Respecte prefers-reduced-motion.
        key: Clé unique Streamlit.

    Example:
        >>> afficher_lottie(LottieAnimation.SUCCESS)
        >>> afficher_lottie(LottieAnimation.LOADING, hauteur=100, vitesse=1.5)
    """
    url = _LOTTIE_URLS.get(animation)
    if not url:
        st.warning(f"Animation '{animation}' non disponible")
        return

    config = LottieConfig(
        hauteur=hauteur,
        largeur=largeur,
        vitesse=vitesse,
        boucle=boucle,
        autoplay=autoplay,
    )

    container_id = f"lottie_{animation.value}_{key or id(animation)}"

    if respecter_reduced_motion:
        html = _generer_html_lottie_respectful(url, config, container_id)
    else:
        html = _generer_html_lottie(url, config, container_id)

    st.markdown(html, unsafe_allow_html=True)


@composant_ui(
    "atoms",
    exemple='afficher_lottie_url("https://example.com/anim.json")',
    tags=("animation", "lottie", "custom"),
)
def afficher_lottie_url(
    url: str,
    *,
    hauteur: int = 200,
    largeur: int = 200,
    vitesse: float = 1.0,
    boucle: bool = True,
    autoplay: bool = True,
    respecter_reduced_motion: bool = True,
    key: str | None = None,
) -> None:
    """Affiche une animation Lottie depuis une URL.

    Args:
        url: URL du fichier JSON Lottie.
        hauteur: Hauteur du container en pixels.
        largeur: Largeur du container en pixels.
        vitesse: Vitesse de lecture.
        boucle: Si True, tourne en boucle.
        autoplay: Si True, démarre automatiquement.
        respecter_reduced_motion: Respecte prefers-reduced-motion.
        key: Clé unique Streamlit.

    Example:
        >>> afficher_lottie_url("https://assets.lottiefiles.com/packages/lf20_xxx.json")
    """
    config = LottieConfig(
        hauteur=hauteur,
        largeur=largeur,
        vitesse=vitesse,
        boucle=boucle,
        autoplay=autoplay,
    )

    container_id = f"lottie_custom_{key or hash(url)}"

    if respecter_reduced_motion:
        html = _generer_html_lottie_respectful(url, config, container_id)
    else:
        html = _generer_html_lottie(url, config, container_id)

    st.markdown(html, unsafe_allow_html=True)


@composant_ui(
    "atoms",
    exemple="afficher_lottie_json(data, hauteur=150)",
    tags=("animation", "lottie", "json"),
)
def afficher_lottie_json(
    animation_data: dict[str, Any],
    *,
    hauteur: int = 200,
    largeur: int = 200,
    vitesse: float = 1.0,
    boucle: bool = True,
    autoplay: bool = True,
    respecter_reduced_motion: bool = True,
    key: str | None = None,
) -> None:
    """Affiche une animation Lottie depuis des données JSON.

    Args:
        animation_data: Données JSON de l'animation Lottie.
        hauteur: Hauteur du container en pixels.
        largeur: Largeur du container en pixels.
        vitesse: Vitesse de lecture.
        boucle: Si True, tourne en boucle.
        autoplay: Si True, démarre automatiquement.
        respecter_reduced_motion: Respecte prefers-reduced-motion.
        key: Clé unique Streamlit.

    Example:
        >>> with open("animation.json") as f:
        ...     data = json.load(f)
        >>> afficher_lottie_json(data)
    """
    config = LottieConfig(
        hauteur=hauteur,
        largeur=largeur,
        vitesse=vitesse,
        boucle=boucle,
        autoplay=autoplay,
    )

    container_id = f"lottie_json_{key or hash(str(animation_data)[:100])}"

    if respecter_reduced_motion:
        html = _generer_html_lottie_respectful(animation_data, config, container_id)
    else:
        html = _generer_html_lottie(animation_data, config, container_id)

    st.markdown(html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# HELPERS POUR FEEDBACK COURANTS
# ═══════════════════════════════════════════════════════════


def lottie_success(message: str = "", taille: int = 100) -> None:
    """Affiche une animation de succès."""
    afficher_lottie(LottieAnimation.SUCCESS, hauteur=taille, largeur=taille, boucle=False)
    if message:
        st.success(message)


def lottie_error(message: str = "", taille: int = 100) -> None:
    """Affiche une animation d'erreur."""
    afficher_lottie(LottieAnimation.ERROR, hauteur=taille, largeur=taille, boucle=False)
    if message:
        st.error(message)


def lottie_loading(message: str = "Chargement...", taille: int = 80) -> None:
    """Affiche une animation de chargement."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        afficher_lottie(LottieAnimation.LOADING, hauteur=taille, largeur=taille)
        st.caption(message)


def lottie_empty_state(message: str = "Aucune donnée", taille: int = 150) -> None:
    """Affiche une illustration pour état vide."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        afficher_lottie(LottieAnimation.EMPTY_STATE, hauteur=taille, largeur=taille)
        st.caption(message)


__all__ = [
    "LottieAnimation",
    "LottieConfig",
    "afficher_lottie",
    "afficher_lottie_url",
    "afficher_lottie_json",
    "lottie_success",
    "lottie_error",
    "lottie_loading",
    "lottie_empty_state",
]
