#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import shutil
import os

DATA = Path("data")
DATA.mkdir(parents=True, exist_ok=True)
src = DATA / "app.db"
outdir = DATA / "backups"
outdir.mkdir(parents=True, exist_ok=True)
if src.exists():
    dst = outdir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(src, dst)
    print("✅ Sauvegarde créée:", dst)
else:
    print("Aucune base trouvée à sauvegarder.")