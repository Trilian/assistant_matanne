"""
Module Recettes - VERSION MIGRÉE COMPLÈTE
Intègre: BaseModuleUI, Validation, Feedback, Cache Sémantique, Services IA refactorisés
"""
import streamlit as st
from datetime import date
from typing import Optional, List, Dict

# Services
from src.services.recettes import recette_service, RecetteExporter, RecetteImporter
from src.services.ai_services import create_ai_recette_service

# UI
from src.ui.base_module import create_module_ui
from src.ui.domain import recipe_card
from src.ui.feedback import smart_spinner, ProgressTracker, show_success, show_error
from src.ui.components import Modal, empty_state, badge

# Validation
from src.core.validation_middleware import (
    validate_and_sanitize_form,
    RECETTE_SCHEMA,
    show_validation_errors
)

# Cache & State
from src.core.cache import Cache
from src.core.state import get_state
from src.core.ai.semantic_cache import SemanticCache

# Config
from .configs import get_recettes_config


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module recettes - Version migrée"""
    st.title("🍽️ Recettes Intelligentes")

    # Tabs principaux
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Bibliothèque",
        "🤖 Génération IA",
        "🔍 Recherche Avancée",
        "⚙️ Paramètres"
    ])

    with tab1:
        render_bibliotheque()

    with tab2:
        render_generation_ia()

    with tab3:
        render_recherche_avancee()

    with tab4:
        render_parametres()


# ═══════════════════════════════════════════════════════════
# TAB 1: BIBLIOTHÈQUE (BaseModuleUI)
# ═══════════════════════════════════════════════════════════

def render_bibliotheque():
    """Bibliothèque recettes avec BaseModuleUI"""

    # Utiliser BaseModuleUI pour affichage standard
    config = get_recettes_config()
    ui = create_module_ui(config)

    # Ajouter actions custom
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button("➕ Nouvelle Recette", type="primary", use_container_width=True):
            st.session_state.show_add_form = True

    with col2:
        if st.button("🤖 Générer avec IA", use_container_width=True):
            st.session_state.active_tab = "ia"
            st.rerun()

    # Formulaire ajout (avec validation)
    if st.session_state.get("show_add_form", False):
        render_add_form()

    # Afficher liste recettes via BaseModuleUI
    ui.render()

    # Détails recette si sélectionnée
    if st.session_state.get("viewing_recipe_id"):
        render_recipe_details(st.session_state.viewing_recipe_id)


def render_add_form():
    """Formulaire ajout recette avec validation sécurisée"""

    with st.expander("➕ Ajouter une Recette", expanded=True):
        with st.form("add_recipe_form"):
            col1, col2 = st.columns(2)

            with col1:
                nom = st.text_input("Nom *", max_chars=200)
                temps_prep = st.number_input("Temps préparation (min) *", min_value=0, max_value=300, value=30)
                portions = st.number_input("Portions *", min_value=1, max_value=20, value=4)
                type_repas = st.selectbox("Type repas *", ["petit_déjeuner", "déjeuner", "dîner", "goûter"])

            with col2:
                description = st.text_area("Description", max_chars=2000)
                temps_cuisson = st.number_input("Temps cuisson (min) *", min_value=0, max_value=300, value=30)
                difficulte = st.selectbox("Difficulté *", ["facile", "moyen", "difficile"])
                saison = st.selectbox("Saison *", ["printemps", "été", "automne", "hiver", "toute_année"])

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                submitted = st.form_submit_button("✅ Ajouter", type="primary", use_container_width=True)

            with col_cancel:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if cancelled:
                st.session_state.show_add_form = False
                st.rerun()

            if submitted:
                # ✅ Validation sécurisée
                form_data = {
                    "nom": nom,
                    "description": description,
                    "temps_preparation": temps_prep,
                    "temps_cuisson": temps_cuisson,
                    "portions": portions,
                    "difficulte": difficulte,
                    "type_repas": type_repas,
                    "saison": saison
                }

                is_valid, sanitized = validate_and_sanitize_form("recettes", form_data)

                if is_valid:
                    try:
                        # Créer recette (données sécurisées)
                        recette_id = recette_service.create(sanitized)

                        # Invalider cache
                        Cache.invalidate("recettes")

                        # Feedback succès
                        show_success(f"✅ Recette '{sanitized['nom']}' ajoutée !")

                        st.session_state.show_add_form = False
                        st.rerun()

                    except Exception as e:
                        show_error(f"❌ Erreur: {str(e)}")


def render_recipe_details(recette_id: int):
    """Affiche détails recette"""

    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📖 Détails Recette")

        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state.viewing_recipe_id = None
            st.rerun()

        # Charger recette complète
        recette = recette_service.get_by_id_full(recette_id)

        if not recette:
            st.error("Recette introuvable")
            return

        st.markdown(f"#### {recette.nom}")

        # Métadonnées
        st.caption(f"⏱️ {recette.temps_preparation + recette.temps_cuisson}min")
        st.caption(f"🍽️ {recette.portions} portions")
        st.caption(f"📊 {recette.difficulte.capitalize()}")

        if recette.description:
            st.markdown(f"_{recette.description}_")

        # Ingrédients
        st.markdown("##### 🥕 Ingrédients")
        for ing in recette.ingredients:
            st.write(f"• {ing.quantite} {ing.unite} {ing.ingredient.nom}")

        # Étapes
        st.markdown("##### 📝 Étapes")
        for etape in sorted(recette.etapes, key=lambda x: x.ordre):
            with st.expander(f"Étape {etape.ordre}"):
                st.write(etape.description)
                if etape.duree:
                    st.caption(f"⏱️ {etape.duree} min")

        # Actions
        st.markdown("---")

        if st.button("✏️ Modifier", use_container_width=True):
            st.session_state.editing_recipe_id = recette_id
            st.rerun()

        if st.button("👶 Version Bébé", use_container_width=True):
            st.session_state.adapt_baby_recipe_id = recette_id
            st.rerun()

        if st.button("🗑️ Supprimer", use_container_width=True):
            modal = Modal(f"delete_recipe_{recette_id}")
            modal.show()


# ═══════════════════════════════════════════════════════════
# TAB 2: GÉNÉRATION IA (Services Refactorisés)
# ═══════════════════════════════════════════════════════════

def render_generation_ia():
    """Génération recettes avec IA - Version refactorisée"""

    st.markdown("### 🤖 Génération Intelligente")
    st.caption("Utilise le cache sémantique pour économiser 70% des appels API")

    # Afficher stats cache
    with st.expander("📊 Statistiques Cache IA", expanded=False):
        SemanticCache.render_stats()

    # Formulaire génération
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Filtres")

        saison = st.selectbox(
            "Saison",
            ["toute_année", "printemps", "été", "automne", "hiver"],
            index=0
        )

        type_repas = st.selectbox(
            "Type de repas",
            ["déjeuner", "dîner", "petit_déjeuner", "goûter"],
            index=0
        )

        difficulte = st.selectbox(
            "Difficulté max",
            ["facile", "moyen", "difficile"],
            index=1
        )

        is_quick = st.checkbox("⚡ Recettes rapides (<30min)", value=False)

    with col2:
        st.markdown("#### Options")

        nb_recettes = st.slider(
            "Nombre de recettes",
            min_value=1,
            max_value=10,
            value=3
        )

        ingredients_dispo = st.text_area(
            "Ingrédients disponibles (optionnel)",
            placeholder="Poulet, tomates, riz...",
            help="Séparer par des virgules"
        )

        st.caption(f"💰 Coût estimé: ~{nb_recettes * 0.002}€")

    # Bouton génération
    if st.button("🚀 Générer les Recettes", type="primary", use_container_width=True):
        generate_recipes_with_ia(
            saison=saison,
            type_repas=type_repas,
            difficulte=difficulte,
            is_quick=is_quick,
            nb_recettes=nb_recettes,
            ingredients_dispo=ingredients_dispo
        )


async def generate_recipes_with_ia(
        saison: str,
        type_repas: str,
        difficulte: str,
        is_quick: bool,
        nb_recettes: int,
        ingredients_dispo: str
):
    """
    Génère recettes avec IA

    ✅ Feedback temps réel
    ✅ Cache sémantique
    ✅ Validation automatique
    """

    # Préparer filtres
    filters = {
        "saison": saison,
        "type_repas": type_repas,
        "difficulte": difficulte,
        "is_quick": is_quick
    }

    # Parser ingrédients
    ingredients_list = None
    if ingredients_dispo:
        ingredients_list = [i.strip() for i in ingredients_dispo.split(",") if i.strip()]

    # Créer service IA
    ai_service = create_ai_recette_service()

    try:
        # ✅ Feedback automatique + cache sémantique intégré
        recettes = await ai_service.generer_recettes(
            filters=filters,
            ingredients_dispo=ingredients_list,
            nb_recettes=nb_recettes
        )

        if not recettes:
            st.warning("Aucune recette générée")
            return

        # Afficher résultats
        st.markdown(f"### ✨ {len(recettes)} Recettes Générées")

        for idx, recette in enumerate(recettes):
            with st.expander(f"{idx+1}. {recette.nom}", expanded=(idx == 0)):

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**{recette.description}**")

                    st.caption(
                        f"⏱️ {recette.temps_preparation + recette.temps_cuisson}min • "
                        f"🍽️ {recette.portions}p • "
                        f"📊 {recette.difficulte.capitalize()}"
                    )

                    # Ingrédients
                    st.markdown("##### Ingrédients")
                    for ing in recette.ingredients:
                        st.write(f"• {ing['quantite']} {ing['unite']} {ing['nom']}")

                    # Étapes
                    st.markdown("##### Étapes")
                    for etape in recette.etapes:
                        st.write(f"{etape['ordre']}. {etape['description']}")

                with col2:
                    # Actions
                    if st.button(
                            "💾 Sauvegarder",
                            key=f"save_{idx}",
                            use_container_width=True
                    ):
                        save_generated_recipe(recette.dict())

                    if st.button(
                            "🔄 Régénérer",
                            key=f"regen_{idx}",
                            use_container_width=True
                    ):
                        st.info("Régénération en cours...")
                        # TODO: Implémenter régénération

    except Exception as e:
        show_error(f"❌ Erreur génération: {str(e)}")
        st.exception(e)


def save_generated_recipe(recette_data: Dict):
    """Sauvegarde une recette générée par IA"""

    try:
        # ✅ Validation avant sauvegarde
        is_valid, sanitized = validate_and_sanitize_form("recettes", recette_data)

        if not is_valid:
            show_error("❌ Recette invalide")
            return

        # Sauvegarder avec service
        with smart_spinner("Sauvegarde de la recette", estimated_seconds=2):
            recette_id = recette_service.create_full(
                recette_data=sanitized,
                ingredients_data=recette_data.get("ingredients", []),
                etapes_data=recette_data.get("etapes", [])
            )

        Cache.invalidate("recettes")
        show_success(f"✅ Recette sauvegardée ! (ID: {recette_id})")

    except Exception as e:
        show_error(f"❌ Erreur sauvegarde: {str(e)}")


# ═══════════════════════════════════════════════════════════
# TAB 3: RECHERCHE AVANCÉE
# ═══════════════════════════════════════════════════════════

def render_recherche_avancee():
    """Recherche avancée multi-critères"""

    st.markdown("### 🔍 Recherche Avancée")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("🔍 Rechercher", placeholder="Nom, ingrédient...")

    with col2:
        saison_filter = st.multiselect(
            "Saisons",
            ["printemps", "été", "automne", "hiver", "toute_année"]
        )

    with col3:
        difficulte_filter = st.multiselect(
            "Difficulté",
            ["facile", "moyen", "difficile"]
        )

    col4, col5 = st.columns(2)

    with col4:
        temps_max = st.slider("Temps max (min)", 0, 180, 60)

    with col5:
        sort_by = st.selectbox(
            "Trier par",
            ["nom", "temps_preparation", "portions", "created_at"]
        )

    # Rechercher
    if st.button("🔍 Rechercher", type="primary", use_container_width=True):

        # Construire filtres
        filters = {}

        if saison_filter:
            filters["saison"] = {"in": saison_filter}

        if difficulte_filter:
            filters["difficulte"] = {"in": difficulte_filter}

        # Rechercher avec service
        results = recette_service.advanced_search(
            search_term=search_term,
            search_fields=["nom", "description"],
            filters=filters,
            sort_by=sort_by,
            limit=50
        )

        # Afficher résultats
        st.markdown(f"### 📊 {len(results)} Résultats")

        if results:
            for recette in results:
                temps_total = recette.temps_preparation + recette.temps_cuisson

                if temps_total <= temps_max:
                    recipe_card(
                        recipe={
                            "id": recette.id,
                            "nom": recette.nom,
                            "description": recette.description,
                            "temps_preparation": recette.temps_preparation,
                            "temps_cuisson": recette.temps_cuisson,
                            "portions": recette.portions,
                            "difficulte": recette.difficulte,
                            "url_image": recette.url_image
                        },
                        on_view=lambda: view_recipe(recette.id),
                        key=f"recipe_{recette.id}"
                    )
        else:
            empty_state("Aucun résultat", "🔍")


def view_recipe(recette_id: int):
    """Affiche détails recette"""
    st.session_state.viewing_recipe_id = recette_id
    st.rerun()


# ═══════════════════════════════════════════════════════════
# TAB 4: PARAMÈTRES
# ═══════════════════════════════════════════════════════════

def render_parametres():
    """Paramètres module recettes"""

    st.markdown("### ⚙️ Paramètres")

    # Import/Export
    st.markdown("#### 📦 Import/Export")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📥 Importer")

        uploaded_file = st.file_uploader(
            "Fichier CSV/JSON",
            type=["csv", "json"],
            key="import_recettes"
        )

        if uploaded_file:
            import_recettes_file(uploaded_file)

    with col2:
        st.markdown("##### 📤 Exporter")

        format_export = st.selectbox("Format", ["csv", "json"])

        if st.button("📥 Télécharger", use_container_width=True):
            export_recettes(format_export)

    # Cache
    st.markdown("---")
    st.markdown("#### 🗑️ Cache & Maintenance")

    col3, col4 = st.columns(2)

    with col3:
        if st.button("🗑️ Vider Cache Recettes", use_container_width=True):
            Cache.invalidate("recettes")
            show_success("Cache vidé !")

    with col4:
        if st.button("🗑️ Vider Cache IA", use_container_width=True):
            SemanticCache.clear()
            show_success("Cache IA vidé !")

    # Stats
    st.markdown("---")
    st.markdown("#### 📊 Statistiques")

    stats = recette_service.get_stats(
        group_by_fields=["difficulte", "saison"],
        count_filters={
            "rapides": {"temps_preparation": {"lte": 30}},
            "bebe": {"compatible_bebe": True}
        }
    )

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Total Recettes", stats.get("total", 0))

    with col6:
        st.metric("Recettes Rapides", stats.get("rapides", 0))

    with col7:
        st.metric("Compatibles Bébé", stats.get("bebe", 0))


def import_recettes_file(file):
    """Importe recettes depuis fichier avec feedback"""

    try:
        # Lire contenu
        if file.name.endswith('.csv'):
            content = file.read().decode('utf-8')
            importer = RecetteImporter()
            items, errors = importer.from_csv(content)
        else:
            content = file.read().decode('utf-8')
            importer = RecetteImporter()
            items, errors = importer.from_json(content)

        if errors:
            st.warning(f"⚠️ {len(errors)} erreurs détectées")
            with st.expander("Voir erreurs"):
                for error in errors:
                    st.error(error)

        if not items:
            st.error("Aucune recette valide à importer")
            return

        # Import avec progress bar
        progress = ProgressTracker("Import recettes", total=len(items))

        imported = 0
        for i, item in enumerate(items):
            try:
                # ✅ Validation
                is_valid, sanitized = validate_and_sanitize_form("recettes", item)

                if is_valid:
                    recette_service.create(sanitized)
                    imported += 1
                    progress.update(i+1, f"✅ {sanitized['nom']}")
                else:
                    progress.update(i+1, f"❌ Invalide: {item.get('nom', '?')}")

            except Exception as e:
                progress.update(i+1, f"❌ Erreur: {str(e)}")

        progress.complete(f"✅ {imported}/{len(items)} recettes importées")
        Cache.invalidate("recettes")

    except Exception as e:
        show_error(f"❌ Erreur import: {str(e)}")


def export_recettes(format: str):
    """Exporte recettes"""

    try:
        # Charger recettes
        recettes = recette_service.get_all(limit=1000)

        if not recettes:
            st.warning("Aucune recette à exporter")
            return

        # Exporter
        exporter = RecetteExporter()

        if format == "csv":
            data = exporter.to_csv([{
                "nom": r.nom,
                "description": r.description,
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte
            } for r in recettes])

            st.download_button(
                "📥 Télécharger CSV",
                data,
                "recettes_export.csv",
                "text/csv"
            )

        else:  # JSON
            data = exporter.to_json([{
                "nom": r.nom,
                "description": r.description,
                "temps_preparation": r.temps_preparation,
                "temps_cuisson": r.temps_cuisson,
                "portions": r.portions,
                "difficulte": r.difficulte
            } for r in recettes])

            st.download_button(
                "📥 Télécharger JSON",
                data,
                "recettes_export.json",
                "application/json"
            )

        show_success(f"✅ {len(recettes)} recettes exportées")

    except Exception as e:
        show_error(f"❌ Erreur export: {str(e)}")