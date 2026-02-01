"""
Script pour configurer la clé API Football-Data et tester
"""

import os
from pathlib import Path

def ajouter_cle_api():
    """Ajoute une clé API à .env.local"""
    
    env_local = Path(".env.local")
    
    print("=" * 60)
    print("🔧 Configuration API Football-Data.org")
    print("=" * 60)
    print()
    
    print("1️⃣  S'inscrire sur: https://www.football-data.org/client/register")
    print("2️⃣  Obtenir une clé API gratuite (10 req/min)")
    print("3️⃣  La copier ci-dessous")
    print()
    
    api_key = input("🔑 Entrer votre clé API: ").strip()
    
    if not api_key:
        print("❌ Clé vide, annulation")
        return False
    
    # Vérifier si .env.local existe
    contenu = ""
    if env_local.exists():
        with open(env_local, "r") as f:
            contenu = f.read()
    
    # Ajouter ou remplacer la clé
    if "FOOTBALL_DATA_API_KEY=" in contenu:
        lines = contenu.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("FOOTBALL_DATA_API_KEY="):
                lines[i] = f"FOOTBALL_DATA_API_KEY={api_key}"
        contenu = "\n".join(lines)
        print("🔄 Remplacement de la clé API existante...")
    else:
        if contenu and not contenu.endswith("\n"):
            contenu += "\n"
        contenu += f"FOOTBALL_DATA_API_KEY={api_key}\n"
        print("✅ Ajout de la clé API...")
    
    # Écrire dans .env.local
    with open(env_local, "w") as f:
        f.write(contenu)
    
    print(f"✅ Clé API ajoutée à {env_local}")
    print()
    print("🚀 Maintenant, redémarrer Streamlit:")
    print("   streamlit run src/app.py")
    print()
    
    return True

if __name__ == "__main__":
    ajouter_cle_api()
