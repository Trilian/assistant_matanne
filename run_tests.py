"""Run pytest and capture failures to a file."""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--tb=no", "-q", "--no-header", "-p", "no:warnings"],
    capture_output=True,
    text=True,
    cwd=r"D:\Projet_streamlit\assistant_matanne",
)

# Extract FAILED lines
failures = [line for line in result.stdout.splitlines() if line.startswith("FAILED")]

with open("test_failures_list.txt", "w", encoding="utf-8") as f:
    f.write(f"Total failures: {len(failures)}\n\n")
    for line in failures:
        f.write(line + "\n")
    f.write("\n--- Summary ---\n")
    # Get last 3 lines for summary
    for line in result.stdout.splitlines()[-3:]:
        f.write(line + "\n")

print(f"Done. {len(failures)} failures written to test_failures_list.txt")
