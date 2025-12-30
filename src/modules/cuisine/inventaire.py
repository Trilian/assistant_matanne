"""
Module Inventaire - VERSION AGRESSIVE REFACTORISÉE
"""
import streamlit as st
import asyncio
from typing import Dict, List

# Core
from src.core.state import get_state
from src.core.cache import Cache
from src.core.errors import handle_errors

# UI Composants Domaine
from src.ui.domain import (
    inventory_card,
    stock_alert,
    inventory_stats,
    inventory_filters,
    quick_add_form
)

# UI Composants Génériques
from src.ui import empty_state, toast, export_buttons

# Services
from src.services.inventaire import (
    inventaire_service,
    CATEGORIES,
    EMPLACEMENTS,
    create_inventaire_ai_service,
    InventaireExporter,
    InventaireImporter
)


# ═══════════════════════════════════════════════════════════════
# TAB 1 : MON STOCK
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_stock():
    """Tab Mon Stock"""
    st.subheader("📦 Mon Stock")

    # Actions rapides
    cols = st.columns(4)
    actions = [
        ("⚠️ Stock bas", lambda: _set_filter("stock_bas")),
        ("⏳ Péremption", lambda: _set_filter("peremption")),
        ("🔄 Tout", lambda: _clear_filters()),
        ("🔄 Actualiser", lambda: Cache.invalidate("inventaire"))
    ]

    for col, (label, action) in zip(cols, actions):
        with col:
            if st.button(label, use_container_width=True):
                action()
                st.rerun()

    # Filtres
    filters = inventory_filters(
        CATEGORIES,
        EMPLACEMENTS,
        on_filter=lambda f: _apply_filters(f),
        key="inv_filters"
    )

    st.markdown("---")

    # Charger inventaire
    inventaire = _load_filtered_inventory(filters)

    if not inventaire:
        empty_state("Inventaire vide", "📦", "Ajoute tes premiers articles")
        return

    # Stats
    stats = inventaire_service.get_stats()
    inventory_stats(stats)

    st.markdown("---")

    # Alertes critiques
    critiques = [a for a in inventaire if a["statut"] == "critique"]
    if critiques:
        stock_alert(critiques, on_click=lambda aid: st.info(f"Article {aid}"))
        st.markdown("---")

    # Affichage par statut
    for statut in ["critique", "sous_seuil", "peremption_proche", "ok"]:
        articles = [a for a in inventaire if a["statut"] == statut]
        if not articles:
            continue

        labels = {
            "critique": "🔴 Critiques",
            "sous_seuil": "⚠️ Stock Bas",
            "peremption_proche": "⏳ Péremption",
            "ok": "✅ OK"
        }

        with st.expander(
                f"{labels[statut]} ({len(articles)})",
                expanded=(statut in ["critique", "sous_seuil"])
        ):
            for article in articles:
                inventory_card(
                    article,
                    on_adjust=lambda aid, delta: _adjust_stock(aid, delta),
                    on_add_to_cart=lambda aid: _add_to_courses(aid),
                    on_delete=lambda aid: _delete_article(aid),
                    key=f"inv_{article['id']}"
                )


# ═══════════════════════════════════════════════════════════════
# TAB 2 : ANALYSE IA
# ═══════════════════════════════════════════════════════════════

@handle_errors(show_in_ui=True)
def tab_analyse():
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
        if st.button("🚨 Détecter Gaspillage", type="primary", use_container_width=True):
            _run_gaspillage_analysis(ai_service, inventaire)

    with col2:
        if st.button("🍽️ Suggérer Recettes", type="primary", use_container_width=True):
            _run_recettes_suggestions(ai_service, inventaire)

    # Afficher résultats
    _display_analysis_results()


# ═══════════════════════════════════════════════════════════════
# TAB 3 : AJOUT
# ═══════════════════════════════════════════════════════════════

def tab_ajout():
    """Tab Ajout"""
    st.subheader("➕ Ajouter Articles")

    quick_add_form(
        CATEGORIES,
        EMPLACEMENTS,
        on_submit=lambda data: _add_article(data),
        key="quick_add"
    )


# ═══════════════════════════════════════════════════════════════
# TAB 4 : IMPORT/EXPORT
# ═══════════════════════════════════════════════════════════════

def tab_import_export():
    """Tab Import/Export"""
    st.subheader("📤 Import/Export")

    tab_exp, tab_imp = st.tabs(["📤 Export", "📥 Import"])

    with tab_exp:
        inventaire = inventaire_service.get_inventaire_complet()

        if inventaire:
            st.info(f"💡 {len(inventaire)} article(s)")
            export_buttons(inventaire, "inventaire", ["csv", "json"], "inv_export")
        else:
            st.info("Inventaire vide")

    with tab_imp:
        uploaded = st.file_uploader("Fichier CSV", type=["csv"])

        if uploaded:
            _import_csv(uploaded)


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _load_filtered_inventory(filters: Dict) -> List[Dict]:
    """Charge inventaire avec filtres session"""
    # Filtres UI
    service_filters = {
        k: v for k, v in filters.items()
        if v is not None and k in ["categorie", "emplacement", "statut"]
    }

    inventaire = inventaire_service.get_inventaire_complet(service_filters)

    # Filtres session
    if st.session_state.get("filter_stock_bas"):
        inventaire = [i for i in inventaire if i["statut"] in ["sous_seuil", "critique"]]

    if st.session_state.get("filter_peremption"):
        inventaire = [
            i for i in inventaire
            if i.get("jours_peremption") is not None and i["jours_peremption"] <= 7
        ]

    return inventaire


def _set_filter(filter_name: str):
    """Active un filtre"""
    st.session_state[f"filter_{filter_name}"] = True


def _clear_filters():
    """Vide tous les filtres"""
    st.session_state["filter_stock_bas"] = False
    st.session_state["filter_peremption"] = False


def _apply_filters(filters: Dict):
    """Applique filtres (callback)"""
    Cache.invalidate("inventaire")


def _adjust_stock(article_id: int, delta: float):
    """Ajuste quantité"""
    inventaire_service.ajuster_quantite(article_id, delta)
    toast(f"{'➕' if delta > 0 else '➖'} Stock ajusté", "success")
    Cache.invalidate("inventaire")
    st.rerun()


def _add_to_courses(article_id: int):
    """Ajoute aux courses"""
    inventaire_service.ajouter_a_courses(article_id)
    toast("✅ Ajouté aux courses", "success")


def _delete_article(article_id: int):
    """Supprime article"""
    if st.button(f"Confirmer suppression ?", key=f"confirm_del_{article_id}"):
        inventaire_service.delete(article_id)
        toast("🗑️ Supprimé", "success")
        Cache.invalidate("inventaire")
        st.rerun()


def _add_article(data: Dict):
    """Ajoute article"""
    inventaire_service.ajouter_ou_modifier(
        nom=data["nom"],
        categorie=data["categorie"],
        quantite=data["quantite"],
        unite=data["unite"],
        seuil=data["seuil"],
        emplacement=data["emplacement"],
        date_peremption=data.get("date_peremption")
    )
    toast(f"✅ {data['nom']} ajouté", "success")
    Cache.invalidate("inventaire")
    st.rerun()


def _run_gaspillage_analysis(ai_service, inventaire: List[Dict]):
    """Lance analyse gaspillage"""
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


def _run_recettes_suggestions(ai_service, inventaire: List[Dict]):
    """Lance suggestions recettes"""
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


def _display_analysis_results():
    """Affiche résultats analyses"""
    # Gaspillage
    if hasattr(st.session_state, "gaspillage_result"):
        st.markdown("---")
        st.markdown("### 🚨 Gaspillage")
        result = st.session_state.gaspillage_result
        st.info(f"**Statut:** {result.statut}")

        if result.recettes_urgentes:
            st.markdown("**Recettes urgentes:**")
            for r in result.recettes_urgentes:
                st.write(f"• {r}")

    # Recettes
    if hasattr(st.session_state, "recettes_result"):
        st.markdown("---")
        st.markdown("### 🍽️ Recettes Suggérées")

        for recette in st.session_state.recettes_result:
            with st.expander(f"{recette.nom} - {recette.faisabilite}%"):
                st.write(f"⏱️ {recette.temps_total}min")
                st.write(f"📦 {', '.join(recette.ingredients_utilises)}")
                st.caption(recette.raison)


def _import_csv(uploaded):
    """Import CSV"""
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
# MAIN
# ═══════════════════════════════════════════════════════════════

def app():
    """Point d'entrée"""
    st.title("📦 Inventaire Intelligent")
    st.caption("Alertes • Prédictions IA • Gestion complète")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 Mon Stock",
        "🤖 Analyse IA",
        "➕ Ajouter",
        "📤 Import/Export"
    ])

    with tab1:
        tab_stock()

    with tab2:
        tab_analyse()

    with tab3:
        tab_ajout()

    with tab4:
        tab_import_export()