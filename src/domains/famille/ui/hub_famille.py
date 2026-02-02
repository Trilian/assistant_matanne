"""
Hub Famille - Dashboard principal avec cards cliquables.

Structure:
┌─────────────┐ ┌─────────────┐
│ 👶 Jules    │ │ 🎉 Weekend  │
│ 19m         │ │ Idées IA    │
└─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐
│ 💪 Anne     │ │ 💪 Mathieu  │
│ 🔥 5j │ ⌚   │ │ 🔥 3j │ ⌚   │
└─────────────┘ └─────────────┘
┌─────────────────────────────┐
│ 🛍️ Achats Famille          │
└─────────────────────────────┘
"""

import streamlit as st
from datetime import date, timedelta
from typing import Callable

from src.core.database import get_db_context
from src.core.models import (
    UserProfile, 
    GarminDailySummary, 
    WeekendActivity,
    FamilyPurchase,
    ChildProfile,
)
from src.services.garmin_sync import get_user_by_username, init_family_users


# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

CARD_STYLES = """
<style>
.family-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 20px;
    color: white;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 10px;
    min-height: 120px;
}
.family-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.family-card.jules {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
.family-card.weekend {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
.family-card.anne {
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}
.family-card.mathieu {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    color: #333;
}
.family-card.achats {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.card-emoji {
    font-size: 2.5rem;
    margin-bottom: 5px;
}
.card-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 5px;
}
.card-subtitle {
    font-size: 0.9rem;
    opacity: 0.9;
}
.card-stats {
    display: flex;
    gap: 15px;
    margin-top: 10px;
}
.card-stat {
    display: flex;
    align-items: center;
    gap: 5px;
}
.streak-badge {
    background: rgba(255,255,255,0.2);
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.85rem;
}
</style>
"""


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def calculer_age_jules() -> dict:
    """Calcule l'âge de Jules"""
    try:
        with get_db_context() as db:
            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            if not jules or not jules.date_of_birth:
                # Valeurs par défaut si pas trouvé
                return {"mois": 19, "jours": 0, "texte": "19 mois"}
            
            today = date.today()
            delta = today - jules.date_of_birth
            mois = delta.days // 30
            jours_restants = delta.days % 30
            
            return {
                "mois": mois,
                "jours": jours_restants,
                "texte": f"{mois} mois" + (f" et {jours_restants}j" if jours_restants > 0 else "")
            }
    except:
        return {"mois": 19, "jours": 0, "texte": "19 mois"}


def get_user_streak(username: str) -> int:
    """Récupère le streak d'un utilisateur"""
    try:
        with get_db_context() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return 0
            
            # Calculer le streak basé sur les résumés quotidiens
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            summaries = db.query(GarminDailySummary).filter(
                GarminDailySummary.user_id == user.id,
                GarminDailySummary.date >= start_date
            ).order_by(GarminDailySummary.date.desc()).all()
            
            if not summaries:
                return 0
            
            streak = 0
            current_date = end_date
            summary_by_date = {s.date: s for s in summaries}
            objectif = user.objectif_pas_quotidien or 10000
            
            while current_date >= start_date:
                summary = summary_by_date.get(current_date)
                if summary and summary.pas >= objectif:
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return streak
    except:
        return 0


def get_user_garmin_connected(username: str) -> bool:
    """Vérifie si Garmin est connecté"""
    try:
        with get_db_context() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            return user.garmin_connected if user else False
    except:
        return False


def count_weekend_activities() -> int:
    """Compte les activités weekend planifiées"""
    try:
        with get_db_context() as db:
            today = date.today()
            # Prochain weekend
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0 and today.weekday() != 5:
                days_until_saturday = 7
            saturday = today + timedelta(days=days_until_saturday)
            sunday = saturday + timedelta(days=1)
            
            count = db.query(WeekendActivity).filter(
                WeekendActivity.date_prevue.in_([saturday, sunday]),
                WeekendActivity.statut == "planifié"
            ).count()
            return count
    except:
        return 0


def count_pending_purchases() -> int:
    """Compte les achats en attente"""
    try:
        with get_db_context() as db:
            return db.query(FamilyPurchase).filter_by(achete=False).count()
    except:
        return 0


def count_urgent_purchases() -> int:
    """Compte les achats urgents"""
    try:
        with get_db_context() as db:
            return db.query(FamilyPurchase).filter(
                FamilyPurchase.achete == False,
                FamilyPurchase.priorite.in_(["urgent", "haute"])
            ).count()
    except:
        return 0


# ═══════════════════════════════════════════════════════════
# COMPOSANTS CARDS
# ═══════════════════════════════════════════════════════════

def render_card_jules():
    """Affiche la card Jules"""
    age = calculer_age_jules()
    
    if st.button("👶 **Jules**", key="card_jules", use_container_width=True, type="primary"):
        st.session_state["famille_page"] = "jules"
        st.rerun()
    
    st.caption(f"🎂 {age['texte']} • 🎨 Activités adaptées")


def render_card_weekend():
    """Affiche la card Weekend"""
    count = count_weekend_activities()
    
    if st.button("🎉 **Ce Weekend**", key="card_weekend", use_container_width=True, type="secondary"):
        st.session_state["famille_page"] = "weekend"
        st.rerun()
    
    if count > 0:
        st.caption(f"📅 {count} activité(s) planifiée(s)")
    else:
        st.caption("💡 Découvrir des idées IA")


def render_card_user(username: str, display_name: str, emoji: str):
    """Affiche la card utilisateur (Anne ou Mathieu)"""
    streak = get_user_streak(username)
    garmin = get_user_garmin_connected(username)
    
    btn_type = "primary" if username == "anne" else "secondary"
    
    if st.button(f"{emoji} **{display_name}**", key=f"card_{username}", use_container_width=True, type=btn_type):
        st.session_state["famille_page"] = "suivi"
        st.session_state["suivi_user"] = username
        st.rerun()
    
    status_parts = []
    if streak > 0:
        status_parts.append(f"🔥 {streak}j")
    if garmin:
        status_parts.append("⌚ Garmin")
    else:
        status_parts.append("⌚ Non connecté")
    
    st.caption(" • ".join(status_parts))


def render_card_achats():
    """Affiche la card Achats"""
    pending = count_pending_purchases()
    urgent = count_urgent_purchases()
    
    if st.button("🛍️ **Achats Famille**", key="card_achats", use_container_width=True, type="secondary"):
        st.session_state["famille_page"] = "achats"
        st.rerun()
    
    if urgent > 0:
        st.caption(f"⚠️ {urgent} urgent(s) • 📋 {pending} en attente")
    elif pending > 0:
        st.caption(f"📋 {pending} article(s) en attente")
    else:
        st.caption("✅ Rien en attente")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du Hub Famille"""
    st.title("👨‍👩‍👧 Hub Famille")
    
    # Initialiser les utilisateurs si nécessaire
    try:
        init_family_users()
    except:
        pass
    
    # Gérer la navigation
    page = st.session_state.get("famille_page", "hub")
    
    if page == "hub":
        render_hub()
    elif page == "jules":
        from src.domains.famille.ui.jules import app as jules_app
        if st.button("⬅️ Retour au Hub"):
            st.session_state["famille_page"] = "hub"
            st.rerun()
        jules_app()
    elif page == "weekend":
        from src.domains.famille.ui.weekend import app as weekend_app
        if st.button("⬅️ Retour au Hub"):
            st.session_state["famille_page"] = "hub"
            st.rerun()
        weekend_app()
    elif page == "suivi":
        from src.domains.famille.ui.suivi_perso import app as suivi_app
        if st.button("⬅️ Retour au Hub"):
            st.session_state["famille_page"] = "hub"
            st.rerun()
        suivi_app()
    elif page == "achats":
        from src.domains.famille.ui.achats_famille import app as achats_app
        if st.button("⬅️ Retour au Hub"):
            st.session_state["famille_page"] = "hub"
            st.rerun()
        achats_app()
    else:
        render_hub()


def render_hub():
    """Affiche le hub principal avec les cards"""
    
    st.markdown("---")
    
    # Première ligne: Jules + Weekend
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            render_card_jules()
    
    with col2:
        with st.container(border=True):
            render_card_weekend()
    
    # Deuxième ligne: Anne + Mathieu
    col3, col4 = st.columns(2)
    
    with col3:
        with st.container(border=True):
            render_card_user("anne", "Anne", "👩")
    
    with col4:
        with st.container(border=True):
            render_card_user("mathieu", "Mathieu", "👨")
    
    # Troisième ligne: Achats (pleine largeur)
    with st.container(border=True):
        render_card_achats()
    
    # Section rapide: Ce weekend
    st.markdown("---")
    st.subheader("🎯 Ce Weekend")
    
    render_weekend_preview()


def render_weekend_preview():
    """Aperçu rapide du weekend"""
    today = date.today()
    
    # Calculer le prochain weekend
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0 and today.weekday() not in [5, 6]:
        days_until_saturday = 7
    
    if today.weekday() == 5:  # Samedi
        saturday = today
    elif today.weekday() == 6:  # Dimanche
        saturday = today - timedelta(days=1)
    else:
        saturday = today + timedelta(days=days_until_saturday)
    
    sunday = saturday + timedelta(days=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**📅 Samedi {saturday.strftime('%d/%m')}**")
        _render_day_activities(saturday)
    
    with col2:
        st.markdown(f"**📅 Dimanche {sunday.strftime('%d/%m')}**")
        _render_day_activities(sunday)


def _render_day_activities(day: date):
    """Affiche les activités d'un jour"""
    try:
        with get_db_context() as db:
            activities = db.query(WeekendActivity).filter(
                WeekendActivity.date_prevue == day,
                WeekendActivity.statut == "planifié"
            ).all()
            
            if activities:
                for act in activities:
                    heure = act.heure_debut or "?"
                    st.write(f"• {heure} - {act.titre}")
            else:
                st.caption("Rien de prévu")
                if st.button("💡 Suggérer", key=f"suggest_{day}"):
                    st.session_state["famille_page"] = "weekend"
                    st.session_state["weekend_suggest_date"] = day
                    st.rerun()
    except:
        st.caption("Rien de prévu")
