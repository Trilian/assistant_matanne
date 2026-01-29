"""
Module API REST FastAPI.

Ce package fournit une API REST pour l'accès programmatique
aux fonctionnalités de l'Assistant Matanne.

Lancer le serveur:
    uvicorn src.api.main:app --reload --port 8000

Documentation:
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

Endpoints principaux:
    - GET /api/v1/recettes - Liste des recettes
    - GET /api/v1/inventaire - Inventaire
    - GET /api/v1/courses - Listes de courses
    - GET /api/v1/planning/semaine - Planning hebdomadaire
    - GET /api/v1/suggestions/recettes - Suggestions IA
"""

from .main import app

__all__ = ["app"]
