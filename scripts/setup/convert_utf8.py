#!/usr/bin/env python3
"""Script de conversion des fichiers en UTF-8 sans BOM.

Ce script détecte et supprime le BOM (Byte Order Mark) des fichiers Python.
Le BOM UTF-8 est la séquence d'octets \xef\xbb\xbf en début de fichier.

Usage:
    python scripts/convert_to_utf8.py --check    # Vérifie sans modifier (exit code 1 si BOM trouvé)
    python scripts/convert_to_utf8.py --fix      # Convertit les fichiers avec BOM
    python scripts/convert_to_utf8.py --verbose  # Affiche tous les fichiers scannés
"""

import argparse
import sys
from pathlib import Path

# BOM UTF-8 en bytes
UTF8_BOM = b"\xef\xbb\xbf"


def detecter_bom(fichier: Path) -> bool:
    """Détecte si un fichier commence par un BOM UTF-8."""
    try:
        with open(fichier, "rb") as f:
            return f.read(3) == UTF8_BOM
    except (OSError, PermissionError) as e:
        print(f"  ⚠️  Erreur lecture {fichier}: {e}", file=sys.stderr)
        return False


def supprimer_bom(fichier: Path) -> bool:
    """Supprime le BOM UTF-8 d'un fichier."""
    try:
        with open(fichier, "rb") as f:
            contenu = f.read()

        if contenu.startswith(UTF8_BOM):
            contenu_sans_bom = contenu[3:]
            with open(fichier, "wb") as f:
                f.write(contenu_sans_bom)
            return True
        return False
    except (OSError, PermissionError) as e:
        print(f"  ❌ Erreur écriture {fichier}: {e}", file=sys.stderr)
        return False


def scanner_dossier(dossier: Path, extensions: tuple[str, ...] = (".py",)) -> list[Path]:
    """Scanne récursivement un dossier pour trouver les fichiers Python."""
    fichiers = []
    for ext in extensions:
        fichiers.extend(dossier.rglob(f"*{ext}"))
    return sorted(fichiers)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convertit les fichiers Python en UTF-8 sans BOM")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Mode vérification uniquement (retourne 1 si BOM trouvé)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Supprime le BOM des fichiers concernés",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche tous les fichiers scannés",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["src", "tests"],
        help="Dossiers à scanner (défaut: src tests)",
    )

    args = parser.parse_args()

    if not args.check and not args.fix:
        args.check = True  # Mode par défaut

    # Trouver la racine du projet
    racine = Path(__file__).parent.parent

    fichiers_avec_bom: list[Path] = []
    fichiers_scannes = 0

    print("[SCAN] Scan des fichiers Python...")
    print(f"   Dossiers: {', '.join(args.paths)}")
    print()

    for dossier_nom in args.paths:
        dossier = racine / dossier_nom
        if not dossier.exists():
            print(f"  [WARN] Dossier inexistant: {dossier}")
            continue

        fichiers = scanner_dossier(dossier)

        for fichier in fichiers:
            fichiers_scannes += 1
            chemin_relatif = fichier.relative_to(racine)

            if args.verbose:
                print(f"  [FILE] {chemin_relatif}")

            if detecter_bom(fichier):
                fichiers_avec_bom.append(fichier)
                if not args.verbose:
                    print(f"  [WARN] BOM detecte: {chemin_relatif}")

    print()
    print("Resume:")
    print(f"   Fichiers scannes: {fichiers_scannes}")
    print(f"   Fichiers avec BOM: {len(fichiers_avec_bom)}")

    if fichiers_avec_bom:
        if args.fix:
            print()
            print("[FIX] Conversion en cours...")
            convertis = 0
            for fichier in fichiers_avec_bom:
                if supprimer_bom(fichier):
                    chemin_relatif = fichier.relative_to(racine)
                    print(f"  [OK] Converti: {chemin_relatif}")
                    convertis += 1
            print()
            print(f"[OK] {convertis} fichier(s) converti(s) en UTF-8 sans BOM")
            return 0
        else:
            print()
            print("[ERROR] Fichiers avec BOM detectes!")
            print("   Utilisez --fix pour les convertir automatiquement")
            return 1
    else:
        print()
        print("[OK] Tous les fichiers sont en UTF-8 sans BOM")
        return 0


if __name__ == "__main__":
    sys.exit(main())
