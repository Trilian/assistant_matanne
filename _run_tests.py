"""Run auth tests and write result to file."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/api/test_auth.py", "-v", "--tb=short"],
    capture_output=True,
    text=True,
    cwd=r"D:\Projet_streamlit\assistant_matanne",
)
with open("_test_auth_result.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
    if result.stderr:
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr)
    f.write(f"\nReturn code: {result.returncode}\n")
print(f"Done. Return code: {result.returncode}")
