"""
Mixin Planning Jardin - Autonomie alimentaire, planning et prévisions.

Fonctionnalités:
- Calcul d'autonomie alimentaire
- Statistiques globales du jardin
- Planning prévisionnel saisonnier
- Prévisions de récoltes
"""

import logging
from datetime import date

from .jardin_taches_mixin import JardinTachesMixin

logger = logging.getLogger(__name__)

NOMS_MOIS = [
    "",
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]


class JardinPlanningMixin(JardinTachesMixin):
    """Mixin ajoutant autonomie alimentaire et planning au JardinService.

    Hérite de JardinTachesMixin (qui hérite de JardinCatalogueMixin),
    fournissant l'ensemble des fonctionnalités: catalogue, tâches,
    autonomie alimentaire et planning.
    """

    # ─────────────────────────────────────────────────────────
    # CALCUL AUTONOMIE ALIMENTAIRE
    # ─────────────────────────────────────────────────────────

    def calculer_autonomie(self, plantes: list[dict], recoltes: list[dict]) -> dict:
        """
        Calcule les métriques d'autonomie alimentaire.

        Args:
            plantes: Liste des plantes cultivées
            recoltes: Liste des récoltes enregistrées

        Returns:
            Dict avec pourcentages d'autonomie et détails
        """
        catalogue = self.charger_catalogue_plantes()
        objectifs = catalogue.get("objectifs_autonomie", {})
        besoins_totaux = sum(objectifs.values()) or 265

        production_prevue = 0
        par_categorie: dict[str, dict] = {}

        for ma_plante in plantes:
            plante_id = ma_plante.get("plante_id")
            plante_data = catalogue.get("plantes", {}).get(plante_id, {})

            surface = ma_plante.get("surface_m2", 1)
            rendement = plante_data.get("rendement_kg_m2", 2)
            categorie = plante_data.get("categorie", "autre")

            prevu = surface * rendement
            production_prevue += prevu

            if categorie not in par_categorie:
                par_categorie[categorie] = {"prevu": 0, "recolte": 0, "besoin": 0}
            par_categorie[categorie]["prevu"] += prevu

        mapping_cat = {
            "légume-fruit": "legumes_fruits_kg",
            "légume-feuille": "legumes_feuilles_kg",
            "légume-racine": "legumes_racines_kg",
            "aromatique": "aromatiques_kg",
        }

        for cat, obj_key in mapping_cat.items():
            if cat in par_categorie:
                par_categorie[cat]["besoin"] = objectifs.get(obj_key, 50)

        production_reelle = sum(r.get("quantite_kg", 0) for r in recoltes)

        for cat in par_categorie:
            besoin = par_categorie[cat]["besoin"] or 50
            prevu = par_categorie[cat]["prevu"]
            par_categorie[cat]["couverture"] = min(100, round(prevu / besoin * 100))

        return {
            "production_prevue_kg": round(production_prevue, 1),
            "production_reelle_kg": round(production_reelle, 1),
            "besoins_kg": besoins_totaux,
            "pourcentage_prevu": min(100, round(production_prevue / besoins_totaux * 100)),
            "pourcentage_reel": min(100, round(production_reelle / besoins_totaux * 100)),
            "par_categorie": par_categorie,
        }

    # ─────────────────────────────────────────────────────────
    # STATISTIQUES GLOBALES
    # ─────────────────────────────────────────────────────────

    def calculer_stats(
        self,
        plantes: list[dict],
        recoltes: list[dict],
        activites: list[dict] | None = None,
    ) -> dict:
        """Calcule les statistiques globales du jardin."""
        autonomie = self.calculer_autonomie(plantes, recoltes)

        semis_total = len([p for p in plantes if p.get("semis_fait")])
        nb_plantes = len(plantes)
        recoltes_total = len(recoltes)
        varietes_uniques = len(set(p.get("plante_id") for p in plantes))

        pratiques_eco = sum(
            [
                1 if any(p.get("compost") for p in plantes) else 0,
                1 if any(p.get("recup_eau") for p in plantes) else 0,
            ]
        )

        return {
            "semis_total": semis_total,
            "nb_plantes": nb_plantes,
            "recoltes_total": recoltes_total,
            "varietes_uniques": varietes_uniques,
            "autonomie_pourcent": autonomie["pourcentage_reel"],
            "autonomie_prevu_pourcent": autonomie["pourcentage_prevu"],
            "production_kg": autonomie["production_reelle_kg"],
            "pratiques_eco": pratiques_eco,
        }

    # ─────────────────────────────────────────────────────────
    # PLANNING ET PRÉVISIONS
    # ─────────────────────────────────────────────────────────

    def generer_planning(self, plantes: list[dict], horizon_mois: int = 6) -> list[dict]:
        """Génère le planning prévisionnel des activités."""
        planning = []
        catalogue = self.charger_catalogue_plantes()
        mois_actuel = date.today().month

        for ma_plante in plantes:
            plante_id = ma_plante.get("plante_id")
            plante_data = catalogue.get("plantes", {}).get(plante_id, {})

            if not plante_data:
                continue

            nom = plante_data.get("nom", plante_id)
            emoji = plante_data.get("emoji", "🌱")

            if not ma_plante.get("plante_en_terre"):
                mois_plantation = plante_data.get("plantation_exterieur", [])
                prochain = self._trouver_prochain_mois(mois_actuel, mois_plantation, horizon_mois)
                if prochain:
                    planning.append(
                        {
                            "type": "plantation",
                            "titre": f"Planter {nom}",
                            "emoji": emoji,
                            "mois": prochain,
                            "mois_label": NOMS_MOIS[prochain] if 1 <= prochain <= 12 else "",
                        }
                    )

            if ma_plante.get("plante_en_terre"):
                mois_recolte = plante_data.get("recolte", [])
                prochain = self._trouver_prochain_mois(mois_actuel, mois_recolte, horizon_mois)
                if prochain:
                    planning.append(
                        {
                            "type": "recolte",
                            "titre": f"Récolter {nom}",
                            "emoji": emoji,
                            "mois": prochain,
                            "mois_label": NOMS_MOIS[prochain] if 1 <= prochain <= 12 else "",
                        }
                    )

        planning.sort(key=lambda p: p["mois"])
        return planning

    def generer_previsions_recoltes(self, plantes: list[dict]) -> list[dict]:
        """Génère les prévisions de récoltes."""
        previsions = []
        catalogue = self.charger_catalogue_plantes()
        mois_actuel = date.today().month

        plantes_en_terre = [p for p in plantes if p.get("plante_en_terre")]

        for ma_plante in plantes_en_terre:
            plante_id = ma_plante.get("plante_id")
            plante_data = catalogue.get("plantes", {}).get(plante_id, {})

            if not plante_data:
                continue

            mois_recolte = plante_data.get("recolte", [])

            if mois_actuel in mois_recolte or (mois_actuel % 12 + 1) in mois_recolte:
                surface = ma_plante.get("surface_m2", 1)
                rendement = plante_data.get("rendement_kg_m2", 2)

                previsions.append(
                    {
                        "plante_id": plante_id,
                        "nom": plante_data.get("nom", plante_id),
                        "emoji": plante_data.get("emoji", "🌱"),
                        "quantite_prevue_kg": round(surface * rendement, 1),
                        "mois_recolte": mois_recolte,
                        "periode": "Bientôt" if mois_actuel in mois_recolte else "Mois prochain",
                    }
                )

        return previsions

    def _trouver_prochain_mois(
        self, mois_actuel: int, mois_possibles: list[int], horizon: int
    ) -> int | None:
        """Trouve le prochain mois dans la liste."""
        if not mois_possibles:
            return None

        for offset in range(horizon):
            mois_check = ((mois_actuel - 1 + offset) % 12) + 1
            if mois_check in mois_possibles:
                return mois_check

        return None
