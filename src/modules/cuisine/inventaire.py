import streamlit as st
from src.services.inventaire.inventaire_service import inventaire_service, CATEGORIES, EMPLACEMENTS
from src.ui import search_bar, empty_state, inventory_card, toast
from src.core.cache import Cache

def app():
    st.title("📦 Inventaire Intelligent")

    tab1, tab2 = st.tabs(["📦 Mon Stock", "➕ Ajouter"])

    with tab1:
        # Charger inventaire
        inventaire = inventaire_service.get_inventaire_complet()

        if not inventaire:
            empty_state("Inventaire vide", "📦")
            return

        # Affichage par statut
        for statut in ["critique", "sous_seuil", "ok"]:
            articles = [a for a in inventaire if a["statut"] == statut]
            if not articles:
                continue

            labels = {"critique": "🔴 Critiques", "sous_seuil": "⚠️ Stock Bas", "ok": "✅ OK"}

            with st.expander(f"{labels[statut]} ({len(articles)})", expanded=(statut == "critique")):
                for article in articles:
                    inventory_card(
                        article,
                        on_adjust=lambda aid, delta: _adjust_stock(aid, delta),
                        key=f"inv_{article['id']}"
                    )

    with tab2:
        st.markdown("### ➕ Ajouter un article")
        st.info("🚧 Formulaire à implémenter")

def _adjust_stock(article_id: int, delta: float):
    # Logique d'ajustement
    toast(f"{'➕' if delta > 0 else '➖'} Stock ajusté", "success")
    Cache.invalidate("inventaire")
    st.rerun()