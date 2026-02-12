"""
GÃenÃeration de courses depuis le planning repas.
"""

from ._common import st, logger, get_courses_intelligentes_service


def render_courses_depuis_planning():
    """GÃenère la liste de courses depuis le planning repas actif."""
    st.subheader("ðŸ½ï¸ Courses depuis le Planning")
    
    st.info("""
    **GÃenÃeration automatique** de la liste de courses basÃee sur votre planning de repas.
    
    Le système analyse les recettes planifiÃees, extrait les ingrÃedients,
    compare avec votre inventaire et gÃenère une liste optimisÃee.
    """)
    
    service = get_courses_intelligentes_service()
    
    # VÃerifier planning actif
    planning = service.obtenir_planning_actif()
    
    if not planning:
        st.warning("âš ï¸ Aucun planning actif trouvÃe.")
        st.caption("CrÃeez d'abord un planning de repas dans 'Cuisine â†’ Planning Semaine'")
        
        if st.button("ðŸ“… Aller au planning", use_container_width=True):
            # Naviguer vers planning
            st.session_state.current_page = "cuisine.planning_semaine"
            st.rerun()
        return
    
    # Afficher info planning
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"âœ… Planning actif: **{planning.nom}**")
        nb_repas = len(planning.repas) if planning.repas else 0
        st.caption(f"ðŸ“† Du {planning.semaine_debut} au {planning.semaine_fin} â€¢ {nb_repas} repas planifiÃes")
    
    with col2:
        # Bouton gÃenÃerer
        if st.button("ðŸ”„ GÃenÃerer la liste", type="primary", use_container_width=True):
            with st.spinner("Analyse du planning en cours..."):
                resultat = service.generer_liste_courses()
                st.session_state["courses_planning_resultat"] = resultat
                st.rerun()
    
    st.divider()
    
    # Afficher rÃesultat si disponible
    resultat = st.session_state.get("courses_planning_resultat")
    
    if resultat:
        # Alertes
        for alerte in resultat.alertes:
            if "âœ…" in alerte:
                st.success(alerte)
            elif "âš ï¸" in alerte:
                st.warning(alerte)
            else:
                st.info(alerte)
        
        if resultat.articles:
            # MÃetriques
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ðŸ›’ Articles Ã  acheter", resultat.total_articles)
            with col2:
                st.metric("ðŸ³ Recettes couvertes", len(resultat.recettes_couvertes))
            with col3:
                # RÃepartition par rayon
                rayons = set(a.rayon for a in resultat.articles)
                st.metric("ðŸ“¦ Rayons", len(rayons))
            
            # Recettes couvertes
            if resultat.recettes_couvertes:
                st.markdown("**Recettes concernÃees:**")
                st.caption(", ".join(resultat.recettes_couvertes[:5]))
            
            st.divider()
            
            # Afficher articles par rayon
            st.subheader("ðŸ“‹ Articles Ã  acheter")
            
            # Grouper par rayon
            articles_par_rayon = {}
            for article in resultat.articles:
                if article.rayon not in articles_par_rayon:
                    articles_par_rayon[article.rayon] = []
                articles_par_rayon[article.rayon].append(article)
            
            # SÃelection articles Ã  ajouter
            articles_selectionnes = []
            
            for rayon in sorted(articles_par_rayon.keys()):
                articles = articles_par_rayon[rayon]
                priorite_emoji = {1: "ðŸ”´", 2: "ðŸŸ¡", 3: "ðŸŸ¢"}.get(articles[0].priorite, "âšª")
                
                with st.expander(f"{priorite_emoji} {rayon} ({len(articles)} articles)", expanded=True):
                    for i, article in enumerate(articles):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            # Checkbox pour sÃelection
                            selected = st.checkbox(
                                f"**{article.nom}**",
                                value=True,
                                key=f"art_sel_{rayon}_{i}"
                            )
                            if selected:
                                articles_selectionnes.append(article)
                            
                            # Sources
                            sources = ", ".join(article.recettes_source[:2])
                            st.caption(f"ðŸ“– {sources}")
                        
                        with col2:
                            st.markdown(f"**{article.a_acheter:.0f}** {article.unite}")
                        
                        with col3:
                            if article.en_stock > 0:
                                st.caption(f"(en stock: {article.en_stock:.0f})")
            
            # Action finale
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    f"âœ… Ajouter {len(articles_selectionnes)} articles Ã  la liste",
                    type="primary",
                    use_container_width=True,
                    disabled=len(articles_selectionnes) == 0
                ):
                    with st.spinner("Ajout en cours..."):
                        ids = service.ajouter_a_liste_courses(articles_selectionnes)
                        if ids:
                            st.success(f"âœ… {len(ids)} articles ajoutÃes Ã  votre liste de courses!")
                            # Reset
                            del st.session_state["courses_planning_resultat"]
                            st.session_state.courses_refresh += 1
                            st.rerun()
            
            with col2:
                if st.button("ðŸ”„ RÃegÃenÃerer", use_container_width=True):
                    del st.session_state["courses_planning_resultat"]
                    st.rerun()
    else:
        # Instructions
        st.markdown("""
        ### Comment ça marche?
        
        1. **Analyse** - Le système parcourt toutes les recettes de votre planning
        2. **Extraction** - Les ingrÃedients sont extraits et regroupÃes
        3. **Comparaison** - VÃerification avec votre inventaire actuel
        4. **Optimisation** - Seuls les articles manquants sont listÃes
        5. **Organisation** - Tri par rayon pour faciliter vos courses
        
        Cliquez sur **"GÃenÃerer la liste"** pour commencer.
        """)


__all__ = ["render_courses_depuis_planning"]
