"""
Utilitaires partagés pour les modules Maison.

Fonctions de chargement, filtrage et statistiques pour Projets, Jardin et Entretien.
"""

import logging
from datetime import date

import pandas as pd
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.decorators import avec_cache
from src.core.models import ElementJardin, JournalJardin, Project, Routine, TacheRoutine

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# PROJETS
# ═══════════════════════════════════════════════════════════


@avec_cache(ttl=300)
def charger_projets(statut: str | None = None) -> pd.DataFrame:
    """Charge les projets depuis la base de données.

    Args:
        statut: Filtre optionnel par statut (en_cours, terminé, etc.)

    Returns:
        DataFrame avec colonnes: nom, progress, jours_restants, etc.
    """
    try:
        with obtenir_contexte_db() as session:
            query = session.query(Project)
            if statut:
                projets = query.filter_by(statut=statut).all()
            else:
                projets = query.all()

            if not projets:
                return pd.DataFrame()

            data = []
            for p in projets:
                tasks = p.tasks if p.tasks else []
                total = len(tasks)
                done = len([t for t in tasks if t.statut == "termine"])
                progress = (done / total * 100) if total > 0 else 0

                jours_restants = None
                if p.date_fin_prevue:
                    jours_restants = (p.date_fin_prevue - date.today()).days

                data.append(
                    {
                        "id": p.id,
                        "nom": p.nom,
                        "description": p.description,
                        "statut": p.statut,
                        "priorite": p.priorite,
                        "progress": progress,
                        "jours_restants": jours_restants,
                        "taches_count": total,
                    }
                )

            return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Erreur chargement projets: {e}")
        return pd.DataFrame()


@avec_cache(ttl=300)
def get_projets_urgents() -> list[dict]:
    """Détecte les projets urgents (priorité haute ou en retard).

    Returns:
        Liste de dicts avec type (PRIORITE/RETARD) et message.
    """
    alertes: list[dict] = []
    try:
        with obtenir_contexte_db() as session:
            projets = session.query(Project).filter_by(statut="en_cours").all()

            for p in projets:
                # Détection priorité haute/urgente
                if p.priorite in ("haute", "urgente"):
                    alertes.append(
                        {
                            "type": "PRIORITE",
                            "message": f"Projet '{p.nom}' en priorité {p.priorite}",
                            "projet": p.nom,
                        }
                    )

                # Détection retard
                if p.date_fin_prevue and p.date_fin_prevue < date.today():
                    jours = (date.today() - p.date_fin_prevue).days
                    alertes.append(
                        {
                            "type": "RETARD",
                            "message": f"Projet '{p.nom}' en retard de {jours} jour(s)",
                            "projet": p.nom,
                        }
                    )

    except Exception as e:
        logger.error(f"Erreur détection projets urgents: {e}")

    return alertes


@avec_cache(ttl=300)
def get_stats_projets() -> dict:
    """Calcule les statistiques globales des projets.

    Returns:
        Dict avec total, en_cours, termines, avg_progress.
    """
    try:
        with obtenir_contexte_db() as session:
            total = session.query(Project).count()
            en_cours = session.query(Project).filter_by(statut="en_cours").count()
            termines = session.query(Project).filter_by(statut="termine").count()

            # Calcul progression moyenne
            projets = session.query(Project).all()
            if projets:
                progressions = []
                for p in projets:
                    tasks = p.tasks if p.tasks else []
                    t_total = len(tasks)
                    t_done = len([t for t in tasks if t.statut == "termine"])
                    progressions.append((t_done / t_total * 100) if t_total > 0 else 0)
                avg_progress = sum(progressions) / len(progressions) if progressions else 0
            else:
                avg_progress = 0

            return {
                "total": total,
                "en_cours": en_cours,
                "termines": termines,
                "avg_progress": avg_progress,
            }
    except Exception as e:
        logger.error(f"Erreur calcul stats projets: {e}")
        return {"total": 0, "en_cours": 0, "termines": 0, "avg_progress": 0}


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════

SEUIL_ARROSAGE_JOURS = 3  # Nombre de jours sans arrosage avant alerte


@avec_cache(ttl=300)
def charger_plantes() -> pd.DataFrame:
    """Charge les plantes actives et leur état d'arrosage.

    Returns:
        DataFrame avec colonnes: nom, a_arroser, jours_depuis_arrosage, recolte, etc.
    """
    try:
        with obtenir_contexte_db() as session:
            plantes = session.query(ElementJardin).filter_by(statut="actif").all()

            if not plantes:
                return pd.DataFrame()

            data = []
            for plante in plantes:
                # Dernier arrosage
                logs = (
                    session.query(JournalJardin)
                    .filter_by(garden_item_id=plante.id)
                    .order_by(JournalJardin.date.desc())
                    .limit(1)
                    .all()
                )

                jours_depuis = None
                a_arroser = True
                if logs:
                    jours_depuis = (date.today() - logs[0].date).days
                    a_arroser = jours_depuis >= SEUIL_ARROSAGE_JOURS

                data.append(
                    {
                        "id": plante.id,
                        "nom": plante.nom,
                        "type": plante.type,
                        "location": plante.location,
                        "a_arroser": a_arroser,
                        "jours_depuis_arrosage": jours_depuis,
                        "recolte": plante.date_recolte_prevue,
                    }
                )

            return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Erreur chargement plantes: {e}")
        return pd.DataFrame()


@avec_cache(ttl=300)
def get_plantes_a_arroser() -> list[dict]:
    """Retourne les plantes qui ont besoin d'eau.

    Returns:
        Liste de dicts des plantes à arroser.
    """
    df = charger_plantes()
    if df.empty:
        return []
    return df[df["a_arroser"] == True].to_dict("records")  # noqa: E712


@avec_cache(ttl=300)
def get_recoltes_proches() -> list[dict]:
    """Retourne les plantes à récolter dans les 7 prochains jours.

    Returns:
        Liste de dicts des plantes à récolter bientôt.
    """
    df = charger_plantes()
    if df.empty:
        return []

    today = date.today()
    result = []
    for _, row in df.iterrows():
        recolte = row.get("recolte")
        if recolte is None:
            continue
        if hasattr(recolte, "date"):
            recolte = recolte.date()
        jours = (recolte - today).days
        if 0 <= jours <= 7:
            result.append(row.to_dict())

    return result


@avec_cache(ttl=300)
def get_stats_jardin() -> dict:
    """Calcule les statistiques du jardin.

    Returns:
        Dict avec total_plantes, a_arroser, categories, etc.
    """
    df = charger_plantes()
    plantes_arroser = get_plantes_a_arroser()
    recoltes = get_recoltes_proches()

    total = len(df) if not df.empty else 0
    categories = df["type"].nunique() if not df.empty and "type" in df.columns else 0

    return {
        "total_plantes": total,
        "a_arroser": len(plantes_arroser),
        "recoltes_proches": len(recoltes),
        "categories": categories,
    }


def get_saison() -> str:
    """Retourne la saison actuelle.

    Returns:
        Nom de la saison en français.
    """
    mois = date.today().month
    if mois in (3, 4, 5):
        return "Printemps"
    elif mois in (6, 7, 8):
        return "Éte"
    elif mois in (9, 10, 11):
        return "Automne"
    else:
        return "Hiver"


# ═══════════════════════════════════════════════════════════
# ENTRETIEN
# ═══════════════════════════════════════════════════════════


@avec_cache(ttl=300)
def charger_routines() -> pd.DataFrame:
    """Charge les routines actives avec leurs tâches.

    Returns:
        DataFrame des routines actives.
    """
    try:
        with obtenir_contexte_db() as session:
            routines = session.query(Routine).filter_by(actif=True).all()

            if not routines:
                return pd.DataFrame()

            data = []
            for r in routines:
                taches_faites = (
                    session.query(TacheRoutine)
                    .filter(
                        TacheRoutine.routine_id == r.id,
                        TacheRoutine.fait_le == date.today(),
                    )
                    .count()
                )

                data.append(
                    {
                        "id": r.id,
                        "nom": r.nom,
                        "categorie": r.categorie,
                        "frequence": r.frequence,
                        "total_taches": len(r.tasks) if r.tasks else 0,
                        "taches_faites": taches_faites,
                    }
                )

            return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Erreur chargement routines: {e}")
        return pd.DataFrame()


@avec_cache(ttl=300)
def get_taches_today() -> list[dict]:
    """Retourne les tâches du jour non encore faites.

    Returns:
        Liste de dicts des tâches à faire aujourd'hui.
    """
    try:
        with obtenir_contexte_db() as session:
            taches = (
                session.query(TacheRoutine)
                .filter(
                    (TacheRoutine.fait_le == None)  # noqa: E711
                    | (TacheRoutine.fait_le < date.today())
                )
                .all()
            )

            return [
                {
                    "id": t.id,
                    "nom": t.nom,
                    "routine_id": t.routine_id,
                    "heure_prevue": t.heure_prevue,
                    "description": t.description,
                }
                for t in taches
            ]
    except Exception as e:
        logger.error(f"Erreur chargement tâches du jour: {e}")
        return []


@avec_cache(ttl=300)
def get_stats_entretien() -> dict:
    """Calcule les statistiques d'entretien.

    Returns:
        Dict avec routines_actives, total_taches, taches_today, completion_today.
    """
    try:
        with obtenir_contexte_db() as session:
            routines_actives = session.query(Routine).filter_by(actif=True).count()
            total_taches = session.query(TacheRoutine).count()
            taches_today = session.query(TacheRoutine).filter_by(fait_le=date.today()).count()

            completion = (taches_today / total_taches * 100) if total_taches > 0 else 0

            return {
                "routines_actives": routines_actives,
                "total_taches": total_taches,
                "taches_today": taches_today,
                "completion_today": completion,
            }
    except Exception as e:
        logger.error(f"Erreur calcul stats entretien: {e}")
        return {
            "routines_actives": 0,
            "total_taches": 0,
            "taches_today": 0,
            "completion_today": 0,
        }


# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════


def clear_maison_cache() -> None:
    """Nettoie le cache Streamlit et relance l'application."""
    st.cache_data.clear()
    st.rerun()
