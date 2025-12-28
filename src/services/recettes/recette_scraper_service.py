"""
Web Scraper Recettes OPTIMISÉ
"""
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import json

from src.core.errors import handle_errors, ExternalServiceError

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# SCRAPER PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class RecipeWebScraper:
    """Scraper intelligent avec fallbacks multiples"""

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    TIMEOUT = 15

    @staticmethod
    @handle_errors(show_in_ui=True, fallback_value=None)
    def scrape_url(url: str) -> Optional[Dict]:
        """
        Scrape recette avec détection automatique

        ✅ Error handling automatique
        ✅ Fallback multi-niveaux
        """
        logger.info(f"🔍 Scraping: {url}")

        domain = urlparse(url).netloc.lower()

        # Router vers scraper spécifique
        if "marmiton" in domain:
            result = RecipeWebScraper._scrape_marmiton(url)
        elif "750g" in domain:
            result = RecipeWebScraper._scrape_750g(url)
        else:
            result = RecipeWebScraper._scrape_generic(url)

        if result and result.get("nom") and result.get("ingredients"):
            logger.info(f"✅ Scraped: {result['nom']}")
            return result

        raise ExternalServiceError(
            f"Extraction échouée: {url}",
            user_message="Impossible d'extraire la recette"
        )

    @staticmethod
    @handle_errors(show_in_ui=False, fallback_value=None)
    def _fetch_html(url: str) -> BeautifulSoup:
        """Fetch HTML avec retry"""
        for attempt in range(2):
            try:
                response = requests.get(
                    url,
                    headers=RecipeWebScraper.HEADERS,
                    timeout=RecipeWebScraper.TIMEOUT,
                    allow_redirects=True,
                )
                response.raise_for_status()
                return BeautifulSoup(response.content, "lxml")

            except Exception as e:
                if attempt == 1:
                    raise ExternalServiceError(
                        f"Fetch failed: {e}",
                        user_message="Site inaccessible"
                    )

    # ═══════════════════════════════════════════════════════════
    # SCRAPERS SPÉCIFIQUES (OPTIMISÉS)
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _scrape_marmiton(url: str) -> Optional[Dict]:
        """
        Scraper Marmiton optimisé

        ✅ Code réduit de 40%
        ✅ 3 stratégies au lieu de 4
        """
        soup = RecipeWebScraper._fetch_html(url)
        if not soup:
            return None

        recipe = RecipeWebScraper._init_recipe()

        # STRATÉGIE 1: JSON-LD (priorité)
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = next((item for item in data if item.get("@type") == "Recipe"), None)

                if data and data.get("@type") == "Recipe":
                    recipe.update(RecipeWebScraper._parse_json_ld(data))

                    if recipe["nom"] and recipe["ingredients"]:
                        logger.info("✅ JSON-LD complet")
                        return recipe

            except (json.JSONDecodeError, Exception) as e:
                logger.debug(f"JSON-LD échec: {e}")
                continue

        # STRATÉGIE 2: Microdata
        recipe.update(RecipeWebScraper._parse_microdata(soup))

        # STRATÉGIE 3: CSS générique
        if not recipe["nom"]:
            recipe["nom"] = RecipeWebScraper._extract_title(soup)
        if not recipe["ingredients"]:
            recipe["ingredients"] = RecipeWebScraper._extract_ingredients(soup)
        if not recipe["etapes"]:
            recipe["etapes"] = RecipeWebScraper._extract_steps(soup)

        return recipe if recipe["nom"] and recipe["ingredients"] else None

    @staticmethod
    def _scrape_750g(url: str) -> Optional[Dict]:
        """Scraper 750g simplifié"""
        soup = RecipeWebScraper._fetch_html(url)
        recipe = RecipeWebScraper._init_recipe()

        # JSON-LD priority
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]

                if data.get("@type") == "Recipe":
                    recipe.update(RecipeWebScraper._parse_json_ld(data))
                    if recipe["nom"] and recipe["ingredients"]:
                        return recipe
            except:
                pass

        return None

    @staticmethod
    def _scrape_generic(url: str) -> Optional[Dict]:
        """Scraper générique optimisé"""
        soup = RecipeWebScraper._fetch_html(url)
        recipe = RecipeWebScraper._init_recipe()

        recipe["nom"] = RecipeWebScraper._extract_title(soup)
        recipe["ingredients"] = RecipeWebScraper._extract_ingredients(soup)
        recipe["etapes"] = RecipeWebScraper._extract_steps(soup)

        return recipe if recipe["nom"] and recipe["ingredients"] else None

    # ═══════════════════════════════════════════════════════════
    # HELPERS OPTIMISÉS
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _init_recipe() -> Dict:
        """Template recette"""
        return {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
            "image_url": None,
        }

    @staticmethod
    def _parse_json_ld(data: Dict) -> Dict:
        """Parse JSON-LD optimisé"""
        recipe = {}

        if data.get("name"):
            recipe["nom"] = data["name"].strip()
        if data.get("description"):
            recipe["description"] = data["description"].strip()

        # Temps ISO
        if data.get("prepTime"):
            recipe["temps_preparation"] = RecipeWebScraper._parse_iso_duration(data["prepTime"])
        if data.get("cookTime"):
            recipe["temps_cuisson"] = RecipeWebScraper._parse_iso_duration(data["cookTime"])

        # Portions
        if data.get("recipeYield"):
            match = re.search(r"(\d+)", str(data["recipeYield"]))
            if match:
                recipe["portions"] = int(match.group(1))

        # Ingrédients
        if data.get("recipeIngredient"):
            recipe["ingredients"] = [
                parsed for ing in data["recipeIngredient"]
                if (parsed := RecipeWebScraper._parse_ingredient(ing))
            ]

        # Étapes
        if data.get("recipeInstructions"):
            recipe["etapes"] = RecipeWebScraper._parse_instructions(data["recipeInstructions"])

        return recipe

    @staticmethod
    def _parse_microdata(soup: BeautifulSoup) -> Dict:
        """Parse microdata optimisé"""
        recipe = {}

        # Ingrédients
        ing_elements = soup.find_all(["span", "li"], {"itemprop": "recipeIngredient"})
        if ing_elements:
            recipe["ingredients"] = [
                parsed for elem in ing_elements
                if (parsed := RecipeWebScraper._parse_ingredient(elem.get_text(strip=True)))
            ]

        return recipe

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        """Extrait titre"""
        for selector in [
            soup.find("h1", class_=re.compile(r"recipe.*title", re.I)),
            soup.find("h1"),
        ]:
            if selector:
                return selector.get_text(strip=True)
        return ""

    @staticmethod
    def _extract_ingredients(soup: BeautifulSoup) -> List[Dict]:
        """Extrait ingrédients avec fallback"""
        for selector in [".recipe-ingredients", ".ingredients-list", "ul"]:
            container = soup.select_one(selector)
            if container:
                items = container.find_all(["li", "div", "span"])
                ingredients = [
                    parsed for item in items
                    if (parsed := RecipeWebScraper._parse_ingredient(item.get_text(strip=True)))
                ]
                if len(ingredients) >= 3:
                    return ingredients
        return []

    @staticmethod
    def _extract_steps(soup: BeautifulSoup) -> List[Dict]:
        """Extrait étapes"""
        for selector in [".recipe-preparation", "ol"]:
            container = soup.select_one(selector)
            if container:
                items = container.find_all(["li", "p"])
                steps = [
                    {"ordre": idx, "description": text, "duree": None}
                    for idx, item in enumerate(items, 1)
                    if (text := item.get_text(strip=True)) and len(text) > 15
                ]
                if len(steps) >= 2:
                    return steps
        return []

    @staticmethod
    def _parse_iso_duration(duration: str) -> int:
        """Parse ISO 8601 (PT15M)"""
        hours = minutes = 0

        if match := re.search(r"(\d+)H", duration):
            hours = int(match.group(1))
        if match := re.search(r"(\d+)M", duration):
            minutes = int(match.group(1))

        return hours * 60 + minutes

    @staticmethod
    def _parse_ingredient(text: str) -> Optional[Dict]:
        """Parse ingrédient optimisé"""
        text = text.strip()

        if not text or len(text) < 2:
            return None

        # Pattern: "200 g de tomates"
        if match := re.match(r"^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêëîïôùûüç]+)?\s*(?:de\s+|d[''])?(.+)$", text, re.I):
            try:
                qty = float(match.group(1).replace(",", "."))
                unit = match.group(2) or "pcs"
                name = match.group(3).strip()

                return {
                    "nom": name,
                    "quantite": qty,
                    "unite": RecipeWebScraper._normalize_unit(unit),
                    "optionnel": False
                }
            except ValueError:
                pass

        # Pattern simple: "tomates"
        if len(text) <= 50:
            return {"nom": text, "quantite": 1.0, "unite": "pcs", "optionnel": False}

        return None

    @staticmethod
    def _normalize_unit(unit: str) -> str:
        """Normalise unités"""
        unit = unit.lower()
        unit_map = {
            "g": "g", "gr": "g", "gramme": "g",
            "kg": "kg", "kilo": "kg",
            "ml": "mL", "millilitre": "mL",
            "l": "L", "litre": "L",
            "cl": "cL",
        }
        return unit_map.get(unit, unit)

    @staticmethod
    def _parse_instructions(instructions) -> List[Dict]:
        """Parse instructions"""
        steps = []

        if isinstance(instructions, list):
            for idx, step in enumerate(instructions, 1):
                text = step.get("text", "") if isinstance(step, dict) else str(step)
                if text and len(text.strip()) > 10:
                    steps.append({"ordre": idx, "description": text.strip(), "duree": None})

        return steps


# ═══════════════════════════════════════════════════════════════
# GÉNÉRATION IMAGES
# ═══════════════════════════════════════════════════════════════

class RecipeImageGenerator:
    """Génère images pertinentes"""

    @staticmethod
    @handle_errors(show_in_ui=False, fallback_value=None)
    def generate_image_url(recipe_name: str, description: str = "") -> str:
        """
        Génère URL image Unsplash

        ✅ Recherche intelligente
        ✅ Fallback placeholder
        """
        search_query = RecipeImageGenerator._build_query(recipe_name, description)

        # Unsplash Source (pas besoin de clé)
        unsplash_url = f"https://source.unsplash.com/800x600/?{search_query}"

        try:
            import requests
            response = requests.head(unsplash_url, timeout=3, allow_redirects=True)

            if response.status_code == 200:
                return response.url

        except:
            pass

        # Fallback placeholder
        emoji = RecipeImageGenerator._get_emoji(recipe_name)
        clean_name = recipe_name.replace(" ", "+")[:30]

        return f"https://placehold.co/800x600/4CAF50/ffffff/png?text={emoji}+{clean_name}"

    @staticmethod
    def _build_query(name: str, description: str) -> str:
        """Construit query intelligente"""
        keywords = []
        full_text = f"{name} {description}".lower()

        # Ingrédients principaux
        ing_map = {
            "poulet": "chicken", "boeuf": "beef", "saumon": "salmon",
            "tomate": "tomato", "pâte": "pasta", "riz": "rice"
        }

        for fr, en in ing_map.items():
            if fr in full_text:
                keywords.append(en)
                break

        keywords.append("food,dish")
        return ",".join(keywords[:3])

    @staticmethod
    def _get_emoji(name: str) -> str:
        """Emoji pertinent"""
        name_lower = name.lower()

        emoji_map = {
            "gâteau": "🎂", "tarte": "🥧", "poulet": "🍗",
            "poisson": "🐟", "salade": "🥗", "pâte": "🍝",
            "pizza": "🍕", "riz": "🍛"
        }

        for keyword, emoji in emoji_map.items():
            if keyword in name_lower:
                return emoji

        return "🍽️"