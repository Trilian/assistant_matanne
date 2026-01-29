"""
Module Projets - Gestion des projets maison avec IA intégrée
Priorisation intelligente, estimation de durée, suivi de progression
"""

from datetime import date, datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.core.database import get_db_context
from src.core.models import Project, ProjectTask
from src.core.decorators import with_db_session
from src.services.base_ai_service import BaseAIService
from src.core.ai import ClientIA

# Logique métier pure
from src.modules.maison.projets_logic import (
    calculer_progression,
    calculer_jours_restants,
    calculer_urgence_projet
)

from src.modules.maison.helpers import (
    charger_projets,
    get_projets_urgents,
    get_stats_projets,
    clear_maison_cache
)


# ════════════════════════════════════════════════════════════════════════════
# SERVICE IA PROJETS
# ════════════════════════════════════════════════════════════════════════════


class ProjetsService(BaseAIService):
    """Service IA pour gestion intelligente des projets"""
    
    def __init__(self, client: ClientIA = None):
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="projets",
            default_ttl=3600,
            service_name="projets"
        )
    
    async def suggerer_taches(self, nom_projet: str, description: str) -> str:
        """Suggère des tâches pour un projet"""
        prompt = f"""Pour le projet "{nom_projet}" : {description}
Suggère 5-7 tâches concrètes et numérotées. Ordonne par ordre logique."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de projets domestiques",
            max_tokens=700
        )
    
    async def estimer_duree(self, nom_projet: str, complexite: str = "moyen") -> str:
        """Estime la durée totale d'un projet"""
        prompt = f"""Pour un projet "{nom_projet}" de complexité {complexite},
estime la durée totale et le temps par phase (préparation, exécution, finition)."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en estimation de projets domestiques",
            max_tokens=400
        )
    
    async def prioriser_taches(self, nom_projet: str, taches_texte: str) -> str:
        """Priorise les tâches pour un projet"""
        prompt = f"""Pour le projet "{nom_projet}", réordonne ces tâches par priorité:
{taches_texte}

Explique brièvement l'ordre."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en priorisation et planification",
            max_tokens=500
        )
    
    async def conseil_blocages(self, nom_projet: str, description: str) -> str:
        """Suggère comment éviter les blocages"""
        prompt = f"""Pour "{nom_projet}" : {description}
Quels sont les 3 risques/blocages principaux et comment les éviter?"""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en gestion de risques de projets",
            max_tokens=500
        )


def get_projets_service() -> ProjetsService:
    """Factory pour obtenir le service projets"""
    return ProjetsService()


# ════════════════════════════════════════════════════════════════════════════
# HELPERS MÉTIER
# ════════════════════════════════════════════════════════════════════════════


@with_db_session
def creer_projet(
    nom: str,
    description: str,
    categorie: str,
    priorite: str,
    date_fin: date = None,
    db=None
) -> int:
    """Crée un nouveau projet"""
    try:
        projet = Project(
            nom=nom,
            description=description,
            statut="en_cours",
            priorite=priorite,
            date_fin_prevue=date_fin
        )
        db.add(projet)
        db.commit()
        db.refresh(projet)
        clear_maison_cache()
        return projet.id
    except Exception as e:
        st.error(f"❌ Erreur création projet: {e}")
        return None


@with_db_session
def ajouter_tache(
    project_id: int,
    nom: str,
    description: str = "",
    priorite: str = "moyenne",
    date_echéance: date = None,
    db=None
) -> bool:
    """Ajoute une tâche à un projet"""
    try:
        tache = ProjectTask(
            project_id=project_id,
            nom=nom,
            description=description,
            priorite=priorite,
            date_echéance=date_echéance,
            statut="à_faire"
        )
        db.add(tache)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout tâche: {e}")
        return False


@with_db_session
def marquer_tache_done(task_id: int, db=None) -> bool:
    """Marque une tâche comme terminée"""
    try:
        tache = db.query(ProjectTask).get(task_id)
        if tache:
            tache.statut = "terminé"
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur mise à jour: {e}")
    return False


@with_db_session
def marquer_projet_done(project_id: int, db=None) -> bool:
    """Marque un projet comme terminé"""
    try:
        projet = db.query(Project).get(project_id)
        if projet:
            projet.statut = "terminé"
            projet.date_fin_reelle = date.today()
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"❌ Erreur: {e}")
    return False


# ════════════════════════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════


def app():
    """Point d'entrée module Projets"""
    st.title("🏗️ Projets Maison")
    st.caption("Gestion et priorisation intelligente des projets")
    
    service = get_projets_service()
    
    # ════════════════════════════════════════════════════════════════════════
    # ALERTES URGENTES
    # ════════════════════════════════════════════════════════════════════════
    
    urgents = get_projets_urgents()
    
    if urgents:
        st.warning(f"⚠️ **{len(urgents)} projet(s) nécessitent attention**")
        for urgent in urgents[:3]:
            if urgent["type"] == "RETARD":
                st.error(f"🔴 **{urgent['projet']}** : {urgent['message']}")
            else:
                st.warning(f"🟡 **{urgent['projet']}** : {urgent['message']}")
        st.markdown("---")
    
    # ════════════════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ════════════════════════════════════════════════════════════════════════
    
    stats = get_stats_projets()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", stats["total"])
    
    with col2:
        st.metric("En cours", stats["en_cours"])
    
    with col3:
        st.metric("Terminés", stats["termines"])
    
    with col4:
        st.metric("Progression", f"{stats['avg_progress']:.0f}%")
    
    st.markdown("---")
    
    # ════════════════════════════════════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════════════════════════════════════
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 En cours", "🤖 Assistant IA", "➕ Nouveau", "📊 Tableau"]
    )
    
    # ════════════════════════════════════════════════════════════════════════
    # TAB 1: PROJETS EN COURS
    # ════════════════════════════════════════════════════════════════════════
    
    with tab1:
        st.subheader("Projets actifs")
        
        df_projets = charger_projets("en_cours")
        
        if df_projets.empty:
            st.info("Aucun projet en cours")
        else:
            for idx, projet in df_projets.iterrows():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {projet['nom']}")
                    
                    # Barre de progression
                    st.progress(projet['progress'] / 100)
                    st.caption(f"✅ {projet['progress']:.0f}% • {projet['taches_count']} tâches")
                    
                    if projet['description']:
                        st.caption(projet['description'][:100] + "...")
                    
                    # Priorité et échéance
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        badge = "🔴" if projet['priorite'] == "urgente" else "🟠" if projet['priorite'] == "haute" else "🟡"
                        st.caption(f"{badge} {projet['priorite'].upper()}")
                    
                    with col_b:
                        if projet['jours_restants'] is not None:
                            jours = projet['jours_restants']
                            if jours < 0:
                                st.caption(f"📅 **En retard de {-jours}j**")
                            elif jours == 0:
                                st.caption("📅 **À livrer aujourd'hui!**")
                            else:
                                st.caption(f"📅 {jours}j restants")
                
                with col2:
                    if st.button("✅ Terminer", key=f"done_{projet['id']}", use_container_width=True):
                        if marquer_projet_done(projet['id']):
                            st.success("Projet marqué comme terminé!")
                            st.rerun()
                
                # Afficher les tâches
                with st.expander("Voir tâches"):
                    with get_db_context() as session:
                        taches = session.query(ProjectTask).filter_by(
                            project_id=projet['id']
                        ).all()
                        
                        if not taches:
                            st.caption("Aucune tâche")
                        else:
                            for t in taches:
                                col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
                                
                                with col_t1:
                                    emoji = "✅" if t.statut == "terminé" else "⏳"
                                    st.caption(f"{emoji} {t.nom}")
                                
                                with col_t2:
                                    if t.date_echéance:
                                        st.caption(t.date_echéance.strftime("%d/%m"))
                                
                                with col_t3:
                                    if t.statut != "terminé":
                                        if st.button("✓", key=f"task_{t.id}", use_container_width=True):
                                            if marquer_tache_done(t.id):
                                                st.rerun()
                
                st.divider()
    
    # ════════════════════════════════════════════════════════════════════════
    # TAB 2: ASSISTANT IA
    # ════════════════════════════════════════════════════════════════════════
    
    with tab2:
        st.subheader("🤖 Assistant Projets IA")
        
        col_ia1, col_ia2 = st.columns(2)
        
        # Suggérer tâches
        with col_ia1:
            st.markdown("#### 📋 Suggérer des tâches")
            
            projet_nom_ia = st.text_input("Nom du projet", placeholder="Ex: Rénover cuisine")
            projet_desc_ia = st.text_area(
                "Description",
                placeholder="Détails du projet...",
                height=100
            )
            
            if st.button("💡 Générer tâches", key="ia_taches", use_container_width=True):
                if projet_nom_ia:
                    with st.spinner("IA analyse le projet..."):
                        try:
                            import asyncio
                            taches = asyncio.run(service.suggerer_taches(projet_nom_ia, projet_desc_ia))
                            if taches:
                                st.success(taches)
                        except Exception as e:
                            st.warning(f"⚠️ IA indisponible: {e}")
        
        # Estimer durée
        with col_ia2:
            st.markdown("#### ⏱️ Estimer la durée")
            
            projet_nom_dur = st.text_input("Nom du projet", placeholder="Ex: Repeindre salon", key="dur")
            complexite = st.selectbox(
                "Complexité",
                ["simple", "moyen", "complexe"],
                key="complex"
            )
            
            if st.button("🔮 Estimer durée", key="ia_duree", use_container_width=True):
                if projet_nom_dur:
                    with st.spinner("Estimation en cours..."):
                        try:
                            import asyncio
                            duree = asyncio.run(service.estimer_duree(projet_nom_dur, complexite))
                            if duree:
                                st.info(duree)
                        except Exception as e:
                            st.warning(f"⚠️ IA indisponible: {e}")
        
        st.markdown("---")
        
        # Analyser blocages
        st.markdown("#### ⚠️ Analyser les risques")
        
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            projet_risque = st.text_input("Nom du projet", placeholder="Ex: Installer piscine")
        
        with col_r2:
            if st.button("🔍 Identifier risques", use_container_width=True):
                if projet_risque:
                    with st.spinner("Analyse des risques..."):
                        try:
                            import asyncio
                            risques = asyncio.run(service.conseil_blocages(projet_risque, ""))
                            if risques:
                                st.warning(risques)
                        except Exception as e:
                            st.warning(f"⚠️ IA indisponible: {e}")
    
    # ════════════════════════════════════════════════════════════════════════
    # TAB 3: CRÉER NOUVEAU PROJET
    # ════════════════════════════════════════════════════════════════════════
    
    with tab3:
        st.subheader("Créer un nouveau projet")
        
        with st.form("form_nouveau_projet"):
            nom = st.text_input("Nom du projet *", placeholder="Ex: Aménagement jardin")
            
            description = st.text_area(
                "Description",
                height=100,
                placeholder="Objectifs, détails du projet..."
            )
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                priorite = st.selectbox("Priorité", ["basse", "moyenne", "haute", "urgente"])
            
            with col_p2:
                date_fin = st.date_input("Date d'échéance (optionnel)", value=None)
            
            submitted = st.form_submit_button("💾 Créer le projet", type="primary")
            
            if submitted:
                if not nom:
                    st.error("Nom obligatoire")
                else:
                    project_id = creer_projet(nom, description, "Général", priorite, date_fin)
                    if project_id:
                        st.success(f"✅ Projet '{nom}' créé!")
                        st.balloons()
                        st.rerun()
        
        st.markdown("---")
        
        # Templates
        st.markdown("### 📋 Templates rapides")
        
        templates = [
            {
                "nom": "Rénovation cuisine",
                "taches": ["Planifier layout", "Acheter matériaux", "Préparer", "Installer", "Finitions"]
            },
            {
                "nom": "Aménagement jardin",
                "taches": ["Préparer sol", "Acheter plants", "Planter", "Installer arrosage", "Entretien"]
            },
            {
                "nom": "Repeindre chambre",
                "taches": ["Choisir couleurs", "Préparer murs", "Acheter peinture", "Peindre", "Finitions"]
            }
        ]
        
        for templ in templates:
            if st.button(f"📋 {templ['nom']}", use_container_width=True):
                p_id = creer_projet(templ["nom"], "", "Général", "moyenne")
                if p_id:
                    for tache in templ["taches"]:
                        ajouter_tache(p_id, tache)
                    st.success("✅ Projet template créé avec tâches!")
                    st.rerun()
    
    # ════════════════════════════════════════════════════════════════════════
    # TAB 4: TABLEAU DE BORD
    # ════════════════════════════════════════════════════════════════════════
    
    with tab4:
        st.subheader("📊 Vue d'ensemble")
        
        df_all = charger_projets()
        
        if df_all.empty:
            st.info("Aucun projet")
        else:
            # Graphique progression
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=df_all["nom"],
                        y=df_all["progress"],
                        marker_color="green"
                    )
                ]
            )
            fig.update_layout(
                title="Progression des projets (%)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau
            st.dataframe(
                df_all[["nom", "priorite", "progress", "taches_count", "jours_restants"]],
                use_container_width=True,
                hide_index=True
            )


if __name__ == "__main__":
    app()
