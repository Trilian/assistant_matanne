"""
Outils utilitaires pour les courses.
"""

from datetime import datetime

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.courses import obtenir_service_courses
from src.ui.fragments import ui_fragment


@ui_fragment
def afficher_outils():
    """Outils utilitaires - Phase 2: Code-barres, partage, UX améliorée"""
    st.subheader("🔧 Outils")

    # PHASE 2 FEATURES
    tab_barcode, tab_share, tab_export, tab_stats = st.tabs(
        ["📱 Code-barres (PHASE 2)", "👥 Partage (PHASE 2)", "💾 Export/Import", "📊 Stats"]
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 2: CODE-BARRES SCANNING
    # ─────────────────────────────────────────────────────────────────────────────

    with tab_barcode:
        st.write("**📱 Scanner code-barres pour saisie rapide**")
        st.info("⏳ Phase 2 - En développement")

        # Simuler la structure Phase 2
        col1, col2 = st.columns(2)
        with col1:
            st.write(
                """
            **Fonctionnalités planifiées:**
            - 📱 Scan code-barres avec webcam
            - 🔍 Reconnaissance automatique article
            - ⚡ Saisie 10x plus rapide
            - 📊 Base de codes-barres articles
            """
            )
        with col2:
            st.write(
                """
            **Intégration:**
            - Ajout rapide en magasin
            - Sync prix automatique
            - Recommandations marque
            - Export liste code-barres
            """
            )

        st.divider()
        st.markdown("**Estimation:** 2-3 jours (composant scanning + base données)")

    # ─────────────────────────────────────────────────────────────────────────────
    # PHASE 2: PARTAGE MULTI-UTILISATEURS
    # ─────────────────────────────────────────────────────────────────────────────

    with tab_share:
        st.write("**👥 Partager liste avec famille/colocataires**")
        st.info("⏳ Phase 2 - En développement")

        col1, col2 = st.columns(2)
        with col1:
            st.write(
                """
            **Fonctionnalités planifiées:**
            - 👥 Partage par email/lien
            - 📄 Sync temps réel
            - ✅ Permissions (lecture/écriture)
            - 📱 Notifications mises à jour
            """
            )
        with col2:
            st.write(
                """
            **Avantages:**
            - Colocataires voient qui achète
            - Une seule liste partagée
            - Pas de doublons articles
            - Historique collaboratif
            """
            )

        st.divider()

        # Structure Phase 2
        st.subheader("Configuration partage (à venir)")
        _shared_with = st.multiselect(
            "Partager avec:",
            ["Alice", "Bob", "Charlie"],
            disabled=True,
            help="Disponible en Phase 2",
        )

        st.markdown("**Estimation:** 3-4 jours (BD + permissions + notifications)")

    # ─────────────────────────────────────────────────────────────────────────────
    # EXPORT/IMPORT (EXISTANT)
    # ─────────────────────────────────────────────────────────────────────────────

    with tab_export:
        st.write("**Exporter/Importer listes**")

        col1, col2 = st.columns(2)
        with col1:
            service = obtenir_service_courses()
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
                    label="📥 Télécharger liste (CSV)",
                    data=csv,
                    file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

        with col2:
            uploaded = st.file_uploader("📤 Importer liste (CSV)", type=["csv"], key="import_csv")
            if uploaded:
                try:
                    import io

                    df_import = pd.read_csv(io.BytesIO(uploaded.getvalue()))
                    st.write(f"✅ Fichier contient {len(df_import)} articles")

                    if st.button("✅ Confirmer import"):
                        service = obtenir_service_courses()
                        count = service.importer_articles_csv(df_import.to_dict("records"))
                        st.success(f"✅ {count} articles importés!")
                        st.session_state[SK.COURSES_REFRESH] += 1
                        rerun()
                except Exception as e:
                    st.error(f"❌ Erreur import: {str(e)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # STATISTIQUES GLOBALES (EXISTANT + PHASE 2)
    # ─────────────────────────────────────────────────────────────────────────────

    with tab_stats:
        st.write("**📊 Statistiques globales**")

        try:
            service = obtenir_service_courses()

            # Stats existantes
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                liste = service.get_liste_courses(achetes=False)
                st.metric("📋 Articles actifs", len(liste))
            with col2:
                liste_achetee = service.get_liste_courses(achetes=True)
                st.metric("✅ Articles achetés", len(liste_achetee))
            with col3:
                rayons = set(a.get("rayon_magasin") for a in liste if a.get("rayon_magasin"))
                st.metric("🍪‘ Rayons utilisés", len(rayons))
            with col4:
                st.metric("â²ï¸ Dernière mise à jour", datetime.now().strftime("%H:%M"))

            st.divider()

            # Stats par priorité
            col1, col2, col3 = st.columns(3)
            with col1:
                haute = len([a for a in liste if a.get("priorite") == "haute"])
                st.metric("🔴 Haute", haute)
            with col2:
                moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])
                st.metric("🟡 Moyenne", moyenne)
            with col3:
                basse = len([a for a in liste if a.get("priorite") == "basse"])
                st.metric("🟢 Basse", basse)

            st.divider()

            # Phase 2: Budgeting
            st.subheader("💰 Budget tracking (PHASE 2)")

        except Exception as e:
            st.error(f"❌ Erreur chargement stats: {str(e)}")


__all__ = ["afficher_outils"]
