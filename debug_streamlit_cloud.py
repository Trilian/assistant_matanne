"""
🔍 Script de diagnostic pour vérifier la configuration Streamlit Cloud
Lance avec: streamlit run debug_streamlit_cloud.py
"""

import os
import sys

print("\n" + "="*80)
print("🔍 DIAGNOSTIC STREAMLIT CLOUD - Clé API Mistral")
print("="*80)

# 1. Variables d'environnement
print("\n1️⃣ Variables d'environnement:")
print(f"   SF_PARTNER: {os.getenv('SF_PARTNER')}")
print(f"   HOSTNAME: {os.getenv('HOSTNAME')}")
print(f"   HOME: {os.getenv('HOME')}")
print(f"   USER: {os.getenv('USER')}")

is_cloud = os.getenv("SF_PARTNER") == "streamlit"
print(f"   ➜ STREAMLIT CLOUD DETECTED: {is_cloud}")

# 2. Vérifier MISTRAL_API_KEY directement
print("\n2️⃣ Variable d'environnement MISTRAL_API_KEY:")
mistral_key = os.getenv("MISTRAL_API_KEY")
if mistral_key:
    print(f"   ✅ TROUVÉE: {mistral_key[:20]}...")
else:
    print(f"   ❌ NON TROUVÉE")

# 3. Variables alternatives Streamlit Cloud
print("\n3️⃣ Variables alternatives (Edge cases):")
alt_key = os.getenv("STREAMLIT_SECRETS_MISTRAL_API_KEY")
if alt_key:
    print(f"   ✅ STREAMLIT_SECRETS_MISTRAL_API_KEY: {alt_key[:20]}...")
else:
    print(f"   ❌ STREAMLIT_SECRETS_MISTRAL_API_KEY: non trouvée")

# 4. Vérifier st.secrets
print("\n4️⃣ Streamlit Secrets:")
try:
    import streamlit as st
    
    print(f"   st.secrets type: {type(st.secrets)}")
    print(f"   st.secrets empty?: {len(st.secrets) == 0}")
    
    if hasattr(st.secrets, '__dict__'):
        print(f"   st.secrets.__dict__: {st.secrets.__dict__}")
    
    # Lister toutes les clés
    try:
        keys = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else list(st.secrets)
        print(f"   Clés disponibles: {keys}")
    except Exception as e:
        print(f"   Erreur listing clés: {e}")
    
    # Vérifier structure mistral
    print("\n   Chemin 1: st.secrets.get('mistral')")
    mistral = st.secrets.get("mistral")
    if mistral:
        print(f"      ✅ Trouvé, type: {type(mistral)}")
        if hasattr(mistral, 'get'):
            api_key = mistral.get("api_key")
            if api_key:
                print(f"      ✅ api_key trouvée: {api_key[:20]}...")
            else:
                print(f"      ❌ api_key pas trouvée dans mistral")
        else:
            print(f"      ❓ mistral n'a pas la méthode .get()")
    else:
        print(f"      ❌ 'mistral' pas trouvée")
    
    # Chemin 2: accès direct
    print("\n   Chemin 2: st.secrets['mistral']['api_key']")
    try:
        key = st.secrets["mistral"]["api_key"]
        print(f"      ✅ Trouvée: {key[:20]}...")
    except KeyError as e:
        print(f"      ❌ KeyError: {e}")
    except Exception as e:
        print(f"      ❌ Erreur: {e}")
    
    # Chemin 3: Recherche toutes les clés mistral
    print("\n   Chemin 3: Recherche toutes les clés")
    try:
        for key in st.secrets:
            print(f"      - {key}: {st.secrets[key]}")
    except Exception as e:
        print(f"      ❌ Erreur iteration: {e}")
        
except ImportError:
    print(f"   ❌ Streamlit pas importable")
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 5. Vérifier .env.local
print("\n5️⃣ Fichier .env.local:")
import pathlib
env_file = pathlib.Path("/workspaces/assistant_matanne/.env.local")
if env_file.exists():
    print(f"   ✅ .env.local existe")
    try:
        with open(env_file) as f:
            for line in f:
                if "MISTRAL" in line.upper():
                    print(f"   {line.strip()}")
    except Exception as e:
        print(f"   ❌ Erreur lecture: {e}")
else:
    print(f"   ❌ .env.local n'existe pas")

print("\n" + "="*80)
print("💡 RECOMMANDATIONS:")
print("="*80)
print("""
Si tu es EN STREAMLIT CLOUD:
1. ✅ Vérifie que tu as configuré les secrets ici:
   https://share.streamlit.io/ → Sélectionne ton app → ⚙️ Settings → Secrets
   
2. ✅ Format correct du fichier secrets:
   [mistral]
   api_key = "sk-xxx" (remplace par ta vraie clé)

3. ✅ Redéploie l'app après modification des secrets
   
4. ✅ Attends 30-60 secondes que les changements se propagent

Si tu es EN DEV LOCAL:
1. ✅ Crée un fichier .env.local à la racine du projet
2. ✅ Ajoute: MISTRAL_API_KEY=sk-xxx
3. ✅ Redémarre Streamlit
""")
print("="*80 + "\n")
