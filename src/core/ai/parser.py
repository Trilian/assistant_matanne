"""
Parser JSON IA Ultra-Robuste
Gère tous les cas edge des réponses Mistral/GPT
"""
import json
import re
from typing import Dict, List, Optional, Type, TypeVar, Any
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AIParser:
    """
    Parser JSON universel pour réponses IA

    Stratégies (dans l'ordre):
    1. Parse direct (JSON propre)
    2. Extraction JSON brut (regex)
    3. Réparation intelligente
    4. Parse partiel
    5. Fallback
    """

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
            response: Réponse brute IA
            model: Modèle Pydantic cible
            fallback: Dict fallback si échec
            strict: Si True, raise si échec (pas de fallback)

        Returns:
            Instance validée du modèle

        Raises:
            ValidationError si échec ET (strict=True OU pas de fallback)
        """
        # Stratégie 1: Parse direct
        try:
            cleaned = AIParser._clean_basic(response)
            return model.parse_raw(cleaned)
        except (ValidationError, json.JSONDecodeError):
            pass

        # Stratégie 2: Extraction JSON
        try:
            json_str = AIParser._extract_json_object(response)
            return model.parse_raw(json_str)
        except (ValidationError, json.JSONDecodeError, ValueError):
            pass

        # Stratégie 3: Réparation
        try:
            repaired = AIParser._smart_repair(response)
            data = json.loads(repaired)
            return model(**data)
        except (ValidationError, json.JSONDecodeError, TypeError):
            pass

        # Stratégie 4: Parse partiel
        try:
            partial_data = AIParser._parse_partial(response, model)
            if partial_data:
                return model(**partial_data)
        except Exception:
            pass

        # Stratégie 5: Fallback
        if not strict and fallback:
            logger.warning("Toutes stratégies échouées, utilisation fallback")
            return model(**fallback)

        # Échec total
        logger.error(f"Impossible de parser: {response[:500]}")
        raise ValidationError("Impossible de parser la réponse IA")

    @staticmethod
    def _clean_basic(text: str) -> str:
        """Nettoyage basique"""
        # BOM et caractères invisibles
        text = text.replace("\ufeff", "")
        text = re.sub(r"[\x00-\x1F\x7F]", "", text)

        # Markdown
        text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```\s*", "", text)

        return text.strip()

    @staticmethod
    def _extract_json_object(text: str) -> str:
        """Extrait le premier objet JSON complet {...}"""
        text = AIParser._clean_basic(text)

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
                    return text[start:i+1]

        raise ValueError("Aucun objet JSON complet trouvé")

    @staticmethod
    def _smart_repair(text: str) -> str:
        """Répare les erreurs JSON courantes"""
        text = AIParser._clean_basic(text)

        # Échapper apostrophes dans strings
        text = re.sub(
            r'(["\'])([^"\']*?)\'([^"\']*?)\1',
            r'\1\2\\\'\3\1',
            text
        )

        # Supprimer virgules trailing
        text = re.sub(r",\s*([}\]])", r"\1", text)

        # Guillemets sur clés
        text = re.sub(r'([{\s,])(\w+)(\s*:)', r'\1"\2"\3', text)

        # Python booleans -> JSON
        text = re.sub(r'\bTrue\b', 'true', text)
        text = re.sub(r'\bFalse\b', 'false', text)
        text = re.sub(r'\bNone\b', 'null', text)

        # Apostrophes simples -> doubles
        text = re.sub(r"'([^']*)'(\s*[:, \]}])", r'"\1"\2', text)

        return text

    @staticmethod
    def _parse_partial(text: str, model: Type[BaseModel]) -> Optional[Dict]:
        """Parse partiel si JSON cassé"""
        try:
            model_fields = model.__fields__.keys()
            result = {}

            for field in model_fields:
                pattern = rf'"{field}"\s*:\s*(.+?)(?:,|\}})'
                match = re.search(pattern, text, re.DOTALL)

                if match:
                    try:
                        value_str = match.group(1).strip()

                        if value_str.startswith('"'):
                            result[field] = json.loads(value_str)
                        elif value_str.startswith('['):
                            result[field] = json.loads(value_str)
                        elif value_str.startswith('{'):
                            result[field] = json.loads(value_str)
                        else:
                            result[field] = json.loads(value_str)
                    except:
                        pass

            if result:
                logger.info(f"Parse partiel: {len(result)} champs extraits")
                return result

        except Exception as e:
            logger.debug(f"Parse partiel échoué: {e}")

        return None


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
        item_model: Modèle d'un item
        list_key: Clé contenant la liste
        fallback_items: Liste fallback

    Returns:
        Liste d'items validés
    """
    class ListWrapper(BaseModel):
        items: List[item_model]

    wrapper_data = AIParser.parse(
        response,
        ListWrapper,
        fallback={list_key: fallback_items or []},
        strict=False
    )

    return wrapper_data.items