"""
Script de découpage famille.py en sous-routeurs — Sprint 12 A2.

Sections → fichiers:
  famille_jules.py     : PROFILS ENFANTS + CROISSANCE OMS +
                         SUGGESTIONS ACTIVITÉS SIMPLIFIÉES + JULES ALIMENTS EXCLUS +
                         JULES COACHING HEBDO + TIMELINE VIE FAMILIALE
  famille_budget.py    : BUDGET FAMILIAL + BUDGET IA + BUDGET RÉSUMÉ MENSUEL
  famille_activites.py : ACTIVITÉS FAMILIALES + SUGGESTIONS IA (weekend/soirée)
  famille.py (reste)   : SCHEMAS LOCAUX + SHOPPING + ROUTINES + ANNIVERSAIRES +
                         RÉSUMÉ HEBDO + CONTEXTE + ACHATS + CONFIG GARDE +
                         CONFIG PRÉFÉRENCES + PLANNING JOURS SANS CRÈCHE +
                         WEEKEND SÉJOUR + SUGGESTIONS IA ACHATS + RAPPELS +
                         AUJOURD'HUI HISTOIRE

Usage: python scripts/split_famille.py
"""

from pathlib import Path

ROOT = Path(__file__).parent.parent

FAMILLE = ROOT / "src" / "api" / "routes" / "famille.py"
ROUTES_DIR = ROOT / "src" / "api" / "routes"

# Format: { target_file: [(start_1based, end_1based), ...] }
# Ranges are 1-based, inclusive on both ends

TARGETS = {
    "jules": [
        (85, 276),        # PROFILS ENFANTS (enfants, jalons)
        (2550, 2583),     # CROISSANCE OMS (Phase R)
        (2582, 2733),     # SUGGESTIONS ACTIVITÉS SIMPLIFIÉES (Phase O)
        (2733, 2798),     # JULES ALIMENTS EXCLUS (CT-09)
        (2797, 2837),     # JULES COACHING HEBDOMADAIRE (CT-05)
        (2836, 3000),     # TIMELINE VIE FAMILIALE (MT-08) + fin fichier
    ],
    "budget": [
        (533, 698),       # BUDGET FAMILIAL
        (697, 936),       # BUDGET IA (Prédictions, Anomalies, Économies)
        (2083, 2157),     # BUDGET RÉSUMÉ MENSUEL
    ],
    "activites": [
        (275, 534),       # ACTIVITÉS FAMILIALES
        (1617, 1683),     # SUGGESTIONS IA (Phase M3) - weekend/soirée
    ],
}

# ---------------------------------------------------------------------------
# File headers for each sub-router
# ---------------------------------------------------------------------------

HEADERS = {
    "jules": '''\
"""
Routes API Famille — Jules (profils enfants, jalons, coaching).

Sous-routeur inclus dans famille.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])

''',
    "budget": '''\
"""
Routes API Famille — Budget familial.

Sous-routeur inclus dans famille.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])

''',
    "activites": '''\
"""
Routes API Famille — Activités familiales et suggestions IA.

Sous-routeur inclus dans famille.py.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import require_auth
from src.api.schemas.common import MessageResponse, ReponsePaginee
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_ECRITURE,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api

import logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Famille"])

''',
}


def split_famille():
    lines = FAMILLE.read_text(encoding="utf-8").splitlines(keepends=True)
    total = len(lines)
    print(f"famille.py: {total} lines")

    # Build a set of which lines go to which target (1-based)
    line_target: dict[int, str] = {}

    for target, ranges in TARGETS.items():
        for (start, end) in ranges:
            actual_end = min(end, total)
            for i in range(start, actual_end + 1):
                if i not in line_target:
                    line_target[i] = target

    # Collect lines for each target
    target_lines: dict[str, list[str]] = {t: [] for t in TARGETS}
    famille_lines: list[str] = []

    for i, line in enumerate(lines, start=1):
        t = line_target.get(i)
        if t:
            target_lines[t].append(line)
        else:
            famille_lines.append(line)

    # Write sub-files
    for target, body_lines in target_lines.items():
        out_path = ROUTES_DIR / f"famille_{target}.py"
        header = HEADERS[target]
        content = header + "".join(body_lines)
        out_path.write_text(content, encoding="utf-8")
        print(f"  → {out_path.name}: {len(body_lines)} lines extracted")

    # Write updated famille.py with include_router calls
    include_block = """

# ═══════════════════════════════════════════════════════════
# SOUS-ROUTEURS (Sprint 12 — A2 split)
# ═══════════════════════════════════════════════════════════
from src.api.routes.famille_jules import router as _jules_router
from src.api.routes.famille_budget import router as _budget_router
from src.api.routes.famille_activites import router as _activites_router

router.include_router(_jules_router)
router.include_router(_budget_router)
router.include_router(_activites_router)
"""

    new_famille = "".join(famille_lines).rstrip() + "\n" + include_block
    FAMILLE.write_text(new_famille, encoding="utf-8")
    print(f"  → famille.py: {len(famille_lines)} lines remaining")
    print("Done!")


if __name__ == "__main__":
    split_famille()
