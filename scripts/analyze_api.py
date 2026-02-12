#!/usr/bin/env python3
"""
API Analysis & Maintenance Tool
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Analyse src/api/, dÃ©tecte patterns, suggÃ¨re improvements.
Similaire Ã  scripts/manage_tests.py mais pour API.
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional
from collections import defaultdict


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: DATA STRUCTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

@dataclass
class APIEndpoint:
    """ReprÃ©sente un endpoint API."""
    path: str
    method: str  # GET, POST, PUT, DELETE, PATCH
    function_name: str
    file: str
    line: int
    requires_auth: bool
    response_model: Optional[str]
    parameters: List[str]


@dataclass
class APIFile:
    """ReprÃ©sente un fichier API."""
    path: Path
    name: str
    lines: int
    endpoints: int
    schemas: int
    middleware: int
    imports: Set[str]
    issues: List[str]


@dataclass
class APISuggestion:
    """Suggestion d'amÃ©lioration API."""
    file: str
    issue: str
    severity: str  # high, medium, low
    suggestion: str
    example: Optional[str]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: API ANALYZER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class APIAnalyzer:
    """Analyse les fichiers src/api/."""

    def __init__(self, api_dir: Path = Path("src/api")):
        self.api_dir = api_dir
        self.files: Dict[str, APIFile] = {}
        self.endpoints: List[APIEndpoint] = []
        self.suggestions: List[APISuggestion] = []

    def analyze_all(self) -> Dict:
        """Analyse tous les fichiers API."""
        print("ðŸ” Analyzing API files...")

        api_files = list(self.api_dir.glob("*.py"))
        
        for api_file in api_files:
            if api_file.name != "__init__.py":
                self._analyze_file(api_file)

        self._detect_endpoints()
        self._generate_suggestions()

        return self._generate_report()

    def _analyze_file(self, filepath: Path) -> None:
        """Analyse un seul fichier API."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            lines = len(content.split('\n'))

            # Compte les Ã©lÃ©ments
            endpoints = len(re.findall(r'@app\.(get|post|put|delete|patch)', content))
            schemas = len([n for n in ast.walk(tree) 
                          if isinstance(n, ast.ClassDef) and 'Base' in str(n.bases)])
            middleware = len(re.findall(r'@app\.middleware', content))

            # Extrait les imports
            imports = self._extract_imports(tree)

            # DÃ©tecte les issues
            issues = self._detect_issues(content)

            self.files[filepath.name] = APIFile(
                path=filepath,
                name=filepath.name,
                lines=lines,
                endpoints=endpoints,
                schemas=schemas,
                middleware=middleware,
                imports=imports,
                issues=issues
            )

        except Exception as e:
            print(f"  âš ï¸  Error analyzing {filepath}: {e}")

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extrait les imports."""
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        return imports

    def _detect_issues(self, content: str) -> List[str]:
        """DÃ©tecte les issues courants."""
        issues = []

        # Issue 1: Pas de docstrings
        if content.count('"""') < 5:
            issues.append("Missing docstrings (< 5)")

        # Issue 2: Trop de logique dans endpoints
        if len(re.findall(r'def.*:.*\n.*\n.*\n.*\n.*\n', content)) > 3:
            issues.append("Complex endpoint logic (>5 lines)")

        # Issue 3: Hardcoded values
        if re.search(r'"(http|localhost|127\.0\.0\.1)"', content):
            issues.append("Hardcoded URLs/IPs")

        # Issue 4: Pas de error handling
        if 'try:' not in content or 'HTTPException' not in content:
            issues.append("Limited error handling")

        # Issue 5: Trop d'endpoints dans un fichier
        endpoints_count = len(re.findall(r'@app\.(get|post|put|delete|patch)', content))
        if endpoints_count > 15:
            issues.append(f"Too many endpoints in single file ({endpoints_count})")

        return issues

    def _detect_endpoints(self) -> None:
        """DÃ©tecte les endpoints dÃ©finis."""
        print("  âœ“ Detecting endpoints...")

        for filename, fileinfo in self.files.items():
            with open(fileinfo.path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Regex patterns pour endpoints
            pattern = r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
            for match in re.finditer(pattern, content):
                method = match.group(1).upper()
                path = match.group(2)

                self.endpoints.append(APIEndpoint(
                    path=path,
                    method=method,
                    function_name="",  # TODO: Extract function name
                    file=filename,
                    line=content[:match.start()].count('\n'),
                    requires_auth=False,  # TODO: Detect
                    response_model=None,  # TODO: Extract
                    parameters=[]  # TODO: Extract
                ))

    def _generate_suggestions(self) -> None:
        """GÃ©nÃ¨re les suggestions."""
        print("  âœ“ Generating suggestions...")

        for filename, fileinfo in self.files.items():
            # Suggestion 1: Trop d'endpoints
            if fileinfo.endpoints > 15:
                self.suggestions.append(APISuggestion(
                    file=filename,
                    issue=f"Too many endpoints ({fileinfo.endpoints})",
                    severity="medium",
                    suggestion="Split into separate routers",
                    example="from fastapi import APIRouter; router = APIRouter()"
                ))

            # Suggestion 2: Pas de documentation
            if fileinfo.endpoints > 0 and len(fileinfo.imports) < 5:
                self.suggestions.append(APISuggestion(
                    file=filename,
                    issue="Limited imports (possible missing dependencies)",
                    severity="low",
                    suggestion="Check if all needed packages imported",
                    example=None
                ))

            # Suggestion 3: Issues dÃ©tectÃ©es
            for issue in fileinfo.issues:
                self.suggestions.append(APISuggestion(
                    file=filename,
                    issue=issue,
                    severity="high" if "error" in issue.lower() else "medium",
                    suggestion="See file for details",
                    example=None
                ))

    def _generate_report(self) -> Dict:
        """GÃ©nÃ¨re le rapport."""
        return {
            'total_files': len(self.files),
            'total_endpoints': len(self.endpoints),
            'total_lines': sum(f.lines for f in self.files.values()),
            'total_schemas': sum(f.schemas for f in self.files.values()),
            'files': {k: asdict(v) for k, v in self.files.items()},
            'endpoints': [asdict(e) for e in self.endpoints],
            'suggestions': [asdict(s) for s in self.suggestions],
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: REPORT GENERATOR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class APIReportGenerator:
    """GÃ©nÃ¨re rapports pour API."""

    @staticmethod
    def print_analysis(report: Dict) -> None:
        """Affiche rapport d'analyse."""
        print("\n" + "="*80)
        print("API ANALYSIS REPORT")
        print("="*80 + "\n")

        print(f"ðŸ“Š OVERVIEW")
        print(f"  Files: {report['total_files']}")
        print(f"  Endpoints: {report['total_endpoints']}")
        print(f"  Total lines: {report['total_lines']}")
        print(f"  Schemas: {report['total_schemas']}")
        print(f"  Suggestions: {len(report['suggestions'])}\n")

        print(f"ðŸ“‹ FILES")
        for filename, fileinfo in report['files'].items():
            print(f"  {filename}")
            print(f"    Lines: {fileinfo['lines']}, Endpoints: {fileinfo['endpoints']}, Schemas: {fileinfo['schemas']}")
            if fileinfo['issues']:
                for issue in fileinfo['issues']:
                    print(f"    âš ï¸  {issue}")

        if report['endpoints']:
            print(f"\nðŸ”Œ ENDPOINTS")
            for endpoint in report['endpoints'][:10]:  # First 10
                print(f"  {endpoint['method']:6} {endpoint['path']:30} ({endpoint['file']})")

        if report['suggestions']:
            print(f"\nðŸ’¡ SUGGESTIONS")
            for i, sugg in enumerate(report['suggestions'][:5], 1):
                print(f"  {i}. [{sugg['severity'].upper()}] {sugg['file']}")
                print(f"     {sugg['issue']}")
                print(f"     â†’ {sugg['suggestion']}\n")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: CLI INTERFACE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def main():
    """Point d'entrÃ©e principal."""
    import sys

    analyzer = APIAnalyzer()
    report = analyzer.analyze_all()

    if len(sys.argv) > 1 and sys.argv[1] == "json":
        import json
        # Convert sets to lists for JSON
        clean_report = report.copy()
        for file_info in clean_report['files'].values():
            file_info['imports'] = list(file_info['imports'])
        print(json.dumps(clean_report, indent=2))
    else:
        APIReportGenerator.print_analysis(report)


if __name__ == '__main__':
    main()
