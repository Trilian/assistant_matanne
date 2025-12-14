"""
Web Scraper pour Import de Recettes
Supporte Marmiton, 750g, Cuisine AZ, etc.
"""
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RecipeWebScraper:
    """Scraper intelligent de recettes web"""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    TIMEOUT = 10

    @staticmethod
    def scrape_url(url: str) -> Optional[Dict]:
        """
        Scrape une recette depuis une URL

        Returns:
            Dict avec structure recette ou None
        """
        try:
            domain = urlparse(url).netloc.lower()

            # Router vers le bon scraper
            if 'marmiton' in domain:
                return RecipeWebScraper._scrape_marmiton(url)
            elif '750g' in domain:
                return RecipeWebScraper._scrape_750g(url)
            elif 'cuisineaz' in domain:
                return RecipeWebScraper._scrape_cuisineaz(url)
            else:
                # Scraper générique
                return RecipeWebScraper._scrape_generic(url)

        except Exception as e:
            logger.error(f"Erreur scraping {url}: {e}")
            return None

    @staticmethod
    def _fetch_html(url: str) -> BeautifulSoup:
        """Fetch HTML et parse"""
        response = requests.get(url, headers=RecipeWebScraper.HEADERS, timeout=RecipeWebScraper.TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'lxml')

    @staticmethod
    def _scrape_marmiton(url: str) -> Dict:
        """Scraper spécifique Marmiton (structure 2024)"""
        soup = RecipeWebScraper._fetch_html(url)

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
            "image_url": None
        }

        # Titre - Structure Marmiton actuelle
        title_selectors = [
            soup.find('h1', class_='recipe-header__title'),
            soup.find('h1', {'itemprop': 'name'}),
            soup.find('h1')
        ]
        for selector in title_selectors:
            if selector:
                recipe["nom"] = selector.get_text(strip=True)
                break

        # Image - Plusieurs patterns possibles
        img_selectors = [
            soup.find('img', {'itemprop': 'image'}),
            soup.find('img', class_='recipe-media__image'),
            soup.find('picture', class_='recipe-media__image'),
            soup.find('img', class_='main-picture')
        ]

        for selector in img_selectors:
            if selector:
                if selector.name == 'picture':
                    img = selector.find('img')
                    if img and img.get('src'):
                        recipe["image_url"] = img['src']
                        break
                elif selector.get('src'):
                    recipe["image_url"] = selector['src']
                    break
                elif selector.get('data-src'):
                    recipe["image_url"] = selector['data-src']
                    break

        # Description
        desc_selectors = [
            soup.find('p', class_='recipe-header__description'),
            soup.find('div', {'itemprop': 'description'}),
            soup.find('p', class_='recipe-description')
        ]
        for selector in desc_selectors:
            if selector:
                recipe["description"] = selector.get_text(strip=True)
                break

        # Temps de préparation et cuisson
        time_container = soup.find('div', class_='recipe-infos__timmings')
        if time_container:
            prep_time = time_container.find('span', class_='recipe-infos__timmings__preparation')
            if prep_time:
                time_text = prep_time.get_text()
                match = re.search(r'(\d+)', time_text)
                if match:
                    recipe["temps_preparation"] = int(match.group(1))

            cook_time = time_container.find('span', class_='recipe-infos__timmings__cooking')
            if cook_time:
                time_text = cook_time.get_text()
                match = re.search(r'(\d+)', time_text)
                if match:
                    recipe["temps_cuisson"] = int(match.group(1))

        # Portions - Chercher "personnes"
        portions_patterns = [
            soup.find('span', class_='recipe-infos__quantity'),
            soup.find('span', string=re.compile(r'personnes?', re.I)),
            soup.find(text=re.compile(r'(\d+)\s*personnes?', re.I))
        ]

        for pattern in portions_patterns:
            if pattern:
                text = pattern if isinstance(pattern, str) else pattern.get_text()
                match = re.search(r'(\d+)', text)
                if match:
                    recipe["portions"] = int(match.group(1))
                    break

        # Difficulté
        difficulty = soup.find('span', class_='recipe-infos__level')
        if difficulty:
            diff_text = difficulty.get_text(strip=True).lower()
            if 'facile' in diff_text:
                recipe["difficulte"] = "facile"
            elif 'difficile' in diff_text:
                recipe["difficulte"] = "difficile"
            else:
                recipe["difficulte"] = "moyen"

        # Ingrédients - Structure JSON-LD ou liste
        # 1. Essayer JSON-LD (Schema.org)
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            try:
                import json
                data = json.loads(json_ld.string)
                if isinstance(data, list):
                    data = data[0]

                if 'recipeIngredient' in data:
                    for idx, ing_text in enumerate(data['recipeIngredient']):
                        parsed = RecipeWebScraper._parse_ingredient(ing_text)
                        if parsed:
                            recipe["ingredients"].append(parsed)

                if 'recipeInstructions' in data and not recipe["etapes"]:
                    instructions = data['recipeInstructions']
                    if isinstance(instructions, list):
                        for idx, step in enumerate(instructions, 1):
                            if isinstance(step, dict):
                                text = step.get('text', '')
                            else:
                                text = str(step)

                            if text:
                                recipe["etapes"].append({
                                    "ordre": idx,
                                    "description": text.strip(),
                                    "duree": None
                                })
            except:
                pass

        # 2. Si pas de JSON-LD, chercher dans le HTML
        if not recipe["ingredients"]:
            ing_containers = [
                soup.find('div', class_='card-ingredient-list'),
                soup.find('ul', class_='recipe-ingredients__list'),
                soup.find('div', class_='recipe-ingredients')
            ]

            for container in ing_containers:
                if container:
                    # Chercher tous les items d'ingrédients
                    ing_items = container.find_all(['li', 'div'], class_=re.compile(r'ingredient', re.I))

                    for item in ing_items:
                        # Extraire le texte complet
                        text = item.get_text(strip=True)

                        # Parfois la quantité est dans un span séparé
                        qty_span = item.find('span', class_=re.compile(r'quantity|qty', re.I))
                        name_span = item.find('span', class_=re.compile(r'name|label', re.I))

                        if qty_span and name_span:
                            qty_text = qty_span.get_text(strip=True)
                            name_text = name_span.get_text(strip=True)
                            text = f"{qty_text} {name_text}"

                        parsed = RecipeWebScraper._parse_ingredient(text)
                        if parsed:
                            recipe["ingredients"].append(parsed)

                    if recipe["ingredients"]:
                        break

        # Étapes - Si pas déjà dans JSON-LD
        if not recipe["etapes"]:
            steps_containers = [
                soup.find('div', class_='recipe-preparation__list'),
                soup.find('ol', class_='recipe-steps'),
                soup.find('div', class_='recipe-instructions')
            ]

            for container in steps_containers:
                if container:
                    step_items = container.find_all(['li', 'p', 'div'], class_=re.compile(r'step|instruction', re.I))

                    for idx, item in enumerate(step_items, 1):
                        text = item.get_text(strip=True)

                        # Nettoyer les numéros d'étapes si présents
                        text = re.sub(r'^étape\s+\d+\s*:?\s*', '', text, flags=re.I)
                        text = re.sub(r'^\d+\.\s*', '', text)

                        if text and len(text) > 10:  # Ignorer les étapes trop courtes
                            recipe["etapes"].append({
                                "ordre": idx,
                                "description": text,
                                "duree": None
                            })

                    if recipe["etapes"]:
                        break

        # Fallback : chercher toutes les listes ordonnées
        if not recipe["etapes"]:
            all_ols = soup.find_all('ol')
            for ol in all_ols:
                items = ol.find_all('li')
                if len(items) >= 3:  # Au moins 3 étapes
                    for idx, li in enumerate(items, 1):
                        text = li.get_text(strip=True)
                        if text and len(text) > 10:
                            recipe["etapes"].append({
                                "ordre": idx,
                                "description": text,
                                "duree": None
                            })
                    if recipe["etapes"]:
                        break

        logger.info(f"Marmiton scraped: {recipe['nom']}, {len(recipe['ingredients'])} ing, {len(recipe['etapes'])} steps")

        return recipe if recipe["nom"] and recipe["ingredients"] else None

    @staticmethod
    def _scrape_750g(url: str) -> Dict:
        """Scraper 750g"""
        soup = RecipeWebScraper._fetch_html(url)

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
            "image_url": None
        }

        # Titre
        title = soup.find('h1', itemprop='name')
        if title:
            recipe["nom"] = title.get_text(strip=True)

        # Image
        img = soup.find('img', itemprop='image')
        if img and img.get('src'):
            recipe["image_url"] = img['src']

        # Ingrédients (structure 750g)
        ing_list = soup.find('ul', class_='recipe-ingredients')
        if ing_list:
            for li in ing_list.find_all('li'):
                text = li.get_text(strip=True)
                parsed = RecipeWebScraper._parse_ingredient(text)
                if parsed:
                    recipe["ingredients"].append(parsed)

        # Étapes
        steps = soup.find_all('p', itemprop='recipeInstructions')
        for idx, step in enumerate(steps, 1):
            text = step.get_text(strip=True)
            if text:
                recipe["etapes"].append({
                    "ordre": idx,
                    "description": text,
                    "duree": None
                })

        return recipe if recipe["nom"] else None

    @staticmethod
    def _scrape_cuisineaz(url: str) -> Dict:
        """Scraper Cuisine AZ"""
        soup = RecipeWebScraper._fetch_html(url)

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
            "image_url": None
        }

        # Titre
        title = soup.find('h1', class_='recipe-title')
        if title:
            recipe["nom"] = title.get_text(strip=True)

        # Image
        img = soup.find('img', class_='recipe-image')
        if img and img.get('src'):
            recipe["image_url"] = img['src']

        # Ingrédients
        ing_divs = soup.find_all('div', class_='ingredient')
        for div in ing_divs:
            text = div.get_text(strip=True)
            parsed = RecipeWebScraper._parse_ingredient(text)
            if parsed:
                recipe["ingredients"].append(parsed)

        # Étapes
        step_divs = soup.find_all('div', class_='recipe-step')
        for idx, div in enumerate(step_divs, 1):
            text = div.get_text(strip=True)
            if text:
                recipe["etapes"].append({
                    "ordre": idx,
                    "description": text,
                    "duree": None
                })

        return recipe if recipe["nom"] else None

    @staticmethod
    def _scrape_generic(url: str) -> Dict:
        """Scraper générique (best effort)"""
        soup = RecipeWebScraper._fetch_html(url)

        recipe = {
            "nom": "",
            "description": "",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "moyen",
            "ingredients": [],
            "etapes": [],
            "image_url": None
        }

        # Titre (h1 le plus probable)
        h1 = soup.find('h1')
        if h1:
            recipe["nom"] = h1.get_text(strip=True)

        # Image (première image avec "recipe" ou grande taille)
        img = soup.find('img', class_=re.compile(r'recipe|recette|main', re.I))
        if img and img.get('src'):
            recipe["image_url"] = img['src']

        # Chercher listes (ingrédients probables)
        lists = soup.find_all('ul')
        for ul in lists:
            items = ul.find_all('li')
            if len(items) > 3:  # Probablement ingrédients si > 3 items
                for item in items[:20]:  # Max 20
                    text = item.get_text(strip=True)
                    parsed = RecipeWebScraper._parse_ingredient(text)
                    if parsed:
                        recipe["ingredients"].append(parsed)
                if recipe["ingredients"]:
                    break

        # Chercher étapes (ordered list ou paragraphes)
        ol = soup.find('ol')
        if ol:
            for idx, li in enumerate(ol.find_all('li'), 1):
                text = li.get_text(strip=True)
                if text:
                    recipe["etapes"].append({
                        "ordre": idx,
                        "description": text,
                        "duree": None
                    })

        return recipe if recipe["nom"] else None

    @staticmethod
    def _parse_ingredient(text: str) -> Optional[Dict]:
        """
        Parse une ligne d'ingrédient (version améliorée)

        Exemples:
        - "200 g de tomates"
        - "2 cuillères à soupe d'huile d'olive"
        - "1 oignon"
        - "sel, poivre"
        """
        text = text.strip()

        if not text or len(text) < 2:
            return None

        # Pattern 1: "200 g de tomates" ou "200g tomates"
        pattern1 = r"^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêë]+)?\s*(?:de |d'|d’)?(.+)$"
        match = re.match(pattern1, text, re.I)

        if match:
            qty_str = match.group(1).replace(',', '.')
        unit = match.group(2) or "pcs"
        name = match.group(3).strip()

        try:
            qty = float(qty_str)

            # Normaliser unités
            unit = unit.lower()
            if unit in ['g', 'gr', 'gramme', 'grammes']:
                unit = 'g'
            elif unit in ['kg', 'kilo', 'kilogramme']:
                unit = 'kg'
            elif unit in ['ml', 'millilitre']:
                unit = 'mL'
            elif unit in ['l', 'litre']:
                unit = 'L'
            elif unit in ['cl', 'centilitre']:
                unit = 'cL'
            elif unit in ['cuillère', 'cuilleres', 'cuillère', 'cs', 'càs']:
                unit = 'c. à soupe'
            elif unit in ['cc', 'càc']:
                unit = 'c. à café'

            return {
                "nom": name,
                "quantite": qty,
                "unite": unit,
                "optionnel": False
            }
        except ValueError:
            pass

        # Pattern 2: "une pincée de sel" -> 1 pincée
        pattern2 = r'^(une?|deux|trois|quatre|cinq)\s+(.+)$'
        match = re.match(pattern2, text, re.I)
        if match:
            qty_word = match.group(1).lower()
            rest = match.group(2)

            qty_map = {
                'un': 1, 'une': 1,
                'deux': 2,
                'trois': 3,
                'quatre': 4,
                'cinq': 5
            }

            qty = qty_map.get(qty_word, 1)

            # Chercher unité dans rest
            unit_match = re.match(
                r"^([a-zàéèê\s]+)\s+(?:de\s+|d['’])?(.+)$",
                rest,
                re.I
            )

            if unit_match:
                unit = unit_match.group(1).strip()
                name = unit_match.group(2).strip()
            else:
                unit = "pcs"
                name = rest

            return {
                "nom": name,
                "quantite": float(qty),
                "unite": unit,
                "optionnel": False
            }

        # Pattern 3: Juste un ingrédient sans quantité -> 1 pcs
        # Vérifier que ce n'est pas un titre/section
        if not any(word in text.lower() for word in ['pour', 'ingrédients', 'préparation']):
            return {
                "nom": text,
                "quantite": 1.0,
                "unite": "pcs",
                "optionnel": False
            }

        return None

    @staticmethod
    def get_supported_sites() -> List[str]:
        """Retourne la liste des sites supportés"""
        return [
            "marmiton.org",
            "750g.com",
            "cuisineaz.com",
            "(autres sites via scraping générique)"
        ]


# ===================================
# GÉNÉRATION D'IMAGES GRATUITES
# ===================================

class RecipeImageGenerator:
    """Génère des images de recettes gratuitement"""

    @staticmethod
    def generate_from_unsplash(recipe_name: str, keywords: List[str] = None) -> str:
        """
        Génère URL image Unsplash

        Args:
            recipe_name: Nom de la recette
            keywords: Mots-clés additionnels

        Returns:
            URL de l'image
        """
        # Nettoyer le nom
        clean_name = recipe_name.lower()
        clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)

        # Construire query
        query_parts = clean_name.split()[:3]  # Max 3 mots

        if keywords:
            query_parts.extend(keywords[:2])

        query = ",".join(query_parts + ["food", "recipe"])

        # URL Unsplash Source API (gratuite, illimitée)
        return f"https://source.unsplash.com/800x600/?{query}"

    @staticmethod
    def generate_from_foodish(recipe_name: str) -> str:
        """
        Alternative : Foodish API (images aléatoires de plats)

        Returns:
            URL image
        """
        # API gratuite, retourne image aléatoire de nourriture
        try:
            response = requests.get("https://foodish-api.herokuapp.com/api/", timeout=5)
            data = response.json()
            return data.get("image", RecipeImageGenerator.generate_from_unsplash(recipe_name))
        except:
            # Fallback Unsplash
            return RecipeImageGenerator.generate_from_unsplash(recipe_name)