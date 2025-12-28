"""
Module Inventaire - VERSION 3.0 REFACTORISÉE
Intègre tous les refactoring core/ui/utils
"""
import streamlit as st
import asyncio
from typing import List, Dict, Optional

# ═══════════════════════════════════════════════════════════════
# IMPORTS REFACTORISÉS
# ═══════════════════════════════════════════════════════════════

# Core
from src.core.state import get_state
from src.core.cache import Cache
from src.core.errors import handle_errors
from src.core.database import get_db_context

# UI - Namespace unifié
from src.ui import (
    # Base
    empty_state, badge, progress_bar,
    # Forms
    DynamicList, filter_panel,
    # Data
    metrics_row, export_buttons,
    # Feedback
    toast, Modal,
    # Layouts
    item_card
)

# Services
from src.services.inventaire import (
    inventaire_service,
    CATEGORIES,
    EMPLACEMENTS,
    create_inventaire_ai_service,
    InventaireExporter,
    InventaireImporter
)

# Utils
from src.utils import format_quantity_with_unit, format_date, relative_date


# Constantes UI
STATUT_COLORS = {
    "ok": "#d4edda",
    "sous_seuil": "#fff3cd",
    "peremption_proche": "#f8d7da",
    "critique": "#dc3545",
}


# ═══════════════════════════════════════════════════════════════
# TAB 1 : MON STOCK
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_mon_stock():
    """Tab Mon Stock - VERSION REFACTORISÉE"""
    st.subheader("📦 Mon Stock")

    # ✅ Actions rapides
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⚠️ Stock bas", use_container_width=True):
            st.session_state.filter_stock_bas = True
            st.rerun()

    with col2:
        if st.button("⏳ Péremption", use_container_width=True):
            st.session_state.filter_peremption = True
            st.rerun()

    with col3:
        if st.button("🔄 Tout afficher", use_container_width=True):
            st.session_state.filter_stock_bas = False
            st.session_state.filter_peremption = False
            st.rerun()

    with col4:
        if st.button("🔄 Actualiser", use_container_width=True):
            Cache.invalidate("inventaire")
            st.rerun()

    # ✅ Filtres unifiés
    filters_config = {
        "categorie": {
            "type": "select",
            "label": "Catégorie",
            "options": ["Toutes"] + CATEGORIES,
            "default": 0
        },
        "emplacement": {
            "type": "select",
            "label": "Emplacement",
            "options": ["Tous"] + EMPLACEMENTS,
            "default": 0
        }
    }

    filters = filter_panel(filters_config, "inv")

    # Préparer filtres pour service
    service_filters = {}
    if filters["categorie"] != "Toutes":
        service_filters["categorie"] = filters["categorie"]
    if filters["emplacement"] != "Tous":
        service_filters["emplacement"] = filters["emplacement"]

    st.markdown("---")

    # ✅ Charger inventaire avec cache
    @Cache.cached(ttl=30)
    def load_inventory():
        return inventaire_service.get_inventaire_complet(service_filters)

    inventaire = load_inventory()

    # Appliquer filtres session
    if st.session_state.get("filter_stock_bas"):
        inventaire = [i for i in inventaire if i["statut"] in ["sous_seuil", "critique"]]

    if st.session_state.get("filter_peremption"):
        inventaire = [
            i for i in inventaire
            if i.get("jours_peremption") is not None and i["jours_peremption"] <= 7
        ]

    if not inventaire:
        empty_state(
            message="Inventaire vide",
            icon="📦",
            subtext="Ajoute tes premiers articles"
        )
        return

    # ✅ Stats
    stats = inventaire_service.get_stats()
    metrics_row([
        {"label": "Total", "value": stats["total_articles"]},
        {"label": "Stock bas", "value": stats["total_stock_bas"]},
        {"label": "Péremption", "value": stats["total_peremption"]},
        {"label": "Critiques", "value": stats["total_critiques"]}
    ], cols=4)

    st.markdown("---")

    # ✅ Affichage par statut
    for statut in ["critique", "sous_seuil", "peremption_proche", "ok"]:
        articles = [a for a in inventaire if a["statut"] == statut]

        if not articles:
            continue

        labels = {
            "critique": "🔴 Critiques",
            "sous_seuil": "⚠️ Stock Bas",
            "peremption_proche": "⏳ Péremption Proche",
            "ok": "✅ OK"
        }

        with st.expander(
                f"{labels[statut]} ({len(articles)})",
                expanded=statut in ["critique", "sous_seuil"]
        ):
            for article in articles:
                _render_article_card(article)


def _render_article_card(article: Dict):
    """Carte article avec composant unifié"""
    # Métadonnées
    metadata = [
        f"📍 {article.get('emplacement', '—')}",
        f"📦 {article['categorie']}"
    ]

    # Alert si péremption proche
    alert = None
    if article.get("jours_peremption") is not None:
        jours = article["jours_peremption"]
        if jours <= 3:
            alert = f"⏳ Expire dans {jours} jour(s)"
        elif jours <= 7:
            metadata.append(f"⏳ {jours}j")

    # Tags
    tags = []
    if article["quantite"] < article["seuil"]:
        tags.append("⚠️ Bas")

    # Actions
    actions = [
        ("➕", lambda a=article: _adjust_stock(a["id"], +1)),
        ("➖", lambda a=article: _adjust_stock(a["id"], -1)),
        ("🛒", lambda a=article: _add_to_courses(a["id"])),
        ("🗑️", lambda a=article: _delete_article(a["id"]))
    ]

    # Contenu extensible
    def expandable_content():
        col1, col2 = st.columns(2)

        with col1:
            st.caption("**Stock actuel**")
            current = article["quantite"]
            seuil = article["seuil"]
            progress_bar(current, seuil, show_percentage=False)
            st.caption(f"{format_quantity_with_unit(current, article['unite'])} / {format_quantity_with_unit(seuil, article['unite'])}")

        with col2:
            if article.get("date_peremption"):
                st.caption("**Péremption**")
                st.write(format_date(article["date_peremption"], "medium"))
                st.caption(relative_date(article["date_peremption"]))

    # ✅ Composant unifié
    item_card(
        title=article["nom"],
        metadata=metadata,
        status=article["statut"].replace("_", " ").title(),
        status_color=STATUT_COLORS.get(article["statut"]),
        tags=tags,
        alert=alert,
        actions=actions,
        expandable_content=expandable_content,
        key=f"inv_{article['id']}"
    )


# ═══════════════════════════════════════════════════════════════
# TAB 2 : ANALYSE IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_analyse_ia():
    """Tab Analyse IA"""
    st.subheader("🤖 Analyse Intelligente")

    agent = get_state().agent_ia
    if not agent:
        st.error("❌ Agent IA indisponible")
        return

    ai_service = create_inventaire_ai_service(agent)
    inventaire = inventaire_service.get_inventaire_complet()

    if not inventaire:
        st.info("Inventaire vide")
        return

    # Analyses
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚨 Détecter Gaspillage", use_container_width=True, type="primary"):
            with st.spinner("🤖 Analyse..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        ai_service.detecter_gaspillage(inventaire)
                    )

                    st.session_state.gaspillage_result = result
                    toast("✅ Analyse terminée", "success")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ {str(e)}")

    with col2:
        if st.button("🍽️ Suggérer Recettes", use_container_width=True, type="primary"):
            with st.spinner("🤖 Recherche..."):
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    result = loop.run_until_complete(
                        ai_service.suggerer_recettes_stock(inventaire, nb=5)
                    )

                    st.session_state.recettes_result = result
                    toast("✅ Suggestions prêtes", "success")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ {str(e)}")

    # Afficher résultats
    if hasattr(st.session_state, "gaspillage_result"):
        st.markdown("---")
        st.markdown("### 🚨 Analyse Gaspillage")

        result = st.session_state.gaspillage_result
        st.info(f"**Statut:** {result['statut']}")

        if result.get("recettes_urgentes"):
            st.markdown("**Recettes urgentes:**")
            for r in result["recettes_urgentes"]:
                st.write(f"• {r}")

    if hasattr(st.session_state, "recettes_result"):
        st.markdown("---")
        st.markdown("### 🍽️ Recettes Suggérées")

        for idx, recette in enumerate(st.session_state.recettes_result):
            with st.expander(f"{recette['nom']} - {recette['faisabilite']}%"):
                st.write(f"**Temps:** {recette['temps_total']}min")
                st.write(f"**Ingrédients utilisés:** {', '.join(recette['ingredients_utilises'])}")


# ═══════════════════════════════════════════════════════════════
# TAB 3 : AJOUT (avec DynamicList)
# ═══════════════════════════════════════════════════════════════

def tab_ajout():
    """Tab Ajout avec DynamicList refactorisé"""
    st.subheader("➕ Ajouter Articles")

    # ✅ DynamicList refactorisé
    st.markdown("### 🚀 Ajout Rapide")

    dynamic_list = DynamicList(
        key="inventaire_quick",
        fields=[
            {
                "name": "nom",
                "type": "text",
                "label": "Nom",
                "required": True,
                "placeholder": "Ex: Tomates"
            },
            {
                "name": "categorie",
                "type": "select",
                "label": "Catégorie",
                "options": CATEGORIES,
                "default": 0
            },
            {
                "name": "quantite",
                "type": "number",
                "label": "Quantité",
                "default": 1.0,
                "min": 0.1,
                "step": 0.1
            },
            {
                "name": "unite",
                "type": "select",
                "label": "Unité",
                "options": ["pcs", "kg", "g", "L", "mL", "sachets", "boîtes"],
                "default": 0
            },
            {
                "name": "emplacement",
                "type": "select",
                "label": "Emplacement",
                "options": EMPLACEMENTS,
                "default": 0
            }
        ],
        add_label="➕ Ajouter"
    )

    items = dynamic_list.render()

    # Bouton validation
    if items and st.button(
            f"✅ Valider {len(items)} article(s)",
            type="primary",
            use_container_width=True
    ):
        count = 0
        for item in items:
            try:
                inventaire_service.ajouter_ou_modifier(
                    nom=item["nom"],
                    categorie=item["categorie"],
                    quantite=item["quantite"],
                    unite=item["unite"],
                    seuil=1.0,
                    emplacement=item["emplacement"]
                )
                count += 1
            except Exception as e:
                st.error(f"Erreur {item['nom']}: {e}")

        if count > 0:
            st.session_state["inventaire_quick_items"] = []
            toast(f"✅ {count} ajouté(s)", "success")
            Cache.invalidate("inventaire")
            st.balloons()
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# TAB 4 : IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════════

def tab_import_export():
    """Tab Import/Export"""
    st.subheader("📤 Import/Export")

    tab_exp, tab_imp = st.tabs(["📤 Export", "📥 Import"])

    with tab_exp:
        inventaire = inventaire_service.get_inventaire_complet()

        if not inventaire:
            st.info("Inventaire vide")
        else:
            st.info(f"💡 {len(inventaire)} article(s)")

            # ✅ Export buttons refactorisé
            export_buttons(
                data=inventaire,
                filename="inventaire",
                formats=["csv", "json"],
                key="inv_export"
            )

    with tab_imp:
        st.markdown("### Importer")
        uploaded = st.file_uploader("Fichier CSV", type=["csv"])

        if uploaded:
            try:
                content = uploaded.read().decode("utf-8")
                articles, errors = InventaireImporter.from_csv(content)

                if errors:
                    with st.expander("⚠️ Erreurs"):
                        for error in errors:
                            st.warning(error)

                if articles:
                    st.success(f"✅ {len(articles)} article(s)")

                    if st.button("➕ Importer", type="primary"):
                        count = 0
                        for art in articles:
                            try:
                                inventaire_service.ajouter_ou_modifier(**art)
                                count += 1
                            except:
                                pass

                        toast(f"✅ {count} importé(s)", "success")
                        Cache.invalidate("inventaire")
                        st.balloons()
                        st.rerun()

            except Exception as e:
                st.error(f"❌ {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _adjust_stock(article_id: int, delta: float):
    """Ajuste le stock"""
    try:
        inventaire_service.ajuster_quantite(article_id, delta)
        toast(f"{'➕' if delta > 0 else '➖'} Stock ajusté", "success")
        Cache.invalidate("inventaire")
        st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)}")


def _add_to_courses(article_id: int):
    """Ajoute aux courses"""
    try:
        inventaire_service.ajouter_a_courses(article_id)
        toast("✅ Ajouté aux courses", "success")
        st.rerun()
    except Exception as e:
        st.error(f"❌ {str(e)}")


def _delete_article(article_id: int):
    """Supprime un article"""
    modal = Modal(f"delete_inv_{article_id}")

    if st.button("🗑️", key=f"del_{article_id}"):
        modal.show()

    if modal.is_showing():
        st.warning("Supprimer cet article ?")

        if modal.confirm():
            try:
                inventaire_service.delete(article_id)
                toast("🗑️ Supprimé", "success")
                Cache.invalidate("inventaire")
                modal.close()
            except Exception as e:
                st.error(f"❌ {str(e)}")

        modal.cancel()


# ═══════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée - VERSION REFACTORISÉE"""
    st.title("📦 Inventaire Intelligent")
    st.caption("Alertes • Prédictions IA • Gestion complète")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Mon Stock",
        "🤖 Analyse IA",
        "➕ Ajouter",
        "📤 Import/Export"
    ])

    with tab1:
        tab_mon_stock()

    with tab2:
        tab_analyse_ia()

    with tab3:
        tab_ajout()

    with tab4:
        tab_import_export()