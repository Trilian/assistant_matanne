"""
Service OpenFoodFacts - Enrichissement des produits par code-barres

Récupère les informations nutritionnelles et descriptives depuis
l'API gratuite OpenFoodFacts.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from src.core.cache import Cache
from src.core.decorators import avec_gestion_erreurs

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

OPENFOODFACTS_API = "https://world.openfoodfacts.org/api/v2/product"
OPENFOODFACTS_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"

# Cache TTL: 24h (les produits changent peu)
CACHE_TTL = 86400


# ═══════════════════════════════════════════════════════════
# DATACLASSES
# ═══════════════════════════════════════════════════════════


@dataclass
class NutritionInfo:
    """Informations nutritionnelles pour 100g."""

    energie_kcal: float | None = None
    proteines_g: float | None = None
    glucides_g: float | None = None
    sucres_g: float | None = None
    lipides_g: float | None = None
    satures_g: float | None = None
    fibres_g: float | None = None
    sel_g: float | None = None

    nutriscore: str | None = None  # A, B, C, D, E
    nova_group: int | None = None  # 1-4 (transformation)
    ecoscore: str | None = None  # A, B, C, D, E


@dataclass
class ProduitOpenFoodFacts:
    """Produit enrichi depuis OpenFoodFacts."""

    # Identifiants
    code_barres: str
    nom: str

    # Infos de base
    marque: str | None = None
    quantite: str | None = None  # Ex: "500g", "1L"
    categories: list[str] = field(default_factory=list)

    # Images
    image_url: str | None = None
    image_thumb_url: str | None = None

    # Nutrition
    nutrition: NutritionInfo | None = None

    # Ingrédients
    ingredients_texte: str | None = None
    allergenes: list[str] = field(default_factory=list)
    traces: list[str] = field(default_factory=list)

    # Labels
    labels: list[str] = field(default_factory=list)  # Bio, Sans gluten, etc.
    origine: str | None = None

    # Conservation
    conservation: str | None = None
    duree_conservation_jours: int | None = None

    # Métadonnées
    source: str = "openfoodfacts"
    date_recuperation: datetime = field(default_factory=datetime.now)
    confiance: float = 0.0  # 0-1


# ═══════════════════════════════════════════════════════════
# SERVICE OPENFOODFACTS
# ═══════════════════════════════════════════════════════════


class OpenFoodFactsService:
    """
    Service d'enrichissement produits via OpenFoodFacts.

    API gratuite et collaborative pour récupérer:
    - Nom, marque, quantité
    - Informations nutritionnelles
    - Nutriscore, Nova, Ecoscore
    - Ingrédients, allergènes
    - Images produit
    """

    def __init__(self):
        self.cache = Cache
        self.timeout = 10.0
        self.user_agent = "AssistantMatanne/1.0 (contact@example.com)"

    def rechercher_produit(self, code_barres: str) -> ProduitOpenFoodFacts | None:
        """
        Recherche un produit par son code-barres.

        Args:
            code_barres: Code EAN-13, EAN-8 ou UPC

        Returns:
            ProduitOpenFoodFacts ou None si non trouvé
        """
        # Vérifier le cache
        cache_key = f"off_product_{code_barres}"
        cached = self.cache.obtenir(cache_key)
        if cached:
            logger.debug(f"Cache hit pour {code_barres}")
            return cached

        try:
            url = f"{OPENFOODFACTS_API}/{code_barres}.json"

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers={"User-Agent": self.user_agent})

                if response.status_code != 200:
                    logger.warning(f"OpenFoodFacts HTTP {response.status_code} pour {code_barres}")
                    return None

                data = response.json()

                if data.get("status") != 1:
                    logger.info(f"Produit {code_barres} non trouvé sur OpenFoodFacts")
                    return None

                product = data.get("product", {})
                result = self._parser_produit(code_barres, product)

                # Mettre en cache
                if result:
                    self.cache.definir(cache_key, result, ttl=CACHE_TTL)

                return result

        except httpx.TimeoutException:
            logger.warning(f"Timeout OpenFoodFacts pour {code_barres}")
            return None
        except Exception as e:
            logger.error(f"Erreur OpenFoodFacts: {e}")
            return None

    def _parser_produit(self, code_barres: str, data: dict) -> ProduitOpenFoodFacts:
        """Parse les données brutes OpenFoodFacts."""

        # Nom du produit
        nom = (
            data.get("product_name_fr")
            or data.get("product_name")
            or data.get("generic_name_fr")
            or data.get("generic_name")
            or "Produit inconnu"
        )

        # Nutrition
        nutriments = data.get("nutriments", {})
        nutrition = NutritionInfo(
            energie_kcal=nutriments.get("energy-kcal_100g"),
            proteines_g=nutriments.get("proteins_100g"),
            glucides_g=nutriments.get("carbohydrates_100g"),
            sucres_g=nutriments.get("sugars_100g"),
            lipides_g=nutriments.get("fat_100g"),
            satures_g=nutriments.get("saturated-fat_100g"),
            fibres_g=nutriments.get("fiber_100g"),
            sel_g=nutriments.get("salt_100g"),
            nutriscore=data.get("nutriscore_grade", "").upper() or None,
            nova_group=data.get("nova_group"),
            ecoscore=data.get("ecoscore_grade", "").upper() or None,
        )

        # Catégories
        categories_raw = data.get("categories_tags_fr") or data.get("categories_tags") or []
        categories = [
            c.replace("en:", "").replace("fr:", "").replace("-", " ").title()
            for c in categories_raw[:5]
        ]

        # Labels
        labels_raw = data.get("labels_tags_fr") or data.get("labels_tags") or []
        labels = [
            l.replace("en:", "").replace("fr:", "").replace("-", " ").title() for l in labels_raw
        ]

        # Allergènes
        allergenes_raw = data.get("allergens_tags") or []
        allergenes = [a.replace("en:", "").replace("fr:", "").title() for a in allergenes_raw]

        # Traces
        traces_raw = data.get("traces_tags") or []
        traces = [t.replace("en:", "").replace("fr:", "").title() for t in traces_raw]

        # Score de confiance basé sur la complétude
        completeness = data.get("completeness", 0)
        confiance = min(completeness / 100, 1.0) if completeness else 0.5

        return ProduitOpenFoodFacts(
            code_barres=code_barres,
            nom=nom,
            marque=data.get("brands"),
            quantite=data.get("quantity"),
            categories=categories,
            image_url=data.get("image_front_url"),
            image_thumb_url=data.get("image_front_small_url"),
            nutrition=nutrition,
            ingredients_texte=data.get("ingredients_text_fr") or data.get("ingredients_text"),
            allergenes=allergenes,
            traces=traces,
            labels=labels,
            origine=data.get("origins"),
            conservation=data.get("conservation_conditions"),
            confiance=confiance,
        )

    @avec_gestion_erreurs(default_return=[])
    def rechercher_par_nom(self, terme: str, limite: int = 10) -> list[ProduitOpenFoodFacts]:
        """
        Recherche des produits par nom/terme.

        Args:
            terme: Terme de recherche
            limite: Nombre max de résultats

        Returns:
            Liste de produits correspondants
        """
        try:
            params = {
                "search_terms": terme,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": limite,
                "lc": "fr",
                "cc": "fr",
            }

            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    OPENFOODFACTS_SEARCH, params=params, headers={"User-Agent": self.user_agent}
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                products = data.get("products", [])

                results = []
                for p in products:
                    code = p.get("code", "")
                    if code:
                        parsed = self._parser_produit(code, p)
                        results.append(parsed)

                return results

        except Exception as e:
            logger.error(f"Erreur recherche OpenFoodFacts: {e}")
            return []

    def obtenir_nutriscore_emoji(self, grade: str | None) -> str:
        """Retourne un emoji pour le nutriscore."""
        mapping = {
            "A": "🟢",
            "B": "🟡",
            "C": "🟠",
            "D": "🟧",
            "E": "🔴",
        }
        return mapping.get(grade.upper() if grade else "", "⚪")

    def obtenir_nova_description(self, group: int | None) -> str:
        """Retourne la description du groupe NOVA."""
        descriptions = {
            1: "🥬 Aliment non transformé",
            2: "🧂 Ingrédient culinaire",
            3: "🥫 Aliment transformé",
            4: "🍟 Ultra-transformé",
        }
        return descriptions.get(group, "❓ Inconnu")


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_service_instance: OpenFoodFactsService | None = None


def obtenir_service_openfoodfacts() -> OpenFoodFactsService:
    """Factory pour obtenir le service OpenFoodFacts (convention française)."""
    global _service_instance
    if _service_instance is None:
        _service_instance = OpenFoodFactsService()
    return _service_instance


def get_openfoodfacts_service() -> OpenFoodFactsService:
    """Factory pour obtenir le service OpenFoodFacts (alias anglais)."""
    return obtenir_service_openfoodfacts()
