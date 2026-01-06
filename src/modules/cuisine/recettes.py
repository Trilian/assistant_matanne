"""
Module Recettes - Refactorisé avec BaseModuleCuisine
✅ -70% de code grâce aux mixins
"""
import streamlit as st
from typing import Dict, List

from .core import BaseModuleCuisine
from src.services.recettes import recette_service
from src.services.ai_services import create_ai_recette_service
from src.utils.constants import DIFFICULTES, SAISONS, TYPES_REPAS


class RecettesModule(BaseModuleCuisine):
    """Module Recettes optimisé"""

    def __init__(self):
        super().__init__(
            title="Recettes Intelligentes",
            icon="🍽️",
            service=recette_service,
            schema_name="recettes",
            cache_key="recettes"
        )
        self.ai_service = create_ai_recette_service()

    # ═══════════════════════════════════════════════════════
    # IMPLÉMENTATION MÉTHODES ABSTRAITES
    # ═══════════════════════════════════════════════════════

    def load_items(self) -> List[Dict]:
        """Charge recettes"""
        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte,
                "type_repas": r.type_repas,
                "saison": r.saison,
                "url_image": r.url_image
            }
            for r in self.service.get_all(limit=100)
        ]

    def render_stats(self, items: List[Dict]):
        """Stats recettes"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total", len(items))

        with col2:
            rapides = len([r for r in items if (r['temps_preparation'] + r['temps_cuisson']) <= 30])
            st.metric("⚡ Rapides", rapides)

        with col3:
            faciles = len([r for r in items if r['difficulte'] == 'facile'])
            st.metric("✅ Faciles", faciles)

        with col4:
            saison = len([r for r in items if r['saison'] != 'toute_année'])
            st.metric("🍂 Saison", saison)

    def render_filters(self, items: List[Dict]) -> List[Dict]:
        """Filtres recettes"""
        col1, col2, col3 = st.columns(3)

        with col1:
            saison = st.selectbox("Saison", ["Toutes"] + SAISONS)

        with col2:
            difficulte = st.selectbox("Difficulté", ["Toutes"] + DIFFICULTES)

        with col3:
            type_repas = st.selectbox("Type", ["Tous"] + TYPES_REPAS)

        # Filtrer
        filtered = items

        if saison != "Toutes":
            filtered = [r for r in filtered if r['saison'] == saison]

        if difficulte != "Toutes":
            filtered = [r for r in filtered if r['difficulte'] == difficulte]

        if type_repas != "Tous":
            filtered = [r for r in filtered if r['type_repas'] == type_repas]

        return filtered

    def render_item_card(self, item: Dict):
        """Carte recette"""
        from src.ui.components import item_card

        metadata = [
            f"{item['temps_preparation'] + item['temps_cuisson']}min",
            f"{item['portions']}p",
            item['difficulte'].capitalize()
        ]

        item_card(
            title=item['nom'],
            metadata=metadata,
            status=item['difficulte'],
            status_color={"facile": "#4CAF50", "moyen": "#FF9800", "difficile": "#f44336"}.get(item['difficulte']),
            image_url=item.get('url_image'),
            actions=[
                ("👁️ Voir", lambda: self.view_recipe(item['id'])),
                ("✏️ Éditer", lambda: self.edit_recipe(item['id']))
            ],
            key=f"recipe_{item['id']}"
        )

    def render_form_fields(self) -> Dict:
        """Champs formulaire recette"""
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom *")
            temps_prep = st.number_input("Temps prépa (min) *", 0, 300, 30)
            portions = st.number_input("Portions *", 1, 20, 4)
            type_repas = st.selectbox("Type *", TYPES_REPAS)

        with col2:
            description = st.text_area("Description")
            temps_cuisson = st.number_input("Temps cuisson (min) *", 0, 300, 30)
            difficulte = st.selectbox("Difficulté *", DIFFICULTES)
            saison = st.selectbox("Saison *", SAISONS)

        return {
            "nom": nom,
            "description": description,
            "temps_preparation": temps_prep,
            "temps_cuisson": temps_cuisson,
            "portions": portions,
            "difficulte": difficulte,
            "type_repas": type_repas,
            "saison": saison
        }

    def render_ia_config(self) -> Dict:
        """Config génération IA"""
        col1, col2 = st.columns(2)

        with col1:
            saison = st.selectbox("Saison", SAISONS, key="ia_saison")
            type_repas = st.selectbox("Type", TYPES_REPAS, key="ia_type")
            rapide = st.checkbox("⚡ Rapide (<30min)")

        with col2:
            difficulte = st.selectbox("Difficulté max", DIFFICULTES, index=1, key="ia_diff")
            nb_recettes = st.slider("Nombre", 1, 10, 3)

        ingredients = st.text_area(
            "Ingrédients dispo (optionnel)",
            placeholder="Poulet, tomates, riz..."
        )

        return {
            "saison": saison,
            "type_repas": type_repas,
            "difficulte": difficulte,
            "rapide": rapide,
            "nb_recettes": nb_recettes,
            "ingredients": ingredients
        }

    async def generate_with_ia(self, config: Dict):
        """Génération IA"""
        filters = {
            "saison": config["saison"],
            "type_repas": config["type_repas"],
            "difficulte": config["difficulte"],
            "is_quick": config["rapide"]
        }

        ingredients_list = None
        if config["ingredients"]:
            ingredients_list = [i.strip() for i in config["ingredients"].split(",")]

        try:
            recettes = await self.ai_service.generer_recettes(
                filters=filters,
                ingredients_dispo=ingredients_list,
                nb_recettes=config["nb_recettes"]
            )

            if recettes:
                st.success(f"✅ {len(recettes)} recettes générées !")
                # Afficher résultats...

        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")

    # ═══════════════════════════════════════════════════════
    # MÉTHODES CUSTOM
    # ═══════════════════════════════════════════════════════

    def view_recipe(self, recipe_id: int):
        """Affiche détails"""
        st.session_state.viewing_recipe_id = recipe_id
        st.rerun()

    def edit_recipe(self, recipe_id: int):
        """Édite recette"""
        st.session_state.editing_recipe_id = recipe_id
        st.rerun()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module"""
    module = RecettesModule()
    module.render()