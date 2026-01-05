"""
Service Import/Export Courses

Gère l'import et l'export des listes de courses en CSV/JSON.
Utile pour :
- Imprimer listes
- Partager avec famille
- Import depuis autres apps
"""
import logging
from typing import List, Dict, Tuple
from datetime import date

from src.services.io_service import IOService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

COURSES_FIELD_MAPPING = {
    "nom": "Article",
    "quantite": "Quantité",
    "unite": "Unité",
    "priorite": "Priorité",
    "magasin": "Magasin",
    "rayon": "Rayon",
    "achete": "Acheté"
}

COURSES_REQUIRED_FIELDS = ["nom", "quantite"]

PRIORITES_VALIDES = ["haute", "moyenne", "basse"]


# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

class CoursesExporter:
    """Exporteur de listes de courses."""

    @staticmethod
    def to_csv(articles: List[Dict], include_achetes: bool = False) -> str:
        """
        Exporte liste de courses en CSV.

        Args:
            articles: Articles à exporter
            include_achetes: Inclure articles déjà achetés

        Returns:
            String CSV

        Example:
            >>> articles = courses_service.get_liste_active()
            >>> csv_data = CoursesExporter.to_csv(articles)
        """
        # Filtrer si demandé
        if not include_achetes:
            articles = [a for a in articles if not a.get("achete", False)]

        # Enrichir pour export lisible
        articles_enriched = []

        for article in articles:
            enriched = article.copy()

            # Checkbox visuelle pour impression
            enriched["achete"] = "☐" if not article.get("achete") else "☑"

            articles_enriched.append(enriched)

        return IOService.to_csv(articles_enriched, COURSES_FIELD_MAPPING)

    @staticmethod
    def to_json(articles: List[Dict], indent: int = 2) -> str:
        """
        Exporte liste de courses en JSON.

        Args:
            articles: Articles à exporter
            indent: Indentation JSON

        Returns:
            String JSON
        """
        return IOService.to_json(articles, indent=indent)

    @staticmethod
    def to_printable(articles: List[Dict], grouper_par_magasin: bool = True) -> str:
        """
        Génère liste imprimable formatée.

        Args:
            articles: Articles
            grouper_par_magasin: Grouper par magasin pour optimiser courses

        Returns:
            String formaté pour impression

        Example:
            >>> printable = CoursesExporter.to_printable(articles)
            >>> print(printable)
        """
        output = []
        output.append("═" * 50)
        output.append("📋 LISTE DE COURSES")
        output.append(f"Date: {date.today().strftime('%d/%m/%Y')}")
        output.append("═" * 50)
        output.append("")

        if grouper_par_magasin:
            # Grouper par magasin
            from collections import defaultdict
            par_magasin = defaultdict(list)

            for article in articles:
                magasin = article.get("magasin", "Non défini")
                par_magasin[magasin].append(article)

            # Afficher par magasin
            for magasin, articles_magasin in sorted(par_magasin.items()):
                output.append(f"🏪 {magasin.upper()} ({len(articles_magasin)} articles)")
                output.append("─" * 50)

                for article in sorted(articles_magasin, key=lambda x: x.get("priorite", "moyenne")):
                    priorite_icon = {
                        "haute": "🔴",
                        "moyenne": "🟡",
                        "basse": "🟢"
                    }.get(article.get("priorite", "moyenne"), "⚪")

                    ligne = f"  ☐ {priorite_icon} {article['nom']}"
                    ligne += f" - {article['quantite']} {article['unite']}"

                    if article.get("rayon"):
                        ligne += f" (Rayon: {article['rayon']})"

                    output.append(ligne)

                output.append("")

        else:
            # Liste simple par priorité
            for priorite in ["haute", "moyenne", "basse"]:
                articles_priorite = [a for a in articles if a.get("priorite") == priorite]

                if articles_priorite:
                    output.append(f"{'🔴' if priorite == 'haute' else '🟡' if priorite == 'moyenne' else '🟢'} PRIORITÉ {priorite.upper()}")
                    output.append("─" * 50)

                    for article in articles_priorite:
                        output.append(
                            f"  ☐ {article['nom']} - {article['quantite']} {article['unite']}"
                        )

                    output.append("")

        output.append("═" * 50)
        output.append(f"TOTAL: {len(articles)} articles")
        output.append("═" * 50)

        return "\n".join(output)


# ═══════════════════════════════════════════════════════════
# IMPORT
# ═══════════════════════════════════════════════════════════

class CoursesImporter:
    """Importeur de listes de courses."""

    @staticmethod
    def from_csv(csv_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe liste de courses depuis CSV.

        Args:
            csv_str: Contenu CSV

        Returns:
            (articles_validés, erreurs)
        """
        articles, errors = IOService.from_csv(
            csv_str,
            COURSES_FIELD_MAPPING,
            COURSES_REQUIRED_FIELDS
        )

        # Validation supplémentaire
        validated_articles = []

        for idx, article in enumerate(articles, start=2):
            try:
                validation_errors = CoursesImporter._validate_article(article)

                if validation_errors:
                    errors.extend([f"Ligne {idx}: {err}" for err in validation_errors])
                    continue

                article = CoursesImporter._enrich_article(article)
                validated_articles.append(article)

            except Exception as e:
                errors.append(f"Ligne {idx}: Erreur validation - {str(e)}")

        logger.info(
            f"Import CSV courses: {len(validated_articles)} articles validés, "
            f"{len(errors)} erreurs"
        )

        return validated_articles, errors

    @staticmethod
    def from_json(json_str: str) -> Tuple[List[Dict], List[str]]:
        """
        Importe liste de courses depuis JSON.

        Args:
            json_str: Contenu JSON

        Returns:
            (articles_validés, erreurs)
        """
        articles, errors = IOService.from_json(json_str, COURSES_REQUIRED_FIELDS)

        # Validation
        validated_articles = []

        for idx, article in enumerate(articles, start=1):
            try:
                validation_errors = CoursesImporter._validate_article(article)

                if validation_errors:
                    errors.extend([f"Item {idx}: {err}" for err in validation_errors])
                    continue

                article = CoursesImporter._enrich_article(article)
                validated_articles.append(article)

            except Exception as e:
                errors.append(f"Item {idx}: Erreur validation - {str(e)}")

        logger.info(
            f"Import JSON courses: {len(validated_articles)} articles validés, "
            f"{len(errors)} erreurs"
        )

        return validated_articles, errors

    # ═══════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def _validate_article(article: Dict) -> List[str]:
        """Valide un article."""
        errors = []

        # Quantité positive
        if article.get("quantite") is not None:
            try:
                qty = float(article["quantite"])
                if qty <= 0:
                    errors.append("Quantité doit être > 0")
            except (ValueError, TypeError):
                errors.append("Quantité invalide")

        # Priorité valide
        if article.get("priorite"):
            if article["priorite"] not in PRIORITES_VALIDES:
                errors.append(
                    f"Priorité '{article['priorite']}' invalide. "
                    f"Valeurs: {', '.join(PRIORITES_VALIDES)}"
                )

        # Unité présente
        if not article.get("unite"):
            errors.append("Unité requise")

        return errors

    @staticmethod
    def _enrich_article(article: Dict) -> Dict:
        """Enrichit article avec valeurs par défaut."""
        # Priorité par défaut
        if not article.get("priorite"):
            article["priorite"] = "moyenne"

        # Unité par défaut
        if not article.get("unite"):
            article["unite"] = "pcs"

        # Statut acheté
        if "achete" not in article:
            article["achete"] = False

        return article