"""
Module Planning - Gestion du planning hebdomadaire
 Fonctionnalités complètes:
- Vue semaine avec édition en ligne
- Génération IA planning
- Historique et gestion plannings
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import logging

from src.services.planning import get_planning_service
from src.services.recettes import get_recette_service
from src.core.database import obtenir_contexte_db
from src.core.errors_base import ErreurValidation

# Logique métier pure
from src.domains.cuisine.logic.planning_logic import (
    get_debut_semaine,
    valider_planning,
    calculer_statistiques_planning
)

logger = logging.getLogger(__name__)

# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•
# CONSTANTES
# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_EMOJI = ["🟡", "🟠", "🟣", "🟢", "⚫", "🔴", "🟢"]
TYPES_REPAS = ["déjeuner", "dîner"]
REGIMES = ["Omnivore", "Végétarien", "Végan", "Sans gluten"]
TEMPS_CUISINE = ["Rapide (< 30 min)", "Moyen (30-60 min)", "Long (> 60 min)"]
BUDGETS = ["Bas (< 20ê‚¬)", "Moyen (20-40ê‚¬)", "Haut (> 40ê‚¬)"]


def app():
    """Point d'entrée module planning"""
    st.title("ðŸ“… Planning Semaine")
    st.caption("Gérez vos repas de la semaine et générez des plannings avec IA")

    tab_planning, tab_generer, tab_historique = st.tabs([
        "ðŸ“‹ Planning Actif", 
        " Générer avec IA", 
        "ðŸ“š Historique"
    ])

    with tab_planning:
        render_planning()

    with tab_generer:
        render_generer()

    with tab_historique:
        render_historique()


# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•
# SECTION 1: PLANNING ACTIF
# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

def render_planning():
    """Affiche et édite le planning actuel"""
    service = get_planning_service()
    recette_service = get_recette_service()
    
    if service is None:
        st.error("êŒ Service planning indisponible")
        return
    
    try:
        # Récupérer planning actif
        planning = service.get_planning()
        
        if not planning:
            st.warning("êš ï¸ Aucun planning actif pour cette semaine")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("êž• Créer nouveau planning", use_container_width=True, type="primary"):
                    st.session_state.go_to_generer = True
                    st.rerun()
            return
        
        # Afficher infos planning
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ðŸ“… Semaine du", planning.semaine_debut.strftime("%d/%m"))
        with col2:
            st.metric("ðŸ“Š Repas planifiés", len(planning.repas) if planning.repas else 0)
        with col3:
            genere_ia = "🤖 IA" if planning.genere_par_ia else "êœï¸ Manuel"
            st.metric("Créé par", genere_ia)
        
        st.divider()
        
        # Récupérer toutes recettes pour selectbox
        db = next(obtenir_contexte_db())
        from src.core.models import Recette
        recettes = db.query(Recette).all()
        recettes_dict = {r.nom: r.id for r in recettes}
        
        # Organiser repas par jour
        repas_par_jour = {}
        if planning.repas:
            for repas in planning.repas:
                jour_key = repas.date_repas.strftime("%Y-%m-%d")
                if jour_key not in repas_par_jour:
                    repas_par_jour[jour_key] = []
                repas_par_jour[jour_key].append(repas)
        
        # Afficher 7 jours
        for idx, jour_offset in enumerate(range(7)):
            jour_date = planning.semaine_debut + timedelta(days=jour_offset)
            jour_key = jour_date.strftime("%Y-%m-%d")
            jour_name = JOURS_SEMAINE[idx]
            emoji = JOURS_EMOJI[idx]
            
            with st.expander(f"{emoji} {jour_name} - {jour_date.strftime('%d/%m')}", expanded=(idx == 0)):
                repas_jour = repas_par_jour.get(jour_key, [])
                
                if not repas_jour:
                    st.info(f"Aucun repas planifié ce jour")
                    continue
                
                for repas in repas_jour:
                    col1, col2, col3, col4 = st.columns([1.5, 2, 1.5, 1])
                    
                    with col1:
                        type_emoji = "🍽️" if repas.type_repas == "dîner" else "☕"
                        st.write(f"**{type_emoji} {repas.type_repas.capitalize()}**")
                    
                    with col2:
                        # Selectbox recette
                        recette_options = ["-- Aucune --"] + list(recettes_dict.keys())
                        recette_current = repas.recette.nom if repas.recette else "-- Aucune --"
                        
                        new_recette = st.selectbox(
                            "Recette",
                            recette_options,
                            index=recette_options.index(recette_current) if recette_current in recette_options else 0,
                            key=f"recette_{repas.id}",
                            label_visibility="collapsed"
                        )
                        
                        # Mettre à jour si changement
                        if new_recette != "-- Aucune --" and new_recette != recette_current:
                            try:
                                from src.core.models import Repas as RepasModel
                                repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                if repas_db:
                                    repas_db.recette_id = recettes_dict[new_recette]
                                    db.commit()
                                    st.success(f"êœ… Recette mise à jour")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"êŒ Erreur: {str(e)}")
                    
                    with col3:
                        # Toggle "Préparé"
                        prepared = st.checkbox(
                            "Préparé",
                            value=repas.prepare,
                            key=f"prepared_{repas.id}"
                        )
                        if prepared != repas.prepare:
                            try:
                                from src.core.models import Repas as RepasModel
                                repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                if repas_db:
                                    repas_db.prepare = prepared
                                    db.commit()
                            except Exception as e:
                                st.error(f"êŒ Erreur: {str(e)}")
                    
                    with col4:
                        if st.button("ðŸ“", key=f"edit_notes_{repas.id}", help="Ã‰diter notes"):
                            st.session_state[f"editing_notes_{repas.id}"] = True
                    
                    # Notes editor
                    if st.session_state.get(f"editing_notes_{repas.id}"):
                        notes = st.text_area(
                            "Notes",
                            value=repas.notes or "",
                            key=f"notes_{repas.id}",
                            height=80
                        )
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("êœ… Sauvegarder", key=f"save_notes_{repas.id}"):
                                try:
                                    from src.core.models import Repas as RepasModel
                                    repas_db = db.query(RepasModel).filter_by(id=repas.id).first()
                                    if repas_db:
                                        repas_db.notes = notes if notes else None
                                        db.commit()
                                        st.session_state[f"editing_notes_{repas.id}"] = False
                                        st.success("êœ… Notes sauvegardées")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"êŒ Erreur: {str(e)}")
                        with col_b:
                            if st.button("êŒ Annuler", key=f"cancel_notes_{repas.id}"):
                                st.session_state[f"editing_notes_{repas.id}"] = False
                                st.rerun()
        
        st.divider()
        
        # Actions de masse
        st.subheader("êš™ï¸ Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("êœ… Marquer tout préparé", use_container_width=True):
                try:
                    from src.core.models import Repas as RepasModel
                    db.query(RepasModel).filter_by(planning_id=planning.id).update({"prepare": True})
                    db.commit()
                    st.success("êœ… Tous les repas marqués comme préparés")
                    st.rerun()
                except Exception as e:
                    st.error(f"êŒ Erreur: {str(e)}")
        
        with col2:
            if st.button("ðŸ“‹ Dupliquer (semaine suiv.)", use_container_width=True):
                try:
                    from src.core.models import Planning as PlanningModel, Repas as RepasModel
                    
                    # Créer nouveau planning
                    semaine_suivante = planning.semaine_debut + timedelta(days=7)
                    semaine_fin = planning.semaine_fin + timedelta(days=7)
                    
                    nouveau = PlanningModel(
                        nom=f"Planning {semaine_suivante.strftime('%d/%m/%Y')}",
                        semaine_debut=semaine_suivante,
                        semaine_fin=semaine_fin,
                        actif=False,
                        genere_par_ia=planning.genere_par_ia
                    )
                    db.add(nouveau)
                    db.flush()
                    
                    # Dupliquer repas
                    for repas in planning.repas:
                        nouveau_repas = RepasModel(
                            planning_id=nouveau.id,
                            recette_id=repas.recette_id,
                            date_repas=repas.date_repas + timedelta(days=7),
                            type_repas=repas.type_repas,
                            portion_ajustee=repas.portion_ajustee,
                            notes=repas.notes
                        )
                        db.add(nouveau_repas)
                    
                    db.commit()
                    st.success("êœ… Planning dupliqué pour la semaine suivante")
                    st.rerun()
                except Exception as e:
                    st.error(f"êŒ Erreur: {str(e)}")
        
        with col3:
            if st.button("ðŸ”’ Archiver planning", use_container_width=True):
                try:
                    from src.core.models import Planning as PlanningModel
                    planning_db = db.query(PlanningModel).filter_by(id=planning.id).first()
                    if planning_db:
                        planning_db.actif = False
                        db.commit()
                        st.success("êœ… Planning archivé")
                        st.rerun()
                except Exception as e:
                    st.error(f"êŒ Erreur: {str(e)}")
    
    except Exception as e:
        st.error(f"êŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_planning: {e}")


# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•
# SECTION 2: GÃ‰NÃ‰RER PLANNING AVEC IA
# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

def render_generer():
    """Générer un planning hebdomadaire avec IA"""
    service = get_planning_service()
    
    if service is None:
        st.error("êŒ Service planning indisponible")
        return
    
    st.subheader("🤖 Générer Planning Hebdomadaire")
    
    try:
        # Date de début (défaut lundi prochain)
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        default_start = today + timedelta(days=days_until_monday)
        
        col1, col2 = st.columns(2)
        
        with col1:
            semaine_debut = st.date_input(
                "ðŸ“… Semaine à partir du",
                value=default_start,
                format="YYYY-MM-DD"
            )
        
        with col2:
            # Vérifier que c'est un lundi
            if semaine_debut.weekday() != 0:
                st.warning("êš ï¸ Veuillez sélectionner un lundi")
                semaine_debut = semaine_debut - timedelta(days=semaine_debut.weekday())
        
        st.divider()
        st.subheader("🍽️ Préférences")
        
        col1, col2 = st.columns(2)
        with col1:
            regime = st.radio("Régime alimentaire", REGIMES, index=0)
        with col2:
            temps = st.radio("Temps de cuisine", TEMPS_CUISINE, index=1)
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.radio("Budget", BUDGETS, index=1)
        with col2:
            allergies = st.multiselect("Allergies à éviter", [
                "Arachides", "Noix", "Lait", "Gluten", "Å’ufs", "Fruits de mer"
            ])
        
        notes_prefs = st.text_area(
            "Notes additionnelles",
            placeholder="Ex: pas de viande rouge, préférez les pÃ✅tes...",
            height=60
        )
        
        st.divider()
        
        if st.button("🚀 Générer Planning avec IA", use_container_width=True, type="primary"):
            try:
                with st.spinner("🤖 Génération en cours..."):
                    # Préparer préférences
                    preferences = {
                        "regime": regime,
                        "temps_cuisine": temps,
                        "budget": budget,
                        "allergies": allergies,
                        "notes": notes_prefs
                    }
                    
                    # Générer planning
                    planning = service.generer_planning_ia(
                        semaine_debut=semaine_debut,
                        preferences=preferences
                    )
                    
                    if planning:
                        st.success("êœ… Planning généré avec succès!")
                        
                        # Afficher preview
                        st.subheader("ðŸ“‹ Aperçu du planning")
                        
                        # Récupérer planning complet
                        planning_complet = service.get_planning_complet(planning.id)
                        
                        if planning_complet:
                            # Créer tableau
                            data = []
                            for jour_offset in range(7):
                                jour_date = semaine_debut + timedelta(days=jour_offset)
                                jour_key = jour_date.strftime("%Y-%m-%d")
                                jour_name = JOURS_SEMAINE[jour_offset]
                                
                                repas_jour = planning_complet.get("repas_par_jour", {}).get(jour_key, [])
                                
                                for repas in repas_jour:
                                    data.append({
                                        "Jour": jour_name,
                                        "Date": jour_date.strftime("%d/%m"),
                                        "Type": repas["type_repas"].capitalize(),
                                        "Recette/Notes": repas.get("recette_nom", repas.get("notes", ""))
                                    })
                            
                            if data:
                                df = pd.DataFrame(data)
                                st.dataframe(df, use_container_width=True)
                        
                        st.divider()
                        st.info("êœ… Planning sauvegardé en BD et prêt à utiliser!")
                        
                        if st.button("ðŸ“‹ Voir planning", use_container_width=True):
                            st.session_state.go_to_planning = True
                            st.rerun()
                    else:
                        st.error("êŒ Erreur lors de la génération")
            
            except Exception as e:
                st.error(f"êŒ Erreur: {str(e)}")
                logger.error(f"Erreur generer_planning_ia: {e}")
    
    except Exception as e:
        st.error(f"êŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_generer: {e}")


# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•
# SECTION 3: HISTORIQUE PLANNINGS
# ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•ê•

def render_historique():
    """Affiche historique des plannings"""
    service = get_planning_service()
    
    if service is None:
        st.error("êŒ Service planning indisponible")
        return
    
    st.subheader("ðŸ“š Historique des Plannings")
    
    try:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_debut = st.date_input("Du", value=date.today() - timedelta(days=90))
        with col2:
            date_fin = st.date_input("Au", value=date.today() + timedelta(days=30))
        with col3:
            filter_ia = st.checkbox("Générés par IA seulement")
        
        st.divider()
        
        # Récupérer tous plannings
        with obtenir_contexte_db() as db:
            from src.core.models import Planning as PlanningModel
            
            query = db.query(PlanningModel)
            query = query.filter(PlanningModel.semaine_debut >= date_debut)
            query = query.filter(PlanningModel.semaine_debut <= date_fin)
            
            if filter_ia:
                query = query.filter(PlanningModel.genere_par_ia == True)
            
            plannings = query.order_by(PlanningModel.semaine_debut.desc()).all()
        
        if not plannings:
            st.info("Aucun planning trouvé")
            return
        
        st.metric("ðŸ“Š Total plannings", len(plannings))
        
        st.divider()
        
        # Tableau plannings
        for planning in plannings:
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1, 0.8, 0.8])
            
            with col1:
                genere_icon = "🤖" if planning.genere_par_ia else "êœï¸"
                actif_icon = "✅" if planning.actif else "⚫"
                st.write(f"**{genere_icon} {planning.nom}** {actif_icon}")
                st.caption(f"ðŸ“… {planning.semaine_debut.strftime('%d/%m')} ê†’ {planning.semaine_fin.strftime('%d/%m')}")
            
            with col2:
                repas_count = len(planning.repas) if planning.repas else 0
                st.metric("ðŸ“Š Repas", repas_count)
            
            with col3:
                created = planning.cree_le.strftime("%d/%m/%y") if planning.cree_le else "N/A"
                st.caption(f"Créé: {created}")
            
            with col4:
                if st.button("ðŸ“‚", key=f"load_{planning.id}", help="Charger ce planning"):
                    try:
                        # Désactiver tous les autres
                        db.query(PlanningModel).filter(PlanningModel.actif == True).update({"actif": False})
                        # Activer celui-ci
                        planning_db = db.query(PlanningModel).filter_by(id=planning.id).first()
                        if planning_db:
                            planning_db.actif = True
                            db.commit()
                            st.success("êœ… Planning chargé")
                            st.rerun()
                    except Exception as e:
                        st.error(f"êŒ Erreur: {str(e)}")
            
            with col5:
                if st.button("ðŸ—‘ï¸", key=f"delete_{planning.id}", help="Supprimer ce planning"):
                    try:
                        db.query(PlanningModel).filter_by(id=planning.id).delete()
                        db.commit()
                        st.success("êœ… Planning supprimé")
                        st.rerun()
                    except Exception as e:
                        st.error(f"êŒ Erreur: {str(e)}")
            
            st.divider()

    except Exception as e:
        st.error(f"êŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_historique: {e}")



