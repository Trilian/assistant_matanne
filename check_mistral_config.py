#!/usr/bin/env python3
"""
Script de vérification rapide - Configure-t-on Mistral correctement?
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("🔍 VÉRIFICATION CONFIGURATION MISTRAL API")
print("="*70 + "\n")

# 1. Vérifier les fichiers
print("📁 FICHIERS DE CONFIGURATION:")
files_status = {
    ".env.local": Path(".env.local").exists(),
    ".env": Path(".env").exists(),
    ".streamlit/secrets.toml": Path(".streamlit/secrets.toml").exists(),
}

for file_name, exists in files_status.items():
    status = "✅" if exists else "❌"
    print(f"   {status} {file_name}")

# 2. Vérifier les variables d'environnement
print("\n🔐 VARIABLES D'ENVIRONNEMENT:")
api_key = os.getenv("MISTRAL_API_KEY")
if api_key:
    print(f"   ✅ MISTRAL_API_KEY: {api_key[:25]}...")
else:
    print(f"   ❌ MISTRAL_API_KEY: NON TROUVÉE")

# 3. Charger la config
print("\n⚙️  CHARGEMENT CONFIGURATION:")
try:
    from src.core.config import obtenir_parametres
    config = obtenir_parametres()
    print(f"   ✅ Configuration chargée")
    print(f"      • Modèle: {config.MISTRAL_MODEL}")
    print(f"      • API Key présente: {bool(config.MISTRAL_API_KEY)}")
    print(f"      • Timeout: {config.MISTRAL_TIMEOUT}s")
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    sys.exit(1)

# 4. Résumé
print("\n" + "="*70)
if api_key and config.MISTRAL_API_KEY:
    print("✅ CONFIGURATION OK - Mistral est prêt à être utilisé!")
else:
    print("❌ CONFIGURATION INCOMPLÈTE - Voir MISTRAL_CONFIG_GUIDE.md")
print("="*70 + "\n")
