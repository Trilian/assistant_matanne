"""
Module Achats Famille - Composants UI
"""

from ._common import (
    st, date,
    get_db_context, FamilyPurchase,
    CATEGORIES, PRIORITES
)
from .helpers import (
    get_all_purchases, get_purchases_by_groupe, get_stats,
    mark_as_bought, delete_purchase
)


def render_dashboard():
    """Affiche le dashboard des achats"""
    stats = get_stats()
    
    st.subheader("📊 Vue d'ensemble")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 En attente", stats["en_attente"])
    
    with col2:
        st.metric("⚠️ Urgents", stats["urgents"])
    
    with col3:
        st.metric("💰 Budget estimé", f"{stats['total_estime']:.0f}€")
    
    with col4:
        st.metric("✅ Achetés", stats["achetes"])
    
    # Liste des urgents
    st.markdown("---")
    st.markdown("**🔴 À acheter en priorité:**")
    
    try:
        with get_db_context() as db:
            urgents = db.query(FamilyPurchase).filter(
                FamilyPurchase.achete == False,
                FamilyPurchase.priorite.in_(["urgent", "haute"])
            ).order_by(FamilyPurchase.priorite).limit(5).all()
            
            if urgents:
                for p in urgents:
                    cat_info = CATEGORIES.get(p.categorie, {"emoji": "📦"})
                    prio_info = PRIORITES.get(p.priorite, {"emoji": "⚪"})
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"{prio_info['emoji']} {cat_info['emoji']} **{p.nom}**")
                    with col2:
                        if p.prix_estime:
                            st.write(f"~{p.prix_estime:.0f}€")
            else:
                st.success("✅ Rien d'urgent!")
    except:
        st.info("Aucun achat urgent")


def render_liste_groupe(groupe: str, titre: str):
    """Affiche la liste d'achats d'un groupe"""
    st.subheader(titre)
    
    achats = get_purchases_by_groupe(groupe, achete=False)
    
    if not achats:
        st.info("Aucun article en attente dans cette catégorie")
        return
    
    # Grouper par priorité
    for prio_key in ["urgent", "haute", "moyenne", "basse", "optionnel"]:
        achats_prio = [a for a in achats if a.priorite == prio_key]
        if not achats_prio:
            continue
        
        prio_info = PRIORITES[prio_key]
        st.markdown(f"**{prio_info['emoji']} {prio_info['label']}**")
        
        for achat in achats_prio:
            render_achat_card(achat)


def render_achat_card(achat: FamilyPurchase):
    """Affiche une card d'achat"""
    cat_info = CATEGORIES.get(achat.categorie, {"emoji": "📦", "label": "Autre"})
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{cat_info['emoji']} {achat.nom}**")
            
            details = []
            if achat.taille:
                details.append(f"Taille: {achat.taille}")
            if achat.magasin:
                details.append(f"📍 {achat.magasin}")
            if details:
                st.caption(" • ".join(details))
            
            if achat.description:
                st.caption(achat.description)
            
            if achat.url:
                st.markdown(f"[🔗 Voir]({achat.url})")
        
        with col2:
            if achat.prix_estime:
                st.write(f"~{achat.prix_estime:.0f}€")
        
        with col3:
            if st.button("✅", key=f"buy_{achat.id}", help="Marquer acheté"):
                mark_as_bought(achat.id)
                st.rerun()
            
            if st.button("🗑️", key=f"del_{achat.id}", help="Supprimer"):
                delete_purchase(achat.id)
                st.rerun()


def render_add_form():
    """Formulaire d'ajout d'achat"""
    st.subheader("➕ Ajouter un article")
    
    with st.form("add_purchase"):
        nom = st.text_input("Nom de l'article *", placeholder="Ex: Pantalon 18 mois")
        
        col1, col2 = st.columns(2)
        
        with col1:
            categorie = st.selectbox(
                "Catégorie *",
                list(CATEGORIES.keys()),
                format_func=lambda x: f"{CATEGORIES[x]['emoji']} {CATEGORIES[x]['label']}"
            )
        
        with col2:
            priorite = st.selectbox(
                "Priorité",
                list(PRIORITES.keys()),
                index=2,  # Moyenne par défaut
                format_func=lambda x: f"{PRIORITES[x]['emoji']} {PRIORITES[x]['label']}"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            prix = st.number_input("Prix estimé (€)", min_value=0.0, step=5.0)
        
        with col4:
            taille = st.text_input("Taille (optionnel)")
        
        col5, col6 = st.columns(2)
        
        with col5:
            magasin = st.text_input("Magasin (optionnel)")
        
        with col6:
            url = st.text_input("Lien URL (optionnel)")
        
        description = st.text_area("Notes", height=80)
        
        # Pour jouets Jules
        if "jouets" in categorie:
            age_recommande = st.number_input(
                "Âge recommandé (mois)", 
                min_value=0, 
                max_value=120,
                value=18
            )
        else:
            age_recommande = None
        
        if st.form_submit_button("✅ Ajouter", type="primary"):
            if not nom:
                st.error("Nom requis")
            else:
                try:
                    with get_db_context() as db:
                        purchase = FamilyPurchase(
                            nom=nom,
                            categorie=categorie,
                            priorite=priorite,
                            prix_estime=prix if prix > 0 else None,
                            taille=taille or None,
                            magasin=magasin or None,
                            url=url or None,
                            description=description or None,
                            age_recommande_mois=age_recommande,
                            suggere_par="manuel"
                        )
                        db.add(purchase)
                        db.commit()
                        st.success(f"✅ {nom} ajouté!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")


def render_historique():
    """Affiche l'historique des achats"""
    st.subheader("📜 Historique des achats")
    
    achats = get_all_purchases(achete=True)
    
    if not achats:
        st.info("Aucun achat enregistré")
        return
    
    # Trier par date d'achat (plus récent d'abord)
    achats_tries = sorted(achats, key=lambda x: x.date_achat or date.min, reverse=True)
    
    # Stats
    total = sum(a.prix_reel or a.prix_estime or 0 for a in achats_tries)
    st.metric("💰 Total dépensé", f"{total:.0f}€")
    
    st.markdown("---")
    
    # Liste
    for achat in achats_tries[:20]:  # Limiter à 20
        cat_info = CATEGORIES.get(achat.categorie, {"emoji": "📦"})
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{cat_info['emoji']} {achat.nom}**")
                if achat.magasin:
                    st.caption(f"📍 {achat.magasin}")
            
            with col2:
                prix = achat.prix_reel or achat.prix_estime or 0
                st.write(f"{prix:.0f}€")
            
            with col3:
                if achat.date_achat:
                    st.caption(achat.date_achat.strftime("%d/%m/%Y"))


def render_par_magasin():
    """Vue par magasin pour les courses"""
    st.subheader("🏪 Par magasin")
    
    achats = get_all_purchases(achete=False)
    
    if not achats:
        st.info("Aucun article en attente")
        return
    
    # Grouper par magasin
    par_magasin = {}
    sans_magasin = []
    
    for achat in achats:
        if achat.magasin:
            if achat.magasin not in par_magasin:
                par_magasin[achat.magasin] = []
            par_magasin[achat.magasin].append(achat)
        else:
            sans_magasin.append(achat)
    
    # Afficher par magasin
    for magasin, articles in sorted(par_magasin.items()):
        total = sum(a.prix_estime or 0 for a in articles)
        
        with st.expander(f"📍 **{magasin}** ({len(articles)} articles, ~{total:.0f}€)"):
            for achat in articles:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"• {achat.nom}")
                with col2:
                    if st.checkbox("", key=f"check_{achat.id}"):
                        mark_as_bought(achat.id)
                        st.rerun()
    
    # Sans magasin
    if sans_magasin:
        with st.expander(f"❓ **Sans magasin** ({len(sans_magasin)} articles)"):
            for achat in sans_magasin:
                st.write(f"• {achat.nom}")
