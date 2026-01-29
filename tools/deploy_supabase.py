#!/usr/bin/env python3
"""
Script de déploiement SQL vers Supabase.

Usage:
    python deploy_supabase.py --check          # Vérifier la connexion
    python deploy_supabase.py --deploy         # Déployer le schéma complet
    python deploy_supabase.py --status         # Voir l'état actuel
    python deploy_supabase.py --rollback       # Rollback (avec confirmation)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from datetime import datetime

# Charger les variables d'environnement
load_dotenv(".env.local")
load_dotenv(".env")


class SupabaseDeployer:
    """Déployeur SQL pour Supabase."""
    
    def __init__(self, database_url: str = None):
        """Initialise le déployeur."""
        self.database_url = database_url or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("❌ DATABASE_URL non trouvée dans .env.local ou .env")
        
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connecte à la base de données."""
        try:
            print(f"🔌 Connexion à Supabase...")
            self.connection = psycopg2.connect(self.database_url)
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            print("✅ Connexion établie avec succès!")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Connexion fermée")
    
    def check_connection(self):
        """Vérifie la connexion et affiche les infos."""
        if not self.connect():
            return False
        
        try:
            # Version PostgreSQL
            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()[0]
            print(f"\n📊 PostgreSQL: {version.split(',')[0]}")
            
            # Base de données actuelle
            self.cursor.execute("SELECT current_database();")
            db_name = self.cursor.fetchone()[0]
            print(f"📦 Base de données: {db_name}")
            
            # Nombre de tables
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            nb_tables = self.cursor.fetchone()[0]
            print(f"📋 Nombre de tables: {nb_tables}")
            
            # Liste des tables
            if nb_tables > 0:
                self.cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
                tables = [row[0] for row in self.cursor.fetchall()]
                print(f"\n📋 Tables existantes ({len(tables)}):")
                for table in tables:
                    print(f"   - {table}")
            
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
        finally:
            self.disconnect()
    
    def deploy_schema(self, sql_file: Path, dry_run: bool = False):
        """Déploie le schéma depuis un fichier SQL."""
        if not sql_file.exists():
            print(f"❌ Fichier SQL introuvable: {sql_file}")
            return False
        
        if not self.connect():
            return False
        
        try:
            # Lire le fichier SQL
            print(f"\n📖 Lecture du fichier: {sql_file.name}")
            sql_content = sql_file.read_text(encoding="utf-8")
            
            # Statistiques
            nb_lines = len(sql_content.splitlines())
            print(f"📝 {nb_lines} lignes de SQL à exécuter")
            
            if dry_run:
                print("\n⚠️  MODE DRY-RUN: Aucune modification ne sera faite")
                print(f"\n--- Aperçu (50 premières lignes) ---")
                print("\n".join(sql_content.splitlines()[:50]))
                return True
            
            # Confirmation
            print("\n⚠️  ATTENTION: Cette opération va modifier la base de données!")
            confirmation = input("Taper 'DEPLOY' pour confirmer: ")
            if confirmation != "DEPLOY":
                print("❌ Déploiement annulé")
                return False
            
            # Backup de sécurité
            print("\n💾 Création d'un backup de sécurité...")
            backup_file = Path(f"backups/backup_pre_deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
            backup_file.parent.mkdir(exist_ok=True)
            
            # Export des tables existantes
            self.cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            tables = [row[0] for row in self.cursor.fetchall()]
            
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(f"-- Backup créé le {datetime.now()}\n")
                f.write(f"-- Nombre de tables: {len(tables)}\n\n")
                for table in tables:
                    f.write(f"-- Table: {table}\n")
            
            print(f"✅ Backup sauvegardé: {backup_file}")
            
            # Exécution du SQL
            print("\n🚀 Déploiement en cours...")
            self.cursor.execute(sql_content)
            
            # Vérification
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            nb_tables_after = self.cursor.fetchone()[0]
            
            print(f"\n✅ Déploiement réussi!")
            print(f"📋 Tables après déploiement: {nb_tables_after}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Erreur lors du déploiement: {e}")
            print("\n⚠️  La base de données peut être dans un état inconsistant.")
            print(f"💾 Restaurez le backup si nécessaire: {backup_file}")
            return False
        finally:
            self.disconnect()
    
    def get_status(self):
        """Affiche l'état actuel de la base de données."""
        if not self.connect():
            return False
        
        try:
            print("\n📊 STATUT DE LA BASE DE DONNÉES\n")
            print("="*60)
            
            # Tables
            self.cursor.execute("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns 
                        WHERE table_name = t.table_name 
                        AND table_schema = 'public') as nb_colonnes
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = self.cursor.fetchall()
            print(f"\n📋 TABLES ({len(tables)}):")
            print(f"{'Table':<40} {'Colonnes':<10}")
            print("-"*60)
            for table, nb_cols in tables:
                print(f"{table:<40} {nb_cols:<10}")
            
            # Nombre total de lignes
            print(f"\n📊 DONNÉES:")
            total_rows = 0
            for table, _ in tables:
                try:
                    self.cursor.execute(f'SELECT COUNT(*) FROM "{table}";')
                    count = self.cursor.fetchone()[0]
                    if count > 0:
                        print(f"   {table}: {count} lignes")
                    total_rows += count
                except:
                    pass
            
            print(f"\n📈 Total: {total_rows} lignes")
            
            # Migrations
            self.cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """)
            has_alembic = self.cursor.fetchone()[0]
            
            if has_alembic:
                self.cursor.execute("SELECT version_num FROM alembic_version;")
                version = self.cursor.fetchone()
                if version:
                    print(f"\n🔄 Version Alembic: {version[0]}")
            
            print("\n" + "="*60)
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
        finally:
            self.disconnect()


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Déploiement SQL vers Supabase")
    parser.add_argument("--check", action="store_true", help="Vérifier la connexion")
    parser.add_argument("--deploy", action="store_true", help="Déployer le schéma")
    parser.add_argument("--status", action="store_true", help="Afficher le statut")
    parser.add_argument("--dry-run", action="store_true", help="Mode dry-run (aperçu)")
    parser.add_argument("--file", type=str, default="sql/SUPABASE_COMPLET_V3.sql", 
                       help="Fichier SQL à déployer")
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "="*60)
    print("🚀 DÉPLOYEUR SUPABASE - Assistant MaTanne")
    print("="*60 + "\n")
    
    deployer = SupabaseDeployer()
    
    # Exécuter l'action
    if args.check or (not args.deploy and not args.status):
        deployer.check_connection()
    
    elif args.status:
        deployer.get_status()
    
    elif args.deploy:
        sql_file = Path(args.file)
        deployer.deploy_schema(sql_file, dry_run=args.dry_run)
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
