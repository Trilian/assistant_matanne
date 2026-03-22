"""
Liste active des courses.
"""

import logging
from datetime import datetime

import streamlit as st

from src.core.session_keys import SK
from src.core.state import rerun
from src.services.cuisine.courses import obtenir_service_courses
from src.services.inventaire import obtenir_service_inventaire
from src.ui.fragments import ui_fragment

from .utils import (
    PRIORITY_EMOJIS,
    RAYONS_DEFAULT,
    filtrer_liste,
    formater_article_label,
    generer_texte_impression,
    grouper_par_magasin,
    grouper_par_magasin_personnalise,
    grouper_par_rayon,
    obtenir_mapping_magasins_par_defaut,
)

logger = logging.getLogger(__name__)


@ui_fragment
def afficher_liste_active():
    """Gestion interactive de la liste active"""
    service = obtenir_service_courses()
    inventaire_service = obtenir_service_inventaire()

    if "new_article_mode" not in st.session_state:
        st.session_state.new_article_mode = False
    if "courses_print_open" not in st.session_state:
        st.session_state["courses_print_open"] = False

    if service is None:
        st.error("❌ Service courses indisponible")
        return

    try:
        # ── Zone d'ajout rapide (style Bring!) ──
        _afficher_ajout_rapide(service)

        st.divider()

        # Récupérer la liste
        liste = service.get_liste_courses(achetes=False)

        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📥 À acheter", len(liste))
        with col2:
            haute = len([a for a in liste if a.get("priorite") == "haute"])
            st.metric("🔴 Urgent", haute)
        with col3:
            if inventaire_service:
                alertes = inventaire_service.get_alertes()
                stock_bas = len(alertes.get("stock_bas", []))
                st.metric("⚠️ Stock bas", stock_bas)
        with col4:
            st.metric("✅ Achetés", len(service.get_liste_courses(achetes=True)))

        st.divider()

        if not liste:
            st.info("✅ Liste vide! Ajoutez des articles ou générez des suggestions IA.")
            if st.button("⏰ Générer suggestions IA"):
                st.session_state.new_article_mode = False
                rerun()
            return

        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_priorite = st.selectbox(
                "Filtrer par priorité",
                ["Toutes", "🔴 Haute", "🟡 Moyenne", "🟢 Basse"],
                key="filter_priorite",
            )
        with col2:
            filter_rayon = st.selectbox(
                "Filtrer par rayon",
                ["Tous les rayons"] + sorted({a.get("rayon_magasin", "Autre") for a in liste}),
                key="filter_rayon",
            )
        with col3:
            search_term = st.text_input("🔍 Chercher...", key="search_courses")

        # Appliquer filtres via fonction utilitaire
        priority_map = {"🔴 Haute": "haute", "🟡 Moyenne": "moyenne", "🟢 Basse": "basse"}
        priorite_filter = priority_map.get(filter_priorite) if filter_priorite != "Toutes" else None
        rayon_filter = filter_rayon if filter_rayon != "Tous les rayons" else None

        liste_filtree = filtrer_liste(
            liste,
            priorite=priorite_filter,
            rayon=rayon_filter,
            search_term=search_term or None,
        )

        st.success(f"📊 {len(liste_filtree)}/{len(liste)} article(s)")

        # Afficher par rayon (via fonction utilitaire)
        st.subheader("📦 Articles par rayon")
        rayons = grouper_par_rayon(liste_filtree)

        for rayon in sorted(rayons.keys()):
            with st.expander(f"📍 {rayon} ({len(rayons[rayon])} articles)", expanded=True):
                afficher_rayon_articles(service, rayon, rayons[rayon])

        st.divider()

        # Actions rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(
                "➕ Ajouter article",
                use_container_width=True,
                help="Ajouter un article manuellement à votre liste",
            ):
                st.session_state.new_article_mode = True
                rerun()
        with col2:
            if st.button(
                "📄 Imprimer liste",
                use_container_width=True,
                help="Afficher la liste dans un format imprimable",
            ):
                st.session_state["courses_print_open"] = True
                rerun()
        with col3:
            if st.button(
                "🗑️ Vider (achetés)",
                use_container_width=True,
                help="Supprimer tous les articles déjà marqués comme achetés",
            ):
                achetes = service.get_liste_courses(achetes=True)
                if achetes:
                    nb_suppr = 0
                    for art in achetes:
                        try:
                            if service.delete(art["id"]):
                                nb_suppr += 1
                        except Exception:
                            logger.error(f"Erreur suppression article {art['id']}")
                    st.success(f"✅ {nb_suppr} article(s) acheté(s) supprimé(s)")
                    st.session_state[SK.COURSES_REFRESH] += 1
                    rerun()
                else:
                    st.info("Aucun article acheté à supprimer")

        # Formulaire ajout article
        if st.session_state.new_article_mode:
            st.divider()
            afficher_ajouter_article()

        # Vue impression persistante (reste ouverte au changement d'option)
        if st.session_state.get("courses_print_open"):
            st.divider()
            afficher_print_view(liste_filtree)

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur afficher_liste_active: {e}")


def afficher_rayon_articles(service, rayon: str, articles: list):
    """Affiche et gère les articles d'un rayon"""
    for article in articles:
        col1, col2, col3, col4 = st.columns([4, 1, 1, 1], gap="small")

        with col1:
            label = formater_article_label(article, PRIORITY_EMOJIS)
            st.write(label)

        with col2:
            if st.button(
                "✅",
                key=f"article_mark_{article['id']}",
                help="Marquer acheté",
                use_container_width=True,
            ):
                try:
                    service.update(article["id"], {"achete": True, "achete_le": datetime.now()})
                    st.success(f"✅ {article.get('ingredient_nom')} marqué acheté!")
                    st.session_state[SK.COURSES_REFRESH] += 1
                    rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

        with col3:
            if st.button(
                "✏️",
                key=f"article_edit_{article['id']}",
                help="Modifier",
                use_container_width=True,
            ):
                st.session_state.edit_article_id = article["id"]
                rerun()

        with col4:
            if st.button(
                "🗑️",
                key=f"article_del_{article['id']}",
                help="Supprimer",
                use_container_width=True,
            ):
                try:
                    service.delete(article["id"])
                    st.success(f"✅ {article.get('ingredient_nom')} supprimé!")
                    st.session_state[SK.COURSES_REFRESH] += 1
                    rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

        # Formulaire édition inline si sélectionné
        if st.session_state.get(SK.EDIT_ARTICLE_ID) == article["id"]:
            st.divider()
            with st.form(f"article_edit_form_{article['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_quantite = st.number_input(
                        "Quantité",
                        value=article.get("quantite_necessaire", 1.0),
                        min_value=0.1,
                        step=0.1,
                        key=f"article_qty_{article['id']}",
                    )
                with col2:
                    new_priorite = st.selectbox(
                        "Priorité",
                        list(PRIORITY_EMOJIS.keys()),
                        index=list(PRIORITY_EMOJIS.keys()).index(
                            article.get("priorite", "moyenne")
                        ),
                        key=f"article_prio_{article['id']}",
                    )

                new_rayon = st.selectbox(
                    "Rayon",
                    RAYONS_DEFAULT,
                    index=RAYONS_DEFAULT.index(article.get("rayon_magasin", "Autre"))
                    if article.get("rayon_magasin") in RAYONS_DEFAULT
                    else -1,
                    key=f"article_ray_{article['id']}",
                )

                new_notes = st.text_area(
                    "Notes",
                    value=article.get("notes", ""),
                    max_chars=200,
                    key=f"article_notes_{article['id']}",
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Sauvegarder", key=f"article_save_{article['id']}"):
                        try:
                            service.update(
                                article["id"],
                                {
                                    "quantite_necessaire": new_quantite,
                                    "priorite": new_priorite,
                                    "rayon_magasin": new_rayon,
                                    "notes": new_notes or None,
                                },
                            )
                            st.success("✅ Article mis à jour!")
                            st.session_state.edit_article_id = None
                            st.session_state[SK.COURSES_REFRESH] += 1
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

                with col2:
                    if st.form_submit_button("❌ Annuler", key=f"article_cancel_{article['id']}"):
                        st.session_state.edit_article_id = None
                        rerun()


def afficher_ajouter_article():
    """Formulaire ajout article"""
    st.subheader("➕ Ajouter un article")

    service = obtenir_service_courses()
    if service is None:
        st.error("❌ Service indisponible")
        return

    with st.form("form_new_article"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom de l'article", placeholder="ex: Tomates", max_chars=100)
        with col2:
            unite = st.selectbox("Unité", ["kg", "l", "pièce", "g", "ml", "paquet"])

        quantite = st.number_input("Quantité", min_value=0.1, value=1.0, step=0.1)

        col1, col2 = st.columns(2)
        with col1:
            priorite = st.selectbox("Priorité", ["basse", "moyenne", "haute"])
        with col2:
            rayon = st.selectbox("Rayon", RAYONS_DEFAULT)

        notes = st.text_area("Notes (optionnel)", max_chars=200)

        submitted = st.form_submit_button("✅ Ajouter", use_container_width=True)
        if submitted:
            if not nom:
                st.error("⚠️ Entrez un nom d'article")
                return

            try:
                # Créer/trouver l'ingrédient via service
                ingredient_id = service.obtenir_ou_creer_ingredient(nom=nom, unite=unite)

                if not ingredient_id:
                    st.error("❌ Erreur création ingrédient")
                    return

                # Ajouter article courses avec le service
                data = {
                    "ingredient_id": ingredient_id,
                    "quantite_necessaire": quantite,
                    "priorite": priorite,
                    "rayon_magasin": rayon,
                    "notes": notes or None,
                }

                service.create(data)

                st.success(f"✅ {nom} ajouté à la liste!")
                st.session_state.new_article_mode = False
                st.session_state[SK.COURSES_REFRESH] += 1
                rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur ajout article: {e}")


def afficher_print_view(liste):
    """Vue d'impression optimisée"""
    st.subheader("🖨️ Liste à emporter")
    st.caption("Vue simple type Bring, avec regroupement au choix.")

    col_close, _ = st.columns([1, 4])
    with col_close:
        if st.button("❌ Fermer", key="courses_print_close", use_container_width=True):
            st.session_state["courses_print_open"] = False
            rerun()

    mode = st.radio(
        "Organisation",
        options=["Simple", "Par rayon", "Par magasin"],
        horizontal=True,
        key="courses_print_mode",
    )

    mapping_custom: dict[str, str] | None = None

    if mode == "Par magasin":
        if "courses_store_map" not in st.session_state:
            st.session_state["courses_store_map"] = obtenir_mapping_magasins_par_defaut()

        with st.expander("⚙️ Personnaliser les magasins", expanded=False):
            st.caption("Choisis le magasin cible pour chaque rayon.")
            mapping_edit = dict(st.session_state.get("courses_store_map", {}))
            rayons_presents = sorted({a.get("rayon_magasin") or "Autre" for a in liste})

            for rayon in rayons_presents:
                default_val = mapping_edit.get(rayon, "Autre magasin")
                new_val = st.text_input(
                    f"{rayon}",
                    value=default_val,
                    key=f"store_map_{rayon}",
                    placeholder="Nom du magasin",
                )
                mapping_edit[rayon] = (new_val or "Autre magasin").strip() or "Autre magasin"

            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Appliquer", use_container_width=True, key="store_map_apply"):
                    st.session_state["courses_store_map"] = mapping_edit
                    st.success("Mapping magasins mis à jour")
            with c2:
                if st.button("↩️ Réinitialiser", use_container_width=True, key="store_map_reset"):
                    st.session_state["courses_store_map"] = obtenir_mapping_magasins_par_defaut()
                    st.success("Mapping magasins réinitialisé")
                    rerun()

        mapping_custom = st.session_state.get("courses_store_map", {})
        groupes = grouper_par_magasin_personnalise(liste, mapping_custom)
        group_key = "magasin"
    elif mode == "Par rayon":
        groupes = grouper_par_rayon(liste)
        group_key = "rayon"
    else:
        groupes = {"Liste rapide": sorted(liste, key=lambda a: a.get("ingredient_nom", "").lower())}
        group_key = "simple"

    # Affichage visuel clair, sans zone grisée
    for groupe in sorted(groupes.keys()):
        with st.expander(f"🧺 {groupe} ({len(groupes[groupe])})", expanded=True):
            for article in groupes[groupe]:
                quantite = article.get("quantite_necessaire", 1)
                unite = (article.get("unite") or "").strip()
                qty = f"{quantite} {unite}".strip()
                article_id = article.get("id")
                nom = article.get("ingredient_nom", "Article")
                if article_id is None:
                    st.markdown(f"- ☐ **{nom}** ({qty})")
                    continue

                checked = st.checkbox(
                    f"{nom} ({qty})",
                    key=f"print_check_{article_id}",
                    value=False,
                )
                if checked:
                    st.caption(f"~~{nom} ({qty})~~")

    print_text = generer_texte_impression(
        liste,
        titre="LISTE DE COURSES",
        group_by=group_key,
        mapping_rayon_magasin=mapping_custom,
    )

    st.download_button(
        "📥 Télécharger (.txt)",
        data=print_text,
        file_name=f"liste_courses_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.code(print_text, language="text")


# ═══════════════════════════════════════════════════════════
# AJOUT RAPIDE (ex-mode_rapide_ui)
# ═══════════════════════════════════════════════════════════


def _afficher_ajout_rapide(service) -> None:
    """Zone d'ajout rapide en tête de liste — un champ, un bouton."""
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        nom = st.text_input(
            "ajout_rapide",
            key="quick_add_nom",
            label_visibility="collapsed",
            placeholder="🛒  lait, pain, tomates… (appuyez sur Entrée)",
        )
    with col_btn:
        ajouter = st.button(
            "➕",
            key="quick_add_btn",
            use_container_width=True,
            type="primary",
            help="Ajouter à la liste",
        )

    if ajouter and nom and nom.strip():
        _ajouter_article_rapide(service, nom.strip())


def _ajouter_article_rapide(service, nom: str) -> None:
    """Ajoute un article rapidement via le service courses."""
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
            st.session_state["quick_add_nom"] = ""
            st.session_state[SK.COURSES_REFRESH] += 1
            rerun()
        else:
            st.toast("❌ Erreur création article", icon="❌")
    except Exception as e:
        st.toast(f"❌ Erreur: {e}", icon="❌")
        logger.error(f"Erreur ajout rapide: {e}")


__all__ = [
    "afficher_liste_active",
    "afficher_rayon_articles",
    "afficher_ajouter_article",
    "afficher_print_view",
]
