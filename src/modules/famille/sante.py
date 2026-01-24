"""
Module Santé & Sport - Suivi des routines, objectifs et entrées de santé
"""

import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import get_session
from src.core.models import HealthRoutine, HealthObjective, HealthEntry
from src.modules.famille.helpers import (
    get_routines_actives, 
    get_objectives_actifs,
    get_stats_santé_semaine,
    calculer_progression_objectif,
    clear_famille_cache
)


def charger_routines_santé():
    """Charge et retourne les routines de santé actives"""
    try:
        routines = get_routines_actives()
        return routines
    except Exception as e:
        st.error(f"❌ Erreur chargement routines: {str(e)}")
        return []


def ajouter_routine_santé(nom: str, type_routine: str, frequence: str, duree_minutes: int, 
                          intensite: str, calories: int, jours: list, notes: str = ""):
    """Ajoute une nouvelle routine de santé"""
    try:
        with get_session() as session:
            routine = HealthRoutine(
                nom=nom,
                type_routine=type_routine,
                frequence=frequence,
                duree_minutes=duree_minutes,
                intensite=intensite,
                jours_semaine=jours,
                calories_brulees_estimees=calories,
                notes=notes,
                actif=True
            )
            session.add(routine)
            session.commit()
            st.success(f"✅ Routine '{nom}' créée!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout routine: {str(e)}")
        return False


def charger_objectifs():
    """Charge les objectifs de santé en cours"""
    try:
        objectives = get_objectives_actifs()
        return objectives
    except Exception as e:
        st.error(f"❌ Erreur chargement objectifs: {str(e)}")
        return []


def ajouter_objectif(titre: str, categorie: str, valeur_cible: float, unite: str,
                     date_cible: date, priorite: str = "moyenne", notes: str = ""):
    """Ajoute un nouveau objectif de santé"""
    try:
        with get_session() as session:
            objective = HealthObjective(
                titre=titre,
                categorie=categorie,
                valeur_cible=valeur_cible,
                unite=unite,
                date_cible=date_cible,
                priorite=priorite,
                statut="en_cours",
                notes=notes
            )
            session.add(objective)
            session.commit()
            st.success(f"✅ Objectif '{titre}' créé!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout objectif: {str(e)}")
        return False


def charger_entrees_recentes(jours: int = 30):
    """Charge les entrées de santé des N derniers jours"""
    try:
        with get_session() as session:
            debut = date.today() - timedelta(days=jours)
            entries = session.query(HealthEntry).filter(HealthEntry.date >= debut).all()
            
            return [
                {
                    "id": e.id,
                    "date": e.date,
                    "type": e.type_activite,
                    "duree": e.duree_minutes,
                    "intensite": e.intensite,
                    "calories": e.calories_brulees,
                    "energie": e.note_energie,
                    "moral": e.note_moral,
                    "ressenti": e.ressenti
                }
                for e in entries
            ]
    except Exception as e:
        st.error(f"❌ Erreur chargement entrées: {str(e)}")
        return []


def ajouter_entree_santé(type_activite: str, duree_minutes: int, intensite: str,
                        calories: int = 0, energie: int = 5, moral: int = 5, ressenti: str = ""):
    """Ajoute une entrée de suivi santé quotidien"""
    try:
        with get_session() as session:
            entry = HealthEntry(
                date=date.today(),
                type_activite=type_activite,
                duree_minutes=duree_minutes,
                intensite=intensite,
                calories_brulees=calories if calories > 0 else None,
                note_energie=max(1, min(10, energie)),
                note_moral=max(1, min(10, moral)),
                ressenti=ressenti if ressenti else None
            )
            session.add(entry)
            session.commit()
            st.success(f"✅ Entrée '{type_activite}' enregistrée!")
            clear_famille_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur ajout entrée: {str(e)}")
        return False


def update_objectif_progression(objective_id: int, nouvelle_valeur: float):
    """Met à jour la progression d'un objectif"""
    try:
        with get_session() as session:
            objective = session.query(HealthObjective).get(objective_id)
            if objective:
                objective.valeur_actuelle = nouvelle_valeur
                if nouvelle_valeur >= objective.valeur_cible:
                    objective.statut = "atteint"
                session.commit()
                st.success("✅ Progression mise à jour!")
                clear_famille_cache()
                return True
    except Exception as e:
        st.error(f"❌ Erreur mise à jour: {str(e)}")
        return False


def app():
    """Interface principale du module Santé"""
    st.title("💪 Santé & Sport")
    
    tabs = st.tabs(["🏃 Routines", "🎯 Objectifs", "📊 Tracking", "🍎 Nutrition"])
    
    # ════════════════════════════════════════════════════════
    # TAB 1: ROUTINES
    # ════════════════════════════════════════════════════════
    with tabs[0]:
        st.header("Routines de Sport")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Mes routines actives")
            routines = charger_routines_santé()
            
            if routines:
                for r in routines:
                    with st.container(border=True):
                        col_info, col_action = st.columns([3, 1])
                        with col_info:
                            st.write(f"**{r['nom']}** ({r['type']})")
                            st.caption(f"{r['duree']} min | {r['frequence']} | {r['intensite']}")
                            if r.get('calories'):
                                st.caption(f"🔥 ~{r['calories']} cal")
                        with col_action:
                            if st.button("Faire", key=f"routine_{r['id']}", use_container_width=True):
                                ajouter_entree_santé(r['type'], r['duree'], r['intensite'], r.get('calories', 0))
            else:
                st.info("Aucune routine créée")
        
        with col2:
            st.subheader("Ajouter une routine")
            with st.form("form_routine"):
                nom = st.text_input("Nom")
                type_routine = st.selectbox("Type", 
                    ["Yoga", "Course", "Gym", "Marche", "Natation", "Vélo", "Autre"])
                duree = st.number_input("Durée (min)", 15, 120, 30)
                intensite = st.radio("Intensité", ["basse", "modérée", "haute"])
                frequence = st.text_input("Fréquence", "3x/semaine")
                calories = st.number_input("Calories (~)", 0, 1000, 200)
                notes = st.text_area("Notes", height=80)
                
                if st.form_submit_button("➕ Créer", use_container_width=True):
                    if nom and type_routine:
                        ajouter_routine_santé(nom, type_routine, frequence, duree, intensite, calories, [], notes)
    
    # ════════════════════════════════════════════════════════
    # TAB 2: OBJECTIFS
    # ════════════════════════════════════════════════════════
    with tabs[1]:
        st.header("Objectifs Santé")
        
        objectives = charger_objectifs()
        
        if objectives:
            # Afficher progression visuelle
            for obj in objectives:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{obj['titre']}**")
                        
                        # Barre de progression
                        progress = obj['progression'] / 100.0
                        st.progress(progress)
                        
                        # Détails
                        col_details = st.columns(3)
                        with col_details[0]:
                            st.metric("Progression", f"{obj['progression']:.0f}%")
                        with col_details[1]:
                            st.metric("Valeur", f"{obj['valeur_actuelle'] or 0:.1f} / {obj['valeur_cible']:.1f} {obj['unite']}")
                        with col_details[2]:
                            jours = obj['jours_restants']
                            couleur = "🟢" if jours > 7 else "🟡" if jours > 0 else "🔴"
                            st.metric("Délai", f"{couleur} {jours}j")
                    
                    with col2:
                        priority_colors = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
                        st.write(f"{priority_colors.get(obj['priorite'], '⚪')} {obj['priorite']}")
            
            # Formulaire mise à jour progression
            st.divider()
            st.subheader("Mettre à jour progression")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                selected_obj = st.selectbox("Objectif", 
                    [f"{o['titre']} ({o['valeur_cible']} {o['unite']})" for o in objectives])
                obj = objectives[[f"{o['titre']} ({o['valeur_cible']} {o['unite']})" for o in objectives].index(selected_obj)]
            
            with col2:
                nouvelle_valeur = st.number_input("Nouvelle valeur", 0.0, obj['valeur_cible'] * 2, 
                                                 obj['valeur_actuelle'] or 0.0)
            with col3:
                st.write("")  # Spacing
                if st.button("✅ Mettre à jour", use_container_width=True):
                    update_objectif_progression(obj['id'], nouvelle_valeur)
        else:
            st.info("Aucun objectif créé")
        
        st.divider()
        st.subheader("Créer un nouvel objectif")
        with st.form("form_objective"):
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Titre")
                categorie = st.text_input("Catégorie", "Fitness")
                valeur_cible = st.number_input("Valeur cible", 1.0, 1000.0, 10.0)
            with col2:
                unite = st.text_input("Unité", "km")
                date_cible = st.date_input("Date cible")
                priorite = st.radio("Priorité", ["basse", "moyenne", "haute"])
            
            notes = st.text_area("Notes")
            
            if st.form_submit_button("➕ Créer objectif", use_container_width=True):
                if titre and valeur_cible and date_cible:
                    ajouter_objectif(titre, categorie, valeur_cible, unite, date_cible, priorite, notes)
    
    # ════════════════════════════════════════════════════════
    # TAB 3: TRACKING
    # ════════════════════════════════════════════════════════
    with tabs[2]:
        st.header("Suivi Quotidien")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Ajouter une entrée
            st.subheader("Enregistrer une activité")
            with st.form("form_entry"):
                col_form = st.columns(2)
                with col_form[0]:
                    type_activite = st.text_input("Activité", "Course")
                    duree = st.number_input("Durée (min)", 10, 180, 30)
                with col_form[1]:
                    intensite = st.radio("Intensité", ["basse", "modérée", "haute"], horizontal=True)
                    calories = st.number_input("Calories", 0, 2000, 200)
                
                col_notes = st.columns(2)
                with col_notes[0]:
                    energie = st.slider("Énergie", 1, 10, 7)
                with col_notes[1]:
                    moral = st.slider("Moral", 1, 10, 7)
                
                ressenti = st.text_area("Ressenti", height=60, placeholder="Comment tu te sens?")
                
                if st.form_submit_button("✅ Enregistrer", use_container_width=True):
                    ajouter_entree_santé(type_activite, duree, intensite, calories, energie, moral, ressenti)
        
        with col2:
            # Stats de la semaine
            st.subheader("Semaine en cours")
            stats = get_stats_santé_semaine()
            
            st.metric("🏃 Séances", stats['nb_seances'])
            st.metric("⏱️ Temps", f"{stats['total_minutes']} min")
            st.metric("🔥 Calories", f"{stats['total_calories']:.0f}")
            st.metric("⚡ Énergie", f"{stats['energie_moyenne']:.1f}/10")
            st.metric("😊 Moral", f"{stats['moral_moyen']:.1f}/10")
        
        st.divider()
        
        # Graphique des 30 derniers jours
        st.subheader("Historique (30 jours)")
        entries = charger_entrees_recentes(30)
        
        if entries:
            df = pd.DataFrame(entries)
            df['date'] = pd.to_datetime(df['date'])
            
            # Graphique 1: Progression calories et durée
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=df['date'],
                y=df['calories'],
                name='Calories',
                marker_color='orange'
            ))
            fig1.add_trace(go.Scatter(
                x=df['date'],
                y=df['duree'],
                name='Durée (min)',
                yaxis='y2',
                line_color='blue'
            ))
            
            fig1.update_layout(
                title="Calories vs Durée",
                xaxis_title="Date",
                yaxis_title="Calories (kcal)",
                yaxis2=dict(title="Durée (min)", overlaying='y', side='right'),
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Graphique 2: Énergie et moral
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df['date'],
                y=df['energie'],
                name='Énergie',
                line_color='green',
                mode='lines+markers'
            ))
            fig2.add_trace(go.Scatter(
                x=df['date'],
                y=df['moral'],
                name='Moral',
                line_color='purple',
                mode='lines+markers'
            ))
            
            fig2.update_layout(
                title="Énergie & Moral",
                xaxis_title="Date",
                yaxis_title="Score (1-10)",
                height=400,
                hovermode='x'
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # ════════════════════════════════════════════════════════
    # TAB 4: NUTRITION
    # ════════════════════════════════════════════════════════
    with tabs[3]:
        st.header("🍎 Nutrition")
        
        st.info("💡 Principes généraux pour une bonne santé:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ À privilégier")
            points = [
                "Fruits et légumes frais (5 portions/jour)",
                "Protéines maigres (poulet, poisson, œufs)",
                "Féculents complets (riz brun, pâtes complètes)",
                "Produits laitiers ou substituts",
                "Huiles saines (olive, tournesol)",
                "Hydratation (1.5-2L eau/jour)"
            ]
            for point in points:
                st.write(f"✓ {point}")
        
        with col2:
            st.subheader("❌ À limiter")
            points = [
                "Sucres raffinés et sodas",
                "Graisses saturées (beurre, fritures)",
                "Aliments ultra-transformés",
                "Sel en excès",
                "Alcool régulier",
                "Repas trop lourds le soir"
            ]
            for point in points:
                st.write(f"✗ {point}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🥗 Exemple menu healthy")
            st.write("""
            **Petit-déjeuner:**
            - Oeufs brouillés + pain complet
            - Fruit frais + verre de lait
            
            **Déjeuner:**
            - Poulet grillé
            - Riz brun + légumes vapeur
            - Salade verte
            
            **Collation:**
            - Yaourt nature + fruit
            - Poignée de noix
            
            **Dîner:**
            - Poisson (saumon, truite)
            - Patate douce rôtie
            - Brocoli vapeur
            """)
        
        with col2:
            st.subheader("📋 Bonnes pratiques")
            practices = [
                ("🍴", "Manger lentement et bien mastiquer"),
                ("⏰", "3 repas réguliers + 2 collations"),
                ("🥤", "Boire de l'eau entre les repas"),
                ("🌙", "Dîner 2-3h avant le coucher"),
                ("🛒", "Préparer ses courses à l'avance"),
                ("📊", "Varier les aliments et couleurs"),
            ]
            for emoji, practice in practices:
                st.write(f"{emoji} {practice}")


if __name__ == "__main__":
    main()
