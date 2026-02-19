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
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from src.core.ai import ClientIA, obtenir_client_ia
from src.core.decorators import avec_gestion_erreurs
from src.services.core.base import BaseAIService

# Parsers et schémas extraits dans parsers.py
from src.services.cuisine.recettes.parsers import (
    CuisineAZParser,
    GenericRecipeParser,
    ImportedIngredient,
    ImportedRecipe,
    ImportResult,
    MarmitonParser,
    RecipeParser,
)

# Rétrocompatibilité: re-export des classes pour les imports existants
__all__ = [
    "ImportedIngredient",
    "ImportedRecipe",
    "ImportResult",
    "RecipeParser",
    "MarmitonParser",
    "CuisineAZParser",
    "GenericRecipeParser",
    "RecipeImportService",
    "obtenir_service_import_recettes",
    "get_recipe_import_service",
]

logger = logging.getLogger(__name__)


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
        "marmiton.org": MarmitonParser,
        "cuisineaz.com": CuisineAZParser,
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
            client = obtenir_client_ia()
        except Exception:
            client = None

        super().__init__(
            client=client,
            cache_prefix="recipe_import",
            default_ttl=86400,  # 24h cache
            service_name="recipe_import",
        )

        self.http_client = httpx.Client(
            headers={"User-Agent": self.USER_AGENT},
            timeout=30.0,
            follow_redirects=True,
        )

    def _get_parser_for_url(self, url: str) -> type:
        """Retourne le parser approprié pour l'URL."""
        domain = urlparse(url).netloc.lower()
        domain = domain.replace("www.", "")

        for site_domain, parser in self.SITE_PARSERS.items():
            if site_domain in domain:
                return parser

        return GenericRecipeParser

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
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
            if parsed.scheme not in ("http", "https"):
                return ImportResult(
                    success=False, message="URL invalide (doit commencer par http:// ou https://)"
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
                success=False, message=f"Erreur HTTP {e.response.status_code}", errors=[str(e)]
            )
        except Exception as e:
            return ImportResult(
                success=False, message=f"Impossible de télécharger la page: {e}", errors=[str(e)]
            )

        # Parser le HTML
        soup = BeautifulSoup(html_content, "html.parser")

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
                success=False, message="Extraction incomplète", recipe=recipe, errors=errors
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
            errors=errors,
        )

    def _extract_with_ai(self, html_content: str, url: str) -> ImportedRecipe | None:
        """Utilise l'IA pour extraire la recette du HTML."""
        if not self.client:
            return None

        # Nettoyer le HTML pour réduire les tokens
        soup = BeautifulSoup(html_content, "html.parser")

        # Supprimer scripts, styles, nav, footer, etc.
        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            tag.decompose()

        # Garder seulement le texte principal
        text_content = soup.get_text(separator="\n", strip=True)
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
                    nom=data.get("nom", ""),
                    description=data.get("description", ""),
                    temps_preparation=data.get("temps_preparation", 0),
                    temps_cuisson=data.get("temps_cuisson", 0),
                    portions=data.get("portions", 4),
                    difficulte=data.get("difficulte", "moyen"),
                    source_url=url,
                    source_site=f"IA - {urlparse(url).netloc}",
                    confiance_score=0.7,  # Score IA
                )

                for ing_data in data.get("ingredients", []):
                    recipe.ingredients.append(
                        ImportedIngredient(
                            nom=ing_data.get("nom", ""),
                            quantite=ing_data.get("quantite"),
                            unite=ing_data.get("unite", ""),
                        )
                    )

                recipe.etapes = data.get("etapes", [])

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


def obtenir_service_import_recettes() -> RecipeImportService:
    """Factory pour le service d'import de recettes (convention française)."""
    global _import_service
    if _import_service is None:
        _import_service = RecipeImportService()
    return _import_service


def get_recipe_import_service() -> RecipeImportService:
    """Factory pour le service d'import de recettes (alias anglais)."""
    return obtenir_service_import_recettes()
