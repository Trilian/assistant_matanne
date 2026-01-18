#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Unsplash sur Streamlit Cloud
"""

import os
import sys

print("=" * 60)
print("TEST CONFIGURATION UNSPLASH")
print("=" * 60)

# 1. Test os.getenv
print("\n1️⃣  Test os.getenv():")
unsplash_env = os.getenv('UNSPLASH_API_KEY')
print(f"   UNSPLASH_API_KEY via os.getenv: {unsplash_env[:10] if unsplash_env else 'NOT SET'}...")

# 2. Test st.secrets
print("\n2️⃣  Test st.secrets (Streamlit):")
try:
    import streamlit as st
    print(f"   Streamlit importé: ✅")
    
    if hasattr(st, 'secrets'):
        print(f"   st.secrets disponible: ✅")
        
        # Afficher ce qu'il y a dans st.secrets
        try:
            secrets_dict = dict(st.secrets)
            print(f"   Sections dans st.secrets: {list(secrets_dict.keys())}")
            
            # Essayer d'accéder à unsplash
            if 'unsplash' in secrets_dict:
                unsplash = st.secrets.get('unsplash', {})
                print(f"   st.secrets['unsplash']: {unsplash}")
                api_key = unsplash.get('api_key') if isinstance(unsplash, dict) else None
                if api_key:
                    print(f"   ✅ Clé trouvée via st.secrets: {api_key[:10]}...")
                else:
                    print(f"   ❌ Pas de clé dans st.secrets['unsplash']['api_key']")
            else:
                print(f"   ❌ Pas de section 'unsplash' dans st.secrets")
                
        except Exception as e:
            print(f"   Erreur accès st.secrets: {e}")
    else:
        print(f"   st.secrets non disponible ❌")
        
except ImportError as e:
    print(f"   Streamlit non importé: {e}")
except Exception as e:
    print(f"   Erreur: {e}")

# 3. Test la fonction _get_api_key
print("\n3️⃣  Test fonction image_generator._get_api_key():")
try:
    from src.utils.image_generator import _get_api_key, UNSPLASH_API_KEY
    
    key = _get_api_key('UNSPLASH_API_KEY')
    print(f"   _get_api_key('UNSPLASH_API_KEY'): {key[:10] if key else 'NOT SET'}...")
    
    print(f"   UNSPLASH_API_KEY (global): {UNSPLASH_API_KEY[:10] if UNSPLASH_API_KEY else 'NOT SET'}...")
    
except Exception as e:
    print(f"   Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("RÉSUMÉ:")
print("=" * 60)
print("""
✅ Si la clé s'affiche: c'est configuré correctement
❌ Si "NOT SET" s'affiche: 

Sur Streamlit Cloud, vous devez:
1. Aller dans Settings → Secrets
2. Ajouter:
   [unsplash]
   api_key = "votre_clé_ici"
3. Sauvegarder (l'app redémarre)

Localement, vous pouvez utiliser:
export UNSPLASH_API_KEY="votre_clé"
""")
