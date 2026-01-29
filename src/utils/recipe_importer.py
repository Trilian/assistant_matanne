"""
Module d'import de recettes depuis différentes sources
- Sites web (URLs HTML)
- Fichiers PDF
- Texte brut
"""

import logging
import re
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RecipeImporter:
    """Classe pour importer des recettes depuis différentes sources"""
    
    @staticmethod
    def from_url(url: str) -> Optional[Dict[str, Any]]:
        """
        Importe une recette depuis une URL
        
        Args:
            url: URL du site contenant la recette
            
        Returns:
            Dict avec les infos extraites ou None
        """
        try:
            # Valider l'URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Télécharger le contenu
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parser le HTML
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                logger.error("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            recipe = RecipeImporter._extract_from_html(soup, url)
            
            if recipe:
                logger.info(f"✅ Recette importée depuis {url}")
                return recipe
            else:
                logger.warning(f"⚠️ Impossible d'extraire la recette depuis {url}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur import URL: {e}")
            return None
    
    @staticmethod
    def from_pdf(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Importe une recette depuis un fichier PDF
        
        Args:
            file_path: Chemin du fichier PDF
            
        Returns:
            Dict avec les infos extraites ou None
        """
        try:
            try:
                import PyPDF2
            except ImportError:
                logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
                return None
            
            recipe = {
                'nom': 'Recette importée du PDF',
                'ingredients': [],
                'etapes': [],
                'description': 'Recette extraite d\'un PDF'
            }
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            # Parser le texte
            recipe = RecipeImporter._extract_from_text(text)
            
            if recipe:
                logger.info(f"✅ Recette importée depuis {file_path}")
                return recipe
            else:
                logger.warning(f"⚠️ Impossible d'extraire la recette du PDF")
                return None
                
        except Exception as e:
            logger.error(f"Erreur import PDF: {e}")
            return None
    
    @staticmethod
    def from_text(text: str) -> Optional[Dict[str, Any]]:
        """
        Importe une recette depuis du texte brut
        
        Args:
            text: Texte contenant la recette
            
        Returns:
            Dict avec les infos extraites ou None
        """
        try:
            recipe = RecipeImporter._extract_from_text(text)
            
            if recipe:
                logger.info("✅ Recette importée depuis texte")
                return recipe
            else:
                logger.warning("⚠️ Impossible d'extraire la recette du texte")
                return None
                
        except Exception as e:
            logger.error(f"Erreur import texte: {e}")
            return None
    
    @staticmethod
    def _extract_from_html(soup, url: str) -> Optional[Dict[str, Any]]:
        """
        Extrait les infos de recette depuis du HTML
        Optimisé pour Marmiton, RecettesTin, CuisineAZ, etc.
        """
        from bs4 import BeautifulSoup
        
        recipe = {
            'nom': '',
            'description': '',
            'ingredients': [],
            'etapes': [],
            'temps_preparation': 0,
            'temps_cuisson': 0,
            'portions': 4,
            'source_url': url
        }
        
        # Chercher le titre (h1, h2, ou property og:title)
        title = soup.find('h1')
        if title:
            recipe['nom'] = title.get_text(strip=True)
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                recipe['nom'] = og_title.get('content', '')
        
        # Chercher la description
        desc = soup.find('meta', property='og:description')
        if desc:
            recipe['description'] = desc.get('content', '')
        else:
            desc_elem = soup.find('p', class_=re.compile('description', re.I))
            if desc_elem:
                recipe['description'] = desc_elem.get_text(strip=True)
        
        # MARMITON - Extraction spécifique des ingrédients
        marmiton_ingredients = soup.find_all(re.compile('^li$', re.I), class_=re.compile('ingredient', re.I))
        if marmiton_ingredients:
            for li in marmiton_ingredients:
                text = li.get_text(strip=True)
                if text and len(text) > 2:
                    recipe['ingredients'].append(text)
        
        # MARMITON - Extraction spécifique des étapes
        marmiton_etapes = soup.find_all(re.compile('^li$', re.I), class_=re.compile('recipe-step', re.I))
        if marmiton_etapes:
            for idx, li in enumerate(marmiton_etapes, 1):
                text = li.get_text(strip=True)
                if text and len(text) > 2:
                    recipe['etapes'].append(f"{idx}. {text}")
        
        # Si pas trouvé avec Marmiton, chercher les listes génériques
        if not recipe['ingredients']:
            # Chercher des listes <ul> ou <ol> contenant des ingrédients
            for ul in soup.find_all(['ul', 'ol']):
                section_name = ul.find_previous(['h2', 'h3', 'h4', 'div'])
                if section_name:
                    section_text = section_name.get_text().lower()
                    if 'ingrédient' in section_text or 'ingredient' in section_text:
                        for li in ul.find_all('li', recursive=False):
                            text = li.get_text(strip=True)
                            if text and len(text) > 2:
                                recipe['ingredients'].append(text)
                        break
        
        # Si pas trouvé, chercher avec des classes communes
        if not recipe['ingredients']:
            ingredient_classes = ['ingredients', 'ingredient-list', 'ingredient', 'ingredient-item']
            for ing_class in ingredient_classes:
                ing_list = soup.find('div', class_=re.compile(ing_class, re.I))
                if ing_list:
                    for li in ing_list.find_all('li'):
                        text = li.get_text(strip=True)
                        if text and len(text) > 2:
                            recipe['ingredients'].append(text)
                    if recipe['ingredients']:
                        break
        
        # Si pas trouvé les étapes, chercher les listes génériques
        if not recipe['etapes']:
            for ol in soup.find_all(['ol', 'ul']):
                section_name = ol.find_previous(['h2', 'h3', 'h4', 'div'])
                if section_name:
                    section_text = section_name.get_text().lower()
                    if any(word in section_text for word in ['étape', 'preparation', 'instruction', 'steps', 'directions']):
                        for idx, li in enumerate(ol.find_all('li', recursive=False), 1):
                            text = li.get_text(strip=True)
                            if text and len(text) > 2:
                                recipe['etapes'].append(f"{idx}. {text}")
                        break
        
        # Si pas trouvé, chercher avec des classes communes
        if not recipe['etapes']:
            etape_classes = ['steps', 'instructions', 'etapes', 'directions', 'preparation']
            for etape_class in etape_classes:
                etape_list = soup.find('div', class_=re.compile(etape_class, re.I))
                if etape_list:
                    for idx, li in enumerate(etape_list.find_all('li'), 1):
                        text = li.get_text(strip=True)
                        if text and len(text) > 2:
                            recipe['etapes'].append(f"{idx}. {text}")
                    if recipe['etapes']:
                        break
        
        # Chercher le temps de préparation/cuisson (schema.org)
        time_elem = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:prep_time'})
        if time_elem:
            time_str = time_elem.get('content', '0')
            recipe['temps_preparation'] = RecipeImporter._parse_duration(time_str)
        
        # Si pas trouvé avec schema.org, chercher avec itemprop
        if recipe['temps_preparation'] == 0:
            prep_time = soup.find(re.compile('^[^>]*$', re.I), {'itemprop': 'prepTime'})
            if prep_time:
                time_str = prep_time.get('content', '0')
                recipe['temps_preparation'] = RecipeImporter._parse_duration(time_str)
        
        cook_time = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:cook_time'})
        if cook_time:
            time_str = cook_time.get('content', '0')
            recipe['temps_cuisson'] = RecipeImporter._parse_duration(time_str)
        
        # Si pas trouvé, chercher avec itemprop
        if recipe['temps_cuisson'] == 0:
            cook_time_elem = soup.find(re.compile('^[^>]*$', re.I), {'itemprop': 'cookTime'})
            if cook_time_elem:
                time_str = cook_time_elem.get('content', '0')
                recipe['temps_cuisson'] = RecipeImporter._parse_duration(time_str)
        
        # Chercher les portions
        yield_elem = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:yield'})
        if yield_elem:
            yield_str = yield_elem.get('content', '4')
            try:
                recipe['portions'] = int(re.search(r'\d+', yield_str).group())
            except:
                recipe['portions'] = 4
        
        # Si pas trouvé, chercher avec itemprop
        if recipe['portions'] == 4:
            yield_elem = soup.find(re.compile('^[^>]*$', re.I), {'itemprop': 'recipeYield'})
            if yield_elem:
                try:
                    recipe['portions'] = int(re.search(r'\d+', yield_elem.get_text()).group())
                except:
                    recipe['portions'] = 4
        
        return recipe if recipe['nom'] else None
    
    @staticmethod
    def _extract_from_text(text: str) -> Optional[Dict[str, Any]]:
        """
        Extrait les infos de recette depuis du texte brut
        """
        recipe = {
            'nom': '',
            'description': '',
            'ingredients': [],
            'etapes': [],
            'temps_preparation': 0,
            'temps_cuisson': 0,
            'portions': 4
        }
        
        lines = text.split('\n')
        
        # Premier ligne = nom
        if lines:
            recipe['nom'] = lines[0].strip()
        
        # Chercher sections
        current_section = None
        for line in lines[1:]:
            line = line.strip()
            
            if not line:
                continue
            
            # Détecter les sections
            if 'ingrédient' in line.lower() or 'ingredients' in line.lower():
                current_section = 'ingredients'
                continue
            elif 'étape' in line.lower() or 'instruction' in line.lower() or 'préparation' in line.lower():
                current_section = 'etapes'
                continue
            elif 'temps' in line.lower():
                # Parser les temps
                if 'prep' in line.lower():
                    match = re.search(r'(\d+)', line)
                    if match:
                        recipe['temps_preparation'] = int(match.group(1))
                elif 'cuisson' in line.lower() or 'cook' in line.lower():
                    match = re.search(r'(\d+)', line)
                    if match:
                        recipe['temps_cuisson'] = int(match.group(1))
                continue
            elif 'portion' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    recipe['portions'] = int(match.group(1))
                continue
            
            # Ajouter au contenu actuel
            if current_section == 'ingredients' and line and not line.startswith('#'):
                recipe['ingredients'].append(line.lstrip('- •*').strip())
            elif current_section == 'etapes' and line and not line.startswith('#'):
                recipe['etapes'].append(line.lstrip('- •*').strip())
            elif not current_section and not recipe['description']:
                recipe['description'] = line
        
        return recipe if recipe['nom'] else None
    
    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """
        Parse une durée ISO 8601 (PT30M, PT1H30M, etc.)
        """
        try:
            # Format ISO 8601: PT[n]H[n]M[n]S
            hours = re.search(r'(\d+)H', duration_str)
            minutes = re.search(r'(\d+)M', duration_str)
            
            total_minutes = 0
            if hours:
                total_minutes += int(hours.group(1)) * 60
            if minutes:
                total_minutes += int(minutes.group(1))
            
            return total_minutes
        except:
            return 0
