"""
Hub Maison - Dashboard central avec cards cliquables.

Structure:
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 📋 Projets  │ │ 🌱 Jardin   │ │ 🧹 Ménage   │
│ Garage,SdB  │ │ 2600m² 😰  │ │ Vitres, Tri │
└─────────────┘ └─────────────┘ └─────────────┘
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ 🛋️ Meubles  │ │ 💡 Éco-Tips │ │ 💰 Dépenses │
│ Wishlist    │ │ Lavable,Gaz │ │ Gaz,Eau,Elec│
└─────────────┘ └─────────────┘ └─────────────┘
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from src.core.database import get_db_context


# ═══════════════════════════════════════════════════════════
# STYLES CSS
# ═══════════════════════════════════════════════════════════

CARD_STYLES = """
<style>
.maison-card {
    background: linear-gradient(135deg, #4a90a4 0%, #2d5a6b 100%);
    border-radius: 16px;
    padding: 1.2rem;
    color: white;
    margin-bottom: 1rem;
    transition: transform 0.2s;
}
.maison-card:hover {
    transform: translateY(-2px);
}
.maison-card.projets {
    background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
}
.maison-card.jardin {
    background: linear-gradient(135deg, #27ae60 0%, #1e8449 100%);
}
.maison-card.menage {
    background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
}
.maison-card.meubles {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
}
.maison-card.eco {
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
}
.maison-card.depenses {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
}
.card-title {
    font-size: 1.3rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.card-stat {
    font-size: 0.9rem;
    opacity: 0.9;
}
.etat-note {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    background: rgba(255,255,255,0.2);
}
.etat-1 { background: #e74c3c; }
.etat-2 { background: #e67e22; }
.etat-3 { background: #f1c40f; color: #333; }
.etat-4 { background: #27ae60; }
.etat-5 { background: #2ecc71; }
</style>
"""


# ═══════════════════════════════════════════════════════════
# HELPERS - STATS
# ═══════════════════════════════════════════════════════════

def get_stats_projets() -> dict:
    """Récupère stats projets"""
    try:
        from src.core.models import Project
        with get_db_context() as db:
            total = db.query(Project).count()
            en_cours = db.query(Project).filter(Project.statut == "en_cours").count()
            return {"total": total, "en_cours": en_cours}
    except:
        return {"total": 0, "en_cours": 0}


def get_stats_jardin() -> dict:
    """Récupère stats zones jardin"""
    try:
        from src.core.models import GardenZone
        with get_db_context() as db:
            zones = db.query(GardenZone).all()
            if not zones:
                return {"zones": 0, "etat_moyen": 0, "surface": 2600}
            etat_moyen = sum(z.etat_note for z in zones) / len(zones)
            surface = sum(z.surface_m2 or 0 for z in zones)
            return {"zones": len(zones), "etat_moyen": round(etat_moyen, 1), "surface": surface or 2600}
    except:
        return {"zones": 0, "etat_moyen": 0, "surface": 2600}


def get_stats_menage() -> dict:
    """Récupère stats tâches ménage"""
    try:
        from src.core.models import MaintenanceTask
        today = date.today()
        with get_db_context() as db:
            total = db.query(MaintenanceTask).filter(MaintenanceTask.fait == False).count()
            urgentes = db.query(MaintenanceTask).filter(
                MaintenanceTask.fait == False,
                MaintenanceTask.prochaine_fois <= today
            ).count()
            return {"a_faire": total, "urgentes": urgentes}
    except:
        return {"a_faire": 0, "urgentes": 0}


def get_stats_meubles() -> dict:
    """Récupère stats wishlist meubles"""
    try:
        from src.core.models import Furniture
        with get_db_context() as db:
            total = db.query(Furniture).filter(Furniture.statut != "achete").count()
            budget = db.query(Furniture).filter(
                Furniture.statut != "achete",
                Furniture.prix_estime != None
            ).all()
            budget_total = sum(float(m.prix_estime or 0) for m in budget)
            return {"en_attente": total, "budget_estime": budget_total}
    except:
        return {"en_attente": 0, "budget_estime": 0}


def get_stats_eco() -> dict:
    """Récupère stats actions éco"""
    try:
        from src.core.models import EcoAction
        with get_db_context() as db:
            actions = db.query(EcoAction).filter(EcoAction.actif == True).all()
            economie_mensuelle = sum(float(a.economie_mensuelle or 0) for a in actions)
            return {"actions": len(actions), "economie_mensuelle": economie_mensuelle}
    except:
        return {"actions": 0, "economie_mensuelle": 0}


def get_stats_depenses() -> dict:
    """Récupère stats dépenses du mois"""
    try:
        from src.core.models import HouseExpense
        today = date.today()
        with get_db_context() as db:
            depenses = db.query(HouseExpense).filter(
                HouseExpense.mois == today.month,
                HouseExpense.annee == today.year
            ).all()
            total = sum(float(d.montant) for d in depenses)
            return {"total_mois": total, "nb_categories": len(set(d.categorie for d in depenses))}
    except:
        return {"total_mois": 0, "nb_categories": 0}


# ═══════════════════════════════════════════════════════════
# CARDS
# ═══════════════════════════════════════════════════════════

def render_card_projets():
    """Card Projets travaux"""
    stats = get_stats_projets()
    
    if st.button("📋 **Projets**", key="card_projets", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "projets"
        st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("En cours", stats["en_cours"])
    with col2:
        st.metric("Total", stats["total"])


def render_card_jardin():
    """Card Jardin 2600m²"""
    stats = get_stats_jardin()
    
    if st.button("🌱 **Jardin**", key="card_jardin", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "jardin"
        st.rerun()
    
    # Afficher état moyen avec emoji
    etat = stats["etat_moyen"]
    if etat <= 1:
        emoji = "😰"
    elif etat <= 2:
        emoji = "😟"
    elif etat <= 3:
        emoji = "😐"
    elif etat <= 4:
        emoji = "🙂"
    else:
        emoji = "😊"
    
    st.caption(f"📏 {stats['surface']}m² | État: {etat}/5 {emoji}")


def render_card_menage():
    """Card Ménage/Entretien"""
    stats = get_stats_menage()
    
    if st.button("🧹 **Ménage**", key="card_menage", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "menage"
        st.rerun()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("À faire", stats["a_faire"])
    with col2:
        if stats["urgentes"] > 0:
            st.metric("🔴 Urgentes", stats["urgentes"])
        else:
            st.metric("Urgentes", 0)


def render_card_meubles():
    """Card Wishlist meubles"""
    stats = get_stats_meubles()
    
    if st.button("🛋️ **Meubles**", key="card_meubles", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "meubles"
        st.rerun()
    
    st.caption(f"📋 {stats['en_attente']} en wishlist")
    if stats["budget_estime"] > 0:
        st.caption(f"💰 Budget: ~{stats['budget_estime']:.0f}€")


def render_card_eco():
    """Card Éco-Tips"""
    stats = get_stats_eco()
    
    if st.button("💡 **Éco-Tips**", key="card_eco", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "eco"
        st.rerun()
    
    st.caption(f"🌿 {stats['actions']} actions actives")
    if stats["economie_mensuelle"] > 0:
        st.caption(f"💰 -{stats['economie_mensuelle']:.0f}€/mois")


def render_card_depenses():
    """Card Dépenses maison"""
    stats = get_stats_depenses()
    
    if st.button("💰 **Dépenses**", key="card_depenses", use_container_width=True, type="primary"):
        st.session_state["maison_page"] = "depenses"
        st.rerun()
    
    st.caption(f"📊 Ce mois: {stats['total_mois']:.0f}€")


# ═══════════════════════════════════════════════════════════
# ROUTEUR INTERNE
# ═══════════════════════════════════════════════════════════

def render_page_content():
    """Route vers la bonne page selon session_state"""
    page = st.session_state.get("maison_page", "hub")
    
    # Bouton retour si pas sur hub
    if page != "hub":
        if st.button("← Retour au Hub", key="btn_retour_hub"):
            st.session_state["maison_page"] = "hub"
            st.rerun()
        st.divider()
    
    if page == "projets":
        from src.domains.maison.ui.projets import app as projets_app
        projets_app()
    
    elif page == "jardin":
        from src.domains.maison.ui.jardin import app as jardin_app
        jardin_app()
    
    elif page == "menage":
        from src.domains.maison.ui.entretien import app as entretien_app
        entretien_app()
    
    elif page == "meubles":
        from src.domains.maison.ui.meubles import app as meubles_app
        meubles_app()
    
    elif page == "eco":
        from src.domains.maison.ui.eco_tips import app as eco_app
        eco_app()
    
    elif page == "depenses":
        from src.domains.maison.ui.depenses import app as depenses_app
        depenses_app()
    
    else:
        # Hub principal
        render_hub()


def render_hub():
    """Affiche le hub avec les cards"""
    st.markdown(CARD_STYLES, unsafe_allow_html=True)
    
    # Titre
    st.title("🏠 Hub Maison")
    st.caption("Gestion travaux, jardin, ménage et budget")
    
    st.divider()
    
    # Ligne 1: Projets, Jardin, Ménage
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            render_card_projets()
    
    with col2:
        with st.container(border=True):
            render_card_jardin()
    
    with col3:
        with st.container(border=True):
            render_card_menage()
    
    # Ligne 2: Meubles, Éco, Dépenses
    col4, col5, col6 = st.columns(3)
    
    with col4:
        with st.container(border=True):
            render_card_meubles()
    
    with col5:
        with st.container(border=True):
            render_card_eco()
    
    with col6:
        with st.container(border=True):
            render_card_depenses()
    
    st.divider()
    
    # Alertes / Actions urgentes
    render_alertes()


def render_alertes():
    """Affiche les alertes et actions urgentes"""
    st.subheader("⚠️ Actions prioritaires")
    
    alertes = []
    
    # Vérifier tâches en retard
    stats_menage = get_stats_menage()
    if stats_menage["urgentes"] > 0:
        alertes.append(f"🧹 {stats_menage['urgentes']} tâche(s) ménage en retard")
    
    # Vérifier état jardin
    stats_jardin = get_stats_jardin()
    if stats_jardin["etat_moyen"] < 2:
        alertes.append(f"🌱 Jardin en mauvais état ({stats_jardin['etat_moyen']}/5)")
    
    if alertes:
        for alerte in alertes:
            st.warning(alerte)
    else:
        st.success("✅ Rien d'urgent pour le moment!")


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module Hub Maison"""
    render_page_content()
