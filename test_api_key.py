#!/usr/bin/env python3
"""
Test rapide - Vérifier si la clé API Mistral est valide
"""

import os
import sys
from pathlib import Path

print("\n" + "="*70)
print("🧪 TEST CLÉS API MISTRAL - VALIDATION")
print("="*70 + "\n")

# Charger .env.local
env_path = Path(".env.local")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if not os.getenv(key):
                    os.environ[key] = value

sys.path.insert(0, '/workspaces/assistant_matanne')
os.chdir('/workspaces/assistant_matanne')

# Charger config
from src.core.config import obtenir_parametres

try:
    config = obtenir_parametres()
    api_key = config.MISTRAL_API_KEY
    
    print(f"✅ Clé API chargée:")
    print(f"   Longueur: {len(api_key)} caractères")
    print(f"   Début: {api_key[:10]}...")
    print(f"   Fin: ...{api_key[-10:]}")
    print(f"   Modèle: {config.MISTRAL_MODEL}")
    
    # Vérifier la validité basique
    if len(api_key) < 10:
        print(f"\n⚠️  ATTENTION: Clé API très courte ({len(api_key)} chars)")
        print(f"   Les clés Mistral font généralement 30+ caractères")
    
    if api_key.startswith("votre_clé"):
        print(f"\n❌ ERREUR: Tu utilises encore la valeur placeholder!")
        print(f"   Remplace 'votre_clé_api_mistral_ici' par ta VRAIE clé")
    else:
        print(f"\n✅ Clé API semble valide")
        print(f"\n2️⃣ PROCHAINE ÉTAPE:")
        print(f"   Teste sur Streamlit Cloud:")
        print(f"   1. Settings → Secrets")
        print(f"   2. Ajoute: [mistral]")
        print(f"   3. api_key = \"{api_key}\"")
        print(f"   4. Save")
        print(f"   5. Attends 60 secondes")
        print(f"   6. Redéploie l'app (ou rafraîchis)")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70 + "\n")
