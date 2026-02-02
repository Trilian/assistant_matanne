"""
Module Suivi Perso - Dashboard santé/sport pour Anne et Mathieu.

Fonctionnalités:
- Switch utilisateur (Anne / Mathieu)
- Dashboard perso (stats Garmin, streak, objectifs)
- Routines sport
- Log alimentation
- Progression (graphiques)
- Sync Garmin
"""

import streamlit as st
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_db_context
from src.core.models import (
    UserProfile,
    GarminToken,
    GarminActivity,
    GarminDailySummary,
    FoodLog,
    HealthRoutine,
)
from src.services.garmin_sync import (
    GarminService,
    get_garmin_service,
    get_or_create_user,
    get_user_by_username,
)


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def get_current_user() -> str:
    """Récupère l'utilisateur courant"""
    return st.session_state.get("suivi_user", "anne")


def set_current_user(username: str):
    """Définit l'utilisateur courant"""
    st.session_state["suivi_user"] = username


def get_user_data(username: str) -> dict:
    """Récupère les données complètes d'un utilisateur"""
    try:
        with get_db_context() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            
            if not user:
                # Créer l'utilisateur
                user = get_or_create_user(
                    username, 
                    "Anne" if username == "anne" else "Mathieu",
                    db=db
                )
            
            # Stats des 7 derniers jours
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            
            summaries = db.query(GarminDailySummary).filter(
                GarminDailySummary.user_id == user.id,
                GarminDailySummary.date >= start_date
            ).all()
            
            activities = db.query(GarminActivity).filter(
                GarminActivity.user_id == user.id,
                GarminActivity.date_debut >= datetime.combine(start_date, datetime.min.time())
            ).all()
            
            # Calculer les stats
            total_pas = sum(s.pas for s in summaries)
            total_calories = sum(s.calories_actives for s in summaries)
            total_minutes = sum(s.minutes_actives for s in summaries)
            
            # Streak
            streak = _calculate_streak(user, summaries)
            
            return {
                "user": user,
                "summaries": summaries,
                "activities": activities,
                "total_pas": total_pas,
                "total_calories": total_calories,
                "total_minutes": total_minutes,
                "streak": streak,
                "garmin_connected": user.garmin_connected,
                "objectif_pas": user.objectif_pas_quotidien,
                "objectif_calories": user.objectif_calories_brulees,
            }
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return {}


def _calculate_streak(user: UserProfile, summaries: list) -> int:
    """Calcule le streak actuel"""
    if not summaries:
        return 0
    
    objectif = user.objectif_pas_quotidien or 10000
    summary_by_date = {s.date: s for s in summaries}
    
    streak = 0
    current_date = date.today()
    
    for _ in range(60):  # Max 60 jours
        summary = summary_by_date.get(current_date)
        if summary and summary.pas >= objectif:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def get_food_logs_today(username: str) -> list:
    """Récupère les logs alimentation du jour"""
    try:
        with get_db_context() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return []
            
            return db.query(FoodLog).filter(
                FoodLog.user_id == user.id,
                FoodLog.date == date.today()
            ).order_by(FoodLog.heure).all()
    except:
        return []


# ═══════════════════════════════════════════════════════════
# UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def render_user_switch():
    """Affiche le switch utilisateur"""
    current = get_current_user()
    
    col1, col2 = st.columns(2)
    
    with col1:
        btn_type = "primary" if current == "anne" else "secondary"
        if st.button("👩 Anne", key="switch_anne", use_container_width=True, type=btn_type):
            set_current_user("anne")
            st.rerun()
    
    with col2:
        btn_type = "primary" if current == "mathieu" else "secondary"
        if st.button("👨 Mathieu", key="switch_mathieu", use_container_width=True, type=btn_type):
            set_current_user("mathieu")
            st.rerun()


def render_dashboard(data: dict):
    """Affiche le dashboard principal"""
    user = data.get("user")
    if not user:
        st.warning("Utilisateur non trouvé")
        return
    
    st.subheader("📊 Dashboard")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        streak = data.get("streak", 0)
        st.metric("🔥 Streak", f"{streak} jours")
    
    with col2:
        today_summary = None
        for s in data.get("summaries", []):
            if s.date == date.today():
                today_summary = s
                break
        
        today_pas = today_summary.pas if today_summary else 0
        objectif = data.get("objectif_pas", 10000)
        pct = min(100, (today_pas / objectif) * 100)
        st.metric("👣 Pas aujourd'hui", f"{today_pas:,}", f"{pct:.0f}%")
    
    with col3:
        today_cal = today_summary.calories_actives if today_summary else 0
        st.metric("🔥 Calories", f"{today_cal}")
    
    with col4:
        garmin = "✅ Connecté" if data.get("garmin_connected") else "❌ Non connecté"
        st.metric("⌚ Garmin", garmin)
    
    # Graphique des 7 derniers jours
    st.markdown("---")
    render_weekly_chart(data.get("summaries", []), data.get("objectif_pas", 10000))


def render_weekly_chart(summaries: list, objectif: int):
    """Affiche le graphique des 7 derniers jours"""
    if not summaries:
        st.info("Pas de données Garmin. Connectez votre montre pour voir vos stats.")
        return
    
    # Préparer les données
    dates = []
    pas_values = []
    calories_values = []
    
    for i in range(7):
        d = date.today() - timedelta(days=6-i)
        dates.append(d.strftime("%a %d"))
        
        summary = next((s for s in summaries if s.date == d), None)
        pas_values.append(summary.pas if summary else 0)
        calories_values.append(summary.calories_actives if summary else 0)
    
    # Créer le graphique
    fig = go.Figure()
    
    # Barres pour les pas
    colors = ["#4CAF50" if p >= objectif else "#FFC107" for p in pas_values]
    fig.add_trace(go.Bar(
        x=dates,
        y=pas_values,
        name="Pas",
        marker_color=colors
    ))
    
    # Ligne objectif
    fig.add_hline(y=objectif, line_dash="dash", line_color="red", 
                  annotation_text=f"Objectif: {objectif:,}")
    
    fig.update_layout(
        title="📈 Pas quotidiens (7 derniers jours)",
        xaxis_title="",
        yaxis_title="Pas",
        showlegend=False,
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_activities(data: dict):
    """Affiche les activités sportives"""
    st.subheader("🏃 Activités récentes")
    
    activities = data.get("activities", [])
    
    if not activities:
        st.info("Aucune activité enregistrée cette semaine")
        return
    
    for act in sorted(activities, key=lambda x: x.date_debut, reverse=True)[:5]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                emoji = {
                    "running": "🏃",
                    "cycling": "🚴",
                    "swimming": "🏊",
                    "walking": "🚶",
                    "hiking": "🥾",
                    "strength": "💪",
                    "yoga": "🧘",
                }.get(act.type_activite.lower(), "🏋️")
                
                st.markdown(f"**{emoji} {act.nom}**")
                st.caption(act.date_debut.strftime("%d/%m à %H:%M"))
            
            with col2:
                st.write(f"⏱️ {act.duree_formatted}")
                if act.distance_metres:
                    st.write(f"📏 {act.distance_km:.1f} km")
            
            with col3:
                if act.calories:
                    st.write(f"🔥 {act.calories} kcal")
                if act.fc_moyenne:
                    st.write(f"❤️ {act.fc_moyenne} bpm")


def render_food_log(username: str):
    """Affiche et permet d'ajouter des logs alimentation"""
    st.subheader("🥗 Alimentation")
    
    tabs = st.tabs(["📝 Aujourd'hui", "➕ Ajouter"])
    
    with tabs[0]:
        logs = get_food_logs_today(username)
        
        if not logs:
            st.caption("Aucun repas enregistré aujourd'hui")
        else:
            total_cal = sum(l.calories_estimees or 0 for l in logs)
            st.metric("Total calories", f"{total_cal} kcal")
            
            for log in logs:
                repas_emoji = {
                    "petit_dejeuner": "🌅",
                    "dejeuner": "🌞",
                    "diner": "🌙",
                    "snack": "🍎"
                }.get(log.repas, "🍽️")
                
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{repas_emoji} {log.repas.replace('_', ' ').title()}**")
                        st.write(log.description)
                    with col2:
                        if log.calories_estimees:
                            st.write(f"~{log.calories_estimees} kcal")
                        if log.qualite:
                            st.write("⭐" * log.qualite)
    
    with tabs[1]:
        render_food_form(username)


def render_food_form(username: str):
    """Formulaire d'ajout de repas"""
    with st.form("add_food"):
        repas = st.selectbox("Repas", [
            ("petit_dejeuner", "🌅 Petit-déjeuner"),
            ("dejeuner", "🌞 Déjeuner"),
            ("diner", "🌙 Dîner"),
            ("snack", "🍎 Snack"),
        ], format_func=lambda x: x[1])
        
        description = st.text_area("Description *", placeholder="Ex: Salade, poulet, riz...")
        
        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories (estimées)", min_value=0, step=50)
        with col2:
            qualite = st.slider("Qualité", 1, 5, 3)
        
        notes = st.text_input("Notes (optionnel)")
        
        if st.form_submit_button("✅ Enregistrer", type="primary"):
            if not description:
                st.error("Description requise")
            else:
                try:
                    with get_db_context() as db:
                        user = db.query(UserProfile).filter_by(username=username).first()
                        if not user:
                            user = get_or_create_user(
                                username,
                                "Anne" if username == "anne" else "Mathieu",
                                db=db
                            )
                        
                        log = FoodLog(
                            user_id=user.id,
                            date=date.today(),
                            heure=datetime.now(),
                            repas=repas[0],
                            description=description,
                            calories_estimees=calories if calories > 0 else None,
                            qualite=qualite,
                            notes=notes or None
                        )
                        db.add(log)
                        db.commit()
                        st.success("✅ Repas enregistré!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def render_garmin_settings(data: dict):
    """Affiche les paramètres Garmin"""
    st.subheader("⌚ Garmin Connect")
    
    user = data.get("user")
    if not user:
        return
    
    if data.get("garmin_connected"):
        st.success("✅ Garmin connecté")
        
        # Dernière sync
        if user.garmin_token and user.garmin_token.derniere_sync:
            st.caption(f"Dernière sync: {user.garmin_token.derniere_sync.strftime('%d/%m/%Y %H:%M')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Synchroniser", type="primary"):
                with st.spinner("Synchronisation..."):
                    try:
                        service = get_garmin_service()
                        result = service.sync_user_data(user.id, days_back=7)
                        st.success(f"✅ {result['activities_synced']} activités, {result['summaries_synced']} jours sync")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur sync: {e}")
        
        with col2:
            if st.button("🔌 Déconnecter", type="secondary"):
                try:
                    service = get_garmin_service()
                    service.disconnect_user(user.id)
                    st.success("Garmin déconnecté")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    else:
        st.info("Connectez votre montre Garmin pour synchroniser vos données.")
        
        if st.button("🔗 Connecter Garmin", type="primary"):
            st.session_state["garmin_auth_user"] = user.id
            
            try:
                service = get_garmin_service()
                auth_url, request_token = service.get_authorization_url()
                
                st.session_state["garmin_request_token"] = request_token
                
                st.markdown(f"""
                ### Étapes de connexion:
                1. [Cliquez ici pour autoriser]({auth_url})
                2. Connectez-vous à Garmin Connect
                3. Autorisez l'accès
                4. Copiez le code de vérification ci-dessous
                """)
                
                verifier = st.text_input("Code de vérification")
                
                if st.button("✅ Valider"):
                    if verifier:
                        try:
                            service.complete_authorization(
                                user.id, 
                                verifier, 
                                request_token
                            )
                            st.success("✅ Garmin connecté!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur: {e}")
                    else:
                        st.error("Entrez le code de vérification")
            
            except ValueError as e:
                st.error(str(e))
                st.info("""
                Pour configurer Garmin:
                1. Créez une app sur developer.garmin.com
                2. Ajoutez dans .env.local:
                   - GARMIN_CONSUMER_KEY=xxx
                   - GARMIN_CONSUMER_SECRET=xxx
                """)


def render_objectifs(data: dict):
    """Affiche et permet de modifier les objectifs"""
    st.subheader("🎯 Objectifs")
    
    user = data.get("user")
    if not user:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_pas = st.number_input(
            "👣 Pas/jour", 
            min_value=1000, 
            max_value=50000, 
            value=user.objectif_pas_quotidien,
            step=1000
        )
    
    with col2:
        new_cal = st.number_input(
            "🔥 Calories actives/jour",
            min_value=100,
            max_value=2000,
            value=user.objectif_calories_brulees,
            step=50
        )
    
    with col3:
        new_min = st.number_input(
            "⏱️ Minutes actives/jour",
            min_value=10,
            max_value=180,
            value=user.objectif_minutes_actives,
            step=5
        )
    
    if st.button("💾 Sauvegarder objectifs"):
        try:
            with get_db_context() as db:
                u = db.query(UserProfile).filter_by(id=user.id).first()
                u.objectif_pas_quotidien = new_pas
                u.objectif_calories_brulees = new_cal
                u.objectif_minutes_actives = new_min
                db.commit()
                st.success("✅ Objectifs mis à jour!")
                st.rerun()
        except Exception as e:
            st.error(f"Erreur: {e}")


# ═══════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée du module Suivi Perso"""
    st.title("💪 Mon Suivi")
    
    # Switch utilisateur
    render_user_switch()
    
    username = get_current_user()
    display_name = "Anne" if username == "anne" else "Mathieu"
    emoji = "👩" if username == "anne" else "👨"
    
    st.caption(f"{emoji} {display_name}")
    
    # Charger les données
    data = get_user_data(username)
    
    # Tabs
    tabs = st.tabs(["📊 Dashboard", "🏃 Activités", "🥗 Alimentation", "🎯 Objectifs", "⌚ Garmin"])
    
    with tabs[0]:
        render_dashboard(data)
    
    with tabs[1]:
        render_activities(data)
    
    with tabs[2]:
        render_food_log(username)
    
    with tabs[3]:
        render_objectifs(data)
    
    with tabs[4]:
        render_garmin_settings(data)
