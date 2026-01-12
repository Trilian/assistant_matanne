#!/usr/bin/env python
"""Debug script pour vérifier la configuration Streamlit Cloud"""

import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Debug Config", layout="wide")

st.title("🔍 Debug Configuration")

# ═══════════════════════════════════════════════════════════
# Section 1: Secrets Streamlit
# ═══════════════════════════════════════════════════════════

st.header("1️⃣ Secrets Streamlit")

try:
    if hasattr(st, 'secrets'):
        st.success("✅ st.secrets disponible")
        
        # Afficher toutes les sections
        try:
            sections = dict(st.secrets)
            st.json(sections)
            
            # Vérifier mistral spécifiquement
            if 'mistral' in st.secrets:
                st.success("✅ Section [mistral] trouvée")
                mistral_config = dict(st.secrets['mistral'])
                if 'api_key' in mistral_config:
                    api_key = mistral_config['api_key']
                    st.success(f"✅ api_key trouvée: {api_key[:20]}...")
                else:
                    st.error("❌ api_key manquante dans [mistral]")
            else:
                st.warning("⚠️ Section [mistral] non trouvée")
                
        except Exception as e:
            st.error(f"Erreur lecture secrets: {e}")
    else:
        st.error("❌ st.secrets non disponible")
except Exception as e:
    st.error(f"❌ Erreur: {e}")

# ═══════════════════════════════════════════════════════════
# Section 2: Config du projet
# ═══════════════════════════════════════════════════════════

st.header("2️⃣ Configuration du projet")

try:
    from src.core.config import obtenir_parametres
    config = obtenir_parametres()
    
    st.success("✅ Config chargée")
    
    try:
        api_key = config.MISTRAL_API_KEY
        st.success(f"✅ MISTRAL_API_KEY: {api_key[:20]}...")
    except ValueError as e:
        st.error(f"❌ MISTRAL_API_KEY: {e}")
        
    try:
        model = config.MISTRAL_MODEL
        st.info(f"📦 MISTRAL_MODEL: {model}")
    except:
        pass
        
except Exception as e:
    st.error(f"Erreur config: {e}")

# ═══════════════════════════════════════════════════════════
# Section 3: Client IA
# ═══════════════════════════════════════════════════════════

st.header("3️⃣ Client IA")

try:
    from src.core.ai.client import obtenir_client_ia
    client = obtenir_client_ia()
    
    if client is None:
        st.error("❌ Client IA = None (clé API non disponible)")
    elif client.cle_api is None:
        st.error("❌ Client IA cle_api = None")
    else:
        st.success(f"✅ Client IA disponible (modèle: {client.modele})")
        
except Exception as e:
    st.error(f"Erreur client IA: {e}")

st.markdown("---")
st.info("Copie cette page pour diagnostiquer les problèmes de configuration")
