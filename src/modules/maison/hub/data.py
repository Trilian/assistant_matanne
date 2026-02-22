"""
Hub Maison - Fonctions de données.

Agrégation des données depuis les services et la base de données.
Les tâches et alertes sont issues des services (jardin, entretien).
DB access délégué à HubDataService.
"""

import logging
from datetime import date, datetime

import streamlit as st

from src.core.session_keys import SK
from src.services.maison import get_hub_data_service

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# STATISTIQUES GLOBALES (DB directe)
# ═══════════════════════════════════════════════════════════


def obtenir_stats_globales() -> dict:
    """Récupère les statistiques globales du hub depuis la base de données."""
    stats = {
        "zones_jardin": 0,
        "pieces": 0,
        "objets_a_changer": 0,
        "taches_jour": 0,
        "temps_prevu_min": 0,
        "autonomie_pourcent": 0,
    }

    try:
        service = get_hub_data_service()
        db_stats = service.obtenir_stats_db()
        stats.update(db_stats)

        # Calculer autonomie via le service jardin
        try:
            import streamlit as _st

            from src.services.maison import get_jardin_service

            jardin_service = get_jardin_service()
            plantes = _st.session_state.get(SK.MES_PLANTES_JARDIN, [])
            recoltes = _st.session_state.get(SK.RECOLTES_JARDIN, [])
            autonomie = jardin_service.calculer_autonomie(plantes, recoltes)
            stats["autonomie_pourcent"] = autonomie.get("pourcentage_prevu", 0)
        except Exception:
            pass

    except Exception as e:
        logger.debug(f"Erreur récupération stats hub: {e}")

    return stats


# ═══════════════════════════════════════════════════════════
# TÂCHES DU JOUR (via services entretien + jardin)
# ═══════════════════════════════════════════════════════════


def _obtenir_objets_entretien() -> list[dict]:
    """Récupère les objets d'entretien depuis session_state ou DB."""
    return st.session_state.get(SK.MES_OBJETS_ENTRETIEN, [])


def _obtenir_historique_entretien() -> list[dict]:
    """Récupère l'historique d'entretien depuis session_state ou DB."""
    return st.session_state.get(SK.HISTORIQUE_ENTRETIEN, [])


def _obtenir_plantes_jardin() -> list[dict]:
    """Récupère les plantes du jardin depuis session_state ou DB."""
    return st.session_state.get(SK.MES_PLANTES, [])


def _obtenir_meteo_jardin() -> dict:
    """Récupère les données météo du jardin."""
    try:
        from src.modules.maison.jardin.data import obtenir_meteo_jardin

        return obtenir_meteo_jardin()
    except Exception:
        return {"temperature": 15, "pluie_prevue": False, "gel_risque": False}


def obtenir_taches_jour() -> list[dict]:
    """
    Récupère les tâches à faire aujourd'hui.

    Agrège les tâches urgentes d'entretien et de jardin
    depuis les services respectifs.
    """
    taches = []
    tache_id = 1

    # ─── Tâches entretien (via service) ───
    try:
        from src.services.maison import get_entretien_service

        service_entretien = get_entretien_service()
        objets = _obtenir_objets_entretien()
        historique = _obtenir_historique_entretien()

        if objets:
            taches_entretien = service_entretien.generer_taches(objets, historique)
            for t in taches_entretien[:5]:  # Top 5 les plus urgentes
                taches.append(
                    {
                        "id": tache_id,
                        "titre": f"{t.get('tache_nom', '')} - {t.get('objet_nom', '')}",
                        "domaine": "entretien",
                        "duree_min": t.get("duree_min", 15),
                        "priorite": t.get("priorite", "normale"),
                        "piece": t.get("piece", ""),
                    }
                )
                tache_id += 1
    except Exception as e:
        logger.debug(f"Erreur tâches entretien hub: {e}")

    # ─── Tâches jardin (via service) ───
    try:
        from src.services.maison import get_jardin_service

        service_jardin = get_jardin_service()
        plantes = _obtenir_plantes_jardin()
        meteo = _obtenir_meteo_jardin()

        if plantes:
            taches_jardin = service_jardin.generer_taches(plantes, meteo)
            for t in taches_jardin[:3]:  # Top 3 tâches jardin
                taches.append(
                    {
                        "id": tache_id,
                        "titre": t.get("tache", t.get("tache_nom", "")),
                        "domaine": "jardin",
                        "duree_min": t.get("duree_min", 15),
                        "priorite": t.get("priorite", "normale"),
                        "zone": t.get("zone", ""),
                    }
                )
                tache_id += 1
    except Exception as e:
        logger.debug(f"Erreur tâches jardin hub: {e}")

    # Trier par priorité
    ordre_priorite = {"urgente": 0, "haute": 1, "normale": 2, "basse": 3}
    taches.sort(key=lambda t: ordre_priorite.get(t.get("priorite", "normale"), 2))

    return taches


# ═══════════════════════════════════════════════════════════
# ALERTES (DB + services)
# ═══════════════════════════════════════════════════════════


def obtenir_alertes() -> list[dict]:
    """
    Récupère les alertes actives.

    Combine alertes de la DB (objets à remplacer) et des services
    (alertes prédictives entretien).
    """
    alertes = []

    # ─── Alertes entretien prédictives ───
    try:
        from src.services.maison import get_entretien_service

        service = get_entretien_service()
        objets = _obtenir_objets_entretien()
        historique = _obtenir_historique_entretien()

        if objets:
            alertes_entretien = service.generer_alertes_predictives(objets, historique)
            for a in alertes_entretien[:3]:
                alertes.append(
                    {
                        "type": "info",
                        "icon": "🧹",
                        "titre": f"{a.get('tache_nom', '')} dans {a.get('jours_restants', '?')}j",
                        "description": f"{a.get('objet_nom', '')} - {a.get('piece', '')}",
                    }
                )
    except Exception as e:
        logger.debug(f"Erreur alertes entretien hub: {e}")

    # ─── Alertes objets à changer (via service) ───
    try:
        service = get_hub_data_service()
        objets_urgents = service.compter_objets_urgents()
        if objets_urgents > 0:
            alertes.append(
                {
                    "type": "warning",
                    "icon": "🔧",
                    "titre": f"{objets_urgents} objet(s) à remplacer",
                    "description": "Priorité urgente - voir détails",
                }
            )
    except Exception as e:
        logger.debug(f"Erreur alertes objets hub: {e}")

    return alertes


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


def calculer_charge(taches: list[dict]) -> dict:
    """Calcule la charge quotidienne à partir des tâches."""
    temps_total = sum(t.get("duree_min", 0) for t in taches)
    max_heures = 2  # Config: 2h max/jour

    pourcent = min(100, int((temps_total / (max_heures * 60)) * 100)) if max_heures > 0 else 0

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
