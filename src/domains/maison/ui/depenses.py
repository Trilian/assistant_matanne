"""
Module Dépenses Maison - Suivi des factures (gaz, eau, électricité, etc.)

Focus sur les dépenses récurrentes de la maison avec consommation.
Utilise le service Budget unifié (src/services/budget.py) pour:
- Ajouter/modifier les factures
- Obtenir l'évolution de consommation
- Analyser les tendances

NOTE: Ce module track spécifiquement les FACTURES avec consommation (kWh, m³).
Le service Budget général gère les dépenses courantes par catégories.
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
import calendar

from src.core.database import get_db_context
from src.core.models import HouseExpense
from src.core.models.maison_extended import ExpenseCategory
from src.services.budget import (
    get_budget_service,
    FactureMaison,
    CategorieDepense,
)


# ═══════════════════════════════════════════════════════════
# CONSTANTES - Focus factures maison
# ═══════════════════════════════════════════════════════════

CATEGORY_LABELS = {
    "gaz": "🔥 Gaz (chauffage)",
    "electricite": "⚡ Électricité",
    "eau": "💧 Eau",
    "internet": "📶 Internet/Box",
    "loyer": "🏠 Loyer",
    "creche": "👶 Crèche Jules",
    "assurance": "🛡️ Assurance habitation",
    "taxe_fonciere": "🏛️ Taxe foncière",
    "entretien": "🔧 Entretien (chaudière...)",
    "autre": "📦 Autre"
}

# Catégories avec suivi consommation
CATEGORIES_AVEC_CONSO = {"gaz", "electricite", "eau"}

MOIS_FR = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]


# ═══════════════════════════════════════════════════════════
# CRUD FUNCTIONS (via service budget si possible)
# ═══════════════════════════════════════════════════════════

def get_depenses_mois(mois: int, annee: int) -> List[HouseExpense]:
    """Récupère les dépenses d'un mois"""
    try:
        with get_db_context() as db:
            return db.query(HouseExpense).filter(
                HouseExpense.mois == mois,
                HouseExpense.annee == annee
            ).order_by(HouseExpense.categorie).all()
    except Exception:
        return []


def get_depenses_annee(annee: int) -> List[HouseExpense]:
    """Récupère toutes les dépenses d'une année"""
    try:
        with get_db_context() as db:
            return db.query(HouseExpense).filter(
                HouseExpense.annee == annee
            ).order_by(HouseExpense.mois, HouseExpense.categorie).all()
    except Exception:
        return []


def get_depense_by_id(depense_id: int) -> Optional[HouseExpense]:
    """Récupère une dépense par ID"""
    try:
        with get_db_context() as db:
            return db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
    except Exception:
        return None


def create_depense(data: dict) -> HouseExpense:
    """Crée une nouvelle dépense - utilise le service budget si catégorie énergie."""
    # Pour gaz/elec/eau, passer par le service budget unifié
    if data.get("categorie") in CATEGORIES_AVEC_CONSO:
        service = get_budget_service()
        facture = FactureMaison(
            categorie=CategorieDepense(data["categorie"]),
            montant=data["montant"],
            consommation=data.get("consommation"),
            unite_consommation=data.get("unite", ""),
            mois=data["mois"],
            annee=data["annee"],
            date_facture=data.get("date_facture"),
            fournisseur=data.get("fournisseur", ""),
            numero_facture=data.get("numero_facture", ""),
            note=data.get("note", ""),
        )
        service.ajouter_facture_maison(facture)
    
    # Toujours créer aussi dans HouseExpense pour compatibilité
    with get_db_context() as db:
        depense = HouseExpense(**data)
        db.add(depense)
        db.commit()
        db.refresh(depense)
        return depense


def update_depense(depense_id: int, data: dict) -> Optional[HouseExpense]:
    """Met à jour une dépense"""
    with get_db_context() as db:
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            for key, value in data.items():
                setattr(depense, key, value)
            db.commit()
            db.refresh(depense)
        return depense


def delete_depense(depense_id: int) -> bool:
    """Supprime une dépense"""
    with get_db_context() as db:
        depense = db.query(HouseExpense).filter(HouseExpense.id == depense_id).first()
        if depense:
            db.delete(depense)
            db.commit()
            return True
        return False


def get_stats_globales() -> dict:
    """Calcule les statistiques globales"""
    today = date.today()
    
    # Ce mois
    depenses_mois = get_depenses_mois(today.month, today.year)
    total_mois = sum(float(d.montant) for d in depenses_mois)
    
    # Mois précédent
    if today.month == 1:
        mois_prec, annee_prec = 12, today.year - 1
    else:
        mois_prec, annee_prec = today.month - 1, today.year
    
    depenses_prec = get_depenses_mois(mois_prec, annee_prec)
    total_prec = sum(float(d.montant) for d in depenses_prec)
    
    # Delta
    delta = total_mois - total_prec if total_prec > 0 else 0
    delta_pct = (delta / total_prec * 100) if total_prec > 0 else 0
    
    # Moyenne mensuelle (12 derniers mois)
    depenses_annee = get_depenses_annee(today.year)
    depenses_annee_prec = get_depenses_annee(today.year - 1)
    all_depenses = depenses_annee + depenses_annee_prec
    
    # Grouper par mois
    par_mois = {}
    for d in all_depenses:
        key = f"{d.annee}-{d.mois:02d}"
        if key not in par_mois:
            par_mois[key] = 0
        par_mois[key] += float(d.montant)
    
    moyenne = sum(par_mois.values()) / len(par_mois) if par_mois else 0
    
    return {
        "total_mois": total_mois,
        "total_prec": total_prec,
        "delta": delta,
        "delta_pct": delta_pct,
        "moyenne_mensuelle": moyenne,
        "nb_categories": len(set(d.categorie for d in depenses_mois))
    }


def get_historique_categorie(categorie: str, nb_mois: int = 12) -> List[dict]:
    """Récupère l'historique d'une catégorie"""
    today = date.today()
    result = []
    
    for i in range(nb_mois):
        mois = today.month - i
        annee = today.year
        while mois <= 0:
            mois += 12
            annee -= 1
        
        with get_db_context() as db:
            depense = db.query(HouseExpense).filter(
                HouseExpense.categorie == categorie,
                HouseExpense.mois == mois,
                HouseExpense.annee == annee
            ).first()
        
        result.append({
            "mois": mois,
            "annee": annee,
            "label": f"{MOIS_FR[mois][:3]} {annee}",
            "montant": float(depense.montant) if depense else 0,
            "consommation": float(depense.consommation) if depense and depense.consommation else 0
        })
    
    return list(reversed(result))


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════

def render_stats_dashboard():
    """Affiche le dashboard de stats"""
    stats = get_stats_globales()
    today = date.today()
    
    st.subheader(f"📊 Résumé {MOIS_FR[today.month]} {today.year}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_str = f"{stats['delta']:+.0f}€" if stats['delta'] != 0 else None
        st.metric("Ce mois", f"{stats['total_mois']:.0f}€", delta=delta_str, delta_color="inverse")
    
    with col2:
        st.metric("Mois précédent", f"{stats['total_prec']:.0f}€")
    
    with col3:
        st.metric("Moyenne mensuelle", f"{stats['moyenne_mensuelle']:.0f}€")
    
    with col4:
        st.metric("Catégories", stats["nb_categories"])


def render_depense_card(depense: HouseExpense):
    """Affiche une card de dépense"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            cat_label = CATEGORY_LABELS.get(depense.categorie, depense.categorie)
            st.markdown(f"**{cat_label}**")
            
            if depense.note:
                st.caption(depense.note)
            
            if depense.consommation:
                unite = "kWh" if depense.categorie == "electricite" else "m³" if depense.categorie in ["gaz", "eau"] else ""
                st.caption(f"📏 {depense.consommation} {unite}")
        
        with col2:
            st.metric("Montant", f"{depense.montant:.2f}€")
        
        with col3:
            col_edit, col_del = st.columns(2)
            with col_edit:
                if st.button("✏️", key=f"edit_{depense.id}", help="Modifier"):
                    st.session_state["edit_depense_id"] = depense.id
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_{depense.id}", help="Supprimer"):
                    delete_depense(depense.id)
                    st.rerun()


def render_formulaire(depense: Optional[HouseExpense] = None):
    """Formulaire d'ajout/édition"""
    is_edit = depense is not None
    prefix = "edit" if is_edit else "new"
    today = date.today()
    
    with st.form(f"form_depense_{prefix}"):
        col1, col2 = st.columns(2)
        
        with col1:
            categories = list(CATEGORY_LABELS.keys())
            cat_index = categories.index(depense.categorie) if is_edit and depense.categorie in categories else 0
            categorie = st.selectbox(
                "Catégorie *",
                options=categories,
                format_func=lambda x: CATEGORY_LABELS.get(x, x),
                index=cat_index
            )
            
            montant = st.number_input(
                "Montant (€) *",
                min_value=0.0,
                value=float(depense.montant) if is_edit else 0.0,
                step=0.01
            )
            
            # Consommation (pour gaz, eau, électricité)
            if categorie in ["gaz", "eau", "electricite"]:
                unite = "kWh" if categorie == "electricite" else "m³"
                consommation = st.number_input(
                    f"Consommation ({unite})",
                    min_value=0.0,
                    value=float(depense.consommation) if is_edit and depense.consommation else 0.0,
                    step=1.0
                )
            else:
                consommation = 0.0
        
        with col2:
            col_mois, col_annee = st.columns(2)
            with col_mois:
                mois = st.selectbox(
                    "Mois",
                    options=range(1, 13),
                    format_func=lambda x: MOIS_FR[x],
                    index=(depense.mois - 1) if is_edit else (today.month - 1)
                )
            with col_annee:
                annee = st.number_input(
                    "Année",
                    min_value=2020,
                    max_value=2030,
                    value=depense.annee if is_edit else today.year
                )
            
            note = st.text_area(
                "Note",
                value=depense.note if is_edit else "",
                placeholder="Commentaire, référence facture..."
            )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if montant <= 0:
                st.error("Le montant doit être supérieur à 0!")
                return
            
            data = {
                "categorie": categorie,
                "montant": Decimal(str(montant)),
                "consommation": Decimal(str(consommation)) if consommation > 0 else None,
                "mois": mois,
                "annee": int(annee),
                "note": note or None
            }
            
            if is_edit:
                update_depense(depense.id, data)
                st.success("✅ Dépense mise à jour!")
            else:
                create_depense(data)
                st.success("✅ Dépense ajoutée!")
            
            st.rerun()


def render_graphique_evolution():
    """Affiche le graphique d'évolution"""
    st.subheader("📈 Évolution")
    
    # Sélection catégorie
    categorie = st.selectbox(
        "Catégorie à afficher",
        options=["total"] + list(CATEGORY_LABELS.keys()),
        format_func=lambda x: "📊 Total toutes catégories" if x == "total" else CATEGORY_LABELS.get(x, x)
    )
    
    today = date.today()
    
    if categorie == "total":
        # Calculer le total par mois
        data = []
        for i in range(12):
            mois = today.month - i
            annee = today.year
            while mois <= 0:
                mois += 12
                annee -= 1
            
            depenses = get_depenses_mois(mois, annee)
            total = sum(float(d.montant) for d in depenses)
            data.append({
                "Mois": f"{MOIS_FR[mois][:3]} {annee}",
                "Montant": total
            })
        data = list(reversed(data))
    else:
        historique = get_historique_categorie(categorie, 12)
        data = [{"Mois": h["label"], "Montant": h["montant"]} for h in historique]
    
    if data:
        import pandas as pd
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index("Mois"))


def render_comparaison_mois():
    """Compare les dépenses de 2 mois"""
    st.subheader("⚖️ Comparaison")
    
    today = date.today()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Mois 1")
        mois1 = st.selectbox("Mois", range(1, 13), format_func=lambda x: MOIS_FR[x], index=today.month - 1, key="mois1")
        annee1 = st.number_input("Année", 2020, 2030, today.year, key="annee1")
    
    with col2:
        st.caption("Mois 2")
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        mois2 = st.selectbox("Mois", range(1, 13), format_func=lambda x: MOIS_FR[x], index=mois_prec - 1, key="mois2")
        annee2 = st.number_input("Année", 2020, 2030, annee_prec, key="annee2")
    
    if st.button("Comparer", type="primary"):
        dep1 = get_depenses_mois(mois1, int(annee1))
        dep2 = get_depenses_mois(mois2, int(annee2))
        
        # Grouper par catégorie
        par_cat1 = {d.categorie: float(d.montant) for d in dep1}
        par_cat2 = {d.categorie: float(d.montant) for d in dep2}
        
        all_cats = set(par_cat1.keys()) | set(par_cat2.keys())
        
        st.divider()
        
        for cat in sorted(all_cats):
            val1 = par_cat1.get(cat, 0)
            val2 = par_cat2.get(cat, 0)
            delta = val1 - val2
            
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.markdown(f"**{CATEGORY_LABELS.get(cat, cat)}**")
            with col_b:
                st.caption(f"{MOIS_FR[mois1]}: {val1:.0f}€")
                st.caption(f"{MOIS_FR[mois2]}: {val2:.0f}€")
            with col_c:
                if delta != 0:
                    color = "🔴" if delta > 0 else "🟢"
                    st.markdown(f"{color} {delta:+.0f}€")
        
        st.divider()
        total1 = sum(par_cat1.values())
        total2 = sum(par_cat2.values())
        delta_total = total1 - total2
        
        st.markdown(f"**TOTAL**: {total1:.0f}€ vs {total2:.0f}€ = **{delta_total:+.0f}€**")


# ═══════════════════════════════════════════════════════════
# ONGLETS
# ═══════════════════════════════════════════════════════════

def render_onglet_mois():
    """Onglet dépenses du mois"""
    today = date.today()
    
    col1, col2 = st.columns(2)
    with col1:
        mois = st.selectbox(
            "Mois",
            options=range(1, 13),
            format_func=lambda x: MOIS_FR[x],
            index=today.month - 1
        )
    with col2:
        annee = st.number_input(
            "Année",
            min_value=2020,
            max_value=2030,
            value=today.year
        )
    
    depenses = get_depenses_mois(mois, int(annee))
    
    if not depenses:
        st.info(f"Aucune dépense enregistrée pour {MOIS_FR[mois]} {annee}")
        return
    
    # Total
    total = sum(float(d.montant) for d in depenses)
    st.metric(f"Total {MOIS_FR[mois]} {annee}", f"{total:.2f}€")
    
    st.divider()
    
    for depense in depenses:
        render_depense_card(depense)


def render_onglet_ajouter():
    """Onglet ajout"""
    st.subheader("➕ Ajouter une dépense")
    render_formulaire(None)


def render_onglet_analyse():
    """Onglet analyse et graphiques"""
    render_graphique_evolution()
    st.divider()
    render_comparaison_mois()


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module Dépenses"""
    st.title("💰 Dépenses Maison")
    st.caption("Suivez vos dépenses: gaz, eau, électricité, loyer...")
    
    # Mode édition
    if "edit_depense_id" in st.session_state:
        depense = get_depense_by_id(st.session_state["edit_depense_id"])
        if depense:
            st.subheader(f"✏️ Modifier: {CATEGORY_LABELS.get(depense.categorie, depense.categorie)}")
            if st.button("❌ Annuler"):
                del st.session_state["edit_depense_id"]
                st.rerun()
            render_formulaire(depense)
            del st.session_state["edit_depense_id"]
            return
    
    # Dashboard
    render_stats_dashboard()
    
    st.divider()
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📅 Ce mois", "➕ Ajouter", "📈 Analyse"])
    
    with tab1:
        render_onglet_mois()
    
    with tab2:
        render_onglet_ajouter()
    
    with tab3:
        render_onglet_analyse()
