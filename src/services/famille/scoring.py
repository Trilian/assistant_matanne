"""
Service de scoring de pertinence pour les suggestions familles.

Calcul déterministe (sans IA) d'un score de pertinence pour chaque suggestion
en fonction du contexte familial courant.
"""

from src.services.core.registry import service_factory


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
            enrichie.setdefault("score_pertinence", 0.5)
            enrichie.setdefault("raison_suggestion", "Suggestion générale")
            enrichie.setdefault("sources_score", [])
            return enrichie

        score = 0.0
        sources: list[str] = []

        # +0.30 — anniversaire proche (≤ 14 jours)
        anniversaires = contexte.get("anniversaires") or []
        for anniv in anniversaires:
            jours = anniv.get("jours_restants")
            if jours is not None and jours <= 14:
                score += 0.30
                sources.append("anniversaire proche")
                break

        # +0.20 — jalon Jules récent
        jalons_recents = contexte.get("jalons_recents") or []
        if jalons_recents:
            score += 0.20
            sources.append("jalon Jules récent")

        # +0.20 — météo adaptée au type d'activité
        meteo_contexte = contexte.get("meteo") or ""
        type_activite = suggestion.get("type_activite") or suggestion.get("lieu") or ""
        if meteo_contexte and type_activite:
            meteo_match = (
                ("pluie" in meteo_contexte.lower() and "interieur" in type_activite.lower())
                or ("soleil" in meteo_contexte.lower() and "exterieur" in type_activite.lower())
                or ("mixte" in meteo_contexte.lower())
            )
            if meteo_match:
                score += 0.20
                sources.append("météo adaptée")

        # +0.15 — budget disponible
        solde = contexte.get("budget_solde") or 0.0
        prix_estime = suggestion.get("prix_estime") or 0.0
        if solde > 0 and prix_estime > 0 and prix_estime <= solde * 0.2:
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

        score = min(score, 1.0)
        raison = ", ".join(sources) if sources else "Suggestion générale"

        enrichie = dict(suggestion)
        enrichie["score_pertinence"] = round(score, 2)
        enrichie["raison_suggestion"] = raison
        enrichie["sources_score"] = sources
        return enrichie


@service_factory("scoring_famille")
def obtenir_service_scoring() -> ScoringPertinenceService:
    """Factory singleton du service de scoring pertinence."""
    return ScoringPertinenceService()
