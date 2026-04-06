"""Point d'entrée exécutable pour les plateformes qui recherchent `main.py`."""

import os

import uvicorn

from src.api.main import app

__all__ = ["app", "run"]


def run() -> None:
    """Lance le serveur Uvicorn pour les environnements locaux et les scripts CLI."""
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENVIRONMENT", "development").lower() == "development",
    )


if __name__ == "__main__":
    run()
