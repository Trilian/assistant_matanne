"""
Parsers de recettes depuis HTML.

Classes de parsing spécialisées par site (Marmiton, CuisineAZ, etc.)
et parser générique utilisant schema.org et heuristiques.

Inclut les schémas Pydantic pour les recettes importées.
"""

import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class ImportedIngredient(BaseModel):
    """Ingrédient importé."""

    nom: str
    quantite: float | None = None
    unite: str = ""


class ImportedRecipe(BaseModel):
    """Recette importée depuis une URL."""

    nom: str = ""
    description: str = ""
    temps_preparation: int = 0  # minutes
    temps_cuisson: int = 0  # minutes
    portions: int = 4
    difficulte: str = "moyen"
    categorie: str = ""

    ingredients: list[ImportedIngredient] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list)

    source_url: str = ""
    source_site: str = ""
    image_url: str | None = None

    confiance_score: float = 0.0  # Score de confiance de l'extraction


class ImportResult(BaseModel):
    """Résultat d'un import."""

    success: bool = False
    message: str = ""
    recipe: ImportedRecipe | None = None
    errors: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# PARSERS SPÉCIALISÉS PAR SITE
# ═══════════════════════════════════════════════════════════


class RecipeParser:
    """Parser de base pour les recettes."""

    @staticmethod
    def clean_text(text: str | None) -> str:
        """Nettoie le texte."""
        if not text:
            return ""
        return " ".join(text.strip().split())

    @staticmethod
    def parse_duration(text: str) -> int:
        """Parse une durée en minutes."""
        if not text:
            return 0

        text = text.lower()
        minutes = 0

        # Heures
        hours_match = re.search(r"(\d+)\s*h", text)
        if hours_match:
            minutes += int(hours_match.group(1)) * 60

        # Minutes
        mins_match = re.search(r"(\d+)\s*(?:min|m(?:inute)?s?)", text)
        if mins_match:
            minutes += int(mins_match.group(1))

        # Si juste un nombre, supposer minutes
        if minutes == 0:
            just_number = re.search(r"^(\d+)$", text.strip())
            if just_number:
                minutes = int(just_number.group(1))

        return minutes

    @staticmethod
    def parse_portions(text: str) -> int:
        """Parse le nombre de portions."""
        if not text:
            return 4

        match = re.search(r"(\d+)", text)
        if match:
            portions = int(match.group(1))
            return min(max(portions, 1), 20)  # Entre 1 et 20
        return 4

    @staticmethod
    def parse_ingredient(text: str) -> ImportedIngredient:
        """Parse une ligne d'ingrédient."""
        text = RecipeParser.clean_text(text)

        if not text:
            return ImportedIngredient(nom="")

        # Patterns pour quantite + unite + nom
        # Ex: "200 g de farine", "2 oeufs", "1 cuillere a soupe de sel"
        patterns = [
            r"^(\d+(?:[.,]\d+)?)\s*(g|kg|ml|cl|l|cuill[eè]re[s]?\s*(?:[aà]\s*)?(?:soupe|caf[eé])?|c\.?\s*[aà]?\s*[sc]\.?|pinc[eé]e[s]?|sachet[s]?|tranche[s]?|feuille[s]?|gousse[s]?|brin[s]?)\s*(?:de\s*|d[\x27\x27])?\s*(.+)",
            r"^(\d+(?:[.,]\d+)?)\s+(.+)",  # Nombre + reste
        ]

        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    quantite_str, unite, nom = groups
                    try:
                        quantite = float(quantite_str.replace(",", "."))
                    except (ValueError, TypeError):
                        quantite = None
                    return ImportedIngredient(
                        nom=nom.strip(), quantite=quantite, unite=unite.strip()
                    )
                elif len(groups) == 2:
                    quantite_str, nom = groups
                    try:
                        quantite = float(quantite_str.replace(",", "."))
                    except (ValueError, TypeError):
                        quantite = None
                    return ImportedIngredient(nom=nom.strip(), quantite=quantite, unite="")

        # Pas de pattern trouvé, garder le texte entier comme nom
        return ImportedIngredient(nom=text)


class MarmitonParser(RecipeParser):
    """Parser spécialisé pour Marmiton."""

    @staticmethod
    def parse(soup: BeautifulSoup, url: str) -> ImportedRecipe:
        """Parse une page Marmiton."""
        recipe = ImportedRecipe(source_url=url, source_site="Marmiton")

        # Titre
        title = soup.find("h1")
        if title:
            recipe.nom = RecipeParser.clean_text(title.get_text())

        # Description
        desc = soup.find("p", class_=re.compile(r"description|intro", re.I))
        if desc:
            recipe.description = RecipeParser.clean_text(desc.get_text())

        # Image
        img = soup.find("img", class_=re.compile(r"recipe-media|photo", re.I))
        if img and img.get("src"):
            recipe.image_url = img["src"]

        # Temps
        time_section = soup.find_all(class_=re.compile(r"time|duration|temps", re.I))
        for section in time_section:
            text = section.get_text().lower()
            if "préparation" in text or "prep" in text:
                recipe.temps_preparation = RecipeParser.parse_duration(text)
            elif "cuisson" in text:
                recipe.temps_cuisson = RecipeParser.parse_duration(text)

        # Portions
        portions_el = soup.find(class_=re.compile(r"serving|portion|personne", re.I))
        if portions_el:
            recipe.portions = RecipeParser.parse_portions(portions_el.get_text())

        # Ingrédients
        ingredients_section = soup.find(class_=re.compile(r"ingredient", re.I))
        if ingredients_section:
            for item in ingredients_section.find_all(["li", "span", "p"]):
                ing = RecipeParser.parse_ingredient(item.get_text())
                if ing.nom:
                    recipe.ingredients.append(ing)

        # Étapes
        steps_section = soup.find(class_=re.compile(r"step|instruction|etape|preparation", re.I))
        if steps_section:
            for item in steps_section.find_all(["li", "p", "div"]):
                step_text = RecipeParser.clean_text(item.get_text())
                if step_text and len(step_text) > 10:  # Éviter les textes trop courts
                    recipe.etapes.append(step_text)

        # Score de confiance
        recipe.confiance_score = MarmitonParser._calculate_confidence(recipe)

        return recipe

    @staticmethod
    def _calculate_confidence(recipe: ImportedRecipe) -> float:
        """Calcule le score de confiance."""
        score = 0.0

        if recipe.nom and len(recipe.nom) > 5:
            score += 0.2
        if recipe.ingredients:
            score += min(0.3, len(recipe.ingredients) * 0.05)
        if recipe.etapes:
            score += min(0.3, len(recipe.etapes) * 0.1)
        if recipe.temps_preparation > 0:
            score += 0.1
        if recipe.image_url:
            score += 0.1

        return min(score, 1.0)


class CuisineAZParser(RecipeParser):
    """Parser spécialisé pour CuisineAZ."""

    @staticmethod
    def parse(soup: BeautifulSoup, url: str) -> ImportedRecipe:
        """Parse une page CuisineAZ."""
        recipe = ImportedRecipe(source_url=url, source_site="CuisineAZ")

        # Titre
        title = soup.find("h1", class_=re.compile(r"title", re.I))
        if not title:
            title = soup.find("h1")
        if title:
            recipe.nom = RecipeParser.clean_text(title.get_text())

        # Image
        img = soup.find("img", class_=re.compile(r"recipe|photo", re.I))
        if img and img.get("src"):
            src = img["src"]
            if src.startswith("//"):
                src = "https:" + src
            recipe.image_url = src

        # Temps et portions dans les meta
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "") or meta.get("name", "")
            content = meta.get("content", "")

            if "prepTime" in prop:
                recipe.temps_preparation = RecipeParser.parse_duration(content)
            elif "cookTime" in prop:
                recipe.temps_cuisson = RecipeParser.parse_duration(content)
            elif "recipeYield" in prop:
                recipe.portions = RecipeParser.parse_portions(content)

        # Ingrédients - JSON-LD si disponible
        script = soup.find("script", type="application/ld+json")
        if script:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "Recipe":
                    if "recipeIngredient" in data:
                        for ing_text in data["recipeIngredient"]:
                            ing = RecipeParser.parse_ingredient(ing_text)
                            if ing.nom:
                                recipe.ingredients.append(ing)

                    if "recipeInstructions" in data:
                        instructions = data["recipeInstructions"]
                        if isinstance(instructions, list):
                            for step in instructions:
                                if isinstance(step, str):
                                    recipe.etapes.append(step)
                                elif isinstance(step, dict) and "text" in step:
                                    recipe.etapes.append(step["text"])
            except Exception:
                pass

        # Fallback HTML si pas de JSON-LD
        if not recipe.ingredients:
            for item in soup.find_all(class_=re.compile(r"ingredient", re.I)):
                ing = RecipeParser.parse_ingredient(item.get_text())
                if ing.nom:
                    recipe.ingredients.append(ing)

        if not recipe.etapes:
            steps_container = soup.find(class_=re.compile(r"instruction|step|preparation", re.I))
            if steps_container:
                for item in steps_container.find_all(["li", "p"]):
                    step = RecipeParser.clean_text(item.get_text())
                    if step and len(step) > 10:
                        recipe.etapes.append(step)

        recipe.confiance_score = CuisineAZParser._calculate_confidence(recipe)
        return recipe

    @staticmethod
    def _calculate_confidence(recipe: ImportedRecipe) -> float:
        score = 0.0
        if recipe.nom:
            score += 0.2
        if recipe.ingredients:
            score += min(0.3, len(recipe.ingredients) * 0.05)
        if recipe.etapes:
            score += min(0.3, len(recipe.etapes) * 0.1)
        if recipe.temps_preparation > 0:
            score += 0.1
        if recipe.image_url:
            score += 0.1
        return min(score, 1.0)


class GenericRecipeParser(RecipeParser):
    """Parser générique utilisant les schema.org et heuristiques."""

    @staticmethod
    def parse(soup: BeautifulSoup, url: str) -> ImportedRecipe:
        """Parse une page avec des heuristiques génériques."""
        recipe = ImportedRecipe(source_url=url, source_site=urlparse(url).netloc)

        # 1. Essayer JSON-LD (schema.org Recipe)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)

                # Peut être une liste
                if isinstance(data, list):
                    data = next(
                        (d for d in data if isinstance(d, dict) and d.get("@type") == "Recipe"),
                        None,
                    )

                if isinstance(data, dict) and data.get("@type") == "Recipe":
                    recipe.nom = data.get("name", "")
                    recipe.description = data.get("description", "")
                    recipe.image_url = (
                        data.get("image", [None])[0]
                        if isinstance(data.get("image"), list)
                        else data.get("image")
                    )

                    # Temps
                    if "prepTime" in data:
                        recipe.temps_preparation = RecipeParser.parse_duration(data["prepTime"])
                    if "cookTime" in data:
                        recipe.temps_cuisson = RecipeParser.parse_duration(data["cookTime"])
                    if "recipeYield" in data:
                        recipe.portions = RecipeParser.parse_portions(str(data["recipeYield"]))

                    # Ingrédients
                    for ing_text in data.get("recipeIngredient", []):
                        ing = RecipeParser.parse_ingredient(ing_text)
                        if ing.nom:
                            recipe.ingredients.append(ing)

                    # Étapes
                    instructions = data.get("recipeInstructions", [])
                    if isinstance(instructions, str):
                        recipe.etapes = [s.strip() for s in instructions.split(".") if s.strip()]
                    elif isinstance(instructions, list):
                        for step in instructions:
                            if isinstance(step, str):
                                recipe.etapes.append(step)
                            elif isinstance(step, dict):
                                recipe.etapes.append(step.get("text", ""))

                    recipe.confiance_score = 0.9
                    return recipe
            except Exception:
                continue

        # 2. Fallback: extraction HTML heuristique
        # Titre
        for selector in ["h1", '[itemprop="name"]', ".recipe-title", ".title"]:
            el = soup.select_one(selector)
            if el:
                recipe.nom = RecipeParser.clean_text(el.get_text())
                break

        # Description
        for selector in [
            '[itemprop="description"]',
            ".recipe-description",
            ".intro",
            'meta[name="description"]',
        ]:
            el = soup.select_one(selector)
            if el:
                if el.name == "meta":
                    recipe.description = el.get("content", "")
                else:
                    recipe.description = RecipeParser.clean_text(el.get_text())
                break

        # Ingrédients
        for selector in [
            '[itemprop="recipeIngredient"]',
            ".ingredient",
            ".ingredients li",
            '[class*="ingredient"] li',
        ]:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    ing = RecipeParser.parse_ingredient(el.get_text())
                    if ing.nom and ing.nom not in [i.nom for i in recipe.ingredients]:
                        recipe.ingredients.append(ing)
                break

        # Étapes
        for selector in [
            '[itemprop="recipeInstructions"]',
            ".instruction",
            ".steps li",
            '[class*="step"] p',
        ]:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    step = RecipeParser.clean_text(el.get_text())
                    if step and len(step) > 10:
                        recipe.etapes.append(step)
                break

        # Temps
        for el in soup.select('[itemprop="prepTime"], .prep-time, [class*="prep"]'):
            recipe.temps_preparation = RecipeParser.parse_duration(el.get_text())
            break

        for el in soup.select('[itemprop="cookTime"], .cook-time, [class*="cook"]'):
            recipe.temps_cuisson = RecipeParser.parse_duration(el.get_text())
            break

        # Image
        for selector in ['[itemprop="image"]', ".recipe-image img", 'meta[property="og:image"]']:
            el = soup.select_one(selector)
            if el:
                if el.name == "meta":
                    recipe.image_url = el.get("content")
                else:
                    recipe.image_url = el.get("src") or el.get("content")
                break

        recipe.confiance_score = GenericRecipeParser._calculate_confidence(recipe)
        return recipe

    @staticmethod
    def _calculate_confidence(recipe: ImportedRecipe) -> float:
        score = 0.0
        if recipe.nom and len(recipe.nom) > 3:
            score += 0.2
        if recipe.ingredients:
            score += min(0.25, len(recipe.ingredients) * 0.04)
        if recipe.etapes:
            score += min(0.25, len(recipe.etapes) * 0.08)
        if recipe.temps_preparation > 0 or recipe.temps_cuisson > 0:
            score += 0.15
        if recipe.image_url:
            score += 0.15
        return min(score, 1.0)
