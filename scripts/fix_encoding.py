#!/usr/bin/env python3
"""Fix encoding issues in test and source files.

Ce script corrige les patterns mojibake (UTF-8 mal interprete en Latin-1/CP1252)
dans les fichiers Python du projet.

Usage:
    python fix_encoding.py           # Corrige tous les fichiers
    python fix_encoding.py --check   # Verifie sans modifier (exit code 1 si problemes)
"""

import glob
import sys

# Mojibake patterns: bytes sequence (as seen in corrupted file) -> correct UTF-8 char
# Using raw bytes to avoid encoding issues in this script itself
# These patterns result from UTF-8 -> CP1252 -> UTF-8 double encoding
REPLACEMENTS = [
    # Box drawing - double lines (most common issue)
    # Pattern: original UTF-8 byte E2 95 XX was interpreted as CP1252:
    #   E2 -> a-circumflex (U+00E2) -> C3 A2 in UTF-8
    #   95 -> bullet (U+2022) -> E2 80 A2 in UTF-8
    #   XX -> various -> C2 XX in UTF-8
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x90", b"\xe2\x95\x90"),  # BOX DOUBLE HORIZONTAL
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x91", b"\xe2\x95\x91"),  # BOX DOUBLE VERTICAL
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x94", b"\xe2\x95\x94"),  # BOX DOUBLE DOWN AND RIGHT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x97", b"\xe2\x95\x97"),  # BOX DOUBLE DOWN AND LEFT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x9a", b"\xe2\x95\x9a"),  # BOX DOUBLE UP AND RIGHT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\x9d", b"\xe2\x95\x9d"),  # BOX DOUBLE UP AND LEFT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\xa0", b"\xe2\x95\xa0"),  # BOX DOUBLE VERTICAL AND RIGHT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\xa3", b"\xe2\x95\xa3"),  # BOX DOUBLE VERTICAL AND LEFT
    (b"\xc3\xa2\xe2\x80\xa2\xc2\xa6", b"\xe2\x95\xa6"),  # BOX DOUBLE DOWN AND HORIZONTAL
    (b"\xc3\xa2\xe2\x80\xa2\xc2\xa9", b"\xe2\x95\xa9"),  # BOX DOUBLE UP AND HORIZONTAL
    (b"\xc3\xa2\xe2\x80\xa2\xc2\xac", b"\xe2\x95\xac"),  # BOX DOUBLE VERTICAL AND HORIZONTAL
    # Box drawing - single lines
    (b"\xc3\xa2\xe2\x82\xac\xe2\x80\x9c", b"\xe2\x94\x80"),  # BOX LIGHT HORIZONTAL
    (b"\xc3\xa2\xe2\x82\xac\xc2\x82", b"\xe2\x94\x82"),  # BOX LIGHT VERTICAL
    (b"\xc3\xa2\xe2\x82\xac\xc5\x92", b"\xe2\x94\x8c"),  # BOX LIGHT DOWN AND RIGHT
    (b"\xc3\xa2\xe2\x82\xac\xc2\x90", b"\xe2\x94\x90"),  # BOX LIGHT DOWN AND LEFT
    (b"\xc3\xa2\xe2\x82\xac\xc5\x94", b"\xe2\x94\x94"),  # BOX LIGHT UP AND RIGHT
    (b"\xc3\xa2\xe2\x82\xac\xcb\x9c", b"\xe2\x94\x98"),  # BOX LIGHT UP AND LEFT
    # French characters - Pattern 1: UTF-8 -> Latin1 -> UTF-8 (double encoding)
    (b"\xc3\x83\xc2\xa0", b"\xc3\xa0"),  # a grave
    (b"\xc3\x83\xc2\xa9", b"\xc3\xa9"),  # e acute
    (b"\xc3\x83\xc2\xa8", b"\xc3\xa8"),  # e grave
    (b"\xc3\x83\xc2\xaa", b"\xc3\xaa"),  # e circumflex
    (b"\xc3\x83\xc2\xa2", b"\xc3\xa2"),  # a circumflex
    (b"\xc3\x83\xc2\xb4", b"\xc3\xb4"),  # o circumflex
    (b"\xc3\x83\xc2\xae", b"\xc3\xae"),  # i circumflex
    (b"\xc3\x83\xc2\xb9", b"\xc3\xb9"),  # u grave
    (b"\xc3\x83\xc2\xbb", b"\xc3\xbb"),  # u circumflex
    (b"\xc3\x83\xc2\xa7", b"\xc3\xa7"),  # c cedilla
    (b"\xc3\x83\xc2\xab", b"\xc3\xab"),  # e diaeresis
    (b"\xc3\x83\xc2\xaf", b"\xc3\xaf"),  # i diaeresis
    (b"\xc3\x83\xc2\xbc", b"\xc3\xbc"),  # u diaeresis
    (b"\xc3\x83\xc2\xb6", b"\xc3\xb6"),  # o diaeresis
    (b"\xc3\x83\xc2\xb1", b"\xc3\xb1"),  # n tilde
    (b"\xc3\x83\xc5\x8a", b"\xc3\x8a"),  # E circumflex
    (b"\xc3\x83\xe2\x80\xb0", b"\xc3\x89"),  # E acute
    (b"\xc3\x83\xe2\x82\xac", b"\xc3\x80"),  # A grave
    (b"\xc3\x83\xe2\x80\xa1", b"\xc3\x87"),  # C cedilla
    (b"\xc3\x83\xcb\x86", b"\xc3\x88"),  # E grave
    # French characters - Pattern 2: Partial corruption (C3 83 XX -> C3 XX)
    # When C3 A9 (e acute) becomes C3 83 65 (A with tilde + e)
    (b"\xc3\x83e", b"\xc3\xa9"),  # e acute (Ãe -> e)
    (b"\xc3\x83a", b"\xc3\xa0"),  # a grave (Ãa -> a)
    (b"\xc3\x83\xa8", b"\xc3\xa8"),  # e grave
    (b"\xc3\x83\xa0", b"\xc3\xa0"),  # a grave variant
    # Unicode replacement chars and symbols
    (b"\xc3\xa2\xe2\x82\xac\xc2\x9d", b"\xe2\x9d\x8c"),  # X mark
    (b"\xc3\xa2\xe2\x82\xac\xc2\xa0", b"\xe2\x9a\xa0"),  # Warning sign
    (b"\xc3\xa2\xc5\x93\xc2\x85", b"\xe2\x9c\x85"),  # Check mark
    (b"\xc3\xa2\xc5\x93\xc2\x93", b"\xe2\x9c\x93"),  # Check mark variant
    (b"\xc3\xa2\xc2\x9d\xe2\x80\x9d", b"\xe2\x9d\x8c"),  # X mark variant
    (b"\xc3\xa2\xc2\x9a\xc2\xa0", b"\xe2\x9a\xa0"),  # Warning
    (b"\xc3\xa2\xc5\x93\xc2\xa8", b"\xe2\x8f\xb0"),  # Timer
    # Punctuation and symbols
    (b"\xc3\xa2\xe2\x82\xac\xc2\xa2", b"\xe2\x80\xa2"),  # bullet
    (b"\xc3\xa2\xe2\x82\xac\xe2\x80\x9d", b"\xe2\x80\x94"),  # em dash
    (b"\xc3\xa2\xe2\x82\xac\xe2\x84\xa2", b"\xe2\x80\x99"),  # right single quote
    (b"\xc3\xa2\xe2\x82\xac\xc5\x93", b"\xe2\x80\x9c"),  # left double quote
    (b"\xc3\x82\xc2\xb0", b"\xc2\xb0"),  # degree
    (b"\xc3\x82\xc2\xa3", b"\xc2\xa3"),  # pound sign
    (b"\xc3\x82\xc2\xb2", b"\xc2\xb2"),  # superscript 2
    (b"\xc3\x82\xc2\xb3", b"\xc2\xb3"),  # superscript 3
    (b"\xc3\x82\xc2\xab", b"\xc2\xab"),  # left guillemet
    (b"\xc3\x82\xc2\xbb", b"\xc2\xbb"),  # right guillemet
]


def fix_file_bytes(filepath: str, check_only: bool = False) -> int:
    """Fix a single file using bytes replacement.

    Returns number of issues found/fixed.
    """
    try:
        with open(filepath, "rb") as f:
            content = f.read()

        new_content = content
        issues = 0

        for bad, good in REPLACEMENTS:
            count = new_content.count(bad)
            if count > 0:
                issues += count
                if not check_only:
                    new_content = new_content.replace(bad, good)

        if issues > 0 and not check_only:
            with open(filepath, "wb") as f:
                f.write(new_content)

        return issues

    except Exception as e:
        print(f"  Error {filepath}: {e}")
        return 0


def fix_files(check_only: bool = False) -> tuple:
    """Fix or check all files.

    Returns:
        Tuple (issues count, files affected)
    """
    issues_count = 0
    files_affected = 0

    files = glob.glob("tests/**/*.py", recursive=True) + glob.glob("src/**/*.py", recursive=True)

    for filepath in files:
        issues = fix_file_bytes(filepath, check_only)

        if issues > 0:
            issues_count += issues
            files_affected += 1

            if check_only:
                print(f"  Warning: {filepath}: {issues} encoding issue(s)")
            else:
                print(f"  Fixed: {filepath}: {issues} issue(s) corrected")

    return issues_count, files_affected


def main() -> int:
    check_only = "--check" in sys.argv

    if check_only:
        print("Checking for encoding issues...")
    else:
        print("Fixing encoding issues...")
    print()

    issues, files = fix_files(check_only)

    print()
    print("Summary:")
    print(f"   Issues found: {issues}")
    print(f"   Files affected: {files}")

    if issues > 0:
        if check_only:
            print()
            print("Encoding issues detected!")
            print("   Run 'python fix_encoding.py' to fix them")
            return 1
        else:
            print()
            print(f"Fixed {issues} issue(s) in {files} file(s)")
    else:
        print()
        print("No encoding issues detected")

    return 0


if __name__ == "__main__":
    sys.exit(main())
