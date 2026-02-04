#!/usr/bin/env python3
"""
Générateur de tests pour les fichiers manquants.
Crée des fichiers de tests structurés basés sur l'inspection du code source.
"""
import ast
import os
from pathlib import Path
from typing import List, Dict, Set

workspace = Path("d:\\Projet_streamlit\\assistant_matanne")
src_dir = workspace / "src"
tests_dir = workspace / "tests"

def extract_classes_and_functions(file_path: Path) -> Dict[str, List[str]]:
    """Extraire les classes et fonctions d'un fichier Python."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())
    except:
        return {'classes': [], 'functions': []}
    
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            # Ignorer les méthodes (elles sont dans les classes)
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                functions.append(node.name)
    
    return {'classes': classes, 'functions': functions}

def generate_model_test(model_name: str, classes: List[str]) -> str:
    """Générer un test pour un modèle SQLAlchemy."""
    return f'''"""
Tests pour le modèle {model_name}.

Couvre les opérations CRUD et validations du modèle {model_name}.
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from src.core.models import {', '.join(classes[:3]) if classes else 'Base'}


@pytest.mark.unit
class Test{model_name.title()}Model:
    """Tests du modèle {model_name}."""
    
    def test_model_creation(self, test_db: Session):
        """Test la création d'une instance du modèle."""
        # À implémenter basé sur la structure du modèle
        pass
    
    def test_model_validation(self, test_db: Session):
        """Test les validations du modèle."""
        pass
    
    def test_model_relationships(self, test_db: Session):
        """Test les relations du modèle."""
        pass
    
    def test_model_serialization(self, test_db: Session):
        """Test la sérialisation du modèle."""
        pass
'''

def generate_service_test(service_name: str, classes: List[str], functions: List[str]) -> str:
    """Générer un test pour un service."""
    class_name = ''.join(word.title() for word in service_name.split('_'))
    
    return f'''"""
Tests pour le service {service_name}.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.services.{service_name} import {class_name if classes else 'get_' + service_name + '_service'}


@pytest.mark.unit
class Test{class_name}Service:
    """Tests du service {service_name}."""
    
    def test_service_initialization(self, test_db: Session):
        """Test l'initialisation du service."""
        # À implémenter
        pass
    
    def test_service_basic_operations(self, test_db: Session):
        """Test les opérations de base du service."""
        pass
    
    def test_service_error_handling(self, test_db: Session):
        """Test la gestion des erreurs."""
        pass
    
    def test_service_integration(self, test_db: Session):
        """Test l'intégration avec la base de données."""
        pass
'''

def generate_generic_test(file_path: Path) -> str:
    """Générer un test générique pour n'importe quel fichier."""
    file_name = file_path.stem
    class_name = ''.join(word.title() for word in file_name.split('_'))
    
    return f'''"""
Tests pour {file_path.name}.
"""

import pytest


@pytest.mark.unit
class Test{class_name}:
    """Tests pour {file_path.name}."""
    
    def test_module_imports(self):
        """Test que le module peut être importé sans erreur."""
        # À implémenter basé sur le module
        pass
    
    def test_module_functions(self):
        """Test les fonctions du module."""
        pass
    
    def test_module_classes(self):
        """Test les classes du module."""
        pass
'''

def find_missing_test_files() -> Dict[str, List[Path]]:
    """Trouve tous les fichiers src sans test correspondant."""
    missing = {}
    
    for src_file in src_dir.rglob('*.py'):
        if src_file.name.startswith('__'):
            continue
        
        # Calculer le chemin du test correspondant
        rel_path = src_file.relative_to(src_dir)
        test_file_name = f'test_{src_file.stem}.py'
        test_path = tests_dir / rel_path.parent / test_file_name
        
        # Vérifier si le test existe
        if not test_path.exists():
            folder = str(rel_path.parent)
            if folder == '.':
                folder = 'root'
            
            if folder not in missing:
                missing[folder] = []
            missing[folder].append(src_file)
    
    return missing

def create_test_file(src_file: Path, test_path: Path):
    """Créer un fichier de test pour un fichier source."""
    # Créer le dossier si nécessaire
    test_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Déterminer le type de fichier
    if 'models' in src_file.parts:
        # C'est un modèle
        content = generate_model_test(src_file.stem, [])
    elif 'services' in src_file.parts:
        # C'est un service
        content = generate_service_test(src_file.stem, [], [])
    else:
        # Générique
        content = generate_generic_test(src_file)
    
    # Écrire le fichier si n'existe pas
    if not test_path.exists():
        with open(test_path, 'w') as f:
            f.write(content)
        return True
    return False

# Affichage
print("="*100)
print("ANALYSE DES FICHIERS MANQUANTS")
print("="*100)

missing = find_missing_test_files()

total_missing = sum(len(files) for files in missing.values())
print(f"\nTotal: {total_missing} fichiers manquant des tests\n")

for folder in sorted(missing.keys()):
    files = missing[folder]
    print(f"{folder}/ - {len(files)} fichiers")
    for f in sorted(files)[:5]:
        print(f"  - {f.name}")
    if len(files) > 5:
        print(f"  ... et {len(files) - 5} autres")
    print()

# Créer les tests pour les fichiers critiques
print("\n" + "="*100)
print("CRÉATION DES TESTS PRIORITAIRES")
print("="*100 + "\n")

priority_patterns = ['models/', 'core/ai/', 'services/']
created_count = 0

for folder in sorted(missing.keys()):
    for src_file in sorted(missing[folder]):
        rel_path = src_file.relative_to(src_dir)
        
        # Déterminer la priorité
        is_priority = any(pattern in str(rel_path) for pattern in priority_patterns)
        
        if is_priority:
            test_file_name = f'test_{src_file.stem}.py'
            test_path = tests_dir / rel_path.parent / test_file_name
            
            if create_test_file(src_file, test_path):
                print(f"✓ Créé: {test_path.relative_to(workspace)}")
                created_count += 1

print(f"\n✓ {created_count} fichiers de tests créés pour les fichiers prioritaires")
