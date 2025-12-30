import streamlit as st
from src.services.courses.courses_service import courses_service
from src.ui import empty_state, toast
from src.core.cache import Cache

def app():
    st.title("🛒 Courses Intelligentes")

    # Charger liste
    liste = courses_service.get_liste_active()

    if not liste:
        empty_state("Liste vide", "🛒")
        return

    # Affichage par priorité
    for prio in ["haute", "moyenne", "basse"]:
        articles = [a for a in liste if a["priorite"] == prio]
        if not articles:
            continue

        icons = {"haute": "🔴", "moyenne": "🟡", "basse": "🟢"}

        with st.expander(f"{icons[prio]} {prio.capitalize()} ({len(articles)})", expanded=(prio == "haute")):
            for article in articles:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{article['nom']}** - {article['quantite']} {article['unite']}")
                with col2:
                    if st.button("✅", key=f"buy_{article['id']}"):
                        toast("✅ Acheté", "success")
                        Cache.invalidate("courses")
                        st.rerun()