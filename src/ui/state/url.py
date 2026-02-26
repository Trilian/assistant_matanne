"""
Synchronisation état URL avec st.query_params.

Permet le deep linking et le partage d'URL avec état
préservé (filtres, onglets, sélections, pagination).

Usage:
    from src.ui.state.url import url_state, sync_to_url, URLState

    # Décorateur pour injecter un paramètre URL
    @url_state("tab", default="overview")
    def page_content(tab: str):
        if tab == "overview":
            show_overview()
        elif tab == "details":
            show_details()

    # Synchronisation manuelle
    category = sync_to_url("category", default="all")

    # Gestionnaire de namespace
    state = URLState("recipes")
    state.set("page", 2)
    page = state.get("page", 1)

    # Widgets synchronisés avec URL
    selected_tab = tabs_with_url(["Vue", "Édition", "Stats"], param="tab")
    category = selectbox_with_url("Catégorie", categories, param="cat")
    page, start, end = pagination_with_url(total_items=100, per_page=10)
"""

from __future__ import annotations

import json
import logging
import math
from functools import wraps
from typing import Any, Callable, TypeVar

import streamlit as st

from src.core.state import rerun

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _has_query_params() -> bool:
    """Vérifie support st.query_params (Streamlit 1.30+)."""
    return hasattr(st, "query_params")


def get_url_param(key: str, default: Any = None) -> Any:
    """Récupère un paramètre URL.

    Args:
        key: Nom du paramètre
        default: Valeur par défaut si absent

    Returns:
        Valeur du paramètre ou default

    Usage:
        page = get_url_param("page", 1)
        filters = get_url_param("filters", {})
    """
    if not _has_query_params():
        return default

    params = st.query_params
    value = params.get(key)

    if value is None:
        return default

    # Tenter de parser JSON pour types complexes (dict, list)
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # Valeur simple (string)
        return value


def set_url_param(key: str, value: Any) -> None:
    """Définit un paramètre URL.

    Args:
        key: Nom du paramètre
        value: Valeur (sera sérialisée en JSON si complexe)

    Usage:
        set_url_param("page", 2)
        set_url_param("filters", {"category": "desserts"})
    """
    if not _has_query_params():
        return

    # Sérialiser les types complexes en JSON
    if isinstance(value, dict | list):
        str_value = json.dumps(value, ensure_ascii=False)
    else:
        str_value = str(value)

    st.query_params[key] = str_value


def clear_url_param(key: str) -> None:
    """Supprime un paramètre URL.

    Args:
        key: Nom du paramètre à supprimer
    """
    if not _has_query_params():
        return

    if key in st.query_params:
        del st.query_params[key]


def sync_to_url(key: str, default: Any) -> Any:
    """Synchronise une valeur avec l'URL (lecture + écriture).

    Lit la valeur depuis l'URL si présente, sinon utilise default.
    La valeur est stockée en session_state pour modifications ultérieures.

    Args:
        key: Clé du paramètre URL
        default: Valeur par défaut

    Returns:
        Valeur actuelle (depuis URL ou default)

    Usage:
        # La category sera synchronisée avec ?category=... dans l'URL
        category = sync_to_url("category", "all")

        # Modifier via session_state
        st.session_state["_url_sync_category"] = "desserts"
    """
    session_key = f"_url_sync_{key}"

    # Charger depuis URL si pas encore en session
    if session_key not in st.session_state:
        url_value = get_url_param(key, default)
        st.session_state[session_key] = url_value

    # Sync session vers URL
    current = st.session_state[session_key]
    set_url_param(key, current)

    return current


def url_state(
    param_name: str,
    default: Any = None,
) -> Callable[[F], F]:
    """Décorateur pour injecter un paramètre URL dans une fonction.

    Le paramètre URL est passé comme premier argument à la fonction.

    Args:
        param_name: Nom du paramètre URL
        default: Valeur par défaut

    Usage:
        @url_state("tab", default="home")
        def render_page(tab: str):
            if tab == "home":
                render_home()
            elif tab == "settings":
                render_settings()

        # L'URL /app?tab=settings affichera settings
        render_page()  # tab sera injecté automatiquement
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Charger depuis URL
            value = get_url_param(param_name, default)
            # Injecter comme premier argument
            return func(value, *args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


class URLState:
    """Gestionnaire d'état URL avancé avec namespace.

    Permet de gérer plusieurs paramètres URL avec préfixe
    pour éviter les collisions entre modules.

    Usage:
        state = URLState("recipes")

        # Lecture
        category = state.get("category", "all")
        page = state.get("page", 1)

        # Écriture
        state.set("category", "desserts")

        # Bulk update
        state.update({"category": "main", "page": 2})

        # Effacer tout le namespace
        state.clear_all()
    """

    def __init__(self, namespace: str = ""):
        """
        Args:
            namespace: Préfixe pour les clés URL (ex: "recipes" â†’ "recipes_page")
        """
        self.namespace = namespace
        self._prefix = f"{namespace}_" if namespace else ""

    def _key(self, name: str) -> str:
        """Génère la clé URL complète avec préfixe."""
        return f"{self._prefix}{name}"

    def get(self, name: str, default: Any = None) -> Any:
        """Récupère une valeur."""
        return get_url_param(self._key(name), default)

    def set(self, name: str, value: Any) -> None:
        """Définit une valeur."""
        set_url_param(self._key(name), value)

    def clear(self, name: str) -> None:
        """Supprime une valeur."""
        clear_url_param(self._key(name))

    def update(self, values: dict[str, Any]) -> None:
        """Met à jour plusieurs valeurs d'un coup."""
        for name, value in values.items():
            self.set(name, value)

    def get_all(self) -> dict[str, Any]:
        """Récupère toutes les valeurs du namespace."""
        if not _has_query_params():
            return {}

        result = {}
        for key in st.query_params:
            if key.startswith(self._prefix):
                name = key[len(self._prefix) :]
                result[name] = get_url_param(key)

        return result

    def clear_all(self) -> None:
        """Supprime toutes les valeurs du namespace."""
        if not _has_query_params():
            return

        to_delete = [k for k in st.query_params if k.startswith(self._prefix)]
        for key in to_delete:
            del st.query_params[key]


# ═══════════════════════════════════════════════════════════
# WIDGETS SYNCHRONISÉS AVEC URL
# ═══════════════════════════════════════════════════════════


def tabs_with_url(
    tabs: list[str],
    param: str = "tab",
    default: int = 0,
) -> int:
    """Index de l'onglet sélectionné, synchronisé avec URL.

    Args:
        tabs: Liste des labels d'onglets
        param: Nom du paramètre URL
        default: Index par défaut (0-based)

    Returns:
        Index de l'onglet sélectionné

    Usage:
        tab_index = tabs_with_url(["Vue", "Édition", "Stats"])
        tab_containers = st.tabs(["Vue", "Édition", "Stats"])

        with tab_containers[0]:
            if tab_index == 0:
                show_view()

        with tab_containers[1]:
            if tab_index == 1:
                show_edit()
    """
    url_tab = get_url_param(param)

    if url_tab and url_tab in tabs:
        selected = tabs.index(url_tab)
    else:
        selected = default

    return selected


def selectbox_with_url(
    label: str,
    options: list[Any],
    param: str,
    default: Any = None,
    format_func: Callable[[Any], str] | None = None,
    **kwargs: Any,
) -> Any:
    """st.selectbox synchronisé avec URL.

    Args:
        label: Label du selectbox
        options: Liste des options
        param: Nom du paramètre URL
        default: Valeur par défaut
        format_func: Fonction de formatage des options
        **kwargs: Arguments supplémentaires pour st.selectbox

    Returns:
        Option sélectionnée

    Usage:
        category = selectbox_with_url(
            "Catégorie",
            ["Tous", "Entrées", "Plats", "Desserts"],
            param="category",
            default="Tous",
        )
    """
    # Valeur initiale depuis URL
    url_value = get_url_param(param, default)

    # Trouver l'index
    try:
        index = options.index(url_value) if url_value in options else 0
    except ValueError:
        index = 0

    # Widget callback pour sync URL
    def on_change():
        key = kwargs.get("key", f"selectbox_{param}")
        selected = st.session_state.get(key)
        if selected is not None:
            set_url_param(param, selected)

    # Construire kwargs
    widget_kwargs = {
        **kwargs,
        "on_change": on_change,
    }
    if "key" not in widget_kwargs:
        widget_kwargs["key"] = f"selectbox_{param}"

    # Afficher selectbox
    selected = st.selectbox(
        label,
        options,
        index=index,
        format_func=format_func,
        **widget_kwargs,
    )

    # Sync initiale vers URL
    set_url_param(param, selected)

    return selected


def multiselect_with_url(
    label: str,
    options: list[Any],
    param: str,
    default: list[Any] | None = None,
    **kwargs: Any,
) -> list[Any]:
    """st.multiselect synchronisé avec URL.

    Args:
        label: Label du multiselect
        options: Liste des options
        param: Nom du paramètre URL
        default: Valeurs par défaut
        **kwargs: Arguments supplémentaires

    Returns:
        Liste des options sélectionnées
    """
    # Valeur depuis URL (JSON list)
    url_value = get_url_param(param, default or [])

    # Filtrer les valeurs valides
    if isinstance(url_value, list):
        valid_defaults = [v for v in url_value if v in options]
    else:
        valid_defaults = []

    # Callback sync
    def on_change():
        key = kwargs.get("key", f"multiselect_{param}")
        selected = st.session_state.get(key, [])
        set_url_param(param, selected)

    widget_kwargs = {
        **kwargs,
        "on_change": on_change,
    }
    if "key" not in widget_kwargs:
        widget_kwargs["key"] = f"multiselect_{param}"

    selected = st.multiselect(
        label,
        options,
        default=valid_defaults,
        **widget_kwargs,
    )

    set_url_param(param, selected)
    return selected


def pagination_with_url(
    total_items: int,
    items_per_page: int = 10,
    param: str = "page",
) -> tuple[int, int, int]:
    """Pagination synchronisée avec URL.

    Args:
        total_items: Nombre total d'items
        items_per_page: Items par page
        param: Paramètre URL pour la page

    Returns:
        (page_actuelle, start_index, end_index)

    Usage:
        page, start, end = pagination_with_url(len(items), 20)

        # Afficher les items de la page
        for item in items[start:end]:
            st.write(item)

        # La navigation est affichée automatiquement
    """
    total_pages = max(1, math.ceil(total_items / items_per_page))

    # Page depuis URL
    url_page = get_url_param(param, 1)
    try:
        current_page = max(1, min(int(url_page), total_pages))
    except (ValueError, TypeError):
        current_page = 1

    # Indices pour le slicing
    start = (current_page - 1) * items_per_page
    end = min(start + items_per_page, total_items)

    # Interface de navigation
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if current_page > 1:
            if st.button("â† Précédent", key=f"{param}_prev", use_container_width=True):
                set_url_param(param, current_page - 1)
                rerun()
        else:
            st.button("â† Précédent", key=f"{param}_prev", disabled=True, use_container_width=True)

    with col2:
        st.markdown(
            f"<div style='text-align:center; padding: 0.5rem;'>"
            f"Page **{current_page}** / {total_pages}"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col3:
        if current_page < total_pages:
            if st.button("Suivant â†’", key=f"{param}_next", use_container_width=True):
                set_url_param(param, current_page + 1)
                rerun()
        else:
            st.button("Suivant â†’", key=f"{param}_next", disabled=True, use_container_width=True)

    return current_page, start, end


def text_input_with_url(
    label: str,
    param: str,
    default: str = "",
    debounce_ms: int = 300,
    **kwargs: Any,
) -> str:
    """st.text_input synchronisé avec URL.

    Args:
        label: Label du champ
        param: Paramètre URL
        default: Valeur par défaut
        debounce_ms: Délai avant sync URL (non implémenté côté Streamlit)
        **kwargs: Arguments supplémentaires

    Returns:
        Texte saisi
    """
    url_value = get_url_param(param, default)

    def on_change():
        key = kwargs.get("key", f"text_{param}")
        value = st.session_state.get(key, "")
        if value:
            set_url_param(param, value)
        else:
            clear_url_param(param)

    widget_kwargs = {
        **kwargs,
        "on_change": on_change,
    }
    if "key" not in widget_kwargs:
        widget_kwargs["key"] = f"text_{param}"

    value = st.text_input(label, value=url_value, **widget_kwargs)

    return value


# ═══════════════════════════════════════════════════════════
# DEEP LINK STATE — Multi-niveaux page → onglet → filtre → item
# Innovation 1.3 du rapport d'audit
# ═══════════════════════════════════════════════════════════


class DeepLinkState:
    """Système de deep linking multi-niveaux complet.

    Permet de bookmarker/partager un état complet:
        /app?tab=recettes&filter=dessert&item=42&view=details

    Niveaux supportés:
    1. page   — Géré par st.navigation (url_path)
    2. tab    — Onglet actif dans la page
    3. filter — Filtres appliqués (catégorie, recherche, date)
    4. item   — Élément sélectionné (ID recette, activité, etc.)
    5. view   — Vue active (liste, détails, édition)

    Usage:
        deep = DeepLinkState("cuisine")

        # Restaurer l'état depuis l'URL
        tab = deep.tab("planificateur")  # ?cuisine_tab=...
        filtre = deep.filter("categorie", "tous")  # ?cuisine_f_categorie=...
        item_id = deep.item()  # ?cuisine_item=...
        vue = deep.view("liste")  # ?cuisine_view=...

        # Construire un lien partageable
        link = deep.build_link(tab="recettes", filter={"cat": "dessert"}, item=42)

        # Naviguer vers un état complet
        deep.navigate(tab="batch", filter={"semaine": "2025-08"})

        # Effacer tous les filtres
        deep.clear_filters()
    """

    def __init__(self, namespace: str):
        """
        Args:
            namespace: Préfixe du module (ex: "cuisine", "famille", "maison")
        """
        self.namespace = namespace
        self._url = URLState(namespace)

    # ─── Niveau 2: Onglet ───

    def tab(self, default: str = "") -> str:
        """Récupère l'onglet actif depuis l'URL.

        Args:
            default: Onglet par défaut

        Returns:
            Nom de l'onglet actif
        """
        return self._url.get("tab", default) or default

    def set_tab(self, tab_name: str) -> None:
        """Change l'onglet actif et met à jour l'URL.

        Args:
            tab_name: Nom de l'onglet
        """
        self._url.set("tab", tab_name)

    # ─── Niveau 3: Filtres ───

    def filter(self, key: str, default: Any = None) -> Any:
        """Récupère un filtre depuis l'URL.

        Args:
            key: Clé du filtre (ex: "categorie", "recherche", "date_debut")
            default: Valeur par défaut

        Returns:
            Valeur du filtre
        """
        return self._url.get(f"f_{key}", default)

    def set_filter(self, key: str, value: Any) -> None:
        """Définit un filtre et met à jour l'URL.

        Args:
            key: Clé du filtre
            value: Valeur du filtre
        """
        if value is None or value == "" or value == []:
            self._url.clear(f"f_{key}")
        else:
            self._url.set(f"f_{key}", value)

    def get_filters(self) -> dict[str, Any]:
        """Récupère tous les filtres actifs.

        Returns:
            Dict des filtres {key: value}
        """
        all_params = self._url.get_all()
        return {
            k[2:]: v  # Enlever le préfixe "f_"
            for k, v in all_params.items()
            if k.startswith("f_")
        }

    def clear_filters(self) -> None:
        """Supprime tous les filtres de l'URL."""
        all_params = self._url.get_all()
        for key in all_params:
            if key.startswith("f_"):
                self._url.clear(key)

    # ─── Niveau 4: Item sélectionné ───

    def item(self, default: Any = None) -> Any:
        """Récupère l'item sélectionné depuis l'URL.

        Args:
            default: Valeur par défaut

        Returns:
            ID ou identifiant de l'item sélectionné
        """
        value = self._url.get("item", default)
        # Tenter conversion en int pour les IDs numériques
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value
        return value

    def set_item(self, item_id: Any) -> None:
        """Sélectionne un item et met à jour l'URL.

        Args:
            item_id: ID de l'item (None pour désélectionner)
        """
        if item_id is None:
            self._url.clear("item")
        else:
            self._url.set("item", item_id)

    # ─── Niveau 5: Vue ───

    def view(self, default: str = "liste") -> str:
        """Récupère la vue active depuis l'URL.

        Args:
            default: Vue par défaut ("liste", "details", "edition", "grille")

        Returns:
            Nom de la vue active
        """
        return self._url.get("view", default) or default

    def set_view(self, view_name: str) -> None:
        """Change la vue active.

        Args:
            view_name: Nom de la vue
        """
        self._url.set("view", view_name)

    # ─── Navigation complète ───

    def navigate(
        self,
        tab: str | None = None,
        filter: dict[str, Any] | None = None,
        item: Any = None,
        view: str | None = None,
        clear_previous: bool = False,
    ) -> None:
        """Navigue vers un état complet d'un coup.

        Args:
            tab: Onglet cible
            filter: Filtres à appliquer
            item: Item à sélectionner
            view: Vue à activer
            clear_previous: Effacer l'état précédent avant

        Usage:
            deep.navigate(
                tab="recettes",
                filter={"categorie": "dessert", "recherche": "tarte"},
                item=42,
                view="details",
            )
        """
        if clear_previous:
            self._url.clear_all()

        if tab is not None:
            self.set_tab(tab)
        if filter:
            for k, v in filter.items():
                self.set_filter(k, v)
        if item is not None:
            self.set_item(item)
        if view is not None:
            self.set_view(view)

    def build_link(
        self,
        tab: str | None = None,
        filter: dict[str, Any] | None = None,
        item: Any = None,
        view: str | None = None,
    ) -> str:
        """Construit un lien partageable avec l'état spécifié.

        Returns:
            Fragment de query string (ex: "?cuisine_tab=recettes&cuisine_item=42")
        """
        params: dict[str, str] = {}

        if tab is not None:
            params[f"{self.namespace}_tab"] = str(tab)
        if filter:
            for k, v in filter.items():
                val = json.dumps(v) if isinstance(v, dict | list) else str(v)
                params[f"{self.namespace}_f_{k}"] = val
        if item is not None:
            params[f"{self.namespace}_item"] = str(item)
        if view is not None:
            params[f"{self.namespace}_view"] = str(view)

        if not params:
            return ""

        from urllib.parse import urlencode

        return "?" + urlencode(params)

    def get_state_snapshot(self) -> dict[str, Any]:
        """Capture complète de l'état deep link actuel.

        Returns:
            Dict avec tab, filters, item, view
        """
        return {
            "tab": self.tab(),
            "filters": self.get_filters(),
            "item": self.item(),
            "view": self.view(),
        }

    def restore_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Restaure un état depuis un snapshot.

        Args:
            snapshot: Dict capturé par get_state_snapshot()
        """
        self.navigate(
            tab=snapshot.get("tab"),
            filter=snapshot.get("filters"),
            item=snapshot.get("item"),
            view=snapshot.get("view"),
            clear_previous=True,
        )

    # ─── Widget helpers ───

    def tabs_synced(self, labels: list[str], default: int = 0) -> int:
        """Tabs synchronisés avec le deep link.

        Args:
            labels: Labels des onglets
            default: Index par défaut

        Returns:
            Index de l'onglet sélectionné (0-based)
        """
        current_tab = self.tab()

        if current_tab and current_tab in labels:
            return labels.index(current_tab)

        return default

    def selectbox_synced(
        self,
        label: str,
        options: list[Any],
        filter_key: str,
        default: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Selectbox synchronisé avec le deep link filtre.

        Args:
            label: Label du selectbox
            options: Options disponibles
            filter_key: Clé du filtre à synchroniser
            default: Valeur par défaut
            **kwargs: Args supplémentaires pour st.selectbox
        """
        return selectbox_with_url(
            label=label,
            options=options,
            param=f"{self.namespace}_f_{filter_key}",
            default=default,
            **kwargs,
        )

    def search_synced(
        self,
        label: str = "🔍 Recherche",
        filter_key: str = "recherche",
        **kwargs: Any,
    ) -> str:
        """Champ de recherche synchronisé avec le deep link.

        Args:
            label: Label du champ
            filter_key: Clé du filtre recherche
        """
        return text_input_with_url(
            label=label,
            param=f"{self.namespace}_f_{filter_key}",
            **kwargs,
        )
