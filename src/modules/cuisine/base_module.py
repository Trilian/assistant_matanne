"""
Base Module Cuisine - FACTORISATION COMPLÈTE
Élimine 60% du code dupliqué dans les 4 modules cuisine
"""
import streamlit as st
from typing import Dict, List, Callable, Optional, Any
from abc import ABC, abstractmethod

from src.ui.feedback import smart_spinner, ProgressTracker, show_success, show_error
from src.ui.components import Modal, empty_state, badge
from src.core.validation_unified import validate_and_sanitize_form
from src.core.cache import Cache
from src.core.state import get_state


class BaseModuleCuisine(ABC):
    """
    Classe de base pour tous les modules cuisine
    Factorise : tabs, formulaires, actions, stats
    """

    def __init__(
            self,
            title: str,
            icon: str,
            service: Any,
            schema_name: str,  # "recettes", "inventaire", "courses", "planning"
            cache_key: str
    ):
        self.title = title
        self.icon = icon
        self.service = service
        self.schema_name = schema_name
        self.cache_key = cache_key

    # ═══════════════════════════════════════════════════════════
    # TEMPLATE METHOD (structure commune)
    # ═══════════════════════════════════════════════════════════

    def render(self):
        """Point d'entrée principal - Template Method"""
        st.title(f"{self.icon} {self.title}")

        tab1, tab2, tab3 = st.tabs([
            "📋 Bibliothèque",
            "🤖 IA",
            "⚙️ Paramètres"
        ])

        with tab1:
            self.render_bibliotheque()

        with tab2:
            self.render_ia()

        with tab3:
            self.render_parametres()

    # ═══════════════════════════════════════════════════════════
    # TAB 1 : BIBLIOTHÈQUE (pattern commun)
    # ═══════════════════════════════════════════════════════════

    def render_bibliotheque(self):
        """Bibliothèque commune"""

        # Actions rapides
        col1, col2 = st.columns([2, 1])

        with col1:
            if st.button("➕ Ajouter", type="primary", use_container_width=True):
                st.session_state.show_add_form = True

        with col2:
            if st.button("🤖 Générer IA", use_container_width=True):
                st.session_state.show_ia_generation = True
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

        # Filtres (spécifique à chaque module)
        filtered_items = self.render_filters(items)

        # Liste
        st.markdown(f"### {self.icon} Éléments ({len(filtered_items)})")

        for item in filtered_items:
            self.render_item_card(item)

    # ═══════════════════════════════════════════════════════════
    # TAB 2 : IA (structure commune)
    # ═══════════════════════════════════════════════════════════

    def render_ia(self):
        """Section IA commune"""
        st.markdown("### 🤖 Génération Intelligente")

        # Configuration (spécifique)
        config = self.render_ia_config()

        # Bouton génération
        if st.button("🚀 Générer", type="primary", use_container_width=True):
            self.generate_with_ia(config)

    # ═══════════════════════════════════════════════════════════
    # TAB 3 : PARAMÈTRES (structure commune)
    # ═══════════════════════════════════════════════════════════

    def render_parametres(self):
        """Paramètres communs"""
        st.markdown("### ⚙️ Paramètres")

        # Import/Export
        st.markdown("#### 📦 Import/Export")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📥 Importer")
            uploaded_file = st.file_uploader(
                "Fichier CSV/JSON",
                type=["csv", "json"],
                key=f"import_{self.schema_name}"
            )

            if uploaded_file:
                self.import_file(uploaded_file)

        with col2:
            st.markdown("##### 📤 Exporter")
            format_export = st.selectbox(
                "Format",
                ["csv", "json"],
                key=f"export_format_{self.schema_name}"
            )

            if st.button("📥 Télécharger", use_container_width=True):
                self.export_file(format_export)

        st.markdown("---")

        # Actions maintenance
        self.render_maintenance_actions()

        st.markdown("---")

        # Stats
        self.render_stats_detail()

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES COMMUNES (réutilisables)
    # ═══════════════════════════════════════════════════════════

    def render_add_form(self):
        """Formulaire ajout générique"""
        with st.expander("➕ Ajouter", expanded=True):
            with st.form(f"add_{self.schema_name}_form"):

                # Champs (spécifiques à chaque module)
                form_data = self.render_form_fields()

                col_submit, col_cancel = st.columns(2)

                with col_submit:
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
        """Gère soumission formulaire (validation + création)"""
        # ✅ Validation sécurisée
        is_valid, sanitized = validate_and_sanitize_form(
            self.schema_name,
            form_data
        )

        if not is_valid:
            return

        try:
            # Hook pré-création (si besoin de transformer les données)
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

    def import_file(self, file):
        """Import générique CSV/JSON"""
        try:
            # Lire contenu
            if file.name.endswith('.csv'):
                content = file.read().decode('utf-8')
                items, errors = self.service.from_csv(content)
            else:
                content = file.read().decode('utf-8')
                items, errors = self.service.from_json(content)

            if errors:
                st.warning(f"⚠️ {len(errors)} erreurs")
                with st.expander("Voir erreurs"):
                    for error in errors:
                        st.error(error)

            if not items:
                st.error("Aucun élément valide")
                return

            # Import avec progress
            progress = ProgressTracker(
                f"Import {self.schema_name}",
                total=len(items)
            )

            imported = 0
            for i, item in enumerate(items):
                try:
                    is_valid, sanitized = validate_and_sanitize_form(
                        self.schema_name,
                        item
                    )

                    if is_valid:
                        sanitized = self.pre_create_hook(sanitized)
                        self.service.create(sanitized)
                        imported += 1
                        progress.update(i+1, f"✅ {sanitized.get('nom', '?')}")
                    else:
                        progress.update(i+1, "❌ Invalide")

                except Exception as e:
                    progress.update(i+1, f"❌ Erreur: {str(e)}")

            progress.complete(f"✅ {imported}/{len(items)} importés")
            Cache.invalidate(self.cache_key)

        except Exception as e:
            show_error(f"❌ Erreur import: {str(e)}")

    def export_file(self, format: str):
        """Export générique CSV/JSON"""
        try:
            items = self.load_items()

            if not items:
                st.warning("Aucun élément à exporter")
                return

            if format == "csv":
                data = self.service.to_csv(items)
                st.download_button(
                    "📥 Télécharger CSV",
                    data,
                    f"{self.schema_name}_export.csv",
                    "text/csv"
                )
            else:
                data = self.service.to_json(items)
                st.download_button(
                    "📥 Télécharger JSON",
                    data,
                    f"{self.schema_name}_export.json",
                    "application/json"
                )

            show_success(f"✅ {len(items)} éléments exportés")

        except Exception as e:
            show_error(f"❌ Erreur export: {str(e)}")

    def render_maintenance_actions(self):
        """Actions maintenance communes"""
        st.markdown("#### 🧹 Maintenance")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗑️ Vider Cache", use_container_width=True):
                Cache.invalidate(self.cache_key)
                show_success("Cache vidé !")

        with col2:
            # Actions spécifiques
            self.render_custom_actions()

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES ABSTRAITES (à implémenter par chaque module)
    # ═══════════════════════════════════════════════════════════

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

    @abstractmethod
    def render_ia_config(self) -> Dict:
        """Affiche config IA et retourne paramètres"""
        pass

    @abstractmethod
    def generate_with_ia(self, config: Dict):
        """Génère avec IA"""
        pass

    # ═══════════════════════════════════════════════════════════
    # HOOKS (optionnels)
    # ═══════════════════════════════════════════════════════════

    def pre_create_hook(self, data: Dict) -> Dict:
        """Hook avant création (transformation données si besoin)"""
        return data

    def render_custom_actions(self):
        """Actions custom supplémentaires"""
        pass

    def render_stats_detail(self):
        """Stats détaillées"""
        stats = self.service.get_stats()
        st.json(stats)