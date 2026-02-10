"""
Module Éco-Tips - Suivi des actions écologiques et économies.

Gestion du passage aux produits réutilisables, suivi des économies mensuelles,
et conseils éco-responsables.
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List

from src.core.database import obtenir_contexte_db
from src.core.models import EcoAction
from src.core.models.maison_extended import EcoActionType


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TYPE_LABELS = {
    "lavable": "🧺 Réutilisable",
    "energie": "⚡ Énergie",
    "eau": "💧 Eau",
    "dechets": "♻️ Déchets",
    "alimentation": "🥗 Alimentation"
}

# Idées d'actions éco avec économies estimées
IDEES_ACTIONS = [
    {
        "nom": "Essuie-tout lavables",
        "type": "lavable",
        "economie_estimee": 8,  # €/mois
        "cout_initial": 25,
        "description": "Remplacer les rouleaux jetables par des essuie-tout lavables en tissu"
    },
    {
        "nom": "Serviettes de table lavables",
        "type": "lavable",
        "economie_estimee": 5,
        "cout_initial": 20,
        "description": "Serviettes en tissu réutilisables"
    },
    {
        "nom": "Lingettes bébé lavables",
        "type": "lavable",
        "economie_estimee": 15,
        "cout_initial": 40,
        "description": "Lingettes en coton pour Jules"
    },
    {
        "nom": "Disques démaquillants lavables",
        "type": "lavable",
        "economie_estimee": 5,
        "cout_initial": 15,
        "description": "Cotons réutilisables"
    },
    {
        "nom": "Chauffage intelligent",
        "type": "energie",
        "economie_estimee": 30,
        "cout_initial": 0,
        "description": "Baisser de 1°C = -7% sur facture gaz"
    },
    {
        "nom": "Multiprise à interrupteur",
        "type": "energie",
        "economie_estimee": 8,
        "cout_initial": 20,
        "description": "Couper les veilles des appareils"
    },
    {
        "nom": "LED partout",
        "type": "energie",
        "economie_estimee": 10,
        "cout_initial": 50,
        "description": "Remplacer toutes les ampoules par des LED"
    },
    {
        "nom": "Réducteur de débit douche",
        "type": "eau",
        "economie_estimee": 12,
        "cout_initial": 15,
        "description": "Économiser 50% d'eau à la douche"
    },
    {
        "nom": "Composteur",
        "type": "dechets",
        "economie_estimee": 5,
        "cout_initial": 30,
        "description": "Réduire les déchets ménagers de 30%"
    },
    {
        "nom": "Batch cooking",
        "type": "alimentation",
        "economie_estimee": 40,
        "cout_initial": 0,
        "description": "Préparer les repas de la semaine = moins de gaspillage"
    }
]


# ═══════════════════════════════════════════════════════════
# CRUD FUNCTIONS
# ═══════════════════════════════════════════════════════════

def get_all_actions(actif_only: bool = False) -> List[EcoAction]:
    """Récupère toutes les actions éco"""
    with obtenir_contexte_db() as db:
        query = db.query(EcoAction)
        if actif_only:
            query = query.filter(EcoAction.actif == True)
        return query.order_by(EcoAction.date_debut.desc()).all()


def get_action_by_id(action_id: int) -> Optional[EcoAction]:
    """Récupère une action par son ID"""
    with obtenir_contexte_db() as db:
        return db.query(EcoAction).filter(EcoAction.id == action_id).first()


def create_action(data: dict) -> EcoAction:
    """Crée une nouvelle action éco"""
    with obtenir_contexte_db() as db:
        action = EcoAction(**data)
        db.add(action)
        db.commit()
        db.refresh(action)
        return action


def update_action(action_id: int, data: dict) -> Optional[EcoAction]:
    """Met à jour une action éco"""
    with obtenir_contexte_db() as db:
        action = db.query(EcoAction).filter(EcoAction.id == action_id).first()
        if action:
            for key, value in data.items():
                setattr(action, key, value)
            db.commit()
            db.refresh(action)
        return action


def delete_action(action_id: int) -> bool:
    """Supprime une action éco"""
    with obtenir_contexte_db() as db:
        action = db.query(EcoAction).filter(EcoAction.id == action_id).first()
        if action:
            db.delete(action)
            db.commit()
            return True
        return False


def calculate_stats() -> dict:
    """Calcule les statistiques globales"""
    actions = get_all_actions(actif_only=True)
    
    economie_mensuelle = sum(float(a.economie_mensuelle or 0) for a in actions)
    economie_annuelle = economie_mensuelle * 12
    
    cout_initial_total = sum(float(a.cout_initial or 0) for a in actions)
    
    # ROI en mois
    roi_mois = cout_initial_total / economie_mensuelle if economie_mensuelle > 0 else 0
    
    # Économies totales depuis début (estimation)
    economies_totales = 0
    for action in actions:
        if action.date_debut:
            mois_actifs = (date.today() - action.date_debut).days / 30
            economies_totales += float(action.economie_mensuelle or 0) * mois_actifs
    
    return {
        "nb_actions": len(actions),
        "economie_mensuelle": economie_mensuelle,
        "economie_annuelle": economie_annuelle,
        "cout_initial": cout_initial_total,
        "roi_mois": roi_mois,
        "economies_totales": economies_totales
    }


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════

def render_stats_dashboard():
    """Affiche le dashboard de stats"""
    stats = calculate_stats()
    
    st.subheader("📊 Bilan Économies")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Actions actives", stats["nb_actions"])
    
    with col2:
        st.metric("Économie/mois", f"{stats['economie_mensuelle']:.0f}€", delta="récurrent")
    
    with col3:
        st.metric("Économie/an", f"{stats['economie_annuelle']:.0f}€")
    
    with col4:
        st.metric("Économisé total", f"{stats['economies_totales']:.0f}€", delta="depuis début")
    
    if stats["cout_initial"] > 0:
        st.info(f"💡 Investissement initial: {stats['cout_initial']:.0f}€ | Rentabilisé en {stats['roi_mois']:.1f} mois")


def render_action_card(action: EcoAction):
    """Affiche une card d'action"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            type_label = TYPE_LABELS.get(action.type_action, "🌿")
            status = "✅" if action.actif else "⏸️"
            st.markdown(f"{status} **{action.nom}** {type_label}")
            
            if action.description:
                st.caption(action.description[:100])
            
            if action.date_debut:
                mois_actifs = (date.today() - action.date_debut).days // 30
                st.caption(f"📅 Depuis {mois_actifs} mois ({action.date_debut})")
        
        with col2:
            if action.economie_mensuelle:
                st.metric("💰/mois", f"{action.economie_mensuelle:.0f}€")
            
            if action.cout_initial and action.cout_initial > 0:
                st.caption(f"Coût initial: {action.cout_initial:.0f}€")
        
        with col3:
            # Toggle actif
            new_actif = st.checkbox(
                "Actif",
                value=action.actif,
                key=f"actif_{action.id}"
            )
            if new_actif != action.actif:
                update_action(action.id, {"actif": new_actif})
                st.rerun()
            
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{action.id}", help="Modifier"):
                    st.session_state["edit_action_id"] = action.id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{action.id}", help="Supprimer"):
                    delete_action(action.id)
                    st.rerun()


def render_formulaire(action: Optional[EcoAction] = None):
    """Formulaire d'ajout/édition d'action"""
    is_edit = action is not None
    prefix = "edit" if is_edit else "new"
    
    with st.form(f"form_action_{prefix}"):
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input(
                "Nom de l'action *",
                value=action.nom if is_edit else "",
                placeholder="Ex: Essuie-tout lavables"
            )
            
            types = list(TYPE_LABELS.keys())
            type_index = types.index(action.type_action) if is_edit and action.type_action in types else 0
            type_action = st.selectbox(
                "Type",
                options=types,
                format_func=lambda x: TYPE_LABELS.get(x, x),
                index=type_index
            )
            
            description = st.text_area(
                "Description",
                value=action.description if is_edit else "",
                placeholder="Détails de l'action..."
            )
        
        with col2:
            economie_mensuelle = st.number_input(
                "Économie mensuelle (€)",
                min_value=0.0,
                value=float(action.economie_mensuelle) if is_edit and action.economie_mensuelle else 0.0,
                step=1.0
            )
            
            cout_initial = st.number_input(
                "Coût initial (€)",
                min_value=0.0,
                value=float(action.cout_initial) if is_edit and action.cout_initial else 0.0,
                step=5.0
            )
            
            date_debut = st.date_input(
                "Date de début",
                value=action.date_debut if is_edit and action.date_debut else date.today()
            )
            
            actif = st.checkbox(
                "Action active",
                value=action.actif if is_edit else True
            )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not nom:
                st.error("Le nom est obligatoire!")
                return
            
            data = {
                "nom": nom,
                "type_action": type_action,
                "description": description or None,
                "economie_mensuelle": Decimal(str(economie_mensuelle)) if economie_mensuelle > 0 else None,
                "cout_initial": Decimal(str(cout_initial)) if cout_initial > 0 else None,
                "date_debut": date_debut,
                "actif": actif
            }
            
            if is_edit:
                update_action(action.id, data)
                st.success("✅ Action mise à jour!")
            else:
                create_action(data)
                st.success("✅ Action ajoutée!")
            
            st.rerun()


def render_idees():
    """Affiche les idées d'actions avec bouton d'ajout rapide"""
    st.subheader("💡 Idées d'actions")
    st.caption("Cliquez pour ajouter rapidement une action")
    
    # Récupérer les noms des actions existantes
    actions_existantes = [a.nom.lower() for a in get_all_actions()]
    
    for idee in IDEES_ACTIONS:
        deja_fait = idee["nom"].lower() in actions_existantes
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                type_label = TYPE_LABELS.get(idee["type"], "🌿")
                status = "✅" if deja_fait else ""
                st.markdown(f"{status} **{idee['nom']}** {type_label}")
                st.caption(idee["description"])
            
            with col2:
                st.caption(f"💰 ~{idee['economie_estimee']}€/mois")
                if idee["cout_initial"] > 0:
                    st.caption(f"Coût: {idee['cout_initial']}€")
            
            with col3:
                if not deja_fait:
                    if st.button("➕ Ajouter", key=f"add_idea_{idee['nom']}"):
                        create_action({
                            "nom": idee["nom"],
                            "type_action": idee["type"],
                            "description": idee["description"],
                            "economie_mensuelle": Decimal(str(idee["economie_estimee"])),
                            "cout_initial": Decimal(str(idee["cout_initial"])),
                            "date_debut": date.today(),
                            "actif": False  # À activer manuellement
                        })
                        st.success(f"✅ '{idee['nom']}' ajouté! Activez-le quand vous commencez.")
                        st.rerun()
                else:
                    st.success("✅ Déjà ajouté")


# ═══════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════

def render_onglet_mes_actions():
    """Onglet mes actions en cours"""
    actions = get_all_actions()
    
    if not actions:
        st.info("🌿 Aucune action éco pour le moment. Ajoutez-en une!")
        return
    
    # Filtrer par type
    filtre = st.radio(
        "Filtrer",
        options=["Toutes", "Actives", "En pause"],
        horizontal=True
    )
    
    if filtre == "Actives":
        actions = [a for a in actions if a.actif]
    elif filtre == "En pause":
        actions = [a for a in actions if not a.actif]
    
    st.caption(f"🌿 {len(actions)} action(s)")
    
    for action in actions:
        render_action_card(action)


def render_onglet_ajouter():
    """Onglet ajout"""
    st.subheader("➕ Nouvelle action éco")
    render_formulaire(None)


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module Éco-Tips"""
    st.title("💡 Éco-Tips")
    st.caption("Suivez vos actions écologiques et vos économies")
    
    # Mode édition
    if "edit_action_id" in st.session_state:
        action = get_action_by_id(st.session_state["edit_action_id"])
        if action:
            st.subheader(f"✏️ Modifier: {action.nom}")
            if st.button("❌ Annuler"):
                del st.session_state["edit_action_id"]
                st.rerun()
            render_formulaire(action)
            del st.session_state["edit_action_id"]
            return
    
    # Dashboard stats en haut
    render_stats_dashboard()
    
    st.divider()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["🌿 Mes actions", "➕ Ajouter", "💡 Idées"])
    
    with tab1:
        render_onglet_mes_actions()
    
    with tab2:
        render_onglet_ajouter()
    
    with tab3:
        render_idees()

