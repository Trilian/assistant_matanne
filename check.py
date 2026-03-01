import os

with open("result.txt", "w") as f:
    f.write(f"Size: {os.path.getsize('sql/INIT_COMPLET.sql')}")
