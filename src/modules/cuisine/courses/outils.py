"""
Outils utilitaires pour les courses.
"""

from ._common import (
    datetime,
    get_courses_service,
    obtenir_contexte_db,
    pd,
    st,
)


def render_outils():
    """Outils utilitaires - Phase 2: Code-barres, partage, UX améliorée"""
    st.subheader("ðŸ“§ Outils")

    # PHASE 2 FEATURES
    tab_barcode, tab_share, tab_export, tab_stats = st.tabs(
        ["ðŸ“± Code-barres (PHASE 2)", "ðŸ‘¥ Partage (PHASE 2)", "ðŸ’¾ Export/Import", "ðŸ“Š Stats"]
    )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # PHASE 2: CODE-BARRES SCANNING
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    with tab_barcode:
        st.write("**ðŸ“± Scanner code-barres pour saisie rapide**")
        st.info("â³ Phase 2 - En développement")

        # Simuler la structure Phase 2
        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **Fonctionnalités planifiées:**
            - ðŸ“± Scan code-barres avec webcam
            - ðŸ” Reconnaissance automatique article
            - âš¡ Saisie 10x plus rapide
            - ðŸ“Š Base de codes-barres articles
            """)
        with col2:
            st.write("""
            **Intégration:**
            - Ajout rapide en magasin
            - Sync prix automatique
            - Recommandations marque
            - Export liste code-barres
            """)

        st.divider()
        st.markdown("**Estimation:** 2-3 jours (composant scanning + base données)")

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # PHASE 2: PARTAGE MULTI-UTILISATEURS
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    with tab_share:
        st.write("**ðŸ‘¥ Partager liste avec famille/colocataires**")
        st.info("â³ Phase 2 - En développement")

        col1, col2 = st.columns(2)
        with col1:
            st.write("""
            **Fonctionnalités planifiées:**
            - ðŸ‘¥ Partage par email/lien
            - ðŸ“„ Sync temps réel
            - âœ… Permissions (lecture/écriture)
            - ðŸ“± Notifications mises à jour
            """)
        with col2:
            st.write("""
            **Avantages:**
            - Colocataires voient qui achète
            - Une seule liste partagée
            - Pas de doublons articles
            - Historique collaboratif
            """)

        st.divider()

        # Structure Phase 2
        st.subheader("Configuration partage (à venir)")
        shared_with = st.multiselect(
            "Partager avec:",
            ["Alice", "Bob", "Charlie"],
            disabled=True,
            help="Disponible en Phase 2",
        )

        st.markdown("**Estimation:** 3-4 jours (BD + permissions + notifications)")

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # EXPORT/IMPORT (EXISTANT)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    with tab_export:
        st.write("**Exporter/Importer listes**")

        col1, col2 = st.columns(2)
        with col1:
            service = get_courses_service()
            liste = service.get_liste_courses(achetes=False)

            if liste:
                df = pd.DataFrame(
                    [
                        {
                            "Article": a.get("ingredient_nom"),
                            "Quantité": a.get("quantite_necessaire"),
                            "Unité": a.get("unite"),
                            "Priorité": a.get("priorite"),
                            "Rayon": a.get("rayon_magasin"),
                            "Notes": a.get("notes", ""),
                        }
                        for a in liste
                    ]
                )

                csv = df.to_csv(index=False)
                st.download_button(
                    label="ðŸ“¥ Télécharger liste (CSV)",
                    data=csv,
                    file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

        with col2:
            uploaded = st.file_uploader("ðŸ“¤ Importer liste (CSV)", type=["csv"], key="import_csv")
            if uploaded:
                try:
                    import io

                    df_import = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                    st.write(f"âœ… Fichier contient {len(df_import)} articles")

                    if st.button("âœ… Confirmer import"):
                        from src.core.models import Ingredient

                        db = next(obtenir_contexte_db())
                        service = get_courses_service()

                        count = 0
                        for _, row in df_import.iterrows():
                            ingredient = (
                                db.query(Ingredient)
                                .filter(Ingredient.nom == row["Article"])
                                .first()
                            )

                            if not ingredient:
                                ingredient = Ingredient(
                                    nom=row["Article"], unite=row.get("Unité", "pièce")
                                )
                                db.add(ingredient)
                                db.commit()

                            service.create(
                                {
                                    "ingredient_id": ingredient.id,
                                    "quantite_necessaire": float(row["Quantité"]),
                                    "priorite": row.get("Priorité", "moyenne"),
                                    "rayon_magasin": row.get("Rayon", "Autre"),
                                    "notes": row.get("Notes"),
                                }
                            )
                            count += 1

                        st.success(f"âœ… {count} articles importés!")
                        st.session_state.courses_refresh += 1
                        st.rerun()
                except Exception as e:
                    st.error(f"âŒ Erreur import: {str(e)}")

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # STATISTIQUES GLOBALES (EXISTANT + PHASE 2)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    with tab_stats:
        st.write("**ðŸ“Š Statistiques globales**")

        try:
            service = get_courses_service()

            # Stats existantes
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                liste = service.get_liste_courses(achetes=False)
                st.metric("ðŸ“‹ Articles actifs", len(liste))
            with col2:
                liste_achetee = service.get_liste_courses(achetes=True)
                st.metric("âœ… Articles achetés", len(liste_achetee))
            with col3:
                rayons = set(a.get("rayon_magasin") for a in liste if a.get("rayon_magasin"))
                st.metric("ðŸª‘ Rayons utilisés", len(rayons))
            with col4:
                st.metric("â²ï¸ Dernière mise à jour", datetime.now().strftime("%H:%M"))

            st.divider()

            # Stats par priorité
            col1, col2, col3 = st.columns(3)
            with col1:
                haute = len([a for a in liste if a.get("priorite") == "haute"])
                st.metric("ðŸ”´ Haute", haute)
            with col2:
                moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])
                st.metric("ðŸŸ¡ Moyenne", moyenne)
            with col3:
                basse = len([a for a in liste if a.get("priorite") == "basse"])
                st.metric("ðŸŸ¢ Basse", basse)

            st.divider()

            # Phase 2: Budgeting
            st.subheader("ðŸ’° Budget tracking (PHASE 2)")

        except Exception as e:
            st.error(f"âŒ Erreur chargement stats: {str(e)}")


__all__ = ["render_outils"]
