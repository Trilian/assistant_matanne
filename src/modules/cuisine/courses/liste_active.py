"""
Liste active des courses.
"""

from ._common import (
    PRIORITY_EMOJIS,
    RAYONS_DEFAULT,
    datetime,
    get_courses_service,
    get_inventaire_service,
    logger,
    st,
)
from .liste_utils import (
    filtrer_liste,
    formater_article_label,
    grouper_par_rayon,
)


def render_liste_active():
    """Gestion interactive de la liste active"""
    service = get_courses_service()
    inventaire_service = get_inventaire_service()

    if service is None:
        st.error("❌ Service courses indisponible")
        return

    try:
        # Récupérer la liste
        liste = service.get_liste_courses(achetes=False)

        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📥 À acheter", len(liste))
        with col2:
            haute = len([a for a in liste if a.get("priorite") == "haute"])
            st.metric("🔴 Haute priorité", haute)
        with col3:
            if inventaire_service:
                alertes = inventaire_service.get_alertes()
                stock_bas = len(alertes.get("stock_bas", []))
                st.metric("⚠️ Stock bas", stock_bas)
        with col4:
            st.metric("💰 Total articles", len(service.get_liste_courses(achetes=True)))

        st.divider()

        if not liste:
            st.info("✅ Liste vide! Ajoutez des articles ou générez des suggestions IA.")
            if st.button("⏰ Générer suggestions IA"):
                st.session_state.new_article_mode = False
                st.rerun()
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
            with st.expander(f"🍪‘ {rayon} ({len(rayons[rayon])} articles)", expanded=True):
                render_rayon_articles(service, rayon, rayons[rayon])

        st.divider()

        # Actions rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Ajouter article", use_container_width=True):
                st.session_state.new_article_mode = True
                st.rerun()
        with col2:
            if st.button("📄 Imprimer liste", use_container_width=True):
                render_print_view(liste_filtree)
        with col3:
            if st.button("🗑️ Vider (achetés)", use_container_width=True):
                if service.get_liste_courses(achetes=True):
                    st.warning("⚠️ Suppression des articles achetés...")
                    st.session_state.courses_refresh += 1
                    st.rerun()

        # Formulaire ajout article
        if st.session_state.new_article_mode:
            st.divider()
            render_ajouter_article()

    except Exception as e:
        st.error(f"❌ Erreur: {str(e)}")
        logger.error(f"Erreur render_liste_active: {e}")


def render_rayon_articles(service, rayon: str, articles: list):
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
                    st.session_state.courses_refresh += 1
                    st.rerun()
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
                st.rerun()

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
                    st.session_state.courses_refresh += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

        # Formulaire édition inline si sélectionné
        if st.session_state.get("edit_article_id") == article["id"]:
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
                            st.session_state.courses_refresh += 1
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur: {str(e)}")

                with col2:
                    if st.form_submit_button("❌ Annuler", key=f"article_cancel_{article['id']}"):
                        st.session_state.edit_article_id = None
                        st.rerun()


def render_ajouter_article():
    """Formulaire ajout article"""
    st.subheader("➕ Ajouter un article")

    service = get_courses_service()
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
                # Créer/trouver l'ingrédient
                from src.core.database import obtenir_contexte_db
                from src.core.models import Ingredient

                with obtenir_contexte_db() as db:
                    ingredient = db.query(Ingredient).filter(Ingredient.nom == nom).first()

                    if not ingredient:
                        ingredient = Ingredient(nom=nom, unite=unite)
                        db.add(ingredient)
                        db.flush()
                        db.refresh(ingredient)

                    ingredient_id = ingredient.id

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
                st.session_state.courses_refresh += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")
                logger.error(f"Erreur ajout article: {e}")


def render_print_view(liste):
    """Vue d'impression optimisée"""
    st.subheader("🖨️ Liste à imprimer")

    # Grouper par rayon
    rayons = {}
    for article in liste:
        rayon = article.get("rayon_magasin", "Autre")
        if rayon not in rayons:
            rayons[rayon] = []
        rayons[rayon].append(article)

    print_text = "📋 LISTE DE COURSES\n"
    print_text += f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
    print_text += "=" * 40 + "\n\n"

    for rayon in sorted(rayons.keys()):
        print_text += f"🏷️ {rayon}\n"
        for article in rayons[rayon]:
            checkbox = "☑"
            qty = f"{article.get('quantite_necessaire')} {article.get('unite')}"
            print_text += f"  {checkbox} {article.get('ingredient_nom')} ({qty})\n"
        print_text += "\n"

    st.text_area("Copier/Coller la liste:", value=print_text, height=400, disabled=True)


__all__ = [
    "render_liste_active",
    "render_rayon_articles",
    "render_ajouter_article",
    "render_print_view",
]
