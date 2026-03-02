import os

res = []
dir_path = r"d:\Projet_streamlit\assistant_matanne\sql\migrations"
for f in os.listdir(dir_path):
    if f.endswith(".sql"):
        p = os.path.join(dir_path, f)
        res.append(f"\n--- {f} ---\n{open(p, encoding='utf-8').read()}")

open(r"d:\Projet_streamlit\assistant_matanne\mig.txt", "w", encoding="utf-8").write("\n".join(res))
