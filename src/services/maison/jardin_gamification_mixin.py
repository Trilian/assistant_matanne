"""
Mixin Gamification Jardin - Badges, streaks, autonomie alimentaire.

Fonctionnalités:
- Système de badges avec conditions
- Calcul des streaks d'activité
- Calcul d'autonomie alimentaire
- Génération automatique des tâches
- Planning et prévisions de récoltes
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from src.core.models import GardenItem

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


class JardinGamificationMixin:
    """Mixin ajoutant gamification et tâches au JardinService."""

    _catalogue_cache: dict | None = None

    # ─────────────────────────────────────────────────────────
    # CATALOGUE PLANTES
    # ─────────────────────────────────────────────────────────

    def charger_catalogue_plantes(self) -> dict:
        """Charge le catalogue des plantes depuis le fichier JSON."""
        if self._catalogue_cache is not None:
            return self._catalogue_cache

        try:
            catalogue_path = (
                Path(__file__).parent.parent.parent.parent / "data" / "catalogue_jardin.json"
            )
            if catalogue_path.exists():
                with open(catalogue_path, encoding="utf-8") as f:
                    self._catalogue_cache = json.load(f)
                    return self._catalogue_cache
        except Exception as e:
            logger.error(f"Erreur chargement catalogue: {e}")

        # Catalogue minimal par défaut
        self._catalogue_cache = self._catalogue_defaut()
        return self._catalogue_cache

    def _catalogue_defaut(self) -> dict:
        """Retourne le catalogue par défaut."""
        return {
            "plantes": {
                "tomate": {
                    "nom": "Tomate",
                    "emoji": "🍅",
                    "categorie": "légume-fruit",
                    "semis_interieur": [2, 3],
                    "plantation_exterieur": [5, 6],
                    "recolte": [7, 8, 9],
                    "rendement_kg_m2": 4,
                    "besoin_eau": "moyen",
                    "exposition": "soleil",
                },
                "courgette": {
                    "nom": "Courgette",
                    "emoji": "🥒",
                    "categorie": "légume-fruit",
                    "semis_interieur": [3, 4],
                    "plantation_exterieur": [5, 6],
                    "recolte": [6, 7, 8, 9],
                    "rendement_kg_m2": 5,
                    "besoin_eau": "élevé",
                },
                "carotte": {
                    "nom": "Carotte",
                    "emoji": "🥕",
                    "categorie": "légume-racine",
                    "semis_direct": [3, 4, 5, 6],
                    "recolte": [6, 7, 8, 9, 10],
                    "rendement_kg_m2": 3,
                    "besoin_eau": "faible",
                },
                "salade": {
                    "nom": "Salade",
                    "emoji": "🥬",
                    "categorie": "légume-feuille",
                    "semis_direct": [3, 4, 5, 6, 7, 8],
                    "recolte": [4, 5, 6, 7, 8, 9, 10],
                    "rendement_kg_m2": 2,
                    "besoin_eau": "moyen",
                },
                "basilic": {
                    "nom": "Basilic",
                    "emoji": "🌿",
                    "categorie": "aromatique",
                    "semis_interieur": [3, 4],
                    "plantation_exterieur": [5, 6],
                    "recolte": [6, 7, 8, 9],
                    "rendement_kg_m2": 0.5,
                    "besoin_eau": "moyen",
                },
            },
            "objectifs_autonomie": {
                "legumes_fruits_kg": 150,
                "legumes_feuilles_kg": 50,
                "legumes_racines_kg": 60,
                "aromatiques_kg": 5,
            },
        }

    # ─────────────────────────────────────────────────────────
    # GÉNÉRATION AUTOMATIQUE DES TÂCHES
    # ─────────────────────────────────────────────────────────

    def generer_taches(self, plantes: list[dict], meteo: dict | None = None) -> list[dict]:
        """
        Génère automatiquement les tâches du jardin.

        Args:
            plantes: Liste des plantes (dict avec plante_id, semis_fait, plante_en_terre)
            meteo: Données météo optionnelles

        Returns:
            Liste de tâches triées par priorité
        """
        meteo = meteo or {}
        taches = []
        catalogue = self.charger_catalogue_plantes()
        aujourd_hui = date.today()
        mois = aujourd_hui.month

        # 1. Tâches liées au calendrier
        for plante_id, plante_data in catalogue.get("plantes", {}).items():
            taches.extend(self._generer_taches_calendrier(plante_id, plante_data, plantes, mois))

        # 2. Tâches d'arrosage
        taches.extend(self._generer_taches_arrosage(plantes, meteo, catalogue))

        # 3. Tâches météo
        taches.extend(self._generer_taches_meteo(plantes, meteo))

        # 4. Entretien régulier
        taches.extend(self._generer_taches_entretien(plantes, aujourd_hui))

        # Trier par priorité
        ordre_priorite = {"urgente": 0, "haute": 1, "normale": 2, "basse": 3}
        taches.sort(key=lambda t: ordre_priorite.get(t.get("priorite", "normale"), 2))

        return taches

    def _generer_taches_calendrier(
        self, plante_id: str, plante_data: dict, mes_plantes: list[dict], mois: int
    ) -> list[dict]:
        """Génère les tâches liées au calendrier de semis/plantation."""
        taches = []

        # Semis en intérieur
        if mois in plante_data.get("semis_interieur", []):
            deja_semis = any(
                p.get("plante_id") == plante_id and p.get("semis_fait") for p in mes_plantes
            )
            if not deja_semis:
                taches.append(
                    {
                        "type": "semis",
                        "titre": f"Semer {plante_data.get('nom', plante_id)} en intérieur",
                        "description": f"C'est la bonne période pour semer les {plante_data.get('nom')} en godets.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "haute"
                        if mois == plante_data.get("semis_interieur", [0])[-1]
                        else "normale",
                        "duree_min": 20,
                        "plante_id": plante_id,
                    }
                )

        # Semis direct
        if mois in plante_data.get("semis_direct", []):
            deja_semis = any(
                p.get("plante_id") == plante_id and p.get("semis_fait") for p in mes_plantes
            )
            if not deja_semis:
                taches.append(
                    {
                        "type": "semis",
                        "titre": f"Semer {plante_data.get('nom', plante_id)} en pleine terre",
                        "description": f"Semis direct possible pour les {plante_data.get('nom')}.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "normale",
                        "duree_min": 30,
                        "plante_id": plante_id,
                    }
                )

        # Plantation extérieur
        if mois in plante_data.get("plantation_exterieur", []):
            a_planter = [
                p
                for p in mes_plantes
                if p.get("plante_id") == plante_id
                and p.get("semis_fait")
                and not p.get("plante_en_terre")
            ]
            if a_planter:
                taches.append(
                    {
                        "type": "plantation",
                        "titre": f"Planter {plante_data.get('nom', plante_id)} en extérieur",
                        "description": f"Vos plants de {plante_data.get('nom')} sont prêts à être repiqués.",
                        "emoji": plante_data.get("emoji", "🌱"),
                        "priorite": "haute",
                        "duree_min": 45,
                        "plante_id": plante_id,
                    }
                )

        return taches

    def _generer_taches_arrosage(
        self, mes_plantes: list[dict], meteo: dict, catalogue: dict
    ) -> list[dict]:
        """Génère les tâches d'arrosage basées sur météo."""
        taches = []
        plantes_en_terre = [p for p in mes_plantes if p.get("plante_en_terre")]

        if plantes_en_terre and not meteo.get("pluie_prevue"):
            besoin_eau_eleve = any(
                catalogue.get("plantes", {}).get(p.get("plante_id"), {}).get("besoin_eau")
                == "élevé"
                for p in plantes_en_terre
            )

            if meteo.get("temperature", 20) > 20 or besoin_eau_eleve:
                taches.append(
                    {
                        "type": "arrosage",
                        "titre": "Arroser le potager",
                        "description": f"Température de {meteo.get('temperature')}°C. Arrosez de préférence le soir.",
                        "emoji": "💧",
                        "priorite": "urgente" if meteo.get("temperature", 0) > 28 else "haute",
                        "duree_min": 20,
                    }
                )

        return taches

    def _generer_taches_meteo(self, mes_plantes: list[dict], meteo: dict) -> list[dict]:
        """Génère les tâches liées aux alertes météo."""
        taches = []

        if meteo.get("gel_risque"):
            if any(p.get("plante_en_terre") for p in mes_plantes):
                taches.append(
                    {
                        "type": "protection",
                        "titre": "Protéger les plants du gel",
                        "description": "Risque de gel annoncé. Installez voiles d'hivernage ou rentrez les pots.",
                        "emoji": "🥶",
                        "priorite": "urgente",
                        "duree_min": 30,
                    }
                )

        return taches

    def _generer_taches_entretien(self, mes_plantes: list[dict], aujourd_hui: date) -> list[dict]:
        """Génère les tâches d'entretien régulier."""
        taches = []
        jour_semaine = aujourd_hui.weekday()
        plantes_en_terre = [p for p in mes_plantes if p.get("plante_en_terre")]

        if jour_semaine == 5 and plantes_en_terre:  # Samedi
            taches.append(
                {
                    "type": "entretien",
                    "titre": "Désherber et biner",
                    "description": "Entretien hebdomadaire: désherbage et aération du sol.",
                    "emoji": "🧹",
                    "priorite": "normale",
                    "duree_min": 45,
                }
            )

        if jour_semaine == 2:  # Mercredi
            taches.append(
                {
                    "type": "observation",
                    "titre": "Inspecter les plants",
                    "description": "Vérifiez l'état sanitaire, cherchez ravageurs et maladies.",
                    "emoji": "🔍",
                    "priorite": "normale",
                    "duree_min": 15,
                }
            )

        return taches

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
                except Exception:
                    pass

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
            except Exception:
                pass
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
