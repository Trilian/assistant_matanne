"""
Base Module UI - Système Universel pour tous les Modules
Génère automatiquement l'UI CRUD complète depuis une config
"""
import streamlit as st
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import date

from src.services.base_service import BaseService
from src.ui.components import (
    badge, empty_state, search_bar, filter_panel,
    pagination, metrics_row, export_buttons, item_card
)
from src.ui.feedback import show_success, show_error
from src.core.cache import Cache


# ═══════════════════════════════════════════════════════════
# CONFIG MODULE
# ═══════════════════════════════════════════════════════════

@dataclass
class ModuleConfig:
    """Configuration complète d'un module"""

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

    # Métadonnées carte
    metadata_fields: List[str] = field(default_factory=list)
    image_field: Optional[str] = None

    # Formulaire ajout
    form_fields: List[Dict] = field(default_factory=list)

    # Import/Export
    io_service: Optional[Any] = None
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])

    # Pagination
    items_per_page: int = 20

    # Callbacks custom
    on_view: Optional[Callable] = None
    on_edit: Optional[Callable] = None
    on_delete: Optional[Callable] = None
    on_create: Optional[Callable] = None


# ═══════════════════════════════════════════════════════════
# BASE MODULE UI
# ═══════════════════════════════════════════════════════════

class BaseModuleUI:
    """
    UI CRUD universel généré depuis config

    Features:
    - Liste avec recherche/filtres
    - Pagination automatique
    - Stats dynamiques
    - Actions bulk
    - Import/Export
    - Formulaires auto-générés
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
                "view_mode": "grid"  # grid ou list
            }

    def render(self):
        """Render complet du module"""

        # Header avec stats
        self._render_header()

        # Barre recherche + filtres
        self._render_search_filters()

        st.markdown("---")

        # Actions bulk
        self._render_bulk_actions()

        # Liste des items
        items = self._load_items()

        if not items:
            empty_state(
                f"Aucun {self.config.name}",
                self.config.icon
            )
            return

        # Pagination
        total_items = len(items)
        current_page = st.session_state[self.session_key]["current_page"]
        items_per_page = self.config.items_per_page

        start_idx = (current_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = items[start_idx:end_idx]

        # Affichage
        view_mode = st.session_state[self.session_key]["view_mode"]

        if view_mode == "grid":
            self._render_grid(page_items)
        else:
            self._render_list(page_items)

        # Pagination controls
        if total_items > items_per_page:
            current_page, _ = pagination(
                total_items,
                items_per_page,
                key=f"{self.session_key}_pagination"
            )
            st.session_state[self.session_key]["current_page"] = current_page

    # ═══════════════════════════════════════════════════════
    # HEADER & STATS
    # ═══════════════════════════════════════════════════════

    def _render_header(self):
        """Header avec titre et stats"""
        col1, col2 = st.columns([3, 1])

        with col1:
            st.title(f"{self.config.icon} {self.config.title}")

        with col2:
            # Bouton switch vue
            if st.button("🔄 Vue", key=f"{self.session_key}_view_switch"):
                current = st.session_state[self.session_key]["view_mode"]
                st.session_state[self.session_key]["view_mode"] = "list" if current == "grid" else "grid"
                st.rerun()

        # Stats
        if self.config.stats_config:
            stats = self._calculate_stats()
            metrics_row(stats)

    def _calculate_stats(self) -> List[Dict]:
        """Calcule stats depuis config"""
        stats = []

        for stat_config in self.config.stats_config:
            if "value_key" in stat_config:
                # Stat simple (total)
                value = self.config.service.count()
                stats.append({
                    "label": stat_config["label"],
                    "value": value
                })

            elif "filter" in stat_config:
                # Stat avec filtre
                value = self.config.service.count(filters=stat_config["filter"])
                stats.append({
                    "label": stat_config["label"],
                    "value": value
                })

        return stats

    # ═══════════════════════════════════════════════════════
    # RECHERCHE & FILTRES
    # ═══════════════════════════════════════════════════════

    def _render_search_filters(self):
        """Barre recherche + filtres"""
        col1, col2 = st.columns([2, 1])

        with col1:
            search_term = search_bar(
                placeholder=f"Rechercher {self.config.name}...",
                key=f"{self.session_key}_search"
            )
            st.session_state[self.session_key]["search_term"] = search_term

        with col2:
            if self.config.filters_config:
                with st.popover("🔍 Filtres"):
                    filters = filter_panel(
                        self.config.filters_config,
                        key_prefix=self.session_key
                    )
                    st.session_state[self.session_key]["filters"] = filters

    # ═══════════════════════════════════════════════════════
    # CHARGEMENT DONNÉES
    # ═══════════════════════════════════════════════════════

    def _load_items(self) -> List[Any]:
        """Charge items avec recherche/filtres"""
        session = st.session_state[self.session_key]

        search_term = session.get("search_term", "")
        filters = session.get("filters", {})

        # Convertir filtres UI en filtres DB
        db_filters = {}
        for key, value in filters.items():
            if value and value != "Tous" and value != "Toutes":
                if isinstance(value, list) and len(value) > 0:
                    db_filters[key] = {"in": value}
                else:
                    db_filters[key] = value

        # Recherche avancée
        if search_term and self.config.search_fields:
            items = self.config.service.advanced_search(
                search_term=search_term,
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
        """Affichage grille (cartes)"""
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
        # Extraire données
        item_dict = self._item_to_dict(item)

        # Titre
        title = item_dict.get(self.config.display_fields[0]["key"], "Sans titre")

        # Métadonnées
        metadata = []
        for field_name in self.config.metadata_fields:
            if field_name in item_dict:
                value = item_dict[field_name]
                if value is not None:
                    metadata.append(str(value))

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
        actions = []
        for action_config in self.config.actions:
            label = action_config["label"]
            callback = action_config["callback"]

            actions.append((
                label,
                lambda i=item: callback(i)
            ))

        # Render avec item_card
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
        """Affichage liste (lignes)"""
        for item in items:
            self._render_item_row(item)

    def _render_item_row(self, item: Any):
        """Render ligne item"""
        item_dict = self._item_to_dict(item)

        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                # Titre
                title = item_dict.get(self.config.display_fields[0]["key"], "Sans titre")
                st.markdown(f"### {title}")

                # Métadonnées
                meta_parts = []
                for field_name in self.config.metadata_fields[:3]:
                    if field_name in item_dict and item_dict[field_name]:
                        meta_parts.append(str(item_dict[field_name]))

                if meta_parts:
                    st.caption(" • ".join(meta_parts))

                # Statut badge
                if self.config.status_field:
                    status = item_dict.get(self.config.status_field)
                    if status:
                        color = self.config.status_colors.get(status, "#gray")
                        badge(status.capitalize(), color)

            with col2:
                # Actions
                for action_config in self.config.actions:
                    icon = action_config.get("icon", "")
                    label = action_config["label"]
                    callback = action_config["callback"]

                    if st.button(
                            f"{icon} {label}",
                            key=f"{self.session_key}_action_{item.id}_{label}",
                            use_container_width=True
                    ):
                        callback(item)

            st.markdown("---")

    # ═══════════════════════════════════════════════════════
    # BULK ACTIONS
    # ═══════════════════════════════════════════════════════

    def _render_bulk_actions(self):
        """Actions groupées"""
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                    "➕ Ajouter",
                    type="primary",
                    use_container_width=True,
                    key=f"{self.session_key}_add"
            ):
                st.session_state[f"{self.session_key}_show_add_form"] = True

        with col2:
            if self.config.io_service and self.config.export_formats:
                if st.button(
                        "📥 Exporter",
                        use_container_width=True,
                        key=f"{self.session_key}_export"
                ):
                    self._export_data()

        with col3:
            if st.button(
                    "🗑️ Vider Cache",
                    use_container_width=True,
                    key=f"{self.session_key}_clear_cache"
            ):
                Cache.invalidate(self.config.name)
                show_success("Cache vidé !")

    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════

    def _item_to_dict(self, item: Any) -> Dict:
        """Convertit item ORM en dict"""
        if isinstance(item, dict):
            return item

        result = {}
        for column in item.__table__.columns:
            value = getattr(item, column.name)
            result[column.name] = value

        # Relations
        for field in self.config.display_fields + self.config.metadata_fields:
            field_key = field if isinstance(field, str) else field.get("key")
            if hasattr(item, field_key) and field_key not in result:
                result[field_key] = getattr(item, field_key)

        return result

    def _export_data(self):
        """Export données"""
        if not self.config.io_service:
            st.warning("Export non configuré")
            return

        items = self._load_items()

        if not items:
            st.warning("Aucune donnée à exporter")
            return

        # Convertir en dicts
        items_dict = [self._item_to_dict(item) for item in items]

        # Export selon format
        export_buttons(
            items_dict,
            filename=f"{self.config.name}_export",
            formats=self.config.export_formats,
            key=f"{self.session_key}_export_btn"
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

def create_module_ui(config: ModuleConfig) -> BaseModuleUI:
    """Factory pour créer module UI"""
    return BaseModuleUI(config)