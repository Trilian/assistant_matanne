"""
Mixins - Fonctionnalités réutilisables
Pattern Mixin pour éviter duplication code
"""
import streamlit as st
from typing import Dict, List
from abc import ABC, abstractmethod

from src.ui.feedback import ProgressTracker, show_success, show_error
from src.core.cache import Cache
from src.utils.validators import validate_required_fields


# ═══════════════════════════════════════════════════════════
# AI GENERATION MIXIN
# ═══════════════════════════════════════════════════════════

class AIGenerationMixin(ABC):
    """
    Mixin génération IA

    Ajoute capacité de génération IA à un module
    """

    @abstractmethod
    def render_ia_config(self) -> Dict:
        """
        Affiche config IA (à implémenter)

        Returns:
            Dict de configuration
        """
        pass

    @abstractmethod
    async def generate_with_ia(self, config: Dict):
        """
        Génère avec IA (à implémenter)

        Args:
            config: Configuration retournée par render_ia_config
        """
        pass

    def render_ia_tab(self):
        """Render tab IA (implémentation commune)"""
        st.markdown("### 🤖 Génération Intelligente")

        # Config spécifique module
        config = self.render_ia_config()

        # Bouton génération
        if st.button("🚀 Générer", type="primary", use_container_width=True):
            import asyncio
            asyncio.run(self.generate_with_ia(config))


# ═══════════════════════════════════════════════════════════
# EXPORT MIXIN
# ═══════════════════════════════════════════════════════════

class ExportMixin:
    """
    Mixin import/export

    Ajoute capacités I/O à un module
    """

    def export_csv(self, items: List[Dict], filename: str):
        """Export CSV"""
        if not items:
            st.warning("Aucune donnée")
            return

        try:
            csv = self.service.to_csv(items)
            st.download_button(
                "📥 Télécharger CSV",
                csv,
                f"{filename}.csv",
                "text/csv",
                use_container_width=True
            )
            show_success(f"✅ {len(items)} éléments exportés")

        except Exception as e:
            show_error(f"❌ Erreur export: {str(e)}")

    def export_json(self, items: List[Dict], filename: str):
        """Export JSON"""
        if not items:
            st.warning("Aucune donnée")
            return

        try:
            json_str = self.service.to_json(items)
            st.download_button(
                "📥 Télécharger JSON",
                json_str,
                f"{filename}.json",
                "application/json",
                use_container_width=True
            )
            show_success(f"✅ {len(items)} éléments exportés")

        except Exception as e:
            show_error(f"❌ Erreur export: {str(e)}")

    def import_csv(self, uploaded_file):
        """Import CSV"""
        try:
            content = uploaded_file.read().decode('utf-8')
            items, errors = self.service.from_csv(content)

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
                    # Validation
                    is_valid, missing = validate_required_fields(
                        item,
                        self.get_required_fields()
                    )

                    if is_valid:
                        # Pré-traitement si besoin
                        item = self.pre_create_hook(item)
                        self.service.create(item)
                        imported += 1
                        progress.update(i+1, f"✅ {item.get('nom', '?')}")
                    else:
                        progress.update(i+1, f"❌ Manque: {missing}")

                except Exception as e:
                    progress.update(i+1, f"❌ Erreur: {str(e)}")

            progress.complete(f"✅ {imported}/{len(items)} importés")
            Cache.invalidate(self.cache_key)

        except Exception as e:
            show_error(f"❌ Erreur import: {str(e)}")

    def get_required_fields(self) -> List[str]:
        """Champs requis (override si besoin)"""
        return ["nom"]


# ═══════════════════════════════════════════════════════════
# SEARCH MIXIN
# ═══════════════════════════════════════════════════════════

class SearchMixin:
    """
    Mixin recherche avancée

    Ajoute capacités recherche à un module
    """

    def search_items(
            self,
            search_term: str,
            search_fields: List[str],
            filters: Dict = None
    ) -> List:
        """
        Recherche avancée

        Args:
            search_term: Terme recherché
            search_fields: Champs où chercher
            filters: Filtres additionnels

        Returns:
            Liste items filtrés
        """
        if not search_term:
            return self.service.get_all(filters=filters or {})

        return self.service.advanced_search(
            search_term=search_term,
            search_fields=search_fields,
            filters=filters or {},
            limit=1000
        )

    def render_search_ui(self, search_fields: List[str]) -> str:
        """
        Render UI recherche

        Returns:
            Terme recherche
        """
        from src.ui.components import search_bar

        return search_bar(
            placeholder=f"Rechercher {self.schema_name}...",
            key=f"{self.schema_name}_search"
        )


# ═══════════════════════════════════════════════════════════
# STATS MIXIN
# ═══════════════════════════════════════════════════════════

class StatsMixin:
    """
    Mixin statistiques

    Ajoute calculs stats à un module
    """

    def calculate_stats(self, items: List[Dict]) -> Dict:
        """
        Calcule stats basiques

        Args:
            items: Liste items

        Returns:
            Dict stats
        """
        return {
            "total": len(items),
            "this_week": self._count_this_week(items),
            "this_month": self._count_this_month(items)
        }

    def _count_this_week(self, items: List[Dict]) -> int:
        """Compte items cette semaine"""
        from datetime import date, timedelta

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        return len([
            item for item in items
            if item.get("created_at") and item["created_at"].date() >= week_start
        ])

    def _count_this_month(self, items: List[Dict]) -> int:
        """Compte items ce mois"""
        from datetime import date

        today = date.today()
        month_start = today.replace(day=1)

        return len([
            item for item in items
            if item.get("created_at") and item["created_at"].date() >= month_start
        ])


# ═══════════════════════════════════════════════════════════
# VALIDATION MIXIN
# ═══════════════════════════════════════════════════════════

class ValidationMixin:
    """
    Mixin validation formulaires

    Ajoute validation automatique
    """

    def validate_form(self, data: Dict, schema: str) -> tuple[bool, Dict]:
        """
        Valide et sanitize formulaire

        Args:
            data: Données formulaire
            schema: Nom schéma validation

        Returns:
            (is_valid, sanitized_data)
        """
        from src.core.validation_unified import validate_and_sanitize_form

        return validate_and_sanitize_form(schema, data)