#!/usr/bin/env python
"""
Script de lancement de l'API REST FastAPI.

Usage:
    # Mode développement (avec rechargement automatique)
    python scripts/run_api.py

    # Mode production
    python scripts/run_api.py --prod

    # Port personnalisé
    python scripts/run_api.py --port 8080
"""

import argparse
import os
import sys

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Lance le serveur API FastAPI."""
    parser = argparse.ArgumentParser(description="Lance l'API REST FastAPI")
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Lancer en mode production (sans rechargement)",
    )
    parser.add_argument(
        "--host",
        default=os.getenv("API_HOST", "127.0.0.1"),
        help="Adresse d'écoute (défaut: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("API_PORT", "8000")),
        help="Port d'écoute (défaut: 8000)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("API_WORKERS", "1")),
        help="Nombre de workers (production uniquement, défaut: 1)",
    )
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("uvicorn non installé. Installez avec: pip install uvicorn[standard]")
        sys.exit(1)

    print(f"🚀 Lancement de l'API sur http://{args.host}:{args.port}")
    print(f"📚 Documentation: http://{args.host}:{args.port}/docs")
    print(f"📖 ReDoc: http://{args.host}:{args.port}/redoc")

    if args.prod:
        print(f"🏭 Mode production avec {args.workers} worker(s)")
        uvicorn.run(
            "src.api:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level="info",
        )
    else:
        print("🔧 Mode développement (rechargement automatique activé)")
        uvicorn.run(
            "src.api:app",
            host=args.host,
            port=args.port,
            reload=True,
            log_level="debug",
        )


if __name__ == "__main__":
    main()
