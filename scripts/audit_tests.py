#!/usr/bin/env python
"""
Script d'audit des tests - Analyse de couverture et mapping source/test.

Ce script:
1. Scanne tous les fichiers Python source dans src/
2. Identifie les fichiers de test correspondants dans tests/
3. Calcule la couverture par fichier
4. GÃ©nÃ¨re un rapport CSV avec mÃ©triques de couverture
5. Identifie les tests inefficaces (hasattr, import-only)

Usage:
    python scripts/audit_tests.py
    python scripts/audit_tests.py --output reports/audit.csv
    python scripts/audit_tests.py --threshold 80
"""

import ast
import csv
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


@dataclass
class SourceFile:
    """ReprÃ©sente un fichier source."""

    path: Path
    lines: int
    functions: list[str]
    classes: list[str]


@dataclass
class TestFile:
    """ReprÃ©sente un fichier de test."""

    path: Path
    lines: int
    test_functions: list[str]
    test_patterns: dict[str, int]  # Patterns dÃ©tectÃ©s (hasattr, import, etc.)


@dataclass
class CoverageResult:
    """RÃ©sultat de couverture pour un fichier source."""

    source_path: str
    test_paths: list[str]
    coverage_percent: float
    covered_lines: int
    total_lines: int
    missing_lines: list[int]
    is_effective: bool  # Tests considÃ©rÃ©s efficaces?
    issues: list[str]  # ProblÃ¨mes dÃ©tectÃ©s


class TestAuditor:
    """Auditeur de tests et couverture."""

    # Patterns de tests potentiellement inefficaces
    INEFFECTIVE_PATTERNS = {
        "hasattr": r"\bhasattr\s*\(",
        "import_only": r"^from\s+\S+\s+import|^import\s+",
        "patch_all": r"@patch\.object\([^)]+\)",
        "pass_only": r"^\s*pass\s*$",
        "mock_session": r"mock.*session|MagicMock\(\)",
    }

    def __init__(self, project_root: Path, threshold: float = 80.0):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.tests_dir = project_root / "tests"
        self.threshold = threshold
        self.source_files: dict[str, SourceFile] = {}
        self.test_files: dict[str, TestFile] = {}
        self.coverage_data: dict[str, CoverageResult] = {}

    def scan_source_files(self) -> dict[str, SourceFile]:
        """Scanne tous les fichiers Python source."""
        print("ðŸ” Scan des fichiers source...")

        for py_file in self.src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8-sig")  # Handle BOM
                tree = ast.parse(content)

                functions = []
                classes = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith("_") or node.name.startswith("__"):
                            functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        classes.append(node.name)

                rel_path = str(py_file.relative_to(self.project_root))
                self.source_files[rel_path] = SourceFile(
                    path=py_file,
                    lines=len(content.splitlines()),
                    functions=functions,
                    classes=classes,
                )
            except Exception as e:
                print(f"  âš ï¸ Erreur parsing {py_file}: {e}")

        print(f"  âœ“ {len(self.source_files)} fichiers source dÃ©tectÃ©s")
        return self.source_files

    def scan_test_files(self) -> dict[str, TestFile]:
        """Scanne tous les fichiers de test."""
        print("ðŸ” Scan des fichiers de test...")

        for py_file in self.tests_dir.rglob("test_*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8-sig")  # Handle BOM

                # Trouver les fonctions de test
                test_funcs = re.findall(r"def (test_\w+)\s*\(", content)

                # DÃ©tecter les patterns inefficaces
                patterns = {}
                for pattern_name, pattern_regex in self.INEFFECTIVE_PATTERNS.items():
                    matches = re.findall(pattern_regex, content, re.MULTILINE)
                    if matches:
                        patterns[pattern_name] = len(matches)

                rel_path = str(py_file.relative_to(self.project_root))
                self.test_files[rel_path] = TestFile(
                    path=py_file,
                    lines=len(content.splitlines()),
                    test_functions=test_funcs,
                    test_patterns=patterns,
                )
            except Exception as e:
                print(f"  âš ï¸ Erreur parsing {py_file}: {e}")

        print(f"  âœ“ {len(self.test_files)} fichiers de test dÃ©tectÃ©s")
        return self.test_files

    def find_matching_tests(self, source_path: str) -> list[str]:
        """Trouve les fichiers de test correspondant Ã  un fichier source."""
        matches = []

        # Extraire le nom du module
        src_name = Path(source_path).stem  # ex: "recettes" de "src/services/recettes.py"

        # Patterns de correspondance
        patterns = [
            f"test_{src_name}.py",  # test_recettes.py
            f"test_{src_name}_",  # test_recettes_service.py
            f"{src_name}_test.py",  # recettes_test.py (moins courant)
        ]

        for test_path in self.test_files.keys():
            test_name = Path(test_path).name
            for pattern in patterns:
                if pattern in test_name or test_name == pattern:
                    matches.append(test_path)
                    break

        return list(set(matches))

    def run_coverage_for_file(self, source_path: str) -> CoverageResult | None:
        """ExÃ©cute la couverture pour un fichier spÃ©cifique."""
        test_paths = self.find_matching_tests(source_path)

        if not test_paths:
            return CoverageResult(
                source_path=source_path,
                test_paths=[],
                coverage_percent=0.0,
                covered_lines=0,
                total_lines=self.source_files.get(source_path, SourceFile(Path(), 0, [], [])).lines,
                missing_lines=[],
                is_effective=False,
                issues=["Aucun fichier de test trouvÃ©"],
            )

        # ExÃ©cuter pytest avec coverage sur les tests correspondants
        try:
            cmd = [
                "python",
                "-m",
                "pytest",
                *test_paths,
                f"--cov={source_path.replace(os.sep, '/')}",
                "--cov-report=json",
                "-q",
                "--tb=no",
            ]

            result = subprocess.run(
                cmd, cwd=str(self.project_root), capture_output=True, text=True, timeout=60
            )

            # Lire le rapport JSON
            cov_json = self.project_root / "coverage.json"
            if cov_json.exists():
                with open(cov_json) as f:
                    data = json.load(f)

                file_data = data.get("files", {}).get(source_path, {})

                covered = file_data.get("summary", {}).get("covered_lines", 0)
                total = file_data.get("summary", {}).get("num_statements", 1)
                missing = file_data.get("missing_lines", [])
                pct = (covered / total * 100) if total > 0 else 0.0

                # Analyser l'efficacitÃ© des tests
                issues = []
                is_effective = True

                for test_path in test_paths:
                    test_file = self.test_files.get(test_path)
                    if test_file:
                        patterns = test_file.test_patterns
                        if patterns.get("hasattr", 0) > 5:
                            issues.append(f"Trop de hasattr ({patterns['hasattr']})")
                            is_effective = False
                        if (
                            patterns.get("import_only", 0) > 10
                            and len(test_file.test_functions) < 5
                        ):
                            issues.append("Principalement des imports")
                            is_effective = False
                        if patterns.get("mock_session", 0) > 10:
                            issues.append("Mocking excessif de session")

                if pct < self.threshold:
                    is_effective = False
                    issues.append(f"Couverture insuffisante ({pct:.1f}% < {self.threshold}%)")

                return CoverageResult(
                    source_path=source_path,
                    test_paths=test_paths,
                    coverage_percent=round(pct, 1),
                    covered_lines=covered,
                    total_lines=total,
                    missing_lines=missing[:20],  # Limiter Ã  20 lignes
                    is_effective=is_effective,
                    issues=issues,
                )

        except subprocess.TimeoutExpired:
            return CoverageResult(
                source_path=source_path,
                test_paths=test_paths,
                coverage_percent=0.0,
                covered_lines=0,
                total_lines=0,
                missing_lines=[],
                is_effective=False,
                issues=["Timeout during coverage run"],
            )
        except Exception as e:
            return CoverageResult(
                source_path=source_path,
                test_paths=test_paths,
                coverage_percent=0.0,
                covered_lines=0,
                total_lines=0,
                missing_lines=[],
                is_effective=False,
                issues=[f"Error: {str(e)}"],
            )

        return None

    def run_full_audit(self) -> dict[str, CoverageResult]:
        """ExÃ©cute l'audit complet."""
        self.scan_source_files()
        self.scan_test_files()

        print("\nðŸ“Š Calcul de la couverture...")

        total = len(self.source_files)
        for i, source_path in enumerate(self.source_files.keys(), 1):
            print(f"  [{i}/{total}] {Path(source_path).name}...", end="\r")
            result = self.run_coverage_for_file(source_path)
            if result:
                self.coverage_data[source_path] = result

        print(f"\n  âœ“ {len(self.coverage_data)} fichiers analysÃ©s")
        return self.coverage_data

    def generate_csv_report(self, output_path: Path) -> None:
        """GÃ©nÃ¨re le rapport CSV."""
        print(f"\nðŸ“ GÃ©nÃ©ration du rapport: {output_path}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "source_file",
                    "test_files",
                    "coverage_pct",
                    "covered_lines",
                    "total_lines",
                    "is_effective",
                    "issues",
                    "action_needed",
                ]
            )

            for source_path, result in sorted(self.coverage_data.items()):
                action = "OK"
                if not result.is_effective:
                    if not result.test_paths:
                        action = "CREATE_TESTS"
                    elif result.coverage_percent < self.threshold:
                        action = "IMPROVE_TESTS"
                    else:
                        action = "REFACTOR_TESTS"

                writer.writerow(
                    [
                        source_path,
                        ";".join(result.test_paths),
                        result.coverage_percent,
                        result.covered_lines,
                        result.total_lines,
                        result.is_effective,
                        ";".join(result.issues),
                        action,
                    ]
                )

        print(f"  âœ“ Rapport gÃ©nÃ©rÃ© avec {len(self.coverage_data)} entrÃ©es")

    def print_summary(self) -> None:
        """Affiche un rÃ©sumÃ© de l'audit."""
        effective = sum(1 for r in self.coverage_data.values() if r.is_effective)
        no_tests = sum(1 for r in self.coverage_data.values() if not r.test_paths)
        low_coverage = sum(
            1
            for r in self.coverage_data.values()
            if r.test_paths and r.coverage_percent < self.threshold
        )

        avg_coverage = (
            sum(r.coverage_percent for r in self.coverage_data.values()) / len(self.coverage_data)
            if self.coverage_data
            else 0
        )

        print("\n" + "=" * 60)
        print("ðŸ“Š RÃ‰SUMÃ‰ DE L'AUDIT")
        print("=" * 60)
        print(f"  Fichiers source analysÃ©s: {len(self.source_files)}")
        print(f"  Fichiers de test: {len(self.test_files)}")
        print(f"  Couverture moyenne: {avg_coverage:.1f}%")
        print()
        print(f"  âœ… Tests efficaces (â‰¥{self.threshold}%): {effective}")
        print(f"  âŒ Sans tests: {no_tests}")
        print(f"  âš ï¸  Couverture insuffisante: {low_coverage}")
        print("=" * 60)

        # Top 10 des fichiers sans couverture
        if no_tests > 0:
            print("\nðŸ”´ Fichiers prioritaires Ã  tester:")
            no_test_files = [
                (path, self.source_files[path].lines)
                for path, r in self.coverage_data.items()
                if not r.test_paths
            ]
            no_test_files.sort(key=lambda x: x[1], reverse=True)
            for path, lines in no_test_files[:10]:
                print(f"   - {path} ({lines} lignes)")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Audit des tests et couverture")
    parser.add_argument(
        "--output", "-o", default="reports/test_audit.csv", help="Chemin du fichier de sortie CSV"
    )
    parser.add_argument(
        "--threshold", "-t", type=float, default=80.0, help="Seuil de couverture minimum (%)"
    )
    parser.add_argument(
        "--quick", "-q", action="store_true", help="Mode rapide (sans exÃ©cution coverage)"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    auditor = TestAuditor(project_root, threshold=args.threshold)

    if args.quick:
        # Mode rapide: juste le mapping sans coverage
        auditor.scan_source_files()
        auditor.scan_test_files()

        print("\nðŸ“‹ Mapping source â†’ test:")
        for source_path in sorted(auditor.source_files.keys())[:30]:
            tests = auditor.find_matching_tests(source_path)
            status = "âœ“" if tests else "âœ—"
            tests_str = ", ".join(Path(t).name for t in tests) if tests else "AUCUN"
            print(f"  {status} {Path(source_path).name} â†’ {tests_str}")
    else:
        auditor.run_full_audit()
        auditor.generate_csv_report(Path(args.output))
        auditor.print_summary()


if __name__ == "__main__":
    main()
