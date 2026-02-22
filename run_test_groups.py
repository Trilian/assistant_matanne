"""Quick test runner for grouped test analysis."""

import subprocess
import sys

groups = [
    ("test_utils", "tests/modules/famille/test_utils.py"),
    ("test_hub", "tests/modules/famille/test_hub_famille.py"),
    ("test_activites", "tests/modules/famille/test_activites.py"),
    ("test_liste", "tests/modules/cuisine/recettes/test_liste.py"),
    ("jules_utils", "tests/modules/famille/jules/test_utils.py"),
    ("test_jules", "tests/modules/famille/test_jules.py"),
    ("suivi_perso", "tests/modules/famille/suivi_perso/test_tableau_bord.py"),
    ("weekend", "tests/modules/famille/weekend/test_utils.py"),
]

results = []
for name, path in groups:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", path, "--tb=no", "-p", "no:warnings", "-q"],
        capture_output=True,
        text=True,
        cwd="D:\\Projet_streamlit\\assistant_matanne",
    )
    # Get last line with counts
    lines = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
    summary = lines[-1] if lines else "NO OUTPUT"
    results.append(f"{name:20s} | {summary}")

with open("test_groups_result.txt", "w") as f:
    f.write("\n".join(results))
print("DONE - see test_groups_result.txt")
