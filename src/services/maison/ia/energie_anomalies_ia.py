"""Service IA pour detection d'anomalies energie (détection anomalies énergie).

Combine:
- scoring heuristique d'anormalite par mois
- explications IA par type de compteur (fallback heuristique si IA indisponible)
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.ai import obtenir_client_ia
from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models.maison_extensions import ReleveCompteur
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


class ExplicationAnomalieIA(BaseModel):
    """Explication IA d'une anomalie mensuelle."""

    mois: str = Field(..., description="Mois YYYY-MM")
    explication: str = Field(..., description="Explication concise de l'anomalie")
    causes_probables: list[str] = Field(default_factory=list)
    actions_recommandees: list[str] = Field(default_factory=list)


class EnergieAnomaliesIAService(BaseAIService):
    """Service maison dedie a l'analyse d'anomalies energie."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="energie_anomalies_ia",
            default_ttl=1800,
            service_name="energie_anomalies_ia",
        )

    @staticmethod
    def _score_anormalite(ecart_pct: float) -> int:
        """Transforme un ecart en score 0-100."""
        # 20% -> 20, 100%+ -> 100
        return int(max(0, min(100, abs(ecart_pct))))

    @staticmethod
    def _severite(score: int) -> str:
        if score >= 60:
            return "critique"
        if score >= 35:
            return "elevee"
        if score >= 20:
            return "moyenne"
        return "faible"

    def _fallback_explanation(self, type_compteur: str, point: dict[str, Any]) -> dict[str, Any]:
        """Fallback deterministic si IA indisponible."""
        tendance = "hausse" if float(point.get("ecart_pct", 0)) > 0 else "baisse"
        type_label = type_compteur.lower()
        return {
            "mois": str(point.get("mois")),
            "explication": (
                f"Variation en {tendance} pour le compteur {type_label} vs moyenne glissante."
            ),
            "causes_probables": [
                "changement d'usage du foyer",
                "conditions meteo inhabituelles",
                "equipement plus energivore",
            ],
            "actions_recommandees": [
                "verifier les appareils les plus consommateurs",
                "comparer avec les memes mois de l'annee precedente",
                "programmer un suivi hebdomadaire temporaire",
            ],
        }

    def _generer_explications_ia(
        self,
        type_compteur: str,
        anomalies: list[dict[str, Any]],
        moyenne: float,
    ) -> list[dict[str, Any]]:
        """Produit des explications IA pour les anomalies detectees."""
        if not anomalies:
            return []

        donnees = [
            {
                "mois": a["mois"],
                "conso": a["conso"],
                "ecart_pct": a["ecart_pct"],
                "score_anormalite": a["score_anormalite"],
            }
            for a in anomalies
        ]

        prompt = (
            "Analyse les anomalies de consommation suivantes et propose des explications "
            "pragmatiques pour un foyer francais.\n"
            f"Type compteur: {type_compteur}\n"
            f"Moyenne periode: {round(moyenne, 2)}\n"
            f"Anomalies: {donnees}\n"
            "Retourne une liste d'objets avec: mois, explication, causes_probables (3 max), "
            "actions_recommandees (3 max)."
        )

        system_prompt = (
            "Tu es un expert energie domestique. "
            "Reponds en JSON strict, factuel, sans inventer de mesures."
        )

        try:
            resultat = self.call_with_list_parsing_sync(
                prompt=prompt,
                item_model=ExplicationAnomalieIA,
                system_prompt=system_prompt,
                max_tokens=1200,
                use_cache=True,
            )
            if not resultat:
                return [self._fallback_explanation(type_compteur, a) for a in anomalies]
            return [item.model_dump() for item in resultat]
        except Exception:
            return [self._fallback_explanation(type_compteur, a) for a in anomalies]

    @avec_gestion_erreurs(default_return={"type": "", "points": [], "anomalies": [], "total": 0})
    @avec_session_db
    def analyser_anomalies(
        self,
        type_compteur: str = "electricite",
        nb_mois: int = 12,
        seuil_pct: float = 20.0,
        *,
        db: Session | None = None,
    ) -> dict[str, Any]:
        """Analyse les anomalies de consommation et retourne un score global."""
        if db is None:
            return {"type": type_compteur, "points": [], "anomalies": [], "total": 0}

        rows = (
            db.query(
                func.date_trunc("month", ReleveCompteur.date_releve).label("mois"),
                func.sum(ReleveCompteur.consommation_periode).label("conso"),
            )
            .filter(ReleveCompteur.type_compteur == type_compteur)
            .filter(ReleveCompteur.consommation_periode.isnot(None))
            .group_by(func.date_trunc("month", ReleveCompteur.date_releve))
            .order_by(func.date_trunc("month", ReleveCompteur.date_releve))
            .limit(nb_mois)
            .all()
        )

        points = [{"mois": str(r.mois)[:7], "conso": float(r.conso or 0)} for r in rows]
        if not points:
            return {
                "type": type_compteur,
                "points": [],
                "anomalies": [],
                "total": 0,
                "score_anormalite_global": 0,
                "moyenne": 0.0,
                "message": "Aucun releve disponible",
            }

        moyenne = sum(p["conso"] for p in points) / len(points)

        anomalies: list[dict[str, Any]] = []
        for p in points:
            ecart_pct = ((p["conso"] - moyenne) / moyenne * 100) if moyenne else 0.0
            score = self._score_anormalite(ecart_pct)
            est_anomalie = abs(ecart_pct) >= seuil_pct
            p["ecart_pct"] = round(ecart_pct, 1)
            p["score_anormalite"] = score
            p["anomalie"] = est_anomalie
            if est_anomalie:
                anomalies.append(
                    {
                        "mois": p["mois"],
                        "conso": p["conso"],
                        "ecart_pct": p["ecart_pct"],
                        "score_anormalite": score,
                        "severite": self._severite(score),
                    }
                )

        explications = self._generer_explications_ia(
            type_compteur=type_compteur,
            anomalies=anomalies,
            moyenne=moyenne,
        )
        explications_par_mois = {e.get("mois"): e for e in explications}

        for a in anomalies:
            e = explications_par_mois.get(a["mois"])
            if e:
                a["explication"] = e.get("explication")
                a["causes_probables"] = e.get("causes_probables", [])
                a["actions_recommandees"] = e.get("actions_recommandees", [])

        score_global = round(
            (sum(a["score_anormalite"] for a in anomalies) / max(1, len(points))), 1
        )

        return {
            "type": type_compteur,
            "points": points,
            "anomalies": anomalies,
            "total": len(points),
            "nb_anomalies": len(anomalies),
            "score_anormalite_global": score_global,
            "moyenne": round(moyenne, 2),
            "seuil_pct": seuil_pct,
            "metadata": {
                "genere_le": date.today().isoformat(),
                "methode": "heuristique+ia",
            },
        }


@service_factory("energie_anomalies_ia", tags={"maison", "energie", "ia"})
def obtenir_service_energie_anomalies_ia() -> EnergieAnomaliesIAService:
    """Factory singleton du service anomalies energie IA."""
    return EnergieAnomaliesIAService()
