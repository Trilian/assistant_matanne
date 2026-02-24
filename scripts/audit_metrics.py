"""Script d'audit rapide des métriques du codebase."""

import os


def count_dir(d):
    count = 0
    loc = 0
    for root, _, files in os.walk(d):
        if "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".py"):
                count += 1
                with open(os.path.join(root, f), encoding="utf-8", errors="ignore") as fh:
                    loc += sum(1 for _ in fh)
    return count, loc


dirs = ["src/api", "src/core", "src/modules", "src/services", "src/ui"]
total_f, total_l = 0, 0
for d in dirs:
    c, l = count_dir(d)
    total_f += c
    total_l += l
    print(f"{d}: {c} files, {l:,} LOC")

# app.py
with open("src/app.py", encoding="utf-8") as fh:
    app_loc = sum(1 for _ in fh)
total_f += 1
total_l += app_loc
print(f"src/app.py: 1 file, {app_loc} LOC")
print(f"TOTAL src/: {total_f} files, {total_l:,} LOC")

# tests
tc, tl = count_dir("tests")
print(f"tests/: {tc} files, {tl:,} LOC")

# Grand total
print(f"GRAND TOTAL (src+tests): {total_f + tc} files, {total_l + tl:,} LOC")

# Non-py files in src
non_py = 0
for root, _, files in os.walk("src"):
    if "__pycache__" in root:
        continue
    for f in files:
        if not f.endswith(".py"):
            non_py += 1
print(f"Non-py files in src/: {non_py}")
