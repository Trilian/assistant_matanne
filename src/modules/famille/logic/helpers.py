"""
Helpers et fonctions utilitaires pour le module Famille
"""

from datetime import date, datetime, timedelta
from typing import Optional
import streamlit as st
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.core.models import (
    ChildProfile, Milestone, FamilyActivity, 
    HealthRoutine, HealthObjective, HealthEntry, FamilyBudget
)
from src.core.database import obtenir_contexte_db


# ═══════════════════════════════════════════════════════════
# CHILD PROFILE HELPERS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=3600)
def get_or_create_jules() -> int:
    """Récupère ou crée le profil Jules, retourne son ID"""
    try:
        with obtenir_contexte_db() as session:
            child = session.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            
            if not child:
                # Créer Jules (né le 22 juin 2024)
                child = ChildProfile(
                    name="Jules",
                    date_of_birth=date(2024, 6, 22),
                    gender="M",
                    notes="Notre petit Jules â¤ï¸",
                    actif=True
                )
                session.add(child)
                session.commit()
                st.success("✅ Profil Jules créé !")
            
            return child.id
    except Exception as e:
        st.error(f"❌ Erreur création Jules: {str(e)}")
        raise


def calculer_age_jules() -> dict:
    """Calcule l'âge de Jules en jours, semaines, mois"""
    try:
        with obtenir_contexte_db() as session:
            child = session.query(ChildProfile).filter_by(name="Jules").first()
            
            if not child or not child.date_of_birth:
                return {"jours": 0, "semaines": 0, "mois": 0, "ans": 0}
            
            aujourd_hui = date.today()
            delta = aujourd_hui - child.date_of_birth
            
            jours = delta.days
            semaines = jours // 7
            mois = jours // 30
            ans = jours // 365
            
            return {
                "jours": jours,
                "semaines": semaines,
                "mois": mois,
                "ans": ans,
                "date_naissance": child.date_of_birth
            }
    except Exception as e:
        st.error(f"❌ Erreur calcul âge: {str(e)}")
        return {"jours": 0, "semaines": 0, "mois": 0, "ans": 0}


# ═══════════════════════════════════════════════════════════
# MILESTONE HELPERS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def get_milestones_by_category(child_id: int) -> dict:
    """Récupère les jalons groupés par catégorie"""
    try:
        with obtenir_contexte_db() as session:
            milestones = session.query(Milestone).filter_by(child_id=child_id).all()
            
            result = {}
            for milestone in milestones:
                cat = milestone.categorie
                if cat not in result:
                    result[cat] = []
                result[cat].append({
                    "id": milestone.id,
                    "titre": milestone.titre,
                    "date": milestone.date_atteint,
                    "description": milestone.description,
                    "notes": milestone.notes
                })
            
            return result
    except Exception as e:
        st.error(f"❌ Erreur lecture jalons: {str(e)}")
        return {}


def count_milestones_by_category(child_id: int) -> dict:
    """Compte les jalons par catégorie"""
    try:
        with obtenir_contexte_db() as session:
            result = session.query(
                Milestone.categorie,
                func.count(Milestone.id).label("count")
            ).filter_by(child_id=child_id).group_by(Milestone.categorie).all()
            
            return {cat: count for cat, count in result}
    except Exception as e:
        st.error(f"❌ Erreur comptage jalons: {str(e)}")
        return {}


# ═══════════════════════════════════════════════════════════
# HEALTH OBJECTIVE HELPERS
# ═══════════════════════════════════════════════════════════


def calculer_progression_objectif(objective: HealthObjective) -> float:
    """Calcule le % de progression d'un objectif santé"""
    try:
        if not objective.valeur_cible or not objective.valeur_actuelle:
            return 0.0
        
        progression = (objective.valeur_actuelle / objective.valeur_cible) * 100
        return min(progression, 100.0)  # Max 100%
    except Exception:
        return 0.0


@st.cache_data(ttl=1800)
def get_objectives_actifs() -> list:
    """Récupère tous les objectifs en cours avec progression"""
    try:
        with obtenir_contexte_db() as session:
            objectives = session.query(HealthObjective).filter_by(statut="en_cours").all()
            
            result = []
            for obj in objectives:
                result.append({
                    "id": obj.id,
                    "titre": obj.titre,
                    "categorie": obj.categorie,
                    "progression": calculer_progression_objectif(obj),
                    "valeur_cible": obj.valeur_cible,
                    "valeur_actuelle": obj.valeur_actuelle,
                    "unite": obj.unite,
                    "priorite": obj.priorite,
                    "date_cible": obj.date_cible,
                    "jours_restants": (obj.date_cible - date.today()).days
                })
            
            return sorted(result, key=lambda x: x["priorite"] == "haute", reverse=True)
    except Exception as e:
        st.error(f"❌ Erreur lecture objectifs: {str(e)}")
        return []


# ═══════════════════════════════════════════════════════════
# BUDGET HELPERS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def get_budget_par_period(period: str = "month") -> dict:
    """Récupère le budget par période (day, week, month)"""
    try:
        with obtenir_contexte_db() as session:
            if period == "day":
                debut = date.today()
                fin = date.today()
            elif period == "week":
                debut = date.today() - timedelta(days=date.today().weekday())
                fin = debut + timedelta(days=6)
            else:  # month
                debut = date(date.today().year, date.today().month, 1)
                if date.today().month == 12:
                    fin = date(date.today().year + 1, 1, 1) - timedelta(days=1)
                else:
                    fin = date(date.today().year, date.today().month + 1, 1) - timedelta(days=1)
            
            budgets = session.query(FamilyBudget).filter(
                and_(FamilyBudget.date >= debut, FamilyBudget.date <= fin)
            ).all()
            
            result = {}
            total = 0
            for budget in budgets:
                cat = budget.categorie
                if cat not in result:
                    result[cat] = 0
                result[cat] += budget.montant
                total += budget.montant
            
            result["TOTAL"] = total
            return result
    except Exception as e:
        st.error(f"❌ Erreur lecture budget: {str(e)}")
        return {}


def get_budget_mois_dernier() -> float:
    """Récupère le budget total du mois dernier"""
    try:
        aujourd_hui = date.today()
        
        if aujourd_hui.month == 1:
            mois_dernier = date(aujourd_hui.year - 1, 12, 1)
        else:
            mois_dernier = date(aujourd_hui.year, aujourd_hui.month - 1, 1)
        
        mois_prochain = date(mois_dernier.year, mois_dernier.month, 1) + timedelta(days=32)
        mois_prochain = date(mois_prochain.year, mois_prochain.month, 1)
        
        with obtenir_contexte_db() as session:
            total = session.query(func.sum(FamilyBudget.montant)).filter(
                and_(
                    FamilyBudget.date >= mois_dernier,
                    FamilyBudget.date < mois_prochain
                )
            ).scalar() or 0
            
            return float(total)
    except Exception as e:
        st.error(f"❌ Erreur calcul budget mois dernier: {str(e)}")
        return 0.0


# ═══════════════════════════════════════════════════════════
# ACTIVITY HELPERS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def get_activites_semaine() -> list:
    """Récupère les activités de cette semaine"""
    try:
        debut_semaine = date.today() - timedelta(days=date.today().weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        with obtenir_contexte_db() as session:
            activities = session.query(FamilyActivity).filter(
                and_(
                    FamilyActivity.date_prevue >= debut_semaine,
                    FamilyActivity.date_prevue <= fin_semaine,
                    FamilyActivity.statut != "annulé"
                )
            ).order_by(FamilyActivity.date_prevue).all()
            
            return [
                {
                    "id": act.id,
                    "titre": act.titre,
                    "date": act.date_prevue,
                    "type": act.type_activite,
                    "lieu": act.lieu,
                    "participants": act.qui_participe or [],
                    "cout_estime": act.cout_estime,
                    "statut": act.statut
                }
                for act in activities
            ]
    except Exception as e:
        st.error(f"❌ Erreur lecture activités: {str(e)}")
        return []


def get_budget_activites_mois() -> float:
    """Récupère les dépenses en activités ce mois"""
    try:
        debut_mois = date(date.today().year, date.today().month, 1)
        if date.today().month == 12:
            fin_mois = date(date.today().year + 1, 1, 1) - timedelta(days=1)
        else:
            fin_mois = date(date.today().year, date.today().month + 1, 1) - timedelta(days=1)
        
        with obtenir_contexte_db() as session:
            total = session.query(func.sum(FamilyActivity.cout_reel)).filter(
                and_(
                    FamilyActivity.date_prevue >= debut_mois,
                    FamilyActivity.date_prevue <= fin_mois,
                    FamilyActivity.cout_reel > 0
                )
            ).scalar() or 0
            
            return float(total)
    except Exception as e:
        st.error(f"❌ Erreur budget activités: {str(e)}")
        return 0.0


# ═══════════════════════════════════════════════════════════
# HEALTH ROUTINE HELPERS
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=1800)
def get_routines_actives() -> list:
    """Récupère les routines de santé actives"""
    try:
        with obtenir_contexte_db() as session:
            routines = session.query(HealthRoutine).filter_by(actif=True).all()
            
            return [
                {
                    "id": r.id,
                    "nom": r.nom,
                    "type": r.type_routine,
                    "frequence": r.frequence,
                    "duree": r.duree_minutes,
                    "intensite": r.intensite,
                    "calories": r.calories_brulees_estimees
                }
                for r in routines
            ]
    except Exception as e:
        st.error(f"❌ Erreur lecture routines: {str(e)}")
        return []


def get_stats_sante_semaine() -> dict:
    """Calcule les stats de santé pour cette semaine"""
    try:
        debut_semaine = date.today() - timedelta(days=date.today().weekday())
        
        with obtenir_contexte_db() as session:
            entries = session.query(HealthEntry).filter(
                HealthEntry.date >= debut_semaine
            ).all()
            
            stats = {
                "nb_seances": len(entries),
                "total_minutes": sum(e.duree_minutes for e in entries),
                "total_calories": sum(e.calories_brulees or 0 for e in entries),
                "energie_moyenne": sum(e.note_energie or 0 for e in entries if e.note_energie) / max(len([e for e in entries if e.note_energie]), 1),
                "moral_moyen": sum(e.note_moral or 0 for e in entries if e.note_moral) / max(len([e for e in entries if e.note_moral]), 1)
            }
            
            return stats
    except Exception as e:
        st.error(f"❌ Erreur stats santé: {str(e)}")
        return {
            "nb_seances": 0,
            "total_minutes": 0,
            "total_calories": 0,
            "energie_moyenne": 0,
            "moral_moyen": 0
        }


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════


def clear_famille_cache():
    """Vide le cache du module famille (à utiliser après modifications)"""
    st.cache_data.clear()


def format_date_fr(d: date) -> str:
    """Formate une date en français"""
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois = ["jan", "fév", "mar", "avr", "mai", "jun", "jul", "aoû", "sep", "oct", "nov", "déc"]
    
    return f"{jours[d.weekday()]} {d.day} {mois[d.month-1]} {d.year}"

