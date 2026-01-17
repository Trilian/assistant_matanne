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
        
        # Chercher les ingrédients
        # Chercher des listes d'ingrédients courants
        ingredient_patterns = [
            re.compile('ingredient', re.I),
            re.compile('ingredient', re.I),
        ]
        
        # Chercher des listes <ul> ou <ol> contenant des ingrédients
        for ul in soup.find_all(['ul', 'ol']):
            section_name = ul.find_previous(['h2', 'h3', 'h4'])
            if section_name and 'ingrédient' in section_name.get_text().lower():
                for li in ul.find_all('li'):
                    text = li.get_text(strip=True)
                    if text and len(text) > 2:
                        recipe['ingredients'].append(text)
        
        # Chercher les étapes
        for ol in soup.find_all('ol'):
            section_name = ol.find_previous(['h2', 'h3', 'h4'])
            if section_name and any(word in section_name.get_text().lower() for word in ['étape', 'preparation', 'instruction']):
                for idx, li in enumerate(ol.find_all('li'), 1):
                    text = li.get_text(strip=True)
                    if text and len(text) > 2:
                        recipe['etapes'].append(f"{idx}. {text}")
        
        # Chercher le temps de préparation/cuisson (schema.org)
        time_elem = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:prep_time'})
        if time_elem:
            time_str = time_elem.get('content', '0')
            recipe['temps_preparation'] = RecipeImporter._parse_duration(time_str)
        
        cook_time = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:cook_time'})
        if cook_time:
            time_str = cook_time.get('content', '0')
            recipe['temps_cuisson'] = RecipeImporter._parse_duration(time_str)
        
        # Chercher les portions
        yield_elem = soup.find(re.compile('^meta$', re.I), {'property': 'recipe:yield'})
        if yield_elem:
            yield_str = yield_elem.get('content', '4')
            try:
                recipe['portions'] = int(re.search(r'\d+', yield_str).group())
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
