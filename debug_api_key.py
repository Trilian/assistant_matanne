#!/usr/bin/env python3
"""Debug du chargement de la clé API Football-Data"""

import os
from pathlib import Path

print("=" * 60)
print("🔍 DEBUG: Chargement clé API Football-Data")
print("=" * 60)

# 1. Vérifier le fichier existe
env_file = Path(".env.local")
print(f"\n1️⃣  Fichier .env.local existe: {env_file.exists()}")
print(f"   Chemin: {env_file.absolute()}")

# 2. Lire le fichier directement
if env_file.exists():
    with open(env_file) as f:
        lines = f.readlines()
    football_lines = [l for l in lines if "FOOTBALL" in l or "football" in l]
    print(f"\n2️⃣  Lignes avec FOOTBALL dans .env.local:")
    for line in football_lines:
        print(f"   {line.strip()}")

# 3. Vérifier la var d'env AVANT import src
env_val = os.getenv("FOOTBALL_DATA_API_KEY")
print(f"\n3️⃣  Variable d'env AVANT import src:")
print(f"   os.getenv('FOOTBALL_DATA_API_KEY'): {env_val[:20] if env_val else None}...")

# 4. Recharger .env
print(f"\n4️⃣  Rechargement .env...")
from src.core.config import _reload_env_files
_reload_env_files()

# 5. Vérifier APRÈS reload
env_val = os.getenv("FOOTBALL_DATA_API_KEY")
print(f"\n5️⃣  Variable d'env APRÈS reload:")
print(f"   os.getenv('FOOTBALL_DATA_API_KEY'): {env_val[:20] if env_val else None}...")

# 6. Vérifier via config
print(f"\n6️⃣  Via config Parametres:")
from src.core.config import obtenir_parametres
config = obtenir_parametres()
if config.FOOTBALL_DATA_API_KEY:
    print(f"   FOOTBALL_DATA_API_KEY: {config.FOOTBALL_DATA_API_KEY[:20]}...")
else:
    print(f"   FOOTBALL_DATA_API_KEY: None")

# 7. Vérifier via api_football
print(f"\n7️⃣  Via api_football.obtenir_cle_api():")
from src.domains.jeux.logic.api_football import obtenir_cle_api
cle = obtenir_cle_api()
if cle:
    print(f"   Clé: {cle[:20]}...")
else:
    print(f"   Clé: None")

print("\n" + "=" * 60)
if cle:
    print("✅ SUCCÈS: Clé chargée correctement!")
else:
    print("❌ ÉCHEC: Clé non trouvée!")
print("=" * 60)
