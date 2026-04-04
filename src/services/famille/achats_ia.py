"""
Service IA Achats Famille - Suggestions d'achats automatiques.

Suggère via Mistral :
- Cadeaux d'anniversaire (basé sur âge, relation, historique)
- Achats saisonniers (vêtements, équipements enfant)
- Achats liés aux jalons OMS (chaussures marche, etc.)
"""

import logging

from src.core.ai import obtenir_client_ia
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class AchatsIAService(BaseAIService):
    """Service IA pour suggestions d'achats familiaux automatiques."""

    def __init__(self):
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="achats_famille",
            default_ttl=86400,  # 24h
            service_name="achats_ia",
        )

    async def suggerer_cadeaux_anniversaire(
        self,
        nom: str,
        age: int,
        relation: str,
        budget_max: float = 50.0,
        historique_cadeaux: list[str] | None = None,
        contexte: dict | None = None,
    ) -> list[dict]:
        """Suggère des idées cadeaux pour un anniversaire."""
        historique_txt = ""
        if historique_cadeaux:
            historique_txt = f"\nCadeaux déjà offerts : {', '.join(historique_cadeaux)}"

        prompt = f"""Suggère 5 idées cadeaux pour {nom}, {age} ans, ({relation}).
Budget max : {budget_max}€.{historique_txt}

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom du cadeau
- description : 1-2 phrases
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON, pas de texte autour."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en cadeaux. Retourne UNIQUEMENT du JSON valide. Français.",
            max_tokens=800,
        )

        suggestions = self._parse_suggestions(result)
        return self._appliquer_scoring(suggestions, contexte)

    async def suggerer_achats_saison(
        self,
        age_enfant_mois: int,
        saison: str,
        tailles: dict | None = None,
        contexte: dict | None = None,
    ) -> list[dict]:
        """Suggère des achats saisonniers pour l'enfant."""
        tailles_txt = ""
        if tailles:
            tailles_txt = f"\nTailles actuelles : {tailles}"

        prompt = f"""Jules a {age_enfant_mois} mois. La saison {saison} arrive.{tailles_txt}

Quels vêtements et équipements prévoir ? Suggère 5 achats.

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom de l'article
- description : 1-2 phrases (pourquoi c'est nécessaire)
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en puériculture et vêtements enfants. JSON valide uniquement. Français.",
            max_tokens=800,
        )

        suggestions = self._parse_suggestions(result)
        return self._appliquer_scoring(suggestions, contexte)

    async def suggerer_achats_jalon(
        self,
        age_mois: int,
        prochains_jalons: list[str],
        contexte: dict | None = None,
    ) -> list[dict]:
        """Suggère des achats liés aux prochains jalons de développement."""
        jalons_txt = "\n".join(f"- {j}" for j in prochains_jalons)

        prompt = f"""Jules a {age_mois} mois. Prochains jalons de développement attendus :
{jalons_txt}

Quels achats préparer pour accompagner ces étapes ? Suggère 3-5 achats pertinents.

Retourne un JSON valide, une liste d'objets avec ces champs :
- titre : nom de l'article
- description : 1-2 phrases (lien avec le jalon)
- fourchette_prix : "X-Y€"
- ou_acheter : suggestion de magasin/site
- pertinence : "haute", "moyenne" ou "basse"

Réponds UNIQUEMENT avec le JSON."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en développement de l'enfant et puériculture. JSON valide uniquement. Français.",
            max_tokens=600,
        )

        suggestions = self._parse_suggestions(result)
        return self._appliquer_scoring(suggestions, contexte)

    def _appliquer_scoring(self, suggestions: list[dict], contexte: dict | None) -> list[dict]:
        """Enrichit chaque suggestion avec un score de pertinence et trie par score décroissant."""
        if not suggestions:
            return suggestions

        from src.services.famille.scoring import obtenir_service_scoring
        return obtenir_service_scoring().scorer_et_trier(suggestions, contexte)

    def _parse_suggestions(self, raw_result: str) -> list[dict]:
        """Parse le résultat IA en liste de suggestions."""
        import json

        if not raw_result:
            return []

        # Nettoyer le résultat (enlever les blocs markdown)
        text = raw_result.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:])
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        try:
            data = json.loads(text)
            if isinstance(data, list):
                return [
                    {
                        "titre": item.get("titre", ""),
                        "description": item.get("description", ""),
                        "fourchette_prix": item.get("fourchette_prix"),
                        "ou_acheter": item.get("ou_acheter"),
                        "pertinence": item.get("pertinence", "moyenne"),
                    }
                    for item in data
                    if isinstance(item, dict) and item.get("titre")
                ]
        except json.JSONDecodeError:
            logger.warning("Impossible de parser les suggestions IA achats")

        return []

    async def suggerer_vetements_qualite(
        self,
        pour_qui: str = "anne",
        style: dict | None = None,
        taille: dict | None = None,
        saison: str = "automne/hiver",
        nb_suggestions: int = 4,
    ) -> list[dict]:
        """Suggestions de vêtements qualité selon le style de la personne.

        Prend en compte l'approche minimaliste / Made in France pour Anne.
        """
        style = style or {}
        taille = taille or {}
        approche = style.get("approche", "normal")
        mif = style.get("prefere_made_france", False)
        budget_piece = style.get("budget_piece_max", 100)

        prompt = f"""Propose {nb_suggestions} suggestions de vêtements pour {pour_qui} pour la saison {saison}.

Profil:
- Approche: {approche}
- Made in France: {'Oui, privilégier les marques françaises / européennes' if mif else 'Non'}
- Budget max par pièce: {budget_piece}€
- Tailles: {taille if taille else 'non précisé'}

Pour chaque suggestion, retourne un JSON array:
[{{
  "titre": "Nom de la pièce",
  "description": "Pourquoi ce choix (qualité, coupe, usage)",
  "fourchette_prix": "X-Y€",
  "ou_acheter": "Marque(s) recommandée(s)",
  "pertinence": "haute/moyenne/basse"
}}]

Privilégier les pièces essentielles, intemporelles, polyvalentes."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en mode durable et minimaliste. Réponds en JSON uniquement.",
            max_tokens=600,
        )
        return self._parse_suggestions(result)

    async def suggerer_achats_sejour(
        self,
        destination: str,
        duree_jours: int,
        age_jules_mois: int = 19,
        nb_suggestions: int = 5,
    ) -> list[dict]:
        """Suggestions d'équipement pour un séjour/voyage.

        Tient compte de l'âge de Jules et de la destination.
        """
        prompt = f"""Pour un séjour de {duree_jours} jours à {destination} avec un enfant de {age_jules_mois} mois, propose {nb_suggestions} achats/locations à prévoir.

Retourne un JSON array:
[{{
  "titre": "Article/équipement",
  "description": "Pourquoi c'est utile pour ce voyage avec bébé",
  "fourchette_prix": "X-Y€ ou 'location X€/j'",
  "ou_acheter": "Marque ou magasin",
  "pertinence": "haute/moyenne/basse"
}}]

Distingue achats vs locations. Pense équipement bébé spécifique à la destination (si mer, si montagne, si ville)."""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en voyage famille avec jeunes enfants. Réponds en JSON uniquement.",
            max_tokens=600,
        )
        return self._parse_suggestions(result)

    async def suggerer_sorties_culture(
        self,
        ville: str = "Paris",
        age_jules_mois: int = 19,
        budget: int = 60,
        interets: list[str] | None = None,
        nb_suggestions: int = 4,
    ) -> list[dict]:
        """Suggestions de sorties culturelles selon les intérêts (gaming, SF, etc.)."""
        interets_str = ", ".join(interets) if interets else "généraliste"

        prompt = f"""Propose {nb_suggestions} sorties culturelles ou loisirs à {ville} pour une famille.

Contexte:
- Enfant de {age_jules_mois} mois (précise si accessible)
- Budget: {budget}€ pour deux adultes
- Intérêts Mathieu: {interets_str}

Retourne un JSON array:
[{{
  "titre": "Nom de la sortie",
  "description": "Description + lien intérêts",
  "fourchette_prix": "X€ pp",
  "ou_acheter": "Lieu/site de réservation",
  "pertinence": "haute/moyenne/basse"
}}]"""

        result = await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en loisirs culturels familiaux. Réponds en JSON uniquement.",
            max_tokens=600,
        )
        return self._parse_suggestions(result)

    async def generer_annonce_lbc(
        self,
        nom: str,
        description: str | None = None,
        etat_usage: str = "bon état",
        prix_cible: float | None = None,
    ) -> str:
        """Génère une annonce Leboncoin optimisée.

        Returns:
            Texte de l'annonce (titre + détails + prix + hashtags).
        """
        prix_str = f"Prix : {prix_cible}€" if prix_cible else "Prix : à définir"
        desc_str = f"\nDétails produit : {description}" if description else ""

        prompt = f"""Génère une annonce Leboncoin optimisée pour vendre cet article.

Article : {nom}{desc_str}
État : {etat_usage}
{prix_str}

Format attendu:
**TITRE** (max 60 caractères, accrocheur, keywords pertinents)

**DESCRIPTION**
[3-5 phrases : état, points forts, conditions vente, disponibilité, livraison possible?]

**PRIX CONSEILLÉ** : X€
(Justification du prix)

**HASHTAGS** : #tag1 #tag2 ..."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en rédaction d'annonces Leboncoin. Réponds en français, ton vendu/pratique.",
            max_tokens=500,
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("achats_ia", tags={"famille", "ia", "achats"})
def obtenir_service_achats_ia() -> AchatsIAService:
    """Factory singleton pour AchatsIAService."""
    return AchatsIAService()


# Alias anglais
get_achats_ia_service = obtenir_service_achats_ia
