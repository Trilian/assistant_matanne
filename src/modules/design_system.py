"""
Design System — Page de documentation interactive des composants UI.

Similaire à Storybook: catalogue auto-généré depuis le registry,
aperçu en direct des composants, palette de couleurs, et tokens.

Point d'entrée: ``app()`` — généré via ``@module_app`` sur ``DesignSystemModule``.

Premier module piloté avec ``BaseModule`` (Phase 4 Audit, item 16).
"""

from __future__ import annotations

from typing import Callable

import streamlit as st

from src.core.monitoring import profiler_rerun
from src.modules._framework import BaseModule, module_app
from src.ui.keys import KeyNamespace
from src.ui.registry import ComponentMeta, obtenir_catalogue, rechercher_composants
from src.ui.state.url import tabs_with_url
from src.ui.tokens import Couleur, Espacement, Ombre, Rayon, Typographie

# Session keys scopées
_keys = KeyNamespace("design_system")


def _afficher_palette() -> None:
    """Affiche la palette de couleurs du design system."""
    st.markdown("### 🎨 Palette de couleurs")

    categories = {
        "Primaires": [
            ("PRIMARY", Couleur.PRIMARY),
            ("SECONDARY", Couleur.SECONDARY),
            ("ACCENT", Couleur.ACCENT),
        ],
        "Sémantiques": [
            ("SUCCESS", Couleur.SUCCESS),
            ("WARNING", Couleur.WARNING),
            ("DANGER", Couleur.DANGER),
            ("INFO", Couleur.INFO),
        ],
        "Texte": [
            ("TEXT_PRIMARY", Couleur.TEXT_PRIMARY),
            ("TEXT_SECONDARY", Couleur.TEXT_SECONDARY),
            ("TEXT_MUTED", Couleur.TEXT_MUTED),
        ],
        "Arrière-plans": [
            ("BG_SURFACE", Couleur.BG_SURFACE),
            ("BG_SUBTLE", Couleur.BG_SUBTLE),
            ("BG_INFO", Couleur.BG_INFO),
            ("BG_SUCCESS", Couleur.BG_SUCCESS),
            ("BG_WARNING", Couleur.BG_WARNING),
            ("BG_DANGER", Couleur.BG_DANGER),
        ],
    }

    for cat_name, couleurs in categories.items():
        st.markdown(f"**{cat_name}**")
        cols = st.columns(min(len(couleurs), 6))
        for i, (nom, valeur) in enumerate(couleurs):
            with cols[i % 6]:
                # Swatch
                text_color = (
                    "white"
                    if valeur
                    not in (
                        "#ffffff",
                        "#f8f9fa",
                        "#f0f0f0",
                        "#e7f3ff",
                        "#d4edda",
                        "#fff3cd",
                        "#f8d7da",
                    )
                    else "#333"
                )
                st.markdown(
                    f'<div style="background:{valeur};color:{text_color};'
                    f"padding:1rem;border-radius:8px;text-align:center;"
                    f'border:1px solid #ddd;margin-bottom:0.5rem;">'
                    f"<strong>{nom}</strong><br>"
                    f"<small>{valeur}</small></div>",
                    unsafe_allow_html=True,
                )


def _afficher_tokens() -> None:
    """Affiche les tokens d'espacement, rayon, typographie, etc."""
    st.markdown("### 📏 Tokens")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Espacements**")
        for token in Espacement:
            st.markdown(
                f'<div style="display:flex;align-items:center;margin:0.25rem 0;">'
                f'<div style="background:#4CAF50;height:12px;width:calc({token.value} * 10);'
                f'border-radius:2px;margin-right:0.5rem;"></div>'
                f"<code>{token.name}: {token.value}</code></div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("**Rayons de bordure**")
        for token in Rayon:
            st.markdown(
                f'<div style="display:flex;align-items:center;margin:0.3rem 0;">'
                f'<div style="background:#e0e0e0;width:40px;height:40px;'
                f'border-radius:{token.value};margin-right:0.5rem;border:2px solid #999;"></div>'
                f"<code>{token.name}: {token.value}</code></div>",
                unsafe_allow_html=True,
            )

    with col3:
        st.markdown("**Typographie**")
        for token in list(Typographie)[:8]:
            st.markdown(
                f'<div style="font-size:{token.value};margin:0.2rem 0;">'
                f'{token.name} <small style="color:#999;">({token.value})</small></div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Ombres**")
        for token in Ombre:
            st.markdown(
                f'<div style="background:white;padding:1rem;margin:0.5rem 0;'
                f'border-radius:8px;box-shadow:{token.value};">'
                f"<code>{token.name}</code></div>",
                unsafe_allow_html=True,
            )


def _afficher_catalogue() -> None:
    """Affiche le catalogue de composants auto-généré."""
    st.markdown("### 🧩 Catalogue de composants")

    catalogue = obtenir_catalogue()

    if not catalogue:
        st.info(
            "Aucun composant enregistré. Les composants s'enregistrent "
            "automatiquement à l'import via `@composant_ui`."
        )

        # Forcer l'import pour déclencher l'enregistrement
        with st.spinner("Chargement des composants..."):
            try:
                import src.ui.components.atoms  # noqa: F401  # pyright: ignore[reportUnusedImport]
                import src.ui.components.forms  # noqa: F401  # pyright: ignore[reportUnusedImport]
                import src.ui.components.metrics  # noqa: F401  # pyright: ignore[reportUnusedImport]
                import src.ui.components.system  # noqa: F401  # pyright: ignore[reportUnusedImport]

                catalogue = obtenir_catalogue()
            except ImportError:
                pass

    if not catalogue:
        st.warning("Impossible de charger le catalogue.")
        return

    # Barre de recherche
    terme = st.text_input("🔍 Rechercher un composant", key="ds_search")
    if terme:
        resultats = rechercher_composants(terme)
        if resultats:
            for meta in resultats:
                _afficher_composant_card(meta)
        else:
            st.info(f"Aucun composant trouvé pour « {terme} »")
        return

    # Affichage par catégorie
    for categorie, composants in sorted(catalogue.items()):
        with st.expander(
            f"📁 {categorie.capitalize()} ({len(composants)} composants)", expanded=True
        ):
            for meta in sorted(composants, key=lambda m: m.nom):
                _afficher_composant_card(meta)


def _afficher_composant_card(meta: ComponentMeta) -> None:
    """Affiche la carte d'un composant."""
    tags_html = " ".join(
        f'<span style="background:#e7f3ff;padding:2px 8px;border-radius:10px;'
        f'font-size:0.75rem;margin-right:4px;">{tag}</span>'
        for tag in meta.tags
    )

    st.markdown(
        f'<div style="border-left:3px solid #4CAF50;padding:0.75rem;'
        f'margin:0.5rem 0;background:#f8f9fa;border-radius:0 8px 8px 0;">'
        f"<strong><code>{meta.nom}</code></strong>"
        f'<span style="color:#999;font-size:0.85rem;margin-left:0.5rem;">'
        f"{meta.signature}</span><br>"
        f'<span style="color:#666;">{meta.description[:120] if meta.description else "—"}</span>'
        f"{' ' + tags_html if tags_html else ''}"
        f"</div>",
        unsafe_allow_html=True,
    )

    if meta.exemple:
        with st.expander("💻 Exemple", expanded=False):
            st.code(meta.exemple, language="python")


class DesignSystemModule(BaseModule[None]):
    """Module Design System — piloté avec BaseModule (Phase 4 Audit)."""

    titre = "Design System Matanne"
    icone = "🎨"
    description = "Documentation interactive auto-générée des composants UI"
    show_refresh_button = False

    def get_service_factory(self) -> Callable[[], None] | None:
        return None  # Pas de service nécessaire

    @profiler_rerun("design_system")
    def render(self) -> None:
        """Rendu principal du Design System."""
        self.render_tabs(
            {
                "🎨 Palette": _afficher_palette,
                "📏 Tokens": _afficher_tokens,
                "🧩 Composants": _afficher_catalogue,
            }
        )


# Point d'entrée standard généré par module_app
app = module_app(DesignSystemModule)
