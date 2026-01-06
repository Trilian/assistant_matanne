"""
Base Module Cuisine - Classe abstraite optimisée avec Mixins
Élimine 60% duplication, architecture DRY
"""
import streamlit as st
from typing import Dict, List, Any
from abc import ABC, abstractmethod

from .mixins import (
    AIGenerationMixin,
    ExportMixin,
    SearchMixin,
    StatsMixin,
    ValidationMixin
)
from src.ui.feedback import show_success, show_error
from src.ui.components import empty_state
from src.core.cache import Cache


class BaseModuleCuisine(
    ABC,
    AIGenerationMixin,
    ExportMixin,
    SearchMixin,
    StatsMixin,
    ValidationMixin
):
    """
    Base abstraite pour modules cuisine

    Composition de Mixins :
    - AIGenerationMixin : Génération IA
    - ExportMixin : Import/Export
    - SearchMixin : Recherche avancée
    - StatsMixin : Calculs statistiques
    - ValidationMixin : Validation formulaires

    Usage:
        class RecettesModule(BaseModuleCuisine):
            def __init__(self):
                super().__init__(
                    title="Recettes",
                    icon="🍽️",
                    service=recette_service,
                    schema_name="recettes",
                    cache_key="recettes"
                )

            def load_items(self):
                return self.service.get_all()

            # ... implémenter méthodes abstraites
    """

    def __init__(
            self,
            title: str,
            icon: str,
            service: Any,
            schema_name: str,
            cache_key: str
    ):
        self.title = title
        self.icon = icon
        self.service = service
        self.schema_name = schema_name
        self.cache_key = cache_key

    # ═══════════════════════════════════════════════════════
    # TEMPLATE METHOD (structure commune)
    # ═══════════════════════════════════════════════════════

    def render(self):
        """Point d'entrée principal"""
        st.title(f"{self.icon} {self.title}")

        tab1, tab2, tab3 = st.tabs([
            "📋 Bibliothèque",
            "🤖 IA",
            "⚙️ Paramètres"
        ])

        with tab1:
            self.render_bibliotheque()

        with tab2:
            self.render_ia_tab()  # Fourni par AIGenerationMixin

        with tab3:
            self.render_parametres()

    # ═══════════════════════════════════════════════════════
    # TAB 1 : BIBLIOTHÈQUE
    # ═══════════════════════════════════════════════════════

    def render_bibliotheque(self):
        """Bibliothèque (override si besoin structure différente)"""

        # Actions rapides
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("➕ Ajouter", type="primary", use_container_width=True):
                st.session_state.show_add_form = True

        with col2:
            if st.button("🤖 IA", use_container_width=True):
                st.session_state.active_tab = 1
                st.rerun()

        # Formulaire ajout
        if st.session_state.get("show_add_form", False):
            self.render_add_form()

        # Charger données
        items = self.load_items()

        if not items:
            empty_state(
                f"Aucun {self.schema_name}",
                self.icon,
                "Ajoute-en un ou génère avec l'IA"
            )
            return

        # Stats
        self.render_stats(items)

        st.markdown("---")

        # Filtres
        filtered = self.render_filters(items)

        # Liste
        st.markdown(f"### {self.icon} Éléments ({len(filtered)})")

        for item in filtered:
            self.render_item_card(item)

    # ═══════════════════════════════════════════════════════
    # TAB 3 : PARAMÈTRES
    # ═══════════════════════════════════════════════════════

    def render_parametres(self):
        """Paramètres communs"""
        st.markdown("### ⚙️ Paramètres")

        # Import/Export
        st.markdown("#### 📦 Import/Export")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📥 Importer")
            uploaded = st.file_uploader(
                "Fichier CSV",
                type=["csv"],
                key=f"import_{self.schema_name}"
            )

            if uploaded:
                self.import_csv(uploaded)  # Fourni par ExportMixin

        with col2:
            st.markdown("##### 📤 Exporter")

            items = self.load_items()

            if items:
                items_dict = [self._item_to_dict(i) for i in items]

                if st.button("📥 CSV", use_container_width=True):
                    self.export_csv(items_dict, self.schema_name)

                if st.button("📥 JSON", use_container_width=True):
                    self.export_json(items_dict, self.schema_name)

        st.markdown("---")

        # Actions maintenance
        self.render_maintenance()

        st.markdown("---")

        # Stats détaillées
        self.render_stats_detail()

    # ═══════════════════════════════════════════════════════
    # FORMULAIRE AJOUT
    # ═══════════════════════════════════════════════════════

    def render_add_form(self):
        """Formulaire ajout générique"""
        with st.expander("➕ Ajouter", expanded=True):
            with st.form(f"add_{self.schema_name}_form"):

                # Champs (spécifiques module)
                form_data = self.render_form_fields()

                col_sub, col_cancel = st.columns(2)

                with col_sub:
                    submitted = st.form_submit_button(
                        "✅ Ajouter",
                        type="primary",
                        use_container_width=True
                    )

                with col_cancel:
                    cancelled = st.form_submit_button(
                        "❌ Annuler",
                        use_container_width=True
                    )

                if cancelled:
                    st.session_state.show_add_form = False
                    st.rerun()

                if submitted:
                    self.handle_form_submit(form_data)

    def handle_form_submit(self, form_data: Dict):
        """Gère soumission formulaire"""
        # Validation
        is_valid, sanitized = self.validate_form(form_data, self.schema_name)

        if not is_valid:
            return

        try:
            # Hook pré-création
            sanitized = self.pre_create_hook(sanitized)

            # Créer
            self.service.create(sanitized)

            # Invalider cache
            Cache.invalidate(self.cache_key)

            show_success(f"✅ {self.schema_name.capitalize()} ajouté !")

            st.session_state.show_add_form = False
            st.rerun()

        except Exception as e:
            show_error(f"❌ Erreur: {str(e)}")

    # ═══════════════════════════════════════════════════════
    # MAINTENANCE
    # ═══════════════════════════════════════════════════════

    def render_maintenance(self):
        """Actions maintenance"""
        st.markdown("#### 🧹 Maintenance")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Vider Cache", use_container_width=True):
                Cache.invalidate(self.cache_key)
                show_success("Cache vidé")

        with col2:
            # Actions custom
            self.render_custom_actions()

    def render_stats_detail(self):
        """Stats détaillées"""
        items = self.load_items()
        stats = self.calculate_stats(items)  # Fourni par StatsMixin

        st.json(stats)

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

        return result

    # ═══════════════════════════════════════════════════════
    # MÉTHODES ABSTRAITES (à implémenter)
    # ═══════════════════════════════════════════════════════

    @abstractmethod
    def load_items(self) -> List[Dict]:
        """Charge les données"""
        pass

    @abstractmethod
    def render_stats(self, items: List[Dict]):
        """Affiche statistiques"""
        pass

    @abstractmethod
    def render_filters(self, items: List[Dict]) -> List[Dict]:
        """Affiche filtres et retourne items filtrés"""
        pass

    @abstractmethod
    def render_item_card(self, item: Dict):
        """Affiche une carte item"""
        pass

    @abstractmethod
    def render_form_fields(self) -> Dict:
        """Affiche champs formulaire et retourne données"""
        pass

    # ═══════════════════════════════════════════════════════
    # HOOKS (optionnels, override si besoin)
    # ═══════════════════════════════════════════════════════

    def pre_create_hook(self, data: Dict) -> Dict:
        """Hook avant création (transformation données)"""
        return data

    def render_custom_actions(self):
        """Actions custom supplémentaires"""
        pass