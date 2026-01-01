"""
Module Courses - VERSION MIGRÉE COMPLÈTE
Intègre: BaseModuleUI, Validation, Feedback, Services IA refactorisés
"""
import streamlit as st
from datetime import date
from typing import Optional, List, Dict

# Services
from src.services.courses import courses_service, MAGASINS_CONFIG
from src.services.ai_services import create_courses_ai_service
from src.services.planning import planning_service
from src.services.inventaire import inventaire_service

# UI
from src.ui.base_module import create_module_ui
from src.ui.feedback import smart_spinner, ProgressTracker, show_success, show_error
from src.ui.components import Modal, empty_state, badge

# Validation
from src.core.validation_middleware import (
    validate_and_sanitize_form,
    COURSES_SCHEMA
)

# Cache & State
from src.core.cache import Cache
from src.core.state import get_state

# Config
from .configs import get_courses_config


# ═══════════════════════════════════════════════════════════
# MODULE PRINCIPAL
# ═══════════════════════════════════════════════════════════

def app():
    """Point d'entrée module courses - Version migrée"""
    st.title("🛒 Courses Intelligentes")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📝 Liste",
        "🤖 Génération IA",
        "⚙️ Paramètres"
    ])

    with tab1:
        render_liste_courses()

    with tab2:
        render_generation_ia()

    with tab3:
        render_parametres()


# ═══════════════════════════════════════════════════════════
# TAB 1: LISTE COURSES
# ═══════════════════════════════════════════════════════════

def render_liste_courses():
    """Affichage liste courses"""

    # Charger liste active
    liste = courses_service.get_liste_active()

    if not liste:
        empty_state(
            "Liste vide",
            "🛒",
            "Ajoute des articles ou génère avec l'IA"
        )
        render_quick_add()
        return

    # Stats rapides
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total", len(liste))

    with col2:
        haute = len([a for a in liste if a.get("priorite") == "haute"])
        st.metric("🔴 Haute", haute)

    with col3:
        moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])
        st.metric("🟡 Moyenne", moyenne)

    with col4:
        basse = len([a for a in liste if a.get("priorite") == "basse"])
        st.metric("🟢 Basse", basse)

    # Actions rapides
    col_add, col_gen, col_clear = st.columns(3)

    with col_add:
        if st.button("➕ Ajouter", type="primary", use_container_width=True):
            st.session_state.show_add_form = True

    with col_gen:
        if st.button("🤖 Générer IA", use_container_width=True):
            st.session_state.show_ia_generation = True

    with col_clear:
        if st.button("🗑️ Vider Liste", use_container_width=True):
            st.session_state.show_clear_confirm = True

    # Formulaire ajout rapide
    if st.session_state.get("show_add_form", False):
        render_quick_add()

    st.markdown("---")

    # Grouper par magasin
    groupes_magasin = {}
    for article in liste:
        magasin = article.get("magasin", "Non assigné")
        if magasin not in groupes_magasin:
            groupes_magasin[magasin] = []
        groupes_magasin[magasin].append(article)

    # Afficher par magasin
    for magasin, articles in groupes_magasin.items():
        with st.expander(f"🏪 {magasin} ({len(articles)} articles)", expanded=True):

            # Couleur magasin
            couleur = MAGASINS_CONFIG.get(magasin, {}).get("couleur", "#gray")

            st.markdown(
                f'<div style="border-left: 4px solid {couleur}; padding-left: 1rem;">',
                unsafe_allow_html=True
            )

            for article in sorted(articles, key=lambda x: x.get("priorite", "moyenne")):
                render_article_card(article)

            st.markdown('</div>', unsafe_allow_html=True)


def render_article_card(article: Dict):
    """Carte article courses"""

    col1, col2, col3 = st.columns([3, 2, 2])

    with col1:
        # Checkbox "acheté"
        checked = st.checkbox(
            article["nom"],
            value=False,
            key=f"check_{article['id']}"
        )

        if checked:
            mark_as_bought(article["id"])

        # Infos
        st.caption(
            f"{article['quantite']} {article['unite']} • "
            f"{article.get('priorite', 'moyenne').capitalize()}"
        )

        if article.get("notes"):
            st.caption(f"📝 {article['notes']}")

    with col2:
        # Priorité
        priorite_colors = {
            "haute": "🔴",
            "moyenne": "🟡",
            "basse": "🟢"
        }

        icon = priorite_colors.get(article.get("priorite", "moyenne"), "⚪")
        st.markdown(f"{icon} {article.get('priorite', 'moyenne').capitalize()}")

        if article.get("rayon_magasin"):
            st.caption(f"📍 {article['rayon_magasin']}")

    with col3:
        # Actions
        col_edit, col_del = st.columns(2)

        with col_edit:
            if st.button("✏️", key=f"edit_{article['id']}", help="Modifier"):
                st.session_state.editing_article_id = article["id"]
                st.rerun()

        with col_del:
            if st.button("🗑️", key=f"del_{article['id']}", help="Supprimer"):
                delete_article(article["id"])


def render_quick_add():
    """Ajout rapide article"""

    with st.expander("➕ Ajout Rapide", expanded=True):
        with st.form("quick_add_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                nom = st.text_input("Article *")
                quantite = st.number_input("Quantité *", min_value=0.1, step=0.1, value=1.0)

            with col2:
                unite = st.selectbox("Unité *", ["pcs", "kg", "g", "L", "mL"])
                priorite = st.selectbox("Priorité", ["haute", "moyenne", "basse"], index=1)

            with col3:
                magasin = st.selectbox("Magasin", [""] + list(MAGASINS_CONFIG.keys()))
                rayon = st.text_input("Rayon (optionnel)")

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                submitted = st.form_submit_button("✅ Ajouter", type="primary", use_container_width=True)

            with col_cancel:
                cancelled = st.form_submit_button("❌ Annuler", use_container_width=True)

            if cancelled:
                st.session_state.show_add_form = False
                st.rerun()

            if submitted:
                # ✅ Validation sécurisée
                form_data = {
                    "nom": nom,
                    "quantite": quantite,
                    "unite": unite,
                    "priorite": priorite,
                    "magasin": magasin if magasin else None
                }

                is_valid, sanitized = validate_and_sanitize_form("courses", form_data)

                if is_valid:
                    try:
                        from src.utils.helpers import find_or_create_ingredient

                        # Créer ingrédient si besoin
                        ingredient_id = find_or_create_ingredient(
                            nom=sanitized["nom"],
                            unite=sanitized["unite"]
                        )

                        # Créer article
                        courses_service.create({
                            "ingredient_id": ingredient_id,
                            "quantite_necessaire": sanitized["quantite"],
                            "priorite": sanitized["priorite"],
                            "magasin_cible": sanitized.get("magasin"),
                            "rayon_magasin": rayon if rayon else None
                        })

                        Cache.invalidate("courses")
                        show_success(f"✅ '{sanitized['nom']}' ajouté !")

                        st.session_state.show_add_form = False
                        st.rerun()

                    except Exception as e:
                        show_error(f"❌ Erreur: {str(e)}")


def mark_as_bought(article_id: int):
    """Marque article comme acheté"""

    try:
        courses_service.update(article_id, {
            "achete": True,
            "achete_le": date.today()
        })

        Cache.invalidate("courses")
        show_success("✅ Article acheté !")

        st.rerun()

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")


def delete_article(article_id: int):
    """Supprime article"""

    try:
        courses_service.delete(article_id)
        Cache.invalidate("courses")
        show_success("🗑️ Article supprimé")
        st.rerun()

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")


# ═══════════════════════════════════════════════════════════
# TAB 2: GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════

def render_generation_ia():
    """Génération liste courses avec IA"""

    st.markdown("### 🤖 Génération Intelligente")
    st.caption("Génère ta liste basée sur planning + inventaire")

    # Charger données
    planning = planning_service.get_planning_semaine(
        planning_service.get_semaine_debut()
    )

    inventaire = inventaire_service.get_inventaire_complet()

    # Infos sources
    col1, col2 = st.columns(2)

    with col1:
        st.info(
            f"📅 **Planning:** "
            f"{len(planning.repas) if planning else 0} repas"
        )

    with col2:
        stock_bas = len([a for a in inventaire if a.get("statut") in ["critique", "sous_seuil"]])
        st.info(f"📦 **Inventaire:** {stock_bas} articles à commander")

    # Options
    st.markdown("#### Options")

    col_opt1, col_opt2 = st.columns(2)

    with col_opt1:
        inclure_planning = st.checkbox(
            "📅 Inclure planning semaine",
            value=True,
            help="Génère liste basée sur repas planifiés"
        )

    with col_opt2:
        inclure_inventaire = st.checkbox(
            "📦 Inclure stock bas inventaire",
            value=True,
            help="Ajoute articles sous le seuil"
        )

    # Bouton génération
    if st.button("🚀 Générer Liste IA", type="primary", use_container_width=True):

        if not inclure_planning and not inclure_inventaire:
            st.warning("⚠️ Sélectionne au moins une source")
            return

        generate_courses_with_ia(
            planning=planning if inclure_planning else None,
            inventaire=inventaire if inclure_inventaire else None
        )


async def generate_courses_with_ia(
        planning: Optional[Dict],
        inventaire: Optional[List[Dict]]
):
    """
    Génère liste courses avec IA

    ✅ Feedback temps réel
    ✅ Cache sémantique
    ✅ Validation automatique
    """

    ai_service = create_courses_ai_service()

    try:
        # Préparer données
        planning_data = {}
        if planning:
            planning_data = planning_service.get_planning_structure(planning.id)

        inventaire_data = inventaire or []

        # ✅ Feedback automatique
        articles = await ai_service.generer_liste_courses(
            planning_semaine=planning_data,
            inventaire=inventaire_data
        )

        if not articles:
            st.warning("Aucun article généré")
            return

        # Afficher résultats
        st.markdown(f"### ✨ {len(articles)} Articles Générés")

        for idx, article in enumerate(articles):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    st.markdown(f"**{article.nom}**")
                    st.caption(f"{article.quantite} {article.unite}")
                    if article.raison:
                        st.caption(f"💡 {article.raison}")

                with col2:
                    # Priorité
                    priorite_colors = {
                        "haute": "🔴",
                        "moyenne": "🟡",
                        "basse": "🟢"
                    }
                    icon = priorite_colors.get(article.priorite, "⚪")
                    st.markdown(f"{icon} {article.priorite.capitalize()}")

                with col3:
                    if st.button(
                            "💾",
                            key=f"save_ia_{idx}",
                            help="Ajouter à la liste",
                            use_container_width=True
                    ):
                        save_generated_article(article.dict())

        # Actions groupées
        st.markdown("---")

        col_all, col_high = st.columns(2)

        with col_all:
            if st.button("💾 Tout Ajouter", type="primary", use_container_width=True):
                add_all_articles([a.dict() for a in articles])

        with col_high:
            if st.button("🔴 Ajouter Priorité Haute", use_container_width=True):
                high_priority = [a.dict() for a in articles if a.priorite == "haute"]
                add_all_articles(high_priority)

    except Exception as e:
        show_error(f"❌ Erreur génération: {str(e)}")
        st.exception(e)


def save_generated_article(article_data: Dict):
    """Sauvegarde un article généré"""

    try:
        # ✅ Validation
        is_valid, sanitized = validate_and_sanitize_form("courses", article_data)

        if not is_valid:
            show_error("❌ Article invalide")
            return

        from src.utils.helpers import find_or_create_ingredient

        ingredient_id = find_or_create_ingredient(
            nom=sanitized["nom"],
            unite=sanitized["unite"]
        )

        courses_service.create({
            "ingredient_id": ingredient_id,
            "quantite_necessaire": sanitized["quantite"],
            "priorite": sanitized["priorite"]
        })

        Cache.invalidate("courses")
        show_success(f"✅ '{sanitized['nom']}' ajouté !")

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")


def add_all_articles(articles: List[Dict]):
    """Ajoute plusieurs articles avec progress"""

    progress = ProgressTracker("Ajout articles", total=len(articles))

    added = 0
    for i, article in enumerate(articles):
        try:
            save_generated_article(article)
            added += 1
            progress.update(i+1, f"✅ {article['nom']}")

        except Exception as e:
            progress.update(i+1, f"❌ Erreur")

    progress.complete(f"✅ {added}/{len(articles)} articles ajoutés")


# ═══════════════════════════════════════════════════════════
# TAB 3: PARAMÈTRES
# ═══════════════════════════════════════════════════════════

def render_parametres():
    """Paramètres module courses"""

    st.markdown("### ⚙️ Paramètres")

    # Magasins
    st.markdown("#### 🏪 Magasins")

    for magasin, config in MAGASINS_CONFIG.items():
        with st.expander(magasin):
            st.markdown(
                f'<div style="background: {config["couleur"]}; padding: 1rem; '
                f'border-radius: 8px; color: white; font-weight: bold;">{magasin}</div>',
                unsafe_allow_html=True
            )

            st.write("**Rayons:**")
            for rayon in config["rayons"]:
                st.write(f"• {rayon}")

    # Actions
    st.markdown("---")
    st.markdown("#### 🧹 Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Supprimer Achetés", use_container_width=True):
            delete_bought_items()

    with col2:
        if st.button("🗑️ Vider Cache", use_container_width=True):
            Cache.invalidate("courses")
            show_success("Cache vidé !")

    # Stats
    st.markdown("---")
    st.markdown("#### 📊 Statistiques")

    stats = courses_service.get_stats(
        group_by_fields=["priorite"],
        count_filters={
            "achetes": {"achete": True}
        }
    )

    col3, col4 = st.columns(2)

    with col3:
        st.metric("Total Articles", stats.get("total", 0))

    with col4:
        st.metric("Achetés", stats.get("achetes", 0))


def delete_bought_items():
    """Supprime articles achetés"""

    try:
        liste = courses_service.get_liste_active(filters={"achete": True})

        if not liste:
            st.info("Aucun article acheté")
            return

        # Confirmation
        st.warning(f"⚠️ {len(liste)} articles achetés à supprimer")

        if st.button("Confirmer Suppression", type="primary"):
            deleted = 0

            for article in liste:
                courses_service.delete(article["id"])
                deleted += 1

            Cache.invalidate("courses")
            show_success(f"✅ {deleted} articles supprimés")
            st.rerun()

    except Exception as e:
        show_error(f"❌ Erreur: {str(e)}")