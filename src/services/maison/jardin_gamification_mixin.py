"""
Mixin Gamification Jardin - Badges, streaks, autonomie alimentaire.

Fonctionnalités:
- Système de badges avec conditions
- Calcul des streaks d'activité
- Calcul d'autonomie alimentaire
- Planning et prévisions de récoltes

Sous-mixins (séparés pour modularité):
- JardinCatalogueMixin (jardin_catalogue_mixin.py): catalogue plantes
- JardinTachesMixin (jardin_taches_mixin.py): génération des tâches
"""

import logging
from datetime import date, datetime, timedelta

from .jardin_taches_mixin import JardinTachesMixin

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES GAMIFICATION
# ═══════════════════════════════════════════════════════════

BADGES_JARDIN = [
    {
        "id": "premier_semis",
        "nom": "Premier Semis",
        "emoji": "🌱",
        "description": "Premier semis effectué",
        "condition": lambda stats: stats.get("semis_total", 0) >= 1,
    },
    {
        "id": "pouce_vert",
        "nom": "Pouce Vert",
        "emoji": "👍",
        "description": "10+ plantes cultivées",
        "condition": lambda stats: stats.get("nb_plantes", 0) >= 10,
    },
    {
        "id": "premiere_recolte",
        "nom": "Première Récolte",
        "emoji": "🥕",
        "description": "Première récolte enregistrée",
        "condition": lambda stats: stats.get("recoltes_total", 0) >= 1,
    },
    {
        "id": "jardinier_assidu",
        "nom": "Jardinier Assidu",
        "emoji": "🔥",
        "description": "7 jours consécutifs au jardin",
        "condition": lambda stats: stats.get("streak", 0) >= 7,
    },
    {
        "id": "polyvalent",
        "nom": "Polyvalent",
        "emoji": "🌈",
        "description": "5+ variétés différentes",
        "condition": lambda stats: stats.get("varietes_uniques", 0) >= 5,
    },
    {
        "id": "autosuffisant_25",
        "nom": "Vers l'autonomie",
        "emoji": "🏡",
        "description": "25% d'autonomie atteint",
        "condition": lambda stats: stats.get("autonomie_pourcent", 0) >= 25,
    },
    {
        "id": "autosuffisant_50",
        "nom": "Semi-autonome",
        "emoji": "🌾",
        "description": "50% d'autonomie atteint",
        "condition": lambda stats: stats.get("autonomie_pourcent", 0) >= 50,
    },
    {
        "id": "eco_expert",
        "nom": "Éco-Expert",
        "emoji": "♻️",
        "description": "Compost et récupération d'eau",
        "condition": lambda stats: stats.get("pratiques_eco", 0) >= 2,
    },
]

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


# ═══════════════════════════════════════════════════════════
# MIXIN GAMIFICATION
# ═══════════════════════════════════════════════════════════


class JardinGamificationMixin(JardinTachesMixin):
    """Mixin ajoutant gamification, autonomie et planning au JardinService.

    Hérite de JardinTachesMixin (qui hérite de JardinCatalogueMixin),
    fournissant l'ensemble des fonctionnalités: catalogue, tâches,
    gamification, autonomie alimentaire et planning.
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

        # Mapper besoins par catégorie
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
    # GAMIFICATION - BADGES & STREAK
    # ─────────────────────────────────────────────────────────

    def calculer_streak(self, activites: list[dict]) -> int:
        """Calcule le nombre de jours consécutifs d'activité jardin."""
        if not activites:
            return 0

        dates_actives: set[date] = set()
        for a in activites:
            date_str = a.get("date")
            if date_str:
                try:
                    d = (
                        datetime.fromisoformat(date_str).date()
                        if isinstance(date_str, str)
                        else date_str
                    )
                    dates_actives.add(d)
                except Exception as e:
                    logger.debug("Date parsing ignorée: %s", e)

        if not dates_actives:
            return 0

        streak = 0
        check_date = date.today()

        while check_date in dates_actives:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def calculer_stats(
        self,
        plantes: list[dict],
        recoltes: list[dict],
        activites: list[dict] | None = None,
    ) -> dict:
        """Calcule les statistiques globales pour badges."""
        activites = activites or []
        autonomie = self.calculer_autonomie(plantes, recoltes)
        streak = self.calculer_streak(activites + recoltes)

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
            "streak": streak,
            "autonomie_pourcent": autonomie["pourcentage_reel"],
            "autonomie_prevu_pourcent": autonomie["pourcentage_prevu"],
            "production_kg": autonomie["production_reelle_kg"],
            "pratiques_eco": pratiques_eco,
        }

    def obtenir_badges(self, stats: dict) -> list[dict]:
        """Retourne les badges obtenus avec leurs définitions."""
        obtenus = []
        for badge_def in BADGES_JARDIN:
            try:
                if badge_def["condition"](stats):
                    obtenus.append(
                        {
                            "id": badge_def["id"],
                            "nom": badge_def["nom"],
                            "emoji": badge_def["emoji"],
                            "description": badge_def["description"],
                        }
                    )
            except Exception as e:
                logger.debug("Évaluation badge ignorée: %s", e)
        return obtenus

    def obtenir_ids_badges(self, stats: dict) -> list[str]:
        """Retourne la liste des IDs de badges obtenus."""
        return [b["id"] for b in self.obtenir_badges(stats)]

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

            # Prochaine plantation
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

            # Prochaine récolte
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
