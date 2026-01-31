"""
Module Entretien - Gestion du ménage et routines domestiques
Suivi des tÃ¢ches quotidiennes, planification hebdomadaire, IA d'optimisation
"""

from datetime import date, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.core.database import get_db_context
from src.core.models import Routine, RoutineTask
from src.core.decorators import with_db_session
from src.services.base_ai_service import BaseAIService
from src.core.ai import ClientIA

# Logique métier pure
from src.domains.maison.logic.entretien_logic import (
    calculer_frequence_tache,
    determiner_urgence_tache,
    suggerer_horaire_optimal
)

from src.domains.maison.logic.helpers import (
    charger_routines,
    get_taches_today,
    get_stats_entretien,
    clear_maison_cache
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SERVICE IA ENTRETIEN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class EntretienService(BaseAIService):
    """Service IA pour optimisation du ménage et routines"""
    
    def __init__(self, client: ClientIA = None):
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="entretien",
            default_ttl=3600,
            service_name="entretien"
        )
    
    async def creer_routine(self, nom: str, description: str = "") -> str:
        """Crée une routine avec tÃ¢ches suggérées"""
        prompt = f"""Pour la routine "{nom}" {description},
suggère 5-8 tÃ¢ches pratiques et dans un ordre logique.
Format: "- TÃ¢che : description courte"."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique",
            max_tokens=600
        )
    
    async def optimiser_semaine(self, types_taches: str) -> str:
        """Optimise la distribution des tÃ¢ches sur la semaine"""
        prompt = f"""Propose une répartition optimale pour ces tÃ¢ches ménagères:
{types_taches}

Organise par jour (Lun-Dim) pour équilibrer la charge et ne pas surcharger un jour."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en planification et organisation du temps",
            max_tokens=700
        )
    
    async def conseil_temps_estime(self, tache: str) -> str:
        """Estime le temps pour une tÃ¢che ménagère"""
        prompt = f"""Pour la tÃ¢che ménagère "{tache}",
estime le temps nécessaire (min/max), la fréquence idéale et des astuces."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en optimisation du ménage",
            max_tokens=400
        )
    
    async def conseil_efficacite(self) -> str:
        """Donne des astuces pour gagner du temps au ménage"""
        prompt = """Donne 5 astuces pratiques pour rendre le ménage plus efficace et moins chronophage.
Sois spécifique et actionnable."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique et efficacité",
            max_tokens=500
        )


def get_entretien_service() -> EntretienService:
    """Factory pour obtenir le service entretien"""
    return EntretienService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS MÃ‰TIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@with_db_session
def creer_routine(
    nom: str,
    categorie: str,
    frequence: str,
    description: str = "",
    db=None
) -> int:
    """Crée une nouvelle routine"""
    try:
        routine = Routine(
            nom=nom,
            categorie=categorie,
            frequence=frequence,
            description=description,
            actif=True
        )
        db.add(routine)
        db.commit()
        db.refresh(routine)
        clear_maison_cache()
        return routine.id
    except Exception as e:
        st.error(f"âŒ Erreur création routine: {e}")
        return None


@with_db_session
@with_db_session
def ajouter_tache_routine(
    routine_id: int,
    nom: str,
    description: str = "",
    heure_prevue: str = None,
    ordre: int = 1,
    db=None
) -> bool:
    """Ajoute une tÃ¢che à une routine"""
    try:
        tache = RoutineTask(
            routine_id=routine_id,
            nom=nom,
            description=description,
            heure_prevue=heure_prevue,
            ordre=ordre
        )
        db.add(tache)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"âŒ Erreur ajout tÃ¢che: {e}")
        return False


@with_db_session
def marquer_tache_faite(task_id: int, db=None) -> bool:
    """Marque une tÃ¢che comme faite aujourd'hui"""
    try:
        tache = db.query(RoutineTask).get(task_id)
        if tache:
            tache.fait_le = date.today()
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"âŒ Erreur: {e}")
    return False


@with_db_session
def desactiver_routine(routine_id: int, db=None) -> bool:
    """Désactive une routine"""
    try:
        routine = db.query(Routine).get(routine_id)
        if routine:
            routine.actif = False
            db.commit()
            clear_maison_cache()
            return True
    except Exception as e:
        st.error(f"âŒ Erreur: {e}")
    return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Point d'entrée module Entretien"""
    st.title("🧹 Entretien & Ménage")
    st.caption("Gestion des routines et tÃ¢ches ménagères avec IA")
    
    service = get_entretien_service()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # STATISTIQUES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    stats = get_stats_entretien()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Routines actives", stats["routines_actives"])
    
    with col2:
        st.metric("TÃ¢ches total", stats["total_taches"])
    
    with col3:
        st.metric("Faites aujourd'hui", stats["taches_today"])
    
    with col4:
        st.metric("Progression", f"{stats['completion_today']:.0f}%")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    tab1, tab2, tab3, tab4 = st.tabs(
        ["â˜‘ï¸ Aujourd'hui", "🍽️ Routines", "– Assistant IA", "âž• Créer"]
    )
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: TÃ‚CHES AUJOURD'HUI
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab1:
        st.subheader("Checklist d'aujourd'hui")
        
        taches = get_taches_today()
        
        if not taches:
            st.success("âœ¨ Aucune tÃ¢che pour aujourd'hui!")
        else:
            # Tri par heure
            taches_triees = sorted(taches, key=lambda x: x.get("heure", ""))
            
            # Progression
            faites = len([t for t in taches if t["fait"]])
            progression = (faites / len(taches) * 100) if taches else 0
            
            st.progress(progression / 100)
            st.caption(f"âœ… {faites}/{len(taches)} tÃ¢ches faites ({progression:.0f}%)")
            
            st.markdown("---")
            
            # Affichage
            for tache in taches_triees:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    emoji = "âœ…" if tache["fait"] else "â³"
                    st.markdown(f"### {emoji} {tache['nom']}")
                    
                    if tache.get("description"):
                        st.caption(tache["description"])
                    
                    if tache.get("heure"):
                        st.caption(f"🎯 {tache['heure']}")
                
                with col2:
                    if not tache["fait"]:
                        if st.button("âœ“ Fait", key=f"check_{tache['id']}", use_container_width=True):
                            if marquer_tache_faite(tache["id"]):
                                st.success("âœ… TÃ¢che marquée!")
                                st.rerun()
                
                with col3:
                    if tache["fait"]:
                        st.success("âœ…")
                
                st.divider()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: ROUTINES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab2:
        st.subheader("Mes routines")
        
        df_routines = charger_routines()
        
        if df_routines.empty:
            st.info("Aucune routine créée. Créez-en une!")
        else:
            # Filtre par catégorie
            categories = ["Tous"] + sorted(df_routines["categorie"].unique().tolist())
            filtre_cat = st.selectbox("Filtrer par catégorie", categories)
            
            if filtre_cat != "Tous":
                df_routines = df_routines[df_routines["categorie"] == filtre_cat]
            
            for idx, routine in df_routines.iterrows():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {routine['nom']}")
                    
                    # Barre de progression
                    st.progress(routine['completion'] / 100)
                    st.caption(
                        f"[CHART] {routine['completion']:.0f}% â€¢ "
                        f"{routine['tasks_aujourd_hui']}/{routine['tasks_count']} tÃ¢ches â€¢ "
                        f"Fréquence: {routine['frequence']}"
                    )
                    
                    if routine['description']:
                        st.caption(routine['description'])
                
                with col2:
                    if st.button("âš™ï¸", key=f"settings_{routine['id']}", use_container_width=True):
                        if desactiver_routine(routine['id']):
                            st.info("Routine désactivée")
                            st.rerun()
                
                # TÃ¢ches
                with st.expander("Voir tÃ¢ches"):
                    with get_db_context() as session:
                        taches_routine = session.query(RoutineTask).filter_by(
                            routine_id=routine['id']
                        ).all()
                        
                        if not taches_routine:
                            st.caption("Aucune tÃ¢che")
                        else:
                            for t in taches_routine:
                                col_t1, col_t2 = st.columns([4, 1])
                                
                                with col_t1:
                                    emoji = "âœ…" if t.fait_le == date.today() else "â³"
                                    st.caption(f"{emoji} {t.nom}")
                                    if t.heure_prevue:
                                        st.caption(f"🎯 {t.heure_prevue}")
                                
                                with col_t2:
                                    if t.fait_le != date.today():
                                        if st.button("âœ“", key=f"tache_{t.id}", use_container_width=True):
                                            if marquer_tache_faite(t.id):
                                                st.rerun()
                
                st.divider()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: ASSISTANT IA
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab3:
        st.subheader("– Assistant Entretien IA")
        
        # Créer routine avec IA
        st.markdown("#### 📅 Créer une routine avec IA")
        
        col_r1, col_r2 = st.columns(2)
        
        with col_r1:
            routine_nom = st.text_input(
                "Nom de la routine",
                placeholder="Ex: Nettoyage cuisine"
            )
        
        with col_r2:
            routine_freq = st.selectbox(
                "Fréquence",
                ["quotidien", "hebdomadaire", "mensuel", "hebdomadaire 2x"]
            )
        
        if st.button("👶 Générer tÃ¢ches", use_container_width=True):
            if routine_nom:
                with st.spinner("IA crée la routine..."):
                    try:
                        import asyncio
                        taches = asyncio.run(service.creer_routine(routine_nom, f"Fréquence: {routine_freq}"))
                        if taches:
                            st.success(taches)
                            
                            # Proposer de créer
                            if st.button("âœ… Créer cette routine", use_container_width=True):
                                r_id = creer_routine(routine_nom, "Général", routine_freq)
                                if r_id:
                                    st.success("Routine créée!")
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")
        
        st.markdown("---")
        
        # Optimiser semaine
        st.markdown("#### 🧹¸ Optimiser la semaine")
        
        types = st.text_area(
            "Lister les tÃ¢ches (une par ligne)",
            placeholder="Nettoyage salle de bain\nLessive\nVaisselle\n...",
            height=120
        )
        
        if st.button("💡 Proposer répartition", use_container_width=True):
            if types:
                with st.spinner("Optimisation en cours..."):
                    try:
                        import asyncio
                        repartition = asyncio.run(service.optimiser_semaine(types))
                        if repartition:
                            st.info(repartition)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")
        
        st.markdown("---")
        
        # Astuces
        st.markdown("#### 👶 Astuces d'efficacité")
        
        if st.button("💰 Obtenir astuces", use_container_width=True):
            with st.spinner("Recherche astuces..."):
                try:
                    import asyncio
                    astuces = asyncio.run(service.conseil_efficacite())
                    if astuces:
                        st.success(astuces)
                except Exception as e:
                    st.warning(f"âš ï¸ IA indisponible: {e}")
        
        st.markdown("---")
        
        # Estimer temps
        st.markdown("#### â±ï¸ Estimer temps d'une tÃ¢che")
        
        tache_temps = st.text_input(
            "Nom de la tÃ¢che",
            placeholder="Ex: Nettoyer la salle de bain"
        )
        
        if st.button("Estimer", use_container_width=True):
            if tache_temps:
                with st.spinner("Estimation..."):
                    try:
                        import asyncio
                        temps = asyncio.run(service.conseil_temps_estime(tache_temps))
                        if temps:
                            st.info(temps)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA indisponible: {e}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 4: CRÃ‰ER ROUTINE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab4:
        st.subheader("Créer une nouvelle routine")
        
        with st.form("form_routine"):
            nom_r = st.text_input("Nom *", placeholder="Ex: Nettoyage salle de bain")
            
            col_r1, col_r2 = st.columns(2)
            
            with col_r1:
                categorie_r = st.selectbox(
                    "Catégorie",
                    ["Cuisine", "Salle de bain", "Chambres", "Salon", "Extérieur", "Autre"]
                )
            
            with col_r2:
                frequence_r = st.selectbox(
                    "Fréquence",
                    ["quotidien", "hebdomadaire", "bi-hebdomadaire", "mensuel"]
                )
            
            desc_r = st.text_area(
                "Description",
                placeholder="Details de la routine...",
                height=80
            )
            
            nb_taches = st.number_input("Nombre de tÃ¢ches à ajouter", 1, 10, 3)
            
            submitted = st.form_submit_button("âœ… Créer routine", type="primary")
            
            if submitted:
                if not nom_r:
                    st.error("Nom obligatoire")
                else:
                    r_id = creer_routine(nom_r, categorie_r, frequence_r, desc_r)
                    if r_id:
                        st.success(f"âœ… Routine '{nom_r}' créée!")
                        st.rerun()
        
        st.markdown("---")
        
        # Templates
        st.markdown("### 📅 Templates rapides")
        
        templates = [
            {
                "nom": "Nettoyage cuisine",
                "categorie": "Cuisine",
                "freq": "quotidien",
                "taches": ["Laver vaisselle", "Nettoyer plan de travail", "Balayer", "Vider poubelle"]
            },
            {
                "nom": "Salle de bain",
                "categorie": "Salle de bain",
                "freq": "hebdomadaire",
                "taches": ["Toilettes", "Baignoire/douche", "Lavabo", "Miroir", "Sol"]
            },
            {
                "nom": "Lessive",
                "categorie": "Chambres",
                "freq": "hebdomadaire",
                "taches": ["Trier linge", "Laver", "Sécher", "Plier", "Ranger"]
            }
        ]
        
        for templ in templates:
            if st.button(f"📅 {templ['nom']}", use_container_width=True):
                r_id = creer_routine(templ["nom"], templ["categorie"], templ["freq"])
                if r_id:
                    for ordre, tache_nom in enumerate(templ["taches"], 1):
                        ajouter_tache_routine(r_id, tache_nom, ordre=ordre)
                    st.success("âœ… Routine créée!")
                    st.rerun()


if __name__ == "__main__":
    app()

