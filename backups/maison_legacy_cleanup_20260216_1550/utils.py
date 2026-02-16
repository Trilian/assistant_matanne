"""
Helpers Maison - Fonctions reutilisables pour les 3 modules
Gestion des projets, jardin et entretien
"""

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.core.database import obtenir_contexte_db
from src.core.models import GardenItem, GardenLog, Project, Routine, RoutineTask

# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# PROJETS
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def charger_projets(statut: str = None) -> pd.DataFrame:
    """Charge les projets avec filtrage optionnel"""
    with obtenir_contexte_db() as session:
        query = session.query(Project)
        if statut:
            query = query.filter_by(statut=statut)
        projets = query.all()

        data = []
        for p in projets:
            jours_restants = None
            if p.date_fin_prevue:
                jours_restants = (p.date_fin_prevue - date.today()).days

            completion = 0
            if p.tasks:
                completed = len([t for t in p.tasks if t.statut == "termine"])
                completion = (completed / len(p.tasks) * 100) if p.tasks else 0

            data.append(
                {
                    "id": p.id,
                    "nom": p.nom,
                    "description": p.description,
                    "statut": p.statut,
                    "priorite": p.priorite,
                    "progress": completion,
                    "jours_restants": jours_restants,
                    "date_fin": p.date_fin_prevue,
                    "taches_count": len(p.tasks),
                }
            )

        return pd.DataFrame(data)


@st.cache_data(ttl=1800)
def get_projets_urgents() -> list[dict]:
    """Detecte les projets urgents ou en retard"""
    with obtenir_contexte_db() as session:
        projets = session.query(Project).filter_by(statut="en_cours").all()
        urgents = []

        for p in projets:
            # Priorite haute ou très haute + en cours
            if p.priorite in ["haute", "urgente"]:
                urgents.append(
                    {
                        "type": "PRIORITE",
                        "projet": p.nom,
                        "message": f"Priorite {p.priorite.upper()}",
                    }
                )

            # En retard
            if p.date_fin_prevue and p.date_fin_prevue < date.today():
                days_late = (date.today() - p.date_fin_prevue).days
                urgents.append(
                    {
                        "type": "RETARD",
                        "projet": p.nom,
                        "message": f"En retard de {days_late} jour(s)",
                    }
                )

        return urgents


@st.cache_data(ttl=1800)
def get_stats_projets() -> dict:
    """Recupère les statistiques des projets"""
    with obtenir_contexte_db() as session:
        total = session.query(Project).count()
        en_cours = session.query(Project).filter_by(statut="en_cours").count()
        termines = session.query(Project).filter_by(statut="termine").count()

        # Progression moyenne
        projets = session.query(Project).all()
        progressions = []
        for p in projets:
            if p.tasks:
                completed = len([t for t in p.tasks if t.statut == "termine"])
                progressions.append(completed / len(p.tasks) * 100)

        avg_progress = sum(progressions) / len(progressions) if progressions else 0

        return {
            "total": total,
            "en_cours": en_cours,
            "termines": termines,
            "avg_progress": round(avg_progress, 1),
        }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# JARDIN
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def charger_plantes() -> pd.DataFrame:
    """Charge toutes les plantes du jardin"""
    with obtenir_contexte_db() as session:
        items = session.query(GardenItem).filter_by(statut="actif").all()

        data = []
        for item in items:
            # Determiner si elle doit être arrosee
            derniers_logs = (
                session.query(GardenLog)
                .filter_by(garden_item_id=item.id, action="arrosage")
                .order_by(GardenLog.date.desc())
                .limit(1)
                .all()
            )

            jours_depuis_arrosage = None
            if derniers_logs:
                jours_depuis_arrosage = (date.today() - derniers_logs[0].date).days

            # Determiner la frequence d'arrosage (mock pour demo)
            freq_arrosage = 2  # À adapter selon modèle BD
            a_arroser = jours_depuis_arrosage is None or jours_depuis_arrosage >= freq_arrosage

            data.append(
                {
                    "id": item.id,
                    "nom": item.nom,
                    "type": item.type,
                    "location": item.location,
                    "plantation": item.date_plantation,
                    "recolte": item.date_recolte_prevue,
                    "a_arroser": a_arroser,
                    "jours_depuis_arrosage": jours_depuis_arrosage,
                    "notes": item.notes,
                }
            )

        return pd.DataFrame(data)


@st.cache_data(ttl=1800)
def get_plantes_a_arroser() -> list[dict]:
    """Detecte les plantes qui ont besoin d'eau"""
    df = charger_plantes()
    if df.empty:
        return []
    return df[df["a_arroser"]].to_dict(orient="records")


@st.cache_data(ttl=1800)
def get_recoltes_proches() -> list[dict]:
    """Detecte les recoltes prevues dans les 7 prochains jours"""
    df = charger_plantes()
    aujourd_hui = date.today()
    dans_7_jours = aujourd_hui + timedelta(days=7)

    if df.empty:
        return []

    df_recolte = df[
        (df["recolte"].notna()) & (df["recolte"] >= aujourd_hui) & (df["recolte"] <= dans_7_jours)
    ]

    return df_recolte.to_dict(orient="records")


@st.cache_data(ttl=1800)
def get_stats_jardin() -> dict:
    """Recupère les statistiques du jardin"""
    df = charger_plantes()

    return {
        "total_plantes": len(df),
        "a_arroser": len(get_plantes_a_arroser()),
        "recoltes_proches": len(get_recoltes_proches()),
        "categories": df["type"].nunique() if not df.empty else 0,
    }


def get_saison() -> str:
    """Determine la saison actuelle"""
    month = date.today().month
    if month in [3, 4, 5]:
        return "Printemps"
    elif month in [6, 7, 8]:
        return "Éte"
    elif month in [9, 10, 11]:
        return "Automne"
    else:
        return "Hiver"


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# ENTRETIEN / MÉNAGE
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def charger_routines() -> pd.DataFrame:
    """Charge toutes les routines actives"""
    with obtenir_contexte_db() as session:
        routines = session.query(Routine).filter_by(actif=True).all()

        data = []
        for r in routines:
            tasks_aujourd_hui = (
                session.query(RoutineTask)
                .filter(RoutineTask.routine_id == r.id, RoutineTask.fait_le == date.today())
                .count()
            )

            total_tasks = len(r.tasks)
            completion = (tasks_aujourd_hui / total_tasks * 100) if total_tasks > 0 else 0

            data.append(
                {
                    "id": r.id,
                    "nom": r.nom,
                    "categorie": r.categorie,
                    "frequence": r.frequence,
                    "tasks_count": total_tasks,
                    "tasks_aujourd_hui": tasks_aujourd_hui,
                    "completion": completion,
                    "description": r.description,
                }
            )

        return pd.DataFrame(data)


@st.cache_data(ttl=1800)
def get_taches_today() -> list[dict]:
    """Retourne les tâches du jour à faire"""
    with obtenir_contexte_db() as session:
        taches = session.query(RoutineTask).filter(RoutineTask.fait_le != date.today()).all()

        return [
            {
                "id": t.id,
                "nom": t.nom,
                "routine_id": t.routine_id,
                "heure": t.heure_prevue,
                "fait": t.fait_le == date.today(),
                "description": t.description,
            }
            for t in taches
        ]


@st.cache_data(ttl=1800)
def get_stats_entretien() -> dict:
    """Recupère les statistiques d'entretien"""
    with obtenir_contexte_db() as session:
        total_routines = session.query(Routine).filter_by(actif=True).count()
        total_taches = session.query(RoutineTask).count()

        taches_aujourd_hui = session.query(RoutineTask).filter_by(fait_le=date.today()).count()

        return {
            "routines_actives": total_routines,
            "total_taches": total_taches,
            "taches_today": taches_aujourd_hui,
            "completion_today": (taches_aujourd_hui / total_taches * 100)
            if total_taches > 0
            else 0,
        }


# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
# GESTION CACHE
# ══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════


def clear_maison_cache():
    """Invalide le cache Streamlit pour le module Maison"""
    st.cache_data.clear()
    st.rerun()
