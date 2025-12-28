# src/services/recettes/recette_io_service.py
"""
Service Import/Export Recettes
Migré depuis src/services/import_export.py
"""
import json
import io
from typing import List, Dict
from datetime import datetime
import pandas as pd

from src.core.database import get_db_context
from src.core.models import Recette, RecetteIngredient, EtapeRecette
from src.core.error_handler import safe_execute  # ✅ NOUVEAU

# ═══════════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════════

class RecetteExporter:
    """Export de recettes"""

    @staticmethod
    @safe_execute(fallback_value="[]", show_error=True)
    def to_json(recette_ids: List[int]) -> str:
        """Exporte en JSON"""
        with get_db_context() as db:
            recettes = db.query(Recette).filter(Recette.id.in_(recette_ids)).all()

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
                            "optionnel": ing.optionnel,
                        }
                        for ing in recette.ingredients
                    ],
                    "etapes": [
                        {
                            "ordre": etape.ordre,
                            "description": etape.description,
                            "duree": etape.duree,
                        }
                        for etape in sorted(recette.etapes, key=lambda x: x.ordre)
                    ],
                    "tags": {
                        "rapide": recette.est_rapide,
                        "equilibre": recette.est_equilibre,
                        "bebe": recette.compatible_bebe,
                        "batch": recette.compatible_batch,
                        "congelable": recette.congelable,
                    },
                }

                data.append(recette_dict)

            return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    @safe_execute(fallback_value="", show_error=True)
    def to_markdown(recette: Recette) -> str:
        """Exporte en Markdown"""
        md = f"# {recette.nom}\n\n"

        if recette.description:
            md += f"*{recette.description}*\n\n"

        md += f"⏱️ **Temps:** {recette.temps_preparation}min prep + {recette.temps_cuisson}min cuisson\n\n"
        md += f"🍽️ **Portions:** {recette.portions}\n\n"
        md += f"**Difficulté:** {recette.difficulte}\n\n"

        tags = []
        if recette.est_rapide: tags.append("⚡ Rapide")
        if recette.est_equilibre: tags.append("🥗 Équilibré")
        if recette.compatible_bebe: tags.append("👶 Bébé")
        if recette.compatible_batch: tags.append("🍳 Batch")

        if tags:
            md += f"**Tags:** {', '.join(tags)}\n\n"

        md += "---\n\n"
        md += "## 🥕 Ingrédients\n\n"

        for ing in sorted(recette.ingredients, key=lambda x: x.ingredient.nom):
            optional = " *(optionnel)*" if ing.optionnel else ""
            md += f"- {ing.quantite} {ing.unite} {ing.ingredient.nom}{optional}\n"

        md += "\n---\n\n"
        md += "## 📝 Préparation\n\n"

        for etape in sorted(recette.etapes, key=lambda x: x.ordre):
            duration = f" *({etape.duree}min)*" if etape.duree else ""
            md += f"**{etape.ordre}.** {etape.description}{duration}\n\n"

        md += "---\n\n"
        md += f"*Recette exportée le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*\n"

        return md

    @staticmethod
    @safe_execute(fallback_value="", show_error=True)
    def to_csv(recette_ids: List[int]) -> str:
        """Exporte en CSV"""
        with get_db_context() as db:
            recettes = db.query(Recette).filter(Recette.id.in_(recette_ids)).all()

            data = []

            for recette in recettes:
                ingredients_str = "; ".join(
                    [
                        f"{ing.quantite}{ing.unite} {ing.ingredient.nom}"
                        for ing in recette.ingredients
                    ]
                )

                etapes_str = " | ".join(
                    [etape.description for etape in sorted(recette.etapes, key=lambda x: x.ordre)]
                )

                data.append(
                    {
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
                        "Équilibré": "Oui" if recette.est_equilibre else "Non",
                    }
                )

            df = pd.DataFrame(data)
            return df.to_csv(index=False)


# ═══════════════════════════════════════════════════════════════
# IMPORT
# ═══════════════════════════════════════════════════════════════

class RecetteImporter:
    """Import de recettes"""

    @staticmethod
    @safe_execute(fallback_value=[], show_error=True)
    def from_json(json_str: str) -> List[Dict]:
        """Importe depuis JSON"""
        data = json.loads(json_str)

        if not isinstance(data, list):
            data = [data]

        validated = []

        for recipe in data:
            required = ["nom", "temps_preparation", "temps_cuisson", "portions"]
            if not all(k in recipe for k in required):
                continue

            if "ingredients" not in recipe or not recipe["ingredients"]:
                continue

            if "etapes" not in recipe or not recipe["etapes"]:
                continue

            validated.append(recipe)

        return validated

    @staticmethod
    @safe_execute(fallback_value=None, show_error=True)
    def from_markdown(md_str: str) -> Dict:
        """Importe depuis Markdown"""
        lines = md_str.split("\n")

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
        }

        current_section = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("# "):
                recipe["nom"] = line[2:].strip()

            elif line.startswith("## "):
                section_title = line[3:].lower()
                if "ingr" in section_title:
                    current_section = "ingredients"
                elif "pr" in section_title or "étape" in section_title:
                    current_section = "etapes"

            elif current_section == "ingredients" and line.startswith("-"):
                ing_text = line[1:].strip()
                parts = ing_text.split()
                if len(parts) >= 3:
                    try:
                        qty = float(parts[0])
                        unit = parts[1]
                        nom = " ".join(parts[2:])

                        recipe["ingredients"].append(
                            {"nom": nom, "quantite": qty, "unite": unit, "optionnel": False}
                        )
                    except ValueError:
                        pass

            elif current_section == "etapes" and line[0].isdigit():
                parts = line.split(".", 1)
                if len(parts) == 2:
                    ordre = int(parts[0])
                    description = parts[1].strip()

                    recipe["etapes"].append(
                        {"ordre": ordre, "description": description, "duree": None}
                    )

        return recipe if recipe["nom"] else None

    @staticmethod
    @safe_execute(fallback_value=[], show_error=True)
    def from_csv(csv_str: str) -> List[Dict]:
        """Importe depuis CSV"""
        df = pd.read_csv(io.StringIO(csv_str))

        recipes = []

        for _, row in df.iterrows():
            ingredients = []
            if "Ingrédients" in row and pd.notna(row["Ingrédients"]):
                for ing_str in row["Ingrédients"].split(";"):
                    ing_str = ing_str.strip()
                    parts = ing_str.split()
                    if len(parts) >= 2:
                        import re

                        match = re.match(r"(\d+\.?\d*)([a-zA-Z]+)", parts[0])
                        if match:
                            qty = float(match.group(1))
                            unit = match.group(2)
                            nom = " ".join(parts[1:])

                            ingredients.append(
                                {"nom": nom, "quantite": qty, "unite": unit, "optionnel": False}
                            )

            etapes = []
            if "Étapes" in row and pd.notna(row["Étapes"]):
                for idx, step_str in enumerate(row["Étapes"].split("|"), start=1):
                    etapes.append({"ordre": idx, "description": step_str.strip(), "duree": None})

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
                    "etapes": etapes,
                }

                recipes.append(recipe)

        return recipes