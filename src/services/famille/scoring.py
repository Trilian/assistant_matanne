"""
Service de scoring de pertinence pour les suggestions familles.

Calcul déterministe (sans IA) d'un score de pertinence pour chaque suggestion
en fonction du contexte familial courant.
"""

from typing import TypedDict

from src.services.core.registry import service_factory


class SuggestionScoree(TypedDict):
    """Champs de scoring ajoutés à une suggestion enrichie."""

    score_pertinence: float
    raison_suggestion: str
    sources_score: list[str]


class ScoringPertinenceService:
    """Service de scoring déterministe pour les suggestions familiales.

    Score chaque suggestion de 0.0 à 1.0 selon plusieurs facteurs additifs.
    """

    def scorer_suggestion(self, suggestion: dict, contexte: dict | None = None) -> dict:
        """Score une suggestion selon le contexte familial.

        Args:
            suggestion: Dictionnaire représentant la suggestion à scorer.
            contexte: Contexte familial (anniversaires, jalons, météo, budget, âge Jules…).

        Returns:
            La suggestion enrichie avec :
              - score_pertinence (float 0.0–1.0)
              - raison_suggestion (str)
              - sources_score (list[str])
        """
        if contexte is None:
            enrichie = dict(suggestion)
            enrichie["score_pertinence"] = 0.5
            enrichie["raison_suggestion"] = "Suggestion générale"
            enrichie["sources_score"] = []
            return enrichie

        score = 0.0
        sources: list[str] = []

        # +0.30 — anniversaire proche (≤ 14 jours)
        anniversaires = contexte.get("anniversaires") or []
        for anniv in anniversaires:
            jours = anniv.get("jours_restants")
            if jours is not None and jours <= 14:
                score += 0.30
                sources.append("anniversaire proche (J-14)")
                break

        # +0.20 — jalon Jules récent
        jalons_recents = contexte.get("jalons_recents") or []
        if jalons_recents:
            score += 0.20
            sources.append("jalon Jules récent")

        # +0.20 — météo adaptée au type de suggestion
        type_suggestion = suggestion.get("type") or ""
        meteo = contexte.get("meteo")
        if type_suggestion and isinstance(meteo, dict):
            icone = meteo.get("icone") or ""
            est_ext = "exterieur" in type_suggestion or "plein_air" in type_suggestion
            est_int = "interieur" in type_suggestion or "maison" in type_suggestion
            meteo_ext = icone in ("☀️", "⛅")
            meteo_int = icone in ("🌧️", "❄️")
            if (est_ext and meteo_ext) or (est_int and meteo_int):
                score += 0.20
                sources.append("météo adaptée")

        # +0.15 — budget disponible
        budget = contexte.get("budget")
        prix_estime = suggestion.get("prix_estime")
        if isinstance(budget, dict):
            solde = budget.get("solde") or 0.0
            if solde > 0 and isinstance(prix_estime, (int, float)) and prix_estime <= solde * 0.3:
                score += 0.15
                sources.append("budget disponible")

        # +0.15 — âge Jules adapté
        jules_age_mois = contexte.get("jules_age_mois")
        age_min = suggestion.get("age_min_mois")
        age_max = suggestion.get("age_max_mois")
        if (
            jules_age_mois is not None
            and age_min is not None
            and age_max is not None
            and age_min <= jules_age_mois <= age_max
        ):
            score += 0.15
            sources.append("adapté à l'âge de Jules")

        raison = ", ".join(sources) if sources else "Suggestion générale"

        enrichie = dict(suggestion)
        enrichie["score_pertinence"] = round(min(score, 1.0), 2)
        enrichie["raison_suggestion"] = raison
        enrichie["sources_score"] = sources
        return enrichie

    def scorer_liste(self, suggestions: list[dict], contexte: dict | None = None) -> list[dict]:
        """Score une liste de suggestions et la trie par score décroissant.

        Args:
            suggestions: Liste de suggestions à scorer.
            contexte: Contexte familial partagé.

        Returns:
            Liste enrichie et triée par score_pertinence décroissant.
        """
        enrichies = [self.scorer_suggestion(s, contexte) for s in suggestions]
        return sorted(enrichies, key=lambda x: x.get("score_pertinence", 0.5), reverse=True)


@service_factory("scoring_famille")
def obtenir_service_scoring() -> ScoringPertinenceService:
    """Factory singleton du service de scoring pertinence."""
    return ScoringPertinenceService()
