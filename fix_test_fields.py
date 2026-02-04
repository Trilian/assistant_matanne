#!/usr/bin/env python3
"""
Script pour corriger les field names incorrects dans test_phase16_extended.py

Corrections:
- Planning: semaine= → nom + semaine_debut + semaine_fin + actif=True
- Planning: jour_semaine= → Supprimer
- Planning: type_repas= → Supprimer
- Repas: jour= → date_repas=
"""

import re
from pathlib import Path
from datetime import date, timedelta

# Chemin du fichier
TEST_FILE = Path("d:/Projet_streamlit/assistant_matanne/tests/integration/test_phase16_extended.py")

def parse_planning_date(semaine_str):
    """Extrait la date du paramètre semaine et retourne semaine_debut et semaine_fin."""
    # Extrait la date du format date(2025, 2, 3)
    match = re.search(r'date\((\d+),\s*(\d+),\s*(\d+)\)', semaine_str)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        semaine_debut = f"date({year}, {month}, {day})"
        semaine_fin = f"date({year}, {month}, {day}) + timedelta(days=6)"
        # Génère un nom pour la semaine
        week_num = (int(day) - 1) // 7 + 1
        nom = f'"Planning Week {week_num}"'
        return nom, semaine_debut, semaine_fin
    return None, None, None

def parse_jour_to_date(jour_str):
    """Convertit le jour en date_repas."""
    # Map jour to date (semaine de 2025-02-03)
    jour_to_date = {
        "lundi": "date(2025, 2, 3)",
        "mardi": "date(2025, 2, 4)",
        "mercredi": "date(2025, 2, 5)",
        "jeudi": "date(2025, 2, 6)",
        "vendredi": "date(2025, 2, 7)",
        "samedi": "date(2025, 2, 8)",
        "dimanche": "date(2025, 2, 9)",
    }
    
    # Extrait le jour du format jour="lundi"
    match = re.search(r'jour\s*=\s*["\']([^"\']+)["\']', jour_str)
    if match:
        jour = match.group(1)
        return jour_to_date.get(jour, "date(2025, 2, 3)")
    return "date(2025, 2, 3)"

def fix_planning_calls(content):
    """Corrige tous les appels Planning()."""
    replacement_count = 0
    
    # Pattern pour Planning(semaine=date(...), ...)
    # Capture tout jusqu'à la fermeture
    pattern = r'Planning\s*\(\s*semaine\s*=\s*(date\([^)]+\))\s*(?:,\s*jour_semaine\s*=\s*["\'][^"\']*["\'])?(?:,\s*type_repas\s*=\s*["\'][^"\']*["\'])?(?:,\s*(notes\s*=\s*["\'][^"\']*["\'])?)?\s*\)'
    
    def replace_planning(match):
        nonlocal replacement_count
        semaine_date = match.group(1)
        notes_part = match.group(2)
        
        nom, semaine_debut, semaine_fin = parse_planning_date(semaine_date)
        
        if nom:
            replacement_count += 1
            # Reconstruit l'appel Planning
            result = f'Planning(nom={nom}, semaine_debut={semaine_debut}, semaine_fin={semaine_fin}, actif=True'
            if notes_part:
                result += f', {notes_part}'
            result += ')'
            return result
        return match.group(0)
    
    new_content = re.sub(pattern, replace_planning, content)
    return new_content, replacement_count

def fix_repas_calls(content):
    """Corrige tous les appels Repas() pour remplacer jour= par date_repas=."""
    replacement_count = 0
    
    # Pattern 1: jour="..." (littéraux de chaîne)
    pattern1 = r'jour\s*=\s*(["\'])([^"\']+)\1'
    
    def replace_jour_literal(match):
        nonlocal replacement_count
        jour = match.group(2)
        
        jour_to_date = {
            "lundi": "date(2025, 2, 3)",
            "mardi": "date(2025, 2, 4)",
            "mercredi": "date(2025, 2, 5)",
            "jeudi": "date(2025, 2, 6)",
            "vendredi": "date(2025, 2, 7)",
            "samedi": "date(2025, 2, 8)",
            "dimanche": "date(2025, 2, 9)",
        }
        
        date_repas = jour_to_date.get(jour, "date(2025, 2, 3)")
        replacement_count += 1
        return f'date_repas={date_repas}'
    
    new_content = re.sub(pattern1, replace_jour_literal, content)
    
    # Pattern 2: jour=jour (variable)
    # Cherche "jour=jour" mais seulement dans le contexte de Repas(...)
    # Cela doit être converti en fonction de la boucle
    # On cherche: for jour in jours: ... Repas(..., jour=jour, ...)
    # Ceci est complexe, donc on va faire un remplacement plus spécifique
    
    # Cherche les patterns comme: jour=jour dans une boucle
    pattern2 = r'for\s+jour\s+in\s+jours:\s*\n\s+repas\s*=\s*Repas\([^)]*jour\s*=\s*jour'
    
    def replace_jour_variable(match):
        nonlocal replacement_count
        # Ceci nécessite une logique plus complexe
        # Pour l'instant, nous allons faire une substitution basique
        replacement_count += 1
        return match.group(0)
    
    # Remplacement plus simple: jour=jour → une logique de mapping
    pattern2_simple = r'jour\s*=\s*jour\s*,'
    new_content = re.sub(pattern2_simple, 'jour=jour,  # TODO: map to date_repas', new_content)
    
    return new_content, replacement_count

def fix_filter_by_jour(content):
    """Corrige les filter_by(jour=...) en filter_by(date_repas=...)."""
    replacement_count = 0
    
    # On doit aussi corriger les filter_by(jour="...")
    pattern = r'filter_by\s*\(\s*jour\s*='
    
    def replace_filter(match):
        nonlocal replacement_count
        replacement_count += 1
        return 'filter_by(date_repas='
    
    new_content = re.sub(pattern, replace_filter, content)
    return new_content, replacement_count

def main():
    """Fonction principale."""
    print(f"📂 Lecture du fichier: {TEST_FILE}")
    
    if not TEST_FILE.exists():
        print(f"❌ Fichier non trouvé: {TEST_FILE}")
        return False
    
    # Lire le contenu
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"✓ Fichier lu: {len(content)} caractères")
    
    # Appliquer les corrections
    print("\n🔧 Application des corrections...")
    
    # Fix Planning calls
    print("  1️⃣  Correction des appels Planning()...")
    content, count1 = fix_planning_calls(content)
    print(f"     → {count1} appels Planning() corrigés")
    
    # Fix Repas jour= → date_repas=
    print("  2️⃣  Correction des appels Repas() (jour → date_repas)...")
    content, count2 = fix_repas_calls(content)
    print(f"     → {count2} appels Repas() corrigés")
    
    # Fix filter_by(jour=...) → filter_by(date_repas=...)
    print("  3️⃣  Correction des filter_by(jour=...)...")
    content, count3 = fix_filter_by_jour(content)
    print(f"     → {count3} appels filter_by() corrigés")
    
    total_replacements = count1 + count2 + count3
    print(f"\n✅ Total de replacements: {total_replacements}")
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde du fichier...")
    try:
        with open(TEST_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Fichier sauvegardé: {TEST_FILE}")
        
        # Vérifier la syntaxe Python
        print("\n🔍 Vérification de la syntaxe Python...")
        try:
            compile(content, str(TEST_FILE), 'exec')
            print("✓ Syntaxe Python valide")
            return True
        except SyntaxError as e:
            print(f"❌ Erreur de syntaxe: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n" + "="*60)
        print("✅ Script exécuté avec succès!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Erreur lors de l'exécution du script")
        print("="*60)
        exit(1)
