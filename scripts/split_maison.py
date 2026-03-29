"""
Script de découpage maison.py en sous-routeurs — Sprint 12 A1.

Sections → fichiers:
  maison_projets.py    : PROJETS DOMESTIQUES + PROJETS PRIORISER IA
  maison_entretien.py  : ROUTINES + TÂCHES D'ENTRETIEN + SANTÉ APPAREILS +
                         ENTRETIEN SAISONNIER + RAPPELS + MÉNAGE/TÂCHES/PLANNING IA +
                         FICHE TÂCHE + GUIDE + ROUTINES PAR DÉFAUT +
                         ROUTINES EXTENSIONS + OBJETS ASSOCIER ROUTINE + SYNC SYNC
  maison_finances.py   : ARTISANS + CONTRATS + GARANTIES + DIAGNOSTICS +
                         CHARGES + DÉPENSES + CONSEILLER IA + DEVIS + RELEVÉS
  maison_jardin.py     : JARDIN + STOCKS + CALENDRIER DES SEMIS + NUISIBLES
  maison.py (reste)    : CONTEXTE/BRIEFING + MEUBLES + CELLIER + ECO-TIPS +
                         VISUALISATION + HUB + DOMOTIQUE + LIENS ACHAT +
                         PIÈCES + SUGGESTIONS RENOUVELLEMENT + FIN DE VIE GARANTIE

Usage: python scripts/split_maison.py
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent

MAISON = ROOT / "src" / "api" / "routes" / "maison.py"
ROUTES_DIR = ROOT / "src" / "api" / "routes"

# ---------------------------------------------------------------------------
# Section ranges (inclusive start, exclusive end — 1-based line numbers)
# Identified by analyzing section headers in maison.py
# ---------------------------------------------------------------------------

SECTION_RANGES = {
    # Each tuple: (start_line, end_line, section_name, target_file)
    # Projets
    (110, 330, "PROJETS DOMESTIQUES", "projets"),
    (3934, 3987, "PROJETS PRIORISER IA + sync final", "projets"),

    # Entretien
    (330, 450, "ROUTINES", "entretien"),
    (450, 604, "TÂCHES D'ENTRETIEN", "entretien"),
    (1055, 1145, "SANTÉ DES APPAREILS", "entretien"),
    (2776, 2876, "ENTRETIEN SAISONNIER", "entretien"),
    (3060, 3109, "BRIEFING NOTE + RAPPELS MAISON", "entretien"),
    (3106, 3250, "MÉNAGE PLANNING + TÂCHES PONCTUELLES + PLANNING IA", "entretien"),
    (3248, 3325, "FICHE TÂCHE + GUIDE + AUTO-COMPLÉTION", "entretien"),
    (3324, 3434, "ROUTINES PAR DÉFAUT (CRUD)", "entretien"),
    (3634, 3898, "ROUTINES EXTENSIONS", "entretien"),
    (3897, 3935, "OBJETS ASSOCIER ROUTINE", "entretien"),
    (3982, 4100, "SYNC TÂCHES → PLANNING", "entretien"),

    # Finances
    (1375, 1533, "ARTISANS", "finances"),
    (1532, 1655, "CONTRATS", "finances"),
    (1654, 1929, "GARANTIES", "finances"),
    (1928, 2226, "DIAGNOSTICS + ESTIMATIONS + ECO-TIPS", "finances"),
    (2223, 2246, "CHARGES RÉCURRENTES", "finances"),
    (2245, 2522, "DÉPENSES MAISON", "finances"),
    (2521, 2585, "CONSEILLER IA MAISON", "finances"),
    (2670, 2777, "DEVIS COMPARATIFS", "finances"),
    (2876, 2930, "RELEVÉS COMPTEURS", "finances"),

    # Jardin
    (604, 800, "JARDIN", "jardin"),
    (799, 933, "STOCKS MAISON", "jardin"),
    (984, 1056, "CALENDRIER DES SEMIS", "jardin"),
    (2584, 2671, "NUISIBLES", "jardin"),
}

# Note: These sets can overlap — we'll deduplicate by prioritizing first occurrence.

# ---------------------------------------------------------------------------
# Simpler approach: define non-overlapping ranges per target file
# ---------------------------------------------------------------------------

# Format: { target_file: [(start_1based, end_1based), ...] }
# Ranges are 1-based, inclusive on both ends
# These correspond to the section separators found in the file

TARGETS = {
    "projets": [
        (109, 329),       # PROJETS DOMESTIQUES header through end of section
        (3934, 3987),     # PROJETS PRIORISER IA + end
    ],
    "entretien": [
        (329, 449),       # ROUTINES
        (449, 603),       # TÂCHES D'ENTRETIEN
        (1054, 1144),     # SANTÉ DES APPAREILS
        (2775, 2875),     # ENTRETIEN SAISONNIER
        (3058, 3107),     # BRIEFING NOTE (comment) + RAPPELS MAISON
        (3105, 3249),     # MÉNAGE + TÂCHES PONCTUELLES + PLANNING IA
        (3247, 3324),     # AUTO-COMPLÉTION + FICHE TÂCHE + GUIDE
        (3323, 3433),     # ROUTINES PAR DÉFAUT
        (3633, 3897),     # ROUTINES EXTENSIONS
        (3896, 3934),     # OBJETS ASSOCIER ROUTINE
        (3982, 9999),     # SYNC TÂCHES → PLANNING (to end of file)
    ],
    "finances": [
        (1374, 1531),     # ARTISANS
        (1531, 1653),     # CONTRATS
        (1653, 1927),     # GARANTIES
        (1927, 2222),     # DIAGNOSTICS + ESTIMATIONS + ECO-TIPS
        (2222, 2245),     # CHARGES RÉCURRENTES
        (2244, 2521),     # DÉPENSES MAISON
        (2520, 2584),     # CONSEILLER IA MAISON
        (2669, 2775),     # DEVIS COMPARATIFS
        (2875, 2929),     # RELEVÉS COMPTEURS
    ],
    "jardin": [
        (603, 798),       # JARDIN
        (798, 931),       # STOCKS MAISON
        (983, 1054),      # CALENDRIER DES SEMIS
        (2583, 2669),     # NUISIBLES
    ],
}

# ---------------------------------------------------------------------------
# File headers for each sub-router
# ---------------------------------------------------------------------------

HEADERS = {
    "projets": '''\
"""
Routes API Maison — Projets domestiques.

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

''',
    "entretien": '''\
"""
Routes API Maison — Entretien, routines et ménage.

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict
from src.services.maison.schemas import TacheJour

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

''',
    "finances": '''\
"""
Routes API Maison — Finances (dépenses, contrats, artisans, garanties, etc.).

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

''',
    "jardin": '''\
"""
Routes API Maison — Jardin, stocks et nuisibles.

Sous-routeur inclus dans maison.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.services.core.backup.utils_serialization import model_to_dict

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Maison"])

''',
}


def split_maison():
    lines = MAISON.read_text(encoding="utf-8").splitlines(keepends=True)
    total = len(lines)
    print(f"maison.py: {total} lines")

    # Build a set of which lines go to which target (1-based)
    # First pass: mark each line
    line_target: dict[int, str] = {}

    # For each target, mark lines
    for target, ranges in TARGETS.items():
        for (start, end) in ranges:
            actual_end = min(end, total)
            for i in range(start, actual_end + 1):
                if i not in line_target:
                    line_target[i] = target

    # Lines not in any target stay in maison.py (maison)
    # Collect lines for each target
    target_lines: dict[str, list[str]] = {t: [] for t in TARGETS}
    maison_lines: list[str] = []

    for i, line in enumerate(lines, start=1):
        t = line_target.get(i)
        if t:
            target_lines[t].append(line)
        else:
            maison_lines.append(line)

    # Write sub-files
    for target, body_lines in target_lines.items():
        out_path = ROUTES_DIR / f"maison_{target}.py"
        header = HEADERS[target]
        content = header + "".join(body_lines)
        out_path.write_text(content, encoding="utf-8")
        print(f"  → {out_path.name}: {len(body_lines)} lines extracted")

    # Write updated maison.py (stripped sections + include_router calls at bottom)
    include_block = """

# ═══════════════════════════════════════════════════════════
# SOUS-ROUTEURS (Sprint 12 — A1 split)
# ═══════════════════════════════════════════════════════════
from src.api.routes.maison_projets import router as _projets_router
from src.api.routes.maison_entretien import router as _entretien_router
from src.api.routes.maison_finances import router as _finances_router
from src.api.routes.maison_jardin import router as _jardin_router

router.include_router(_projets_router)
router.include_router(_entretien_router)
router.include_router(_finances_router)
router.include_router(_jardin_router)
"""

    new_maison = "".join(maison_lines).rstrip() + "\n" + include_block
    MAISON.write_text(new_maison, encoding="utf-8")
    print(f"  → maison.py: {len(maison_lines)} lines remaining")
    print("Done!")


if __name__ == "__main__":
    split_maison()
