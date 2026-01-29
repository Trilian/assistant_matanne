#!/usr/bin/env python3
"""Debug script: test ModeleCourses existence and data"""

import sys
import traceback
from sqlalchemy import text, inspect
from src.core.database import obtenir_moteur
from src.core.models import Base, ModeleCourses, ArticleModele
from sqlalchemy.orm import Session

def main():
    """Test database state"""
    print("\n" + "="*60)
    print("DIAGNOSTIC: ModeleCourses et Articles")
    print("="*60)
    
    try:
        engine = obtenir_moteur()
        
        # 1. Check table existence
        print("\n1️⃣ Vérification des tables...")
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        print(f"   Tables trouvées: {all_tables}")
        
        modeles_exists = "modeles_courses" in all_tables
        articles_exists = "articles_modeles" in all_tables
        
        print(f"   ✓ modeles_courses existe: {modeles_exists}")
        print(f"   ✓ articles_modeles existe: {articles_exists}")
        
        if not (modeles_exists and articles_exists):
            print("\n   ❌ TABLES MANQUANTES! Créez les migrations:")
            print("      python manage.py migrate")
            return
        
        # 2. Check modeles data
        print("\n2️⃣ Vérification des données...")
        with Session(engine) as session:
            # Count modeles
            modeles = session.query(ModeleCourses).all()
            print(f"   Modèles trouvés: {len(modeles)}")
            
            if not modeles:
                print("   ❌ AUCUN MODÈLE! Insérez les données de démo:")
                print("      python -c 'from sqlalchemy import text; from src.core.database import get_db_context; exec(open(\"sql/006_add_modeles_courses.sql\").read())'")
                return
            
            # Display modeles
            for m in modeles:
                print(f"\n   📋 {m.nom} (ID: {m.id})")
                print(f"      Articles dans relationship: {len(m.articles)}")
                print(f"      Actif: {m.actif}")
                
                # Check articles in DB
                articles = session.query(ArticleModele).filter_by(modele_id=m.id).all()
                print(f"      Articles dans BD: {len(articles)}")
                
                if articles:
                    for a in articles[:3]:  # Show first 3
                        print(f"        - {a.nom_article} ({a.quantite} {a.unite})")
                    if len(articles) > 3:
                        print(f"        ... et {len(articles)-3} autres")
        
        # 3. Test appliquer_modele
        print("\n3️⃣ Test d'application du modèle...")
        
        with Session(engine) as session:
            first_modele = session.query(ModeleCourses).filter_by(actif=True).first()
            if first_modele:
                print(f"   Test avec modèle: {first_modele.nom} (ID: {first_modele.id})")
                print(f"   Articles dans relationship: {len(first_modele.articles)}")
                
                # Simulate appliquer_modele logic
                print("\n   Simulation appliquer_modele:")
                for i, article_modele in enumerate(first_modele.articles):
                    print(f"     {i+1}. {article_modele.nom_article}")
                    if not article_modele.ingredient:
                        print(f"        ⚠️ ingredient=None (sera créé)")
                    else:
                        print(f"        ✓ ingredient={article_modele.ingredient.nom}")
        
        print("\n✅ DEBUG TERMINÉ - Vérifiez les détails ci-dessus")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
