"""Parse pytest --tb=line -q output for failures."""

with open("test_full_feb22.txt", encoding="utf-8", errors="replace") as f:
    content = f.read()

lines = content.split("\n")
failures = []
for line in lines:
    stripped = line.strip()
    # In -q --tb=line mode, failures appear as: "FAILED path::test - reason"
    if stripped.startswith("FAILED"):
        test_path = stripped.replace("FAILED ", "").split(" - ")[0]
        failures.append(test_path)
    # Also capture the F lines like "tests/path.py::Test::test_name"
    if "::" in stripped and stripped.endswith("FAILED"):
        test_path = stripped.replace(" FAILED", "")
        failures.append(test_path)

# Find summary line
for line in lines:
    if "failed" in line and "passed" in line:
        print(line.strip())
        break

print(f"\nTotal FAILED lines found: {len(failures)}")
print("\n--- By file ---")
from collections import Counter

files = Counter()
for f in failures:
    file_path = f.split("::")[0]
    files[file_path] += 1

for file_path, count in sorted(files.items(), key=lambda x: -x[1]):
    print(f"  {count:3d} | {file_path}")

print("\n--- All failures ---")
for f in failures:
    print(f"  {f}")
