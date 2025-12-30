"""
BaseModuleUI - Interface Streamlit Unifiée
Élimine duplication entre tous les modules

Architecture:
- Configuration dict (flexibilité maximale)
- Composants réutilisables (formulaires, filtres, recherche)
- Actions standardisées (CRUD)

Gain: -300 lignes
"""
import streamlit as st
from typing import Dict, List, Optional, Callable, Any, Type
from datetime import date
from dataclasses import dataclass, field

# Core imports
from src.ui import (
    empty_state, search_bar, filter_panel, pagination,
    metrics_row, item_card, Modal, toast, DynamicList
)
from src.core.cache import Cache
from src.core.errors import handle_errors


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

@dataclass
class ModuleConfig:
    """Configuration complète d'un module"""

    # Identité
    name: str                           # "recettes", "inventaire"
    title: str                          # "🍽️ Recettes Intelligentes"
    icon: str                           # "🍽️"

    # Service
    service: Any                        # recette_service

    # Champs
    display_fields: List[Dict]          # [{"key": "nom", "label": "Nom", "type": "text"}]
    search_fields: List[str]            # ["nom", "description"]

    # Filtres
    filters_config: Dict[str, Dict]     # {"categorie": {"type": "select", ...}}

    # Stats
    stats_config: List[Dict]            # [{"label": "Total", "value_key": "total"}]

    # Actions
    actions: List[Dict]                 # [{"label": "Modifier", "callback": ..., "icon": "✏️"}]

    # États
    status_field: Optional[str] = None  # "statut"
    status_colors: Dict = field(default_factory=dict)  # {"ok": "#4CAF50"}

    # Métadonnées carte
    metadata_fields: List[str] = field(default_factory=list)  # ["temps", "portions"]
    tags_field: Optional[str] = None    # "tags"
    image_field: Optional[str] = None   # "url_image"

    # Formulaire ajout
    form_fields: Optional[List[Dict]] = None

    # Import/Export
    io_service: Optional[Any] = None
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])

    # Pagination
    items_per_page: int = 12


# ═══════════════════════════════════════════════════════════════
# BASE MODULE UI
# ═══════════════════════════════════════════════════════════════

class BaseModuleUI:
    """
    Interface Streamlit générique pour tous les modules

    Usage:
        config = ModuleConfig(...)
        ui = BaseModuleUI(config)
        ui.render()
    """

    def __init__(self, config: ModuleConfig):
        self.config = config
        self._init_session_state()

    def _init_session_state(self):
        """Initialise session state"""
        prefix = self.config.name

        if f"{prefix}_page" not in st.session_state:
            st.session_state[f"{prefix}_page"] = 1

        if f"{prefix}_filters" not in st.session_state:
            st.session_state[f"{prefix}_filters"] = {}

    # ═══════════════════════════════════════════════════════════
    # RENDER PRINCIPAL
    # ═══════════════════════════════════════════════════════════

    def render(self):
        """Point d'entrée principal"""
        st.title(self.config.title)

        # Tabs standard
        tabs = ["📋 Liste", "➕ Ajouter"]

        if self.config.io_service:
            tabs.append("📤 Import/Export")

        tab_objects = st.tabs(tabs)

        with tab_objects[0]:
            self.render_list_tab()

        with tab_objects[1]:
            self.render_add_tab()

        if self.config.io_service and len(tab_objects) > 2:
            with tab_objects[2]:
                self.render_io_tab()

    # ═══════════════════════════════════════════════════════════
    # TAB LISTE
    # ═══════════════════════════════════════════════════════════

    def render_list_tab(self):
        """Tab liste avec recherche/filtres/pagination"""
        st.subheader(f"📋 {self.config.title.split()[-1]}")

        # Barre recherche
        search = search_bar(
            placeholder=f"Rechercher...",
            key=f"{self.config.name}_search"
        )

        # Filtres
        filters = filter_panel(
            self.config.filters_config,
            key_prefix=self.config.name
        )

        st.markdown("---")

        # Charger items avec cache
        @Cache.cached(ttl=30)
        def load_items():
            # Préparer filtres pour service
            service_filters = {
                k: v for k, v in filters.items()
                if v not in ["Tous", "Toutes", None, False]
            }

            return self.config.service.advanced_search(
                search_term=search if search else None,
                search_fields=self.config.search_fields,
                filters=service_filters,
                limit=1000
            )

        items = load_items()

        if not items:
            empty_state(
                message=f"Aucun {self.config.name[:-1]} trouvé",
                icon=self.config.icon,
                subtext="Ajuste les filtres ou ajoute un élément"
            )
            return

        # Stats
        if self.config.stats_config:
            stats_data = self._compute_stats(items)
            metrics_row(stats_data, cols=len(stats_data))
            st.markdown("---")

        # Pagination
        page, per_page = pagination(
            total_items=len(items),
            items_per_page=self.config.items_per_page,
            key=f"{self.config.name}_pagination"
        )

        start = (page - 1) * per_page
        end = start + per_page
        items_page = items[start:end]

        # Affichage grille
        self._render_grid(items_page)

    def _compute_stats(self, items: List) -> List[Dict]:
        """Calcule stats depuis config"""
        stats = []

        for stat_config in self.config.stats_config:
            if "value_key" in stat_config:
                # Valeur directe
                value = len(items)  # Total par défaut
            elif "filter" in stat_config:
                # Filtrage
                filtered = [
                    i for i in items
                    if all(
                        getattr(i, k, None) == v
                        for k, v in stat_config["filter"].items()
                    )
                ]
                value = len(filtered)
            else:
                value = 0

            stats.append({
                "label": stat_config["label"],
                "value": value
            })

        return stats

    def _render_grid(self, items: List):
        """Affiche grille d'items"""
        from src.ui import grid_layout

        def render_item_card(item, key):
            # Métadonnées
            metadata = []
            for field in self.config.metadata_fields:
                if hasattr(item, field):
                    value = getattr(item, field)
                    metadata.append(str(value))

            # Tags
            tags = []
            if self.config.tags_field and hasattr(item, self.config.tags_field):
                tags = getattr(item, self.config.tags_field) or []

            # Image
            image_url = None
            if self.config.image_field and hasattr(item, self.config.image_field):
                image_url = getattr(item, self.config.image_field)

            # Statut
            status = None
            status_color = None
            if self.config.status_field and hasattr(item, self.config.status_field):
                status = getattr(item, self.config.status_field)
                status_color = self.config.status_colors.get(status)

            # Actions
            actions = [
                (action["label"], lambda a=action, i=item: a["callback"](i))
                for action in self.config.actions
            ]

            # Render
            item_card(
                title=getattr(item, "nom", str(item.id)),
                metadata=metadata,
                status=status,
                status_color=status_color,
                tags=tags,
                image_url=image_url,
                actions=actions,
                key=key
            )

        grid_layout(
            items=items,
            cols_per_row=3,
            card_renderer=render_item_card,
            key=f"{self.config.name}_grid"
        )

    # ═══════════════════════════════════════════════════════════
    # TAB AJOUT
    # ═══════════════════════════════════════════════════════════

    def render_add_tab(self):
        """Tab ajout avec formulaire dynamique"""
        st.subheader(f"➕ Ajouter {self.config.name[:-1]}")

        if not self.config.form_fields:
            st.info("Formulaire à configurer")
            return

        # DynamicList si configuré
        if any(f.get("dynamic_list") for f in self.config.form_fields):
            self._render_dynamic_form()
        else:
            self._render_standard_form()

    def _render_standard_form(self):
        """Formulaire standard avec st.form"""
        with st.form(f"{self.config.name}_add_form"):
            data = {}

            # Render tous les champs
            for field_config in self.config.form_fields:
                from src.ui import form_field

                data[field_config["name"]] = form_field(
                    field_config,
                    key_prefix=f"{self.config.name}_add"
                )

            submitted = st.form_submit_button(
                "➕ Ajouter",
                type="primary",
                use_container_width=True
            )

            if submitted:
                self._handle_create(data)

    def _render_dynamic_form(self):
        """Formulaire avec DynamicList (ingrédients, étapes, etc.)"""
        st.info("🚧 Formulaire dynamique (utiliser DynamicList existant)")

        # À implémenter selon besoins spécifiques
        # Exemple pour recettes : ingrédients + étapes
        pass

    @handle_errors(show_in_ui=True)
    def _handle_create(self, data: Dict):
        """Gère la création"""
        # Validation basique
        required = [
            f for f in self.config.form_fields
            if f.get("required", False)
        ]

        missing = [
            f["label"] for f in required
            if not data.get(f["name"])
        ]

        if missing:
            st.error(f"Champs obligatoires: {', '.join(missing)}")
            return

        # Créer
        self.config.service.create(data)

        toast(f"✅ {self.config.name[:-1].title()} créé", "success")
        Cache.invalidate(self.config.name)
        st.balloons()
        st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TAB IMPORT/EXPORT
    # ═══════════════════════════════════════════════════════════

    def render_io_tab(self):
        """Tab import/export"""
        if not self.config.io_service:
            return

        st.subheader("📤 Import/Export")

        tab_exp, tab_imp = st.tabs(["📤 Export", "📥 Import"])

        with tab_exp:
            self._render_export()

        with tab_imp:
            self._render_import()

    def _render_export(self):
        """Section export"""
        items = self.config.service.get_all(limit=1000)

        if not items:
            st.info("Aucune donnée")
            return

        st.info(f"💡 {len(items)} élément(s)")

        # Boutons export
        from src.ui import export_buttons

        export_buttons(
            data=[{"id": i.id, "nom": getattr(i, "nom", str(i.id))} for i in items],
            filename=self.config.name,
            formats=self.config.export_formats,
            key=f"{self.config.name}_export"
        )

    def _render_import(self):
        """Section import"""
        st.markdown("### Importer")

        uploaded = st.file_uploader(
            "Fichier",
            type=["csv", "json"],
            key=f"{self.config.name}_upload"
        )

        if uploaded:
            try:
                content = uploaded.read().decode("utf-8")

                # Parser selon format
                if uploaded.name.endswith(".csv"):
                    items, errors = self.config.io_service.from_csv(content)
                else:
                    items = self.config.io_service.from_json(content)
                    errors = []

                if errors:
                    with st.expander("⚠️ Erreurs"):
                        for error in errors:
                            st.warning(error)

                if items:
                    st.success(f"✅ {len(items)} élément(s)")

                    if st.button("➕ Importer", type="primary"):
                        count = 0
                        for item in items:
                            try:
                                self.config.service.create(item)
                                count += 1
                            except:
                                pass

                        toast(f"✅ {count} importé(s)", "success")
                        Cache.invalidate(self.config.name)
                        st.balloons()
                        st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# FACTORY & HELPERS
# ═══════════════════════════════════════════════════════════════

def create_module_ui(config: ModuleConfig) -> BaseModuleUI:
    """Factory pour créer une UI module"""
    return BaseModuleUI(config)


def standard_actions(
        service: Any,
        id_field: str = "id"
) -> List[Dict]:
    """Actions CRUD standard"""
    return [
        {
            "label": "👁️ Voir",
            "callback": lambda item: _view_item(item, id_field),
            "icon": "👁️"
        },
        {
            "label": "✏️ Éditer",
            "callback": lambda item: _edit_item(item, id_field),
            "icon": "✏️"
        },
        {
            "label": "🗑️ Supprimer",
            "callback": lambda item: _delete_item(service, item, id_field),
            "icon": "🗑️"
        }
    ]


def _view_item(item, id_field: str):
    """Affiche détails"""
    st.session_state.viewing_item_id = getattr(item, id_field)
    st.rerun()


def _edit_item(item, id_field: str):
    """Édite item"""
    st.session_state.editing_item_id = getattr(item, id_field)
    st.rerun()


@handle_errors(show_in_ui=True)
def _delete_item(service, item, id_field: str):
    """Supprime item avec confirmation"""
    modal = Modal(f"delete_{getattr(item, id_field)}")

    if modal.is_showing():
        st.warning("⚠️ Confirmer la suppression ?")

        if modal.confirm():
            service.delete(getattr(item, id_field))
            toast("🗑️ Supprimé", "success")
            Cache.invalidate("*")
            modal.close()

        modal.cancel()