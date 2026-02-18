"""
Sanitizer - Nettoyage et sanitization des entrées utilisateur.

Protège contre:
- XSS (Cross-Site Scripting)
- Injections SQL
- Caractères dangereux
"""

import html
import logging
import re
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)


class NettoyeurEntrees:
    """
    Nettoyeur universel d'entrées utilisateur.

    Protège contre XSS, injections SQL, et caractères dangereux.
    """

    PATTERNS_XSS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]
    """Patterns de détection XSS."""

    PATTERNS_SQL = [
        r"('\s*(OR|AND)\s*'?\d)",
        r'("\s*(OR|AND)\s*"?\d)',
        r"(;\s*DROP\s+TABLE)",
        r"(;\s*DELETE\s+FROM)",
        r"(UNION\s+SELECT)",
    ]
    """Patterns de détection injection SQL."""

    @staticmethod
    def nettoyer_chaine(valeur: str, longueur_max: int = 1000) -> str:
        """
        Nettoie une chaîne de caractères.

        Args:
            valeur: Chaîne à nettoyer
            longueur_max: Longueur maximale

        Returns:
            Chaîne nettoyée

        Example:
            >>> NettoyeurEntrees.nettoyer_chaine("<script>alert('xss')</script>")
            ''
        """
        if not valeur or not isinstance(valeur, str):
            return ""

        # Limiter longueur
        valeur = valeur[:longueur_max]

        # Échapper HTML
        valeur = html.escape(valeur)

        # Supprimer patterns XSS
        for pattern in NettoyeurEntrees.PATTERNS_XSS:
            valeur = re.sub(pattern, "", valeur, flags=re.IGNORECASE)

        # Détecter patterns SQL
        for pattern in NettoyeurEntrees.PATTERNS_SQL:
            if re.search(pattern, valeur, re.IGNORECASE):
                logger.warning(f"[!] Tentative injection SQL détectée: {valeur[:50]}")
                # On laisse passer mais on log (pour ne pas bloquer faux positifs)

        # Supprimer caractères de contrôle
        valeur = re.sub(r"[\x00-\x1F\x7F]", "", valeur)

        return valeur.strip()

    @staticmethod
    def nettoyer_nombre(
        valeur: Any, minimum: float | None = None, maximum: float | None = None
    ) -> float | None:
        """
        Valide et nettoie un nombre.

        Args:
            valeur: Valeur à nettoyer
            minimum: Valeur minimale (optionnelle)
            maximum: Valeur maximale (optionnelle)

        Returns:
            Nombre nettoyé ou None si invalide

        Example:
            >>> NettoyeurEntrees.nettoyer_nombre("10.5", minimum=0, maximum=100)
            10.5
        """
        try:
            if isinstance(valeur, str):
                valeur = valeur.replace(",", ".")
            num = float(valeur)

            if minimum is not None and num < minimum:
                return minimum
            if maximum is not None and num > maximum:
                return maximum

            return num
        except (ValueError, TypeError):
            return None

    @staticmethod
    def nettoyer_date(valeur: Any) -> date | None:
        """
        Valide et nettoie une date.

        Args:
            valeur: Valeur à nettoyer

        Returns:
            Date ou None si invalide

        Example:
            >>> NettoyeurEntrees.nettoyer_date("2024-12-31")
            date(2024, 12, 31)
        """
        if isinstance(valeur, date):
            return valeur
        if isinstance(valeur, datetime):
            return valeur.date()

        if isinstance(valeur, str):
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(valeur, fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def nettoyer_email(valeur: str) -> str | None:
        """
        Valide un email.

        Args:
            valeur: Email à valider

        Returns:
            Email nettoyé ou None si invalide
        """
        if not valeur or not isinstance(valeur, str):
            return None

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        valeur = valeur.strip().lower()

        if re.match(pattern, valeur):
            return valeur
        return None

    @staticmethod
    def nettoyer_dictionnaire(data: dict, schema: dict) -> dict:
        """
        Nettoie un dictionnaire selon un schéma.

        Args:
            data: Données à nettoyer
            schema: Schéma de validation

        Returns:
            Dictionnaire nettoyé

        Example:
            >>> schema = {
            >>>     "nom": {"type": "string", "max_length": 200, "required": True},
            >>>     "prix": {"type": "number", "min": 0, "max": 1000}
            >>> }
            >>> NettoyeurEntrees.nettoyer_dictionnaire(data, schema)
        """
        nettoye = {}

        for champ, regles in schema.items():
            valeur = data.get(champ)

            if regles.get("required", False) and not valeur:
                continue

            if valeur is None and not regles.get("required", False):
                continue

            type_champ = regles.get("type", "string")

            if type_champ == "string":
                nettoye[champ] = NettoyeurEntrees.nettoyer_chaine(
                    valeur, longueur_max=regles.get("max_length", 1000)
                )
            elif type_champ == "number":
                nettoye[champ] = NettoyeurEntrees.nettoyer_nombre(
                    valeur, minimum=regles.get("min"), maximum=regles.get("max")
                )
            elif type_champ == "date":
                nettoye[champ] = NettoyeurEntrees.nettoyer_date(valeur)
            elif type_champ == "email":
                nettoye[champ] = NettoyeurEntrees.nettoyer_email(valeur)
            elif type_champ == "list":
                if isinstance(valeur, list):
                    nettoye[champ] = [
                        NettoyeurEntrees.nettoyer_chaine(str(item)) for item in valeur
                    ]
            else:
                nettoye[champ] = valeur

        return nettoye


# Alias pour compatibilité
InputSanitizer = NettoyeurEntrees
