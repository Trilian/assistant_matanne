"""
Import/Export de Recettes
Formats supportés: JSON, Markdown, CSV
"""
import json
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import io

from src.core.database import get_db_context
from src.core.models import Recette, RecetteIngredient, EtapeRecette


# ===================================
# EXPORT
# ===================================

class RecetteExporter:
    """Export de recettes en différents formats"""

    @staticmethod
    def to_json(recette_ids: List[int]) -> str:
        """
        Exporte recettes en JSON

        Args:
            recette_ids: Liste des IDs à exporter

        Returns:
            String JSON
        """
        with get_db_context() as db:
            recettes = db.query(Recette).filter(
                Recette.id.in_(recette_ids)
            ).all()

            data = []

            for recette in recettes:
                recette_dict = {
                    "nom": recette.nom,
                    "description": recette.description,
                    "temps_preparation": recette.temps_preparation,
                    "temps_cuisson": recette.temps_cuisson,
                    "portions": recette.portions,
                    "difficulte": recette.difficulte,
                    "type_repas": recette.type_repas,
                    "saison": recette.saison,
                    "categorie": recette.categorie,
                    "ingredients": [
                        {
                            "nom": ing.ingredient.nom,
                            "quantite": ing.quantite,
                            "unite": ing.unite,
                            "optionnel": ing.optionnel
                        }
                        for ing in recette.ingredients
                    ],
                    "etapes": [
                        {
                            "ordre": etape.ordre,
                            "description": etape.description,
                            "duree": etape.duree
                        }
                        for etape in sorted(recette.etapes, key=lambda x: x.ordre)
                    ],
                    "tags": {
                        "rapide": recette.est_rapide,
                        "equilibre": recette.est_equilibre,
                        "bebe": recette.compatible_bebe,
                        "batch": recette.compatible_batch,
                        "congelable": recette.congelable
                    }
                }

                data.append(recette_dict)

            return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_markdown(recette: Recette) -> str:
        """
        Exporte une recette en Markdown

        Args:
            recette: Instance Recette

        Returns:
            String Markdown
        """
        md = f"# {recette.nom}\n\n"

        if recette.description:
            md += f"*{recette.description}*\n\n"

        # Métadonnées
        md += f"⏱️ **Temps:** {recette.temps_preparation}min prep + {recette.temps_cuisson}min cuisson = {recette.temps_preparation + recette.temps_cuisson}min total\n\n"
        md += f"🍽️ **Portions:** {recette.portions}\n\n"
        md += f"**Difficulté:** {recette.difficulte}\n\n"

        # Tags
        tags = []
        if recette.est_rapide:
            tags.append("⚡ Rapide")
        if recette.est_equilibre:
            tags.append("🥗 Équilibré")
        if recette.compatible_bebe:
            tags.append("👶 Bébé")
        if recette.compatible_batch:
            tags.append("🍳 Batch")

        if tags:
            md += f"**Tags:** {', '.join(tags)}\n\n"

        md += "---\n\n"

        # Ingrédients
        md += "## 🥕 Ingrédients\n\n"

        for ing in sorted(recette.ingredients, key=lambda x: x.ingredient.nom):
            optional = " *(optionnel)*" if ing.optionnel else ""
            md += f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}{optional}\n"

        md += "\n---\n\n"

        # Étapes
        md += "## 📝 Préparation\n\n"

        for etape in sorted(recette.etapes, key=lambda x: x.ordre):
            duration = f" *({etape.duree}min)*" if etape.duree else ""
            md += f"**{etape.ordre}.** {etape.description}{duration}\n\n"

        md += "---\n\n"
        md += f"*Recette exportée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n"

        return md

    @staticmethod
    def to_csv(recette_ids: List[int]) -> str:
        """
        Exporte recettes en CSV

        Args:
            recette_ids: Liste des IDs

        Returns:
            String CSV
        """
        with get_db_context() as db:
            recettes = db.query(Recette).filter(
                Recette.id.in_(recette_ids)
            ).all()

            data = []

            for recette in recettes:
                # Concaténer ingrédients
                ingredients_str = "; ".join([
                    f"{ing.quantite}{ing.unite} {ing.ingredient.nom}"
                    for ing in recette.ingredients
                ])

                # Concaténer étapes
                etapes_str = " | ".join([
                    etape.description
                    for etape in sorted(recette.etapes, key=lambda x: x.ordre)
                ])

                data.append({
                    "Nom": recette.nom,
                    "Description": recette.description or "",
                    "Temps préparation (min)": recette.temps_preparation,
                    "Temps cuisson (min)": recette.temps_cuisson,
                    "Portions": recette.portions,
                    "Difficulté": recette.difficulte,
                    "Type repas": recette.type_repas,
                    "Saison": recette.saison,
                    "Ingrédients": ingredients_str,
                    "Étapes": etapes_str,
                    "Rapide": "Oui" if recette.est_rapide else "Non",
                    "Équilibré": "Oui" if recette.est_equilibre else "Non"
                })

            df = pd.DataFrame(data)
            return df.to_csv(index=False)

    @staticmethod
    def to_pdf(recette: Recette) -> bytes:
        """
        Exporte en PDF (nécessite reportlab)

        Note: Fonction placeholder - nécessite l'installation de reportlab
        """
        # TODO: Implémenter avec reportlab si nécessaire
        raise NotImplementedError("Export PDF nécessite reportlab")


# ===================================
# IMPORT
# ===================================

class RecetteImporter:
    """Import de recettes depuis différents formats"""

    @staticmethod
    def from_json(json_str: str) -> List[Dict]:
        """
        Importe depuis JSON

        Args:
            json_str: String JSON

        Returns:
            Liste de dicts recettes validées
        """
        try:
            data = json.loads(json_str)

            # Valider structure
            if not isinstance(data, list):
                data = [data]

            validated = []

            for recipe in data:
                # Vérifier champs obligatoires
                required = ["nom", "temps_preparation", "temps_cuisson", "portions"]
                if not all(k in recipe for k in required):
                    continue

                # Valider ingrédients
                if "ingredients" not in recipe or not recipe["ingredients"]:
                    continue

                # Valider étapes
                if "etapes" not in recipe or not recipe["etapes"]:
                    continue

                validated.append(recipe)

            return validated

        except json.JSONDecodeError:
            raise ValueError("JSON invalide")

    @staticmethod
    def from_markdown(md_str: str) -> Dict:
        """
        Importe depuis Markdown (parsing simple)

        Note: Parser basique, peut nécessiter amélioration
        """
        lines = md_str.split("\n")

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": []
        }

        current_section = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Titre (nom)
            if line.startswith("# "):
                recipe["nom"] = line[2:].strip()

            # Sections
            elif line.startswith("## "):
                section_title = line[3:].lower()
                if "ingr" in section_title:
                    current_section = "ingredients"
                elif "pr" in section_title or "étape" in section_title:
                    current_section = "etapes"

            # Ingrédients
            elif current_section == "ingredients" and line.startswith("-"):
                # Parser ligne ingrédient (simple)
                ing_text = line[1:].strip()
                # Format attendu: "500 g tomates"
                parts = ing_text.split()
                if len(parts) >= 3:
                    try:
                        qty = float(parts[0])
                        unit = parts[1]
                        nom = " ".join(parts[2:])

                        recipe["ingredients"].append({
                            "nom": nom,
                            "quantite": qty,
                            "unite": unit,
                            "optionnel": False
                        })
                    except ValueError:
                        pass

            # Étapes
            elif current_section == "etapes" and line[0].isdigit():
                # Format: "1. Description"
                parts = line.split(".", 1)
                if len(parts) == 2:
                    ordre = int(parts[0])
                    description = parts[1].strip()

                    recipe["etapes"].append({
                        "ordre": ordre,
                        "description": description,
                        "duree": None
                    })

        return recipe if recipe["nom"] else None

    @staticmethod
    def from_csv(csv_str: str) -> List[Dict]:
        """
        Importe depuis CSV

        Args:
            csv_str: String CSV

        Returns:
            Liste de dicts recettes
        """
        df = pd.read_csv(io.StringIO(csv_str))

        recipes = []

        for _, row in df.iterrows():
            # Parser ingrédients
            ingredients = []
            if "Ingrédients" in row and pd.notna(row["Ingrédients"]):
                for ing_str in row["Ingrédients"].split(";"):
                    ing_str = ing_str.strip()
                    # Format: "500g tomates"
                    parts = ing_str.split()
                    if len(parts) >= 2:
                        # Extraire quantité et unité
                        qty_unit = parts[0]
                        nom = " ".join(parts[1:])

                        # Séparer quantité et unité
                        import re
                        match = re.match(r'(\d+\.?\d*)([a-zA-Z]+)', qty_unit)
                        if match:
                            qty = float(match.group(1))
                            unit = match.group(2)

                            ingredients.append({
                                "nom": nom,
                                "quantite": qty,
                                "unite": unit,
                                "optionnel": False
                            })

            # Parser étapes
            etapes = []
            if "Étapes" in row and pd.notna(row["Étapes"]):
                for idx, step_str in enumerate(row["Étapes"].split("|"), start=1):
                    etapes.append({
                        "ordre": idx,
                        "description": step_str.strip(),
                        "duree": None
                    })

            if ingredients and etapes:
                recipe = {
                    "nom": row.get("Nom", "Sans nom"),
                    "description": row.get("Description", ""),
                    "temps_preparation": int(row.get("Temps préparation (min)", 15)),
                    "temps_cuisson": int(row.get("Temps cuisson (min)", 30)),
                    "portions": int(row.get("Portions", 4)),
                    "difficulte": row.get("Difficulté", "moyen"),
                    "type_repas": row.get("Type repas", "dîner"),
                    "saison": row.get("Saison", "toute_année"),
                    "ingredients": ingredients,
                    "etapes": etapes
                }

                recipes.append(recipe)

        return recipes


# ===================================
# HELPERS STREAMLIT
# ===================================

def render_export_ui(recette_ids: List[int]):
    """
    Widget Streamlit pour l'export

    Args:
        recette_ids: IDs des recettes à exporter
    """
    import streamlit as st

    st.markdown("### 📤 Exporter les recettes")

    format_export = st.selectbox(
        "Format",
        ["JSON", "Markdown", "CSV"],
        key="export_format"
    )

    if st.button("📥 Générer l'export", use_container_width=True):
        try:
            if format_export == "JSON":
                content = RecetteExporter.to_json(recette_ids)
                filename = f"recettes_{datetime.now().strftime('%Y%m%d')}.json"
                mime = "application/json"

            elif format_export == "Markdown":
                # Pour markdown, exporter chaque recette
                with get_db_context() as db:
                    recettes = db.query(Recette).filter(Recette.id.in_(recette_ids)).all()
                    content = "\n\n---\n\n".join([
                        RecetteExporter.to_markdown(r) for r in recettes
                    ])
                filename = f"recettes_{datetime.now().strftime('%Y%m%d')}.md"
                mime = "text/markdown"

            else:  # CSV
                content = RecetteExporter.to_csv(recette_ids)
                filename = f"recettes_{datetime.now().strftime('%Y%m%d')}.csv"
                mime = "text/csv"

            st.download_button(
                label=f"💾 Télécharger ({format_export})",
                data=content,
                file_name=filename,
                mime=mime,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Erreur lors de l'export: {e}")


# Remplacer la fonction render_import_ui existante par :

def render_import_ui(service):
    """Widget Streamlit pour l'import

    Args:
        service: Service de recettes (recette_service)
    """
    import streamlit as st

    st.markdown("### 📥 Importer des recettes")

    format_import = st.selectbox(
        "Format",
        ["JSON", "Markdown", "CSV"],
        key="import_format"
    )

    uploaded_file = st.file_uploader(
        f"Choisir un fichier {format_import}",
        type=["json", "md", "csv"],
        key="import_file"
    )

    if uploaded_file:
        try:
            content = uploaded_file.read().decode("utf-8")

            # Parser selon format
            if format_import == "JSON":
                recipes = RecetteImporter.from_json(content)
            elif format_import == "Markdown":
                recipe = RecetteImporter.from_markdown(content)
                recipes = [recipe] if recipe else []
            else:  # CSV
                recipes = RecetteImporter.from_csv(content)

            if recipes:
                st.success(f"✅ {len(recipes)} recette(s) détectée(s)")

                # Afficher aperçu
                for idx, recipe in enumerate(recipes):
                    with st.expander(f"Recette {idx+1}: {recipe['nom']}", expanded=False):
                        st.write(f"**Temps:** {recipe['temps_preparation']}min + {recipe['temps_cuisson']}min")
                        st.write(f"**Ingrédients:** {len(recipe['ingredients'])}")
                        st.write(f"**Étapes:** {len(recipe['etapes'])}")

                if st.button("➕ Importer toutes les recettes", type="primary"):
                    imported_count = 0

                    for recipe in recipes:
                        try:
                            # Extraire données
                            recette_data = {
                                k: v for k, v in recipe.items()
                                if k not in ['ingredients', 'etapes']
                            }

                            # Créer avec le service passé en paramètre
                            service.create_full(
                                recette_data=recette_data,
                                ingredients_data=recipe['ingredients'],
                                etapes_data=recipe['etapes']
                            )

                            imported_count += 1

                        except Exception as e:
                            st.warning(f"Erreur pour '{recipe['nom']}': {e}")

                    st.success(f"✅ {imported_count} recette(s) importée(s)")
                    st.balloons()
                    st.rerun()

            else:
                st.warning("Aucune recette valide détectée")

        except Exception as e:
            st.error(f"Erreur lors de l'import: {e}")

# ===================================
# IMPORT DEPUIS WEB
# ===================================

def render_import_from_web_ui(service):
    """Widget Streamlit pour import depuis URL - VERSION CORRIGÉE"""
    import streamlit as st
    from src.services.web_scraper import RecipeWebScraper, RecipeImageGenerator

    st.markdown("### 🌐 Importer depuis le Web")
    st.info("💡 Supporte : Marmiton, 750g, Cuisine AZ et autres sites")

    with st.expander("📋 Sites supportés", expanded=False):
        sites = RecipeWebScraper.get_supported_sites()
        for site in sites:
            st.write(f"• {site}")

    # Input URL
    url = st.text_input(
        "🔗 URL de la recette",
        placeholder="https://www.marmiton.org/recettes/...",
        key="import_web_url"
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        auto_image = st.checkbox(
            "🖼️ Générer image automatiquement",
            value=True,
            help="Utilise Unsplash pour trouver une belle image"
        )

    with col2:
        image_keywords = st.text_input(
            "Mots-clés image (optionnel)",
            placeholder="Ex: italien, pasta",
            key="image_keywords"
        )

    # ✅ CORRECTION : Stocker la recette dans session_state
    if st.button("📥 Importer la recette", type="primary", use_container_width=True):
        if not url:
            st.error("❌ URL obligatoire")
            return

        with st.spinner("🔍 Extraction de la recette..."):
            try:
                recipe_data = RecipeWebScraper.scrape_url(url)

                if not recipe_data:
                    st.error("❌ Impossible d'extraire la recette. Vérifie l'URL ou essaie un autre site.")
                    return

                # Générer image si demandé
                if auto_image:
                    keywords = [k.strip() for k in image_keywords.split(",")] if image_keywords else []
                    recipe_data["url_image"] = RecipeImageGenerator.generate_from_unsplash(
                        recipe_data["nom"],
                        keywords
                    )

                # ✅ STOCKER dans session_state
                st.session_state.scraped_recipe = recipe_data
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

    # ✅ AFFICHER la recette stockée
    if "scraped_recipe" in st.session_state:
        recipe_data = st.session_state.scraped_recipe

        st.success(f"✅ Recette trouvée : **{recipe_data['nom']}**")

        # Afficher aperçu
        col_prev1, col_prev2 = st.columns([1, 2])

        with col_prev1:
            if recipe_data.get("url_image"):
                try:
                    st.image(recipe_data["url_image"], use_column_width=True)
                except Exception as e:
                    st.warning(f"⚠️ Image non disponible")
                    # Générer une image de fallback
                    fallback_img = f"https://via.placeholder.com/400x300/4CAF50/FFFFFF?text={recipe_data['nom'][:20]}"
                    st.image(fallback_img, use_column_width=True)

        with col_prev2:
            st.write(f"**⏱️ Temps:** {recipe_data['temps_preparation']}min + {recipe_data['temps_cuisson']}min")
            st.write(f"**🍽️ Portions:** {recipe_data['portions']}")
            st.write(f"**🥕 Ingrédients:** {len(recipe_data['ingredients'])}")
            st.write(f"**📝 Étapes:** {len(recipe_data['etapes'])}")

        # Détails ingrédients
        with st.expander("👁️ Voir les détails", expanded=False):
            if recipe_data["ingredients"]:
                st.markdown("**Ingrédients :**")
                for ing in recipe_data["ingredients"]:
                    st.write(f"• {ing['quantite']} {ing['unite']} {ing['nom']}")

            if recipe_data["etapes"]:
                st.markdown("**Étapes :**")
                for etape in recipe_data["etapes"][:3]:
                    st.write(f"{etape['ordre']}. {etape['description'][:100]}...")
                if len(recipe_data["etapes"]) > 3:
                    st.caption(f"... et {len(recipe_data['etapes']) - 3} autres étapes")

        st.markdown("---")

        # ✅ Boutons d'action HORS de l'expander
        col_btn1, col_btn2 = st.columns([2, 1])

        with col_btn1:
            if st.button("✅ Ajouter à mes recettes", type="primary", use_container_width=True, key="add_scraped_recipe"):
                try:
                    # Préparer données
                    recette_data = {
                        k: v for k, v in recipe_data.items()
                        if k not in ['ingredients', 'etapes', 'image_url']
                    }

                    # Valeurs par défaut
                    recette_data['type_repas'] = 'dîner'
                    recette_data['saison'] = 'toute_année'
                    recette_data['genere_par_ia'] = False
                    recette_data['url_image'] = recipe_data.get('url_image')
                    recette_data['est_rapide'] = (recipe_data['temps_preparation'] + recipe_data['temps_cuisson']) < 30
                    recette_data['est_equilibre'] = True

                    # Créer recette
                    recipe_id = service.create_full(
                        recette_data=recette_data,
                        ingredients_data=recipe_data['ingredients'],
                        etapes_data=recipe_data['etapes']
                    )

                    # Nettoyer session_state
                    del st.session_state.scraped_recipe

                    st.success(f"✅ Recette '{recipe_data['nom']}' importée !")
                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'import: {e}")
                    import traceback
                    st.code(traceback.format_exc())

        with col_btn2:
            if st.button("❌ Annuler", use_container_width=True, key="cancel_scraped"):
                del st.session_state.scraped_recipe
                st.rerun()