"""Run pytest and extract failures to a clean file."""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "--tb=no", "-q", "-p", "no:warnings"],
    capture_output=True,
    text=True,
    timeout=400,
)

# Write raw output
with open("test_raw_output.txt", "w", encoding="utf-8") as f:
    f.write(result.stdout)
    f.write("\n---STDERR---\n")
    f.write(result.stderr)

# Parse failures from the output
lines = result.stdout.split("\n")
failures = []
for line in lines:
    if " FAILED" in line:
        # Format: "tests/path/test.py::Class::method FAILED"
        parts = line.strip().split(" FAILED")
        if parts:
            failures.append(parts[0].strip())

# Write clean list
with open("test_failures_clean.txt", "w", encoding="utf-8") as f:
    for fail in failures:
        f.write(fail + "\n")

# Print summary
from collections import Counter

files = Counter()
for fail in failures:
    file_path = fail.split("::")[0]
    files[file_path] += 1

print(f"Total failures: {len(failures)}")
print("\nBy file:")
for file_path, count in sorted(files.items(), key=lambda x: -x[1]):
    print(f"  {count:3d} | {file_path}")

# Print summary line
for line in lines[-5:]:
    if "failed" in line or "passed" in line:
        print(f"\n{line.strip()}")
