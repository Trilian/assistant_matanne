#!/usr/bin/env python3
"""
Script pour ajouter la colonne magasin manquante à family_budgets
"""

import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
project_root = Path(__file__).parent
load_dotenv(project_root / ".env.local")
load_dotenv(project_root / ".env")

# Connexion PostgreSQL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found in environment variables")
    exit(1)

try:
    # Parser la URL
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/')
    )
    
    cursor = conn.cursor()
    
    # Vérifier si la colonne existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'family_budgets' AND column_name = 'magasin'
        )
    """)
    
    column_exists = cursor.fetchone()[0]
    
    if column_exists:
        print("✅ Colonne 'magasin' existe déjà dans family_budgets")
    else:
        print("➕ Ajout de la colonne 'magasin' à family_budgets...")
        cursor.execute("""
            ALTER TABLE family_budgets
            ADD COLUMN magasin VARCHAR(200) NULL
        """)
        conn.commit()
        print("✅ Colonne 'magasin' ajoutée avec succès!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    exit(1)
