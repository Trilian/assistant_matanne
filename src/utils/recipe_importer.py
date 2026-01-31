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
        Optimisé pour JSON-LD (schema.org) - Marmiton, RecettesTin, CuisineAZ, etc.
        """
        from bs4 import BeautifulSoup
        import json
        
        recipe = {
            'nom': '',
            'description': '',
            'ingredients': [],
            'etapes': [],
            'temps_preparation': 0,
            'temps_cuisson': 0,
            'portions': 4,
            'source_url': url,
            'image_url': ''  # Nouvelle clé pour l'image
        }
        
        # D'abord essayer JSON-LD (schema.org) - BEAUCOUP plus fiable!
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Vérifier si c'est une recette
                if data.get('@type') == 'Recipe' or 'recipe' in str(data).lower():
                    # Récupérer le nom
                    if 'name' in data:
                        recipe['nom'] = data.get('name', '')
                    
                    # Récupérer la description
                    if 'description' in data:
                        recipe['description'] = data.get('description', '')
                    
                    # Récupérer les ingrédients
                    if 'recipeIngredient' in data:
                        ingredients = data.get('recipeIngredient', [])
                        if isinstance(ingredients, list):
                            recipe['ingredients'] = ingredients
                    
                    # Récupérer les étapes
                    if 'recipeInstructions' in data:
                        instructions = data.get('recipeInstructions', [])
                        if isinstance(instructions, list):
                            recipe['etapes'] = []
                            for idx, inst in enumerate(instructions, 1):
                                if isinstance(inst, dict):
                                    # Format HowToStep
                                    text = inst.get('text', '')
                                elif isinstance(inst, str):
                                    text = inst
                                else:
                                    continue
                                
                                if text:
                                    recipe['etapes'].append(f"{idx}. {text}")
                    
                    # Récupérer les temps
                    if 'prepTime' in data:
                        recipe['temps_preparation'] = RecipeImporter._parse_duration(data.get('prepTime', ''))
                    if 'cookTime' in data:
                        recipe['temps_cuisson'] = RecipeImporter._parse_duration(data.get('cookTime', ''))
                    
                    # Récupérer les portions
                    if 'recipeYield' in data:
                        yield_val = data.get('recipeYield', 4)
                        if isinstance(yield_val, list):
                            yield_val = yield_val[0] if yield_val else 4
                        try:
                            recipe['portions'] = int(str(yield_val).split()[0])
                        except:
                            recipe['portions'] = 4
                    
                    # Récupérer l'image
                    if 'image' in data:
                        image = data.get('image', '')
                        if isinstance(image, list):
                            image = image[0] if image else ''
                        if isinstance(image, dict):
                            image = image.get('url', '')
                        recipe['image_url'] = image
                    
                    # Si on a un nom, on a trouvé la recette!
                    if recipe['nom']:
                        return recipe
            except:
                pass  # Continuer si erreur JSON
        
        # Fallback: chercher le titre (h1, h2, ou property og:title)
        if not recipe['nom']:
            title = soup.find('h1')
            if title:
                recipe['nom'] = title.get_text(strip=True)
            else:
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    recipe['nom'] = og_title.get('content', '')
        
        # Chercher la description
        if not recipe['description']:
            desc = soup.find('meta', property='og:description')
            if desc:
                recipe['description'] = desc.get('content', '')
            else:
                desc_elem = soup.find('p', class_=re.compile('description', re.I))
                if desc_elem:
                    recipe['description'] = desc_elem.get_text(strip=True)
        
        # EXTRAIT IMAGE - Chercher les images de recette
        if not recipe['image_url']:
            # Priorité: og:image > twitter:image > img tags
            image_url = soup.find('meta', property='og:image')
            if image_url:
                recipe['image_url'] = image_url.get('content', '')
            else:
                twitter_image = soup.find('meta', {'name': 'twitter:image'})
                if twitter_image:
                    recipe['image_url'] = twitter_image.get('content', '')
                else:
                    # Chercher la première image grande dans le contenu
                    img = soup.find('img', class_=re.compile('recipe|dish|food|ingredient', re.I))
                    if img and img.get('src'):
                        recipe['image_url'] = img.get('src', '')
        
        # S'assurer que l'URL est absolue
        if recipe['image_url'] and not recipe['image_url'].startswith('http'):
            from urllib.parse import urljoin
            recipe['image_url'] = urljoin(url, recipe['image_url'])
        
        # Fallback pour les ingrédients si JSON-LD n'avait pas
        if not recipe['ingredients']:
            # Chercher MARMITON spécifiquement - div avec mrtn-recette_ingredients-items
            ing_container = soup.find('div', class_='mrtn-recette_ingredients-items')
            if ing_container:
                # Chercher tous les spans ou divs contenant les ingredients
                ing_divs = ing_container.find_all(['div', 'span'], recursive=True)
                for ing_div in ing_divs:
                    text = ing_div.get_text(strip=True)
                    # Éviter les vides et les trop courts
                    if text and len(text) > 3 and not text.isnumeric():
                        # Vérifier que ce n'est pas un bouton ou UI element
                        if not any(word in text.lower() for word in ['voir', 'moins', 'filtre', 'version']):
                            recipe['ingredients'].append(text)
                
                # Deduplicer
                recipe['ingredients'] = list(dict.fromkeys(recipe['ingredients']))
        
        # Fallback pour les étapes si JSON-LD n'avait pas
        if not recipe['etapes']:
            # Chercher les listes génériques
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
        + formats textuels français (1h 30, 1h30min, 30min, 1 heure, etc.)
        """
        try:
            if not duration_str:
                return 0
            
            duration_str = str(duration_str).strip()
            
            # Format ISO 8601: PT[n]H[n]M[n]S
            if duration_str.startswith('PT'):
                hours = re.search(r'(\d+)H', duration_str)
                minutes = re.search(r'(\d+)M', duration_str)
                
                total_minutes = 0
                if hours:
                    total_minutes += int(hours.group(1)) * 60
                if minutes:
                    total_minutes += int(minutes.group(1))
                
                return total_minutes
            
            # Formats français: "1h 30", "1h30min", "1h", "30min", "1 heure 30 minutes", etc.
            total_minutes = 0
            
            # Chercher les heures
            hours_match = re.search(r'(\d+)\s*(?:h|heure)', duration_str, re.IGNORECASE)
            if hours_match:
                total_minutes += int(hours_match.group(1)) * 60
            
            # Chercher les minutes
            minutes_match = re.search(r'(\d+)\s*(?:min|m(?:inute)?)', duration_str, re.IGNORECASE)
            if minutes_match:
                total_minutes += int(minutes_match.group(1))
            
            # Si rien trouvé, chercher juste un nombre
            if total_minutes == 0:
                number_match = re.search(r'(\d+)', duration_str)
                if number_match:
                    total_minutes = int(number_match.group(1))
            
            return total_minutes
        except:
            return 0
