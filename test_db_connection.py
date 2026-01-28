#!/usr/bin/env python3
"""
Script pour tester et diagnostiquer la connexion Supabase.
"""
import os
from dotenv import load_dotenv
import sys

# Charger les variables d'environnement
load_dotenv(".env.local")
load_dotenv(".env")

print("\n" + "="*70)
print("🔍 DIAGNOSTIC CONNEXION SUPABASE")
print("="*70 + "\n")

# Vérifier DATABASE_URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    print("❌ DATABASE_URL non trouvée dans .env.local ou .env")
    sys.exit(1)

print("✅ DATABASE_URL trouvée")
print(f"\n📋 URL (masquée): {database_url[:30]}...{database_url[-20:]}")

# Parser l'URL
try:
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    
    print(f"\n📊 Détails de connexion:")
    print(f"   Protocole: {parsed.scheme}")
    print(f"   Utilisateur: {parsed.username}")
    print(f"   Mot de passe: {'*' * len(parsed.password) if parsed.password else 'Aucun'}")
    print(f"   Hôte: {parsed.hostname}")
    print(f"   Port: {parsed.port}")
    print(f"   Base: {parsed.path.lstrip('/')}")
    
    # Vérifier le format de l'hôte
    if parsed.hostname:
        if "pooler.supabase.com" in parsed.hostname:
            print(f"\n✅ Utilise le pooler Supabase (recommandé)")
        elif "supabase.co" in parsed.hostname:
            print(f"\n⚠️  Utilise l'ancienne URL Supabase")
        elif parsed.hostname.startswith("db."):
            print(f"\n❌ URL incorrecte: 'db.' n'est pas résolvable")
            print(f"\n💡 Solution:")
            print(f"   Remplacer 'db.{parsed.hostname[3:]}' par:")
            print(f"   'aws-0-eu-central-1.pooler.supabase.com'")
        else:
            print(f"\n⚠️  Format d'hôte inhabituel")
        
        # Vérifier le port
        if parsed.port == 6543:
            print(f"✅ Port 6543 (Connection Pooler)")
        elif parsed.port == 5432:
            print(f"✅ Port 5432 (Connexion directe)")
        else:
            print(f"⚠️  Port inhabituel: {parsed.port}")
    
except Exception as e:
    print(f"❌ Erreur lors du parsing: {e}")
    sys.exit(1)

# Test de connexion
print(f"\n🔌 Test de connexion...")
try:
    import psycopg2
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    
    print(f"✅ CONNEXION RÉUSSIE!")
    print(f"📊 PostgreSQL: {version.split(',')[0]}")
    
except ImportError:
    print(f"⚠️  psycopg2 non installé")
    print(f"   Installation: pip install psycopg2-binary")
except Exception as e:
    print(f"❌ ÉCHEC DE CONNEXION:")
    print(f"   {str(e)}")
    print(f"\n💡 Solutions possibles:")
    print(f"   1. Vérifier que l'URL est correcte dans .env.local")
    print(f"   2. Vérifier que le projet Supabase existe")
    print(f"   3. Vérifier les credentials (user/password)")
    print(f"   4. Vérifier votre connexion internet")
    print(f"   5. Essayer avec le pooler: aws-0-eu-central-1.pooler.supabase.com:6543")

print("\n" + "="*70)
