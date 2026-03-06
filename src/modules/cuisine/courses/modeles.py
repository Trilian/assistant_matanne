"""
Gestion des modèles de listes récurrentes.
"""

import logging

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.courses import obtenir_service_courses
from src.ui.components.atoms import etat_vide
from src.ui.fragments import ui_fragment

from .utils import get_current_user_id

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_modeles():
    """Gestion des modèles de listes récurrentes."""
    st.subheader("📄 Modèles de listes")

    service = obtenir_service_courses()

    try:
        # Récupérer modèles depuis BD
        modeles = service.get_modeles(utilisateur_id=get_current_user_id())

        tab_mes_modeles, tab_nouveau = st.tabs(["📋 Mes modèles", "➕ Nouveau"])

        # ─────────────────────────────────────────────────────────────────────────────
        # ONGLET: MES MODÈLES (affichage et actions)
        # ─────────────────────────────────────────────────────────────────────────────

        with tab_mes_modeles:
            st.write("**Modèles sauvegardés en BD**")

            if not modeles:
                etat_vide("Aucun modèle sauvegardé", "📝", "Créez-en un dans l'onglet 'Nouveau'")
            else:
                for modele in modeles:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 1, 1])

                        with col1:
                            st.write(f"**📋 {modele['nom']}**")
                            if modele.get("description"):
                                st.caption(f"📝 {modele['description']}")
                            st.caption(
                                f"📦 {len(modele.get('articles', []))} articles | 📅 {modele.get('cree_le', '')[:10]}"
                            )

                        with col2:
                            if st.button(
                                "📥 Charger",
                                key=f"modele_load_{modele['id']}",
                                use_container_width=True,
                                help="Charger ce modèle dans la liste",
                            ):
                                try:
                                    # Appliquer le modèle (crée articles courses)
                                    article_ids = service.appliquer_modele(modele["id"])
                                    if not article_ids:
                                        st.warning("⚠️ Modèle chargé mais aucun article trouvé")
                                    else:
                                        st.success(
                                            f"✅ Modèle chargé ({len(article_ids)} articles)!"
                                        )
                                        st.session_state[SK.COURSES_REFRESH] += 1
                                        rerun()
                                except Exception as e:
                                    import traceback

                                    st.error(f"❌ Erreur: {str(e)}")
                                    with st.expander("📋 Détails d'erreur"):
                                        st.code(traceback.format_exc())

                        with col3:
                            if st.button(
                                "🗑️ Supprimer",
                                key=f"modele_del_{modele['id']}",
                                use_container_width=True,
                                help="Supprimer ce modèle",
                            ):
                                try:
                                    service.delete_modele(modele["id"])
                                    st.success("✅ Modèle supprimé!")
                                    rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")

                        # Afficher les articles du modèle
                        with st.expander(f"👁️ Voir {len(modele.get('articles', []))} articles"):
                            for article in modele.get("articles", []):
                                priorite_emoji = (
                                    "🔴"
                                    if article["priorite"] == "haute"
                                    else ("🟡" if article["priorite"] == "moyenne" else "🟢")
                                )
                                st.write(
                                    f"{priorite_emoji} **{article['nom']}** - {article['quantite']} {article['unite']} ({article['rayon']})"
                                )
                                if article.get("notes"):
                                    st.caption(f"📜 {article['notes']}")

        # ─────────────────────────────────────────────────────────────────────────────
        # ONGLET: CRÉER NOUVEAU MODÈLE
        # ─────────────────────────────────────────────────────────────────────────────

        with tab_nouveau:
            st.write("**Sauvegarder la liste actuelle comme modèle réutilisable**")

            # Récupérer liste actuelle
            liste_actuelle = service.get_liste_courses(achetes=False)

            if not liste_actuelle:
                st.warning("⚠️ La liste est vide. Ajoutez des articles d'abord!")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    nom_modele = st.text_input(
                        "Nom du modèle",
                        placeholder="ex: Courses hebdomadaires",
                        max_chars=100,
                        key="new_modele_name",
                    )

                with col2:
                    description = st.text_area(
                        "Description (optionnel)",
                        placeholder="ex: Courses standard pour 4 personnes",
                        max_chars=500,
                        height=50,
                        key="new_modele_desc",
                    )

                st.divider()

                # Aperçu des articles à sauvegarder
                st.subheader(f"📦 Articles ({len(liste_actuelle)})")
                for i, article in enumerate(liste_actuelle):
                    priorite_emoji = (
                        "🔴"
                        if article["priorite"] == "haute"
                        else ("🟡" if article["priorite"] == "moyenne" else "🟢")
                    )
                    st.write(
                        f"{i + 1}. {priorite_emoji} **{article['ingredient_nom']}** - {article['quantite_necessaire']} {article['unite']} ({article['rayon_magasin']})"
                    )

                st.divider()

                if st.button(
                    "💾 Sauvegarder comme modèle", use_container_width=True, type="primary"
                ):
                    if not nom_modele or nom_modele.strip() == "":
                        st.error("⚠️ Entrez un nom pour le modèle")
                    else:
                        try:
                            # Préparer les données articles
                            articles_data = [
                                {
                                    "ingredient_id": a.get("ingredient_id"),
                                    "nom": a.get("ingredient_nom"),
                                    "quantite": float(a.get("quantite_necessaire", 1.0)),
                                    "unite": a.get("unite", "pièce"),
                                    "rayon": a.get("rayon_magasin", "Autre"),
                                    "priorite": a.get("priorite", "moyenne"),
                                    "notes": a.get("notes"),
                                }
                                for a in liste_actuelle
                            ]

                            # Sauvegarder en BD (Phase 2)
                            service.create_modele(
                                nom=nom_modele.strip(),
                                articles=articles_data,
                                description=description.strip() if description else None,
                                utilisateur_id=get_current_user_id(),
                            )

                            st.success(f"✅ Modèle '{nom_modele}' créé et sauvegardé en BD!")
                            st.balloons()
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
                            logger.error(f"Erreur create_modele: {e}")

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur afficher_modeles: {e}")


__all__ = ["afficher_modeles"]
