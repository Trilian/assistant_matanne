"""
Outils d'administration - Onglet outils de l'inventaire.
Import/Export et statistiques globales.
"""

import streamlit as st
import pandas as pd

from src.services.inventaire import get_inventaire_service


def render_tools():
    """Outils utilitaires pour l'inventaire"""
    st.subheader("ðŸ”§ Outils d'administration")
    
    tab_import_export, tab_stats = st.tabs(["ðŸ“¤ Import/Export", "ðŸ“Š Statistiques"])
    
    with tab_import_export:
        render_import_export()
    
    with tab_stats:
        service = get_inventaire_service()
        if service:
            try:
                inventaire = service.get_inventaire_complet()
                alertes = service.get_alertes()
                
                st.subheader("ðŸ“Š Statistiques globales")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total articles", len(inventaire))
                with col2:
                    emplacements = len(set(a["emplacement"] for a in inventaire if a["emplacement"]))
                    st.metric("Emplacements", emplacements)
                with col3:
                    categories = len(set(a["ingredient_categorie"] for a in inventaire))
                    st.metric("CatÃegories", categories)
                with col4:
                    total_alertes = sum(len(v) for v in alertes.values())
                    st.metric("Alertes actives", total_alertes)
                
                st.divider()
                
                # Graphiques
                st.subheader("ðŸ“Š RÃepartition")
                
                col_graph1, col_graph2 = st.columns(2)
                
                with col_graph1:
                    st.write("**Statuts**")
                    statuts = {}
                    for article in inventaire:
                        s = article["statut"]
                        statuts[s] = statuts.get(s, 0) + 1
                    st.bar_chart(statuts)
                
                with col_graph2:
                    st.write("**CatÃegories**")
                    cats = {}
                    for article in inventaire:
                        c = article["ingredient_categorie"]
                        cats[c] = cats.get(c, 0) + 1
                    st.bar_chart(cats)
            
            except Exception as e:
                st.error(f"âŒ Erreur: {str(e)}")


def render_import_export():
    """Gestion import/export avancÃee"""
    service = get_inventaire_service()
    
    st.subheader("ðŸ“¤ Import/Export AvancÃe")
    
    tab_import, tab_export = st.tabs(["ðŸ“¥ Importer", "ðŸ“¤ Exporter"])
    
    with tab_import:
        st.write("**Importer articles depuis fichier**")
        
        # Uploader fichier
        uploaded_file = st.file_uploader(
            "SÃelectionne un fichier CSV ou Excel",
            type=["csv", "xlsx", "xls"],
            help="Format: Nom, QuantitÃe, UnitÃe, Seuil Min, Emplacement, CatÃegorie, Date PÃeremption"
        )
        
        if uploaded_file:
            try:
                # Parse le fichier
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write(f"**Fichier parsÃe:** {len(df)} lignes")
                
                # Affiche un aperçu
                st.dataframe(df.head(5), width='stretch')
                
                # Valide les donnÃees
                if st.button("âœ¨ Valider & Importer", type="primary", width='stretch'):
                    try:
                        # Convertit en format attendu
                        articles_list = df.to_dict("records")
                        
                        # Renomme colonnes si besoin
                        articles_list = [
                            {
                                "nom": row.get("Nom") or row.get("nom"),
                                "quantite": float(row.get("QuantitÃe") or row.get("quantite") or 0),
                                "quantite_min": float(row.get("Seuil Min") or row.get("quantite_min") or 1),
                                "unite": row.get("UnitÃe") or row.get("unite") or "pièce",
                                "emplacement": row.get("Emplacement") or row.get("emplacement"),
                                "categorie": row.get("CatÃegorie") or row.get("categorie"),
                                "date_peremption": row.get("Date PÃeremption") or row.get("date_peremption"),
                            }
                            for row in articles_list
                        ]
                        
                        # Valide
                        rapport = service.valider_fichier_import(articles_list)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("âœ¨ Valides", rapport["valides"])
                        with col2:
                            st.metric("âŒ Invalides", rapport["invalides"])
                        with col3:
                            if rapport["valides"] > 0:
                                pct = (rapport["valides"] / (rapport["valides"] + rapport["invalides"]) * 100) if (rapport["valides"] + rapport["invalides"]) > 0 else 0
                                st.metric("% OK", f"{pct:.0f}%")
                        
                        # Affiche les erreurs
                        if rapport["erreurs"]:
                            st.error("**Erreurs de validation:**")
                            for err in rapport["erreurs"][:5]:
                                st.caption(f"Ligne {err['ligne']}: {err['erreur']}")
                            if len(rapport["erreurs"]) > 5:
                                st.caption(f"... et {len(rapport['erreurs']) - 5} autres")
                        
                        # Confirme et importe
                        if rapport["valides"] > 0:
                            if st.button("ðŸš€ Importer les articles valides", width='stretch'):
                                resultats = service.importer_articles(articles_list)
                                
                                # Affiche rÃesultats
                                success = [r for r in resultats if r["status"] == "âœ¨"]
                                errors = [r for r in resultats if r["status"] == "âŒ"]
                                
                                st.success(f"âœ¨ {len(success)}/{len(resultats)} articles importÃes!")
                                st.toast(f"Import complÃetÃe: {len(success)} rÃeussis", icon="âœ¨")
                                
                                if errors:
                                    st.warning(f"âš ï¸ {len(errors)} articles avec erreurs")
                                    for err in errors[:3]:
                                        st.caption(f"â€¢ {err['nom']}: {err['message']}")
                    
                    except Exception as e:
                        st.error(f"âŒ Erreur import: {str(e)}")
            
            except Exception as e:
                st.error(f"âŒ Erreur parsing fichier: {str(e)}")
    
    with tab_export:
        st.write("**Exporter l'inventaire**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("ðŸ“¥ TÃelÃecharger CSV", width='stretch'):
                try:
                    csv_content = service.exporter_inventaire("csv")
                    st.download_button(
                        label="ðŸŽ¯ TÃelÃecharger CSV",
                        data=csv_content,
                        file_name="inventaire.csv",
                        mime="text/csv",
                    )
                    st.success("âœ¨ CSV prêt Ã  tÃelÃecharger")
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        with col2:
            if st.button("ðŸ“¥ TÃelÃecharger JSON", width='stretch'):
                try:
                    json_content = service.exporter_inventaire("json")
                    st.download_button(
                        label="ðŸŽ¯ TÃelÃecharger JSON",
                        data=json_content,
                        file_name="inventaire.json",
                        mime="application/json",
                    )
                    st.success("âœ¨ JSON prêt Ã  tÃelÃecharger")
                except Exception as e:
                    st.error(f"âŒ Erreur: {str(e)}")
        
        st.divider()
        
        # Info export
        articles = service.get_inventaire_complet()
        st.info(
            f"ðŸ“Š **Statistiques export:**\n"
            f"â€¢ **Articles:** {len(articles)}\n"
            f"â€¢ **Stock total:** {sum(a['quantite'] for a in articles)}\n"
            f"â€¢ **Date export:** Automatique"
        )


__all__ = ["render_tools", "render_import_export"]
