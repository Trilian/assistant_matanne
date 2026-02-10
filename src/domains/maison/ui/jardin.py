"""
Module Jardin - Gestion du jardin avec IA intégrée
Conseils saisonniers, arrosage intelligent, récoltes planifiées
"""

from datetime import date, timedelta
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.core.database import get_db_context
from src.core.models import GardenItem, GardenLog
from src.core.decorators import with_db_session
from src.services.base_ai_service import BaseAIService
from src.core.ai import ClientIA

# Logique métier pure
from src.domains.maison.logic.jardin_logic import (
    get_saison_actuelle,
    calculer_jours_avant_arrosage,
    calculer_jours_avant_recolte,
    get_plantes_a_arroser as logic_plantes_arroser,
    get_recoltes_proches as logic_recoltes_proches,
    calculer_statistiques_jardin
)

from src.domains.maison.logic.helpers import (
    charger_plantes,
    get_plantes_a_arroser,
    get_recoltes_proches,
    get_stats_jardin,
    get_saison,
    clear_maison_cache
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SERVICE IA JARDIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class JardinService(BaseAIService):
    """Service IA pour les conseils et suggestions de jardin"""
    
    def __init__(self, client: ClientIA = None):
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="jardin",
            default_ttl=3600,
            service_name="jardin"
        )
    
    async def generer_conseils_saison(self, saison: str) -> str:
        """Génère des conseils spécifiques à la saison"""
        prompt = f"""Tu es un expert jardinier. Donne 3-4 conseils pratiques 
pour les travaux de jardinage en {saison} (maintenant). Sois concis et actionnable."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es un expert en jardinage et agriculture biologique",
            max_tokens=500
        )
    
    async def suggerer_plantes_saison(self, saison: str, climat: str = "tempéré") -> str:
        """Suggère des plantes à planter cette saison"""
        prompt = f"""Suggère 5 plantes/légumes parfaits à planter en {saison} 
sous climat {climat}. Format: "- Nom (type) : description courte"."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en jardinage et sélection de plantes",
            max_tokens=600
        )
    
    async def conseil_arrosage(self, nom_plante: str, saison: str) -> str:
        """Conseil d'arrosage pour une plante spécifique"""
        prompt = f"""Donne un conseil d'arrosage pour {nom_plante} en {saison}. 
Inclus: fréquence, quantité, moment de la journée."""
        
        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en arrosage et soins des plantes",
            max_tokens=300
        )


def get_jardin_service() -> JardinService:
    """Factory pour obtenir le service jardin"""
    return JardinService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# HELPERS MÉTIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@with_db_session
def ajouter_plante(
    nom: str,
    type_plante: str,
    emplacement: str,
    date_plantation: date = None,
    date_recolte: date = None,
    notes: str = "",
    db=None
) -> bool:
    """Ajoute une nouvelle plante au jardin"""
    try:
        item = GardenItem(
            nom=nom,
            type=type_plante,
            location=emplacement,
            date_plantation=date_plantation or date.today(),
            date_recolte_prevue=date_recolte,
            notes=notes,
            statut="actif"
        )
        db.add(item)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout plante: {e}")
        return False


@with_db_session
def arroser_plante(item_id: int, notes: str = "", db=None) -> bool:
    """Enregistre un arrosage"""
    try:
        log = GardenLog(
            garden_item_id=item_id,
            date=date.today(),
            action="arrosage",
            notes=notes
        )
        db.add(log)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"❌ Erreur enregistrement: {e}")
        return False


@with_db_session
def ajouter_log(item_id: int, action: str, notes: str = "", db=None) -> bool:
    """Ajoute une entrée au journal du jardin"""
    try:
        log = GardenLog(
            garden_item_id=item_id,
            date=date.today(),
            action=action,
            notes=notes
        )
        db.add(log)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        st.error(f"❌ Erreur ajout log: {e}")
        return False


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MODULE PRINCIPAL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def app():
    """Point d'entrée module Jardin"""
    st.title("💡¿ Mon Jardin")
    st.caption("Gestion intelligente du jardin avec conseils IA et météo")
    
    saison = get_saison()
    st.info(f"💡 Saison actuelle : **{saison}**")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALERTES URGENTES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    plantes_arroser = get_plantes_a_arroser()
    recoltes = get_recoltes_proches()
    
    if plantes_arroser:
        st.warning(f"🔔 **{len(plantes_arroser)} plante(s) à arroser aujourd'hui!**")
        for plante in plantes_arroser[:3]:
            st.caption(f"• {plante['nom']} ({plante['type']})")
    
    if recoltes:
        st.success(f"💡½ **{len(recoltes)} récolte(s) prévue(s) cette semaine!**")
        for r in recoltes[:3]:
            jours = (r["recolte"] - date.today()).days
            st.caption(f"• {r['nom']} dans {jours} jour(s)")
    
    st.markdown("---")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TABS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🪴 Mes Plantes", "– Conseils IA", "➕ Ajouter", "📊 Stats", "🍽️ Journal"]
    )
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 1: MES PLANTES
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab1:
        st.subheader("Inventaire du jardin")
        
        df = charger_plantes()
        
        if df.empty:
            st.info("🪴 Aucune plante pour le moment. Ajoutes-en une!")
        else:
            # Filtre par type
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                types = ["Tous"] + sorted(df["type"].unique().tolist())
                filtre_type = st.selectbox("Type", types)
                if filtre_type != "Tous":
                    df = df[df["type"] == filtre_type]
            
            with col_f2:
                filtre_arrosage = st.checkbox("Montrer seulement à arroser")
                if filtre_arrosage:
                    df = df[df["a_arroser"]]
            
            # Affichage en grille
            for idx, row in df.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    emoji = "�" if row["a_arroser"] else "✅"
                    st.markdown(f"### {emoji} {row['nom']}")
                    st.caption(f"📍 {row['location']} • {row['type']}")
                    if row["notes"]:
                        st.caption(f"📝 {row['notes']}")
                
                with col2:
                    if row["jours_depuis_arrosage"] is not None:
                        st.metric(
                            "Arrosé il y a",
                            f"{row['jours_depuis_arrosage']} j",
                            delta=None
                        )
                    
                    if row["recolte"]:
                        jours = (row["recolte"] - date.today()).days
                        if jours > 0:
                            st.metric("Récolte dans", f"{jours} j")
                
                with col3:
                    if st.button("🔔 Arroser", key=f"arroser_{row['id']}"):
                        if arroser_plante(row["id"]):
                            st.rerun()
                
                st.divider()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 2: CONSEILS IA
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab2:
        st.subheader("– Conseils Jardin avec IA")
        
        service = get_jardin_service()
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if st.button("🧹 Conseils pour cette saison", use_container_width=True):
                with st.spinner("Génération des conseils IA..."):
                    try:
                        import asyncio
                        conseils = asyncio.run(service.generer_conseils_saison(saison))
                        if conseils:
                            st.success(conseils)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA temporairement indisponible: {e}")
        
        with col_c2:
            if st.button("💡¿ Plantes à planter maintenant", use_container_width=True):
                with st.spinner("Recherche des meilleures plantes..."):
                    try:
                        import asyncio
                        suggestions = asyncio.run(service.suggerer_plantes_saison(saison))
                        if suggestions:
                            st.success(suggestions)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA temporairement indisponible: {e}")
        
        st.markdown("---")
        
        # Conseil personnalisé pour une plante
        st.subheader("Conseil spécifique")
        plante_conseil = st.text_input("Nom de la plante (ex: Tomate)")
        
        if st.button("Obtenir conseil d'arrosage", use_container_width=True):
            if plante_conseil:
                with st.spinner("Analyse IA en cours..."):
                    try:
                        import asyncio
                        conseil = asyncio.run(service.conseil_arrosage(plante_conseil, saison))
                        if conseil:
                            st.info(conseil)
                    except Exception as e:
                        st.warning(f"âš ï¸ IA temporairement indisponible: {e}")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 3: AJOUTER PLANTE
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab3:
        st.subheader("Ajouter une plante")
        
        with st.form("form_plante"):
            nom = st.text_input("Nom *", placeholder="Ex: Tomate cerise")
            
            col_1, col_2 = st.columns(2)
            
            with col_1:
                type_plante = st.selectbox(
                    "Type *",
                    ["Légume", "Fruit", "Herbe aromatique", "Fleur", "Arbre", "Autre"]
                )
                emplacement = st.text_input(
                    "Emplacement",
                    placeholder="Ex: Potager nord"
                )
            
            with col_2:
                date_plantation = st.date_input("Date de plantation", value=date.today())
                date_recolte = st.date_input("Date récolte (optionnel)", value=None)
            
            notes = st.text_area(
                "Notes",
                placeholder="Variété, exposition, particularités...",
                height=80
            )
            
            submitted = st.form_submit_button("🪴 Ajouter au jardin", type="primary")
            
            if submitted:
                if not nom or not type_plante:
                    st.error("Nom et type obligatoires")
                else:
                    if ajouter_plante(nom, type_plante, emplacement, date_plantation, date_recolte, notes):
                        st.balloons()
                        st.rerun()
        
        st.markdown("---")
        
        # Suggestions rapides
        st.markdown("### ⚡ Ajouts rapides")
        
        suggestions = [
            {"nom": "Tomates cerises", "type": "Fruit", "emoji": "🍅"},
            {"nom": "Basilic", "type": "Herbe aromatique", "emoji": "🌿"},
            {"nom": "Fraises", "type": "Fruit", "emoji": "🍓"},
            {"nom": "Courgettes", "type": "Légume", "emoji": "🥒"},
        ]
        
        cols = st.columns(2)
        for i, sugg in enumerate(suggestions):
            col = cols[i % 2]
            with col:
                if st.button(f"{sugg['emoji']} {sugg['nom']}", use_container_width=True):
                    if ajouter_plante(sugg["nom"], sugg["type"], "Potager"):
                        st.success(f"✅ {sugg['nom']} ajouté!")
                        st.rerun()
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 4: STATS
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab4:
        st.subheader("📊 Statistiques")
        
        stats = get_stats_jardin()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Plantes totales", stats["total_plantes"])
        
        with col2:
            st.metric("À arroser", stats["a_arroser"])
        
        with col3:
            st.metric("Récoltes proches", stats["recoltes_proches"])
        
        with col4:
            st.metric("Catégories", stats["categories"])
        
        st.markdown("---")
        
        # Graphique d'arrosage
        if not charger_plantes().empty:
            df_stats = charger_plantes()
            type_counts = df_stats["type"].value_counts()
            
            fig = go.Figure(
                data=[go.Bar(x=type_counts.index, y=type_counts.values, marker_color="green")]
            )
            fig.update_layout(
                title="Plantes par catégorie",
                xaxis_title="Type",
                yaxis_title="Nombre",
                height=400
            )
            st.plotly_chart(fig, width="stretch", key="garden_plants_by_category")
    
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TAB 5: JOURNAL
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    with tab5:
        st.subheader("🍽️… Journal d'entretien")
        
        df_plantes = charger_plantes()
        
        if df_plantes.empty:
            st.info("Aucune plante pour le moment")
        else:
            plante_selected = st.selectbox(
                "Sélectionner une plante",
                df_plantes["nom"].tolist(),
                key="journal_plante"
            )
            
            selected_id = df_plantes[df_plantes["nom"] == plante_selected].iloc[0]["id"]
            
            col_a1, col_a2 = st.columns(2)
            
            with col_a1:
                action = st.selectbox(
                    "Action",
                    ["arrosage", "désherbage", "taille", "traitement", "fertilisation", "récolte"]
                )
            
            with col_a2:
                notes_log = st.text_input("Notes", placeholder="Observations...")
            
            if st.button("🍽️ Enregistrer", use_container_width=True):
                if ajouter_log(selected_id, action, notes_log):
                    st.success("✅ Enregistré!")
                    st.rerun()
            
            st.markdown("---")
            st.caption(f"🍽️ Dernier enregistrement pour {plante_selected}")


if __name__ == "__main__":
    app()

