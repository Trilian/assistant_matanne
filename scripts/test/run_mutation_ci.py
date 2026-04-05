#!/usr/bin/env python3
"""Exécute un mutation testing focalisé pour la CI sur les modules critiques.

Par défaut, le script vise le service dashboard, déjà configuré dans
`pyproject.toml` via `[tool.mutmut]`.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
PROFILS = {
    "dashboard": {
        "path_to_mutate": "src/services/dashboard",
        "tests": ["tests/services/dashboard"],
        "min_kill_ratio": 0.60,
        "max_no_tests": 400,
    },
    "planning": {
        "path_to_mutate": "src/services/planning",
        "tests": ["tests/services/planning"],
        "min_kill_ratio": 0.50,
        "max_no_tests": 450,
    },
    "cuisine": {
        "path_to_mutate": "src/services/cuisine",
        "tests": [
            "tests/services/recettes",
            "tests/services/courses",
            "tests/services/batch_cooking",
            "tests/services/inventaire",
        ],
        "min_kill_ratio": 0.45,
        "max_no_tests": 650,
    },
}

CANDIDATS_STATS = (
    RACINE / "mutants" / "mutmut-cicd-stats.json",
    RACINE / "mutants" / "mutmut-stats.json",
    RACINE / "mutmut-stats.json",
)


def executer_commande(cmd: list[str], description: str, dry_run: bool = False) -> int:
    """Exécute une commande shell de manière traçable."""
    print(f"[MUTATION] {description}")
    print("           ", " ".join(cmd))
    if dry_run:
        return 0
    resultat = subprocess.run(cmd, cwd=RACINE)
    return resultat.returncode


def localiser_fichier_stats() -> Path | None:
    """Retourne le fichier de stats mutmut le plus pertinent s'il existe."""
    for candidat in CANDIDATS_STATS:
        if candidat.exists():
            return candidat

    trouves = sorted(RACINE.rglob("mutmut*stats.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return trouves[0] if trouves else None


def charger_stats(path: Path) -> dict[str, int]:
    """Charge les statistiques JSON produites par mutmut."""
    contenu = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(contenu, dict):
        raise ValueError(f"Format JSON inattendu pour {path}")
    return {str(cle): int(valeur) for cle, valeur in contenu.items()}


def normaliser_stats(stats: dict[str, int]) -> dict[str, int]:
    """Assure la présence des clés principales, avec des valeurs par défaut."""
    cles = [
        "killed",
        "survived",
        "total",
        "no_tests",
        "skipped",
        "suspicious",
        "timeout",
        "segfault",
    ]
    return {cle: int(stats.get(cle, 0)) for cle in cles}


def sauvegarder_stats_ci(stats: dict[str, int], profil: str) -> Path:
    """Sauvegarde une copie stable des stats pour la CI."""
    dossier = RACINE / "mutants"
    dossier.mkdir(parents=True, exist_ok=True)

    chemin = dossier / "mutmut-cicd-stats.json"
    chemin.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    chemin_profil = dossier / f"mutmut-cicd-stats-{profil}.json"
    chemin_profil.write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return chemin


def evaluer_qualite(stats: dict[str, int], min_kill_ratio: float, max_no_tests: int) -> int:
    """Applique les seuils de qualité et retourne un code de sortie."""
    stats = normaliser_stats(stats)
    total = max(stats["total"], 1)
    kill_ratio = stats["killed"] / total

    print("[MUTATION] Résultats")
    print(f"  - killed     : {stats['killed']}")
    print(f"  - survived   : {stats['survived']}")
    print(f"  - no_tests   : {stats['no_tests']}")
    print(f"  - suspicious : {stats['suspicious']}")
    print(f"  - timeout    : {stats['timeout']}")
    print(f"  - total      : {stats['total']}")
    print(f"  - score      : {kill_ratio:.1%}")

    erreurs: list[str] = []
    if stats["survived"] > 0:
        erreurs.append(f"{stats['survived']} mutants ont survécu")
    if stats["suspicious"] > 0 or stats["timeout"] > 0 or stats["segfault"] > 0:
        erreurs.append("des mutants sont en état suspicious/timeout/segfault")
    if kill_ratio < min_kill_ratio:
        erreurs.append(f"score de mutation {kill_ratio:.1%} < seuil requis {min_kill_ratio:.1%}")
    if stats["no_tests"] > max_no_tests:
        erreurs.append(f"{stats['no_tests']} mutants sans tests > seuil autorisé {max_no_tests}")

    if erreurs:
        print("[ERROR] Seuils CI non respectés :")
        for erreur in erreurs:
            print(f"  - {erreur}")
        return 1

    print("[OK] Seuils mutation CI validés")
    return 0


def parser_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exécuter mutmut pour la CI sur les modules critiques.")
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILS.keys()),
        default="dashboard",
        help="Profil de mutation testing à exécuter (défaut: dashboard)",
    )
    parser.add_argument(
        "--min-kill-ratio",
        type=float,
        default=None,
        help="Seuil minimum de mutation score (défaut: dépend du profil)",
    )
    parser.add_argument(
        "--max-no-tests",
        type=int,
        default=None,
        help="Nombre maximum de mutants 'no_tests' toléré (défaut: dépend du profil)",
    )
    parser.add_argument("--skip-run", action="store_true", help="Ne lance pas mutmut, relit simplement les stats existantes")
    parser.add_argument("--skip-patch", action="store_true", help="N'applique pas le patch de compatibilité mutmut/src")
    parser.add_argument("--dry-run", action="store_true", help="Affiche les commandes sans rien exécuter")
    return parser.parse_args()


def main() -> int:
    args = parser_args()
    profil = PROFILS[args.profile]
    min_kill_ratio = args.min_kill_ratio if args.min_kill_ratio is not None else float(profil["min_kill_ratio"])
    max_no_tests = args.max_no_tests if args.max_no_tests is not None else int(profil["max_no_tests"])

    print(f"[MUTATION] Profil actif : {args.profile}")
    print(f"[MUTATION] Module cible : {profil['path_to_mutate']}")
    print(f"[MUTATION] Suites de tests : {', '.join(profil['tests'])}")

    if sys.platform.startswith("win") and not args.skip_run and not args.dry_run:
        print("[WARN] mutmut ne supporte pas nativement Windows.")
        print("       Utiliser la CI GitHub Actions ou lancer la commande depuis WSL.")
        return 1

    if not args.skip_patch:
        code = executer_commande(
            [sys.executable, "scripts/qualite/patch_mutmut_src_prefix.py"],
            "Patch de compatibilité mutmut",
            dry_run=args.dry_run,
        )
        if code != 0:
            return code

    if not args.skip_run:
        code = executer_commande(
            [sys.executable, "-m", "mutmut", "run", "--paths-to-mutate", str(profil["path_to_mutate"])],
            f"Lancement mutation testing focalisé ({args.profile})",
            dry_run=args.dry_run,
        )
        if code != 0:
            return code

    if args.dry_run:
        print("[OK] Dry-run mutation CI prêt")
        return 0

    source_stats = localiser_fichier_stats()
    if source_stats is None:
        print("[ERROR] Aucun fichier de statistiques mutmut trouvé après exécution")
        return 1

    stats = charger_stats(source_stats)
    chemin_ci = sauvegarder_stats_ci(stats, args.profile)

    # Conserver aussi une copie stable si mutmut a écrit ailleurs.
    if source_stats.resolve() != chemin_ci.resolve():
        shutil.copyfile(source_stats, chemin_ci)

    return evaluer_qualite(stats, min_kill_ratio=min_kill_ratio, max_no_tests=max_no_tests)


if __name__ == "__main__":
    raise SystemExit(main())
