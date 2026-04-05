"""Service IA - detection d'anomalies de depenses (IA3)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory


@dataclass
class MoisRef:
    annee: int
    mois: int


class ResumeAnomaliesIA(BaseModel):
    """Sortie IA courte pour widget dashboard."""

    resume: str = ""
    recommandations: list[str] = Field(default_factory=list)


class ServiceAnomaliesFinancieres(BaseAIService):
    """Compare mois courant vs N-1/N-2 et detecte les variations anormales."""

    def __init__(self) -> None:
        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="anomalies_financieres",
            default_ttl=1800,
            service_name="anomalies_financieres",
        )

    @staticmethod
    def _mois_precedents(ref: date) -> list[MoisRef]:
        courant = MoisRef(annee=ref.year, mois=ref.month)
        mois_1 = ref.month - 1
        annee_1 = ref.year
        if mois_1 == 0:
            mois_1 = 12
            annee_1 -= 1

        mois_2 = mois_1 - 1
        annee_2 = annee_1
        if mois_2 == 0:
            mois_2 = 12
            annee_2 -= 1

        return [courant, MoisRef(annee_1, mois_1), MoisRef(annee_2, mois_2)]

    @staticmethod
    def _normaliser_categorie(categorie: str | None) -> str:
        cat = (categorie or "autre").strip().lower()
        if any(k in cat for k in ("course", "aliment", "supermarche", "epicer")):
            return "courses"
        if any(k in cat for k in ("energie", "electric", "gaz", "eau", "chauffage")):
            return "energie"
        if any(k in cat for k in ("loisir", "sortie", "jeu", "culture", "restaurant")):
            return "loisirs"
        return cat or "autre"

    def _collecter_depenses(self, reference: date | None = None) -> dict[str, dict[str, float]]:
        """Collecte les montants par categorie normalisee sur mois courant, N-1, N-2."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)

        result: dict[str, dict[str, float]] = {
            f"{m.annee:04d}-{m.mois:02d}": defaultdict(float) for m in mois_refs
        }

        with obtenir_contexte_db() as session:
            from sqlalchemy import extract, func
            from src.core.models import BudgetFamille
            from src.core.models.finances import DepenseMaison

            for m in mois_refs:
                key = f"{m.annee:04d}-{m.mois:02d}"

                dep_famille = (
                    session.query(BudgetFamille.categorie, func.sum(BudgetFamille.montant))
                    .filter(
                        extract("year", BudgetFamille.date) == m.annee,
                        extract("month", BudgetFamille.date) == m.mois,
                    )
                    .group_by(BudgetFamille.categorie)
                    .all()
                )
                for categorie, montant in dep_famille:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

                dep_maison = (
                    session.query(DepenseMaison.categorie, func.sum(DepenseMaison.montant))
                    .filter(DepenseMaison.annee == m.annee, DepenseMaison.mois == m.mois)
                    .group_by(DepenseMaison.categorie)
                    .all()
                )
                for categorie, montant in dep_maison:
                    result[key][self._normaliser_categorie(categorie)] += float(montant or 0.0)

        return {k: dict(v) for k, v in result.items()}

    def detecter_anomalies(self, reference: date | None = None) -> dict[str, Any]:
        """Detecte les anomalies de depenses par categorie."""
        ref = reference or date.today()
        mois_refs = self._mois_precedents(ref)
        key_courant = f"{mois_refs[0].annee:04d}-{mois_refs[0].mois:02d}"
        key_n1 = f"{mois_refs[1].annee:04d}-{mois_refs[1].mois:02d}"
        key_n2 = f"{mois_refs[2].annee:04d}-{mois_refs[2].mois:02d}"

        series = self._collecter_depenses(ref)
        courant = series.get(key_courant, {})
        prev_1 = series.get(key_n1, {})
        prev_2 = series.get(key_n2, {})

        anomalies: list[dict[str, Any]] = []
        categories = sorted(set(courant) | set(prev_1) | set(prev_2))

        for categorie in categories:
            montant_courant = float(courant.get(categorie, 0.0))
            base = [float(prev_1.get(categorie, 0.0)), float(prev_2.get(categorie, 0.0))]
            moyenne = (base[0] + base[1]) / 2 if base else 0.0

            if moyenne <= 0:
                continue

            variation_pct = ((montant_courant - moyenne) / moyenne) * 100
            if variation_pct < 20:
                continue

            niveau = "moyenne"
            if variation_pct >= 50:
                niveau = "haute"
            if variation_pct >= 80:
                niveau = "critique"

            anomalies.append(
                {
                    "categorie": categorie,
                    "montant_courant": round(montant_courant, 2),
                    "moyenne_n1_n2": round(moyenne, 2),
                    "variation_pct": round(variation_pct, 1),
                    "niveau": niveau,
                    "recommandation": (
                        f"Verifier les postes '{categorie}' et fixer une limite hebdomadaire."
                    ),
                }
            )

        anomalies.sort(key=lambda a: a["variation_pct"], reverse=True)

        resume_ia = self._generer_resume_ia(anomalies[:5], key_courant)

        return {
            "mois_reference": key_courant,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "resume_ia": resume_ia.get("resume", "Aucune anomalie notable."),
            "recommandations_ia": resume_ia.get("recommandations", []),
            "series_mensuelles": {
                "courant": courant,
                "n_1": prev_1,
                "n_2": prev_2,
            },
        }

    def _generer_resume_ia(self, anomalies: list[dict[str, Any]], mois_ref: str) -> dict[str, Any]:
        """Genere un resume IA court pour le widget dashboard."""
        if not anomalies:
            return {
                "resume": "Aucune derive financiere detectee sur les categories suivies.",
                "recommandations": ["Maintenir le rythme actuel et suivre la tendance chaque semaine."],
            }

        prompt = (
            f"Mois de reference: {mois_ref}.\n"
            f"Anomalies detectees: {anomalies}.\n"
            "Retourne uniquement du JSON: {resume, recommandations[]} "
            "avec un ton concret et actionnable."
        )

        parsed = self.call_with_json_parsing_sync(
            prompt=prompt,
            response_model=ResumeAnomaliesIA,
            system_prompt=(
                "Tu es un conseiller budget familial pragmatique. "
                "Propose des actions simples, mesurables, en francais."
            ),
            max_tokens=500,
            use_cache=True,
        )

        if parsed is None:
            top = anomalies[0]
            return {
                "resume": (
                    "Derive budget detectee: "
                    f"{top['categorie']} est a +{top['variation_pct']}% vs moyenne N-1/N-2."
                ),
                "recommandations": [
                    "Definir un plafond hebdomadaire par categorie",
                    "Programmer un point budget en milieu de mois",
                    "Verifier les depenses impulsives de la categorie la plus en hausse",
                ],
            }

        return {"resume": parsed.resume, "recommandations": parsed.recommandations}


@service_factory("anomalies_financieres", tags={"dashboard", "budget", "ia"})
def obtenir_service_anomalies_financieres() -> ServiceAnomaliesFinancieres:
    """Factory singleton du service anomalies financieres."""
    return ServiceAnomaliesFinancieres()


obtenir_service_anomalies_financieres = obtenir_service_anomalies_financieres
