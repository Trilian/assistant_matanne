"""Audit script for session_state string literal usage in modules."""

import os
import re

# Match st.session_state["something"] or st.session_state['something']
# But NOT st.session_state[SK.xxx] or st.session_state[_keys("xxx")]
pattern = re.compile(r'st\.session_state\[(?!SK\.|_keys)["\']([^"\']+)["\']')

count = 0
for root, dirs, files in os.walk("src/modules"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    matches = pattern.findall(line)
                    if matches:
                        for m in matches:
                            count += 1
                            print(f'{path}:{i} -> key="{m}"')
print(f"\nTotal raw string literals (not using SK or _keys): {count}")
