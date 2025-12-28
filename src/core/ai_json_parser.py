"""
Parser JSON IA Ultra-Robuste
Gère TOUS les cas edge des réponses Mistral/GPT

"""
import json
import re
from typing import Dict, List, Optional, Type, TypeVar, Any
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AIJsonParser:
    """
    Parser JSON universel pour réponses IA

    Stratégies (dans l'ordre) :
    1. Parse direct (JSON propre)
    2. Extraction JSON brut (regex)
    3. Réparation intelligente (fixes courants)
    4. Validation individuelle (parse partiel)
    5. Fallback (valeur par défaut)
    """

    # ═══════════════════════════════════════════════════════════════
    # PARSE PRINCIPAL
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def parse(
            response: str,
            model: Type[T],
            fallback: Optional[Dict] = None,
            strict: bool = False
    ) -> T:
        """
        Parse réponse IA en modèle Pydantic

        Args:
            response: Réponse brute de l'IA
            model: Modèle Pydantic cible
            fallback: Dict de fallback si tout échoue
            strict: Si True, raise si parsing échoue (pas de fallback)

        Returns:
            Instance validée du modèle

        Raises:
            ValidationError si parsing échoue ET (strict=True OU pas de fallback)

        Usage:
            response = await mistral.call(...)

            result = AIJsonParser.parse(
                response,
                RecettesResponse,
                fallback={"recettes": []}
            )
        """

        # ───────────────────────────────────────────────────────────
        # STRATÉGIE 1 : Parse direct (JSON propre)
        # ───────────────────────────────────────────────────────────
        try:
            cleaned = AIJsonParser._clean_basic(response)
            return model.parse_raw(cleaned)

        except (ValidationError, json.JSONDecodeError) as e:
            logger.debug(f"Stratégie 1 échouée: {type(e).__name__}")

        # ───────────────────────────────────────────────────────────
        # STRATÉGIE 2 : Extraction JSON brut
        # ───────────────────────────────────────────────────────────
        try:
            json_str = AIJsonParser._extract_json_object(response)
            return model.parse_raw(json_str)

        except (ValidationError, json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Stratégie 2 échouée: {type(e).__name__}")

        # ───────────────────────────────────────────────────────────
        # STRATÉGIE 3 : Réparation intelligente
        # ───────────────────────────────────────────────────────────
        try:
            repaired = AIJsonParser._smart_repair(response)
            data = json.loads(repaired)
            return model(**data)

        except (ValidationError, json.JSONDecodeError, TypeError) as e:
            logger.debug(f"Stratégie 3 échouée: {type(e).__name__}")

        # ───────────────────────────────────────────────────────────
        # STRATÉGIE 4 : Validation individuelle (partiel OK)
        # ───────────────────────────────────────────────────────────
        try:
            partial_data = AIJsonParser._parse_partial(response, model)
            if partial_data:
                return model(**partial_data)

        except Exception as e:
            logger.debug(f"Stratégie 4 échouée: {type(e).__name__}")

        # ───────────────────────────────────────────────────────────
        # STRATÉGIE 5 : Fallback
        # ───────────────────────────────────────────────────────────
        if not strict and fallback:
            logger.warning("Toutes stratégies échouées, utilisation fallback")
            return model(**fallback)

        # ───────────────────────────────────────────────────────────
        # ÉCHEC TOTAL
        # ───────────────────────────────────────────────────────────
        error_msg = f"Impossible de parser la réponse IA"
        logger.error(f"{error_msg}. Contenu: {response[:500]}")
        raise ValidationError(error_msg)

    # ═══════════════════════════════════════════════════════════════
    # NETTOYAGE DE BASE
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _clean_basic(text: str) -> str:
        """
        Nettoyage basique du JSON

        - Supprime BOM et caractères invisibles
        - Supprime markdown (```json)
        - Trim whitespace
        """
        # BOM et caractères invisibles
        text = text.replace("\ufeff", "")
        text = re.sub(r"[\x00-\x1F\x7F]", "", text)

        # Markdown
        text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```\s*", "", text)

        return text.strip()

    # ═══════════════════════════════════════════════════════════════
    # EXTRACTION JSON
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _extract_json_object(text: str) -> str:
        """
        Extrait le premier objet JSON complet {...}

        Utilise un compteur de brackets pour trouver
        le JSON même s'il y a du texte avant/après
        """
        text = AIJsonParser._clean_basic(text)

        stack = []
        start = None

        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start = i
                stack.append(char)

            elif char == '}':
                if stack:
                    stack.pop()

                if not stack and start is not None:
                    # JSON complet trouvé
                    return text[start:i+1]

        raise ValueError("Aucun objet JSON complet trouvé")

    @staticmethod
    def _extract_json_array(text: str) -> str:
        """Extrait le premier array JSON complet [...]"""
        text = AIJsonParser._clean_basic(text)

        stack = []
        start = None

        for i, char in enumerate(text):
            if char == '[':
                if not stack:
                    start = i
                stack.append(char)

            elif char == ']':
                if stack:
                    stack.pop()

                if not stack and start is not None:
                    return text[start:i+1]

        raise ValueError("Aucun array JSON complet trouvé")

    # ═══════════════════════════════════════════════════════════════
    # RÉPARATION INTELLIGENTE
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _smart_repair(text: str) -> str:
        """
        Répare les erreurs JSON courantes

        Fixes:
        - Apostrophes non échappées
        - Virgules trailing
        - Guillemets manquants sur clés
        - True/False au lieu de true/false
        - None au lieu de null
        - Apostrophes simples au lieu de doubles
        """
        text = AIJsonParser._clean_basic(text)

        # 1. Échapper apostrophes dans strings
        # "l'été" -> "l\'été"
        text = re.sub(
            r'(["\'])([^"\']*?)\'([^"\']*?)\1',
            r'\1\2\\\'\3\1',
            text
        )

        # 2. Supprimer virgules trailing
        text = re.sub(r",\s*([}\]])", r"\1", text)

        # 3. Guillemets sur clés
        # {nom: "value"} -> {"nom": "value"}
        text = re.sub(
            r'([{\s,])(\w+)(\s*:)',
            r'\1"\2"\3',
            text
        )

        # 4. Python booleans -> JSON
        text = re.sub(r'\bTrue\b', 'true', text)
        text = re.sub(r'\bFalse\b', 'false', text)
        text = re.sub(r'\bNone\b', 'null', text)

        # 5. Apostrophes simples -> doubles
        # Seulement pour les strings, pas dans le contenu
        text = re.sub(r"'([^']*)'(\s*[:, \]}])", r'"\1"\2', text)

        return text

    # ═══════════════════════════════════════════════════════════════
    # PARSING PARTIEL
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _parse_partial(text: str, model: Type[BaseModel]) -> Optional[Dict]:
        """
        Tente de parser partiellement

        Si le JSON est cassé mais contient des données valides,
        essaie d'extraire ce qui est utilisable
        """
        try:
            # Essayer d'extraire les clés principales du modèle
            model_fields = model.__fields__.keys()

            result = {}

            for field in model_fields:
                # Chercher "field": valeur
                pattern = rf'"{field}"\s*:\s*(.+?)(?:,|\}})'
                match = re.search(pattern, text, re.DOTALL)

                if match:
                    try:
                        value_str = match.group(1).strip()

                        # Tenter de parser la valeur
                        if value_str.startswith('"'):
                            # String
                            result[field] = json.loads(value_str)
                        elif value_str.startswith('['):
                            # Array
                            result[field] = json.loads(value_str)
                        elif value_str.startswith('{'):
                            # Object
                            result[field] = json.loads(value_str)
                        else:
                            # Number/boolean/null
                            result[field] = json.loads(value_str)

                    except:
                        pass

            if result:
                logger.info(f"Parsing partiel réussi: {len(result)} champs extraits")
                return result

        except Exception as e:
            logger.debug(f"Parsing partiel échoué: {e}")

        return None

    # ═══════════════════════════════════════════════════════════════
    # HELPERS POUR CORRECTIONS SPÉCIFIQUES
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def fix_common_model_errors(data: Dict, model: Type[BaseModel]) -> Dict:
        """
        Corrige les erreurs courantes pour un modèle spécifique

        Usage:
            data = AIJsonParser._parse_partial(response)
            data = AIJsonParser.fix_common_model_errors(data, RecetteAI)
        """
        # Liste des corrections par type de champ
        fixes = {
            "int": lambda v: int(float(v)) if v else 0,
            "float": lambda v: float(v) if v else 0.0,
            "str": lambda v: str(v).strip() if v else "",
            "bool": lambda v: bool(v) if isinstance(v, bool) else str(v).lower() in ['true', '1', 'yes'],
            "list": lambda v: v if isinstance(v, list) else [],
            "dict": lambda v: v if isinstance(v, dict) else {},
        }

        for field_name, field in model.__fields__.items():
            if field_name not in data:
                continue

            value = data[field_name]
            field_type = str(field.outer_type_)

            # Appliquer fix si disponible
            for type_name, fix_func in fixes.items():
                if type_name in field_type.lower():
                    try:
                        data[field_name] = fix_func(value)
                    except:
                        pass
                    break

        return data


# ═══════════════════════════════════════════════════════════════
# HELPERS SPÉCIFIQUES
# ═══════════════════════════════════════════════════════════════

def parse_list_response(
        response: str,
        item_model: Type[BaseModel],
        list_key: str = "items",
        fallback_items: Optional[List[Dict]] = None
) -> List[BaseModel]:
    """
    Parse une réponse contenant une liste

    Args:
        response: Réponse IA
        item_model: Modèle d'un item de la liste
        list_key: Clé contenant la liste
        fallback_items: Liste de fallback

    Returns:
        Liste d'items validés

    Usage:
        recettes = parse_list_response(
            response,
            RecetteAI,
            list_key="recettes",
            fallback_items=[{"nom": "Fallback", ...}]
        )
    """

    # Wrapper pour avoir une structure avec clé
    class ListWrapper(BaseModel):
        items: List[item_model]

    # Parser avec le wrapper
    wrapper_data = AIJsonParser.parse(
        response,
        ListWrapper,
        fallback={list_key: fallback_items or []},
        strict=False
    )

    return wrapper_data.items