"""
Historique des courses.
"""

from ._common import (
    PRIORITY_EMOJIS,
    datetime,
    get_courses_service,
    logger,
    obtenir_contexte_db,
    pd,
    st,
    timedelta,
)


def render_historique():
    """Historique des listes de courses"""
    _service = get_courses_service()

    st.subheader("📋 Historique des courses")

    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Du", value=datetime.now() - timedelta(days=30))
    with col2:
        date_fin = st.date_input("Au", value=datetime.now())

    try:
        # Récupérer les articles achetés dans la période
        from sqlalchemy.orm import joinedload

        from src.core.models import ArticleCourses

        with obtenir_contexte_db() as db:
            articles_achetes = (
                db.query(ArticleCourses)
                .options(joinedload(ArticleCourses.ingredient))
                .filter(
                    ArticleCourses.achete == True,
                    ArticleCourses.achete_le >= datetime.combine(date_debut, datetime.min.time()),
                    ArticleCourses.achete_le <= datetime.combine(date_fin, datetime.max.time()),
                )
                .all()
            )

        if not articles_achetes:
            st.info("Aucun achat pendant cette période")
            return

        # Statistiques
        total_articles = len(articles_achetes)
        rayons_utilises = set(a.rayon_magasin for a in articles_achetes if a.rayon_magasin)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Articles achetés", total_articles)
        with col2:
            st.metric("🍪‘ Rayons différents", len(rayons_utilises))
        with col3:
            priorite_haute = len([a for a in articles_achetes if a.priorite == "haute"])
            st.metric("🔴 Haute priorité", priorite_haute)

        st.divider()

        # Tableau détaillé
        st.subheader("📋 Détail des achats")

        df = pd.DataFrame(
            [
                {
                    "Article": a.ingredient.nom if a.ingredient else "N/A",
                    "Quantité": f"{a.quantite_necessaire} {a.ingredient.unite if a.ingredient else ''}",
                    "Priorité": PRIORITY_EMOJIS.get(a.priorite, "âš«") + " " + a.priorite,
                    "Rayon": a.rayon_magasin or "N/A",
                    "Acheté le": a.achete_le.strftime("%d/%m/%Y %H:%M") if a.achete_le else "N/A",
                    "IA": "⏰" if a.suggere_par_ia else "",
                }
                for a in articles_achetes
            ]
        )

        st.dataframe(df, width="stretch")

        # Export CSV - directement, sans button wrapper
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


__all__ = ["render_historique"]
