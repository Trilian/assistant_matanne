"""
Historique des courses et modèles récurrents.

Fusionne les anciens historique.py et modeles.py.
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.courses import obtenir_service_courses
from src.ui.components.atoms import etat_vide
from src.ui.fragments import ui_fragment

from .utils import PRIORITY_EMOJIS, get_current_user_id

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_historique_et_modeles():
    """Point d'entrée — 2 sous-onglets Historique & Modèles."""
    st.subheader("📊 Historique & Modèles")

    tab_historique, tab_modeles = st.tabs(["📋 Historique", "📄 Modèles récurrents"])

    with tab_historique:
        _afficher_historique()

    with tab_modeles:
        _afficher_modeles()


# ═══════════════════════════════════════════════════════════
# HISTORIQUE
# ═══════════════════════════════════════════════════════════


def _afficher_historique():
    """Historique des listes de courses."""
    service = obtenir_service_courses()

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=datetime.now() - timedelta(days=30))
    with col2:
        date_fin = st.date_input("Au", value=datetime.now())

    try:
        articles_achetes = service.obtenir_historique_achats(
            date_debut=date_debut,
            date_fin=date_fin,
        )

        if not articles_achetes:
            etat_vide("Aucun achat pendant cette période", "🛒")
            return

        total_articles = len(articles_achetes)
        rayons_utilises = set(
            a["rayon_magasin"] for a in articles_achetes if a.get("rayon_magasin")
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Articles achetés", total_articles)
        with col2:
            st.metric("🏪 Rayons différents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.get("priorite") == "haute"])
            st.metric("🔴 Haute priorité", priorite_haute)

        st.divider()
        st.subheader("📋 Détail des achats")

        df = pd.DataFrame(
            [
                {
                    "Article": a.get("ingredient_nom", "N/A"),
                    "Quantité": f"{a.get('quantite_necessaire', '')} {a.get('unite', '')}",
                    "Priorité": PRIORITY_EMOJIS.get(a.get("priorite", ""), "⚫")
                    + " "
                    + a.get("priorite", ""),
                    "Rayon": a.get("rayon_magasin") or "N/A",
                    "Acheté le": a["achete_le"].strftime("%d/%m/%Y %H:%M")
                    if a.get("achete_le")
                    else "N/A",
                    "IA": "⏰" if a.get("suggere_par_ia") else "",
                }
                for a in articles_achetes
            ]
        )

        st.dataframe(df, use_container_width=True)

        if df is not None and not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name=f"historique_courses_{date_debut}_{date_fin}.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur historique: {e}")


# ═══════════════════════════════════════════════════════════
# MODÈLES RÉCURRENTS
# ═══════════════════════════════════════════════════════════


def _afficher_modeles():
    """Gestion des modèles de listes récurrentes."""
    service = obtenir_service_courses()

    try:
        modeles = service.get_modeles(utilisateur_id=get_current_user_id())

        tab_mes_modeles, tab_nouveau = st.tabs(["📋 Mes modèles", "➕ Nouveau"])

        with tab_mes_modeles:
            _afficher_mes_modeles(service, modeles)

        with tab_nouveau:
            _afficher_creer_modele(service)

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur afficher_modeles: {e}")


def _afficher_mes_modeles(service, modeles):
    """Affiche les modèles sauvegardés."""
    if not modeles:
        etat_vide("Aucun modèle sauvegardé", "📝", "Créez-en un dans l'onglet 'Nouveau'")
        return

    for modele in modeles:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"**📋 {modele['nom']}**")
                if modele.get("description"):
                    st.caption(f"📝 {modele['description']}")
                st.caption(
                    f"📦 {len(modele.get('articles', []))} articles "
                    f"| 📅 {modele.get('cree_le', '')[:10]}"
                )

            with col2:
                if st.button(
                    "📥 Charger",
                    key=f"modele_load_{modele['id']}",
                    use_container_width=True,
                    help="Charger ce modèle dans la liste",
                ):
                    try:
                        article_ids = service.appliquer_modele(modele["id"])
                        if not article_ids:
                            st.warning("⚠️ Modèle chargé mais aucun article trouvé")
                        else:
                            st.success(f"✅ Modèle chargé ({len(article_ids)} articles)!")
                            st.session_state[SK.COURSES_REFRESH] += 1
                            rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")

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

            with st.expander(f"👁️ Voir {len(modele.get('articles', []))} articles"):
                for article in modele.get("articles", []):
                    priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "⚫")
                    st.write(
                        f"{priorite_emoji} **{article['nom']}** — "
                        f"{article['quantite']} {article['unite']} ({article['rayon']})"
                    )
                    if article.get("notes"):
                        st.caption(f"📜 {article['notes']}")


def _afficher_creer_modele(service):
    """Créer un nouveau modèle depuis la liste actuelle."""
    st.write("**Sauvegarder la liste actuelle comme modèle réutilisable**")

    liste_actuelle = service.get_liste_courses(achetes=False)

    if not liste_actuelle:
        st.warning("⚠️ La liste est vide. Ajoutez des articles d'abord!")
        return

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

    st.subheader(f"📦 Articles ({len(liste_actuelle)})")
    for i, article in enumerate(liste_actuelle):
        priorite_emoji = PRIORITY_EMOJIS.get(article.get("priorite", "moyenne"), "⚫")
        st.write(
            f"{i + 1}. {priorite_emoji} **{article['ingredient_nom']}** — "
            f"{article['quantite_necessaire']} {article['unite']} ({article['rayon_magasin']})"
        )

    st.divider()

    if st.button("💾 Sauvegarder comme modèle", use_container_width=True, type="primary"):
        if not nom_modele or nom_modele.strip() == "":
            st.error("⚠️ Entrez un nom pour le modèle")
        else:
            try:
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

                service.create_modele(
                    nom=nom_modele.strip(),
                    articles=articles_data,
                    description=description.strip() if description else None,
                    utilisateur_id=get_current_user_id(),
                )

                st.success(f"✅ Modèle '{nom_modele}' créé et sauvegardé!")
                st.balloons()
                rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de la sauvegarde: {str(e)}")
                logger.error(f"Erreur create_modele: {e}")


# Compatibilité ancienne API
afficher_historique = afficher_historique_et_modeles

__all__ = ["afficher_historique_et_modeles", "afficher_historique"]
