"""
Service d'import de recettes depuis URL.

Fonctionnalités:
- Scraping de recettes depuis des sites populaires
- Extraction automatique des ingrédients, étapes, temps
- Support de nombreux formats de sites culinaires
- Parsing intelligent avec fallback IA
- Import en lot depuis fichier d'URLs
"""

import logging
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, HttpUrl

from src.core.ai import ClientIA, AnalyseurIA
from src.core.decorators import with_error_handling
from src.services.base_ai_service import BaseAIService

logger = logging.getLogger(__name__)


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
        return ' '.join(text.strip().split())
    
    @staticmethod
    def parse_duration(text: str) -> int:
        """Parse une durée en minutes."""
        if not text:
            return 0
        
        text = text.lower()
        minutes = 0
        
        # Heures
        hours_match = re.search(r'(\d+)\s*h', text)
        if hours_match:
            minutes += int(hours_match.group(1)) * 60
        
        # Minutes
        mins_match = re.search(r'(\d+)\s*(?:min|m(?:inute)?s?)', text)
        if mins_match:
            minutes += int(mins_match.group(1))
        
        # Si juste un nombre, supposer minutes
        if minutes == 0:
            just_number = re.search(r'^(\d+)$', text.strip())
            if just_number:
                minutes = int(just_number.group(1))
        
        return minutes
    
    @staticmethod
    def parse_portions(text: str) -> int:
        """Parse le nombre de portions."""
        if not text:
            return 4
        
        match = re.search(r'(\d+)', text)
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
            r'^(\d+(?:[.,]\d+)?)\s*(g|kg|ml|cl|l|cuill[eè]re[s]?\s*(?:[aà]\s*)?(?:soupe|caf[eé])?|c\.?\s*[aà]?\s*[sc]\.?|pinc[eé]e[s]?|sachet[s]?|tranche[s]?|feuille[s]?|gousse[s]?|brin[s]?)\s*(?:de\s*|d[\x27\x27])?\s*(.+)',
            r'^(\d+(?:[.,]\d+)?)\s+(.+)',  # Nombre + reste
        ]
        
        for pattern in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    quantite_str, unite, nom = groups
                    try:
                        quantite = float(quantite_str.replace(',', '.'))
                    except:
                        quantite = None
                    return ImportedIngredient(nom=nom.strip(), quantite=quantite, unite=unite.strip())
                elif len(groups) == 2:
                    quantite_str, nom = groups
                    try:
                        quantite = float(quantite_str.replace(',', '.'))
                    except:
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
        title = soup.find('h1')
        if title:
            recipe.nom = RecipeParser.clean_text(title.get_text())
        
        # Description
        desc = soup.find('p', class_=re.compile(r'description|intro', re.I))
        if desc:
            recipe.description = RecipeParser.clean_text(desc.get_text())
        
        # Image
        img = soup.find('img', class_=re.compile(r'recipe-media|photo', re.I))
        if img and img.get('src'):
            recipe.image_url = img['src']
        
        # Temps
        time_section = soup.find_all(class_=re.compile(r'time|duration|temps', re.I))
        for section in time_section:
            text = section.get_text().lower()
            if 'préparation' in text or 'prep' in text:
                recipe.temps_preparation = RecipeParser.parse_duration(text)
            elif 'cuisson' in text:
                recipe.temps_cuisson = RecipeParser.parse_duration(text)
        
        # Portions
        portions_el = soup.find(class_=re.compile(r'serving|portion|personne', re.I))
        if portions_el:
            recipe.portions = RecipeParser.parse_portions(portions_el.get_text())
        
        # Ingrédients
        ingredients_section = soup.find(class_=re.compile(r'ingredient', re.I))
        if ingredients_section:
            for item in ingredients_section.find_all(['li', 'span', 'p']):
                ing = RecipeParser.parse_ingredient(item.get_text())
                if ing.nom:
                    recipe.ingredients.append(ing)
        
        # Étapes
        steps_section = soup.find(class_=re.compile(r'step|instruction|etape|preparation', re.I))
        if steps_section:
            for item in steps_section.find_all(['li', 'p', 'div']):
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
        title = soup.find('h1', class_=re.compile(r'title', re.I))
        if not title:
            title = soup.find('h1')
        if title:
            recipe.nom = RecipeParser.clean_text(title.get_text())
        
        # Image
        img = soup.find('img', class_=re.compile(r'recipe|photo', re.I))
        if img and img.get('src'):
            src = img['src']
            if src.startswith('//'):
                src = 'https:' + src
            recipe.image_url = src
        
        # Temps et portions dans les meta
        for meta in soup.find_all('meta'):
            prop = meta.get('property', '') or meta.get('name', '')
            content = meta.get('content', '')
            
            if 'prepTime' in prop:
                recipe.temps_preparation = RecipeParser.parse_duration(content)
            elif 'cookTime' in prop:
                recipe.temps_cuisson = RecipeParser.parse_duration(content)
            elif 'recipeYield' in prop:
                recipe.portions = RecipeParser.parse_portions(content)
        
        # Ingrédients - JSON-LD si disponible
        script = soup.find('script', type='application/ld+json')
        if script:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    if 'recipeIngredient' in data:
                        for ing_text in data['recipeIngredient']:
                            ing = RecipeParser.parse_ingredient(ing_text)
                            if ing.nom:
                                recipe.ingredients.append(ing)
                    
                    if 'recipeInstructions' in data:
                        instructions = data['recipeInstructions']
                        if isinstance(instructions, list):
                            for step in instructions:
                                if isinstance(step, str):
                                    recipe.etapes.append(step)
                                elif isinstance(step, dict) and 'text' in step:
                                    recipe.etapes.append(step['text'])
            except:
                pass
        
        # Fallback HTML si pas de JSON-LD
        if not recipe.ingredients:
            for item in soup.find_all(class_=re.compile(r'ingredient', re.I)):
                ing = RecipeParser.parse_ingredient(item.get_text())
                if ing.nom:
                    recipe.ingredients.append(ing)
        
        if not recipe.etapes:
            steps_container = soup.find(class_=re.compile(r'instruction|step|preparation', re.I))
            if steps_container:
                for item in steps_container.find_all(['li', 'p']):
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
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                
                # Peut être une liste
                if isinstance(data, list):
                    data = next((d for d in data if isinstance(d, dict) and d.get('@type') == 'Recipe'), None)
                
                if isinstance(data, dict) and data.get('@type') == 'Recipe':
                    recipe.nom = data.get('name', '')
                    recipe.description = data.get('description', '')
                    recipe.image_url = data.get('image', [None])[0] if isinstance(data.get('image'), list) else data.get('image')
                    
                    # Temps
                    if 'prepTime' in data:
                        recipe.temps_preparation = RecipeParser.parse_duration(data['prepTime'])
                    if 'cookTime' in data:
                        recipe.temps_cuisson = RecipeParser.parse_duration(data['cookTime'])
                    if 'recipeYield' in data:
                        recipe.portions = RecipeParser.parse_portions(str(data['recipeYield']))
                    
                    # Ingrédients
                    for ing_text in data.get('recipeIngredient', []):
                        ing = RecipeParser.parse_ingredient(ing_text)
                        if ing.nom:
                            recipe.ingredients.append(ing)
                    
                    # Étapes
                    instructions = data.get('recipeInstructions', [])
                    if isinstance(instructions, str):
                        recipe.etapes = [s.strip() for s in instructions.split('.') if s.strip()]
                    elif isinstance(instructions, list):
                        for step in instructions:
                            if isinstance(step, str):
                                recipe.etapes.append(step)
                            elif isinstance(step, dict):
                                recipe.etapes.append(step.get('text', ''))
                    
                    recipe.confiance_score = 0.9
                    return recipe
            except:
                continue
        
        # 2. Fallback: extraction HTML heuristique
        # Titre
        for selector in ['h1', '[itemprop="name"]', '.recipe-title', '.title']:
            el = soup.select_one(selector)
            if el:
                recipe.nom = RecipeParser.clean_text(el.get_text())
                break
        
        # Description
        for selector in ['[itemprop="description"]', '.recipe-description', '.intro', 'meta[name="description"]']:
            el = soup.select_one(selector)
            if el:
                if el.name == 'meta':
                    recipe.description = el.get('content', '')
                else:
                    recipe.description = RecipeParser.clean_text(el.get_text())
                break
        
        # Ingrédients
        for selector in ['[itemprop="recipeIngredient"]', '.ingredient', '.ingredients li', '[class*="ingredient"] li']:
            elements = soup.select(selector)
            if elements:
                for el in elements:
                    ing = RecipeParser.parse_ingredient(el.get_text())
                    if ing.nom and ing.nom not in [i.nom for i in recipe.ingredients]:
                        recipe.ingredients.append(ing)
                break
        
        # Étapes
        for selector in ['[itemprop="recipeInstructions"]', '.instruction', '.steps li', '[class*="step"] p']:
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
        for selector in ['[itemprop="image"]', '.recipe-image img', 'meta[property="og:image"]']:
            el = soup.select_one(selector)
            if el:
                if el.name == 'meta':
                    recipe.image_url = el.get('content')
                else:
                    recipe.image_url = el.get('src') or el.get('content')
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


# ═══════════════════════════════════════════════════════════
# SERVICE D'IMPORT
# ═══════════════════════════════════════════════════════════


class RecipeImportService(BaseAIService):
    """
    Service d'import de recettes depuis des URLs.
    
    Supporte:
    - Sites français populaires (Marmiton, CuisineAZ, etc.)
    - Schema.org Recipe (JSON-LD)
    - Extraction heuristique
    - Fallback IA pour les pages difficiles
    """
    
    # Mapping domaine -> parser
    SITE_PARSERS = {
        'marmiton.org': MarmitonParser,
        'cuisineaz.com': CuisineAZParser,
    }
    
    # User-Agent pour les requêtes
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    def __init__(self):
        """Initialise le service d'import."""
        try:
            client = ClientIA()
        except:
            client = None
        
        super().__init__(
            client=client,
            cache_prefix="recipe_import",
            default_ttl=86400,  # 24h cache
            service_name="recipe_import"
        )
        
        self.http_client = httpx.Client(
            headers={"User-Agent": self.USER_AGENT},
            timeout=30.0,
            follow_redirects=True,
        )
    
    def _get_parser_for_url(self, url: str) -> type:
        """Retourne le parser approprié pour l'URL."""
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        
        for site_domain, parser in self.SITE_PARSERS.items():
            if site_domain in domain:
                return parser
        
        return GenericRecipeParser
    
    @with_error_handling(default_return=None, afficher_erreur=True)
    def import_from_url(self, url: str, use_ai_fallback: bool = True) -> ImportResult:
        """
        Importe une recette depuis une URL.
        
        Args:
            url: URL de la page de recette
            use_ai_fallback: Utiliser l'IA si l'extraction classique échoue
            
        Returns:
            ImportResult avec la recette ou les erreurs
        """
        logger.info(f"📥 Import recette depuis {url}")
        
        # Valider l'URL
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https'):
                return ImportResult(
                    success=False,
                    message="URL invalide (doit commencer par http:// ou https://)"
                )
        except Exception as e:
            return ImportResult(success=False, message=f"URL invalide: {e}")
        
        # Télécharger la page
        try:
            response = self.http_client.get(url)
            response.raise_for_status()
            html_content = response.text
        except httpx.HTTPStatusError as e:
            return ImportResult(
                success=False,
                message=f"Erreur HTTP {e.response.status_code}",
                errors=[str(e)]
            )
        except Exception as e:
            return ImportResult(
                success=False,
                message=f"Impossible de télécharger la page: {e}",
                errors=[str(e)]
            )
        
        # Parser le HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Choisir le parser approprié
        parser_class = self._get_parser_for_url(url)
        logger.debug(f"Utilisation du parser: {parser_class.__name__}")
        
        # Extraire la recette
        recipe = parser_class.parse(soup, url)
        
        # Vérifier la qualité de l'extraction
        if recipe.confiance_score < 0.3 or not recipe.nom:
            if use_ai_fallback and self.client:
                logger.info("⚙️ Score de confiance bas, utilisation de l'IA...")
                ai_recipe = self._extract_with_ai(html_content, url)
                if ai_recipe and ai_recipe.confiance_score > recipe.confiance_score:
                    recipe = ai_recipe
        
        # Validation finale
        errors = []
        if not recipe.nom:
            errors.append("Nom de recette non trouvé")
        if not recipe.ingredients:
            errors.append("Aucun ingrédient trouvé")
        if not recipe.etapes:
            errors.append("Aucune étape trouvée")
        
        if errors and recipe.confiance_score < 0.3:
            return ImportResult(
                success=False,
                message="Extraction incomplète",
                recipe=recipe,
                errors=errors
            )
        
        logger.info(
            f"✅ Recette importée: {recipe.nom} "
            f"({len(recipe.ingredients)} ingrédients, {len(recipe.etapes)} étapes, "
            f"confiance: {recipe.confiance_score:.0%})"
        )
        
        return ImportResult(
            success=True,
            message=f"Recette '{recipe.nom}' importée avec succès",
            recipe=recipe,
            errors=errors
        )
    
    def _extract_with_ai(self, html_content: str, url: str) -> ImportedRecipe | None:
        """Utilise l'IA pour extraire la recette du HTML."""
        if not self.client:
            return None
        
        # Nettoyer le HTML pour réduire les tokens
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer scripts, styles, nav, footer, etc.
        for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
            tag.decompose()
        
        # Garder seulement le texte principal
        text_content = soup.get_text(separator='\n', strip=True)
        # Limiter à 5000 caractères
        text_content = text_content[:5000]
        
        prompt = f"""Extrait les informations de cette recette de cuisine.
URL source: {url}

Contenu de la page:
{text_content}

Réponds en JSON avec cette structure exacte:
{{
    "nom": "Nom de la recette",
    "description": "Description courte",
    "temps_preparation": 30,
    "temps_cuisson": 45,
    "portions": 4,
    "difficulte": "facile|moyen|difficile",
    "ingredients": [
        {{"nom": "farine", "quantite": 200, "unite": "g"}},
        ...
    ],
    "etapes": [
        "Première étape...",
        "Deuxième étape...",
        ...
    ]
}}
"""
        
        try:
            import asyncio
            
            async def call_ai():
                return await self.call_with_cache(
                    prompt=prompt,
                    system_prompt="Tu es un expert en extraction de recettes. Réponds uniquement en JSON valide.",
                    temperature=0.3,
                    max_tokens=2000,
                    use_cache=False,
                )
            
            response = asyncio.run(call_ai())
            
            if response:
                # Parser la réponse JSON
                import json
                data = json.loads(response)
                
                recipe = ImportedRecipe(
                    nom=data.get('nom', ''),
                    description=data.get('description', ''),
                    temps_preparation=data.get('temps_preparation', 0),
                    temps_cuisson=data.get('temps_cuisson', 0),
                    portions=data.get('portions', 4),
                    difficulte=data.get('difficulte', 'moyen'),
                    source_url=url,
                    source_site=f"IA - {urlparse(url).netloc}",
                    confiance_score=0.7,  # Score IA
                )
                
                for ing_data in data.get('ingredients', []):
                    recipe.ingredients.append(ImportedIngredient(
                        nom=ing_data.get('nom', ''),
                        quantite=ing_data.get('quantite'),
                        unite=ing_data.get('unite', ''),
                    ))
                
                recipe.etapes = data.get('etapes', [])
                
                return recipe
                
        except Exception as e:
            logger.error(f"Erreur extraction IA: {e}")
        
        return None
    
    def import_batch(self, urls: list[str]) -> list[ImportResult]:
        """
        Importe plusieurs recettes en lot.
        
        Args:
            urls: Liste d'URLs à importer
            
        Returns:
            Liste de résultats d'import
        """
        results = []
        
        for url in urls:
            result = self.import_from_url(url)
            results.append(result)
        
        successes = sum(1 for r in results if r.success)
        logger.info(f"📊 Import lot terminé: {successes}/{len(urls)} réussis")
        
        return results


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_import_service: RecipeImportService | None = None


def get_recipe_import_service() -> RecipeImportService:
    """Factory pour le service d'import de recettes."""
    global _import_service
    if _import_service is None:
        _import_service = RecipeImportService()
    return _import_service


# ═══════════════════════════════════════════════════════════
# COMPOSANT UI STREAMLIT
# ═══════════════════════════════════════════════════════════


def render_import_recipe_ui():  # pragma: no cover
    """Interface Streamlit pour l'import de recettes."""
    import streamlit as st
    
    st.subheader("🌐 Importer une recette depuis le web")
    
    st.info(
        "📝 Collez l'URL d'une recette depuis Marmiton, CuisineAZ, "
        "ou tout autre site de cuisine."
    )
    
    # Import simple
    url = st.text_input(
        "URL de la recette",
        placeholder="https://www.marmiton.org/recettes/...",
        key="recipe_import_url"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        use_ai = st.checkbox("Utiliser l'IA si nécessaire", value=True, key="use_ai_import")
    
    with col2:
        import_btn = st.button("📥 Importer", type="primary", use_container_width=True)
    
    if import_btn and url:
        service = get_recipe_import_service()
        
        with st.spinner("Import en cours..."):
            result = service.import_from_url(url, use_ai_fallback=use_ai)
        
        if result.success and result.recipe:
            st.success(f"✅ {result.message}")
            
            recipe = result.recipe
            
            # Afficher la prévisualisation
            st.markdown("---")
            st.markdown(f"### {recipe.nom}")
            
            if recipe.image_url:
                st.image(recipe.image_url, width=300)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("⏱️ Préparation", f"{recipe.temps_preparation} min")
            with col_b:
                st.metric("🔥 Cuisson", f"{recipe.temps_cuisson} min")
            with col_c:
                st.metric("👥 Portions", recipe.portions)
            
            if recipe.description:
                st.markdown(f"*{recipe.description}*")
            
            # Ingrédients
            st.markdown("#### 🥕 Ingrédients")
            for ing in recipe.ingredients:
                qty = f"{ing.quantite} {ing.unite}" if ing.quantite else ""
                st.markdown(f"- {qty} {ing.nom}")
            
            # Étapes
            st.markdown("#### 📝 Préparation")
            for i, step in enumerate(recipe.etapes, 1):
                st.markdown(f"{i}. {step}")
            
            st.markdown("---")
            st.caption(f"🔗 Source: {recipe.source_site} | Confiance: {recipe.confiance_score:.0%}")
            
            # Bouton pour sauvegarder
            if st.button("💾 Ajouter à mes recettes", type="primary"):
                try:
                    from src.services.recettes import get_recette_service
                    
                    service = get_recette_service()
                    
                    # Préparer les données
                    recette_data = {
                        "nom": recipe.nom,
                        "description": recipe.description,
                        "temps_preparation": recipe.temps_preparation,
                        "temps_cuisson": recipe.temps_cuisson,
                        "portions": recipe.portions,
                        "difficulte": recipe.difficulte,
                        "url_image": recipe.image_url,
                        "ingredients": [
                            {"nom": ing.nom, "quantite": ing.quantite or 1, "unite": ing.unite}
                            for ing in recipe.ingredients
                        ],
                        "etapes": [
                            {"ordre": i, "description": step}
                            for i, step in enumerate(recipe.etapes, 1)
                        ],
                    }
                    
                    result = service.create_complete(recette_data)
                    if result:
                        st.success(f"✅ Recette '{recipe.nom}' ajoutée avec succès!")
                        st.balloons()
                    else:
                        st.error("❌ Erreur lors de l'ajout")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        
        else:
            st.error(f"❌ {result.message}")
            if result.errors:
                for error in result.errors:
                    st.warning(f"⚠️ {error}")
            
            if result.recipe:
                st.markdown("---")
                st.markdown("### Extraction partielle:")
                st.json(result.recipe.model_dump())
    
    # Import en lot
    st.markdown("---")
    with st.expander("📋 Import en lot (plusieurs URLs)"):
        urls_text = st.text_area(
            "URLs (une par ligne)",
            height=150,
            key="batch_import_urls",
            placeholder="https://www.marmiton.org/recette1\nhttps://www.cuisineaz.com/recette2"
        )
        
        if st.button("📥 Importer tout", key="batch_import_btn"):
            urls = [u.strip() for u in urls_text.split('\n') if u.strip()]
            
            if urls:
                service = get_recipe_import_service()
                
                progress_bar = st.progress(0)
                status = st.empty()
                
                results = []
                for i, url in enumerate(urls):
                    status.text(f"Import {i+1}/{len(urls)}: {url[:50]}...")
                    result = service.import_from_url(url)
                    results.append(result)
                    progress_bar.progress((i + 1) / len(urls))
                
                # Résumé
                successes = [r for r in results if r.success]
                failures = [r for r in results if not r.success]
                
                st.success(f"✅ {len(successes)}/{len(urls)} recettes importées")
                
                if failures:
                    with st.expander(f"⚠️ {len(failures)} échecs"):
                        for r in failures:
                            st.warning(f"{r.message}")
