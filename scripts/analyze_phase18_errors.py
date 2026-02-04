#!/usr/bin/env python3
"""
PHASE 18 - ANALYSE DES ERREURS DE TEST
======================================

Script pour analyser les patterns d'erreur dans les 319 tests échoués
et les 115 erreurs de service.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class TestErrorAnalyzer:
    """Analyser les patterns d'erreur des tests."""
    
    def __init__(self):
        self.patterns = defaultdict(list)
        self.error_categories = defaultdict(int)
        self.failed_tests = []
        self.service_errors = []
    
    def run_pytest_collect(self) -> str:
        """Exécuter pytest et capturer les résultats."""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v", "--tb=line"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        return result.stdout + result.stderr
    
    def categorize_error(self, error_msg: str) -> str:
        """Catégoriser un message d'erreur."""
        if "assert" in error_msg.lower():
            return "assertion"
        elif "typeerror" in error_msg.lower():
            return "type_error"
        elif "404" in error_msg:
            return "api_404_mismatch"
        elif "mock" in error_msg.lower():
            return "mock_issue"
        elif "fixture" in error_msg.lower():
            return "fixture_issue"
        elif "valueerror" in error_msg.lower():
            return "value_error"
        elif "keyerror" in error_msg.lower():
            return "key_error"
        elif "attributeerror" in error_msg.lower():
            return "attribute_error"
        else:
            return "other"
    
    def parse_pytest_output(self, output: str):
        """Parser la sortie pytest pour extraire les erreurs."""
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            # Détecter les échecs FAILED
            if "FAILED" in line:
                match = re.search(r'FAILED ([\w/\.]+::\S+)', line)
                if match:
                    test_name = match.group(1)
                    
                    # Chercher le message d'erreur suivant
                    error_msg = ""
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip():
                            error_msg += lines[j] + "\n"
                        if "assert" in lines[j] or "Error" in lines[j]:
                            break
                    
                    category = self.categorize_error(error_msg)
                    self.failed_tests.append({
                        "test": test_name,
                        "error": error_msg.strip(),
                        "category": category
                    })
                    self.error_categories[category] += 1
            
            # Détecter les erreurs ERROR
            if "ERROR" in line and "error" in line.lower():
                self.service_errors.append(line.strip())
    
    def analyze_file_patterns(self):
        """Analyser les patterns par fichier de test."""
        test_dir = Path("tests")
        error_by_file = defaultdict(int)
        
        for failed_test in self.failed_tests:
            file_match = re.search(r'tests/([\w/\.]+)\.py', failed_test["test"])
            if file_match:
                file_name = file_match.group(1)
                error_by_file[file_name] += 1
        
        # Trier par nombre d'erreurs décroissant
        sorted_errors = sorted(error_by_file.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors
    
    def generate_report(self) -> str:
        """Générer un rapport complet des erreurs."""
        report = []
        report.append("=" * 80)
        report.append("PHASE 18 - ANALYSE DES ERREURS DE TEST")
        report.append("=" * 80)
        report.append("")
        
        # Résumé par catégorie
        report.append("RESUME PAR CATEGORIE D'ERREUR")
        report.append("-" * 80)
        
        sorted_categories = sorted(
            self.error_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for category, count in sorted_categories:
            percentage = (count / len(self.failed_tests)) * 100 if self.failed_tests else 0
            report.append(f"  • {category:20s}: {count:3d} tests ({percentage:5.1f}%)")
        
        report.append("")
        report.append(f"TOTAL TESTS ÉCHOUÉS: {len(self.failed_tests)}")
        report.append(f"TOTAL ERREURS SERVICE: {len(self.service_errors)}")
        report.append("")
        
        # Erreurs par fichier
        report.append("FICHIERS LES PLUS AFFECTES")
        report.append("-" * 80)
        
        file_patterns = self.analyze_file_patterns()
        for file_name, count in file_patterns[:15]:  # Top 15
            report.append(f"  • {file_name:50s}: {count:3d} échoués")
        
        report.append("")
        
        # Recommandations prioritaires
        report.append("PRIORITES DE CORRECTION")
        report.append("-" * 80)
        
        if self.error_categories.get("api_404_mismatch", 0) > 0:
            count = self.error_categories["api_404_mismatch"]
            report.append(f"  1. API Response Mismatch ({count} tests)")
            report.append("     → Vérifier les endpoints qui retournent 200 au lieu de 404")
            report.append("     → Revoir les modèles de validation FastAPI")
            report.append("")
        
        if self.error_categories.get("type_error", 0) > 0:
            count = self.error_categories["type_error"]
            report.append(f"  2. Type Errors ({count} tests)")
            report.append("     → Vérifier les signatures de constructeur")
            report.append("     → Améliorer les fixtures de service")
            report.append("")
        
        if self.error_categories.get("assertion", 0) > 0:
            count = self.error_categories["assertion"]
            report.append(f"  3. Assertion Failures ({count} tests)")
            report.append("     → Vérifier les attentes des tests")
            report.append("     → Mettre à jour les données de test")
            report.append("")
        
        if self.error_categories.get("mock_issue", 0) > 0:
            count = self.error_categories["mock_issue"]
            report.append(f"  4. Mock Issues ({count} tests)")
            report.append("     → Implémenter les factories de mock")
            report.append("     → Améliorer l'isolation des tests")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_detailed_results(self):
        """Sauvegarder les résultats détaillés en JSON."""
        output = {
            "timestamp": str(Path("phase_18_test_results_raw.txt").read_text() if Path("phase_18_test_results_raw.txt").exists() else ""),
            "summary": {
                "total_failed": len(self.failed_tests),
                "total_errors": len(self.service_errors),
                "categories": dict(self.error_categories)
            },
            "failed_tests": self.failed_tests[:50],  # Top 50
            "error_files": self.analyze_file_patterns()[:20]
        }
        
        output_file = Path("phase_18_error_analysis.json")
        output_file.write_text(json.dumps(output, indent=2, ensure_ascii=False))
        return output_file


if __name__ == "__main__":
    analyzer = TestErrorAnalyzer()
    
    print("[*] Collection des resultats de test...")
    output = analyzer.run_pytest_collect()
    
    print("[*] Analyse des patterns d'erreur...")
    analyzer.parse_pytest_output(output)
    
    # Générer et afficher le rapport
    report = analyzer.generate_report()
    print("\n" + report)
    
    # Sauvegarder les résultats détaillés
    print("\n[*] Sauvegarde des resultats detailles...")
    results_file = analyzer.save_detailed_results()
    print(f"[+] Resultats sauvegardes: {results_file}")
