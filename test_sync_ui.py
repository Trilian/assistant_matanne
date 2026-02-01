"""
Script de test des fonctions sync - À lancer avec streamlit run
"""

import streamlit as st
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="🧪 Test Sync", layout="wide")

st.title("🧪 Test Sync Équipes & Refresh Scores")

# Importer les fonctions
from src.domains.jeux.ui.paris import (
    sync_equipes_depuis_api,
    sync_tous_championnats,
    refresh_scores_matchs,
    CHAMPIONNATS
)

from src.domains.jeux.logic.api_football import obtenir_cle_api

# ════════════════════════════════════════════════════════════
# INFO API
# ════════════════════════════════════════════════════════════

st.subheader("1️⃣ État de l'API")
cle_api = obtenir_cle_api()
if cle_api:
    st.success(f"✅ Clé API configurée: {cle_api[:10]}...") 
else:
    st.error("❌ Clé API Football-Data non configurée")
    st.info("💡 Configurer `FOOTBALL_DATA_API_KEY` dans `.env`")

# ════════════════════════════════════════════════════════════
# TEST SYNC UN CHAMPIONNAT
# ════════════════════════════════════════════════════════════

st.subheader("2️⃣ Test Sync Un Championnat")
col1, col2 = st.columns([2, 1])

with col1:
    champ_test = st.selectbox("Championnat à tester:", CHAMPIONNATS)
with col2:
    if st.button("🧪 Test Sync"):
        st.info(f"Tentative de sync: {champ_test}")
        logger.info(f"🧪 TEST SYNC: {champ_test}")
        try:
            result = sync_equipes_depuis_api(champ_test)
            st.success(f"✅ Résultat: {result} équipes synchronisées")
            st.write(f"Code retour: {result}")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            import traceback
            st.error(traceback.format_exc())

# ════════════════════════════════════════════════════════════
# TEST SYNC TOUS LES CHAMPIONNATS
# ════════════════════════════════════════════════════════════

st.subheader("3️⃣ Test Sync Tous les Championnats")
if st.button("🧪 Test Sync Tous"):
    with st.spinner("Synchronisation en cours..."):
        logger.info(f"🧪 TEST SYNC TOUS")
        try:
            resultats = sync_tous_championnats()
            st.json(resultats)
            total = sum(resultats.values())
            st.success(f"✅ Total: {total} équipes synchronisées")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            import traceback
            st.error(traceback.format_exc())

# ════════════════════════════════════════════════════════════
# TEST REFRESH SCORES
# ════════════════════════════════════════════════════════════

st.subheader("4️⃣ Test Refresh Scores")
if st.button("🧪 Test Refresh"):
    with st.spinner("Actualisation des scores..."):
        logger.info(f"🧪 TEST REFRESH SCORES")
        try:
            result = refresh_scores_matchs()
            st.success(f"✅ Résultat: {result} matchs trouvés")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")
            import traceback
            st.error(traceback.format_exc())

# ════════════════════════════════════════════════════════════
# LOGS
# ════════════════════════════════════════════════════════════

st.subheader("📋 Infos de Débogage")
st.write(f"Championnats configurés: {CHAMPIONNATS}")
st.info("💡 Regardez la console/terminal pour les logs détaillés")
