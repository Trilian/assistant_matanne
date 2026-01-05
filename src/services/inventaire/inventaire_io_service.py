"""
Service Import/Export Inventaire

Gère l'import et l'export de l'inventaire en CSV/JSON avec :
- Validation automatique des données
- Gestion des dates de péremption
- Validation des seuils
- Enrichissement avec catégories
"""
import logging
from typing import List, Dict, Tuple
from datetime import date

from src.services.io_service import IOService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

INVENTAIRE_FIELD_MAPPING = {
    "nom": "Nom",
    "categorie": "Catégorie",
    "quantite": "Quantité",
    "unite": "Unité",
    "quantite_min": "Seuil",
    "emplacement": "Emplacement",
    "date_peremption": "Péremption"
}

INVENTAIRE_REQUIRED_FIELDS = ["nom", "quantite"]

CATEGORIES_VALIDES = [
    "Légumes", "Fruits", "Féculents", "Protéines", "Laitier",
    "Épices & Condiments", "Conserves", "Surgelés", "Autre"
]

EMPLACEMENTS_VALIDES = [
    "Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"
]


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

class InventaireExporter:
    """Exporteur d'inventaire avec enrichissement."""

    @staticmethod
    def to_csv(articles: List[Dict]) -> str:
        """
        Exporte inventaire en CSV.

        Args:
            articles: Liste d'articles inventaire

        Returns:
            String CSV avec tous les champs

        Example:
            >>> articles = inventaire_service.get_inventaire_complet()
            >>> csv_data = InventaireExporter.to_csv(articles)
        """
        # Enrichir avec statuts pour export complet
        articles_enriched = []

        for article in articles:
            enriched = article.copy()

            # Formater date péremption
            if enriched.get("date_peremption"):
                if isinstance(enriched["date_peremption"], date):
                    enriched["date_peremption"] = enriched["date_peremption"].strftime("%d/%m/%Y")

            articles_enriched.append(enriched)

        return IOService.to_csv(articles_enriched, INVENTAIRE_FIELD_MAPPING)

    @staticmethod
    def to_json(articles: List[Dict], indent: int = 2) -> str:
        """
        Exporte inventaire en JSON.

        Args:
            articles: Liste d'articles inventaire
            indent: Indentation JSON

        Returns:
            String JSON
        """
        # Convertir dates pour JSON
        articles_json = []

        for article in articles:
            article_copy = article.copy()

            if article_copy.get("date_peremption") and isinstance(article_copy["date_peremption"], date):
                article_copy["date_peremption"] = article_copy["date_peremption"].isoformat()

            articles_json.append(article_copy)

        return IOService.to_json(articles_json, indent=indent)


# ═══════════════════════════════════════════════════════════
# IMPORT
# ═══════════════════════════════════════════════════════════

class InventaireImporter:
    """Importeur d'inventaire avec validation stricte."""

    @staticmethod
    def from_csv(csv_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe inventaire depuis CSV avec validation.

        Args:
            csv_str: Contenu CSV

        Returns:
            (articles_validés, erreurs)

        Validations appliquées :
        - Champs requis présents
        - Quantités > 0
        - Catégories valides
        - Emplacements valides
        - Dates péremption futures
        - Seuils cohérents (seuil < quantité idéalement)
        """
        articles, errors = IOService.from_csv(
            csv_str,
            INVENTAIRE_FIELD_MAPPING,
            INVENTAIRE_REQUIRED_FIELDS
        )

        # Validation supplémentaire
        validated_articles = []

        for idx, article in enumerate(articles, start=2):
            try:
                # Validation métier
                validation_errors = InventaireImporter._validate_article(article)

                if validation_errors:
                    errors.extend([f"Ligne {idx}: {err}" for err in validation_errors])
                    continue

                # Enrichissement automatique
                article = InventaireImporter._enrich_article(article)

                validated_articles.append(article)

            except Exception as e:
                errors.append(f"Ligne {idx}: Erreur validation - {str(e)}")

        logger.info(
            f"Import CSV: {len(validated_articles)} articles validés, "
            f"{len(errors)} erreurs"
        )

        return validated_articles, errors

    @staticmethod
    def from_json(json_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe inventaire depuis JSON avec validation.

        Args:
            json_str: Contenu JSON

        Returns:
            (articles_validés, erreurs)
        """
        articles, errors = IOService.from_json(json_str, INVENTAIRE_REQUIRED_FIELDS)

        # Validation supplémentaire
        validated_articles = []

        for idx, article in enumerate(articles, start=1):
            try:
                validation_errors = InventaireImporter._validate_article(article)

                if validation_errors:
                    errors.extend([f"Item {idx}: {err}" for err in validation_errors])
                    continue

                article = InventaireImporter._enrich_article(article)
                validated_articles.append(article)

            except Exception as e:
                errors.append(f"Item {idx}: Erreur validation - {str(e)}")

        logger.info(
            f"Import JSON: {len(validated_articles)} articles validés, "
            f"{len(errors)} erreurs"
        )

        return validated_articles, errors

    # ═══════════════════════════════════════════════════════════
    # VALIDATION MÉTIER
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _validate_article(article: Dict) -> List[str]:
        """
        Valide un article selon règles métier.

        Args:
            article: Données article à valider

        Returns:
            Liste d'erreurs (vide si OK)
        """
        errors = []

        # 1. Quantité positive
        if article.get("quantite") is not None:
            try:
                qty = float(article["quantite"])
                if qty < 0:
                    errors.append("Quantité doit être >= 0")
            except (ValueError, TypeError):
                errors.append("Quantité invalide")

        # 2. Seuil positif si présent
        if article.get("quantite_min") is not None:
            try:
                seuil = float(article["quantite_min"])
                if seuil < 0:
                    errors.append("Seuil doit être >= 0")

                # Warning si seuil > quantité (mais pas bloquant)
                if article.get("quantite") and seuil > float(article["quantite"]):
                    logger.warning(
                        f"Article '{article.get('nom')}': seuil ({seuil}) > quantité ({article['quantite']})"
                    )
            except (ValueError, TypeError):
                errors.append("Seuil invalide")

        # 3. Catégorie valide si présente
        if article.get("categorie"):
            if article["categorie"] not in CATEGORIES_VALIDES:
                errors.append(
                    f"Catégorie '{article['categorie']}' invalide. "
                    f"Valeurs: {', '.join(CATEGORIES_VALIDES)}"
                )

        # 4. Emplacement valide si présent
        if article.get("emplacement"):
            if article["emplacement"] not in EMPLACEMENTS_VALIDES:
                errors.append(
                    f"Emplacement '{article['emplacement']}' invalide. "
                    f"Valeurs: {', '.join(EMPLACEMENTS_VALIDES)}"
                )

        # 5. Date péremption future si présente
        if article.get("date_peremption"):
            try:
                if isinstance(article["date_peremption"], str):
                    # Parser la date
                    from datetime import datetime
                    peremption = datetime.strptime(article["date_peremption"], "%d/%m/%Y").date()
                    article["date_peremption"] = peremption

                if isinstance(article["date_peremption"], date):
                    if article["date_peremption"] < date.today():
                        # Warning mais pas bloquant (peut importer produits périmés pour suivi)
                        logger.warning(
                            f"Article '{article.get('nom')}': date péremption passée"
                        )
            except Exception as e:
                errors.append(f"Date péremption invalide: {str(e)}")

        # 6. Unité présente
        if not article.get("unite"):
            errors.append("Unité requise")

        return errors

    @staticmethod
    def _enrich_article(article: Dict) -> Dict:
        """
        Enrichit un article avec valeurs par défaut.

        Args:
            article: Article à enrichir

        Returns:
            Article enrichi
        """
        # Valeurs par défaut
        if not article.get("categorie"):
            article["categorie"] = "Autre"

        if not article.get("unite"):
            article["unite"] = "pcs"

        if article.get("quantite_min") is None:
            # Seuil par défaut = 20% de la quantité actuelle
            if article.get("quantite"):
                article["quantite_min"] = max(1.0, float(article["quantite"]) * 0.2)
            else:
                article["quantite_min"] = 1.0

        if not article.get("emplacement"):
            # Deviner emplacement selon catégorie
            categorie = article.get("categorie", "")

            if categorie in ["Légumes", "Fruits", "Laitier", "Protéines"]:
                article["emplacement"] = "Frigo"
            elif categorie == "Surgelés":
                article["emplacement"] = "Congélateur"
            else:
                article["emplacement"] = "Placard"

        return article


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def valider_import_inventaire(articles: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """
    Valide une liste d'articles avant import massif.

    Args:
        articles: Articles à valider

    Returns:
        (articles_valides, erreurs_globales)

    Example:
        >>> articles = [{"nom": "Tomates", "quantite": 5, ...}]
        >>> valides, erreurs = valider_import_inventaire(articles)
    """
    valides = []
    erreurs = []

    for idx, article in enumerate(articles, start=1):
        validation_errors = InventaireImporter._validate_article(article)

        if validation_errors:
            erreurs.extend([f"Article {idx} ({article.get('nom', '?')}): {err}" for err in validation_errors])
        else:
            valides.append(InventaireImporter._enrich_article(article))

    return valides, erreurs