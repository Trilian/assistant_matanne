"""

Service de bilan mensuel IA.



Agrège les données du mois écoulé (dépenses, repas, activités, entretien)

et génère un résumé narratif via Mistral AI.

"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from decimal import Decimal

from src.core.ai import obtenir_client_ia
from src.core.db import obtenir_contexte_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BilanMensuelService(BaseAIService):
    """Génère le bilan mensuel IA de la famille."""

    def __init__(self) -> None:

        super().__init__(
            client=obtenir_client_ia(),
            cache_prefix="bilan_mensuel",
            default_ttl=3600 * 6,  # 6h — données quasi-statiques en cours de mois
            service_name="bilan_mensuel",
        )

    def _collecter_donnees(self, debut: date, fin: date) -> dict:
        """Collecte les données brutes du mois."""

        from src.core.models.famille import ActiviteFamille
        from src.core.models.finances import Depense
        from src.core.models.habitat import TacheEntretien
        from src.core.models.planning import Repas

        with obtenir_contexte_db() as session:
            # Dépenses par catégorie

            depenses = (
                session.query(Depense).filter(Depense.date >= debut, Depense.date <= fin).all()
            )

            total_depenses = sum(float(d.montant) for d in depenses)

            par_categorie: dict[str, float] = defaultdict(float)

            for d in depenses:
                par_categorie[d.categorie] += float(d.montant)

            # Repas planifiés

            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= debut, Repas.date_repas <= fin)
                .all()
            )

            types_repas: dict[str, int] = defaultdict(int)

            for r in repas:
                types_repas[r.type_repas] += 1

            # Activités famille

            activites = (
                session.query(ActiviteFamille)
                .filter(
                    ActiviteFamille.date_prevue >= debut,
                    ActiviteFamille.date_prevue <= fin,
                )
                .all()
            )

            # Tâches entretien complétées

            taches_faites = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.fait.is_(True),
                    TacheEntretien.prochaine_fois >= debut,
                    TacheEntretien.prochaine_fois <= fin,
                )
                .count()
            )

            taches_retard = (
                session.query(TacheEntretien)
                .filter(
                    TacheEntretien.fait.is_(False),
                    TacheEntretien.prochaine_fois < date.today(),
                )
                .count()
            )

        return {
            "periode": f"{debut.isoformat()} → {fin.isoformat()}",
            "depenses": {
                "total": round(total_depenses, 2),
                "nb_transactions": len(depenses),
                "par_categorie": dict(sorted(par_categorie.items(), key=lambda x: -x[1])),
            },
            "repas": {
                "total_planifies": len(repas),
                "repartition": dict(types_repas),
            },
            "activites": {
                "total": len(activites),
                "noms": [a.nom for a in activites[:10]],
            },
            "entretien": {
                "taches_completees": taches_faites,
                "taches_en_retard": taches_retard,
            },
        }

    async def generer_bilan(self, mois: str | None = None) -> dict:
        """

        Génère le bilan mensuel complet avec synthèse IA.



        Args:

            mois: Mois au format YYYY-MM (défaut: mois courant).



        Returns:

            Dict avec données + texte de synthèse IA.

        """

        import calendar

        if mois:
            annee, num_mois = int(mois[:4]), int(mois[5:7])

        else:
            today = date.today()

            annee, num_mois = today.year, today.month

        dernier_jour = calendar.monthrange(annee, num_mois)[1]

        debut = date(annee, num_mois, 1)

        fin = date(annee, num_mois, dernier_jour)

        donnees = self._collecter_donnees(debut, fin)

        # Générer le résumé IA

        prompt = self._construire_prompt(donnees, debut)

        synthese = await self.call_with_cache(
            prompt=prompt,
            system_prompt=(
                "Tu es un assistant familial bienveillant. "
                "Génère un bilan mensuel concis, positif et constructif en français. "
                "Sois précis sur les chiffres, donne 2-3 points forts et 1-2 axes d'amélioration. "
                "Limite ta réponse à 200 mots."
            ),
            max_tokens=400,
            category="bilan_mensuel",
        )

        return {
            "mois": f"{annee}-{num_mois:02d}",
            "donnees": donnees,
            "synthese_ia": synthese or "Synthèse indisponible (quota IA atteint).",
        }

    def _construire_prompt(self, donnees: dict, debut: date) -> str:

        mois_fr = debut.strftime("%B %Y")

        d = donnees

        lignes = [
            f"Bilan familial du mois de {mois_fr} :",
            f"- Dépenses totales : {d['depenses']['total']} €",
            f"- Catégories principales : {', '.join(list(d['depenses']['par_categorie'].keys())[:3])}",
            f"- Repas planifiés : {d['repas']['total_planifies']}",
            f"- Activités réalisées : {d['activites']['total']}",
            f"- Tâches entretien complétées : {d['entretien']['taches_completees']}",
            f"- Tâches entretien en retard : {d['entretien']['taches_en_retard']}",
        ]

        if d["activites"]["noms"]:
            lignes.append(f"- Activités notables : {', '.join(d['activites']['noms'][:5])}")

        return "\n".join(lignes)


@service_factory("bilan_mensuel")
def obtenir_bilan_mensuel_service() -> BilanMensuelService:

    return BilanMensuelService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────

obtenir_bilan_mensuel_service = obtenir_bilan_mensuel_service  # alias rétrocompatibilité
