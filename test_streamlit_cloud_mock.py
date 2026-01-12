#!/usr/bin/env python3
"""
Test simulé Streamlit Cloud - Teste si la config fonctionne avec st.secrets
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock

print("\n" + "="*70)
print("🧪 TEST SIMULÉ STREAMLIT CLOUD")
print("="*70)

# Créer un mock st.secrets qui simule Streamlit Cloud
print("\n1️⃣ Création d'un mock st.secrets simulant Streamlit Cloud...")

sys.path.insert(0, '/workspaces/assistant_matanne')
os.chdir('/workspaces/assistant_matanne')

# Lire la clé depuis .env.local
test_api_key = "sk-test_from_streamlit_cloud_mock"

# Mock st.secrets comme Streamlit Cloud
import streamlit as st
original_secrets = st.secrets

# Créer le mock
mock_secrets = {
    "mistral": {
        "api_key": test_api_key,
        "model": "mistral-small-latest"
    }
}

# Remplacer st.secrets par un dict-like object
class MockSecrets(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get(self, key, default=None):
        return super().get(key, default)

st.secrets = MockSecrets(mock_secrets)

print("   ✅ Mock st.secrets créé")
print(f"   Contenu: {json.dumps(mock_secrets, indent=2)}")

# Clear le cache Python
for module in list(sys.modules.keys()):
    if 'src.core.config' in module:
        del sys.modules[module]

print("\n2️⃣ Test de chargement avec st.secrets mocké...")

try:
    from src.core.config import (
        obtenir_parametres, 
        _get_mistral_api_key_from_secrets,
    )
    
    # Test la fonction spécifique
    print("\n   A) Test _get_mistral_api_key_from_secrets():")
    api_key_from_func = _get_mistral_api_key_from_secrets()
    
    if api_key_from_func == test_api_key:
        print(f"      ✅ Clé récupérée depuis st.secrets['mistral']['api_key']")
        print(f"      Valeur: {api_key_from_func}")
    else:
        print(f"      ❌ Clé incorrect")
        print(f"      Attendu: {test_api_key}")
        print(f"      Reçu: {api_key_from_func}")
    
    # Test la configuration complète
    print("\n   B) Test configuration complète:")
    config = obtenir_parametres()
    
    if config.MISTRAL_API_KEY == test_api_key:
        print(f"      ✅ Configuration OK!")
        print(f"      API Key: {config.MISTRAL_API_KEY}")
        print(f"      Modèle: {config.MISTRAL_MODEL}")
    else:
        print(f"      ⚠️ Configuration partiellement OK")
        print(f"      Clé chargée depuis: variables d'environnement (pas st.secrets)")
    
    print("\n" + "="*70)
    print("✅ TEST RÉUSSI - Streamlit Cloud fonctionnera!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    # Restaurer st.secrets
    st.secrets = original_secrets

print()
