"""
Mixin Gamification Entretien - Badges, streaks, score propreté.

Fonctionnalités:
- Système de badges entretien avec conditions
- Calcul des streaks d'activité
- Score de propreté dynamique
- Génération automatique des tâches d'entretien
- Planning prévisionnel et alertes prédictives
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES GAMIFICATION
# ═══════════════════════════════════════════════════════════

BADGES_ENTRETIEN = [
    {
        "id": "premiere_tache",
        "nom": "Premier pas",
        "emoji": "🎯",
        "description": "Première tâche accomplie",
        "condition": lambda stats: stats.get("taches_accomplies", 0) >= 1,
    },
    {
        "id": "maison_nickel",
        "nom": "Maison nickel",
        "emoji": "✨",
        "description": "Score propreté ≥ 90",
        "condition": lambda stats: stats.get("score", 0) >= 90,
    },
    {
        "id": "streak_7",
        "nom": "Série de 7 jours",
        "emoji": "🔥",
        "description": "7 jours consécutifs sans retard",
        "condition": lambda stats: stats.get("streak", 0) >= 7,
    },
    {
        "id": "streak_30",
        "nom": "Mois parfait",
        "emoji": "🏆",
        "description": "30 jours consécutifs",
        "condition": lambda stats: stats.get("streak", 0) >= 30,
    },
    {
        "id": "electromenager_ok",
        "nom": "Électroménager au top",
        "emoji": "🔌",
        "description": "Tous les appareils entretenus",
        "condition": lambda stats: stats.get("electromenager_ok", False),
    },
    {
        "id": "pro_annuel",
        "nom": "Entretien pro",
        "emoji": "🔧",
        "description": "Entretien professionnel effectué",
        "condition": lambda stats: stats.get("pro_effectue", False),
    },
    {
        "id": "inventaire_complet",
        "nom": "Inventaire complet",
        "emoji": "📦",
        "description": "10+ équipements enregistrés",
        "condition": lambda stats: stats.get("nb_objets", 0) >= 10,
    },
    {
        "id": "assidu",
        "nom": "Assidu",
        "emoji": "📅",
        "description": "50+ tâches accomplies",
        "condition": lambda stats: stats.get("taches_accomplies", 0) >= 50,
    },
]


# ═══════════════════════════════════════════════════════════
# MIXIN GAMIFICATION ENTRETIEN
# ═══════════════════════════════════════════════════════════


class EntretienGamificationMixin:
    """Mixin ajoutant gamification et tâches au EntretienService."""

    _catalogue_cache: dict[str, Any] | None = None

    # ─────────────────────────────────────────────────────────
    # CATALOGUE ENTRETIEN
    # ─────────────────────────────────────────────────────────

    def charger_catalogue_entretien(self) -> dict:
        """Charge le catalogue d'entretien depuis le fichier JSON."""
        if self._catalogue_cache is not None:
            return self._catalogue_cache

        try:
            chemin = Path(__file__).parent.parent.parent / "data" / "entretien_catalogue.json"
            if chemin.exists():
                with open(chemin, encoding="utf-8") as f:
                    self._catalogue_cache = json.load(f)
                    return self._catalogue_cache
        except Exception as e:
            logger.error(f"Erreur chargement catalogue entretien: {e}")

        self._catalogue_cache = self._catalogue_entretien_defaut()
        return self._catalogue_cache

    def _catalogue_entretien_defaut(self) -> dict:
        """Retourne le catalogue d'entretien par défaut."""
        return {
            "categories": {
                "electromenager": {
                    "icon": "🔌",
                    "couleur": "#3498db",
                    "objets": {
                        "refrigerateur": {
                            "nom": "Réfrigérateur",
                            "taches": [
                                {"nom": "Nettoyer joints", "frequence_jours": 30, "duree_min": 10},
                                {
                                    "nom": "Nettoyer intérieur",
                                    "frequence_jours": 60,
                                    "duree_min": 30,
                                },
                                {
                                    "nom": "Dégivrer congélateur",
                                    "frequence_jours": 180,
                                    "duree_min": 45,
                                },
                            ],
                        },
                        "lave_linge": {
                            "nom": "Lave-linge",
                            "taches": [
                                {"nom": "Nettoyer filtre", "frequence_jours": 30, "duree_min": 15},
                                {
                                    "nom": "Cycle tambour vide 90°",
                                    "frequence_jours": 30,
                                    "duree_min": 5,
                                },
                                {
                                    "nom": "Nettoyer bac lessive",
                                    "frequence_jours": 14,
                                    "duree_min": 10,
                                },
                            ],
                        },
                    },
                },
                "sanitaires": {
                    "icon": "🚿",
                    "couleur": "#1abc9c",
                    "objets": {
                        "douche": {
                            "nom": "Douche",
                            "taches": [
                                {
                                    "nom": "Détartrer pommeau",
                                    "frequence_jours": 30,
                                    "duree_min": 20,
                                },
                                {"nom": "Nettoyer joints", "frequence_jours": 14, "duree_min": 15},
                            ],
                        },
                    },
                },
                "surfaces": {
                    "icon": "🧹",
                    "couleur": "#e74c3c",
                    "objets": {
                        "sols": {
                            "nom": "Sols",
                            "taches": [
                                {"nom": "Aspirer", "frequence_jours": 3, "duree_min": 20},
                                {"nom": "Laver", "frequence_jours": 7, "duree_min": 30},
                            ],
                        },
                    },
                },
            },
        }

    # ─────────────────────────────────────────────────────────
    # GÉNÉRATION AUTOMATIQUE DES TÂCHES
    # ─────────────────────────────────────────────────────────

    def generer_taches(self, objets: list[dict], historique: list[dict]) -> list[dict]:
        """
        Génère automatiquement les tâches d'entretien.

        Args:
            objets: Liste des objets/équipements possédés
            historique: Historique des tâches accomplies

        Returns:
            Liste de tâches triées par priorité
        """
        taches: list[dict] = []
        catalogue = self.charger_catalogue_entretien()
        mois_actuel = datetime.now().month
        aujourd_hui = date.today()

        # Index historique par objet/tache
        historique_index = self._construire_index_historique(historique)

        # Parcourir les objets
        for mon_objet in objets:
            objet_id = mon_objet.get("objet_id")
            categorie_id = mon_objet.get("categorie_id")
            piece = mon_objet.get("piece", "")

            categorie_data = catalogue.get("categories", {}).get(categorie_id, {})
            objet_data = categorie_data.get("objets", {}).get(objet_id, {})

            if not objet_data:
                continue

            nom_objet = objet_data.get("nom", objet_id)
            icon_cat = categorie_data.get("icon", "📦")

            for tache_def in objet_data.get("taches", []):
                tache = self._evaluer_tache(
                    tache_def,
                    objet_id,
                    nom_objet,
                    categorie_id,
                    icon_cat,
                    piece,
                    mois_actuel,
                    aujourd_hui,
                    historique_index,
                )
                if tache:
                    taches.append(tache)

        # Trier par priorité puis par retard
        ordre = {"urgente": 0, "haute": 1, "moyenne": 2, "basse": 3}
        taches.sort(
            key=lambda t: (ordre.get(t.get("priorite", "moyenne"), 2), -t.get("retard_jours", 0))
        )

        return taches

    def _construire_index_historique(self, historique: list[dict]) -> dict[str, date]:
        """Construit un index dates dernière exécution par tâche."""
        index: dict[str, date] = {}
        for h in historique:
            cle = f"{h.get('objet_id')}_{h.get('tache_nom')}"
            date_h = h.get("date")
            if date_h:
                try:
                    d = datetime.fromisoformat(date_h).date() if isinstance(date_h, str) else date_h
                    if cle not in index or d > index[cle]:
                        index[cle] = d
                except Exception:
                    pass
        return index

    def _evaluer_tache(
        self,
        tache_def: dict,
        objet_id: str,
        nom_objet: str,
        categorie_id: str,
        icon_cat: str,
        piece: str,
        mois_actuel: int,
        aujourd_hui: date,
        historique_index: dict[str, date],
    ) -> dict | None:
        """Évalue si une tâche est due et la retourne si oui."""
        tache_nom = tache_def.get("nom")
        frequence_jours = tache_def.get("frequence_jours", 30)
        duree_min = tache_def.get("duree_min", 15)
        description = tache_def.get("description", "")
        est_pro = tache_def.get("pro", False)
        obligatoire = tache_def.get("obligatoire", False)
        saisonnier = tache_def.get("saisonnier", [])
        mois_specifiques = tache_def.get("mois", [])

        # Vérifier saisonnalité
        if saisonnier and mois_actuel not in saisonnier:
            return None
        if mois_specifiques and mois_actuel not in mois_specifiques:
            return None

        # Calculer si tâche due
        cle = f"{objet_id}_{tache_nom}"
        derniere_fois = historique_index.get(cle)

        if derniere_fois:
            jours_depuis = (aujourd_hui - derniere_fois).days
            retard_jours = max(0, jours_depuis - frequence_jours)
            est_due = jours_depuis >= frequence_jours
        else:
            est_due = True
            jours_depuis = frequence_jours + 30
            retard_jours = 30

        if not est_due:
            return None

        # Déterminer priorité
        if retard_jours > frequence_jours:
            priorite = "urgente"
        elif retard_jours > frequence_jours // 2:
            priorite = "haute"
        elif obligatoire:
            priorite = "haute"
        else:
            priorite = "moyenne"

        return {
            "objet_id": objet_id,
            "objet_nom": nom_objet,
            "categorie_id": categorie_id,
            "categorie_icon": icon_cat,
            "tache_nom": tache_nom,
            "description": description,
            "duree_min": duree_min,
            "frequence_jours": frequence_jours,
            "piece": piece,
            "priorite": priorite,
            "retard_jours": retard_jours,
            "derniere_fois": derniere_fois.isoformat() if derniere_fois else None,
            "est_pro": est_pro,
            "obligatoire": obligatoire,
        }

    # ─────────────────────────────────────────────────────────
    # SCORE DE PROPRETÉ
    # ─────────────────────────────────────────────────────────

    def calculer_score_proprete(self, objets: list[dict], historique: list[dict]) -> dict:
        """Calcule un score de propreté/entretien global."""
        if not objets:
            return {"score": 100, "niveau": "Parfait", "couleur": "#27ae60"}

        taches = self.generer_taches(objets, historique)

        urgentes = len([t for t in taches if t.get("priorite") == "urgente"])
        hautes = len([t for t in taches if t.get("priorite") == "haute"])

        penalite = (urgentes * 15) + (hautes * 5) + (len(taches) * 2)
        score = max(0, 100 - penalite)

        if score >= 90:
            niveau, couleur = "Excellent", "#27ae60"
        elif score >= 70:
            niveau, couleur = "Bon", "#3498db"
        elif score >= 50:
            niveau, couleur = "Moyen", "#f39c12"
        else:
            niveau, couleur = "À améliorer", "#e74c3c"

        return {
            "score": score,
            "niveau": niveau,
            "couleur": couleur,
            "taches_total": len(taches),
            "urgentes": urgentes,
            "hautes": hautes,
        }

    # ─────────────────────────────────────────────────────────
    # GAMIFICATION - BADGES & STREAK
    # ─────────────────────────────────────────────────────────

    def calculer_streak(self, historique: list[dict]) -> int:
        """Calcule le nombre de jours consécutifs avec tâches accomplies."""
        if not historique:
            return 0

        dates_accomplies: set[date] = set()
        for h in historique:
            date_str = h.get("date")
            if date_str:
                try:
                    d = (
                        datetime.fromisoformat(date_str).date()
                        if isinstance(date_str, str)
                        else date_str
                    )
                    dates_accomplies.add(d)
                except Exception:
                    pass

        if not dates_accomplies:
            return 0

        streak = 0
        check_date = date.today()
        while check_date in dates_accomplies:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def calculer_stats_globales(self, objets: list[dict], historique: list[dict]) -> dict:
        """Calcule les statistiques globales pour badges."""
        score_data = self.calculer_score_proprete(objets, historique)
        streak = self.calculer_streak(historique)

        taches = self.generer_taches(objets, historique)
        electro_urgentes = [
            t
            for t in taches
            if t.get("categorie_id") == "electromenager"
            and t.get("priorite") in ["urgente", "haute"]
        ]

        pro_fait = any(h.get("est_pro") for h in historique)

        return {
            "score": score_data["score"],
            "streak": streak,
            "taches_accomplies": len(historique),
            "nb_objets": len(objets),
            "electromenager_ok": len(electro_urgentes) == 0,
            "pro_effectue": pro_fait,
            "taches_urgentes": score_data["urgentes"],
            "taches_hautes": score_data["hautes"],
        }

    def obtenir_badges(self, stats: dict) -> list[dict]:
        """Retourne les badges obtenus avec leurs définitions."""
        obtenus = []
        for badge_def in BADGES_ENTRETIEN:
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
    # PLANNING PRÉVISIONNEL
    # ─────────────────────────────────────────────────────────

    def generer_planning_previsionnel(
        self, objets: list[dict], historique: list[dict], horizon_jours: int = 60
    ) -> list[dict]:
        """Génère le planning prévisionnel des tâches futures."""
        planning: list[dict] = []
        catalogue = self.charger_catalogue_entretien()
        aujourd_hui = date.today()
        historique_index = self._construire_index_historique(historique)

        for mon_objet in objets:
            objet_id = mon_objet.get("objet_id")
            categorie_id = mon_objet.get("categorie_id")
            piece = mon_objet.get("piece", "")

            categorie_data = catalogue.get("categories", {}).get(categorie_id, {})
            objet_data = categorie_data.get("objets", {}).get(objet_id, {})

            if not objet_data:
                continue

            nom_objet = objet_data.get("nom", objet_id)

            for tache_def in objet_data.get("taches", []):
                tache_nom = tache_def.get("nom")
                frequence = tache_def.get("frequence_jours", 30)
                duree_min = tache_def.get("duree_min", 15)

                cle = f"{objet_id}_{tache_nom}"
                derniere_fois = historique_index.get(cle)

                if derniere_fois:
                    prochaine_date = derniere_fois + timedelta(days=frequence)
                else:
                    prochaine_date = aujourd_hui + timedelta(days=7)

                jours_restants = (prochaine_date - aujourd_hui).days

                if 0 < jours_restants <= horizon_jours:
                    planning.append(
                        {
                            "objet_id": objet_id,
                            "objet_nom": nom_objet,
                            "tache_nom": tache_nom,
                            "date_prevue": prochaine_date.strftime("%d/%m"),
                            "jours_restants": jours_restants,
                            "piece": piece,
                            "duree_min": duree_min,
                            "frequence_jours": frequence,
                        }
                    )

        planning.sort(key=lambda t: t["jours_restants"])
        return planning

    def generer_alertes_predictives(self, objets: list[dict], historique: list[dict]) -> list[dict]:
        """Génère les alertes pour les tâches arrivant dans 14 jours."""
        planning = self.generer_planning_previsionnel(objets, historique, horizon_jours=14)
        return planning[:5]
