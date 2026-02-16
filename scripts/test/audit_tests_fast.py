#!/usr/bin/env python
"""
Audit rapide des tests - Analyse des patterns et mapping sans coverage.

Ce script analyse rapidement:
1. Le mapping source/test
2. Les patterns de tests inefficaces
3. GÃ©nÃ¨re un rapport actionnable

Usage:
    python scripts/audit_tests_fast.py
"""

import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


@dataclass
class TestAnalysis:
    """Analyse d'un fichier de test."""

    path: str
    lines: int
    nb_tests: int
    patterns: dict[str, int] = field(default_factory=dict)
    score: float = 0.0  # 0-100, qualitÃ© estimÃ©e
    issues: list[str] = field(default_factory=list)


# Patterns indiquant des tests potentiellement inefficaces
INEFFECTIVE_PATTERNS = {
    "hasattr": (r"\bhasattr\s*\(", 3, "hasattr checks (ne teste pas la logique)"),
    "import_check": (r"def test_\w+import|def test_import", 5, "Tests d'import uniquement"),
    "pass_body": (
        r"def test_\w+[^:]+:\s*\n\s+(?:\"\"\"[^\"]*\"\"\"\s*\n\s+)?pass\b",
        10,
        "Tests avec pass",
    ),
    "mock_all": (r"@patch\.object\([^)]+\)\s*\n\s*@patch\.object", 4, "Mocking excessif"),
    "assert_true_only": (r"\bassert True\b", 5, "assert True sans condition"),
    "no_assert": (r"def test_\w+[^:]+:[^}]+return\b", 3, "Tests sans assertion"),
}

# Patterns positifs (bonnes pratiques)
POSITIVE_PATTERNS = {
    "db_fixture": (r"def test_\w+\([^)]*db\s*:", 2, "Utilise fixture DB"),
    "real_assert": (r"assert\s+\w+\.\w+\s*==", 2, "Assertion sur attribut rÃ©el"),
    "exception_test": (r"pytest\.raises\(|with self\.assertRaises", 3, "Test d'exception"),
}


def analyze_test_file(filepath: Path) -> TestAnalysis:
    """Analyse un fichier de test."""
    try:
        content = filepath.read_text(encoding="utf-8-sig")
    except Exception:
        return TestAnalysis(path=str(filepath), lines=0, nb_tests=0)

    lines = len(content.splitlines())

    # Compter les tests
    test_matches = re.findall(r"def (test_\w+)\s*\(", content)
    nb_tests = len(test_matches)

    if nb_tests == 0:
        return TestAnalysis(path=str(filepath), lines=lines, nb_tests=0)

    patterns_found = {}
    issues = []
    score = 100.0  # Start with perfect score

    # DÃ©tecter patterns nÃ©gatifs
    for name, (pattern, penalty, desc) in INEFFECTIVE_PATTERNS.items():
        matches = re.findall(pattern, content, re.MULTILINE)
        count = len(matches)
        if count > 0:
            patterns_found[name] = count
            # PÃ©nalitÃ© proportionnelle au nombre de matchs
            score -= min(30, count * penalty)
            if count >= 5:
                issues.append(f"{desc} ({count}x)")

    # Bonus pour patterns positifs
    for name, (pattern, bonus, desc) in POSITIVE_PATTERNS.items():
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            patterns_found[name] = len(matches)
            score += min(15, len(matches) * bonus)

    # Ratio tests/lignes (trop peu = tests superficiels)
    test_density = nb_tests / max(1, lines / 50)
    if test_density > 3:  # Plus de 3 tests par 50 lignes = probablement hasattr
        score -= 10
        issues.append("DensitÃ© tests trÃ¨s haute (tests superficiels?)")

    score = max(0, min(100, score))

    return TestAnalysis(
        path=str(filepath.relative_to(filepath.parent.parent.parent.parent)),
        lines=lines,
        nb_tests=nb_tests,
        patterns=patterns_found,
        score=round(score, 1),
        issues=issues,
    )


def find_source_for_test(test_path: str, source_files: dict[str, Path]) -> list[str]:
    """Trouve les fichiers source correspondant Ã  un test."""
    test_name = Path(test_path).stem

    # Extraire le nom de module du test
    # test_recettes.py -> recettes
    # test_recettes_service.py -> recettes
    # test_recettes_coverage.py -> recettes

    patterns = [
        r"^test_([a-z_]+?)(?:_service|_coverage|_deep|_extended|_logic|_ui|_integration)?$",
        r"^test_([a-z_]+)$",
    ]

    module_name = None
    for pattern in patterns:
        match = re.match(pattern, test_name)
        if match:
            module_name = match.group(1)
            break

    if not module_name:
        return []

    # Chercher les fichiers source correspondants
    matches = []
    for src_path in source_files.keys():
        src_name = Path(src_path).stem
        if src_name == module_name or src_name.startswith(module_name + "_"):
            matches.append(src_path)

    return matches


def run_audit(project_root: Path, output_csv: Path):
    """ExÃ©cute l'audit rapide."""
    src_dir = project_root / "src"
    tests_dir = project_root / "tests"

    print("[*] Scan des fichiers source...")
    source_files = {}
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            rel = str(py_file.relative_to(project_root))
            try:
                content = py_file.read_text(encoding="utf-8-sig")
                source_files[rel] = py_file
            except:
                pass
    print(f"    {len(source_files)} fichiers source")

    print("[*] Analyse des fichiers de test...")
    test_analyses: list[TestAnalysis] = []
    for py_file in tests_dir.rglob("test_*.py"):
        if "__pycache__" not in str(py_file):
            analysis = analyze_test_file(py_file)
            test_analyses.append(analysis)

    print(f"    {len(test_analyses)} fichiers de test analysÃ©s")

    # Mapper tests -> sources
    test_to_sources = {}
    for analysis in test_analyses:
        sources = find_source_for_test(analysis.path, source_files)
        test_to_sources[analysis.path] = sources

    # Identifier sources sans tests
    covered_sources = set()
    for sources in test_to_sources.values():
        covered_sources.update(sources)

    uncovered_sources = [s for s in source_files.keys() if s not in covered_sources]

    # Identifier tests inefficaces
    ineffective_tests = [a for a in test_analyses if a.score < 50]
    low_quality_tests = [a for a in test_analyses if 50 <= a.score < 70]
    good_tests = [a for a in test_analyses if a.score >= 70]

    # GÃ©nÃ©rer le rapport CSV
    print(f"\n[*] GÃ©nÃ©ration du rapport: {output_csv}")
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "type",
                "path",
                "lines",
                "nb_tests",
                "quality_score",
                "mapped_sources",
                "issues",
                "action",
            ]
        )

        # Tests
        for analysis in sorted(test_analyses, key=lambda x: x.score):
            sources = test_to_sources.get(analysis.path, [])

            if analysis.score < 40:
                action = "DELETE"
            elif analysis.score < 60:
                action = "REWRITE"
            elif analysis.score < 75:
                action = "IMPROVE"
            else:
                action = "OK"

            writer.writerow(
                [
                    "test",
                    analysis.path,
                    analysis.lines,
                    analysis.nb_tests,
                    analysis.score,
                    ";".join(sources),
                    "; ".join(analysis.issues),
                    action,
                ]
            )

        # Sources sans tests
        for src in sorted(uncovered_sources):
            try:
                lines = len(Path(project_root / src).read_text(encoding="utf-8-sig").splitlines())
            except:
                lines = 0
            writer.writerow(
                ["source", src, lines, 0, 0, "", "Pas de test correspondant", "CREATE_TESTS"]
            )

    # RÃ©sumÃ©
    print("\n" + "=" * 70)
    print("RESUME DE L'AUDIT")
    print("=" * 70)
    print(f"\nFichiers source: {len(source_files)}")
    print(f"Fichiers de test: {len(test_analyses)}")
    print(f"Tests totaux: {sum(a.nb_tests for a in test_analyses)}")

    print(f"\n[+] Tests de qualitÃ© (>=70): {len(good_tests)}")
    print(f"[~] Tests Ã  amÃ©liorer (50-70): {len(low_quality_tests)}")
    print(f"[-] Tests inefficaces (<50): {len(ineffective_tests)}")
    print(f"[!] Sources sans tests: {len(uncovered_sources)}")

    # Top tests Ã  supprimer/rÃ©Ã©crire
    if ineffective_tests:
        print("\n--- TESTS A SUPPRIMER/REECRIRE (score < 50) ---")
        for a in sorted(ineffective_tests, key=lambda x: x.score)[:15]:
            print(f"  {a.score:5.1f} | {a.path}")
            for issue in a.issues:
                print(f"        -> {issue}")

    # Top sources sans tests (par taille)
    if uncovered_sources:
        print("\n--- SOURCES PRIORITAIRES A TESTER ---")
        sized_uncovered = []
        for src in uncovered_sources:
            try:
                lines = len(Path(project_root / src).read_text(encoding="utf-8-sig").splitlines())
                sized_uncovered.append((src, lines))
            except:
                pass
        sized_uncovered.sort(key=lambda x: x[1], reverse=True)
        for src, lines in sized_uncovered[:15]:
            print(f"  {lines:5d} lignes | {src}")

    print("\n" + "=" * 70)
    print(f"Rapport CSV: {output_csv}")
    print("=" * 70)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    output = project_root / "reports" / "test_audit_fast.csv"
    run_audit(project_root, output)
