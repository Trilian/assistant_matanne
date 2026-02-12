"""
Module Depenses Maison - Composants UI
"""

from .utils import (
    st, date, Decimal, Optional,
    obtenir_contexte_db, HouseExpense,
    CATEGORY_LABELS, CATEGORIES_AVEC_CONSO, MOIS_FR
)
from .crud import (
    get_depenses_mois, get_depense_by_id, get_stats_globales,
    get_historique_categorie, create_depense, update_depense, delete_depense
)


def render_stats_dashboard():
    """Affiche le dashboard de stats"""
    stats = get_stats_globales()
    today = date.today()
    
    st.subheader(f"📊 Resume {MOIS_FR[today.month]} {today.year}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_str = f"{stats['delta']:+.0f}€" if stats['delta'] != 0 else None
        st.metric("Ce mois", f"{stats['total_mois']:.0f}€", delta=delta_str, delta_color="inverse")
    
    with col2:
        st.metric("Mois precedent", f"{stats['total_prec']:.0f}€")
    
    with col3:
        st.metric("Moyenne mensuelle", f"{stats['moyenne_mensuelle']:.0f}€")
    
    with col4:
        st.metric("Categories", stats["nb_categories"])


def render_depense_card(depense: HouseExpense):
    """Affiche une card de depense"""
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
    """Formulaire d'ajout/edition"""
    is_edit = depense is not None
    prefix = "edit" if is_edit else "new"
    today = date.today()
    
    with st.form(f"form_depense_{prefix}"):
        col1, col2 = st.columns(2)
        
        with col1:
            categories = list(CATEGORY_LABELS.keys())
            cat_index = categories.index(depense.categorie) if is_edit and depense.categorie in categories else 0
            categorie = st.selectbox(
                "Categorie *",
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
            
            # Consommation (pour gaz, eau, electricite)
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
                    "Annee",
                    min_value=2020,
                    max_value=2030,
                    value=depense.annee if is_edit else today.year
                )
            
            note = st.text_area(
                "Note",
                value=depense.note if is_edit else "",
                placeholder="Commentaire, reference facture..."
            )
        
        submitted = st.form_submit_button(
            "💾 Enregistrer" if is_edit else "➕ Ajouter",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if montant <= 0:
                st.error("Le montant doit être superieur à 0!")
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
                st.success("✅ Depense mise à jour!")
            else:
                create_depense(data)
                st.success("✅ Depense ajoutee!")
            
            st.rerun()


def render_graphique_evolution():
    """Affiche le graphique d'evolution"""
    st.subheader("📈 Évolution")
    
    # Selection categorie
    categorie = st.selectbox(
        "Categorie à afficher",
        options=["total"] + list(CATEGORY_LABELS.keys()),
        format_func=lambda x: "📊 Total toutes categories" if x == "total" else CATEGORY_LABELS.get(x, x)
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
    """Compare les depenses de 2 mois"""
    st.subheader("⚖️ Comparaison")
    
    today = date.today()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("Mois 1")
        mois1 = st.selectbox("Mois", range(1, 13), format_func=lambda x: MOIS_FR[x], index=today.month - 1, key="mois1")
        annee1 = st.number_input("Annee", 2020, 2030, today.year, key="annee1")
    
    with col2:
        st.caption("Mois 2")
        mois_prec = today.month - 1 if today.month > 1 else 12
        annee_prec = today.year if today.month > 1 else today.year - 1
        mois2 = st.selectbox("Mois", range(1, 13), format_func=lambda x: MOIS_FR[x], index=mois_prec - 1, key="mois2")
        annee2 = st.number_input("Annee", 2020, 2030, annee_prec, key="annee2")
    
    if st.button("Comparer", type="primary"):
        dep1 = get_depenses_mois(mois1, int(annee1))
        dep2 = get_depenses_mois(mois2, int(annee2))
        
        # Grouper par categorie
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


def render_onglet_mois():
    """Onglet depenses du mois"""
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
            "Annee",
            min_value=2020,
            max_value=2030,
            value=today.year
        )
    
    depenses = get_depenses_mois(mois, int(annee))
    
    if not depenses:
        st.info(f"Aucune depense enregistree pour {MOIS_FR[mois]} {annee}")
        return
    
    # Total
    total = sum(float(d.montant) for d in depenses)
    st.metric(f"Total {MOIS_FR[mois]} {annee}", f"{total:.2f}€")
    
    st.divider()
    
    for depense in depenses:
        render_depense_card(depense)


def render_onglet_ajouter():
    """Onglet ajout"""
    st.subheader("➕ Ajouter une depense")
    render_formulaire(None)


def render_onglet_analyse():
    """Onglet analyse et graphiques"""
    render_graphique_evolution()
    st.divider()
    render_comparaison_mois()

