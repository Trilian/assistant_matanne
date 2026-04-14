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
            modifie_le=datetime.utcnow(),
        )
        db.add(recette)
        db.flush()

        # Parser et ajouter les ingrédients (idempotent : sommer si même ingrédient déjà présent)
        for ing_text in ingredients_textes:
            quantite, unite, nom_ing = self._parser_ingredient_texte(ing_text)
            if not nom_ing:
                continue

            ingredient = self._find_or_create_ingredient(db, nom_ing)
            existant = (
                db.query(RecetteIngredient)
                .filter_by(recette_id=recette.id, ingredient_id=ingredient.id)
                .first()
            )
            if existant:
                existant.quantite += quantite
            else:
                db.add(RecetteIngredient(
                    recette_id=recette.id,
                    ingredient_id=ingredient.id,
                    quantite=quantite,
                    unite=unite or "pièce",
                ))

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

        Exemples:
            "200 g farine"                 → (200.0, "g", "Farine")
            "1 sachet (11g) levure chimique" → (1.0, "sachet", "Levure chimique")
            "2 oignons"                    → (2.0, "", "Oignons")
            "sel"                          → (1.0, "", "Sel")
        """
        import re

        text = ing_text.strip()
        if not text:
            return 1.0, "", ""

        parts = text.split(maxsplit=2)
        if len(parts) >= 3:
            quantite_str, unite_brute, nom_ing = parts[0], parts[1], " ".join(parts[2:])
            try:
                quantite = float(quantite_str.replace(",", "."))
            except (ValueError, TypeError):
                return 1.0, "", text.strip().title()
            # Retirer les spécificatifs entre parenthèses de l'unité et du nom
            # Ex: "sachet (11g)" → unite="sachet", et "(11g) levure" → "levure"
            unite = re.sub(r"\s*\([^)]*\)", "", unite_brute).strip()
            nom_ing = re.sub(r"^\s*\([^)]*\)\s*", "", nom_ing).strip()
        elif len(parts) >= 2:
            quantite_str, nom_ing = parts[0], parts[1]
            try:
                quantite = float(quantite_str.replace(",", "."))
            except (ValueError, TypeError):
                return 1.0, "", text.strip().title()
            unite = ""
        else:
            return 1.0, "", text.strip().title()

        nom_ing = nom_ing.strip().title()
        return quantite, unite, nom_ing


class RecetteIOMixin(RecetteIOExportMixin, RecetteIOImportMixin):
    """
    Mixin combiné pour Import/Export.

    Combine RecetteIOExportMixin et RecetteIOImportMixin.
    """

    pass


__all__ = ["RecetteIOMixin", "RecetteIOExportMixin", "RecetteIOImportMixin"]
