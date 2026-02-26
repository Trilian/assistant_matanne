"""
Service import en masse — Import CSV avec validation Pydantic.

Fournit des templates CSV et l'import validé pour chaque domaine.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from dataclasses import dataclass, field
from typing import Any

from src.core.db import obtenir_contexte_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TEMPLATES CSV PAR DOMAINE
# ═══════════════════════════════════════════════════════════

TEMPLATES_CSV: dict[str, dict[str, Any]] = {
    "recettes": {
        "label": "🍽️ Recettes",
        "colonnes": [
            "nom",
            "description",
            "temps_preparation",
            "temps_cuisson",
            "portions",
            "difficulte",
            "categorie",
            "saison",
            "ingredients_json",
            "etapes_json",
        ],
        "exemple": {
            "nom": "Tarte aux pommes",
            "description": "Recette classique",
            "temps_preparation": "30",
            "temps_cuisson": "45",
            "portions": "6",
            "difficulte": "facile",
            "categorie": "dessert",
            "saison": "automne",
            "ingredients_json": '[{"nom": "pommes", "quantite": 4, "unite": "pièces"}]',
            "etapes_json": '[{"ordre": 1, "description": "Éplucher les pommes"}]',
        },
    },
    "depenses": {
        "label": "💰 Dépenses",
        "colonnes": ["montant", "categorie", "description", "date", "recurrence", "tags"],
        "exemple": {
            "montant": "45.90",
            "categorie": "alimentation",
            "description": "Courses Leclerc",
            "date": "2026-02-20",
            "recurrence": "ponctuel",
            "tags": '["courses", "février"]',
        },
    },
    "inventaire": {
        "label": "🥫 Inventaire",
        "colonnes": [
            "nom",
            "categorie",
            "quantite",
            "unite",
            "lieu_stockage",
            "date_peremption",
            "seuil_alerte",
        ],
        "exemple": {
            "nom": "Riz basmati",
            "categorie": "féculents",
            "quantite": "2",
            "unite": "kg",
            "lieu_stockage": "placard cuisine",
            "date_peremption": "2027-06-15",
            "seuil_alerte": "1",
        },
    },
    "contacts": {
        "label": "📇 Contacts",
        "colonnes": ["nom", "categorie", "telephone", "email", "adresse", "horaires", "notes"],
        "exemple": {
            "nom": "Dr Martin",
            "categorie": "sante",
            "telephone": "01 23 45 67 89",
            "email": "dr.martin@mail.com",
            "adresse": "12 rue de la Paix, Paris",
            "horaires": "9h-18h lun-ven",
            "notes": "Pédiatre de Jules",
        },
    },
    "notes": {
        "label": "📝 Notes",
        "colonnes": ["titre", "contenu", "categorie", "tags"],
        "exemple": {
            "titre": "Liste courses urgentes",
            "contenu": "Acheter du lait et des couches",
            "categorie": "courses",
            "tags": '["urgent"]',
        },
    },
}


@dataclass
class ResultatImport:
    """Résultat d'un import en masse."""

    domaine: str
    total_lignes: int = 0
    lignes_importees: int = 0
    lignes_erreur: int = 0
    erreurs: list[dict[str, Any]] = field(default_factory=list)

    @property
    def succes(self) -> bool:
        return self.lignes_erreur == 0

    @property
    def taux_succes(self) -> float:
        if self.total_lignes == 0:
            return 0.0
        return (self.lignes_importees / self.total_lignes) * 100


class ImportService:
    """Service d'import en masse avec validation."""

    def generer_template_csv(self, domaine: str) -> str:
        """Génère un template CSV téléchargeable pour un domaine."""
        if domaine not in TEMPLATES_CSV:
            raise ValueError(f"Domaine inconnu: {domaine}")

        config = TEMPLATES_CSV[domaine]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=config["colonnes"])
        writer.writeheader()
        # Ligne d'exemple
        writer.writerow(config["exemple"])
        return output.getvalue()

    def parser_csv(self, contenu_csv: str, domaine: str) -> tuple[list[dict], list[dict]]:
        """Parse un CSV et retourne (données_valides, erreurs)."""
        if domaine not in TEMPLATES_CSV:
            raise ValueError(f"Domaine inconnu: {domaine}")

        config = TEMPLATES_CSV[domaine]
        colonnes_attendues = set(config["colonnes"])

        reader = csv.DictReader(io.StringIO(contenu_csv))
        colonnes_fichier = set(reader.fieldnames or [])

        manquantes = colonnes_attendues - colonnes_fichier
        if manquantes:
            return [], [{"ligne": 0, "erreur": f"Colonnes manquantes: {manquantes}"}]

        valides = []
        erreurs = []

        for i, row in enumerate(reader, start=2):
            try:
                # Nettoyage basique
                cleaned = {
                    k: v.strip() if v else "" for k, v in row.items() if k in colonnes_attendues
                }
                # Parser les champs JSON
                for key in cleaned:
                    if key.endswith("_json") or key == "tags":
                        if cleaned[key]:
                            try:
                                cleaned[key] = json.loads(cleaned[key])
                            except json.JSONDecodeError:
                                erreurs.append({"ligne": i, "erreur": f"JSON invalide: {key}"})
                                continue
                valides.append(cleaned)
            except Exception as e:
                erreurs.append({"ligne": i, "erreur": str(e)})

        return valides, erreurs

    def importer_donnees(
        self, domaine: str, contenu_csv: str, dry_run: bool = False
    ) -> ResultatImport:
        """Importe les données CSV dans la base."""
        resultat = ResultatImport(domaine=domaine)
        valides, erreurs = self.parser_csv(contenu_csv, domaine)
        resultat.total_lignes = len(valides) + len(erreurs)
        resultat.erreurs = erreurs
        resultat.lignes_erreur = len(erreurs)

        if dry_run or not valides:
            resultat.lignes_importees = len(valides) if dry_run else 0
            return resultat

        # Import effectif selon le domaine
        try:
            if domaine == "depenses":
                resultat.lignes_importees = self._importer_depenses(valides)
            elif domaine == "contacts":
                resultat.lignes_importees = self._importer_contacts(valides)
            elif domaine == "notes":
                resultat.lignes_importees = self._importer_notes(valides)
            elif domaine == "inventaire":
                resultat.lignes_importees = self._importer_inventaire(valides)
            elif domaine == "recettes":
                resultat.lignes_importees = self._importer_recettes(valides)
            else:
                resultat.erreurs.append({"ligne": 0, "erreur": f"Import non supporté: {domaine}"})
        except Exception as e:
            resultat.erreurs.append({"ligne": 0, "erreur": f"Erreur import: {e}"})
            logger.error(f"Erreur import {domaine}: {e}")

        return resultat

    def _importer_depenses(self, rows: list[dict]) -> int:
        """Importe des dépenses."""
        from src.core.models.finances import Depense

        count = 0
        with obtenir_contexte_db() as db:
            for row in rows:
                try:
                    dep = Depense(
                        montant=float(row["montant"]),
                        categorie=row.get("categorie", "autre"),
                        description=row.get("description"),
                        date=row.get("date"),
                        recurrence=row.get("recurrence"),
                        tags=row.get("tags", []),
                    )
                    db.add(dep)
                    count += 1
                except Exception:
                    continue
            db.commit()
        return count

    def _importer_contacts(self, rows: list[dict]) -> int:
        """Importe des contacts."""
        from src.core.models.utilitaires import ContactUtile

        count = 0
        with obtenir_contexte_db() as db:
            for row in rows:
                try:
                    contact = ContactUtile(**{k: v for k, v in row.items() if v})
                    db.add(contact)
                    count += 1
                except Exception:
                    continue
            db.commit()
        return count

    def _importer_notes(self, rows: list[dict]) -> int:
        """Importe des notes."""
        from src.core.models.utilitaires import NoteMemo

        count = 0
        with obtenir_contexte_db() as db:
            for row in rows:
                try:
                    note = NoteMemo(**{k: v for k, v in row.items() if v})
                    db.add(note)
                    count += 1
                except Exception:
                    continue
            db.commit()
        return count

    def _importer_inventaire(self, rows: list[dict]) -> int:
        """Importe des articles d'inventaire."""
        from src.core.models.inventaire import ArticleInventaire

        count = 0
        with obtenir_contexte_db() as db:
            for row in rows:
                try:
                    article = ArticleInventaire(
                        nom=row["nom"],
                        categorie=row.get("categorie", "divers"),
                        quantite=float(row.get("quantite", 1)),
                        unite=row.get("unite", "pièce"),
                    )
                    db.add(article)
                    count += 1
                except Exception:
                    continue
            db.commit()
        return count

    def _importer_recettes(self, rows: list[dict]) -> int:
        """Importe des recettes."""
        from src.core.models.recettes import Recette

        count = 0
        with obtenir_contexte_db() as db:
            for row in rows:
                try:
                    recette = Recette(
                        nom=row["nom"],
                        description=row.get("description"),
                        temps_preparation=int(row.get("temps_preparation", 0)) or None,
                        temps_cuisson=int(row.get("temps_cuisson", 0)) or None,
                        portions=int(row.get("portions", 4)),
                    )
                    db.add(recette)
                    count += 1
                except Exception:
                    continue
            db.commit()
        return count


@service_factory("import_service", tags={"utilitaires", "donnees"})
def get_import_service() -> ImportService:
    """Factory singleton ImportService."""
    return ImportService()
