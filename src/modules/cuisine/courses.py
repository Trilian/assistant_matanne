"""
Module Courses - VERSION 3.0 REFACTORISÉE
Intègre tous les refactoring core/ui/utils
"""
import streamlit as st
import asyncio
from typing import Dict, Optional

# ═══════════════════════════════════════════════════════════════
# IMPORTS REFACTORISÉS
# ═══════════════════════════════════════════════════════════════

# Core
from src.core.state import get_state
from src.core.cache import Cache, RateLimit
from src.core.errors import handle_errors

# UI - Namespace unifié
from src.ui import (
    # Base
    empty_state, badge,
    # Forms
    filter_panel,
    # Data
    metrics_row,
    # Feedback
    toast, Modal,
    # Layouts
    item_card
)

# Services
from src.services.courses import courses_service, MAGASINS_CONFIG
from src.services.courses import create_courses_ai_service

# Utils
from src.utils import format_quantity_with_unit


# Constantes
PRIORITE_ICONS = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
PRIORITE_COLORS = {"haute": "#dc3545", "moyenne": "#ffc107", "basse": "#28a745"}


# ═══════════════════════════════════════════════════════════════
# TAB 1 : MA LISTE
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_ma_liste():
    """Tab Ma Liste - REFACTORISÉ"""
    st.subheader("📋 Ma Liste")

    # ✅ Actions rapides
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⚡ Stock bas", use_container_width=True):
            with st.spinner("Génération..."):
                items = courses_service.generer_depuis_stock_bas()
                if items:
                    count = courses_service.ajouter_batch(items)
                    toast(f"✅ {count} ajouté(s)", "success")
                    Cache.invalidate("courses")
                    st.rerun()

    with col2:
        if st.button("📅 Repas", use_container_width=True):
            with st.spinner("Génération..."):
                items = courses_service.generer_depuis_repas_planifies()
                if items:
                    count = courses_service.ajouter_batch(items)
                    toast(f"✅ {count} ajouté(s)", "success")
                    Cache.invalidate("courses")
                    st.rerun()

    with col3:
        if st.button("🗑️ Nettoyer", use_container_width=True):
            count = courses_service.nettoyer_achetes(7)
            toast(f"🗑️ {count} nettoyé(s)", "success")
            Cache.invalidate("courses")
            st.rerun()

    with col4:
        if st.button("🔄 Actualiser", use_container_width=True):
            Cache.invalidate("courses")
            st.rerun()

    st.markdown("---")

    # ✅ Charger liste avec cache
    @Cache.cached(ttl=30)
    def load_liste():
        return courses_service.get_liste_active()

    liste = load_liste()

    if not liste:
        empty_state(
            message="Liste vide",
            icon="🛒",
            subtext="Ajoute des articles"
        )
        return

    # ✅ Stats
    stats = courses_service.get_stats()
    metrics_row([
        {"label": "Total", "value": stats["total_actifs"]},
        {"label": "Prioritaires", "value": stats["prioritaires"]},
        {"label": "IA", "value": stats["part_ia"]}
    ], cols=3)

    st.markdown("---")

    # ✅ Affichage par priorité
    for priorite in ["haute", "moyenne", "basse"]:
        articles = [a for a in liste if a["priorite"] == priorite]

        if not articles:
            continue

        with st.expander(
                f"{PRIORITE_ICONS[priorite]} {priorite.capitalize()} ({len(articles)})",
                expanded=priorite == "haute"
        ):
            for article in articles:
                _render_article_card(article)


def _render_article_card(article: Dict):
    """Carte article avec composant unifié"""
    # Métadonnées
    metadata = [
        format_quantity_with_unit(article["quantite"], article["unite"])
    ]

    if article.get("rayon"):
        metadata.append(f"📍 {article['rayon']}")

    if article.get("magasin"):
        metadata.append(f"🏬 {article['magasin']}")

    # Tags
    tags = []
    if article.get("suggere_par_ia"):
        tags.append("🤖 IA")

    tags.append(f"{PRIORITE_ICONS[article['priorite']]} {article['priorite'].title()}")

    # Actions
    actions = [
        ("✅ Acheté", lambda a=article: _mark_bought(a["id"])),
        ("🗑️ Supprimer", lambda a=article: _delete_article(a["id"]))
    ]

    # Contenu extensible
    def expandable_content():
        if article.get("notes"):
            st.caption("**Notes**")
            st.write(article["notes"])

    # ✅ Composant unifié
    item_card(
        title=article["nom"],
        metadata=metadata,
        status=article.get("priorite", "moyenne").title(),
        status_color=PRIORITE_COLORS.get(article.get("priorite", "moyenne")),
        tags=tags,
        actions=actions,
        expandable_content=expandable_content if article.get("notes") else None,
        key=f"course_{article['id']}"
    )


# ═══════════════════════════════════════════════════════════════
# TAB 2 : GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Tab Génération IA - REFACTORISÉ"""
    st.subheader("🤖 Génération IA")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA indisponible")
        return

    # Vérifier rate limit
    can_call, error_msg = RateLimit.can_call()
    if not can_call:
        st.warning(error_msg)
        return

    ai_service = create_courses_ai_service(agent)

    with st.form("gen_form"):
        col1, col2 = st.columns(2)

        with col1:
            inclure_stock = st.checkbox("📦 Stock bas", value=True)
            inclure_repas = st.checkbox("📅 Repas", value=True)

        with col2:
            magasin = st.selectbox("🏬 Magasin", list(MAGASINS_CONFIG.keys()))
            budget = st.number_input("💶 Budget (€)", 10, 500, 100, 10)

        with st.expander("⚙️ Préférences"):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pref_bio = st.checkbox("🌱 Bio")
                pref_local = st.checkbox("🏘️ Local")
            with col_p2:
                pref_eco = st.checkbox("💰 Économique")

        submitted = st.form_submit_button("✨ Générer", type="primary", use_container_width=True)

    if submitted:
        with st.spinner("🤖 Génération..."):
            try:
                # Préparer articles base
                articles_base = []
                if inclure_stock:
                    articles_base.extend(courses_service.generer_depuis_stock_bas())
                if inclure_repas:
                    articles_base.extend(courses_service.generer_depuis_repas_planifies())

                if not articles_base:
                    st.warning("Aucun article à générer")
                    return

                # Appel IA
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(
                    ai_service.generer_liste_optimisee(
                        articles_base,
                        magasin,
                        MAGASINS_CONFIG[magasin]["rayons"],
                        budget,
                        {"bio": pref_bio, "local": pref_local, "economique": pref_eco}
                    )
                )

                st.session_state.liste_ia = result
                toast("✅ Liste générée !", "success")
                st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")

    # Afficher résultat
    if hasattr(st.session_state, "liste_ia"):
        _render_ia_result(st.session_state.liste_ia, magasin)


def _render_ia_result(result, magasin: str):
    """Affiche résultat IA"""
    st.markdown("---")
    st.markdown("### 📋 Liste Générée")

    # Budget
    metrics_row([
        {"label": "Budget", "value": f"{result.budget_estime:.2f}€"},
        {
            "label": "Statut",
            "value": "⚠️ Dépassement" if result.depasse_budget else "✅ OK"
        },
        {"label": "Économies", "value": f"{result.economies_possibles:.2f}€"}
    ], cols=3)

    st.markdown("---")

    # Articles par rayon
    for rayon, articles in result.par_rayon.items():
        with st.expander(f"📍 {rayon} ({len(articles)})", expanded=True):
            for article in articles:
                _render_ia_article(article, magasin)

    # Actions globales
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Tout ajouter", type="primary", use_container_width=True):
            articles = []
            for arts in result.par_rayon.values():
                for art in arts:
                    articles.append({
                        "nom": art.article,
                        "quantite": art.quantite,
                        "unite": art.unite,
                        "priorite": art.priorite,
                        "rayon": art.rayon,
                        "magasin": magasin,
                        "ia": True
                    })

            count = courses_service.ajouter_batch(articles)
            del st.session_state.liste_ia
            toast(f"✅ {count} ajouté(s) !", "success")
            Cache.invalidate("courses")
            st.balloons()
            st.rerun()

    with col2:
        if st.button("🗑️ Annuler", use_container_width=True):
            del st.session_state.liste_ia
            st.rerun()


def _render_ia_article(article, magasin: str):
    """Carte article IA"""
    metadata = [
        format_quantity_with_unit(article.quantite, article.unite),
        f"📍 {article.rayon}"
    ]

    if article.prix_estime:
        metadata.append(f"💶 ~{article.prix_estime:.2f}€")

    tags = [f"{PRIORITE_ICONS[article.priorite]} {article.priorite.title()}"]

    actions = [
        ("➕ Ajouter", lambda a=article: _add_ia_article(a, magasin))
    ]

    item_card(
        title=article.article,
        metadata=metadata,
        tags=tags,
        actions=actions,
        key=f"ia_{article.article}"
    )


# ═══════════════════════════════════════════════════════════════
# TAB 3 : AJOUT MANUEL
# ═══════════════════════════════════════════════════════════════

def tab_ajout_manuel():
    """Tab Ajout Manuel"""
    st.subheader("➕ Ajouter")

    with st.form("form_ajout"):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Article *", placeholder="Ex: Tomates")
            quantite = st.number_input("Quantité *", 0.1, 1000.0, 1.0, 0.1)
            unite = st.selectbox("Unité", ["pcs", "kg", "g", "L", "mL", "sachets", "boîtes"])

        with col2:
            priorite = st.selectbox(
                "Priorité",
                ["basse", "moyenne", "haute"],
                format_func=lambda x: f"{PRIORITE_ICONS[x]} {x.capitalize()}"
            )
            magasin = st.selectbox("Magasin", list(MAGASINS_CONFIG.keys()))

        notes = st.text_area("Notes", placeholder="Format, marque...")

        if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
            if not nom:
                st.error("Nom obligatoire")
            else:
                try:
                    courses_service.ajouter(
                        nom, quantite, unite, priorite,
                        magasin=magasin, notes=notes
                    )
                    toast(f"✅ {nom} ajouté", "success")
                    Cache.invalidate("courses")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _mark_bought(article_id: int):
    """Marque acheté"""
    modal = Modal(f"buy_{article_id}")

    if st.button("✅", key=f"buy_{article_id}"):
        modal.show()

    if modal.is_showing():
        st.info("📦 Ajouter au stock ?")

        add_stock = st.checkbox("Ajouter au stock", value=True, key=f"stock_{article_id}")

        if modal.confirm("✅ Confirmer"):
            try:
                courses_service.marquer_achete(article_id, add_stock)
                toast("✅ Acheté", "success")
                Cache.invalidate("courses")
                modal.close()
            except Exception as e:
                st.error(f"❌ {str(e)}")

        modal.cancel()


def _delete_article(article_id: int):
    """Supprime article"""
    try:
        courses_service.delete(article_id)
        toast("🗑️ Supprimé", "success")
        Cache.invalidate("courses")
        st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)}")


def _add_ia_article(article, magasin: str):
    """Ajoute article IA"""
    try:
        courses_service.ajouter(
            article.article,
            article.quantite,
            article.unite,
            article.priorite,
            rayon=article.rayon,
            magasin=magasin,
            ia_suggere=True
        )
        toast("✅ Ajouté", "success")
        Cache.invalidate("courses")
        st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - VERSION REFACTORISÉE"""
    st.title("🛒 Courses Intelligentes")
    st.caption("IA • Optimisation • Organisation magasins")

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Ma Liste",
        "🤖 Génération IA",
        "➕ Ajouter"
    ])

    with tab1:
        tab_ma_liste()

    with tab2:
        tab_generation_ia()

    with tab3:
        tab_ajout_manuel()