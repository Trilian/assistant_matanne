"""
Service export global — Hub centralisé d'export multi-format.

Exporte les données de tous les domaines en JSON, CSV, ou Excel.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import zipfile
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from src.core.db import obtenir_contexte_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Domaines exportables et leurs modèles
DOMAINES_EXPORT = {
    "recettes": {
        "label": "🍽️ Recettes",
        "model_path": "src.core.models.recettes",
        "model_name": "Recette",
    },
    "ingredients": {
        "label": "🥕 Ingrédients",
        "model_path": "src.core.models.recettes",
        "model_name": "Ingredient",
    },
    "courses": {
        "label": "🛒 Listes de courses",
        "model_path": "src.core.models.courses",
        "model_name": "ListeCourses",
    },
    "articles_courses": {
        "label": "📝 Articles courses",
        "model_path": "src.core.models.courses",
        "model_name": "ArticleCourses",
    },
    "inventaire": {
        "label": "🥫 Inventaire",
        "model_path": "src.core.models.inventaire",
        "model_name": "ArticleInventaire",
    },
    "depenses": {
        "label": "💰 Dépenses",
        "model_path": "src.core.models.finances",
        "model_name": "Depense",
    },
    "planning": {
        "label": "📅 Planning",
        "model_path": "src.core.models.planning",
        "model_name": "Planning",
    },
    "notes": {
        "label": "📝 Notes",
        "model_path": "src.core.models.utilitaires",
        "model_name": "NoteMemo",
    },
    "journal": {
        "label": "📓 Journal de bord",
        "model_path": "src.core.models.utilitaires",
        "model_name": "EntreeJournal",
    },
    "contacts": {
        "label": "📇 Contacts",
        "model_path": "src.core.models.utilitaires",
        "model_name": "ContactUtile",
    },
}


def _serialiser_valeur(val: Any) -> Any:
    """Sérialise une valeur pour JSON/CSV."""
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, list | dict):
        return val
    return val


class ExportService:
    """Service d'export global multi-format."""

    def _charger_modele(self, domaine: str):
        """Charge dynamiquement un modèle SQLAlchemy."""
        import importlib

        config = DOMAINES_EXPORT[domaine]
        module = importlib.import_module(config["model_path"])
        return getattr(module, config["model_name"])

    def _modele_vers_dicts(self, domaine: str) -> list[dict]:
        """Charge les données d'un domaine sous forme de dicts."""
        model_class = self._charger_modele(domaine)
        with obtenir_contexte_db() as db:
            rows = db.query(model_class).all()
            result = []
            for row in rows:
                d = {}
                for col in row.__table__.columns:
                    d[col.name] = _serialiser_valeur(getattr(row, col.name))
                result.append(d)
            return result

    def exporter_json(self, domaines: list[str]) -> str:
        """Exporte les domaines sélectionnés en JSON."""
        data = {}
        for domaine in domaines:
            try:
                data[domaine] = self._modele_vers_dicts(domaine)
            except Exception as e:
                logger.error(f"Erreur export JSON '{domaine}': {e}")
                data[domaine] = {"erreur": str(e)}

        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

    def exporter_csv(self, domaine: str) -> str:
        """Exporte un domaine en CSV."""
        rows = self._modele_vers_dicts(domaine)
        if not rows:
            return ""

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            # Convertir listes/dicts en strings pour CSV
            csv_row = {}
            for k, v in row.items():
                csv_row[k] = json.dumps(v, ensure_ascii=False) if isinstance(v, list | dict) else v
            writer.writerow(csv_row)

        return output.getvalue()

    def exporter_excel(self, domaines: list[str]) -> bytes:
        """Exporte les domaines en Excel (une feuille par domaine)."""
        import pandas as pd

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for domaine in domaines:
                try:
                    rows = self._modele_vers_dicts(domaine)
                    if rows:
                        df = pd.DataFrame(rows)
                        # Nom de feuille limité à 31 chars
                        sheet_name = DOMAINES_EXPORT[domaine]["label"][:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                except Exception as e:
                    logger.error(f"Erreur export Excel '{domaine}': {e}")

        return output.getvalue()

    def exporter_zip(self, domaines: list[str], format_csv: bool = True) -> bytes:
        """Exporte chaque domaine en fichier séparé dans un ZIP."""
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for domaine in domaines:
                try:
                    if format_csv:
                        contenu = self.exporter_csv(domaine)
                        zf.writestr(f"{domaine}.csv", contenu)
                    else:
                        rows = self._modele_vers_dicts(domaine)
                        contenu = json.dumps(rows, ensure_ascii=False, indent=2, default=str)
                        zf.writestr(f"{domaine}.json", contenu)
                except Exception as e:
                    logger.error(f"Erreur export ZIP '{domaine}': {e}")

        return output.getvalue()

    def apercu(self, domaine: str, limite: int = 5) -> list[dict]:
        """Aperçu des premières lignes d'un domaine."""
        rows = self._modele_vers_dicts(domaine)
        return rows[:limite]

    def compter(self, domaine: str) -> int:
        """Compte les enregistrements d'un domaine."""
        model_class = self._charger_modele(domaine)
        with obtenir_contexte_db() as db:
            return db.query(model_class).count()

    # ────────────────────────────────────────────────────────
    # Chiffrement (Fernet + PBKDF2)
    # ────────────────────────────────────────────────────────

    def exporter_json_chiffre(self, domaines: list[str], mot_de_passe: str) -> bytes:
        """
        Exporte les domaines en JSON puis chiffre le résultat.

        Format binaire : SALT (16 octets) | TOKEN FERNET (variable)
        Le sel aléatoire garantit qu'un même mot de passe génère un fichier
        différent à chaque export.
        """
        import base64
        import os

        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        json_bytes = self.exporter_json(domaines).encode("utf-8")

        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode("utf-8")))
        token = Fernet(key).encrypt(json_bytes)

        return salt + token

    @staticmethod
    def dechiffrer_json(donnees: bytes, mot_de_passe: str) -> str:
        """
        Déchiffre un fichier produit par ``exporter_json_chiffre``.

        Raises:
            ValueError: Mot de passe incorrect ou fichier corrompu.
        """
        import base64

        from cryptography.fernet import Fernet, InvalidToken
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

        if len(donnees) <= 16:  # noqa: PLR2004
            raise ValueError("Fichier invalide ou trop court")

        salt = donnees[:16]
        token = donnees[16:]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(mot_de_passe.encode("utf-8")))

        try:
            plaintext = Fernet(key).decrypt(token)
        except InvalidToken as exc:
            raise ValueError("Mot de passe incorrect ou fichier corrompu") from exc

        return plaintext.decode("utf-8")


@service_factory("export_service", tags={"utilitaires", "donnees"})
def obtenir_export_service() -> ExportService:
    """Factory singleton ExportService."""
    return ExportService()
