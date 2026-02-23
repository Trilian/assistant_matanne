"""
Module d'import de recettes depuis fichiers PDF et texte brut.

Méthodes disponibles:
- from_pdf(): Extraction de recettes depuis des fichiers PDF
- from_text(): Extraction de recettes depuis du texte brut

⚠️ MIGRATION TERMINÉE pour les URLs:
    - L'import URL est désormais géré par import_url.py (RecipeImportService)
      qui offre: AI fallback, modèles Pydantic, parsers modulaires, scoring
    - from_url() et _extract_from_html() ont été supprimés de ce fichier
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class RecipeImporter:
    """Classe pour importer des recettes depuis fichiers PDF et texte brut.

    Pour l'import depuis URL, utiliser RecipeImportService (import_url.py).
    """

    @staticmethod
    def from_pdf(file_path: str) -> dict[str, Any] | None:
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
                "nom": "Recette importée du PDF",
                "ingredients": [],
                "etapes": [],
                "description": "Recette extraite d'un PDF",
            }

            with open(file_path, "rb") as file:
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
                logger.warning("⚠️ Impossible d'extraire la recette du PDF")
                return None

        except Exception as e:
            logger.error(f"Erreur import PDF: {e}")
            return None

    @staticmethod
    def from_text(text: str) -> dict[str, Any] | None:
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
    def _extract_from_text(text: str) -> dict[str, Any] | None:
        """
        Extrait les infos de recette depuis du texte brut
        """
        recipe = {
            "nom": "",
            "description": "",
            "ingredients": [],
            "etapes": [],
            "temps_preparation": 0,
            "temps_cuisson": 0,
            "portions": 4,
        }

        lines = text.split("\n")

        # Premier ligne = nom
        if lines:
            recipe["nom"] = lines[0].strip()

        # Chercher sections
        current_section = None
        for line in lines[1:]:
            line = line.strip()

            if not line:
                continue

            # Détecter les sections
            if "ingrédient" in line.lower() or "ingredients" in line.lower():
                current_section = "ingredients"
                continue
            elif (
                "étape" in line.lower()
                or "instruction" in line.lower()
                or "préparation" in line.lower()
            ):
                current_section = "etapes"
                continue
            elif "temps" in line.lower():
                # Parser les temps
                if "prep" in line.lower():
                    match = re.search(r"(\d+)", line)
                    if match:
                        recipe["temps_preparation"] = int(match.group(1))
                elif "cuisson" in line.lower() or "cook" in line.lower():
                    match = re.search(r"(\d+)", line)
                    if match:
                        recipe["temps_cuisson"] = int(match.group(1))
                continue
            elif "portion" in line.lower():
                match = re.search(r"(\d+)", line)
                if match:
                    recipe["portions"] = int(match.group(1))
                continue

            # Ajouter au contenu actuel
            if current_section == "ingredients" and line and not line.startswith("#"):
                recipe["ingredients"].append(line.lstrip("- •*").strip())
            elif current_section == "etapes" and line and not line.startswith("#"):
                recipe["etapes"].append(line.lstrip("- •*").strip())
            elif not current_section and not recipe["description"]:
                recipe["description"] = line

        return recipe if recipe["nom"] else None
