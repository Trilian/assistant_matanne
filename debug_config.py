#!/usr/bin/env python
"""Debug script pour vérifier la configuration Streamlit Cloud"""

import streamlit as st
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Debug Config", layout="wide")

st.title("🔍 Debug Configuration")

# ═══════════════════════════════════════════════════════════
# Section 1: Vérifier st.secrets disponible
# ═══════════════════════════════════════════════════════════

st.header("1️⃣ État de st.secrets")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Vérification")
    try:
        has_secrets = hasattr(st, 'secrets')
        st.write(f"✅ hasattr(st, 'secrets'): {has_secrets}")
        
        if has_secrets:
            is_none = st.secrets is None
            st.write(f"✅ st.secrets is not None: {not is_none}")
            
            if not is_none:
                try:
                    secrets_dict = dict(st.secrets)
                    st.write(f"✅ Convertible en dict: True")
                    st.write(f"✅ Nombre de clés: {len(secrets_dict)}")
                except Exception as e:
                    st.error(f"❌ Erreur conversion dict: {e}")
        
    except Exception as e:
        st.error(f"❌ Erreur accès st.secrets: {e}")

with col2:
    st.subheader("Type")
    try:
        st.write(f"Type: `{type(st.secrets)}`")
        st.write(f"Repr: `{repr(st.secrets)[:100]}...`")
    except Exception as e:
        st.error(f"Erreur: {e}")

# ═══════════════════════════════════════════════════════════
# Section 2: Lister toutes les clés
# ═══════════════════════════════════════════════════════════

st.header("2️⃣ Secrets disponibles")

try:
    if hasattr(st, 'secrets') and st.secrets is not None:
        st.json(dict(st.secrets))
    else:
        st.warning("⚠️ Aucun secret chargé")
except Exception as e:
    st.error(f"❌ Erreur listing secrets: {e}")

# ═══════════════════════════════════════════════════════════
# Section 3: Recherche spécifique Mistral
# ═══════════════════════════════════════════════════════════

st.header("3️⃣ Configuration Mistral")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Chemin 1: st.secrets['mistral']['api_key']")
    try:
        mistral = st.secrets.get("mistral")
        if mistral:
            st.success(f"✅ st.secrets['mistral'] trouvé")
            if isinstance(mistral, dict):
                st.write(f"Type: dict avec {len(mistral)} clés")
                st.json(mistral)
                if "api_key" in mistral:
                    api_key = mistral["api_key"]
                    st.success(f"✅ api_key trouvée: {api_key[:20]}...")
                else:
                    st.error("❌ Clé 'api_key' manquante dans [mistral]")
            else:
                st.error(f"❌ st.secrets['mistral'] n'est pas un dict: {type(mistral)}")
        else:
            st.warning("⚠️ st.secrets['mistral'] non trouvée")
    except Exception as e:
        st.error(f"❌ Erreur: {e}")

with col2:
    st.subheader("Chemin 2: Variable d'environnement")
    try:
        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key:
            st.success(f"✅ MISTRAL_API_KEY chargée: {api_key[:20]}...")
        else:
            st.warning("⚠️ MISTRAL_API_KEY non définie")
    except Exception as e:
        st.error(f"❌ Erreur: {e}")

# ═══════════════════════════════════════════════════════════
# Section 4: Test chargement config app
# ═══════════════════════════════════════════════════════════

st.header("4️⃣ Chargement configuration app")

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from src.core.config import obtenir_parametres
    
    config = obtenir_parametres()
    
    st.success("✅ Configuration app chargée!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Info app")
        st.write(f"Nom: {config.APP_NAME}")
        st.write(f"Version: {config.APP_VERSION}")
        st.write(f"Environnement: {config.ENV}")
    
    with col2:
        st.subheader("Mistral")
        st.write(f"Modèle: {config.MISTRAL_MODEL}")
        st.write(f"Timeout: {config.MISTRAL_TIMEOUT}s")
        try:
            api_key = config.MISTRAL_API_KEY
            st.success(f"✅ API Key: {api_key[:20]}...")
        except ValueError as e:
            st.error(f"❌ {e}")
    
except Exception as e:
    st.error(f"❌ Erreur chargement config: {e}")
    import traceback
    st.error(traceback.format_exc())

# ═══════════════════════════════════════════════════════════
# Section 5: Recommandations
# ═══════════════════════════════════════════════════════════

st.header("5️⃣ Recommandations")

st.markdown("""
### Si Mistral ne fonctionne pas:

1. **Vérifiez le format des secrets Streamlit Cloud:**
   ```toml
   [mistral]
   api_key = "sk-xxxxxxxxxxxxx"
   ```
   
2. **Pas de guillemets supplémentaires!**
   ❌ `api_key = "'sk-xxx'"`
   ✅ `api_key = "sk-xxx"`

3. **Après modification des secrets:**
   - Re-déployez l'app
   - Attendez 30 secondes
   - Rafraîchissez la page

4. **Alternative avec variable d'environnement:**
   - Allez dans Settings → Advanced settings
   - Ajoutez: `MISTRAL_API_KEY=sk-xxx`
""")

st.divider()

st.markdown("""
**Debug créé par:** Configuration Manager
**Date:** 2026-01-12
""")


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
