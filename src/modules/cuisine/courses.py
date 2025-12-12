"""
Module Courses - UI Refactorisée
Version simplifiée : 300 lignes max, logique externalisée
"""
import streamlit as st
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

from src.services.courses.courses_service import courses_service, MAGASINS_CONFIG
from src.services.courses.courses_ai_service import create_courses_ai_service
from src.core.state_manager import StateManager, get_state
from src.ui.components import (
    render_stat_row, render_badge, render_empty_state,
    render_confirmation_dialog, render_toast
)


# ===================================
# CONSTANTES UI
# ===================================

PRIORITE_ICONS = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}
PRIORITE_COLORS = {"haute": "#dc3545", "moyenne": "#ffc107", "basse": "#28a745"}


# ===================================
# COMPOSANTS UI
# ===================================

def render_article_simple(article: Dict, key: str):
    """Affiche un article en mode liste simple"""
    icone_priorite = PRIORITE_ICONS[article["priorite"]]
    icone_ia = "🤖" if article["ia"] else ""

    col1, col2, col3 = st.columns([4, 2, 2])

    with col1:
        st.markdown(f"{icone_priorite} {icone_ia} **{article['nom']}**")
        if article.get("notes"):
            st.caption(article["notes"])

    with col2:
        st.write(f"{article['quantite']:.1f} {article['unite']}")
        if article.get("rayon"):
            st.caption(f"📍 {article['rayon']}")

    with col3:
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            if st.button("✅", key=f"check_{key}", help="Acheté"):
                # Demander confirmation
                if st.session_state.get(f"confirm_buy_{article['id']}", False):
                    # Confirmation active → acheter
                    ajouter_stock = st.session_state.get(f"stock_{key}", True)
                    courses_service.marquer_achete(article['id'], ajouter_stock)
                    del st.session_state[f"confirm_buy_{article['id']}"]
                    render_toast(f"✅ {article['nom']} acheté", "success")
                    st.rerun()
                else:
                    # Premier clic → demander confirmation
                    st.session_state[f"confirm_buy_{article['id']}"] = True
                    st.rerun()

        with col_btn2:
            if st.button("🗑️", key=f"del_{key}", help="Supprimer"):
                courses_service.delete(article['id'])
                render_toast(f"🗑️ {article['nom']} supprimé", "success")
                st.rerun()

    # Modal confirmation achat
    if st.session_state.get(f"confirm_buy_{article['id']}", False):
        with st.container():
            st.info(f"📦 Ajouter **{article['nom']}** au stock ?")
            col_c1, col_c2, col_c3 = st.columns([2, 1, 1])

            with col_c1:
                st.session_state[f"stock_{key}"] = st.checkbox(
                    "Ajouter au stock inventaire",
                    value=True,
                    key=f"stock_chk_{key}"
                )

            with col_c2:
                if st.button("✅ Oui", key=f"yes_{key}", type="primary"):
                    # Déjà géré par le bouton principal
                    pass

            with col_c3:
                if st.button("❌ Non", key=f"no_{key}"):
                    del st.session_state[f"confirm_buy_{article['id']}"]
                    st.rerun()


def render_article_carte_ia(article: Dict, magasin: str, key: str):
    """Affiche un article généré par IA en mode carte"""
    couleur = MAGASINS_CONFIG.get(magasin, {}).get("couleur", "#6c757d")

    with st.container():
        st.markdown(f"""
        <div style="border-left: 4px solid {couleur}; 
                    padding: 1rem; 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    margin-bottom: 0.5rem;">
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])

        with col1:
            icone = PRIORITE_ICONS.get(article.get("priorite", "moyenne"), "⚪")
            st.markdown(f"### {icone} {article['article']}")

            if article.get("conseil"):
                st.info(f"💡 {article['conseil']}")

            st.caption(f"{article['quantite']:.1f} {article['unite']}")

            if article.get("prix_estime"):
                st.caption(f"💶 ~{article['prix_estime']:.2f}€")

        with col2:
            if st.button("➕ Ajouter", key=f"add_{key}", use_container_width=True):
                courses_service.ajouter(
                    nom=article['article'],
                    quantite=article['quantite'],
                    unite=article['unite'],
                    priorite=article.get('priorite', 'moyenne'),
                    rayon=article.get('rayon'),
                    magasin=magasin,
                    ia_suggere=True
                )
                render_toast(f"✅ {article['article']} ajouté", "success")
                st.rerun()

        # Alternatives
        if article.get("alternatives"):
            with st.expander("🔄 Alternatives"):
                for alt in article["alternatives"]:
                    st.write(f"• {alt}")


def render_quick_actions():
    """Barre d'actions rapides"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Stock bas
        suggestions = courses_service.generer_depuis_stock_bas()
        if suggestions and st.button(f"⚡ Stock bas ({len(suggestions)})", use_container_width=True):
            count = courses_service.ajouter_batch(suggestions)
            render_toast(f"✅ {count} articles ajoutés", "success")
            st.rerun()

    with col2:
        # Repas planifiés
        suggestions = courses_service.generer_depuis_repas_planifies()
        if suggestions and st.button(f"📅 Repas ({len(suggestions)})", use_container_width=True):
            count = courses_service.ajouter_batch(suggestions)
            render_toast(f"✅ {count} articles ajoutés", "success")
            st.rerun()

    with col3:
        if st.button("🗑️ Nettoyer", use_container_width=True):
            count = courses_service.nettoyer_achetes(jours=7)
            render_toast(f"🗑️ {count} articles nettoyés", "success")
            st.rerun()

    with col4:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.rerun()


# ===================================
# TABS
# ===================================

def tab_ma_liste():
    """Tab 1: Ma liste active"""
    st.subheader("📋 Ma Liste Active")

    # Actions rapides
    render_quick_actions()
    st.markdown("---")

    # Charger liste
    liste = courses_service.get_liste_active()

    if not liste:
        render_empty_state(
            message="Ta liste est vide",
            icon="🛒",
            action_label="➕ Ajouter un article",
            action_callback=lambda: st.session_state.update({"active_tab": 2})
        )
        return

    # Stats
    stats = courses_service.get_stats()
    stats_data = [
        {"label": "Total", "value": stats["total_actifs"]},
        {"label": "Prioritaires", "value": stats["prioritaires"], "delta_color": "inverse"},
        {"label": "IA", "value": stats["part_ia"]},
    ]
    render_stat_row(stats_data, cols=3)

    st.markdown("---")

    # Afficher par priorité
    for priorite in ["haute", "moyenne", "basse"]:
        articles = [a for a in liste if a["priorite"] == priorite]
        if articles:
            icone = PRIORITE_ICONS[priorite]
            st.markdown(f"### {icone} {priorite.capitalize()} ({len(articles)})")

            for idx, article in enumerate(articles):
                render_article_simple(article, f"{priorite}_{idx}")


def tab_generation_ia():
    """Tab 2: Génération IA"""
    st.subheader("🤖 Génération Automatique")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA non disponible")
        return

    ai_service = create_courses_ai_service(agent)

    with st.form("form_generation"):
        col1, col2 = st.columns(2)

        with col1:
            inclure_stock = st.checkbox("📦 Stock bas", value=True)
            inclure_repas = st.checkbox("📅 Repas planifiés", value=True)

        with col2:
            magasin = st.selectbox("🏬 Magasin", list(MAGASINS_CONFIG.keys()))
            budget = st.number_input("💶 Budget max (€)", 10, 500, 100, 10)

        # Préférences
        with st.expander("⚙️ Préférences"):
            col_pref1, col_pref2 = st.columns(2)
            with col_pref1:
                pref_bio = st.checkbox("🌱 Bio")
                pref_local = st.checkbox("🏘️ Local")
            with col_pref2:
                pref_eco = st.checkbox("💰 Économique")

        generer = st.form_submit_button("✨ Générer", type="primary", use_container_width=True)

    if generer:
        with st.spinner("🤖 L'IA génère ta liste optimisée..."):
            try:
                # Collecter articles de base
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

                preferences = {
                    "bio": pref_bio,
                    "local": pref_local,
                    "economique": pref_eco
                }

                result = loop.run_until_complete(
                    ai_service.generer_liste_optimisee(
                        articles_base,
                        magasin,
                        MAGASINS_CONFIG[magasin]["rayons"],
                        budget,
                        preferences
                    )
                )

                # Sauvegarder résultat
                StateManager.cache_set("liste_ia_generee", result.dict())
                StateManager.cache_set("magasin_ia", magasin)

                render_toast("✅ Liste générée !", "success")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur: {str(e)}")

    # Afficher résultat
    result_data = StateManager.cache_get("liste_ia_generee", ttl=3600)
    if result_data:
        st.markdown("---")
        st.markdown("### 📋 Liste Générée")

        # Budget
        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.metric("Budget estimé", f"{result_data['budget_estime']:.2f}€")
        with col_b2:
            if result_data["depasse_budget"]:
                st.error("⚠️ Dépassement")
            else:
                st.success("✅ OK")
        with col_b3:
            if result_data.get("economies_possibles"):
                st.metric("Économies", f"{result_data['economies_possibles']:.2f}€")

        st.markdown("---")

        # Articles par rayon
        magasin_actif = StateManager.cache_get("magasin_ia") or "Cora"

        for rayon, articles in result_data.get("par_rayon", {}).items():
            with st.expander(f"📍 {rayon} ({len(articles)})", expanded=True):
                for idx, article in enumerate(articles):
                    render_article_carte_ia(article, magasin_actif, f"{rayon}_{idx}")

        # Conseils
        if result_data.get("conseils_globaux"):
            st.markdown("### 💡 Conseils")
            for conseil in result_data["conseils_globaux"]:
                st.info(conseil)

        # Actions
        st.markdown("---")
        col_act1, col_act2 = st.columns(2)

        with col_act1:
            if st.button("✅ Tout ajouter", type="primary", use_container_width=True):
                articles_a_ajouter = []
                for articles_rayon in result_data.get("par_rayon", {}).values():
                    for art in articles_rayon:
                        articles_a_ajouter.append({
                            "nom": art["article"],
                            "quantite": art["quantite"],
                            "unite": art["unite"],
                            "priorite": art.get("priorite", "moyenne"),
                            "rayon": art.get("rayon"),
                            "magasin": magasin_actif,
                            "ia": True
                        })

                count = courses_service.ajouter_batch(articles_a_ajouter)
                StateManager.cache_clear("liste_ia")
                render_toast(f"✅ {count} articles ajoutés !", "success")
                st.balloons()
                st.rerun()

        with col_act2:
            if st.button("🗑️ Annuler", use_container_width=True):
                StateManager.cache_clear("liste_ia")
                st.rerun()


def tab_ajout_manuel():
    """Tab 3: Ajout manuel"""
    st.subheader("➕ Ajouter Manuellement")

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

        notes = st.text_area("Notes (optionnel)", placeholder="Format, marque...")

        if st.form_submit_button("➕ Ajouter", type="primary", use_container_width=True):
            if not nom:
                st.error("Le nom est obligatoire")
            else:
                courses_service.ajouter(
                    nom=nom,
                    quantite=quantite,
                    unite=unite,
                    priorite=priorite,
                    magasin=magasin,
                    notes=notes
                )
                render_toast(f"✅ {nom} ajouté", "success")
                st.rerun()


def tab_historique():
    """Tab 4: Historique & stats"""
    st.subheader("📊 Historique")

    periode = st.selectbox("Période", ["7 jours", "30 jours", "90 jours"], index=1)
    jours = int(periode.split()[0])

    stats = courses_service.get_stats(jours)

    # Métriques
    stats_data = [
        {"label": "Achetés", "value": stats["total_achetes"]},
        {"label": "IA", "value": stats["part_ia_achetes"]},
        {"label": "Moy/semaine", "value": f"{stats['moyenne_semaine']:.1f}"},
    ]
    render_stat_row(stats_data, cols=3)

    st.markdown("---")

    # Top articles
    if stats["articles_frequents"]:
        st.markdown("### 🏆 Top Articles")

        import pandas as pd
        df = pd.DataFrame([
            {"Article": nom, "Achats": count}
            for nom, count in stats["articles_frequents"].items()
        ])

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index("Article"))


# ===================================
# MODULE PRINCIPAL
# ===================================

def app():
    """Point d'entrée du module Courses"""
    st.title("🛒 Courses Intelligentes")
    st.caption("Génération IA, optimisation automatique, organisation par magasins")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Ma Liste",
        "🤖 Génération IA",
        "➕ Ajouter",
        "📊 Historique"
    ])

    with tab1:
        tab_ma_liste()

    with tab2:
        tab_generation_ia()

    with tab3:
        tab_ajout_manuel()

    with tab4:
        tab_historique()