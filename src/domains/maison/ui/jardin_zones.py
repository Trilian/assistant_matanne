"""
Module Dashboard Zones Jardin - Vue 2600m² avec photos avant/après

Affiche l'état des zones du jardin avec:
- Vue d'ensemble des 8 zones
- Photos avant/après par zone
- Progression des objectifs
- Alertes par état
"""

from datetime import date
from typing import Any, Optional

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db
from src.core.models import GardenZone
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

EMOJI_ZONE = {
    "pelouse": "🌱",
    "potager": "🥕",
    "arbres": "🌳",
    "arbres_deco": "🎄",
    "arbres_fruitiers": "🍎",
    "piscine": "🏊",
    "terrain_boules": "🎱",
    "terrasse": "☕",
    "allee": "🚶",
    "compost": "♻️",
    "autre": "📍",
}

COULEUR_ETAT = {
    1: "#f44336",  # Critique - rouge
    2: "#ff9800",  # Mauvais - orange
    3: "#ffeb3b",  # Moyen - jaune
    4: "#8bc34a",  # Bon - vert clair
    5: "#4caf50",  # Parfait - vert
}

LABEL_ETAT = {
    1: "❌ Critique",
    2: "⚠️ Mauvais",
    3: "😐 Moyen",
    4: "👍 Bon",
    5: "✅ Parfait",
}


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DONNÉES
# ═══════════════════════════════════════════════════════════


@st.cache_data(ttl=300)
def charger_zones() -> list[dict[str, Any]]:
    """Charge toutes les zones du jardin."""
    try:
        with obtenir_contexte_db() as db:
            zones = db.query(GardenZone).all()
            return [
                {
                    "id": z.id,
                    "nom": z.nom,
                    "type_zone": z.type_zone,
                    "surface_m2": z.surface_m2 or 0,
                    "etat_note": z.etat_note or 3,
                    "etat_description": z.etat_description or "",
                    "objectif": z.objectif or "",
                    "prochaine_action": z.prochaine_action or "",
                    "date_prochaine_action": z.date_prochaine_action,
                    "photos_url": z.photos_url or [],
                    "budget_estime": float(z.budget_estime) if z.budget_estime else 0,
                }
                for z in zones
            ]
    except Exception as e:
        logger.error(f"Erreur chargement zones: {e}")
        return []


@avec_session_db
def mettre_a_jour_zone(zone_id: int, champs: dict[str, Any], db: Optional[Session] = None) -> bool:
    """Met à jour une zone du jardin."""
    try:
        zone = db.query(GardenZone).filter_by(id=zone_id).first()
        if not zone:
            return False
        
        for k, v in champs.items():
            if hasattr(zone, k):
                setattr(zone, k, v)
        
        db.commit()
        charger_zones.clear()  # Invalider cache
        return True
    except Exception as e:
        logger.error(f"Erreur MAJ zone: {e}")
        return False


@avec_session_db
def ajouter_photo_zone(zone_id: int, photo_url: str, est_avant: bool = True, db: Optional[Session] = None) -> bool:
    """Ajoute une photo à une zone."""
    try:
        zone = db.query(GardenZone).filter_by(id=zone_id).first()
        if not zone:
            return False
        
        photos = zone.photos_url or []
        # Format: ["avant:url1", "apres:url2", ...]
        prefix = "avant" if est_avant else "apres"
        photos.append(f"{prefix}:{photo_url}")
        zone.photos_url = photos
        
        db.commit()
        charger_zones.clear()
        return True
    except Exception as e:
        logger.error(f"Erreur ajout photo: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_carte_zone(zone: dict[str, Any]):
    """Affiche une carte pour une zone du jardin."""
    emoji = EMOJI_ZONE.get(zone["type_zone"], "📍")
    etat = zone["etat_note"]
    couleur = COULEUR_ETAT.get(etat, "#9e9e9e")
    label_etat = LABEL_ETAT.get(etat, "?")
    
    with st.container(border=True):
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {emoji} {zone['nom']}")
        with col2:
            st.markdown(f"**{label_etat}**")
        
        # Surface
        st.caption(f"📐 {zone['surface_m2']}m²")
        
        # Description de l'état
        if zone["etat_description"]:
            st.markdown(zone["etat_description"][:100])
        
        # Barre de progression état
        st.progress(etat / 5, text=f"État: {etat}/5")
        
        # Actions
        if zone["prochaine_action"]:
            st.info(f"🎯 {zone['prochaine_action']}")
        
        # Photos miniatures
        photos = zone.get("photos_url", [])
        if photos:
            col_p1, col_p2 = st.columns(2)
            avant = [p.replace("avant:", "") for p in photos if p.startswith("avant:")]
            apres = [p.replace("apres:", "") for p in photos if p.startswith("apres:")]
            
            with col_p1:
                if avant:
                    st.image(avant[-1], caption="Avant", width=100)
            with col_p2:
                if apres:
                    st.image(apres[-1], caption="Après", width=100)


def render_vue_ensemble():
    """Affiche la vue d'ensemble de toutes les zones."""
    zones = charger_zones()
    
    if not zones:
        st.warning("🌱 Aucune zone configurée. Exécutez la migration SQL 016.")
        return
    
    # Métriques globales
    total_surface = sum(z["surface_m2"] for z in zones)
    etat_moyen = sum(z["etat_note"] for z in zones) / len(zones)
    zones_critiques = len([z for z in zones if z["etat_note"] <= 2])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏡 Surface totale", f"{total_surface}m²")
    with col2:
        st.metric("📊 État moyen", f"{etat_moyen:.1f}/5")
    with col3:
        st.metric("⚠️ Zones critiques", zones_critiques)
    with col4:
        st.metric("🌳 Nb zones", len(zones))
    
    st.divider()
    
    # Graphique état par zone
    fig = go.Figure()
    
    noms = [z["nom"] for z in zones]
    etats = [z["etat_note"] for z in zones]
    couleurs = [COULEUR_ETAT.get(e, "#9e9e9e") for e in etats]
    
    fig.add_trace(go.Bar(
        x=noms,
        y=etats,
        marker_color=couleurs,
        text=[LABEL_ETAT.get(e, "?") for e in etats],
        textposition="outside",
    ))
    
    fig.update_layout(
        title="État des zones du jardin",
        yaxis_title="Note",
        yaxis=dict(range=[0, 6]),
        height=350,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Alertes
    alertes = [z for z in zones if z["etat_note"] <= 2]
    if alertes:
        st.error(f"⚠️ **{len(alertes)} zone(s) nécessitent une attention urgente:**")
        for z in alertes:
            emoji = EMOJI_ZONE.get(z["type_zone"], "📍")
            action = z["prochaine_action"] or "Évaluer l'état"
            st.markdown(f"- {emoji} **{z['nom']}**: {action}")


def render_detail_zone(zone: dict[str, Any]):
    """Affiche le détail d'une zone avec formulaire d'édition."""
    emoji = EMOJI_ZONE.get(zone["type_zone"], "📍")
    
    st.markdown(f"## {emoji} {zone['nom']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Infos
        st.markdown(f"**Type:** {zone['type_zone']}")
        st.markdown(f"**Surface:** {zone['surface_m2']}m²")
        st.markdown(f"**État:** {LABEL_ETAT.get(zone['etat_note'], '?')}")
        st.progress(zone["etat_note"] / 5)
        
        if zone["etat_description"]:
            st.markdown("**Description de l'état:**")
            st.info(zone["etat_description"])
        
        if zone["objectif"]:
            st.markdown("**Objectif:**")
            st.success(zone["objectif"])
    
    with col2:
        # Photos avant/après
        st.markdown("### 📸 Photos")
        
        photos = zone.get("photos_url", [])
        avant = [p.replace("avant:", "") for p in photos if p.startswith("avant:")]
        apres = [p.replace("apres:", "") for p in photos if p.startswith("apres:")]
        
        tab_avant, tab_apres = st.tabs(["Avant", "Après"])
        
        with tab_avant:
            if avant:
                for url in avant[-3:]:  # Max 3 photos
                    st.image(url, use_container_width=True)
            else:
                st.caption("Pas de photo 'avant'")
            
            photo_avant = st.text_input("URL photo avant", key=f"photo_avant_{zone['id']}")
            if st.button("➕ Ajouter", key=f"add_avant_{zone['id']}"):
                if photo_avant and ajouter_photo_zone(zone["id"], photo_avant, est_avant=True):
                    st.success("✅ Photo ajoutée!")
                    st.rerun()
        
        with tab_apres:
            if apres:
                for url in apres[-3:]:
                    st.image(url, use_container_width=True)
            else:
                st.caption("Pas de photo 'après'")
            
            photo_apres = st.text_input("URL photo après", key=f"photo_apres_{zone['id']}")
            if st.button("➕ Ajouter", key=f"add_apres_{zone['id']}"):
                if photo_apres and ajouter_photo_zone(zone["id"], photo_apres, est_avant=False):
                    st.success("✅ Photo ajoutée!")
                    st.rerun()
    
    st.divider()
    
    # Formulaire de mise à jour
    st.markdown("### ✏️ Mettre à jour")
    
    with st.form(f"form_zone_{zone['id']}"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            nouvel_etat = st.slider(
                "Nouvel état",
                min_value=1,
                max_value=5,
                value=zone["etat_note"],
                help="1=Critique, 5=Parfait"
            )
            
            nouvelle_action = st.text_area(
                "Prochaine action",
                value=zone["prochaine_action"],
                height=100
            )
        
        with col_f2:
            nouvelle_description = st.text_area(
                "Description de l'état",
                value=zone["etat_description"],
                height=100
            )
            
            nouvel_objectif = st.text_area(
                "Objectif",
                value=zone["objectif"],
                height=100
            )
        
        if st.form_submit_button("💾 Enregistrer", type="primary"):
            if mettre_a_jour_zone(zone["id"], {
                "etat_note": nouvel_etat,
                "prochaine_action": nouvelle_action,
                "etat_description": nouvelle_description,
                "objectif": nouvel_objectif,
            }):
                st.success("✅ Zone mise à jour!")
                st.rerun()
            else:
                st.error("❌ Erreur lors de la mise à jour")


def render_conseils_amelioration():
    """Affiche les conseils pour améliorer la terre."""
    st.markdown("## 🌱 Conseils amélioration terre")
    
    st.info("""
    **Votre jardin de 2600m² a besoin d'amour!** Voici le plan d'action:
    """)
    
    with st.expander("🔬 ÉTAPE 1: Diagnostic", expanded=True):
        st.markdown("""
        - **Sol argileux**: Compact, mal drainé → Ajouter sable + compost
        - **Sol sableux**: Ne retient pas l'eau → Ajouter matière organique
        - **Sol calcaire**: Bloque nutriments → Acidifier avec soufre
        
        💡 **Test maison**: Prendre une poignée de terre humide, si elle forme une boule compacte = argileux
        """)
    
    with st.expander("♻️ ÉTAPE 2: Compost (ESSENTIEL)", expanded=True):
        st.markdown("""
        **Créez votre "or noir" en 6-12 mois:**
        
        | Déchets VERTS (1/3) | Déchets BRUNS (2/3) |
        |---------------------|---------------------|
        | Tontes de gazon | Carton non imprimé |
        | Épluchures | Branches broyées |
        | Feuilles vertes | Paille, foin |
        | Marc de café | Feuilles mortes |
        
        ⚠️ **JAMAIS**: viande, poisson, produits laitiers, agrumes en excès
        """)
    
    with st.expander("🍂 ÉTAPE 3: Paillage permanent"):
        st.markdown("""
        Le paillage protège le sol et le nourrit:
        
        - **BRF** (Bois Raméal Fragmenté): Branches < 7cm broyées
        - **Paille**: 10-15cm d'épaisseur
        - **Feuilles mortes**: Gratuit et efficace!
        - **Tontes séchées**: Ne pas mettre en couche épaisse humide
        
        ✅ **Avantages**: Limite évaporation, nourrit le sol, réduit désherbage
        """)
    
    with st.expander("🌾 ÉTAPE 4: Engrais verts (hiver)"):
        st.markdown("""
        **Semer en automne, faucher au printemps:**
        
        - **Moutarde**: Rapide, décompacte le sol
        - **Phacélie**: Fleurs pour les abeilles
        - **Trèfle**: Fixe l'azote (légumineuse)
        - **Seigle**: Structurant, racines profondes
        """)
    
    with st.expander("📅 PLANNING PELOUSE 2600m²"):
        st.markdown("""
        | Mois | Action |
        |------|--------|
        | **Mars** | Scarifier (arracher mousse) |
        | **Avril** | Aérer + ressemer zones nues |
        | **Mai-Sept** | Tonte mulching (laisser l'herbe au sol) |
        | **Automne** | Épandre compost fin (1-2cm) |
        | **Hiver** | Laisser reposer |
        
        🎯 **Tonte mulching**: Tondre sans ramasser = +30% nutriments gratuits!
        """)


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


def app():
    """Point d'entrée du module Dashboard Zones Jardin."""
    
    st.title("🌳 Jardin - Dashboard Zones")
    st.caption("Votre terrain de 2600m² en un coup d'œil")
    
    zones = charger_zones()
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Vue d'ensemble",
        "🔍 Détail par zone",
        "🌱 Conseils amélioration",
    ])
    
    with tab1:
        render_vue_ensemble()
        
        st.divider()
        st.markdown("### 🗺️ Toutes les zones")
        
        # Affichage en grille
        cols = st.columns(2)
        for i, zone in enumerate(zones):
            with cols[i % 2]:
                render_carte_zone(zone)
    
    with tab2:
        if not zones:
            st.warning("Aucune zone configurée")
        else:
            zone_selectionnee = st.selectbox(
                "Sélectionner une zone",
                options=[z["nom"] for z in zones],
                format_func=lambda x: f"{EMOJI_ZONE.get(next((z['type_zone'] for z in zones if z['nom']==x), 'autre'), '📍')} {x}"
            )
            
            zone = next((z for z in zones if z["nom"] == zone_selectionnee), None)
            if zone:
                render_detail_zone(zone)
    
    with tab3:
        render_conseils_amelioration()


if __name__ == "__main__":
    app()

