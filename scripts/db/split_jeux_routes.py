#!/usr/bin/env python3
"""
Script pour decoupe src/api/routes/jeux.py en sous-modules thematiques.
Strategie: assignation par URL pattern de chaque @router.xxx("/url") endpoint.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
ROUTES_DIR = ROOT / "src" / "api" / "routes"
JEUX_FILE = ROUTES_DIR / "jeux.py"

# Assignation URLs -> fichier de destination (du plus specifique au plus general)
URL_ROUTING = [
    ("/loto/", "loto"),
    ("/euromillions/", "euromillions"),
    ("/dashboard", "dashboard"),
    ("/stats/personnelles", "dashboard"),
    ("/performance", "dashboard"),
    ("/resume-mensuel", "dashboard"),
    ("/ocr-ticket", "dashboard"),
    ("/analyse-ia", "dashboard"),
    ("/backtest", "dashboard"),
    ("/notifications", "dashboard"),
    ("/equipes", "paris"),
    ("/matchs", "paris"),
    ("/bankroll", "paris"),
    ("/paris", "paris"),
    ("/series", "paris"),
    ("/alertes", "paris"),
    ("/patterns", "paris"),
]

DEST_NAMES = {
    "paris": "Paris Sportifs (Equipes, Matchs, Bankroll, Series, Predictions, Cotes historique)",
    "loto": "Loto (Tirages, Grilles, Statistiques, Generation IA)",
    "euromillions": "Euromillions (Tirages, Grilles, Statistiques, Generation IA)",
    "dashboard": "Dashboard, Performance, Resume Mensuel, Analyse IA, Backtest, Notifications",
}

SUB_HEADER = '''\
"""Routes API jeux - {domain}.

Sous-module de jeux.py. Le routeur n'a pas de prefixe ici,
car le prefixe /api/v1/jeux est defini dans jeux.py (agregateur).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from src.api.dependencies import require_auth
from src.api.pagination import appliquer_cursor_filter, construire_reponse_cursor, decoder_cursor
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import (
    REPONSES_CRUD_CREATION,
    REPONSES_CRUD_LECTURE,
    REPONSES_CRUD_SUPPRESSION,
    REPONSES_LISTE,
)
from src.api.schemas.jeux import AnalyseIARequest, GenererGrilleRequest
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

'''


def get_dest(url):
    for prefix, dest in URL_ROUTING:
        if url.startswith(prefix):
            return dest
    return "paris"


def split_file(content):
    """
    Decoupe par endpoint. Chaque @router.xxx(...) introduit un nouveau bloc.
    Les lignes de commentaires/sections entre deux blocs suivent le PROCHAIN endpoint.
    """
    lines = content.splitlines(keepends=True)

    # Trouver fin du header (apres la ligne "router = APIRouter(prefix=...")
    header_end = 0
    for i, line in enumerate(lines):
        if re.match(r'^router\s*=\s*APIRouter', line):
            header_end = i + 1
            # Sauter la ligne vide qui suit
            while header_end < len(lines) and lines[header_end].strip() == "":
                header_end += 1
            break

    body = lines[header_end:]
    n = len(body)

    # Trouver toutes les positions @router. et leur URL/destination
    router_infos = []  # (index, dest, url)
    for i, line in enumerate(body):
        if re.match(r'^@router\.', line):
            m = re.search(r'@router\.\w+\(\s*["\']([^"\']+)["\']', line)
            if m:
                url = m.group(1)
                router_infos.append((i, get_dest(url), url))

    if not router_infos:
        print("ERREUR: aucun endpoint trouve")
        return {"paris": [], "loto": [], "euromillions": [], "dashboard": []}

    # Assigner une destination a chaque ligne du body
    line_dests = ["paris"] * n

    # Chaque fonction @router[pos:next_pos] prend la destination du @router
    for idx, (pos, dest, url) in enumerate(router_infos):
        next_pos = router_infos[idx + 1][0] if idx + 1 < len(router_infos) else n
        for j in range(pos, next_pos):
            line_dests[j] = dest

    # Les lignes AVANT le premier @router: commentaires, lignes vides
    # -> elles vont avec la destination du premier @router (mais on peut les ignorer
    #    car elles sont des separateurs de section)
    # On les assigne a la destination du premier endpoint suivant
    first_router_pos = router_infos[0][0] if router_infos else 0
    for j in range(first_router_pos):
        # Ces lignes precedent le 1er endpoint - trouver le 1er router
        line_dests[j] = router_infos[0][1] if router_infos else "paris"

    # Maintenant, les lignes de "separateurs de section" (# ===...) entre deux sections
    # peuvent etre mal assigns si elles sont avant un @router d'une section differente
    # On doit reassigner: un bloc de commentaires avant un @router va avec ce @router
    i = 0
    while i < n:
        # Detecter une ligne de commentaire pur (hors section header)
        # qu'il faut potentiellement reassigner
        if body[i].startswith('#') or body[i].strip() == "":
            # Trouver le prochain @router apres ce point
            for pos, dest, _ in router_infos:
                if pos > i:
                    # Reassigner les lignes de commentaires/vides consecutives
                    j = i
                    while j < pos and (body[j].startswith('#') or body[j].strip() == ""):
                        line_dests[j] = dest
                        j += 1
                    break
        i += 1

    # Grouper les lignes par destination
    result = {"paris": [], "loto": [], "euromillions": [], "dashboard": []}
    for i, line in enumerate(body):
        result[line_dests[i]].append(line)

    return result


def main():
    if not JEUX_FILE.exists():
        print(f"ERREUR: fichier non trouve: {JEUX_FILE}")
        sys.exit(1)

    content = JEUX_FILE.read_text(encoding="utf-8")
    print(f"Lecture de jeux.py ({len(content.splitlines())} lignes)...")

    dests = split_file(content)
    total = sum(len(v) for v in dests.values())
    print(f"  Lignes assignees: {total}")

    for dest, dest_lines in dests.items():
        if not dest_lines:
            print(f"  ATTENTION: aucune ligne pour {dest}")
            continue
        out = ROUTES_DIR / f"jeux_{dest}.py"
        text = SUB_HEADER.replace("{domain}", DEST_NAMES[dest]) + "".join(dest_lines)
        out.write_text(text, encoding="utf-8")
        print(f"  -> jeux_{dest}.py ({len(dest_lines)} lignes)")

    # Backup + aggregateur
    bak = JEUX_FILE.with_suffix(".py.bak")
    bak.write_text(content, encoding="utf-8")
    print(f"\nBackup: {bak.name}")

    aggregator = '''\
"""Routes API pour les jeux (Paris sportifs, Loto, Euromillions).

Agregateur: inclut 4 sous-routeurs thematiques:
- jeux_paris       : Equipes, Matchs, Paris, Bankroll, Series, Predictions, Cotes
- jeux_loto        : Loto tirages, grilles, stats, generation IA
- jeux_euromillions: Euromillions tirages, grilles, stats, generation IA
- jeux_dashboard   : Dashboard, Performance, Resume Mensuel, Analyse IA, Backtest

Pour routes/__init__.py, "jeux_router": ".jeux" reste inchange.
"""

from fastapi import APIRouter

from .jeux_paris import router as paris_router
from .jeux_loto import router as loto_router
from .jeux_euromillions import router as euromillions_router
from .jeux_dashboard import router as dashboard_router

router = APIRouter(prefix="/api/v1/jeux", tags=["Jeux"])

router.include_router(paris_router)
router.include_router(loto_router)
router.include_router(euromillions_router)
router.include_router(dashboard_router)
'''

    JEUX_FILE.write_text(aggregator, encoding="utf-8")
    print(f"-> jeux.py (agregateur, {len(aggregator.splitlines())} lignes)")
    print("\nDecoupage termine!")


if __name__ == "__main__":
    main()
