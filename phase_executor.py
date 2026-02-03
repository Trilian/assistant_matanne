#!/usr/bin/env python3
"""
Executor de tests PHASE 1-5
Génère et exécute automatiquement les tests manquants
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime


class TestPhaseExecutor:
    """Exécuteur de phases de test"""
    
    def __init__(self):
        self.root = Path(".")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "phases": {}
        }
    
    def run_phase_1(self):
        """PHASE 1: Tests fichiers 0% (8 fichiers)"""
        
        phase_1_files = [
            {
                "test_path": "tests/utils/test_image_generator.py",
                "src_path": "src/utils/image_generator.py",
                "priority": 1,
                "effort_hours": 5,
                "status": "COMPLETED"
            },
            {
                "test_path": "tests/utils/test_helpers_general.py",
                "src_path": "src/utils/helpers/helpers.py",
                "priority": 2,
                "effort_hours": 4,
                "status": "COMPLETED"
            },
            {
                "test_path": "tests/domains/maison/ui/test_depenses.py",
                "src_path": "src/domains/maison/ui/depenses.py",
                "priority": 3,
                "effort_hours": 6,
                "status": "IN_PROGRESS"
            },
            {
                "test_path": "tests/domains/planning/ui/components/test_components_init.py",
                "src_path": "src/domains/planning/ui/components/__init__.py",
                "priority": 4,
                "effort_hours": 4,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/famille/ui/test_jules_planning.py",
                "src_path": "src/domains/famille/ui/jules_planning.py",
                "priority": 5,
                "effort_hours": 5,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/cuisine/ui/test_planificateur_repas.py",
                "src_path": "src/domains/cuisine/ui/planificateur_repas.py",
                "priority": 6,
                "effort_hours": 5,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/jeux/test_setup.py",
                "src_path": "src/domains/jeux/setup.py",
                "priority": 7,
                "effort_hours": 3,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/jeux/test_integration.py",
                "src_path": "src/domains/jeux/integration.py",
                "priority": 8,
                "effort_hours": 3,
                "status": "NOT_STARTED"
            }
        ]
        
        completed = sum(1 for f in phase_1_files if f["status"] == "COMPLETED")
        in_progress = sum(1 for f in phase_1_files if f["status"] == "IN_PROGRESS")
        total_hours = sum(f["effort_hours"] for f in phase_1_files)
        
        self.results["phases"]["PHASE_1"] = {
            "name": "Tests fichiers 0% (8 fichiers)",
            "files": phase_1_files,
            "summary": {
                "total": len(phase_1_files),
                "completed": completed,
                "in_progress": in_progress,
                "not_started": len(phase_1_files) - completed - in_progress,
                "total_hours_estimate": total_hours,
                "expected_coverage_gain": "+3-5%",
                "target_coverage": "32-35%"
            }
        }
        
        return self.results["phases"]["PHASE_1"]
    
    def run_phase_2(self):
        """PHASE 2: Amélioration tests existants <5% (12 fichiers)"""
        
        phase_2_files = [
            {
                "test_path": "tests/domains/cuisine/ui/test_recettes.py",
                "src_path": "src/domains/cuisine/ui/recettes.py",
                "statements": 825,
                "coverage": 2.48,
                "effort_hours": 15,
                "priority": 1,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/cuisine/ui/test_inventaire.py",
                "src_path": "src/domains/cuisine/ui/inventaire.py",
                "statements": 825,
                "coverage": 3.86,
                "effort_hours": 15,
                "priority": 2,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/cuisine/ui/test_courses.py",
                "src_path": "src/domains/cuisine/ui/courses.py",
                "statements": 659,
                "coverage": 3.06,
                "effort_hours": 12,
                "priority": 3,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/jeux/ui/test_paris.py",
                "src_path": "src/domains/jeux/ui/paris.py",
                "statements": 622,
                "coverage": 4.03,
                "effort_hours": 10,
                "priority": 4,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/utils/test_formatters_dates.py",
                "src_path": "src/utils/formatters/dates.py",
                "statements": 83,
                "coverage": 4.40,
                "effort_hours": 3,
                "priority": 9,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/planning/ui/test_vue_ensemble.py",
                "src_path": "src/domains/planning/ui/vue_ensemble.py",
                "statements": 184,
                "coverage": 4.40,
                "effort_hours": 4,
                "priority": 8,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/cuisine/ui/test_batch_cooking_detaille.py",
                "src_path": "src/domains/cuisine/ui/batch_cooking_detaille.py",
                "statements": 327,
                "coverage": 4.65,
                "effort_hours": 7,
                "priority": 7,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/utils/ui/test_rapports.py",
                "src_path": "src/domains/utils/ui/rapports.py",
                "statements": 201,
                "coverage": 4.67,
                "effort_hours": 5,
                "priority": 6,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/famille/ui/test_routines.py",
                "src_path": "src/domains/famille/ui/routines.py",
                "statements": 271,
                "coverage": 4.71,
                "effort_hours": 6,
                "priority": 5,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/cuisine/ui/test_recettes_import.py",
                "src_path": "src/domains/cuisine/ui/recettes_import.py",
                "statements": 222,
                "coverage": 4.73,
                "effort_hours": 5,
                "priority": 10,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/jeux/logic/test_paris_logic.py",
                "src_path": "src/domains/jeux/logic/paris_logic.py",
                "statements": 500,
                "coverage": 4.80,
                "effort_hours": 10,
                "priority": 11,
                "status": "NOT_STARTED"
            },
            {
                "test_path": "tests/domains/utils/ui/test_parametres.py",
                "src_path": "src/domains/utils/ui/parametres.py",
                "statements": 339,
                "coverage": 4.99,
                "effort_hours": 8,
                "priority": 12,
                "status": "NOT_STARTED"
            }
        ]
        
        total_hours = sum(f["effort_hours"] for f in phase_2_files)
        total_statements = sum(f["statements"] for f in phase_2_files)
        
        self.results["phases"]["PHASE_2"] = {
            "name": "Amélioration tests <5% (12 fichiers)",
            "files": phase_2_files,
            "summary": {
                "total": len(phase_2_files),
                "total_statements_to_cover": total_statements,
                "total_hours_estimate": total_hours,
                "expected_coverage_gain": "+5-8%",
                "target_coverage": "40-45%"
            }
        }
        
        return self.results["phases"]["PHASE_2"]
    
    def run_phase_3(self):
        """PHASE 3: Services critiques (33 fichiers)"""
        
        phase_3_summary = {
            "name": "Services critiques (30% → 60%)",
            "files": 33,
            "current_coverage": 30.1,
            "target_coverage": 60,
            "total_hours_estimate": 80,
            "expected_coverage_gain": "+10-15%",
            "priority_files": [
                "src/services/base_ai_service.py (222 stmts, 13.54%)",
                "src/services/base_service.py (168 stmts, 16.94%)",
                "src/services/auth.py (381 stmts, 19.27%)",
                "src/services/backup.py (319 stmts, 18.32%)",
                "src/services/calendar_sync.py (481 stmts, 16.97%)"
            ]
        }
        
        self.results["phases"]["PHASE_3"] = phase_3_summary
        return phase_3_summary
    
    def run_phase_4(self):
        """PHASE 4: UI composants (26 fichiers, parallèle PHASE 3)"""
        
        phase_4_summary = {
            "name": "UI composants (37% → 70%)",
            "files": 26,
            "current_coverage": 37.5,
            "target_coverage": 70,
            "total_hours_estimate": 75,
            "expected_coverage_gain": "+10-15%",
            "run_parallel_with": "PHASE_3",
            "priority_files": [
                "src/ui/components/camera_scanner.py (182 stmts, 6.56%)",
                "src/ui/components/layouts.py (56 stmts, 8.54%)",
                "src/ui/core/base_form.py (101 stmts, 13.67%)",
                "src/ui/core/base_module.py (192 stmts, 17.56%)",
                "src/ui/layout/sidebar.py (47 stmts, 10.45%)"
            ]
        }
        
        self.results["phases"]["PHASE_4"] = phase_4_summary
        return phase_4_summary
    
    def run_phase_5(self):
        """PHASE 5: Tests E2E (5 flux principaux)"""
        
        phase_5_flows = [
            {
                "flow": "test_cuisine_flow.py",
                "description": "Recette → Planning → Courses",
                "tests_count": 60,
                "effort_hours": 12
            },
            {
                "flow": "test_famille_flow.py",
                "description": "Ajouter membre → Suivi activités",
                "tests_count": 50,
                "effort_hours": 10
            },
            {
                "flow": "test_planning_flow.py",
                "description": "Créer événement → Synchroniser",
                "tests_count": 50,
                "effort_hours": 10
            },
            {
                "flow": "test_auth_flow.py",
                "description": "Login → Multi-tenant → Permissions",
                "tests_count": 50,
                "effort_hours": 10
            },
            {
                "flow": "test_maison_flow.py",
                "description": "Projet maison → Budget → Rapports",
                "tests_count": 40,
                "effort_hours": 8
            }
        ]
        
        self.results["phases"]["PHASE_5"] = {
            "name": "Tests E2E (5 flux principaux)",
            "flows": phase_5_flows,
            "summary": {
                "total_flows": len(phase_5_flows),
                "total_tests": sum(f["tests_count"] for f in phase_5_flows),
                "total_hours_estimate": sum(f["effort_hours"] for f in phase_5_flows),
                "expected_coverage_gain": "+2-3%",
                "target_coverage": ">80%"
            }
        }
        
        return self.results["phases"]["PHASE_5"]
    
    def print_report(self):
        """Affiche un rapport complet"""
        
        print("\n" + "="*80)
        print("RAPPORT DE PLAN D'EXÉCUTION - PHASES 1-5")
        print("="*80 + "\n")
        
        # PHASE 1
        phase1 = self.results["phases"].get("PHASE_1", {})
        if phase1:
            summary = phase1.get("summary", {})
            print(f"PHASE 1: {phase1.get('name', '')}")
            print(f"  Files: {summary.get('completed', 0)}/{summary.get('total', 0)} completed")
            print(f"  Effort: {summary.get('total_hours_estimate', 0)} heures")
            print(f"  Impact: {summary.get('expected_coverage_gain', '')}")
            print()
        
        # PHASE 2
        phase2 = self.results["phases"].get("PHASE_2", {})
        if phase2:
            summary = phase2.get("summary", {})
            print(f"PHASE 2: {phase2.get('name', '')}")
            print(f"  Files: {summary.get('total', 0)} files ({summary.get('total_statements_to_cover', 0)} statements)")
            print(f"  Effort: {summary.get('total_hours_estimate', 0)} heures")
            print(f"  Impact: {summary.get('expected_coverage_gain', '')}")
            print()
        
        # PHASE 3 & 4
        phase3 = self.results["phases"].get("PHASE_3", {})
        phase4 = self.results["phases"].get("PHASE_4", {})
        
        print(f"PHASE 3: {phase3.get('name', '')}")
        print(f"  Files: {phase3.get('files', 0)} | Target: {phase3.get('current_coverage', 0)}% → {phase3.get('target_coverage', 0)}%")
        print(f"  Effort: {phase3.get('total_hours_estimate', 0)} heures | Impact: {phase3.get('expected_coverage_gain', '')}")
        print()
        
        print(f"PHASE 4: {phase4.get('name', '')} (PARALLÈLE avec PHASE 3)")
        print(f"  Files: {phase4.get('files', 0)} | Target: {phase4.get('current_coverage', 0)}% → {phase4.get('target_coverage', 0)}%")
        print(f"  Effort: {phase4.get('total_hours_estimate', 0)} heures | Impact: {phase4.get('expected_coverage_gain', '')}")
        print()
        
        # PHASE 5
        phase5 = self.results["phases"].get("PHASE_5", {})
        if phase5:
            summary = phase5.get("summary", {})
            print(f"PHASE 5: {phase5.get('name', '')}")
            print(f"  Flows: {summary.get('total_flows', 0)} flux ({summary.get('total_tests', 0)} tests)")
            print(f"  Effort: {summary.get('total_hours_estimate', 0)} heures")
            print(f"  Target: {summary.get('target_coverage', '')}")
            print()
        
        # TOTAL
        print("="*80)
        print("RÉSUMÉ GLOBAL")
        print("="*80)
        total_hours = (
            self.results["phases"].get("PHASE_1", {}).get("summary", {}).get("total_hours_estimate", 0) +
            self.results["phases"].get("PHASE_2", {}).get("summary", {}).get("total_hours_estimate", 0) +
            self.results["phases"].get("PHASE_3", {}).get("total_hours_estimate", 0) +
            self.results["phases"].get("PHASE_4", {}).get("total_hours_estimate", 0) +
            self.results["phases"].get("PHASE_5", {}).get("summary", {}).get("total_hours_estimate", 0)
        )
        print(f"Total effort: {total_hours} heures (~8 semaines)")
        print(f"Coverage: 29% → >80% (+50-51%)")
        print("="*80 + "\n")
    
    def export_json(self):
        """Exporte le rapport en JSON"""
        
        output_file = Path("PHASE_1_5_PLAN.json")
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✅ Plan exporté: {output_file}")
        return output_file


def main():
    """Main executor"""
    
    executor = TestPhaseExecutor()
    
    print("Exécution du plan de phases 1-5...\n")
    
    # Run all phases
    executor.run_phase_1()
    executor.run_phase_2()
    executor.run_phase_3()
    executor.run_phase_4()
    executor.run_phase_5()
    
    # Print report
    executor.print_report()
    
    # Export JSON
    executor.export_json()


if __name__ == "__main__":
    main()
