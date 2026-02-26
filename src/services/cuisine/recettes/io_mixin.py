"""
Mixin Import/Export pour les recettes.

Extrait du service principal pour réduire sa taille.
Contient toutes les méthodes liées à:
- Export CSV/JSON
- Import depuis texte/URL/PDF
- Parsing d'ingrédients
"""

import csv
import json
import logging
from io import StringIO

from sqlalchemy.orm import Session

from src.core.caching import obtenir_cache
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import EtapeRecette, Ingredient, Recette, RecetteIngredient
from src.services.core.events import obtenir_bus

logger = logging.getLogger(__name__)


class RecetteIOExportMixin:
    """
    Mixin fournissant les fonctionnalités d'export.

    Méthodes d'export vers CSV et JSON.
    """

    def export_to_csv(self, recettes: list[Recette], separator: str = ",") -> str:
        """Exporte des recettes en CSV.

        Args:
            recettes: List of Recette objects to export
            separator: CSV separator character

        Returns:
            CSV string with recipe data
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "nom",
                "description",
                "temps_preparation",
                "temps_cuisson",
                "portions",
                "difficulte",
                "type_repas",
                "saison",
            ],
            delimiter=separator,
        )

        writer.writeheader()
        for r in recettes:
            writer.writerow(
                {
                    "nom": r.nom,
                    "description": r.description or "",
                    "temps_preparation": r.temps_preparation,
                    "temps_cuisson": r.temps_cuisson,
                    "portions": r.portions,
                    "difficulte": r.difficulte,
                    "type_repas": r.type_repas,
                    "saison": r.saison,
                }
            )

        logger.info(f"✅ Exported {len(recettes)} recipes to CSV")
        return output.getvalue()

    def export_to_json(self, recettes: list[Recette], indent: int = 2) -> str:
        """Exporte des recettes en JSON.

        Args:
            recettes: List of Recette objects to export
            indent: JSON indentation level

        Returns:
            JSON string with recipe data
        """
        data = []
        for r in recettes:
            data.append(
                {
                    "nom": r.nom,
                    "description": r.description,
                    "temps_preparation": r.temps_preparation,
                    "temps_cuisson": r.temps_cuisson,
                    "portions": r.portions,
                    "difficulte": r.difficulte,
                    "type_repas": r.type_repas,
                    "saison": r.saison,
                    "ingredients": [
                        {"nom": ri.ingredient.nom, "quantite": ri.quantite, "unite": ri.unite}
                        for ri in r.ingredients
                    ],
                    "etapes": [{"ordre": e.ordre, "description": e.description} for e in r.etapes],
                }
            )

        logger.info(f"✅ Exported {len(recettes)} recipes to JSON")
        return json.dumps(data, indent=indent, ensure_ascii=False)


class RecetteIOImportMixin:
    """
    Mixin fournissant les fonctionnalités d'import.

    Méthodes d'import depuis texte (avec parsing des ingrédients).
    """

    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    @avec_session_db
    def create_from_import(
        self,
        nom: str,
        type_repas: str,
        description: str,
        temps_preparation: int,
        temps_cuisson: int,
        portions: int,
        difficulte: str,
        ingredients_textes: list[str],
        etapes_textes: list[str],
        image_path: str | None = None,
        db: Session | None = None,
    ) -> Recette:
        """Crée une recette depuis un import (URL/PDF/texte).

        Parse les ingrédients en format texte libre ("200 g farine")
        et crée automatiquement les ingrédients manquants.

        Args:
            nom: Nom de la recette
            type_repas: Type de repas
            description: Description
            temps_preparation: Temps préparation (minutes)
            temps_cuisson: Temps cuisson (minutes)
            portions: Nombre de portions
            difficulte: Niveau de difficulté
            ingredients_textes: Liste de textes d'ingrédients ("200 g farine")
            etapes_textes: Liste de textes d'étapes
            image_path: Chemin ou URL de l'image
            db: Session DB (injectée)

        Returns:
            Recette créée
        """
        from datetime import datetime

        recette = Recette(
            nom=nom,
            type_repas=type_repas,
            description=description,
            temps_preparation=temps_preparation,
            temps_cuisson=temps_cuisson,
            portions=portions,
            difficulte=difficulte,
            url_image=image_path,
            updated_at=datetime.utcnow(),
        )
        db.add(recette)
        db.flush()

        # Parser et ajouter les ingrédients
        for ing_text in ingredients_textes:
            quantite, unite, nom_ing = self._parser_ingredient_texte(ing_text)

            ingredient = self._find_or_create_ingredient(db, nom_ing)
            ri = RecetteIngredient(
                recette_id=recette.id,
                ingredient_id=ingredient.id,
                quantite=quantite,
                unite=unite,
            )
            db.add(ri)

        # Ajouter les étapes
        for idx, etape_text in enumerate(etapes_textes, 1):
            etape = EtapeRecette(
                recette_id=recette.id,
                description=etape_text,
                ordre=idx,
            )
            db.add(etape)

        db.commit()
        obtenir_cache().invalidate(pattern="recettes")

        # Émettre événement domaine
        obtenir_bus().emettre(
            "recette.importee",
            {"recette_id": recette.id, "nom": recette.nom, "source": "import"},
            source="recettes",
        )

        logger.info(f"✅ Recette importée : {recette.nom} (ID: {recette.id})")
        return recette

    @staticmethod
    def _parser_ingredient_texte(ing_text: str) -> tuple[float, str, str]:
        """Parse un texte d'ingrédient en (quantité, unité, nom).

        Exemples: "200 g farine" → (200.0, "g", "farine")
                  "2 oignons" → (2.0, "g", "oignons")
                  "sel" → (1.0, "", "sel")
        """
        parts = ing_text.split(maxsplit=2)
        if len(parts) >= 3:
            quantite_str, unite, nom_ing = parts[0], parts[1], " ".join(parts[2:])
            try:
                quantite = float(quantite_str.replace(",", "."))
            except (ValueError, TypeError):
                return 1.0, "", ing_text
        elif len(parts) >= 2:
            quantite_str, nom_ing = parts[0], parts[1]
            try:
                quantite = float(quantite_str.replace(",", "."))
            except (ValueError, TypeError):
                return 1.0, "", ing_text
            unite = "g"
        else:
            return 1.0, "", ing_text
        return quantite, unite, nom_ing


class RecetteIOMixin(RecetteIOExportMixin, RecetteIOImportMixin):
    """
    Mixin combiné pour Import/Export.

    Combine RecetteIOExportMixin et RecetteIOImportMixin.
    """

    pass


__all__ = ["RecetteIOMixin", "RecetteIOExportMixin", "RecetteIOImportMixin"]
