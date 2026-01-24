"""
Module Shopping Famille - Achats centralisés (Jules, Nous, Maison)
"""

from datetime import date

import pandas as pd
import streamlit as st

from src.core.database import get_db_context
from src.core.models import ArticleCourses


# ===================================
# HELPERS
# ===================================


def charger_articles_shopping(categorie: str = None) -> pd.DataFrame:
    """Charge les articles du shopping"""
    with get_db_context() as db:
        query = db.query(ArticleCourses).filter(ArticleCourses.priorite == "shopping")

        if categorie:
            query = query.filter(ArticleCourses.categorie == categorie)

        articles = query.order_by(ArticleCourses.cree_le.desc()).all()

        return pd.DataFrame(
            [
                {
                    "id": a.id,
                    "article": a.nom,
                    "categorie": a.categorie or "Autre",
                    "quantite": a.quantite,
                    "unite": a.unite or "",
                    "notes": a.notes or "",
                    "prix_estime": a.prix or 0,
                }
                for a in articles
            ]
        )


def ajouter_au_shopping(article: str, categorie: str, quantite: int = 1, notes: str = None, prix_estime: float = None):
    """Ajoute un article au shopping"""
    with get_db_context() as db:
        existing = db.query(ArticleCourses).filter(
            ArticleCourses.nom == article,
            ArticleCourses.categorie == categorie,
            ArticleCourses.priorite == "shopping"
        ).first()

        if existing:
            existing.quantite += quantite
        else:
            article_obj = ArticleCourses(
                nom=article,
                categorie=categorie,
                quantite=quantite,
                unite="",
                notes=notes,
                prix=prix_estime,
                priorite="shopping",
                achete=False,
            )
            db.add(article_obj)

        db.commit()


def marquer_achet(article_id: int):
    """Marque un article comme acheté"""
    with get_db_context() as db:
        article = db.query(ArticleCourses).filter(ArticleCourses.id == article_id).first()
        if article:
            article.achete = True
            db.commit()


def supprimer_article(article_id: int):
    """Supprime un article"""
    with get_db_context() as db:
        article = db.query(ArticleCourses).filter(ArticleCourses.id == article_id).first()
        if article:
            db.delete(article)
            db.commit()


# Suggestions d'achats par catégorie
SUGGESTIONS_SHOPPING = {
    "Jules - Jouets": [
        {"article": "Blocs/Duplo", "prix": 30},
        {"article": "Balles molles", "prix": 15},
        {"article": "Livres tactiles", "prix": 12},
        {"article": "Instruments musique", "prix": 20},
        {"article": "Jeux d'eau", "prix": 10},
        {"article": "Téléphone jouet", "prix": 15},
    ],
    "Jules - Vêtements": [
        {"article": "T-shirts (taille 86-92)", "prix": 25},
        {"article": "Pantalons (taille 86-92)", "prix": 35},
        {"article": "Chaussures (pointure 24-26)", "prix": 45},
        {"article": "Pulls/cardigans", "prix": 30},
        {"article": "Pyjamas", "prix": 25},
        {"article": "Chaussettes", "prix": 10},
    ],
    "Jules - Couches/Hygiène": [
        {"article": "Couches (taille 4)", "prix": 40},
        {"article": "Lingettes bébé", "prix": 8},
        {"article": "Savon bébé", "prix": 6},
        {"article": "Crème change", "prix": 8},
    ],
    "Nous - Sport": [
        {"article": "Tapis de yoga", "prix": 30},
        {"article": "Bandes élastiques", "prix": 15},
        {"article": "Gourde réutilisable", "prix": 20},
        {"article": "Chaussures de sport", "prix": 80},
        {"article": "Vêtements sport", "prix": 50},
    ],
    "Nous - Nutrition": [
        {"article": "Blender/mixer", "prix": 50},
        {"article": "Pèse-aliments", "prix": 15},
        {"article": "Bouteilles eau", "prix": 25},
        {"article": "Boîtes conservation", "prix": 20},
    ],
    "Maison": [
        {"article": "Produits nettoyage", "prix": 20},
        {"article": "Sacs poubelle", "prix": 10},
        {"article": "Papier toilette", "prix": 15},
        {"article": "Savon mains", "prix": 8},
        {"article": "Ampoules LED", "prix": 15},
    ],
}


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Module Shopping - Achats centralisés"""

    st.title("🛍️ Shopping Famille")
    st.caption("Achats centralisés pour Jules, Nous et la Maison")

    st.markdown("---")

    # ===================================
    # TABS
    # ===================================

    tab1, tab2, tab3 = st.tabs(
        ["📋 Liste de shopping", "💡 Idées d'achats", "📊 Suivi budget"]
    )

    # ===================================
    # TAB 1 : LISTE
    # ===================================

    with tab1:
        st.subheader("📋 Votre liste de shopping")

        st.info("💡 Ajoute des articles et cochez-les quand tu les as achetés")

        # Ajouter article manuel
        with st.expander("➕ Ajouter un article", expanded=False):
            col_add1, col_add2 = st.columns(2)

            with col_add1:
                article = st.text_input("Article *", placeholder="Ex: Blocs Duplo")

                categorie = st.selectbox(
                    "Catégorie *",
                    [
                        "Jules - Jouets",
                        "Jules - Vêtements",
                        "Jules - Couches/Hygiène",
                        "Nous - Sport",
                        "Nous - Nutrition",
                        "Maison",
                        "Autre",
                    ],
                )

            with col_add2:
                quantite = st.number_input("Quantité", 1, 100, 1)

                prix_estime = st.number_input("Prix estimé (€)", 0.0, 1000.0, 0.0)

            notes = st.text_area("Notes (optionnel)", placeholder="Marque, couleur, etc.", height=50)

            if st.button("➕ Ajouter à la liste", type="primary", use_container_width=True):
                if not article or not categorie:
                    st.error("Article et catégorie obligatoires")
                else:
                    ajouter_au_shopping(
                        article,
                        categorie,
                        quantite,
                        notes or None,
                        prix_estime if prix_estime > 0 else None,
                    )
                    st.success(f"✅ '{article}' ajouté!")
                    st.rerun()

        st.markdown("---")

        # Afficher liste par catégorie
        df_shopping = charger_articles_shopping()

        if df_shopping.empty:
            st.info("Aucun article. Ajoute-en un! 🛒")
        else:
            # Statistiques
            col_stat1, col_stat2, col_stat3 = st.columns(3)

            with col_stat1:
                st.metric("Articles", len(df_shopping))

            with col_stat2:
                total_prix = df_shopping["prix_estime"].sum()
                st.metric("Budget estimé", f"{total_prix:.0f}€")

            with col_stat3:
                achetes = len(df_shopping[df_shopping["achet"] == True]) if "achet" in df_shopping.columns else 0
                st.metric("Achetés", achetes)

            st.markdown("---")

            # Par catégorie
            for categorie in sorted(df_shopping["categorie"].unique()):
                df_cat = df_shopping[df_shopping["categorie"] == categorie]

                with st.expander(f"**{categorie}** ({len(df_cat)} articles)", expanded=True):
                    for _, row in df_cat.iterrows():
                        col_shop1, col_shop2, col_shop3 = st.columns([2, 1, 1])

                        with col_shop1:
                            st.write(f"• {row['article']}")
                            if row["notes"]:
                                st.caption(f"📝 {row['notes']}")

                        with col_shop2:
                            info_prix = ""
                            if row["prix_estime"] > 0:
                                info_prix = f"~{row['prix_estime']:.0f}€"

                            if row["quantite"] > 1:
                                st.caption(f"x{row['quantite']} {info_prix}")
                            else:
                                st.caption(info_prix if info_prix else "")

                        with col_shop3:
                            if st.button(
                                "✅ Acheté",
                                key=f"done_{row['id']}",
                                use_container_width=True,
                            ):
                                marquer_achet(row["id"])
                                st.success("Marqué comme acheté! ✨")
                                st.rerun()

    # ===================================
    # TAB 2 : IDÉES
    # ===================================

    with tab2:
        st.subheader("💡 Idées d'achats suggérées")

        st.info("💡 Clique sur une idée pour l'ajouter à ta liste")

        # Afficher suggestions par catégorie
        for categorie, articles in SUGGESTIONS_SHOPPING.items():
            with st.expander(f"📦 {categorie}", expanded=False):
                col_idea1, col_idea2 = st.columns(2)

                for idx, suggestion in enumerate(articles):
                    with (col_idea1 if idx % 2 == 0 else col_idea2):
                        col_sug1, col_sug2 = st.columns([2, 1])

                        with col_sug1:
                            st.write(f"• {suggestion['article']}")

                        with col_sug2:
                            st.caption(f"~{suggestion['prix']}€")

                        if st.button(
                            "➕ Ajouter",
                            key=f"add_idea_{categorie}_{suggestion['article']}",
                            use_container_width=True,
                        ):
                            ajouter_au_shopping(
                                suggestion["article"],
                                categorie,
                                1,
                                None,
                                suggestion["prix"],
                            )
                            st.success(f"✅ Ajouté!")
                            st.rerun()

    # ===================================
    # TAB 3 : BUDGET
    # ===================================

    with tab3:
        st.subheader("📊 Suivi budget shopping")

        st.info("💡 Analyse des dépenses par catégorie")

        df_shopping = charger_articles_shopping()

        if df_shopping.empty:
            st.info("Aucun article pour analyser")
        else:
            # Par catégorie
            budget_par_cat = df_shopping.groupby("categorie")["prix_estime"].sum().sort_values(
                ascending=False
            )

            # Graphique
            st.bar_chart(budget_par_cat)

            st.markdown("---")

            # Tableau résumé
            st.write("**Détail par catégorie**")

            resumé = (
                df_shopping.groupby("categorie")
                .agg(
                    Articles=("article", "count"),
                    Budget=("prix_estime", "sum"),
                )
                .sort_values("Budget", ascending=False)
            )

            st.dataframe(
                resumé,
                use_container_width=True,
            )

            st.markdown("---")

            # Stats globales
            col_global1, col_global2, col_global3 = st.columns(3)

            with col_global1:
                st.metric("Articles total", len(df_shopping))

            with col_global2:
                st.metric("Budget total", f"{df_shopping['prix_estime'].sum():.0f}€")

            with col_global3:
                # Moyenne par article
                avg_prix = df_shopping[df_shopping["prix_estime"] > 0]["prix_estime"].mean()
                st.metric("Prix moyen", f"{avg_prix:.0f}€" if avg_prix > 0 else "—")


if __name__ == "__main__":
    app()
