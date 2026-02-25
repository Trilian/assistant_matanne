"""
Mixin Import/Export pour le service inventaire.

Contient les méthodes d'import et d'export d'articles:
- Import batch avec validation Pydantic
- Export CSV et JSON
- Validation de fichiers d'import
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from src.core.decorators import avec_gestion_erreurs
from src.core.exceptions import ErreurValidation

from .types import ArticleImport

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class InventaireIOMixin:
    """Mixin pour les opérations d'import/export de l'inventaire.

    Méthodes déléguées depuis ServiceInventaire:
    - importer_articles
    - exporter_inventaire
    - _exporter_csv
    - _exporter_json
    - valider_fichier_import

    Utilise self.get_inventaire_complet() et self.ajouter_article()
    du service principal (cooperative mixin pattern).
    """

    @avec_gestion_erreurs(default_return=[])
    def importer_articles(  # pragma: no cover
        self,
        articles_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Importe plusieurs articles en batch.

        Args:
            articles_data: Liste des articles à importer (dictionnaires)

        Returns:
            Liste des articles importés avec leurs IDs
        """
        resultats: list[dict[str, Any]] = []
        errors: list[str] = []

        for idx, article_data in enumerate(articles_data):
            try:
                # Valide avec Pydantic
                article_import = ArticleImport(**article_data)

                # Cherche ou crée l'ingrédient
                from src.core.db import obtenir_contexte_db
                from src.core.models import Ingredient

                db = obtenir_contexte_db().session

                ingredient = db.query(Ingredient).filter_by(nom=article_import.nom).first()

                if not ingredient:
                    ingredient = Ingredient(
                        nom=article_import.nom,
                        unite=article_import.unite,
                        categorie=article_import.categorie or "Autre",
                    )
                    db.add(ingredient)
                    db.commit()
                    db.refresh(ingredient)

                # Ajoute l'article à l'inventaire
                self.ajouter_article(
                    ingredient_id=ingredient.id,
                    quantite=article_import.quantite,
                    quantite_min=article_import.quantite_min,
                    emplacement=article_import.emplacement,
                    date_peremption=(
                        date.fromisoformat(article_import.date_peremption)
                        if article_import.date_peremption
                        else None
                    ),
                )

                resultats.append(
                    {
                        "nom": article_import.nom,
                        "status": "✅",
                        "message": "Importé avec succès",
                    }
                )

            except Exception as e:
                errors.append(f"Ligne {idx + 2}: {str(e)}")
                resultats.append(
                    {
                        "nom": article_data.get("nom", "?"),
                        "status": "❌",
                        "message": str(e),
                    }
                )

        logger.info(f"✅ {len(resultats) - len(errors)}/{len(resultats)} articles importés")

        return resultats

    @avec_gestion_erreurs(default_return=None)
    def exporter_inventaire(  # pragma: no cover
        self,
        format_export: str = "csv",
    ) -> str | None:
        """Exporte l'inventaire dans le format demandé.

        Args:
            format_export: "csv" ou "json"

        Returns:
            Contenu du fichier en string
        """
        inventaire = self.get_inventaire_complet()

        if format_export == "csv":
            return self._exporter_csv(inventaire)
        elif format_export == "json":
            return self._exporter_json(inventaire)
        else:
            raise ErreurValidation(f"Format non supporté: {format_export}")

    def _exporter_csv(self, inventaire: dict[str, Any]) -> str:  # pragma: no cover
        """Exporte en CSV"""
        import io

        output = io.StringIO()

        # Headers
        headers = [
            "Nom",
            "Quantité",
            "Unité",
            "Seuil Min",
            "Emplacement",
            "Catégorie",
            "Date Péremption",
            "État",
        ]
        output.write(",".join(headers) + "\n")

        # Données
        for article in inventaire["articles"]:
            row = [
                article["nom"],
                str(article["quantite"]),
                article.get("unite", ""),
                str(article["quantite_min"]),
                article.get("emplacement", ""),
                article.get("categorie", ""),
                str(article.get("date_peremption", "")),
                article.get("statut", ""),
            ]
            # Échapper les valeurs contenant des virgules
            row = [f'"{v}"' if "," in str(v) else str(v) for v in row]
            output.write(",".join(row) + "\n")

        return output.getvalue()

    def _exporter_json(self, inventaire: dict[str, Any]) -> str:  # pragma: no cover
        """Exporte en JSON"""
        import json

        export_data = {
            "date_export": datetime.utcnow().isoformat(),
            "nombre_articles": len(inventaire["articles"]),
            "articles": inventaire["articles"],
            "statistiques": inventaire.get("statistiques", {}),
        }

        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)

    def valider_fichier_import(  # pragma: no cover
        self,
        donnees: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Valide les données d'import et retourne un rapport.

        Args:
            donnees: Données parsées du fichier

        Returns:
            Rapport de validation
        """
        rapport = {
            "valides": 0,
            "invalides": 0,
            "erreurs": [],
            "articles_valides": [],
            "articles_invalides": [],
        }

        for idx, article in enumerate(donnees):
            try:
                article_import = ArticleImport(**article)
                rapport["valides"] += 1
                rapport["articles_valides"].append(
                    {
                        "nom": article_import.nom,
                        "quantite": article_import.quantite,
                    }
                )
            except Exception as e:
                rapport["invalides"] += 1
                rapport["erreurs"].append(
                    {
                        "ligne": idx + 2,
                        "erreur": str(e),
                    }
                )
                rapport["articles_invalides"].append(article.get("nom", "?"))

        return rapport


__all__ = [
    "InventaireIOMixin",
]
