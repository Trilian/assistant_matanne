"""
Page Mode Rapide Magasin — Liste organisée par rayon + ajout rapide.

Interface style Bring! : ajout en un tap, cochage par rayon, parcours optimisé.
"""

import logging

import streamlit as st

from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace

logger = logging.getLogger(__name__)

_keys = KeyNamespace("mode_rapide")


def afficher_mode_rapide() -> None:
    """Affiche la liste de courses en mode rapide style Bring! (ajout + cochage par rayon)."""
    st.subheader("⚡ Mode Rapide Magasin")
    st.caption("Ajoutez et cochez vos articles directement depuis le magasin")

    with error_boundary(titre="Erreur mode rapide"):
        # ── Zone d'ajout rapide (style Bring!) ──
        _afficher_ajout_rapide()

        st.divider()

        # ── Liste organisée par rayon ──
        _charger_et_afficher()


def _afficher_ajout_rapide() -> None:
    """Zone d'ajout rapide en tête de liste — un champ, un bouton, c'est tout."""
    from src.services.cuisine.courses import obtenir_service_courses

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        nom = st.text_input(
            "ajout_rapide",
            key=_keys("quick_add_nom"),
            label_visibility="collapsed",
            placeholder="🛒  lait, pain, tomates… (appuyez sur Entrée)",
        )
    with col_btn:
        ajouter = st.button(
            "➕ Ajouter",
            key=_keys("quick_add_btn"),
            use_container_width=True,
            type="primary",
            help="Ajouter à la liste",
        )

    if ajouter or (nom and nom != st.session_state.get(_keys("_last_added"), "")):
        if ajouter and nom and nom.strip():
            _ajouter_article_rapide(nom.strip())


def _ajouter_article_rapide(nom: str) -> None:
    """Ajoute un article à la liste via le service courses."""
    from src.services.cuisine.courses import obtenir_service_courses

    service = obtenir_service_courses()
    if not service:
        st.toast("❌ Service indisponible", icon="❌")
        return

    try:
        ingredient_id = service.obtenir_ou_creer_ingredient(nom=nom, unite="pièce")
        if ingredient_id:
            service.create(
                {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": 1,
                    "priorite": "moyenne",
                    "rayon_magasin": "Autre",
                }
            )
            st.toast(f"✅ {nom} ajouté !", icon="✅")
            # Mémoriser pour éviter double-ajout, puis vider le champ
            st.session_state[_keys("_last_added")] = nom
            st.session_state[_keys("quick_add_nom")] = ""
            st.rerun()
        else:
            st.toast("❌ Erreur création article", icon="❌")
    except Exception as e:
        st.toast(f"❌ Erreur: {e}", icon="❌")
        logger.error(f"Erreur ajout rapide mode_rapide: {e}")


def _charger_et_afficher() -> None:
    """Charge la liste active et l'affiche par rayon."""
    from src.services.cuisine.courses.plan_magasin import construire_liste_rapide

    # Récupérer la liste active
    try:
        from src.core.db import obtenir_contexte_db
        from src.core.models.courses import ListeCourses

        with obtenir_contexte_db() as session:
            liste = (
                session.query(ListeCourses)
                .filter(ListeCourses.statut == "active")
                .order_by(ListeCourses.date_creation.desc())
                .first()
            )

            if not liste:
                st.info("📋 Aucune liste de courses active.")
                return

            liste_id = liste.id
    except Exception as e:
        st.error(f"Erreur accès liste: {e}")
        return

    # Construire la liste rapide
    liste_rapide = construire_liste_rapide(liste_id)

    if not liste_rapide or not liste_rapide.rayons:
        st.info("La liste est vide ou tous les articles sont cochés.")
        return

    # Header avec estimation temps
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Articles", liste_rapide.nb_articles)
    with col2:
        st.metric("Rayons", len(liste_rapide.rayons))
    with col3:
        st.metric("Temps estimé", f"{liste_rapide.temps_estime_min} min")

    st.divider()

    # Affichage par rayon
    for rayon in liste_rapide.rayons:
        with st.expander(
            f"📍 {rayon.nom} ({len(rayon.articles)} articles)",
            expanded=True,
        ):
            for article in rayon.articles:
                checked = st.checkbox(
                    f"{article.nom} — {article.quantite or ''}",
                    key=_keys(f"art_{article.id}"),
                    value=article.achete,
                )
                if checked != article.achete:
                    # Mettre à jour le statut
                    try:
                        # Simple toggle, pas besoin de service complexe
                        from src.core.db import obtenir_contexte_db
                        from src.core.models.courses import ArticleCourses
                        from src.services.inventaire import obtenir_service_inventaire

                        with obtenir_contexte_db() as session:
                            art_db = session.query(ArticleCourses).get(article.id)
                            if art_db:
                                art_db.achete = checked
                                session.commit()
                    except Exception:
                        pass

    # Bouton export texte
    if st.button("📤 Copier la liste", key=_keys("copier")):
        texte = []
        for rayon in liste_rapide.rayons:
            texte.append(f"\n📍 {rayon.nom}")
            for a in rayon.articles:
                texte.append(f"  □ {a.nom} {a.quantite or ''}")
        st.code("\n".join(texte), language=None)


__all__ = ["afficher_mode_rapide"]
