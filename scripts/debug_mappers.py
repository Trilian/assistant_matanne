#!/usr/bin/env python3
"""Diagnostic helper to force SQLAlchemy mapper configuration and print full traceback.

Usage: python scripts/debug_mappers.py
"""

import sys
import traceback
from pathlib import Path


def main() -> None:
    try:
        # Ensure repo root is on sys.path so `src` can be imported
        repo_root = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo_root))
        print(f"Added repo root to sys.path: {repo_root}")
        print("Importing src.core.models...")
        import src.core.models as models

        # If the package exposes a loader to import all model modules, call it.
        if hasattr(models, "charger_tous_modeles"):
            print("Calling charger_tous_modeles() to import all model modules...")
            try:
                models.charger_tous_modeles()
            except Exception:
                print(
                    "charger_tous_modeles() raised an exception; continuing to force registry access..."
                )

        # Try to access the Declarative Base registry to force mapper configuration
        from src.core.models.base import Base

        print("Accessing Base.registry to enumerate mappers...")
        registry = getattr(Base, "registry", None)
        if registry is None:
            print("No registry attribute found on Base; nothing to enumerate.")
            return

        # Iterate over mappers to trigger any configuration exceptions
        print("Enumerating mappers:")
        for mapper in registry.mappers:
            try:
                print(f"- Mapper: {mapper}")
            except Exception:
                print("- Mapper repr failed; printing full exception")
                traceback.print_exc()

        print("Finished enumerating mappers.")

    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
