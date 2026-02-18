"""Analyze test failures from test_full_summary.txt"""

from collections import Counter

lines = open("test_full_summary.txt", encoding="utf-8").readlines()
c = Counter()
for l in lines:
    l = l.strip()
    if "FAILED" in l and "::" in l:
        parts = l.split("::")[0].replace("FAILED ", "").strip()
        c[parts] += 1
    elif "ERROR" in l and "::" in l:
        parts = l.split("::")[0].replace("ERROR ", "").strip()
        c["ERROR:" + parts] += 1

for k, v in sorted(c.items()):
    print(f"{v:3d} | {k}")
print(f"\nTotal failures: {sum(v for k,v in c.items() if not k.startswith('ERROR:'))}")
print(f"Total errors: {sum(v for k,v in c.items() if k.startswith('ERROR:'))}")
