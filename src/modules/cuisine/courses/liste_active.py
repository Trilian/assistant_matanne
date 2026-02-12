"""
Liste active des courses.
"""

from ._common import (
    st, logger, datetime, 
    get_courses_service, get_inventaire_service,
    PRIORITY_EMOJIS, RAYONS_DEFAULT,
)


def render_liste_active():
    """Gestion interactive de la liste active"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()
    
    if service is None:
        st.error("âŒ Service courses indisponible")
        return
    
    try:
        # RÃecupÃerer la liste
        liste = service.get_liste_courses(achetes=False)
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("ðŸ“¥ Ã€ acheter", len(liste))
        with col2:
            haute = len([a for a in liste if a.get("priorite") == "haute"])
            st.metric("ðŸ”´ Haute prioritÃe", haute)
        with col3:
            if inventaire_service:
                alertes = inventaire_service.get_alertes()
                stock_bas = len(alertes.get("stock_bas", []))
                st.metric("âš ï¸ Stock bas", stock_bas)
        with col4:
            st.metric("ðŸ’° Total articles", len(service.get_liste_courses(achetes=True)))
        
        st.divider()
        
        if not liste:
            st.info("âœ… Liste vide! Ajoutez des articles ou gÃenÃerez des suggestions IA.")
            if st.button("âœ¨ GÃenÃerer suggestions IA"):
                st.session_state.new_article_mode = False
                st.rerun()
            return
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_priorite = st.selectbox(
                "Filtrer par prioritÃe",
                ["Toutes", "ðŸ”´ Haute", "ðŸŸ¡ Moyenne", "ðŸŸ¢ Basse"],
                key="filter_priorite"
            )
        with col2:
            filter_rayon = st.selectbox(
                "Filtrer par rayon",
                ["Tous les rayons"] + sorted(set(a.get("rayon_magasin", "Autre") for a in liste)),
                key="filter_rayon"
            )
        with col3:
            search_term = st.text_input("ðŸ” Chercher...", key="search_courses")
        
        # Appliquer filtres
        liste_filtree = liste.copy()
        
        if filter_priorite != "Toutes":
            priority_map = {"ðŸ”´ Haute": "haute", "ðŸŸ¡ Moyenne": "moyenne", "ðŸŸ¢ Basse": "basse"}
            liste_filtree = [a for a in liste_filtree if a.get("priorite") == priority_map[filter_priorite]]
        
        if filter_rayon != "Tous les rayons":
            liste_filtree = [a for a in liste_filtree if a.get("rayon_magasin") == filter_rayon]
        
        if search_term:
            liste_filtree = [a for a in liste_filtree if search_term.lower() in a.get("ingredient_nom", "").lower()]
        
        st.success(f"ðŸ“Š {len(liste_filtree)}/{len(liste)} article(s)")
        
        # Afficher par rayon
        st.subheader("ðŸ“¦ Articles par rayon")
        
        rayons = {}
        for article in liste_filtree:
            rayon = article.get("rayon_magasin", "Autre")
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(article)
        
        for rayon in sorted(rayons.keys()):
            with st.expander(f"ðŸª‘ {rayon} ({len(rayons[rayon])} articles)", expanded=True):
                render_rayon_articles(service, rayon, rayons[rayon])
        
        st.divider()
        
        # Actions rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("âž• Ajouter article", use_container_width=True):
                st.session_state.new_article_mode = True
                st.rerun()
        with col2:
            if st.button("ðŸ“„ Imprimer liste", use_container_width=True):
                render_print_view(liste_filtree)
        with col3:
            if st.button("ðŸ—‘ï¸ Vider (achetÃes)", use_container_width=True):
                if service.get_liste_courses(achetes=True):
                    st.warning("âš ï¸ Suppression des articles achetÃes...")
                    st.session_state.courses_refresh += 1
                    st.rerun()
        
        # Formulaire ajout article
        if st.session_state.new_article_mode:
            st.divider()
            render_ajouter_article()
            
    except Exception as e:
        st.error(f"âŒ Erreur: {str(e)}")
        logger.error(f"Erreur render_liste_active: {e}")


def render_rayon_articles(service, rayon: str, articles: list):
    """Affiche et gère les articles d'un rayon"""
    for article in articles:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1], gap="small")
        
        with col1:
            priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "âš«")
            label = f"{priorite_emoji} {article.get('ingredient_nom')} ({article.get('quantite_necessaire')} {article.get('unite')})"
            
            if article.get("notes"):
                label += f" | ðŸ“ {article.get('notes')}"
            
            if article.get("suggere_par_ia"):
                label += " âœ¨"
            
            st.write(label)
        
        with col2:
            if st.button("âœ…", key=f"article_mark_{article['id']}", help="Marquer achetÃe", use_container_width=True):
                try:
                    service.update(article['id'], {"achete": True, "achete_le": datetime.now()})
                    st.success(f"âœ… {article.get('ingredient_nom')} marquÃe achetÃe!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        with col3:
            if st.button("âœï¸", key=f"article_edit_{article['id']}", help="Modifier", use_container_width=True):
                st.session_state.edit_article_id = article['id']
                st.rerun()
        
        with col4:
            if st.button("ðŸ—‘ï¸", key=f"article_del_{article['id']}", help="Supprimer", use_container_width=True):
                try:
                    service.delete(article['id'])
                    st.success(f"âœ… {article.get('ingredient_nom')} supprimÃe!")
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        # Formulaire Ãedition inline si sÃelectionnÃe
        if st.session_state.get('edit_article_id') == article['id']:
            st.divider()
            with st.form(f"article_edit_form_{article['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_quantite = st.number_input(
                        "QuantitÃe",
                        value=article.get('quantite_necessaire', 1.0),
                        min_value=0.1,
                        step=0.1,
                        key=f"article_qty_{article['id']}"
                    )
                with col2:
                    new_priorite = st.selectbox(
                        "PrioritÃe",
                        list(PRIORITY_EMOJIS.keys()),
                        index=list(PRIORITY_EMOJIS.keys()).index(article.get('priorite', 'moyenne')),
                        key=f"article_prio_{article['id']}"
                    )
                
                new_rayon = st.selectbox(
                    "Rayon",
                    RAYONS_DEFAULT,
                    index=RAYONS_DEFAULT.index(article.get('rayon_magasin', 'Autre')) if article.get('rayon_magasin') in RAYONS_DEFAULT else -1,
                    key=f"article_ray_{article['id']}"
                )
                
                new_notes = st.text_area(
                    "Notes",
                    value=article.get('notes', ''),
                    max_chars=200,
                    key=f"article_notes_{article['id']}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("ðŸ’¾ Sauvegarder", key=f"article_save_{article['id']}"):
                        try:
                            service.update(article['id'], {
                                "quantite_necessaire": new_quantite,
                                "priorite": new_priorite,
                                "rayon_magasin": new_rayon,
                                "notes": new_notes or None
                            })
                            st.success("âœ… Article mis Ã  jour!")
                            st.session_state.edit_article_id = None
                            st.session_state.courses_refresh += 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"âŒ Erreur: {str(e)}")
                
                with col2:
                    if st.form_submit_button("âŒ Annuler", key=f"article_cancel_{article['id']}"):
                        st.session_state.edit_article_id = None
                        st.rerun()


def render_ajouter_article():
    """Formulaire ajout article"""
    st.subheader("âž• Ajouter un article")
    
    service = get_courses_service()
    if service is None:
        st.error("âŒ Service indisponible")
        return
    
    with st.form("form_new_article"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de l'article", placeholder="ex: Tomates", max_chars=100)
        with col2:
            unite = st.selectbox("UnitÃe", ["kg", "l", "pièce", "g", "ml", "paquet"])
        
        quantite = st.number_input("QuantitÃe", min_value=0.1, value=1.0, step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            priorite = st.selectbox("PrioritÃe", ["basse", "moyenne", "haute"])
        with col2:
            rayon = st.selectbox("Rayon", RAYONS_DEFAULT)
        
        notes = st.text_area("Notes (optionnel)", max_chars=200)
        
        submitted = st.form_submit_button("âœ… Ajouter", use_container_width=True)
        if submitted:
            if not nom:
                st.error("âš ï¸ Entrez un nom d'article")
                return
            
            try:
                # CrÃeer/trouver l'ingrÃedient
                from src.core.models import Ingredient
                from src.core.database import obtenir_contexte_db
                
                with obtenir_contexte_db() as db:
                    ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()
                    
                    if not ingredient:
                        ingredient = Ingredient(nom=nom, unite=unite)
                        db.add(ingredient)
                        db.flush()
                        db.refresh(ingredient)
                    
                    ingredient_id = ingredient.id
                
                # Ajouter article courses avec le service
                data = {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": quantite,
                    "priorite": priorite,
                    "rayon_magasin": rayon,
                    "notes": notes or None
                }
                
                service.create(data)
                
                st.success(f"âœ… {nom} ajoutÃe Ã  la liste!")
                st.session_state.new_article_mode = False
                st.session_state.courses_refresh += 1
                st.rerun()
            except Exception as e:
                st.error(f"âŒ Erreur: {str(e)}")
                logger.error(f"Erreur ajout article: {e}")


def render_print_view(liste):
    """Vue d'impression optimisÃee"""
    st.subheader("ðŸ–¨ï¸ Liste Ã  imprimer")
    
    # Grouper par rayon
    rayons = {}
    for article in liste:
        rayon = article.get("rayon_magasin", "Autre")
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)
    
    print_text = "ðŸ“‹ LISTE DE COURSES\n"
    print_text += f"ðŸ“… {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    print_text += "=" * 40 + "\n\n"
    
    for rayon in sorted(rayons.keys()):
        print_text += f"ðŸª‘ {rayon}\n"
        for article in rayons[rayon]:
            checkbox = "â˜‘"
            qty = f"{article.get('quantite_necessaire')} {article.get('unite')}"
            print_text += f"  {checkbox} {article.get('ingredient_nom')} ({qty})\n"
        print_text += "\n"
    
    st.text_area("Copier/Coller la liste:", value=print_text, height=400, disabled=True)


__all__ = [
    "render_liste_active",
    "render_rayon_articles",
    "render_ajouter_article",
    "render_print_view",
]
