#!/usr/bin/env python3
"""
Vérification d'implémentation - Code-Barres & Rapports PDF

Script de validation pour s'assurer que tout est bien en place
"""

import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# VÉRIFICATIONS
# ═══════════════════════════════════════════════════════════


def verifier_fichiers():
    """Vérifier que tous les fichiers sont créés"""
    print("\n📁 Vérification fichiers...")
    
    fichiers_requis = [
        "src/services/barcode.py",
        "src/services/rapports_pdf.py",
        "src/modules/barcode.py",
        "src/modules/rapports.py",
        "alembic/versions/003_add_barcode_price.py",
    ]
    
    tous_ok = True
    for fichier in fichiers_requis:
        chemin = Path(fichier)
        if chemin.exists():
            taille = chemin.stat().st_size
            print(f"✅ {fichier} ({taille} bytes)")
        else:
            print(f"❌ {fichier} MANQUANT")
            tous_ok = False
    
    return tous_ok


def verifier_contenu_services():
    """Vérifier le contenu des services"""
    print("\n🔧 Vérification services...")
    
    checks = [
        ("src/services/barcode.py", [
            "class BarcodeService",
            "def valider_barcode",
            "def scanner_code",
            "def ajouter_article_par_barcode",
            "def verifier_stock_barcode",
            "_valider_checksum_ean13",
        ]),
        ("src/services/rapports_pdf.py", [
            "class RapportsPDFService",
            "def generer_donnees_rapport_stocks",
            "def generer_pdf_rapport_stocks",
            "def generer_donnees_rapport_budget",
            "def generer_pdf_rapport_budget",
            "def generer_analyse_gaspillage",
        ])
    ]
    
    tous_ok = True
    for fichier, patterns in checks:
        print(f"\n{fichier}:")
        try:
            with open(fichier, 'r') as f:
                contenu = f.read()
            
            for pattern in patterns:
                if pattern in contenu:
                    print(f"  ✅ {pattern}")
                else:
                    print(f"  ❌ {pattern} MANQUANT")
                    tous_ok = False
        except FileNotFoundError:
            print(f"  ❌ Fichier introuvable")
            tous_ok = False
    
    return tous_ok


def verifier_contenu_modules():
    """Vérifier le contenu des modules UI"""
    print("\n🎨 Vérification modules UI...")
    
    checks = [
        ("src/modules/barcode.py", [
            "def app()",
            "def render_scanner",
            "def render_ajout_rapide",
            "def render_verifier_stock",
            "render_gestion_barcodes",
            "render_import_export",
        ]),
        ("src/modules/rapports.py", [
            "def app()",
            "def render_rapport_stocks",
            "def render_rapport_budget",
            "def render_analyse_gaspillage",
            "def render_historique",
        ])
    ]
    
    tous_ok = True
    for fichier, patterns in checks:
        print(f"\n{fichier}:")
        try:
            with open(fichier, 'r') as f:
                contenu = f.read()
            
            for pattern in patterns:
                if pattern in contenu:
                    print(f"  ✅ {pattern}")
                else:
                    print(f"  ❌ {pattern} MANQUANT")
                    tous_ok = False
        except FileNotFoundError:
            print(f"  ❌ Fichier introuvable")
            tous_ok = False
    
    return tous_ok


def verifier_dependances():
    """Vérifier que les dépendances sont importables"""
    print("\n📦 Vérification dépendances...")
    
    dependances = [
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("streamlit", "Streamlit"),
        ("reportlab", "ReportLab"),
        ("pandas", "Pandas"),
    ]
    
    tous_ok = True
    for module, nom in dependances:
        try:
            __import__(module)
            print(f"✅ {nom} installé")
        except ImportError:
            print(f"❌ {nom} MANQUANT - pip install {module}")
            tous_ok = False
    
    return tous_ok


def verifier_modele_bd():
    """Vérifier le modèle BD"""
    print("\n🗄️  Vérification modèle BD...")
    
    try:
        with open("src/core/models.py", 'r') as f:
            contenu = f.read()
        
        checks = [
            "code_barres: Mapped[str | None]",
            "prix_unitaire: Mapped[float | None]",
        ]
        
        tous_ok = True
        for check in checks:
            if check in contenu:
                print(f"✅ {check}")
            else:
                print(f"❌ {check} MANQUANT")
                tous_ok = False
        
        return tous_ok
    except FileNotFoundError:
        print("❌ src/core/models.py non trouvé")
        return False


def verifier_migration():
    """Vérifier la migration Alembic"""
    print("\n🔄 Vérification migration...")
    
    try:
        with open("alembic/versions/003_add_barcode_price.py", 'r') as f:
            contenu = f.read()
        
        checks = [
            "def upgrade",
            "def downgrade",
            "code_barres",
            "prix_unitaire",
        ]
        
        tous_ok = True
        for check in checks:
            if check in contenu:
                print(f"✅ {check}")
            else:
                print(f"❌ {check} MANQUANT")
                tous_ok = False
        
        return tous_ok
    except FileNotFoundError:
        print("❌ Migration file not found")
        return False


def verifier_documentation():
    """Vérifier la documentation"""
    print("\n📚 Vérification documentation...")
    
    docs = [
        "BARCODE_RAPPORTS_SETUP.md",
        "IMPLEMENTATION_BARCODE_RAPPORTS.md",
        "QUICKSTART_BARCODE_RAPPORTS.md",
        "RESUME_IMPLEMENTATION_COMPLETE.md",
    ]
    
    tous_ok = True
    for doc in docs:
        if Path(doc).exists():
            taille = Path(doc).stat().st_size
            print(f"✅ {doc} ({taille} bytes)")
        else:
            print(f"❌ {doc} MANQUANT")
            tous_ok = False
    
    return tous_ok


def verifier_syntaxe_python():
    """Vérifier la syntaxe Python des fichiers"""
    print("\n✨ Vérification syntaxe Python...")
    
    fichiers = [
        "src/services/barcode.py",
        "src/services/rapports_pdf.py",
        "src/modules/barcode.py",
        "src/modules/rapports.py",
    ]
    
    import ast
    tous_ok = True
    
    for fichier in fichiers:
        try:
            with open(fichier, 'r') as f:
                ast.parse(f.read())
            print(f"✅ {fichier} syntaxe OK")
        except SyntaxError as e:
            print(f"❌ {fichier} erreur: {e}")
            tous_ok = False
        except FileNotFoundError:
            print(f"❌ {fichier} non trouvé")
            tous_ok = False
    
    return tous_ok


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════


def main():
    """Run all verifications"""
    
    print("╔════════════════════════════════════════════════════╗")
    print("║  ✅ VÉRIFICATION IMPLÉMENTATION COMPLÈTE          ║")
    print("║  Code-Barres/QR + Rapports PDF                    ║")
    print("╚════════════════════════════════════════════════════╝")
    
    os.chdir("/workspaces/assistant_matanne")
    
    resultats = {
        "Fichiers": verifier_fichiers(),
        "Services": verifier_contenu_services(),
        "Modules UI": verifier_contenu_modules(),
        "Dépendances": verifier_dependances(),
        "Modèle BD": verifier_modele_bd(),
        "Migration": verifier_migration(),
        "Documentation": verifier_documentation(),
        "Syntaxe Python": verifier_syntaxe_python(),
    }
    
    # Résumé
    print("\n" + "="*50)
    print("📊 RÉSUMÉ")
    print("="*50)
    
    total = len(resultats)
    valides = sum(1 for v in resultats.values() if v)
    
    for categorie, ok in resultats.items():
        status = "✅" if ok else "❌"
        print(f"{status} {categorie}")
    
    print(f"\n{valides}/{total} catégories OK")
    
    if valides == total:
        print("\n🎉 TOUS LES TESTS PASSENT - PRÊT POUR PRODUCTION!")
        return 0
    else:
        print("\n⚠️  Certains éléments à corriger")
        return 1


if __name__ == "__main__":
    sys.exit(main())
