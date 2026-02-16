"""
Entretien - Logique métier.

Génération automatique des tâches, calcul du score propreté, badges et prédictions.
"""

import logging
from datetime import date, datetime, timedelta

from .data import charger_catalogue_entretien

logger = logging.getLogger(__name__)


# =============================================================================
# BADGES GAMIFICATION
# =============================================================================

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


# =============================================================================
# GÉNÉRATION AUTOMATIQUE DES TÂCHES
# =============================================================================


def generer_taches_entretien(mes_objets: list[dict], historique: list[dict]) -> list[dict]:
    """
    Génère automatiquement les tâches d'entretien basées sur:
    - Les objets/équipements possédés
    - L'historique des tâches effectuées
    - Le calendrier (saison)
    """
    taches = []
    catalogue = charger_catalogue_entretien()
    mois_actuel = datetime.now().month
    aujourd_hui = date.today()

    # Construire un index historique par objet/tâche
    historique_index = {}
    for h in historique:
        cle = f"{h.get('objet_id')}_{h.get('tache_nom')}"
        date_h = h.get("date")
        if date_h:
            try:
                d = datetime.fromisoformat(date_h).date() if isinstance(date_h, str) else date_h
                if cle not in historique_index or d > historique_index[cle]:
                    historique_index[cle] = d
            except:
                pass

    # Parcourir mes objets
    for mon_objet in mes_objets:
        objet_id = mon_objet.get("objet_id")
        categorie_id = mon_objet.get("categorie_id")
        piece = mon_objet.get("piece", "")
        date_achat = mon_objet.get("date_achat")

        # Trouver la définition dans le catalogue
        categorie_data = catalogue.get("categories", {}).get(categorie_id, {})
        objet_data = categorie_data.get("objets", {}).get(objet_id, {})

        if not objet_data:
            continue

        nom_objet = objet_data.get("nom", objet_id)
        icon_cat = categorie_data.get("icon", "📦")
        couleur_cat = categorie_data.get("couleur", "#95a5a6")

        # Parcourir les tâches de cet objet
        for tache_def in objet_data.get("taches", []):
            tache_nom = tache_def.get("nom")
            frequence_jours = tache_def.get("frequence_jours", 30)
            duree_min = tache_def.get("duree_min", 15)
            description = tache_def.get("description", "")
            est_pro = tache_def.get("pro", False)
            obligatoire = tache_def.get("obligatoire", False)
            saisonnier = tache_def.get("saisonnier", [])
            mois_specifiques = tache_def.get("mois", [])

            # Vérifier si saisonnier ou mois spécifique
            if saisonnier and mois_actuel not in saisonnier:
                continue
            if mois_specifiques and mois_actuel not in mois_specifiques:
                continue

            # Calculer si la tâche est due
            cle_historique = f"{objet_id}_{tache_nom}"
            derniere_fois = historique_index.get(cle_historique)

            jours_depuis = None
            retard_jours = 0

            if derniere_fois:
                jours_depuis = (aujourd_hui - derniere_fois).days
                retard_jours = max(0, jours_depuis - frequence_jours)
                est_due = jours_depuis >= frequence_jours
            else:
                # Jamais fait - considérer comme dû
                est_due = True
                jours_depuis = frequence_jours + 30  # Simuler un retard
                retard_jours = 30

            if est_due:
                # Déterminer la priorité
                if retard_jours > frequence_jours:
                    priorite = "urgente"
                elif retard_jours > frequence_jours // 2:
                    priorite = "haute"
                elif obligatoire:
                    priorite = "haute"
                else:
                    priorite = "moyenne"

                taches.append(
                    {
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
                )

    # Trier par priorité puis par retard
    ordre_priorite = {"urgente": 0, "haute": 1, "moyenne": 2, "basse": 3}
    taches.sort(
        key=lambda t: (
            ordre_priorite.get(t.get("priorite", "moyenne"), 2),
            -t.get("retard_jours", 0),
        )
    )

    return taches


# =============================================================================
# CALCUL DU SCORE PROPRETÉ
# =============================================================================


def calculer_score_proprete(mes_objets: list[dict], historique: list[dict]) -> dict:
    """Calcule un score de propreté/entretien global."""
    if not mes_objets:
        return {"score": 100, "niveau": "Parfait", "couleur": "#27ae60"}

    taches = generer_taches_entretien(mes_objets, historique)

    # Score basé sur le ratio de tâches en retard
    total_objets = len(mes_objets)
    taches_urgentes = len([t for t in taches if t.get("priorite") == "urgente"])
    taches_hautes = len([t for t in taches if t.get("priorite") == "haute"])

    # Pénalité pour les retards
    penalite = (taches_urgentes * 15) + (taches_hautes * 5) + (len(taches) * 2)
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
        "urgentes": taches_urgentes,
        "hautes": taches_hautes,
    }


# =============================================================================
# CALCUL DU STREAK
# =============================================================================


def calculer_streak(historique: list[dict]) -> int:
    """Calcule le nombre de jours consécutifs avec des tâches accomplies."""
    if not historique:
        return 0

    # Extraire les dates uniques
    dates_accomplies = set()
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
            except:
                pass

    if not dates_accomplies:
        return 0

    # Compter les jours consécutifs depuis aujourd'hui
    streak = 0
    check_date = date.today()

    while check_date in dates_accomplies:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


# =============================================================================
# STATS GLOBALES POUR BADGES
# =============================================================================


def calculer_stats_globales(mes_objets: list[dict], historique: list[dict]) -> dict:
    """Calcule les statistiques globales pour l'attribution des badges."""
    score_data = calculer_score_proprete(mes_objets, historique)
    streak = calculer_streak(historique)

    # Compter les tâches accomplies
    taches_accomplies = len(historique)

    # Vérifier si électroménager OK (pas de tâches urgentes)
    taches = generer_taches_entretien(mes_objets, historique)
    electro_urgentes = [
        t
        for t in taches
        if t.get("categorie_id") == "electromenager" and t.get("priorite") in ["urgente", "haute"]
    ]

    # Vérifier si entretien pro effectué
    pro_fait = any(h.get("est_pro") for h in historique)

    return {
        "score": score_data["score"],
        "streak": streak,
        "taches_accomplies": taches_accomplies,
        "nb_objets": len(mes_objets),
        "electromenager_ok": len(electro_urgentes) == 0,
        "pro_effectue": pro_fait,
        "taches_urgentes": score_data["urgentes"],
        "taches_hautes": score_data["hautes"],
    }


def obtenir_badges_obtenus(stats: dict) -> list[str]:
    """Retourne la liste des IDs de badges obtenus."""
    obtenus = []
    for badge_def in BADGES_ENTRETIEN:
        if badge_def["condition"](stats):
            obtenus.append(badge_def["id"])
    return obtenus


# =============================================================================
# PRÉDICTIONS ET PLANNING
# =============================================================================


def generer_planning_previsionnel(
    mes_objets: list[dict], historique: list[dict], horizon_jours: int = 60
) -> list[dict]:
    """
    Génère le planning prévisionnel des tâches pour les prochaines semaines.

    Prédit quand chaque tâche sera due basé sur la fréquence et l'historique.
    """
    planning = []
    catalogue = charger_catalogue_entretien()
    aujourd_hui = date.today()

    # Construire l'index des dernières exécutions
    historique_index = {}
    for h in historique:
        cle = f"{h.get('objet_id')}_{h.get('tache_nom')}"
        date_h = h.get("date")
        if date_h:
            try:
                d = datetime.fromisoformat(date_h).date() if isinstance(date_h, str) else date_h
                if cle not in historique_index or d > historique_index[cle]:
                    historique_index[cle] = d
            except:
                pass

    # Parcourir mes objets
    for mon_objet in mes_objets:
        objet_id = mon_objet.get("objet_id")
        categorie_id = mon_objet.get("categorie_id")
        piece = mon_objet.get("piece", "")

        # Trouver la définition
        categorie_data = catalogue.get("categories", {}).get(categorie_id, {})
        objet_data = categorie_data.get("objets", {}).get(objet_id, {})

        if not objet_data:
            continue

        nom_objet = objet_data.get("nom", objet_id)

        # Parcourir les tâches
        for tache_def in objet_data.get("taches", []):
            tache_nom = tache_def.get("nom")
            frequence = tache_def.get("frequence_jours", 30)
            duree_min = tache_def.get("duree_min", 15)

            # Calculer la prochaine date
            cle_historique = f"{objet_id}_{tache_nom}"
            derniere_fois = historique_index.get(cle_historique)

            if derniere_fois:
                prochaine_date = derniere_fois + timedelta(days=frequence)
            else:
                # Jamais fait, considérer comme dû dans 7 jours
                prochaine_date = aujourd_hui + timedelta(days=7)

            jours_restants = (prochaine_date - aujourd_hui).days

            # N'inclure que les tâches futures dans l'horizon
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

    # Trier par date
    planning.sort(key=lambda t: t["jours_restants"])

    return planning


def generer_alertes_predictives(mes_objets: list[dict], historique: list[dict]) -> list[dict]:
    """Génère les alertes pour les tâches arrivant bientôt."""
    planning = generer_planning_previsionnel(mes_objets, historique, horizon_jours=14)

    # Filtrer les alertes les plus urgentes
    alertes = [t for t in planning if t["jours_restants"] <= 14]

    return alertes[:5]
