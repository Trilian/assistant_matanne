"""
Gestion des photos - Onglet photos de l'inventaire.
Upload et affichage des photos des articles.
"""

import streamlit as st

from src.services.inventaire import get_inventaire_service


def render_photos():
    """Gestion des photos pour les articles de l'inventaire"""
    st.subheader("📷 Gestion des photos")
    
    # Récupère l'inventaire
    service = get_inventaire_service()
    articles_data = service.get_inventaire_complet()
    
    if not articles_data:
        st.info("Aucun article dans l'inventaire")
        return
    
    # Sélectionne un article
    col1, col2 = st.columns([3, 1])
    with col1:
        article_names = [f"{a['ingredient_nom']} ({a['quantite']} {a['unite']})" for a in articles_data]
        selected_idx = st.selectbox("Sélectionne un article", range(len(article_names)), format_func=lambda i: article_names[i], key="select_photo_article")
        selected_article = articles_data[selected_idx]
        article_id = selected_article["id"]
    
    # Affiche la photo actuelle
    with col2:
        photo_status = "✅ Avec photo" if selected_article.get("photo_url") else "ℹ️ Pas de photo"
        st.info(f"État: {photo_status}")
    
    # Onglets upload/gestion
    tab_upload, tab_view = st.tabs(["📤 Ajouter/Remplacer", "👁️ Afficher"])
    
    with tab_upload:
        st.write("**Ajouter ou remplacer la photo**")
        
        # Upload image
        uploaded_file = st.file_uploader(
            "Sélectionne une image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Format: JPG, PNG, ou WebP. Max 5 MB"
        )
        
        if uploaded_file:
            # Affiche un aperçu
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(uploaded_file, width=150, caption="Aperçu")
            
            with col2:
                st.write(f"**Fichier:** {uploaded_file.name}")
                st.write(f"**Taille:** {uploaded_file.size / 1024:.1f} KB")
                
                # Simule l'upload (dans une vraie app, on sauvegarderait le fichier)
                if st.button("✨ Confirmer l'upload", key="confirm_photo_upload"):
                    try:
                        # Pour le prototype, on utilise une URL Streamlit
                        photo_url = f"streamlit_uploaded://{uploaded_file.name}"
                        
                        result = service.ajouter_photo(
                            article_id=article_id,
                            photo_url=photo_url,
                            photo_filename=uploaded_file.name,
                        )
                        
                        st.success("✨ Photo ajoutée avec succès!")
                        st.toast("Photo mise à jour", icon="📷")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
        
        # Bouton supprimer
        if selected_article.get("photo_url"):
            st.divider()
            if st.button("🗑️ Supprimer la photo", key="delete_photo"):
                try:
                    service.supprimer_photo(article_id)
                    st.success("✨ Photo supprimée")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
    
    with tab_view:
        st.write(f"**Photo de {selected_article['ingredient_nom']}**")
        
        if selected_article.get("photo_url"):
            # Affiche la photo
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Essaie d'afficher l'image
                try:
                    st.image(
                        selected_article["photo_url"],
                        caption=selected_article.get("photo_filename", "Photo"),
                        use_column_width=True
                    )
                except:
                    st.warning("Impossible d'afficher la photo")
            
            with col2:
                # Info
                st.metric("Fichier", selected_article.get("photo_filename", "N/A"))
                if selected_article.get("photo_uploaded_at"):
                    st.caption(f"Uploadée: {selected_article['photo_uploaded_at']}")
        else:
            st.info("Pas de photo pour cet article")
            st.write("Ajoute une photo dans l'onglet 'Ajouter/Remplacer'")


__all__ = ["render_photos"]
