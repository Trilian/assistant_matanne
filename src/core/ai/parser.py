"""
Analyseur JSON IA Ultra-Robuste
Gère tous les cas edge des réponses Mistral/GPT
"""

__all__ = ["AnalyseurIA", "analyser_liste_reponse"]

import json
import logging
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError, create_model

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


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
        reponse: str, modele: type[T], valeur_secours: dict | None = None, strict: bool = False
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
            result = modele.model_validate_json(nettoye)
            logger.info(f"[OK] Stratégie 1 (parse direct) réussie pour {modele.__name__}")
            return result
        except (ValidationError, json.JSONDecodeError) as e:
            logger.debug(f"Stratégie 1 échouée: {str(e)[:100]}")
            pass

        # Stratégie 2: Extraction JSON
        try:
            json_str = AnalyseurIA._extraire_objet_json(reponse)
            result = modele.model_validate_json(json_str)
            logger.info(f"[OK] Stratégie 2 (extraction JSON) réussie pour {modele.__name__}")
            return result
        except (ValidationError, json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Stratégie 2 échouée: {str(e)[:100]}")
            pass

        # Stratégie 3: Réparation
        try:
            repare = AnalyseurIA._reparer_intelligemment(reponse)
            donnees = json.loads(repare)
            result = modele(**donnees)
            logger.info(f"[OK] Stratégie 3 (réparation) réussie pour {modele.__name__}")
            return result
        except (ValidationError, json.JSONDecodeError, TypeError) as e:
            logger.debug(f"Stratégie 3 échouée: {str(e)[:100]}")
            pass

        # Stratégie 4: Parse partiel
        try:
            donnees_partielles = AnalyseurIA._analyser_partiel(reponse, modele)
            if donnees_partielles:
                result = modele(**donnees_partielles)
                logger.info(f"[OK] Stratégie 4 (parse partiel) réussie pour {modele.__name__}")
                return result
        except Exception as e:
            logger.debug(f"Stratégie 4 échouée: {str(e)[:100]}")
            pass

        # Stratégie 5: Fallback
        if not strict and valeur_secours:
            logger.warning(
                f"[!]  Toutes stratégies échouées, utilisation fallback pour {modele.__name__}"
            )
            logger.warning(f"   Response IA brute (300 chars): {reponse[:300]}")
            return modele(**valeur_secours)

        # Échec total
        logger.error(
            f"[ERROR] Impossible d'analyser réponse pour {modele.__name__}: {reponse[:200]}"
        )
        raise ValueError(f"Impossible d'analyser la réponse IA pour {modele.__name__}")

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
        """Extrait le premier objet JSON complet {...} ou liste [...]

        Gère correctement les structures imbriquées et les chaînes de caractères.
        """
        texte = AnalyseurIA._nettoyer_basique(texte)

        pile = []
        debut = None
        in_string = False
        escape = False

        for i, char in enumerate(texte):
            # Gestion des chaînes de caractères
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            # Si on n'est pas dans une chaîne
            if char == '"':
                in_string = True
                continue

            if char == "{":
                if not pile:
                    debut = i
                pile.append("{")
            elif char == "[":
                if not pile:
                    debut = i
                pile.append("[")
            elif char == "}":
                if pile and pile[-1] == "{":
                    pile.pop()
                if not pile and debut is not None:
                    return texte[debut : i + 1]
            elif char == "]":
                if pile and pile[-1] == "[":
                    pile.pop()
                if not pile and debut is not None:
                    return texte[debut : i + 1]

        raise ValueError("Aucun objet/liste JSON complet trouvé")

    @staticmethod
    def _reparer_troncature(texte: str) -> str:
        """Tentative de réparation d'un JSON tronqué"""
        texte = texte.strip()

        # 1. État de parsing simple
        pile = []
        in_string = False
        escape = False

        for char in texte:
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
            else:
                if char == '"':
                    in_string = True
                elif char in "{[":
                    pile.append(char)
                elif char in "}]":
                    if pile:
                        last_open = pile[-1]
                        if (char == "}" and last_open == "{") or (char == "]" and last_open == "["):
                            pile.pop()

        # 2. Fermer la chaîne en cours si nécessaire
        if in_string:
            texte += '"'

        # 3. Nettoyer la fin (virgules, deux points orphelins)
        texte = texte.rstrip()
        if texte.endswith(","):
            texte = texte[:-1]
        elif texte.endswith(":"):
            texte += " null"

        # 4. Fermer les accolades/crochets restants
        while pile:
            ouvrant = pile.pop()
            fermant = "}" if ouvrant == "{" else "]"
            texte += fermant

        return texte

    @staticmethod
    def _corriger_echappements_invalides(texte: str) -> str:
        """Corrige les séquences d'échappement invalides dans les chaînes JSON.

        Mistral génère parfois des backslashes invalides dans le texte français
        (ex: ``\\°C``, ``\\e``, ``l\\italienne``). Cette méthode les double
        pour en faire des backslashes littéraux valides en JSON.
        """
        valides = frozenset('"\\bfnrt/')
        resultat = []
        i = 0
        n = len(texte)
        in_string = False

        while i < n:
            char = texte[i]

            if not in_string:
                if char == '"':
                    in_string = True
                resultat.append(char)
                i += 1
            else:
                if char == '\\':
                    if i + 1 < n:
                        suivant = texte[i + 1]
                        if suivant in valides or suivant == 'u':
                            # Échappement JSON valide — conserver tel quel
                            resultat.append(char)
                            resultat.append(suivant)
                            i += 2
                        else:
                            # Échappement invalide — doubler le backslash
                            resultat.append('\\')
                            resultat.append('\\')
                            i += 1
                    else:
                        resultat.append('\\')
                        resultat.append('\\')
                        i += 1
                elif char == '"':
                    in_string = False
                    resultat.append(char)
                    i += 1
                else:
                    resultat.append(char)
                    i += 1

        return ''.join(resultat)

    @staticmethod
    def _reparer_intelligemment(texte: str) -> str:
        """Répare les erreurs JSON courantes

        Note: Cette méthode est heuristique et peut échouer sur des cas complexes.
        Elle tente de fixer les erreurs les plus fréquentes sans casser le JSON valide.
        """
        texte = AnalyseurIA._nettoyer_basique(texte)

        # 0. Réparation des troncatures (récupération d'erreurs fréquentes en streaming/taille max)
        texte = AnalyseurIA._reparer_troncature(texte)

        # 0b. Corriger les échappements invalides (\°, \e, etc.) générés par l'IA
        texte = AnalyseurIA._corriger_echappements_invalides(texte)

        # 1. Échapper apostrophes UNIQUEMENT dans les chaines simple-quotes
        def escape_inner_quotes(match):
            quote = match.group(1)
            # Ne JAMAIS toucher aux chaînes entre double quotes (JSON valide)
            if quote == '"':
                return match.group(0)

            # Pour single quotes (Python/JS style), on échappe l'apostrophe interne
            return f"{quote}{match.group(2)}\\'{match.group(3)}{quote}"

        # Regex: quote, content without quotes, quote literal, content without quotes, matching quote
        texte = re.sub(r'(["\'])([^"\']*?)\'([^"\']*?)\1', escape_inner_quotes, texte)

        # 2. Supprimer virgules trailing
        texte = re.sub(r",\s*([}\]])", r"\1", texte)

        # 2b. Ajouter virgules manquantes entre propriétés/éléments
        # Ex: "value" "key" → "value", "key"  ou  } { → }, {  ou  ] [ → ], [
        texte = re.sub(r'"\s*\n\s*"', '",\n"', texte)
        texte = re.sub(r"}\s*\n\s*{", "},\n{", texte)
        texte = re.sub(r'}\s*"', '},"', texte)
        texte = re.sub(r'"\s*{', '",{', texte)
        # Fix: "value"  "key" on same line
        texte = re.sub(r'"\s+"(?=[a-zA-Z_])', '", "', texte)

        # 3. Guillemets sur clés (ex: {key: val} -> {"key": val})
        texte = re.sub(r"([{\s,])(\w+)(\s*:)", r'\1"\2"\3', texte)

        # 4. Python booleans -> JSON
        texte = re.sub(r"\bTrue\b", "true", texte)
        texte = re.sub(r"\bFalse\b", "false", texte)
        texte = re.sub(r"\bNone\b", "null", texte)

        # 5. Convertir single quotes (clés/valeurs) en double quotes
        texte = re.sub(r"'([^']*)'(\s*[:, \]}])", r'"\1"\2', texte)

        return texte

    @staticmethod
    def _analyser_partiel(texte: str, modele: type[BaseModel]) -> dict | None:
        """Parse partiel si JSON cassé"""
        try:
            champs_modele = modele.model_fields.keys()
            resultat = {}

            for champ in champs_modele:
                pattern = rf'"{champ}"\s*:\s*(.+?)(?:,|\}})'
                match = re.search(pattern, texte, re.DOTALL)

                if match:
                    try:
                        chaine_valeur = match.group(1).strip()

                        if chaine_valeur.startswith('"'):
                            resultat[champ] = json.loads(chaine_valeur)
                        elif chaine_valeur.startswith("["):
                            resultat[champ] = json.loads(chaine_valeur)
                        elif chaine_valeur.startswith("{"):
                            resultat[champ] = json.loads(chaine_valeur)
                        else:
                            resultat[champ] = json.loads(chaine_valeur)
                    except Exception as e:
                        logger.debug(f"Impossible parser champ {champ}: {e}")

            if resultat:
                logger.info(f"Parse partiel: {len(resultat)} champs extraits")
                return resultat

        except Exception as e:
            logger.debug(f"Parse partiel échoué: {e}")

        return None


def analyser_liste_reponse(
    reponse: str,
    modele_item: type[BaseModel],
    cle_liste: str = "items",
    items_secours: list[dict] | None = None,
) -> list[BaseModel]:
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

    # LOG: Première partie de la réponse pour diagnostiquer
    reponse_debut = reponse[:500] if len(reponse) > 500 else reponse
    logger.debug(f"RAW AI RESPONSE (first 500 chars): {repr(reponse_debut)}")

    # Stratégie 1: Essayer de parser comme liste directe
    try:
        json_str = AnalyseurIA._extraire_objet_json(reponse)
        items_data = json.loads(json_str)
        logger.debug(f"[S1] JSON parsed successfully: {type(items_data)}")

        # Si c'est une liste directe
        if isinstance(items_data, list):
            logger.info(f"✅ Parser directe liste pour {modele_item.__name__}")
            return [modele_item(**item) for item in items_data]

        # Si c'est un dict avec la clé attendue
        if isinstance(items_data, dict) and cle_liste in items_data:
            items_list = items_data[cle_liste]
            if isinstance(items_list, list):
                logger.info(f"✅ Parser liste avec clé '{cle_liste}' pour {modele_item.__name__}")
                result = [modele_item(**item) for item in items_list]
                logger.info(f"✅ Successfully parsed {len(result)} items")
                return result

        # Stratégie 1b: dict avec clé différente — chercher la première valeur qui est une liste de dicts
        if isinstance(items_data, dict):
            for key, val in items_data.items():
                if isinstance(val, list) and val and isinstance(val[0], dict):
                    try:
                        result = [modele_item(**item) for item in val]
                        logger.info(f"✅ Parser liste avec clé alternative '{key}' pour {modele_item.__name__}")
                        return result
                    except Exception:
                        pass
    except Exception as e:
        logger.debug(f"Stratégie 1 échouée: {str(e)[:100]}")
        pass

    # Stratégie 2: Chercher [{ json objects }] pattern directement
    try:
        import re

        # Chercher pattern: [ { ... }, { ... } ]
        pattern = r"\[\s*\{.*?\}\s*\]"
        match = re.search(pattern, reponse, re.DOTALL)
        if match:
            json_str = match.group(0)
            items_list = json.loads(json_str)
            if isinstance(items_list, list):
                logger.info(f"✅ Regex array pattern found for {modele_item.__name__}")
                result = [modele_item(**item) for item in items_list]
                logger.info(f"✅ Successfully parsed {len(result)} items from regex")
                return result
    except Exception as e:
        logger.debug(f"Stratégie 2 (regex) échouée: {str(e)[:100]}")
        pass

    # Stratégie 3: Utiliser la clé de liste comme fallback via enveloppe dynamique
    try:
        EnvelopeListe = create_model(
            "EnvelopeListe",
            **{cle_liste: (list[modele_item], ...)},
        )

        donnees_enveloppe = AnalyseurIA.analyser(
            reponse, EnvelopeListe, valeur_secours={cle_liste: items_secours or []}, strict=False
        )
        items_result = getattr(donnees_enveloppe, cle_liste, [])
        if items_result:
            logger.info(f"✅ Envelope parser successful: {len(items_result)} items")
        return items_result
    except Exception as e:
        logger.warning(f"Stratégie 3 (envelope) échouée: {e}")

    # Fallback final: retourner items_secours
    if items_secours:
        logger.warning(f"Utilisation fallback avec {len(items_secours)} items")
        try:
            return [modele_item(**item) for item in items_secours]
        except Exception as e:
            logger.debug(f"Échec instantiation items_secours: {e}")

    logger.warning(
        f"[PARSE_FAIL] Impossible de parser liste pour {modele_item.__name__}. "
        f"Réponse IA (500 chars): {repr(reponse_debut)}"
    )
    return []
