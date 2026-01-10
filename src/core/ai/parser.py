"""
Analyseur JSON IA Ultra-Robuste
Gère tous les cas edge des réponses Mistral/GPT
"""
import json
import re
from typing import Dict, List, Optional, Type, TypeVar, Any
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AnalyseurIA:
    """
    Analyseur JSON universel pour réponses IA

    Stratégies (dans l'ordre):
    1. Parse direct (JSON propre)
    2. Extraction JSON brut (regex)
    3. Réparation intelligente
    4. Parse partiel
    5. Fallback
    """

    @staticmethod
    def analyser(
            reponse: str,
            modele: Type[T],
            valeur_secours: Optional[Dict] = None,
            strict: bool = False
    ) -> T:
        """
        Parse réponse IA en modèle Pydantic

        Args:
            reponse: Réponse brute IA
            modele: Modèle Pydantic cible
            valeur_secours: Dict fallback si échec
            strict: Si True, raise si échec (pas de fallback)

        Returns:
            Instance validée du modèle

        Raises:
            ValidationError si échec ET (strict=True OU pas de fallback)
        """
        # Stratégie 1: Parse direct
        try:
            nettoye = AnalyseurIA._nettoyer_basique(reponse)
            return modele.parse_raw(nettoye)
        except (ValidationError, json.JSONDecodeError):
            pass

        # Stratégie 2: Extraction JSON
        try:
            json_str = AnalyseurIA._extraire_objet_json(reponse)
            return modele.parse_raw(json_str)
        except (ValidationError, json.JSONDecodeError, ValueError):
            pass

        # Stratégie 3: Réparation
        try:
            repare = AnalyseurIA._reparer_intelligemment(reponse)
            donnees = json.loads(repare)
            return modele(**donnees)
        except (ValidationError, json.JSONDecodeError, TypeError):
            pass

        # Stratégie 4: Parse partiel
        try:
            donnees_partielles = AnalyseurIA._analyser_partiel(reponse, modele)
            if donnees_partielles:
                return modele(**donnees_partielles)
        except Exception:
            pass

        # Stratégie 5: Fallback
        if not strict and valeur_secours:
            logger.warning("Toutes stratégies échouées, utilisation fallback")
            return modele(**valeur_secours)

        # Échec total
        logger.error(f"Impossible d'analyser: {reponse[:500]}")
        raise ValidationError("Impossible d'analyser la réponse IA")

    @staticmethod
    def _nettoyer_basique(texte: str) -> str:
        """Nettoyage basique"""
        # BOM et caractères invisibles
        texte = texte.replace("\ufeff", "")
        texte = re.sub(r"[\x00-\x1F\x7F]", "", texte)

        # Markdown
        texte = re.sub(r"```json\s*", "", texte, flags=re.IGNORECASE)
        texte = re.sub(r"```\s*", "", texte)

        return texte.strip()

    @staticmethod
    def _extraire_objet_json(texte: str) -> str:
        """Extrait le premier objet JSON complet {...}"""
        texte = AnalyseurIA._nettoyer_basique(texte)

        pile = []
        debut = None

        for i, char in enumerate(texte):
            if char == '{':
                if not pile:
                    debut = i
                pile.append(char)
            elif char == '}':
                if pile:
                    pile.pop()
                if not pile and debut is not None:
                    return texte[debut:i+1]

        raise ValueError("Aucun objet JSON complet trouvé")

    @staticmethod
    def _reparer_intelligemment(texte: str) -> str:
        """Répare les erreurs JSON courantes"""
        texte = AnalyseurIA._nettoyer_basique(texte)

        # Échapper apostrophes dans strings
        texte = re.sub(
            r'(["\'])([^"\']*?)\'([^"\']*?)\1',
            r'\1\2\\\'\3\1',
            texte
        )

        # Supprimer virgules trailing
        texte = re.sub(r",\s*([}\]])", r"\1", texte)

        # Guillemets sur clés
        texte = re.sub(r'([{\s,])(\w+)(\s*:)', r'\1"\2"\3', texte)

        # Python booleans -> JSON
        texte = re.sub(r'\bTrue\b', 'true', texte)
        texte = re.sub(r'\bFalse\b', 'false', texte)
        texte = re.sub(r'\bNone\b', 'null', texte)

        # Apostrophes simples -> doubles
        texte = re.sub(r"'([^']*)'(\s*[:, \]}])", r'"\1"\2', texte)

        return texte

    @staticmethod
    def _analyser_partiel(texte: str, modele: Type[BaseModel]) -> Optional[Dict]:
        """Parse partiel si JSON cassé"""
        try:
            champs_modele = modele.__fields__.keys()
            resultat = {}

            for champ in champs_modele:
                pattern = rf'"{champ}"\s*:\s*(.+?)(?:,|\}})'
                match = re.search(pattern, texte, re.DOTALL)

                if match:
                    try:
                        chaine_valeur = match.group(1).strip()

                        if chaine_valeur.startswith('"'):
                            resultat[champ] = json.loads(chaine_valeur)
                        elif chaine_valeur.startswith('['):
                            resultat[champ] = json.loads(chaine_valeur)
                        elif chaine_valeur.startswith('{'):
                            resultat[champ] = json.loads(chaine_valeur)
                        else:
                            resultat[champ] = json.loads(chaine_valeur)
                    except:
                        pass

            if resultat:
                logger.info(f"Parse partiel: {len(resultat)} champs extraits")
                return resultat

        except Exception as e:
            logger.debug(f"Parse partiel échoué: {e}")

        return None


def analyser_liste_reponse(
        reponse: str,
        modele_item: Type[BaseModel],
        cle_liste: str = "items",
        items_secours: Optional[List[Dict]] = None
) -> List[BaseModel]:
    """
    Parse une réponse contenant une liste

    Args:
        reponse: Réponse IA
        modele_item: Modèle d'un item
        cle_liste: Clé contenant la liste
        items_secours: Liste fallback

    Returns:
        Liste d'items validés
    """
    class EnvelopeListe(BaseModel):
        items: List[modele_item]

    donnees_enveloppe = AnalyseurIA.analyser(
        reponse,
        EnvelopeListe,
        valeur_secours={cle_liste: items_secours or []},
        strict=False
    )

    return donnees_enveloppe.items