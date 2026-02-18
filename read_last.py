"""Extract summary from test output file."""

import sys

f = sys.argv[1]
lines = open(f, encoding="utf-8").readlines()
print(lines[-1].strip())
