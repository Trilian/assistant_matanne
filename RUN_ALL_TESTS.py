#!/usr/bin/env python3
"""
Test Launcher for ALL Phases (Core, API, UI, Utils, Modules, Services, E2E)

Provides quick access to run all test suites with various options.
"""

import subprocess
import sys
import os
from pathlib import Path


class TestLauncher:
    """Unified test launcher for all test phases."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
    
    def run_command(self, cmd, description=""):
        """Execute pytest command."""
        if description:
            print(f"\n{'='*70}")
            print(f"▶️  {description}")
            print(f"{'='*70}\n")
        
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    
    # ═══════════════════════════════════════════════════════════
    # PHASE 1: Core Tests
    # ═══════════════════════════════════════════════════════════
    
    def core_week1(self):
        """Run core Week 1 tests."""
        return self.run_command(
            "pytest tests/core/test_week1.py -v",
            "CORE - Week 1: Base, Config, Database, Decorators"
        )
    
    def core_week2(self):
        """Run core Week 2 tests."""
        return self.run_command(
            "pytest tests/core/test_week2.py -v",
            "CORE - Week 2: Cache, State, Logging, Errors"
        )
    
    def core_week3_4(self):
        """Run core Week 3-4 tests."""
        return self.run_command(
            "pytest tests/core/test_week3_4.py -v",
            "CORE - Week 3-4: Integration, Performance, Security"
        )
    
    def core_all(self):
        """Run all core tests."""
        return self.run_command(
            "pytest tests/core/ -v --cov=src/core --cov-report=term-missing",
            "CORE - All Tests (684 tests)"
        )
    
    # ═══════════════════════════════════════════════════════════
    # PHASE 2: API Tests
    # ═══════════════════════════════════════════════════════════
    
    def api_week1_2(self):
        """Run API Week 1-2 tests."""
        return self.run_command(
            "pytest tests/api/test_week1_2.py -v",
            "API - Week 1-2: GET/POST Endpoints, Auth"
        )
    
    def api_week3_4(self):
        """Run API Week 3-4 tests."""
        return self.run_command(
            "pytest tests/api/test_week3_4.py -v",
            "API - Week 3-4: PUT/DELETE, Rate Limiting, Integration"
        )
    
    def api_all(self):
        """Run all API tests."""
        return self.run_command(
            "pytest tests/api/ -v --cov=src/api --cov-report=term-missing",
            "API - All Tests (270 tests)"
        )
    
    # ═══════════════════════════════════════════════════════════
    # PHASE 3: UI & Utils Tests
    # ═══════════════════════════════════════════════════════════
    
    def ui_week1(self):
        """Run UI Week 1 tests."""
        return self.run_command(
            "pytest tests/ui/test_week1.py -v",
            "UI - Week 1: Atoms, Forms, Data Display"
        )
    
    def ui_week2(self):
        """Run UI Week 2 tests."""
        return self.run_command(
            "pytest tests/ui/test_week2.py -v",
            "UI - Week 2: Layouts, DataGrid, Charts"
        )
    
    def ui_week3_4(self):
        """Run UI Week 3-4 tests."""
        return self.run_command(
            "pytest tests/ui/test_week3_4.py -v",
            "UI - Week 3-4: Feedback, Modals, Integration"
        )
    
    def ui_all(self):
        """Run all UI tests."""
        return self.run_command(
            "pytest tests/ui/ -v --cov=src/ui --cov-report=term-missing",
            "UI - All Tests (169 tests)"
        )
    
    def utils_week1_2(self):
        """Run Utils Week 1-2 tests."""
        return self.run_command(
            "pytest tests/utils/test_week1_2.py -v",
            "UTILS - Week 1-2: Formatters, Validators"
        )
    
    def utils_week3_4(self):
        """Run Utils Week 3-4 tests."""
        return self.run_command(
            "pytest tests/utils/test_week3_4.py -v",
            "UTILS - Week 3-4: Conversions, Media, Integration"
        )
    
    def utils_all(self):
        """Run all Utils tests."""
        return self.run_command(
            "pytest tests/utils/ -v --cov=src/utils --cov-report=term-missing",
            "UTILS - All Tests (138 tests)"
        )
    
    def ui_utils_all(self):
        """Run all UI and Utils tests."""
        return self.run_command(
            "pytest tests/ui tests/utils -v --cov=src/ui --cov=src/utils",
            "UI + UTILS - All Tests (307 tests)"
        )
    
    # ═══════════════════════════════════════════════════════════
    # PHASE 4: Modules, Services, E2E Tests
    # ═══════════════════════════════════════════════════════════
    
    def modules_week1_2(self):
        """Run Modules Week 1-2 tests."""
        return self.run_command(
            "pytest tests/modules/test_week1_2.py -v",
            "MODULES - Week 1-2: Accueil, Cuisine, Planning"
        )
    
    def modules_week3_4(self):
        """Run Modules Week 3-4 tests."""
        return self.run_command(
            "pytest tests/modules/test_week3_4.py -v",
            "MODULES - Week 3-4: Famille, Planning, Error Handling"
        )
    
    def modules_all(self):
        """Run all Modules tests."""
        return self.run_command(
            "pytest tests/modules/ -v --cov=src/modules --cov-report=term-missing",
            "MODULES - All Tests (167 tests)"
        )
    
    def services_week1_2(self):
        """Run Services Week 1-2 tests."""
        return self.run_command(
            "pytest tests/services/test_week1_2.py -v",
            "SERVICES - Week 1-2: CRUD, AI, Cache, Factories"
        )
    
    def services_week3_4(self):
        """Run Services Week 3-4 tests."""
        return self.run_command(
            "pytest tests/services/test_week3_4.py -v",
            "SERVICES - Week 3-4: Orchestration, Error Handling"
        )
    
    def services_all(self):
        """Run all Services tests."""
        return self.run_command(
            "pytest tests/services/ -v --cov=src/services --cov-report=term-missing",
            "SERVICES - All Tests (145 tests)"
        )
    
    def e2e_all(self):
        """Run all E2E tests."""
        return self.run_command(
            "pytest tests/e2e/ -v -m e2e",
            "E2E - All Tests (29 user workflows)"
        )
    
    def phase4_all(self):
        """Run all Phase 4 tests."""
        return self.run_command(
            "pytest tests/modules tests/services tests/e2e -v --cov=src/modules --cov=src/services",
            "PHASE 4 - All Tests (341 tests)"
        )
    
    # ═══════════════════════════════════════════════════════════
    # COMPREHENSIVE: All Tests
    # ═══════════════════════════════════════════════════════════
    
    def all_tests(self):
        """Run all tests across all phases."""
        return self.run_command(
            "pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v",
            "ALL TESTS - Complete System (1,600+ tests)"
        )
    
    def all_tests_fast(self):
        """Run all tests without coverage (faster)."""
        return self.run_command(
            "pytest tests/ -v",
            "ALL TESTS - Fast (no coverage)"
        )
    
    def all_by_marker(self, marker):
        """Run all tests with specific marker."""
        return self.run_command(
            f"pytest tests/ -v -m {marker}",
            f"ALL TESTS - Marker: {marker.upper()}"
        )
    
    # ═══════════════════════════════════════════════════════════
    # REPORTING
    # ═══════════════════════════════════════════════════════════
    
    def coverage_report(self):
        """Generate HTML coverage report."""
        self.run_command(
            "pytest tests/ --cov=src --cov-report=html --cov-report=term-missing",
            "COVERAGE REPORT - Generating HTML report"
        )
        print("\n✅ HTML coverage report: htmlcov/index.html")
    
    def test_status(self):
        """Show test status."""
        print("\n" + "="*70)
        print("📊 TEST SYSTEM STATUS")
        print("="*70)
        
        stats = {
            "Core": ("tests/core", "684"),
            "API": ("tests/api", "270"),
            "UI": ("tests/ui", "169"),
            "Utils": ("tests/utils", "138"),
            "Modules": ("tests/modules", "167"),
            "Services": ("tests/services", "145+"),
            "E2E": ("tests/e2e", "29"),
        }
        
        for name, (path, count) in stats.items():
            if os.path.exists(self.project_root / path):
                print(f"✅ {name:12} {count:6} tests")
            else:
                print(f"❌ {name:12} {count:6} tests - NOT FOUND")
        
        total = "1,600+"
        print(f"\n{'─'*40}")
        print(f"📈 TOTAL: {total} tests")
    
    def help(self):
        """Show help message."""
        print("""
╔════════════════════════════════════════════════════════════════════╗
║           UNIFIED TEST LAUNCHER - ALL PHASES                       ║
╚════════════════════════════════════════════════════════════════════╝

USAGE:
  python RUN_ALL_TESTS.py [command]

PHASE 1 - CORE (684 tests):
  core_week1      Run Week 1 tests
  core_week2      Run Week 2 tests
  core_week3_4    Run Week 3-4 tests
  core_all        Run all core tests

PHASE 2 - API (270 tests):
  api_week1_2     Run Week 1-2 tests
  api_week3_4     Run Week 3-4 tests
  api_all         Run all API tests

PHASE 3 - UI & UTILS (307 tests):
  ui_week1        Run UI Week 1 tests
  ui_week2        Run UI Week 2 tests
  ui_week3_4      Run UI Week 3-4 tests
  ui_all          Run all UI tests
  utils_week1_2   Run Utils Week 1-2 tests
  utils_week3_4   Run Utils Week 3-4 tests
  utils_all       Run all Utils tests
  ui_utils_all    Run all UI & Utils tests

PHASE 4 - MODULES, SERVICES, E2E (341 tests):
  modules_week1_2 Run Modules Week 1-2 tests
  modules_week3_4 Run Modules Week 3-4 tests
  modules_all     Run all Modules tests
  services_week1_2 Run Services Week 1-2 tests
  services_week3_4 Run Services Week 3-4 tests
  services_all    Run all Services tests
  e2e_all         Run all E2E tests
  phase4_all      Run all Phase 4 tests

COMPREHENSIVE:
  all_tests       Run all tests (1,600+) with coverage report
  all_tests_fast  Run all tests without coverage (faster)
  all_unit        Run all unit tests
  all_integration Run all integration tests
  all_e2e         Run all E2E tests
  all_performance Run all performance tests

REPORTING:
  coverage_report Generate HTML coverage report
  status          Show test system status
  help            Show this help message

EXAMPLES:
  python RUN_ALL_TESTS.py core_all
  python RUN_ALL_TESTS.py all_tests
  python RUN_ALL_TESTS.py all_integration
  python RUN_ALL_TESTS.py coverage_report
        """)


def main():
    """Main entry point."""
    launcher = TestLauncher()
    
    # Show status by default
    launcher.test_status()
    
    if len(sys.argv) < 2:
        print("\nNo command specified. Use 'help' to see available commands.")
        launcher.help()
        return 0
    
    command = sys.argv[1]
    
    # Check for direct method call
    if hasattr(launcher, command):
        method = getattr(launcher, command)
        if callable(method):
            try:
                method()
            except Exception as e:
                print(f"❌ Error: {e}")
                return 1
        else:
            print(f"❌ Unknown command: {command}")
            return 1
    else:
        print(f"❌ Unknown command: {command}")
        launcher.help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
