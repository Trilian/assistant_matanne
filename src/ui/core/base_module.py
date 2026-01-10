"""
Base Module UI - Module CRUD universel générique
100% réutilisable, agnostique du domaine métier

✅ Import depuis types.py pour éviter cycle avec services/__init__.py
"""
import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field

# ✅ Import depuis types.py au lieu de base_service.py
from src.services.types import BaseService

from src.ui.components import (
    empty_state, search_bar, pagination, export_buttons
)
from src.ui.feedback import show_success, show_error
from src.core.cache import Cache


# ═══════════════════════════════════════════════════════════
# CONFIG MODULE
# ═══════════════════════════════════════════════════════════

@dataclass
class ModuleConfig:
    """
    Configuration complète d'un module CRUD

    Permet de générer automatiquement l'UI complète
    """

    # Identité
    name: str
    title: str
    icon: str

    # Service
    service: BaseService

    # Affichage
    display_fields: List[Dict] = field(default_factory=list)
    search_fields: List[str] = field(default_factory=list)

    # Filtres
    filters_config: Dict = field(default_factory=dict)

    # Stats
    stats_config: List[Dict] = field(default_factory=list)

    # Actions
    actions: List[Dict] = field(default_factory=list)

    # Statut
    status_field: Optional[str] = None
    status_colors: Dict[str, str] = field(default_factory=dict)

    # Métadonnées
    metadata_fields: List[str] = field(default_factory=list)
    image_field: Optional[str] = None

    # Formulaire
    form_fields: List[Dict] = field(default_factory=list)

    # Import/Export
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])

    # Pagination
    items_per_page: int = 20

    # Callbacks
    on_view: Optional[Callable] = None
    on_edit: Optional[Callable] = None
    on_delete: Optional[Callable] = None
    on_create: Optional[Callable] = None


# ═══════════════════════════════════════════════════════════
# BASE MODULE UI
# ═══════════════════════════════════════════════════════════

class BaseModuleUI:
    """
    Module CRUD universel

    Génère automatiquement UI complète depuis config :
    - Liste avec recherche/filtres
    - Pagination
    - Stats dynamiques
    - Actions
    - Import/Export
    - Formulaires

    Usage:
        config = ModuleConfig(
            name="recettes",
            title="Recettes",
            icon="🍽️",
            service=recette_service,
            ...
        )
        module = BaseModuleUI(config)
        module.render()
    """

    def __init__(self, config: ModuleConfig):
        self.config = config
        self.session_key = f"module_{config.name}"
        self._init_session()

    def _init_session(self):
        """Initialise session state"""
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                "current_page": 1,
                "search_term": "",
                "filters": {},
                "selected_items": [],
                "view_mode": "grid"
            }

    # ═══════════════════════════════════════════════════════
    # RENDER PRINCIPAL
    # ═══════════════════════════════════════════════════════

    def render(self):
        """Render complet du module"""

        # Header
        self._render_header()

        # Search & Filters
        self._render_search_filters()

        st.markdown("---")

        # Actions
        self._render_actions()

        # Liste items
        items = self._load_items()

        if not items:
            empty_state(
                f"Aucun {self.config.name}",
                self.config.icon
            )
            return

        # Pagination
        total = len(items)
        page = st.session_state[self.session_key]["current_page"]
        per_page = self.config.items_per_page

        start = (page - 1) * per_page
        end = start + per_page
        page_items = items[start:end]

        # Affichage
        mode = st.session_state[self.session_key]["view_mode"]

        if mode == "grid":
            self._render_grid(page_items)
        else:
            self._render_list(page_items)

        # Pagination controls
        if total > per_page:
            current, _ = pagination(total, per_page, key=f"{self.session_key}_pag")
            st.session_state[self.session_key]["current_page"] = current

    # ═══════════════════════════════════════════════════════
    # HEADER & STATS
    # ═══════════════════════════════════════════════════════

    def _render_header(self):
        """Header avec titre et stats"""
        col1, col2 = st.columns([3, 1])

        with col1:
            st.title(f"{self.config.icon} {self.config.title}")

        with col2:
            if st.button("🔄 Vue", key=f"{self.session_key}_view"):
                current = st.session_state[self.session_key]["view_mode"]
                st.session_state[self.session_key]["view_mode"] = (
                    "list" if current == "grid" else "grid"
                )
                st.rerun()

        # Stats
        if self.config.stats_config:
            self._render_stats()

    def _render_stats(self):
        """Affiche stats"""
        stats = []

        for stat_config in self.config.stats_config:
            if "value_key" in stat_config:
                value = self.config.service.count()
                stats.append({
                    "label": stat_config["label"],
                    "value": value
                })
            elif "filter" in stat_config:
                value = self.config.service.count(filters=stat_config["filter"])
                stats.append({
                    "label": stat_config["label"],
                    "value": value
                })

        if stats:
            from src.ui.components import metrics_row
            metrics_row(stats)

    # ═══════════════════════════════════════════════════════
    # RECHERCHE & FILTRES
    # ═══════════════════════════════════════════════════════

    def _render_search_filters(self):
        """Barre recherche + filtres"""
        col1, col2 = st.columns([2, 1])

        with col1:
            search = search_bar(
                placeholder=f"Rechercher {self.config.name}...",
                key=f"{self.session_key}_search"
            )
            st.session_state[self.session_key]["search_term"] = search

        with col2:
            if self.config.filters_config:
                with st.popover("🔍 Filtres"):
                    from src.ui.components import filter_panel
                    filters = filter_panel(
                        self.config.filters_config,
                        key_prefix=self.session_key
                    )
                    st.session_state[self.session_key]["filters"] = filters

    # ═══════════════════════════════════════════════════════
    # ACTIONS
    # ═══════════════════════════════════════════════════════

    def _render_actions(self):
        """Actions rapides"""
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                    "➕ Ajouter",
                    type="primary",
                    use_container_width=True,
                    key=f"{self.session_key}_add"
            ):
                if self.config.on_create:
                    self.config.on_create()
                else:
                    st.session_state[f"{self.session_key}_show_form"] = True

        with col2:
            if st.button(
                    "📥 Exporter",
                    use_container_width=True,
                    key=f"{self.session_key}_export"
            ):
                self._export_data()

        with col3:
            if st.button(
                    "🗑️ Cache",
                    use_container_width=True,
                    key=f"{self.session_key}_cache"
            ):
                Cache.invalider(self.config.name)
                show_success("Cache vidé")

    # ═══════════════════════════════════════════════════════
    # CHARGEMENT DONNÉES
    # ═══════════════════════════════════════════════════════

    def _load_items(self) -> List[Any]:
        """Charge items avec recherche/filtres"""
        session = st.session_state[self.session_key]

        search = session.get("search_term", "")
        filters = session.get("filters", {})

        # Convertir filtres UI → DB
        db_filters = {}
        for key, value in filters.items():
            if value and value not in ["Tous", "Toutes"]:
                if isinstance(value, list) and len(value) > 0:
                    db_filters[key] = {"in": value}
                else:
                    db_filters[key] = value

        # Recherche
        if search and self.config.search_fields:
            items = self.config.service.advanced_search(
                search_term=search,
                search_fields=self.config.search_fields,
                filters=db_filters,
                limit=1000
            )
        else:
            items = self.config.service.get_all(
                filters=db_filters,
                limit=1000
            )

        return items

    # ═══════════════════════════════════════════════════════
    # AFFICHAGE GRID
    # ═══════════════════════════════════════════════════════

    def _render_grid(self, items: List[Any]):
        """Affichage grille"""
        cols_per_row = 3

        for row_idx in range(0, len(items), cols_per_row):
            cols = st.columns(cols_per_row)

            for col_idx in range(cols_per_row):
                item_idx = row_idx + col_idx

                if item_idx < len(items):
                    with cols[col_idx]:
                        self._render_item_card(items[item_idx])

    def _render_item_card(self, item: Any):
        """Render carte item"""
        from src.ui.components import item_card

        item_dict = self._item_to_dict(item)

        # Titre
        title = item_dict.get(
            self.config.display_fields[0]["key"] if self.config.display_fields else "nom",
            "Sans titre"
        )

        # Métadonnées
        metadata = [
            str(item_dict[f])
            for f in self.config.metadata_fields
            if f in item_dict and item_dict[f] is not None
        ]

        # Statut
        status = None
        status_color = None
        if self.config.status_field:
            status = item_dict.get(self.config.status_field)
            status_color = self.config.status_colors.get(status)

        # Image
        image_url = None
        if self.config.image_field:
            image_url = item_dict.get(self.config.image_field)

        # Actions
        actions = [
            (action["label"], lambda i=item: action["callback"](i))
            for action in self.config.actions
        ]

        item_card(
            title=title,
            metadata=metadata,
            status=status,
            status_color=status_color,
            image_url=image_url,
            actions=actions,
            key=f"{self.session_key}_card_{item.id}"
        )

    # ═══════════════════════════════════════════════════════
    # AFFICHAGE LISTE
    # ═══════════════════════════════════════════════════════

    def _render_list(self, items: List[Any]):
        """Affichage liste"""
        for item in items:
            self._render_item_row(item)

    def _render_item_row(self, item: Any):
        """Render ligne item"""
        from src.ui.components import badge

        item_dict = self._item_to_dict(item)

        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                title = item_dict.get(
                    self.config.display_fields[0]["key"] if self.config.display_fields else "nom",
                    "Sans titre"
                )
                st.markdown(f"### {title}")

                # Métadonnées
                meta = [
                    str(item_dict[f])
                    for f in self.config.metadata_fields[:3]
                    if f in item_dict and item_dict[f]
                ]
                if meta:
                    st.caption(" • ".join(meta))

                # Statut
                if self.config.status_field:
                    status = item_dict.get(self.config.status_field)
                    if status:
                        color = self.config.status_colors.get(status, "#gray")
                        badge(status.capitalize(), color)

            with col2:
                for action in self.config.actions:
                    icon = action.get("icon", "")
                    label = action["label"]

                    if st.button(
                            f"{icon} {label}",
                            key=f"{self.session_key}_act_{item.id}_{label}",
                            use_container_width=True
                    ):
                        action["callback"](item)

            st.markdown("---")

    # ═══════════════════════════════════════════════════════
    # EXPORT
    # ═══════════════════════════════════════════════════════

    def _export_data(self):
        """Export données"""
        items = self._load_items()

        if not items:
            st.warning("Aucune donnée")
            return

        items_dict = [self._item_to_dict(i) for i in items]

        export_buttons(
            items_dict,
            filename=f"{self.config.name}_export",
            formats=self.config.export_formats,
            key=f"{self.session_key}_export_btn"
        )

    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════

    def _item_to_dict(self, item: Any) -> Dict:
        """Convertit ORM → dict"""
        if isinstance(item, dict):
            return item

        result = {}
        for column in item.__table__.columns:
            result[column.name] = getattr(item, column.name)

        # Relations
        for field in self.config.display_fields + self.config.metadata_fields:
            field_key = field if isinstance(field, str) else field.get("key")
            if hasattr(item, field_key) and field_key not in result:
                result[field_key] = getattr(item, field_key)

        return result


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_module_ui(config: ModuleConfig) -> BaseModuleUI:
    """Factory pour créer module UI"""
    return BaseModuleUI(config)