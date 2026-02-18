"""
Hub Maison - Fonctions de données.
"""

from datetime import date, datetime

from src.core.database import obtenir_contexte_db
from src.core.models import ObjetMaison, PieceMaison
from src.core.models.temps_entretien import SessionTravail, ZoneJardin


def obtenir_stats_globales() -> dict:
    """Récupère les statistiques globales du hub."""
    stats = {
        "zones_jardin": 0,
        "pieces": 0,
        "objets_a_changer": 0,
        "taches_jour": 0,
        "temps_prevu_min": 0,
        "autonomie_pourcent": 47,  # TODO: calculer depuis recoltes
    }

    try:
        with obtenir_contexte_db() as db:
            # Zones jardin
            stats["zones_jardin"] = db.query(ZoneJardin).count()

            # Pièces
            stats["pieces"] = db.query(PieceMaison).count()

            # Objets à changer
            stats["objets_a_changer"] = (
                db.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_reparer"]))
                .count()
            )

            # Sessions ce mois
            debut_mois = date.today().replace(day=1)
            sessions = (
                db.query(SessionTravail)
                .filter(SessionTravail.debut >= datetime.combine(debut_mois, datetime.min.time()))
                .all()
            )
            stats["temps_mois_heures"] = sum(s.duree_minutes or 0 for s in sessions) / 60

    except Exception:
        pass

    return stats


def obtenir_taches_jour() -> list[dict]:
    """Récupère les tâches à faire aujourd'hui (mock pour l'instant)."""
    # TODO: Implémenter avec la vraie table taches_home
    return [
        {
            "id": 1,
            "titre": "Arroser les tomates",
            "domaine": "jardin",
            "duree_min": 15,
            "priorite": "normale",
            "zone": "Potager sud",
        },
        {
            "id": 2,
            "titre": "Passer l'aspirateur salon",
            "domaine": "entretien",
            "duree_min": 20,
            "priorite": "haute",
            "piece": "Salon",
        },
        {
            "id": 3,
            "titre": "Vérifier facture EDF",
            "domaine": "charges",
            "duree_min": 10,
            "priorite": "normale",
            "contrat": "EDF",
        },
    ]


def obtenir_alertes() -> list[dict]:
    """Récupère les alertes actives (mock pour l'instant)."""
    alertes = []

    # TODO: Implémenter avec vraies données (météo, factures, etc.)
    # Exemple d'alertes
    alertes.append(
        {
            "type": "info",
            "icon": "🌡️",
            "titre": "Gel prévu vendredi",
            "description": "Pensez à protéger les plants sensibles",
        }
    )

    # Vérifier objets à changer
    try:
        with obtenir_contexte_db() as db:
            objets_urgents = (
                db.query(ObjetMaison)
                .filter(
                    ObjetMaison.statut == "a_changer",
                    ObjetMaison.priorite_remplacement == "urgente",
                )
                .count()
            )
            if objets_urgents > 0:
                alertes.append(
                    {
                        "type": "warning",
                        "icon": "🔧",
                        "titre": f"{objets_urgents} objet(s) à remplacer",
                        "description": "Priorité urgente - voir détails",
                    }
                )
    except Exception:
        pass

    return alertes


def calculer_charge(taches: list[dict]) -> dict:
    """Calcule la charge quotidienne."""
    temps_total = sum(t.get("duree_min", 0) for t in taches)
    max_heures = 2  # Config par défaut: 2h max/jour

    pourcent = min(100, int((temps_total / (max_heures * 60)) * 100))

    if pourcent < 50:
        niveau = "leger"
    elif pourcent < 80:
        niveau = "normal"
    else:
        niveau = "eleve"

    return {
        "temps_min": temps_total,
        "temps_str": f"{temps_total // 60}h{temps_total % 60:02d}"
        if temps_total >= 60
        else f"{temps_total} min",
        "pourcent": pourcent,
        "niveau": niveau,
        "nb_taches": len(taches),
    }
