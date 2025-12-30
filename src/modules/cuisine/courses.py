"""
Module Courses
"""
import streamlit as st
import asyncio
from typing import Dict, List

# Core
from src.core.state import get_state
from src.core.cache import Cache
from src.core.errors import handle_errors

# UI Composants
from src.ui import empty_state, badge, metrics_row, toast, Modal
from src.ui.forms import form_field

# Services
from src.services.courses import courses_service, MAGASINS_CONFIG, create_courses_ai_service

# Utils
from src.utils import format_quantity_with_unit


# ═══════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════

PRIORITE_CONFIG = {
    "haute": {"icon": "🔴", "color": "#dc3545"},
    "moyenne": {"icon": "🟡", "color": "#ffc107"},
    "basse": {"icon": "🟢", "color": "#28a745"}
}


# ═══════════════════════════════════════════════════════════════
# COMPOSANTS INTERNES
# ═══════════════════════════════════════════════════════════════

def _course_card(article: Dict, on_buy: callable, on_delete: callable, key: str):
    """Carte course optimisée"""
    config = PRIORITE_CONFIG[article.get("priorite", "moyenne")]

    with st.container():
        st.markdown(
            f'<div style="border-left: 4px solid {config["color"]}; padding: 0.75rem; '
            f'background: #fff; border-radius: 8px; margin-bottom: 0.5rem;"></div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### {config['icon']} {article['nom']}")
            meta = [
                format_quantity_with_unit(article["quantite"], article["unite"]),
                f"📍 {article.get('rayon', '—')}",
                f"🏬 {article.get('magasin', '—')}"
            ]
            st.caption(" • ".join([m for m in meta if "—" not in m]))

        with col2:
            if article.get("suggere_par_ia"):
                badge("🤖 IA", "#9C27B0")
            if article.get("notes"):
                with st.expander("📝"):
                    st.caption(article["notes"])

        with col3:
            if st.button("✅", key=f"{key}_buy", help="Acheté"):
                on_buy(article["id"])
            if st.button("🗑️", key=f"{key}_del", help="Supprimer"):
                on_delete(article["id"])


# ═══════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_liste():
    """Tab Ma Liste"""
    st.subheader("📋 Ma Liste")

    # Actions rapides
    cols = st.columns(4)
    actions = [
        ("⚡ Stock bas", lambda: _gen_stock_bas()),
        ("📅 Repas", lambda: _gen_repas()),
        ("🗑️ Nettoyer", lambda: _nettoyer()),
        ("🔄 Actualiser", lambda: Cache.invalidate("courses"))
    ]

    for col, (label, action) in zip(cols, actions):
        with col:
            if st.button(label, use_container_width=True):
                action()
                st.rerun()

    st.markdown("---")

    # Charger liste
    liste = courses_service.get_liste_active()

    if not liste:
        empty_state("Liste vide", "🛒", "Ajoute des articles")
        return

    # Stats
    stats = courses_service.get_stats()
    metrics_row([
        {"label": "Total", "value": stats["total_actifs"]},
        {"label": "Prioritaires", "value": stats["prioritaires"]},
        {"label": "IA", "value": stats["part_ia"]}
    ], cols=3)

    st.markdown("---")

    # Affichage par priorité
    for prio in ["haute", "moyenne", "basse"]:
        articles = [a for a in liste if a["priorite"] == prio]
        if not articles:
            continue

        config = PRIORITE_CONFIG[prio]
        with st.expander(
                f"{config['icon']} {prio.capitalize()} ({len(articles)})",
                expanded=(prio == "haute")
        ):
            for idx, article in enumerate(articles):
                _course_card(
                    article,
                    on_buy=lambda aid=article["id"]: _mark_bought(aid),
                    on_delete=lambda aid=article["id"]: courses_service.delete(aid),
                    key=f"c_{idx}"
                )


@handle_errors(show_in_ui=True)
def tab_generation_ia():
    """Tab Génération IA"""
    st.subheader("🤖 Génération IA")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA indisponible")
        return

    with st.form("gen_form"):
        col1, col2 = st.columns(2)

        with col1:
            stock = st.checkbox("📦 Stock bas", value=True)
            repas = st.checkbox("📅 Repas", value=True)

        with col2:
            magasin = st.selectbox("🏬 Magasin", list(MAGASINS_CONFIG.keys()))
            budget = st.number_input("💶 Budget (€)", 10, 500, 100, 10)

        if st.form_submit_button("✨ Générer", type="primary", use_container_width=True):
            _generate_ai_list(stock, repas, magasin, budget)


def tab_ajout():
    """Tab Ajout Manuel"""
    st.subheader("➕ Ajouter")

    fields = {
        "nom": {"type": "text", "label": "Article *", "required": True},
        "quantite": {"type": "number", "label": "Quantité", "default": 1.0, "min": 0.1},
        "unite": {"type": "select", "label": "Unité", "options": ["pcs", "kg", "g", "L", "mL"]},
        "priorite": {"type": "select", "label": "Priorité", "options": ["basse", "moyenne", "haute"]},
        "magasin": {"type": "select", "label": "Magasin", "options": list(MAGASINS_CONFIG.keys())},
        "notes": {"type": "textarea", "label": "Notes", "height": 100}
    }

    with st.form("add_form"):
        data = {}
        col1, col2 = st.columns(2)

        for idx, (name, config) in enumerate(fields.items()):
            with (col1 if idx % 2 == 0 else col2):
                data[name] = form_field(config, "add")

        if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
            if data["nom"]:
                courses_service.ajouter(
                    data["nom"], data["quantite"], data["unite"],
                    data["priorite"], magasin=data["magasin"], notes=data["notes"]
                )
                toast(f"✅ {data['nom']} ajouté", "success")
                Cache.invalidate("courses")
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _gen_stock_bas():
    """Génère depuis stock bas"""
    items = courses_service.generer_depuis_stock_bas()
    if items:
        count = courses_service.ajouter_batch(items)
        toast(f"✅ {count} ajouté(s)", "success")
        Cache.invalidate("courses")


def _gen_repas():
    """Génère depuis repas"""
    items = courses_service.generer_depuis_repas_planifies()
    if items:
        count = courses_service.ajouter_batch(items)
        toast(f"✅ {count} ajouté(s)", "success")
        Cache.invalidate("courses")


def _nettoyer():
    """Nettoie achats anciens"""
    count = courses_service.nettoyer_achetes(7)
    toast(f"🗑️ {count} nettoyé(s)", "success")
    Cache.invalidate("courses")


def _mark_bought(article_id: int):
    """Marque acheté avec modal"""
    modal = Modal(f"buy_{article_id}")

    if modal.is_showing():
        add_stock = st.checkbox("📦 Ajouter au stock", value=True)

        if modal.confirm("✅ Confirmer"):
            courses_service.marquer_achete(article_id, add_stock)
            toast("✅ Acheté", "success")
            Cache.invalidate("courses")
            modal.close()

        modal.cancel()
    else:
        modal.show()


def _generate_ai_list(stock: bool, repas: bool, magasin: str, budget: float):
    """Génère liste IA"""
    agent = get_state().agent_ia
    ai_service = create_courses_ai_service(agent)

    with st.spinner("🤖 Génération..."):
        try:
            articles = []
            if stock:
                articles.extend(courses_service.generer_depuis_stock_bas())
            if repas:
                articles.extend(courses_service.generer_depuis_repas_planifies())

            if not articles:
                st.warning("Aucun article à générer")
                return

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                ai_service.generer_liste_optimisee(
                    articles, magasin,
                    MAGASINS_CONFIG[magasin]["rayons"],
                    budget, {}
                )
            )

            st.session_state.liste_ia = result
            toast("✅ Liste générée", "success")
            st.rerun()

        except Exception as e:
            st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée"""
    st.title("🛒 Courses Intelligentes")
    st.caption("IA • Optimisation • Organisation")

    tab1, tab2, tab3 = st.tabs(["📋 Ma Liste", "🤖 IA", "➕ Ajouter"])

    with tab1:
        tab_liste()

    with tab2:
        tab_generation_ia()

    with tab3:
        tab_ajout()