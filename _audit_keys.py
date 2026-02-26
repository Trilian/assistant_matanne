"""Audit dynamic session keys via _keys() in modules."""

import collections
import os
import re

pattern = re.compile(r'_keys\("([^"]+)"')
keys_found = collections.Counter()
for root, dirs, files in os.walk("src/modules"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    matches = pattern.findall(line)
                    for m in matches:
                        keys_found[m] += 1

with open("_audit_keys_output.txt", "w") as out:
    out.write(f"Unique _keys() arguments: {len(keys_found)}\n")
    for k, c in sorted(keys_found.items()):
        out.write(f"  {k}: {c} usages\n")
