# src/services/web_scraper.py - VERSION CORRIGÉE
"""
Web Scraper pour Import de Recettes - Version Robuste 2024/2025
Supporte Marmiton, 750g, Cuisine AZ avec détection automatique de structure
"""
import re
import logging
from typing import Dict, Optional, List
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class RecipeWebScraper:
    """Scraper intelligent de recettes web avec fallbacks multiples"""

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    TIMEOUT = 15

    @staticmethod
    def scrape_url(url: str) -> Optional[Dict]:
        """
        Scrape une recette depuis une URL avec détection automatique

        Returns:
            Dict avec structure recette ou None
        """
        try:
            logger.info(f"🔍 Scraping: {url}")

            domain = urlparse(url).netloc.lower()

            # Router vers le bon scraper
            if 'marmiton' in domain:
                result = RecipeWebScraper._scrape_marmiton_robust(url)
            elif '750g' in domain:
                result = RecipeWebScraper._scrape_750g(url)
            elif 'cuisineaz' in domain:
                result = RecipeWebScraper._scrape_cuisineaz(url)
            else:
                result = RecipeWebScraper._scrape_generic(url)

            if result:
                logger.info(f"✅ Scraped: {result['nom']}, {len(result['ingredients'])} ing, {len(result['etapes'])} steps")
            else:
                logger.warning(f"⚠️ Aucune recette extraite de {url}")

            return result

        except Exception as e:
            logger.error(f"❌ Erreur scraping {url}: {e}")
            return None

    @staticmethod
    def _fetch_html(url: str) -> BeautifulSoup:
        """Fetch HTML avec retry et meilleurs headers"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=RecipeWebScraper.HEADERS,
                    timeout=RecipeWebScraper.TIMEOUT,
                    allow_redirects=True
                )
                response.raise_for_status()

                # Parser avec lxml (plus robuste)
                return BeautifulSoup(response.content, 'lxml')

            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries} après erreur: {e}")

        return None

    @staticmethod
    def _scrape_marmiton_robust(url: str) -> Optional[Dict]:
        """
        Scraper Marmiton avec multiples stratégies de fallback

        Stratégies dans l'ordre :
        1. JSON-LD (Schema.org) - Le plus fiable
        2. Microdata (itemprop)
        3. Classes CSS spécifiques Marmiton
        4. Scraping générique
        """
        soup = RecipeWebScraper._fetch_html(url)

        if not soup:
            return None

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

        # ===================================
        # STRATÉGIE 1 : JSON-LD (Schema.org)
        # ===================================
        json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)

                # Gérer les cas où c'est une liste
                if isinstance(data, list):
                    # Chercher l'objet Recipe
                    recipe_data = next(
                        (item for item in data if item.get('@type') == 'Recipe'),
                        None
                    )
                    if not recipe_data:
                        continue
                    data = recipe_data

                # Vérifier que c'est bien une recette
                if data.get('@type') != 'Recipe':
                    continue

                logger.info("✅ JSON-LD Schema.org trouvé")

                # Nom
                if data.get('name'):
                    recipe["nom"] = data['name'].strip()

                # Description
                if data.get('description'):
                    recipe["description"] = data['description'].strip()

                # Image
                if data.get('image'):
                    img = data['image']
                    if isinstance(img, list):
                        recipe["image_url"] = img[0] if img else None
                    elif isinstance(img, dict):
                        recipe["image_url"] = img.get('url')
                    else:
                        recipe["image_url"] = str(img)

                # Temps (format ISO 8601: PT15M = 15 minutes)
                if data.get('prepTime'):
                    recipe["temps_preparation"] = RecipeWebScraper._parse_iso_duration(data['prepTime'])

                if data.get('cookTime'):
                    recipe["temps_cuisson"] = RecipeWebScraper._parse_iso_duration(data['cookTime'])

                # Portions
                if data.get('recipeYield'):
                    yield_val = data['recipeYield']
                    if isinstance(yield_val, list):
                        yield_val = yield_val[0]

                    # Extraire le nombre
                    match = re.search(r'(\d+)', str(yield_val))
                    if match:
                        recipe["portions"] = int(match.group(1))

                # Ingrédients
                if data.get('recipeIngredient'):
                    for ing_text in data['recipeIngredient']:
                        parsed = RecipeWebScraper._parse_ingredient(ing_text)
                        if parsed:
                            recipe["ingredients"].append(parsed)

                # Étapes
                if data.get('recipeInstructions'):
                    instructions = data['recipeInstructions']

                    # Peut être une liste d'objets ou une liste de strings
                    if isinstance(instructions, list):
                        for idx, step in enumerate(instructions, 1):
                            if isinstance(step, dict):
                                text = step.get('text', '') or step.get('description', '')
                            else:
                                text = str(step)

                            if text and len(text.strip()) > 5:
                                recipe["etapes"].append({
                                    "ordre": idx,
                                    "description": text.strip(),
                                    "duree": None
                                })
                    elif isinstance(instructions, str):
                        # Parfois c'est un seul string avec des sauts de ligne
                        lines = instructions.split('\n')
                        for idx, line in enumerate(lines, 1):
                            line = line.strip()
                            if line and len(line) > 5:
                                recipe["etapes"].append({
                                    "ordre": idx,
                                    "description": line,
                                    "duree": None
                                })

                # Si on a trouvé nom + ingrédients, c'est bon
                if recipe["nom"] and recipe["ingredients"]:
                    logger.info(f"✅ JSON-LD complet: {len(recipe['ingredients'])} ing, {len(recipe['etapes'])} steps")
                    return recipe

            except json.JSONDecodeError as e:
                logger.warning(f"JSON-LD invalide: {e}")
                continue
            except Exception as e:
                logger.warning(f"Erreur parsing JSON-LD: {e}")
                continue

        # ===================================
        # STRATÉGIE 2 : Microdata (itemprop)
        # ===================================
        if not recipe["ingredients"]:
            logger.info("🔄 Tentative avec microdata...")

            # Ingrédients avec itemprop
            ing_elements = soup.find_all(['span', 'li', 'div'], {'itemprop': 'recipeIngredient'})
            for elem in ing_elements:
                text = elem.get_text(strip=True)
                parsed = RecipeWebScraper._parse_ingredient(text)
                if parsed:
                    recipe["ingredients"].append(parsed)

            if recipe["ingredients"]:
                logger.info(f"✅ Microdata: {len(recipe['ingredients'])} ingrédients")

        if not recipe["etapes"]:
            # Étapes avec itemprop
            step_elements = soup.find_all(['li', 'p', 'div'], {'itemprop': 'recipeInstructions'})
            for idx, elem in enumerate(step_elements, 1):
                text = elem.get_text(strip=True)
                if text and len(text) > 10:
                    recipe["etapes"].append({
                        "ordre": idx,
                        "description": text,
                        "duree": None
                    })

            if recipe["etapes"]:
                logger.info(f"✅ Microdata: {len(recipe['etapes'])} étapes")

        # ===================================
        # STRATÉGIE 3 : Classes CSS Marmiton
        # ===================================
        if not recipe["nom"]:
            # Chercher titre avec plusieurs patterns
            title_selectors = [
                soup.find('h1', class_=re.compile(r'recipe.*title', re.I)),
                soup.find('h1', class_=re.compile(r'title', re.I)),
                soup.find('h1')
            ]

            for selector in title_selectors:
                if selector:
                    recipe["nom"] = selector.get_text(strip=True)
                    logger.info(f"✅ Titre trouvé: {recipe['nom']}")
                    break

        if not recipe["image_url"]:
            # Chercher image avec plusieurs patterns
            img_selectors = [
                soup.find('img', class_=re.compile(r'recipe.*image', re.I)),
                soup.find('img', class_=re.compile(r'main.*picture', re.I)),
                soup.find('picture', class_=re.compile(r'recipe', re.I)),
                soup.select_one('.recipe-media img'),
                soup.find('img', alt=re.compile(recipe["nom"] if recipe["nom"] else "recette", re.I))
            ]

            for selector in img_selectors:
                if selector:
                    if selector.name == 'picture':
                        img = selector.find('img')
                        if img:
                            recipe["image_url"] = img.get('src') or img.get('data-src')
                    else:
                        recipe["image_url"] = selector.get('src') or selector.get('data-src')

                    if recipe["image_url"]:
                        logger.info(f"✅ Image trouvée")
                        break

        # Ingrédients - multiples sélecteurs
        if not recipe["ingredients"]:
            logger.info("🔄 Recherche ingrédients dans le HTML...")

            # Liste des sélecteurs CSS possibles
            ing_container_selectors = [
                '.recipe-ingredients',
                '.card-ingredient',
                '.ingredients-list',
                '[class*="ingredient"]',
                'ul[class*="ingredient"]',
                'div[class*="ingredient"]'
            ]

            for selector in ing_container_selectors:
                container = soup.select_one(selector)

                if container:
                    logger.info(f"✅ Container ingrédients trouvé: {selector}")

                    # Chercher tous les items d'ingrédients
                    ing_items = container.find_all(['li', 'div', 'span'], recursive=True)

                    for item in ing_items:
                        # Ignorer les conteneurs vides ou titres
                        text = item.get_text(strip=True)

                        # Filtrer les titres de sections
                        if not text or len(text) < 3:
                            continue

                        if any(word in text.lower() for word in ['pour', 'ingrédients', 'préparation', 'étapes']):
                            continue

                        parsed = RecipeWebScraper._parse_ingredient(text)
                        if parsed:
                            recipe["ingredients"].append(parsed)

                    if recipe["ingredients"]:
                        logger.info(f"✅ {len(recipe['ingredients'])} ingrédients extraits")
                        break

        # Étapes - multiples sélecteurs
        if not recipe["etapes"]:
            logger.info("🔄 Recherche étapes dans le HTML...")

            step_container_selectors = [
                '.recipe-preparation',
                '.recipe-steps',
                '.preparation-steps',
                '[class*="preparation"]',
                '[class*="instruction"]',
                'ol[class*="step"]',
                'ol[class*="recipe"]'
            ]

            for selector in step_container_selectors:
                container = soup.select_one(selector)

                if container:
                    logger.info(f"✅ Container étapes trouvé: {selector}")

                    # Chercher les items d'étapes
                    step_items = container.find_all(['li', 'p', 'div'], recursive=True)

                    ordre = 1
                    for item in step_items:
                        text = item.get_text(strip=True)

                        # Nettoyer
                        text = re.sub(r'^(étape|step)\s+\d+\s*:?\s*', '', text, flags=re.I)
                        text = re.sub(r'^\d+\.\s*', '', text)

                        # Valider
                        if text and len(text) > 15:  # Étapes substantielles
                            recipe["etapes"].append({
                                "ordre": ordre,
                                "description": text,
                                "duree": None
                            })
                            ordre += 1

                    if recipe["etapes"]:
                        logger.info(f"✅ {len(recipe['etapes'])} étapes extraites")
                        break

        # ===================================
        # STRATÉGIE 4 : Scraping générique en dernier recours
        # ===================================
        if not recipe["ingredients"]:
            logger.warning("⚠️ Fallback: scraping générique des listes")

            # Chercher TOUTES les listes non ordonnées
            all_uls = soup.find_all('ul')

            for ul in all_uls:
                items = ul.find_all('li')

                # Si la liste a entre 3 et 30 items, probable que ce soit des ingrédients
                if 3 <= len(items) <= 30:
                    temp_ings = []

                    for item in items:
                        text = item.get_text(strip=True)
                        parsed = RecipeWebScraper._parse_ingredient(text)
                        if parsed:
                            temp_ings.append(parsed)

                    # Si on a réussi à parser au moins 50% des items, c'est probablement des ingrédients
                    if len(temp_ings) >= len(items) * 0.5:
                        recipe["ingredients"] = temp_ings
                        logger.info(f"✅ Générique: {len(temp_ings)} ingrédients")
                        break

        if not recipe["etapes"]:
            # Chercher les listes ordonnées pour les étapes
            all_ols = soup.find_all('ol')

            for ol in all_ols:
                items = ol.find_all('li')

                if 2 <= len(items) <= 20:
                    temp_steps = []

                    for idx, item in enumerate(items, 1):
                        text = item.get_text(strip=True)

                        if text and len(text) > 15:
                            temp_steps.append({
                                "ordre": idx,
                                "description": text,
                                "duree": None
                            })

                    if len(temp_steps) >= 2:
                        recipe["etapes"] = temp_steps
                        logger.info(f"✅ Générique: {len(temp_steps)} étapes")
                        break

        # ===================================
        # VALIDATION FINALE
        # ===================================
        if recipe["nom"] and recipe["ingredients"] and recipe["etapes"]:
            logger.info(f"✅ Recette complète extraite: {recipe['nom']}")
            return recipe
        else:
            logger.warning(f"⚠️ Extraction incomplète - Nom: {bool(recipe['nom'])}, Ing: {len(recipe['ingredients'])}, Étapes: {len(recipe['etapes'])}")

            # Retourner quand même si on a au moins le nom et les ingrédients
            if recipe["nom"] and recipe["ingredients"]:
                logger.info("⚠️ Retour avec ingrédients sans étapes")
                return recipe

            return None

    @staticmethod
    def _parse_iso_duration(duration: str) -> int:
        """
        Parse une durée ISO 8601 (ex: PT15M, PT1H30M)

        Returns:
            Durée en minutes
        """
        if not duration:
            return 0

        # Pattern: PT15M ou PT1H30M
        hours = 0
        minutes = 0

        hour_match = re.search(r'(\d+)H', duration)
        if hour_match:
            hours = int(hour_match.group(1))

        min_match = re.search(r'(\d+)M', duration)
        if min_match:
            minutes = int(min_match.group(1))

        return hours * 60 + minutes

    @staticmethod
    def _parse_ingredient(text: str) -> Optional[Dict]:
        """
        Parse une ligne d'ingrédient - VERSION AMÉLIORÉE

        Patterns supportés:
        - "200 g de tomates"
        - "200g tomates"
        - "2 cuillères à soupe d'huile"
        - "1 oignon"
        - "sel, poivre"
        - "Une pincée de sel"
        """
        text = text.strip()

        if not text or len(text) < 2:
            return None

        # Ignorer les titres de sections
        if any(word in text.lower() for word in [
            'pour la', 'pour le', 'ingrédients', 'préparation',
            'garniture', 'sauce', 'pâte'
        ]):
            return None

        # Pattern 1: "200 g de tomates" ou "200g tomates"
        pattern1 = r"^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêëîïôùûüç]+)?\s*(?:de\s+|d[''']|d')?(.+)$"
        match = re.match(pattern1, text, re.I)

        if match:
            qty_str = match.group(1).replace(',', '.')
            unit = match.group(2) or "pcs"
            name = match.group(3).strip()

            try:
                qty = float(qty_str)

                # Normaliser unités
                unit = unit.lower()
                unit_map = {
                    'g': 'g', 'gr': 'g', 'gramme': 'g', 'grammes': 'g',
                    'kg': 'kg', 'kilo': 'kg', 'kilogramme': 'kg',
                    'ml': 'mL', 'millilitre': 'mL', 'millilitres': 'mL',
                    'l': 'L', 'litre': 'L', 'litres': 'L',
                    'cl': 'cL', 'centilitre': 'cL', 'centilitres': 'cL',
                    'cuillère': 'c. à soupe', 'cuillères': 'c. à soupe',
                    'cs': 'c. à soupe', 'càs': 'c. à soupe', 'cas': 'c. à soupe',
                    'cc': 'c. à café', 'càc': 'c. à café', 'cac': 'c. à café',
                    'pincée': 'pincée', 'pincees': 'pincée',
                    'tranche': 'tranche', 'tranches': 'tranches',
                    'gousse': 'gousse', 'gousses': 'gousses'
                }

                unit = unit_map.get(unit, unit)

                return {
                    "nom": name,
                    "quantite": qty,
                    "unite": unit,
                    "optionnel": False
                }
            except ValueError:
                pass

        # Pattern 2: "une pincée de sel", "deux oignons"
        pattern2 = r'^(une?|deux|trois|quatre|cinq|six|sept|huit|neuf|dix)\s+(.+)$'
        match = re.match(pattern2, text, re.I)

        if match:
            qty_word = match.group(1).lower()
            rest = match.group(2)

            qty_map = {
                'un': 1, 'une': 1, 'deux': 2, 'trois': 3,
                'quatre': 4, 'cinq': 5, 'six': 6, 'sept': 7,
                'huit': 8, 'neuf': 9, 'dix': 10
            }

            qty = qty_map.get(qty_word, 1)

            # Chercher unité dans rest
            unit_match = re.match(
                r"^([a-zàéèêëîïôùûüç\s]+)\s+(?:de\s+|d[''])?(.+)$",
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

        # Pattern 3: Juste un ingrédient "tomates" -> 1 pcs
        if len(text) <= 50:  # Pas trop long pour être un ingrédient simple
            return {
                "nom": text,
                "quantite": 1.0,
                "unite": "pcs",
                "optionnel": False
            }

        return None

    @staticmethod
    def _scrape_750g(url: str) -> Dict:
        """Scraper 750g - Version robuste"""
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

        # Essayer JSON-LD d'abord
        json_ld = soup.find('script', {'type': 'application/ld+json'})
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, list):
                    data = data[0]

                if data.get('@type') == 'Recipe':
                    if data.get('name'):
                        recipe["nom"] = data['name']
                    if data.get('recipeIngredient'):
                        for ing in data['recipeIngredient']:
                            parsed = RecipeWebScraper._parse_ingredient(ing)
                            if parsed:
                                recipe["ingredients"].append(parsed)
                    if data.get('recipeInstructions'):
                        for idx, step in enumerate(data['recipeInstructions'], 1):
                            if isinstance(step, dict):
                                text = step.get('text', '')
                            else:
                                text = str(step)
                            if text:
                                recipe["etapes"].append({
                                    "ordre": idx,
                                    "description": text,
                                    "duree": None
                                })

                    if recipe["nom"] and recipe["ingredients"]:
                        return recipe
            except:
                pass

        # Fallback HTML
        title = soup.find('h1', itemprop='name') or soup.find('h1')
        if title:
            recipe["nom"] = title.get_text(strip=True)

        return recipe if recipe["nom"] else None

    @staticmethod
    def _scrape_cuisineaz(url: str) -> Dict:
        """Scraper Cuisine AZ"""
        # Similaire à Marmiton, utilise la même logique robuste
        return RecipeWebScraper._scrape_marmiton_robust(url)

    @staticmethod
    def _scrape_generic(url: str) -> Dict:
        """Scraper générique pour tout site"""
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
        h1 = soup.find('h1')
        if h1:
            recipe["nom"] = h1.get_text(strip=True)

        # Ingrédients (listes)
        lists = soup.find_all('ul')
        for ul in lists:
            items = ul.find_all('li')
            if 3 <= len(items) <= 30:
                for item in items:
                    parsed = RecipeWebScraper._parse_ingredient(item.get_text(strip=True))
                    if parsed:
                        recipe["ingredients"].append(parsed)
                if recipe["ingredients"]:
                    break

        # Étapes (ordered lists)
        ol = soup.find('ol')
        if ol:
            for idx, li in enumerate(ol.find_all('li'), 1):
                text = li.get_text(strip=True)
                if text and len(text) > 10:
                    recipe["etapes"].append({
                        "ordre": idx,
                        "description": text,
                        "duree": None
                    })

        return recipe if recipe["nom"] and recipe["ingredients"] else None

    @staticmethod
    def get_supported_sites() -> List[str]:
        """Retourne la liste des sites supportés"""
        return [
            "✅ marmiton.org (structure 2024/2025 supportée)",
            "✅ 750g.com",
            "✅ cuisineaz.com",
            "⚠️ Autres sites (via scraping générique - résultats variables)"
        ]


# ===================================
# GÉNÉRATION D'IMAGES
# ===================================

class RecipeImageGenerator:
    """Génère des images de recettes gratuitement"""

    @staticmethod
    def generate_from_unsplash(recipe_name: str, keywords: List[str] = None) -> str:
        """Génère URL image Unsplash"""
        clean_name = re.sub(r'[^a-z0-9\s]', '', recipe_name.lower())
        query_parts = clean_name.split()[:3]

        if keywords:
            query_parts.extend(keywords[:2])

        query = ",".join(query_parts + ["food", "recipe", "french"])
        return f"https://source.unsplash.com/800x600/?{query}"

    @staticmethod
    def generate_from_foodish(recipe_name: str) -> str:
        """Alternative : Foodish API"""
        try:
            response = requests.get("https://foodish-api.herokuapp.com/api/", timeout=5)
            data = response.json()
            return data.get("image", RecipeImageGenerator.generate_from_unsplash(recipe_name))
        except:
            return RecipeImageGenerator.generate_from_unsplash(recipe_name)