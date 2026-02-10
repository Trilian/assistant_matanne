#!/usr/bin/env python3
"""
Script pour diviser les fichiers sources volumineux (>1000 lignes).

Ce script identifie et propose des divisions pour les gros fichiers.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re


LARGE_FILE_THRESHOLD = 1000
SRC_DIR = Path("src")


class FileAnalyzer:
    """Analyse un fichier Python pour suggérer des divisions."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")
        self.tree = None
        
        try:
            self.tree = ast.parse(self.content)
        except Exception as e:
            print(f"⚠️ Erreur de parsing pour {file_path}: {e}")
    
    def count_lines(self) -> int:
        """Compte le nombre de lignes."""
        return len(self.lines)
    
    def analyze_structure(self) -> Dict:
        """Analyse la structure du fichier."""
        if not self.tree:
            return {}
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                # Compter les lignes de la classe
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                line_count = end_line - start_line + 1
                
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                
                classes.append({
                    "name": node.name,
                    "line_start": start_line,
                    "line_end": end_line,
                    "line_count": line_count,
                    "methods": methods,
                    "method_count": len(methods)
                })
            
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions (not methods)
                if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(self.tree)):
                    start_line = node.lineno
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                    line_count = end_line - start_line + 1
                    
                    functions.append({
                        "name": node.name,
                        "line_start": start_line,
                        "line_end": end_line,
                        "line_count": line_count
                    })
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node.lineno)
        
        return {
            "classes": classes,
            "functions": functions,
            "import_lines": imports,
            "total_lines": self.count_lines()
        }
    
    def suggest_split(self) -> List[Dict]:
        """Suggère comment diviser le fichier."""
        structure = self.analyze_structure()
        suggestions = []
        
        # Stratégie 1: Diviser par classes volumineuses
        large_classes = [c for c in structure.get("classes", []) if c["line_count"] > 200]
        if large_classes:
            for cls in large_classes:
                suggestions.append({
                    "strategy": "extract_class",
                    "class_name": cls["name"],
                    "new_file": f"{cls['name'].lower()}.py",
                    "line_range": (cls["line_start"], cls["line_end"]),
                    "reason": f"Classe volumineuse: {cls['line_count']} lignes"
                })
        
        # Stratégie 2: Grouper des fonctions par domaine (basé sur les noms)
        functions = structure.get("functions", [])
        if len(functions) > 10:
            # Grouper par préfixe commun
            function_groups = {}
            for func in functions:
                prefix = func["name"].split("_")[0] if "_" in func["name"] else "misc"
                if prefix not in function_groups:
                    function_groups[prefix] = []
                function_groups[prefix].append(func)
            
            for prefix, funcs in function_groups.items():
                if len(funcs) >= 3:
                    total_lines = sum(f["line_count"] for f in funcs)
                    if total_lines > 100:
                        suggestions.append({
                            "strategy": "group_functions",
                            "group_name": prefix,
                            "new_file": f"{prefix}_utils.py",
                            "functions": [f["name"] for f in funcs],
                            "reason": f"Groupe de {len(funcs)} fonctions ({total_lines} lignes)"
                        })
        
        return suggestions


def find_large_files() -> List[Tuple[Path, int]]:
    """Trouve tous les fichiers volumineux."""
    large_files = []
    
    for py_file in SRC_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        try:
            line_count = len(py_file.read_text(encoding="utf-8").split("\n"))
            if line_count > LARGE_FILE_THRESHOLD:
                large_files.append((py_file, line_count))
        except Exception as e:
            print(f"⚠️ Erreur de lecture {py_file}: {e}")
    
    return sorted(large_files, key=lambda x: x[1], reverse=True)


def main():
    """Point d'entrée principal."""
    print("=" * 80)
    print("📏 ANALYSE DES FICHIERS VOLUMINEUX")
    print("=" * 80)
    print()
    
    large_files = find_large_files()
    
    print(f"✅ Trouvé {len(large_files)} fichiers dépassant {LARGE_FILE_THRESHOLD} lignes\n")
    
    all_analysis = []
    
    for file_path, line_count in large_files:
        print(f"\n{'='*80}")
        print(f"📄 {file_path.relative_to(SRC_DIR)}")
        print(f"   Lignes: {line_count}")
        print(f"{'='*80}")
        
        analyzer = FileAnalyzer(file_path)
        structure = analyzer.analyze_structure()
        suggestions = analyzer.suggest_split()
        
        # Afficher la structure
        if structure.get("classes"):
            print(f"\n  Classes ({len(structure['classes'])}):")
            for cls in structure["classes"]:
                print(f"    - {cls['name']}: {cls['line_count']} lignes, {cls['method_count']} méthodes")
        
        if structure.get("functions"):
            print(f"\n  Fonctions top-level ({len(structure['functions'])}):")
            for func in structure["functions"][:5]:  # Limiter l'affichage
                print(f"    - {func['name']}: {func['line_count']} lignes")
            if len(structure["functions"]) > 5:
                print(f"    ... et {len(structure['functions']) - 5} autres")
        
        # Afficher les suggestions
        if suggestions:
            print(f"\n  💡 Suggestions de division ({len(suggestions)}):")
            for i, sug in enumerate(suggestions, 1):
                print(f"    {i}. {sug['strategy']}: {sug.get('new_file', 'N/A')}")
                print(f"       Raison: {sug['reason']}")
        else:
            print("\n  ℹ️ Pas de suggestion automatique - analyse manuelle nécessaire")
        
        all_analysis.append({
            "file": str(file_path.relative_to(SRC_DIR)),
            "line_count": line_count,
            "structure": structure,
            "suggestions": suggestions
        })
    
    # Sauvegarder l'analyse
    output_file = Path("large_files_analysis.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Analyse complète sauvegardée dans: {output_file}")
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
