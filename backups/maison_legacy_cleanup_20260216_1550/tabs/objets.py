"""Tab Objets - Gestion des objets à remplacer."""

import streamlit as st

from src.core.database import obtenir_contexte_db


def tab_objets():
    """Affiche les objets à remplacer avec intégration courses/budget."""
    st.subheader("🔧 Objets à Remplacer")

    try:
        from src.core.models import ObjetMaison, PieceMaison

        with obtenir_contexte_db() as db:
            objets = (
                db.query(ObjetMaison, PieceMaison.nom.label("piece_nom"))
                .join(PieceMaison, ObjetMaison.piece_id == PieceMaison.id)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_acheter", "a_reparer"]))
                .order_by(
                    ObjetMaison.statut,
                    ObjetMaison.priorite_remplacement,
                )
                .all()
            )

        if not objets:
            st.success("✅ Aucun objet à remplacer actuellement")
            return

        nb_total = len(objets)
        budget_total = sum(float(o[0].prix_remplacement_estime or 0) for o in objets)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Objets à remplacer", nb_total)
        with col2:
            st.metric("Budget estimé", f"{budget_total:,.0f}€")

        st.markdown("---")

        for objet, piece_nom in objets:
            statut_icon = {
                "a_changer": "🔴",
                "a_acheter": "🟠",
                "a_reparer": "🟡",
            }.get(objet.statut, "⚪")

            priorite_badge = {
                "urgente": ("🔥 Urgent", "#e74c3c"),
                "haute": ("⚡ Haute", "#e67e22"),
                "normale": ("📋 Normale", "#3498db"),
                "basse": ("📦 Basse", "#95a5a6"),
            }.get(objet.priorite_remplacement or "normale", ("📋", "#95a5a6"))

            prix = (
                f"{objet.prix_remplacement_estime:,.0f}€" if objet.prix_remplacement_estime else "-"
            )

            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

                with col1:
                    st.markdown(f"**{statut_icon} {objet.nom}**")
                    st.caption(f"📍 {piece_nom}")

                with col2:
                    st.markdown(
                        f"""<span style="
                            background: {priorite_badge[1]};
                            color: white;
                            padding: 4px 10px;
                            border-radius: 12px;
                            font-size: 0.8rem;
                        ">{priorite_badge[0]}</span>""",
                        unsafe_allow_html=True,
                    )

                with col3:
                    st.markdown(f"💰 {prix}")

                with col4:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("🛒", key=f"courses_{objet.id}", help="Ajouter aux courses"):
                            _ajouter_aux_courses(objet)
                    with col_b:
                        if st.button("📊", key=f"budget_{objet.id}", help="Ajouter au budget"):
                            _ajouter_au_budget(objet)

                st.markdown("---")

    except Exception as e:
        st.error(f"Erreur chargement objets: {e}")


def _ajouter_aux_courses(objet):
    """Ajoute un objet à la liste de courses."""
    try:
        from src.core.models import ArticleCourses

        with obtenir_contexte_db() as db:
            article = ArticleCourses(
                nom=objet.nom,
                categorie="Maison",
                quantite=1,
                unite="pièce",
                notes=f"Remplacement - {objet.marque or ''} {objet.modele or ''}".strip(),
            )
            db.add(article)
            db.commit()
        st.success(f"✅ '{objet.nom}' ajouté aux courses")
    except Exception as e:
        st.error(f"Erreur: {e}")


def _ajouter_au_budget(objet):
    """Ajoute un objet au budget prévisionnel."""
    try:
        from datetime import date

        from src.core.models import Depense

        today = date.today()

        with obtenir_contexte_db() as db:
            depense = Depense(
                libelle=f"Remplacement: {objet.nom}",
                montant=float(objet.prix_remplacement_estime or 0),
                categorie="Maison",
                date=today,
                type_depense="previsionnel",
                notes=f"Objet marqué '{objet.statut}'",
            )
            db.add(depense)
            db.commit()
        st.success(f"✅ '{objet.nom}' ajouté au budget ({objet.prix_remplacement_estime or 0}€)")
    except Exception as e:
        st.error(f"Erreur: {e}")
