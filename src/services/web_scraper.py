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
        """Scraper spécifique Marmiton"""
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
        title_tag = soup.find('h1', class_='SHRD__sc-10plygc-0')
        if title_tag:
            recipe["nom"] = title_tag.get_text(strip=True)

        # Image
        img_tag = soup.find('img', class_='RCP__sc-1wtzf9a-4')
        if img_tag and img_tag.get('src'):
            recipe["image_url"] = img_tag['src']

        # Temps
        time_tags = soup.find_all('span', class_='SHRD__sc-10plygc-0')
        for tag in time_tags:
            text = tag.get_text(strip=True).lower()
            if 'préparation' in text:
                match = re.search(r'(\d+)', text)
                if match:
                    recipe["temps_preparation"] = int(match.group(1))
            elif 'cuisson' in text:
                match = re.search(r'(\d+)', text)
                if match:
                    recipe["temps_cuisson"] = int(match.group(1))

        # Portions
        portion_tag = soup.find('span', string=re.compile(r'personnes?', re.I))
        if portion_tag:
            match = re.search(r'(\d+)', portion_tag.get_text())
            if match:
                recipe["portions"] = int(match.group(1))

        # Ingrédients
        ing_section = soup.find('div', class_='RCP__sc-1wtzf9a-0')
        if ing_section:
            ing_items = ing_section.find_all('li')
            for idx, item in enumerate(ing_items, 1):
                text = item.get_text(strip=True)
                # Parser "200g de tomates"
                parsed = RecipeWebScraper._parse_ingredient(text)
                if parsed:
                    recipe["ingredients"].append(parsed)

        # Étapes
        steps_section = soup.find('div', class_='RCP__sc-1wtzf9a-1')
        if steps_section:
            step_items = steps_section.find_all('li')
            for idx, item in enumerate(step_items, 1):
                text = item.get_text(strip=True)
                if text:
                    recipe["etapes"].append({
                        "ordre": idx,
                        "description": text,
                        "duree": None
                    })

        return recipe if recipe["nom"] else None

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
        Parse une ligne d'ingrédient

        Exemples:
        - "200g de tomates"
        - "2 cuillères à soupe d'huile d'olive"
        - "1 oignon"
        """
        text = text.strip()

        # Pattern : "quantité unité de/d' ingrédient"
        pattern = r'^(\d+(?:[.,]\d+)?)\s*([a-zA-Zàéèêë]+)?\s*(?:de |d\')?(.+)$'
        match = re.match(pattern, text, re.I)

        if match:
            qty_str = match.group(1).replace(',', '.')
            unit = match.group(2) or "pcs"
            name = match.group(3).strip()

            try:
                qty = float(qty_str)
                return {
                    "nom": name,
                    "quantite": qty,
                    "unite": unit,
                    "optionnel": False
                }
            except ValueError:
                pass

        # Fallback : considérer tout comme 1 unité
        return {
            "nom": text,
            "quantite": 1.0,
            "unite": "pcs",
            "optionnel": False
        }

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