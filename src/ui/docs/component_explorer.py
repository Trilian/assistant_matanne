"""
Component Explorer — Playground interactif style Storybook.

Permet de visualiser et expérimenter les composants UI en live,
modifier les props via des contrôles et voir le rendu instantané.

Usage:
    from src.ui.docs.component_explorer import ComponentExplorer

    explorer = ComponentExplorer()
    explorer.afficher()  # Dans le module design_system
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, get_type_hints

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.registry import ComponentMeta, obtenir_catalogue, obtenir_composant
from src.ui.tokens import Couleur

_keys = KeyNamespace("component_explorer")


class ComponentExplorer:
    """Explorateur de composants style Storybook.

    Fonctionnalités:
    - Navigation par catégorie
    - Contrôles dynamiques pour les props
    - Preview live du rendu
    - Code snippet auto-généré
    - Documentation inline
    """

    # Composants avec preview supportée (nom → fonction de démo)
    _DEMOS: dict[str, Callable[..., None]] = {}

    @classmethod
    def register_demo(
        cls, component_name: str
    ) -> Callable[[Callable[..., None]], Callable[..., None]]:
        """Décorateur pour enregistrer une démo de composant.

        Usage:
            @ComponentExplorer.register_demo("badge_html")
            def demo_badge(texte: str = "Badge", variante: str = "success"):
                return badge_html(texte, variante=variante)
        """

        def decorator(func: Callable[..., None]) -> Callable[..., None]:
            cls._DEMOS[component_name] = func
            return func

        return decorator

    def afficher(self) -> None:
        """Affiche l'explorateur de composants complet."""
        st.markdown(
            """
            <style>
            .explorer-container {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
            }
            .preview-panel {
                background: white;
                padding: 2rem;
                border-radius: 8px;
                min-height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .preview-dark {
                background: #1a202c;
                color: #e2e8f0;
            }
            .controls-panel {
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            .code-panel {
                background: #2d2d2d;
                color: #f0f0f0;
                padding: 1rem;
                border-radius: 8px;
                font-family: 'Fira Code', 'Consolas', monospace;
                overflow-x: auto;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Header
        st.markdown("## 🎨 Component Explorer")
        st.caption("Documentation interactive — explorez et expérimentez les composants")

        # Layout principal
        col_nav, col_main = st.columns([1, 3])

        with col_nav:
            composant_selectionne = self._afficher_navigation()

        with col_main:
            if composant_selectionne:
                self._afficher_playground(composant_selectionne)
            else:
                self._afficher_accueil()

    def _afficher_navigation(self) -> ComponentMeta | None:
        """Affiche la navigation par catégorie."""
        st.markdown("### 📁 Catégories")

        catalogue = obtenir_catalogue()

        # Forcer l'import pour remplir le catalogue
        if not catalogue:
            self._charger_composants()
            catalogue = obtenir_catalogue()

        selected_name = None

        for categorie, composants in sorted(catalogue.items()):
            with st.expander(f"{categorie.capitalize()} ({len(composants)})", expanded=False):
                for meta in sorted(composants, key=lambda m: m.nom):
                    # Bouton pour chaque composant
                    if st.button(
                        f"🔹 {meta.nom}",
                        key=_keys(f"nav_{meta.nom}"),
                        use_container_width=True,
                    ):
                        st.session_state[_keys("selected")] = meta.nom
                        selected_name = meta.nom

        # Récupérer la sélection persistante
        if not selected_name and _keys("selected") in st.session_state:
            selected_name = st.session_state[_keys("selected")]

        if selected_name:
            return obtenir_composant(selected_name)

        return None

    def _afficher_playground(self, meta: ComponentMeta) -> None:
        """Affiche le playground pour un composant."""
        # Header du composant
        st.markdown(f"### `{meta.nom}`")
        st.markdown(f"*{meta.description or 'Pas de description'}*")

        # Tags
        if meta.tags:
            tags_html = " ".join(
                f'<span style="background:{Couleur.BG_INFO};padding:4px 10px;'
                f'border-radius:12px;font-size:0.8rem;margin-right:4px;">{tag}</span>'
                for tag in meta.tags
            )
            st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("---")

        # Tabs: Preview | Contrôles | Code | Documentation
        tab_preview, tab_controls, tab_code, tab_docs = st.tabs(
            ["👁️ Preview", "🎛️ Contrôles", "💻 Code", "📚 Documentation"]
        )

        with tab_preview:
            self._afficher_preview(meta)

        with tab_controls:
            self._afficher_controles(meta)

        with tab_code:
            self._afficher_code(meta)

        with tab_docs:
            self._afficher_documentation(meta)

    def _afficher_preview(self, meta: ComponentMeta) -> None:
        """Affiche la preview du composant."""
        # Toggle light/dark mode
        col1, col2 = st.columns([3, 1])
        with col2:
            dark_mode = st.toggle("🌙 Dark", key=_keys(f"dark_{meta.nom}"))

        # Container de preview
        preview_class = "preview-panel preview-dark" if dark_mode else "preview-panel"

        st.markdown(f'<div class="{preview_class}">', unsafe_allow_html=True)

        # Vérifier si une démo existe
        if meta.nom in self._DEMOS:
            props = self._obtenir_props_session(meta.nom)
            try:
                self._DEMOS[meta.nom](**props)
            except Exception as e:
                st.error(f"Erreur de rendu: {e}")
        elif meta.exemple:
            # Essayer d'exécuter l'exemple
            st.info("💡 Preview via l'exemple enregistré")
            st.code(meta.exemple, language="python")
        else:
            st.info("🔧 Pas de preview disponible pour ce composant")

        st.markdown("</div>", unsafe_allow_html=True)

    def _afficher_controles(self, meta: ComponentMeta) -> None:
        """Affiche les contrôles pour modifier les props."""
        st.markdown("#### Paramètres")

        # Parser la signature pour extraire les paramètres
        params = self._parser_signature(meta.signature)

        if not params:
            st.info("Pas de paramètres configurables")
            return

        props = {}
        for param_name, param_info in params.items():
            param_type = param_info.get("type", "str")
            default = param_info.get("default")

            # Créer un contrôle approprié selon le type
            if param_type == "bool":
                props[param_name] = st.checkbox(
                    param_name,
                    value=default if default is not None else False,
                    key=_keys(f"ctrl_{meta.nom}_{param_name}"),
                )
            elif param_type == "int":
                props[param_name] = st.number_input(
                    param_name,
                    value=default if default is not None else 0,
                    step=1,
                    key=_keys(f"ctrl_{meta.nom}_{param_name}"),
                )
            elif param_type == "float":
                props[param_name] = st.number_input(
                    param_name,
                    value=default if default is not None else 0.0,
                    step=0.1,
                    key=_keys(f"ctrl_{meta.nom}_{param_name}"),
                )
            elif "Couleur" in str(param_type) or param_name in ("couleur", "color", "variante"):
                # Sélecteur de couleur
                options = ["success", "warning", "danger", "info", "primary", "secondary"]
                props[param_name] = st.selectbox(
                    param_name,
                    options,
                    index=options.index(str(default)) if default in options else 0,
                    key=_keys(f"ctrl_{meta.nom}_{param_name}"),
                )
            else:
                # Texte par défaut
                props[param_name] = st.text_input(
                    param_name,
                    value=str(default) if default is not None else "",
                    key=_keys(f"ctrl_{meta.nom}_{param_name}"),
                )

        # Sauvegarder dans session state
        st.session_state[_keys(f"props_{meta.nom}")] = props

        st.markdown("---")
        st.success(f"✅ {len(props)} paramètres configurés")

    def _afficher_code(self, meta: ComponentMeta) -> None:
        """Affiche le code d'utilisation."""
        st.markdown("#### Exemple d'utilisation")

        # Code snippet généré
        props = self._obtenir_props_session(meta.nom)

        # Construire le code
        args_str = ", ".join(f"{k}={repr(v)}" for k, v in props.items() if v)

        if meta.exemple:
            st.code(meta.exemple, language="python")
        else:
            code = f"{meta.nom}({args_str})" if args_str else f"{meta.nom}()"
            st.code(code, language="python")

        # Import statement
        st.markdown("#### Import")
        # Déduire le chemin d'import
        import_path = meta.fichier.replace("\\", "/")
        if "src/ui/components" in import_path:
            module = (
                import_path.split("src/ui/components/")[-1].replace(".py", "").replace("/", ".")
            )
            st.code(f"from src.ui.components.{module} import {meta.nom}", language="python")

    def _afficher_documentation(self, meta: ComponentMeta) -> None:
        """Affiche la documentation complète."""
        st.markdown("#### Description")
        st.write(meta.description or "*Pas de description*")

        st.markdown("#### Signature")
        st.code(f"def {meta.nom}{meta.signature}", language="python")

        st.markdown("#### Emplacement")
        st.text(f"📁 {meta.fichier}")
        st.text(f"📍 Ligne {meta.ligne}")

        if meta.tags:
            st.markdown("#### Tags")
            st.write(", ".join(f"`{tag}`" for tag in meta.tags))

    def _afficher_accueil(self) -> None:
        """Affiche la page d'accueil de l'explorateur."""
        st.markdown(
            """
            ### 👈 Sélectionnez un composant

            Le **Component Explorer** vous permet de :

            - 🔍 **Explorer** tous les composants du Design System
            - 🎛️ **Modifier** les props en temps réel
            - 👁️ **Prévisualiser** le rendu instantanément
            - 💻 **Copier** le code d'utilisation

            ---

            #### 📊 Statistiques
            """
        )

        catalogue = obtenir_catalogue()
        total = sum(len(c) for c in catalogue.values())

        col1, col2, col3 = st.columns(3)
        col1.metric("Composants", total)
        col2.metric("Catégories", len(catalogue))
        col3.metric("Avec démos", len(self._DEMOS))

    def _charger_composants(self) -> None:
        """Force le chargement des composants pour remplir le registry."""
        try:
            import src.ui.components.atoms  # noqa: F401
            import src.ui.components.forms  # noqa: F401
            import src.ui.components.lottie  # noqa: F401
            import src.ui.components.metrics  # noqa: F401
            import src.ui.components.system  # noqa: F401
        except ImportError:
            pass

    def _obtenir_props_session(self, nom: str) -> dict[str, Any]:
        """Récupère les props depuis la session."""
        return st.session_state.get(_keys(f"props_{nom}"), {})

    def _parser_signature(self, signature: str) -> dict[str, dict[str, Any]]:
        """Parse une signature de fonction pour extraire les paramètres."""
        params: dict[str, dict[str, Any]] = {}

        # Retirer les parenthèses
        sig = signature.strip("()")
        if not sig:
            return params

        # Parser chaque paramètre (simpliste)
        for part in sig.split(", "):
            if "=" in part:
                name_type, default = part.split("=", 1)
                name = name_type.split(":")[0].strip()
                type_hint = name_type.split(":")[1].strip() if ":" in name_type else "str"
                params[name] = {"type": type_hint, "default": eval(default.strip())}
            elif ":" in part:
                name, type_hint = part.split(":", 1)
                params[name.strip()] = {"type": type_hint.strip(), "default": None}
            else:
                name = part.strip()
                if name and name != "*" and not name.startswith("*"):
                    params[name] = {"type": "str", "default": None}

        return params


# ═══════════════════════════════════════════════════════════
# DÉMOS ENREGISTRÉES POUR LES COMPOSANTS PRINCIPAUX
# ═══════════════════════════════════════════════════════════


@ComponentExplorer.register_demo("badge_html")
def _demo_badge(
    texte: str = "Badge",
    variante: str = "success",
) -> None:
    """Démo du composant badge_html."""
    from src.ui.components.atoms import badge_html

    html = badge_html(texte, variant=variante)
    st.markdown(html, unsafe_allow_html=True)


@ComponentExplorer.register_demo("boite_info_html")
def _demo_boite_info(
    message: str = "Information importante",
    type_info: str = "info",
) -> None:
    """Démo du composant boite_info_html."""
    from src.ui.components.atoms import boite_info_html

    html = boite_info_html(message, type_info=type_info)
    st.markdown(html, unsafe_allow_html=True)


@ComponentExplorer.register_demo("afficher_lottie")
def _demo_lottie(animation: str = "success", hauteur: int = 150) -> None:
    """Démo d'une animation Lottie."""
    from src.ui.components.lottie import LottieAnimation, afficher_lottie

    try:
        anim = LottieAnimation(animation)
        afficher_lottie(anim, hauteur=hauteur, largeur=hauteur)
    except ValueError:
        st.warning(f"Animation '{animation}' non trouvée")


# Point d'accès global
explorer = ComponentExplorer()


def afficher_component_explorer() -> None:
    """Point d'entrée pour le module design_system."""
    explorer.afficher()


__all__ = [
    "ComponentExplorer",
    "afficher_component_explorer",
]
