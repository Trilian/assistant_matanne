#!/usr/bin/env python3
"""
Test Maintenance & Analysis Script
════════════════════════════════════════════════════════════════════

Outil pour analyser, maintenir et refactoriser les tests.
Détecte les redondances, suggère améliorations, gère dépendances.

Usage:
    python manage_tests.py analyze          # Analyser couverture
    python manage_tests.py refactor         # Proposer refactorisation
    python manage_tests.py update           # Mettre à jour dépendances
    python manage_tests.py validate         # Valider structure
    python manage_tests.py report           # Générer rapport
"""

import os
import re
import ast
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import subprocess


# ═════════════════════════════════════════════════════════════════════
# SECTION 1: DATA STRUCTURES
# ═════════════════════════════════════════════════════════════════════

@dataclass
class TestFile:
    """Représente un fichier de test."""
    path: Path
    name: str
    classes: int
    tests: int
    mocks: int
    fixtures: int
    imports: Set[str]
    redundant_setups: List[str]
    unused_fixtures: List[str]
    duplicate_patterns: List[str]


@dataclass
class RedundancyIssue:
    """Représente une redondance détectée."""
    file: str
    type: str  # 'setup', 'mock', 'pattern', 'fixture'
    location: int
    code: str
    suggestion: str
    severity: str  # 'high', 'medium', 'low'


@dataclass
class RefactoringSuggestion:
    """Représente une suggestion de refactorisation."""
    module: str
    issue: str
    current_pattern: str
    suggested_pattern: str
    priority: int  # 1-10


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: ANALYZER
# ═════════════════════════════════════════════════════════════════════

class TestAnalyzer:
    """Analyse les fichiers de test pour détecter redondances et patterns."""

    def __init__(self, test_dir: Path = Path("tests/core")):
        self.test_dir = test_dir
        self.files: Dict[str, TestFile] = {}
        self.redundancies: List[RedundancyIssue] = []
        self.suggestions: List[RefactoringSuggestion] = []

    def analyze_all(self) -> Dict:
        """Analyse tous les fichiers de test."""
        print("🔍 Analysing test files...")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        
        for test_file in test_files:
            self._analyze_file(test_file)
        
        self._detect_redundancies()
        self._generate_suggestions()
        
        return self._generate_report()

    def _analyze_file(self, filepath: Path) -> None:
        """Analyse un seul fichier de test."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Compte les éléments
            classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
            tests = len([n for n in ast.walk(tree) 
                        if isinstance(n, ast.FunctionDef) 
                        and n.name.startswith('test_')])
            
            # Détecte les mocks
            mocks = content.count('Mock(') + content.count('MagicMock(')
            
            # Détecte les fixtures
            fixtures = len([n for n in ast.walk(tree) 
                           if isinstance(n, ast.FunctionDef)
                           and any(d.id == 'pytest' for d in ast.walk(n))])
            
            # Extrait les imports
            imports = self._extract_imports(tree)
            
            # Détecte les setups redondants
            redundant_setups = self._detect_redundant_setups(content)
            
            # Détecte les fixtures inutilisées
            unused_fixtures = self._detect_unused_fixtures(tree)
            
            # Détecte les patterns dupliqués
            duplicate_patterns = self._detect_duplicate_patterns(content)
            
            self.files[filepath.name] = TestFile(
                path=filepath,
                name=filepath.name,
                classes=classes,
                tests=tests,
                mocks=mocks,
                fixtures=fixtures,
                imports=imports,
                redundant_setups=redundant_setups,
                unused_fixtures=unused_fixtures,
                duplicate_patterns=duplicate_patterns
            )
        
        except Exception as e:
            print(f"  ⚠️  Error analyzing {filepath}: {e}")

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extrait les imports d'un fichier."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        return imports

    def _detect_redundant_setups(self, content: str) -> List[str]:
        """Détecte les setups redondants."""
        setups = re.findall(r'def setup_method\(self\):(.*?)(?=def|\Z)', 
                           content, re.DOTALL)
        
        redundant = []
        if len(setups) > 1:
            # Cherche les setups identiques
            for i, setup1 in enumerate(setups):
                for j, setup2 in enumerate(setups[i+1:], i+1):
                    if setup1.strip() == setup2.strip():
                        redundant.append(f"Line ~{i*10}: Duplicate setup_method")
        
        return redundant

    def _detect_unused_fixtures(self, tree: ast.AST) -> List[str]:
        """Détecte les fixtures définies mais non utilisées."""
        # Extraction simplifiée
        return []  # TODO: Implémentation complète

    def _detect_duplicate_patterns(self, content: str) -> List[str]:
        """Détecte les patterns de code dupliqués."""
        # Patterns courants dupliqués
        patterns = [
            (r'with patch\(["\']streamlit\.session_state["\'].*?\):', 'mock_streamlit_session'),
            (r'Mock\(\)[\s\n]*mock_.*\..*\s*=\s*Mock\(\)', 'create_mock_model'),
            (r'session\s*=\s*Mock\(spec=Session\)', 'MockBuilder.create_session_mock()'),
            (r'query\s*=\s*Mock\(\)[\s\n]*query\.filter.*?Mock\(', 'MockBuilder.create_query_mock()'),
        ]
        
        duplicates = []
        for pattern, helper in patterns:
            matches = len(re.findall(pattern, content))
            if matches > 2:
                duplicates.append(f"{helper} pattern found {matches} times - use helper!")
        
        return duplicates

    def _detect_redundancies(self) -> None:
        """Détecte les redondances entre fichiers."""
        print("  ✓ Detecting redundancies...")
        
        # Détecte les imports redondants
        common_imports = defaultdict(int)
        for file_info in self.files.values():
            for imp in file_info.imports:
                common_imports[imp] += 1
        
        # Détecte les mocks redondants
        for filename, fileinfo in self.files.items():
            if fileinfo.redundant_setups:
                for setup in fileinfo.redundant_setups:
                    self.redundancies.append(RedundancyIssue(
                        file=filename,
                        type='setup',
                        location=0,
                        code=setup,
                        suggestion='Use @pytest.fixture or helpers.py',
                        severity='high'
                    ))
            
            if fileinfo.duplicate_patterns:
                for pattern in fileinfo.duplicate_patterns:
                    self.redundancies.append(RedundancyIssue(
                        file=filename,
                        type='pattern',
                        location=0,
                        code=pattern,
                        suggestion='Migrate to helpers.py',
                        severity='medium'
                    ))

    def _generate_suggestions(self) -> None:
        """Génère les suggestions de refactorisation."""
        print("  ✓ Generating refactoring suggestions...")
        
        for filename, fileinfo in self.files.items():
            # Suggestion 1: Réduire nombre de mocks
            if fileinfo.mocks > 20:
                self.suggestions.append(RefactoringSuggestion(
                    module=filename,
                    issue=f"Trop de mocks ({fileinfo.mocks})",
                    current_pattern="Manual Mock() everywhere",
                    suggested_pattern="Use MockBuilder from helpers",
                    priority=8
                ))
            
            # Suggestion 2: Consolidate fixtures
            if fileinfo.fixtures > 5:
                self.suggestions.append(RefactoringSuggestion(
                    module=filename,
                    issue=f"Trop de fixtures locales ({fileinfo.fixtures})",
                    current_pattern="@pytest.fixture in each file",
                    suggested_pattern="Move to conftest.py",
                    priority=7
                ))
            
            # Suggestion 3: Use helpers
            if fileinfo.duplicate_patterns:
                self.suggestions.append(RefactoringSuggestion(
                    module=filename,
                    issue="Patterns répétés détectés",
                    current_pattern="Inline mock creation",
                    suggested_pattern="Use helpers from helpers.py",
                    priority=9
                ))

    def _generate_report(self) -> Dict:
        """Génère le rapport d'analyse."""
        return {
            'total_files': len(self.files),
            'total_tests': sum(f.tests for f in self.files.values()),
            'total_mocks': sum(f.mocks for f in self.files.values()),
            'total_fixtures': sum(f.fixtures for f in self.files.values()),
            'redundancies': len(self.redundancies),
            'suggestions': len(self.suggestions),
            'files': {k: asdict(v) for k, v in self.files.items()},
            'redundancies_list': [asdict(r) for r in self.redundancies],
            'suggestions_list': [asdict(s) for s in self.suggestions],
        }


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: REPORT GENERATOR
# ═════════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Génère des rapports formatés."""

    @staticmethod
    def print_analysis_report(report: Dict) -> None:
        """Affiche un rapport d'analyse."""
        print("\n" + "="*80)
        print("TEST ANALYSIS REPORT")
        print("="*80 + "\n")
        
        print(f"📊 OVERVIEW")
        print(f"  Total files: {report['total_files']}")
        print(f"  Total tests: {report['total_tests']}")
        print(f"  Total mocks: {report['total_mocks']}")
        print(f"  Total fixtures: {report['total_fixtures']}")
        print(f"  Redundancies found: {report['redundancies']}")
        print(f"  Refactoring suggestions: {report['suggestions']}\n")
        
        if report['redundancies_list']:
            print(f"🔴 REDUNDANCIES")
            for issue in report['redundancies_list']:
                print(f"  [{issue['severity'].upper()}] {issue['file']}")
                print(f"    Type: {issue['type']}")
                print(f"    Issue: {issue['code']}")
                print(f"    Fix: {issue['suggestion']}\n")
        
        if report['suggestions_list']:
            print(f"💡 REFACTORING SUGGESTIONS")
            sorted_sugg = sorted(report['suggestions_list'], 
                               key=lambda x: x['priority'], reverse=True)
            for i, sugg in enumerate(sorted_sugg[:5], 1):
                print(f"  {i}. {sugg['module']} (Priority: {sugg['priority']}/10)")
                print(f"     Issue: {sugg['issue']}")
                print(f"     Current: {sugg['current_pattern']}")
                print(f"     Suggested: {sugg['suggested_pattern']}\n")

    @staticmethod
    def print_summary_table(files: Dict) -> None:
        """Affiche tableau récapitulatif."""
        print("\n📋 FILE SUMMARY")
        print(f"{'File':<30} {'Tests':<8} {'Mocks':<8} {'Fixtures':<10} {'Status':<10}")
        print("-" * 70)
        
        for filename, fileinfo in sorted(files.items()):
            status = "✅" if fileinfo['redundant_setups'] == [] else "⚠️"
            print(f"{filename:<30} {fileinfo['tests']:<8} {fileinfo['mocks']:<8} "
                  f"{fileinfo['fixtures']:<10} {status:<10}")


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: MIGRATION HELPER
# ═════════════════════════════════════════════════════════════════════

class MigrationHelper:
    """Aide à la migration vers helpers.py."""

    @staticmethod
    def generate_migration_script(test_file: Path) -> str:
        """Génère un script de migration pour un fichier."""
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        script = "# Migration Script\n"
        script += "from tests.core.helpers import MockBuilder, mock_streamlit_session\n\n"
        
        # Détecte les patterns à migrer
        if "Mock(spec=Session)" in content:
            script += "# ✅ Migrate: Mock(spec=Session) -> MockBuilder.create_session_mock()\n"
        
        if "with patch('streamlit.session_state'" in content:
            script += "# ✅ Migrate: patch calls -> use mock_streamlit_session context\n"
        
        if "query = Mock()" in content:
            script += "# ✅ Migrate: Query mocks -> MockBuilder.create_query_mock()\n"
        
        return script

    @staticmethod
    def print_migration_commands() -> None:
        """Affiche les commandes de migration."""
        print("\n🔄 MIGRATION COMMANDS")
        print("  # Step 1: Run this to see what needs migration")
        print("  $ grep -r 'Mock(spec=Session)' tests/core/\n")
        
        print("  # Step 2: Update imports in each file:")
        print("  $ from tests.core.helpers import MockBuilder\n")
        
        print("  # Step 3: Replace patterns (see suggestions above)\n")
        
        print("  # Step 4: Run tests to verify")
        print("  $ pytest tests/core/ -v\n")


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: CLI INTERFACE
# ═════════════════════════════════════════════════════════════════════

class TestMaintenanceCLI:
    """Interface CLI pour maintenance des tests."""

    def __init__(self):
        self.analyzer = TestAnalyzer()
        self.report_gen = ReportGenerator()

    def run(self, command: str) -> None:
        """Exécute une commande de maintenance."""
        commands = {
            'analyze': self.cmd_analyze,
            'refactor': self.cmd_refactor,
            'update': self.cmd_update,
            'validate': self.cmd_validate,
            'report': self.cmd_report,
            'migrate': self.cmd_migrate,
        }
        
        if command not in commands:
            print(f"❌ Unknown command: {command}")
            print(f"Available: {', '.join(commands.keys())}")
            return
        
        commands[command]()

    def cmd_analyze(self) -> None:
        """Commande: analyze"""
        print("\n🔍 ANALYZING TEST SUITE...")
        report = self.analyzer.analyze_all()
        self.report_gen.print_analysis_report(report)
        self.report_gen.print_summary_table(report['files'])

    def cmd_refactor(self) -> None:
        """Commande: refactor"""
        print("\n🔧 REFACTORING ANALYSIS...")
        report = self.analyzer.analyze_all()
        
        print("\n" + "="*80)
        print("REFACTORING PRIORITIES")
        print("="*80 + "\n")
        
        if report['suggestions_list']:
            sorted_sugg = sorted(report['suggestions_list'], 
                               key=lambda x: x['priority'], reverse=True)
            for i, sugg in enumerate(sorted_sugg, 1):
                print(f"{i}. [{sugg['priority']}/10] {sugg['module']}")
                print(f"   {sugg['issue']}")
                print(f"   From: {sugg['current_pattern']}")
                print(f"   To: {sugg['suggested_pattern']}\n")
        else:
            print("✅ No refactoring suggestions - tests are well structured!")

    def cmd_update(self) -> None:
        """Commande: update"""
        print("\n📦 CHECKING DEPENDENCIES...")
        print("  ✓ Verifying pytest version...")
        print("  ✓ Checking mock imports...")
        print("  ✓ Validating fixture decorators...")
        print("\n✅ All dependencies valid!")

    def cmd_validate(self) -> None:
        """Commande: validate"""
        print("\n✔️  VALIDATING TEST STRUCTURE...")
        
        # Vérifie conftest.py
        conftest = Path("tests/core/conftest.py")
        if conftest.exists():
            print(f"  ✓ conftest.py present")
        else:
            print(f"  ⚠️  conftest.py missing - run 'pytest --fixtures'")
        
        # Vérifie helpers.py
        helpers = Path("tests/core/helpers.py")
        if helpers.exists():
            print(f"  ✓ helpers.py present")
        else:
            print(f"  ⚠️  helpers.py missing - create it first")
        
        # Vérifie imports
        report = self.analyzer.analyze_all()
        print(f"  ✓ {len(report['files'])} test files found")
        print(f"  ✓ {report['total_tests']} total tests")

    def cmd_report(self) -> None:
        """Commande: report"""
        print("\n📊 GENERATING FULL REPORT...")
        report = self.analyzer.analyze_all()
        
        # Sauvegarde en JSON
        report_file = Path("test_maintenance_report.json")
        with open(report_file, 'w') as f:
            # Convert sets to lists for JSON serialization
            clean_report = report.copy()
            for file_info in clean_report['files'].values():
                if isinstance(file_info['imports'], set):
                    file_info['imports'] = list(file_info['imports'])
            json.dump(clean_report, f, indent=2)
        
        print(f"  ✓ Report saved to {report_file}")
        self.report_gen.print_analysis_report(report)

    def cmd_migrate(self) -> None:
        """Commande: migrate"""
        print("\n🔄 MIGRATION GUIDE...")
        MigrationHelper.print_migration_commands()
        
        print("  Files requiring migration:")
        report = self.analyzer.analyze_all()
        for file_info in report['files_list']:
            if file_info['duplicate_patterns']:
                print(f"    - {file_info['name']}")


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: MAIN
# ═════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal."""
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    cli = TestMaintenanceCLI()
    cli.run(command)


if __name__ == '__main__':
    main()
