"""
Service de scoring de pertinence pour les suggestions familles.

Calcul déterministe (sans IA) d'un score de pertinence pour chaque suggestion
en fonction du contexte familial courant.
"""

from src.services.core.registry import service_factory
from src.services.core.scoring import BaseScoringService


from dataclasses import dataclass, field

@dataclass
class SuggestionScoree:
    """Suggestion enrichie avec score de pertinence."""
    score_pertinence: float = 0.5
    raison_suggestion: str = "Suggestion générale"
    sources_score: list[str] = field(default_factory=list)


class ScoringPertinenceService(BaseScoringService):
    """Score la pertinence des suggestions selon le contexte familial."""

    FACTEURS = {
        "anniversaire_proche": 0.30,
        "jalon_recent": 0.20,
        "meteo_adaptee": 0.20,
        "budget_disponible": 0.15,
        "age_jules_adapte": 0.15,
    }

    def scorer_suggestion(self, suggestion: dict, contexte: dict | None = None) -> SuggestionScoree:
        """Score une suggestion selon le contexte. Retourne SuggestionScoree avec score 0.0–1.0."""
        if contexte is None:
            return SuggestionScoree()

        score = 0.0
        sources: list[str] = []

        # Anniversaire proche (J-14)
        anniversaires = contexte.get("anniversaires") or []
        if any(int(a.get("jours_restants", 99)) <= 14 for a in anniversaires if isinstance(a, dict)):
            score += self.FACTEURS["anniversaire_proche"]
            sources.append("anniversaire proche")

        # Jalon Jules récent
        jalons_recents = contexte.get("jalons_recents") or contexte.get("jalons") or []
        if jalons_recents:
            score += self.FACTEURS["jalon_recent"]
            sources.append("jalon Jules récent")

        # Météo adaptée
        meteo = contexte.get("meteo") or {}
        type_activite = suggestion.get("type_activite") or suggestion.get("type") or ""
        if meteo and type_activite:
            temps = str(meteo.get("description") or meteo.get("temps") or "").lower()
            exterieur = any(k in type_activite.lower() for k in ["extérieur", "exterieur", "plein_air", "sport"])
            interieur = any(k in type_activite.lower() for k in ["intérieur", "interieur", "maison", "culture"])
            pluie = any(k in temps for k in ["pluie", "orage", "nuage"])
            beau = any(k in temps for k in ["soleil", "clair", "beau"])
            if (exterieur and beau) or (interieur and pluie):
                score += self.FACTEURS["meteo_adaptee"]
                sources.append("météo adaptée")

        # Budget disponible
        budget = contexte.get("budget") or {}
        solde = float(budget.get("solde") or budget.get("disponible") or 0)
        prix = float(suggestion.get("prix_estime") or suggestion.get("fourchette_prix_min") or 0)
        if solde > 0 and (prix == 0 or prix <= solde * 0.25):
            score += self.FACTEURS["budget_disponible"]
            sources.append("budget disponible")

        # Âge Jules adapté
        jules = contexte.get("jules") or contexte.get("profil_enfant") or {}
        age_mois = int(jules.get("age_mois") or 0)
        age_min = int(suggestion.get("age_min_mois") or 0)
        age_max = int(suggestion.get("age_max_mois") or 999)
        if age_mois > 0 and age_min <= age_mois <= age_max:
            score += self.FACTEURS["age_jules_adapte"]
            sources.append("adapté à l'âge de Jules")

        score_construit = self.construire_score(score, sources)
        return SuggestionScoree(
            score_pertinence=score_construit.score,
            raison_suggestion=score_construit.raison,
            sources_score=score_construit.sources,
        )

    def scorer_et_trier(self, suggestions: list[dict], contexte: dict | None = None) -> list[dict]:
        """Score toutes les suggestions et les trie par pertinence décroissante."""
        resultats = []
        for s in suggestions:
            try:
                scored = self.scorer_suggestion(s, contexte)
                resultats.append({
                    **s,
                    "score_pertinence": scored.score_pertinence,
                    "raison_suggestion": scored.raison_suggestion,
                    "sources_score": scored.sources_score,
                })
            except Exception as exc:  # noqa: BLE001
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Scoring échoué pour suggestion '%s': %s", s.get("titre", "?"), exc)
                resultats.append({**s, "score_pertinence": 0.5, "raison_suggestion": "Suggestion générale", "sources_score": []})
        return sorted(resultats, key=lambda x: x.get("score_pertinence", 0), reverse=True)


def obtenir_service_scoring() -> ScoringPertinenceService:
    """Factory — retourne le service de scoring pertinence."""
    return ScoringPertinenceService()
