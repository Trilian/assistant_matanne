"""
API REST FastAPI pour l'Assistant Matanne - Version Refactorée.

Point d'entrée principal de l'API avec les middlewares et routers.
"""

import logging
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# APPLICATION FASTAPI
# ═══════════════════════════════════════════════════════════


app = FastAPI(
    title="Assistant Matanne API",
    description="API REST pour la gestion familiale",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS sécurisé
_cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
_default_origins = [
    "http://localhost:8501",          # Streamlit local
    "http://localhost:8000",          # API local
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
    "https://matanne.streamlit.app",  # Production Streamlit Cloud
]
_allowed_origins = _cors_origins if _cors_origins else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Middleware de Limitation de Débit
from src.api.limitation_debit import MiddlewareLimitationDebit
app.add_middleware(MiddlewareLimitationDebit)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS COMMUNS
# ═══════════════════════════════════════════════════════════


class HealthResponse(BaseModel):
    """Réponse du health check."""
    status: str
    version: str
    database: str
    timestamp: datetime


# ═══════════════════════════════════════════════════════════
# AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict | None:
    """Valide le token JWT Supabase et retourne l'utilisateur."""
    if not credentials:
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"id": "dev", "email": "dev@local", "role": "admin"}
        raise HTTPException(status_code=401, detail="Token requis")
    
    try:
        from src.services.utilisateur import get_auth_service
        auth = get_auth_service()
        user = auth.validate_token(credentials.credentials)
        
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
            }
        
        payload = auth.decode_jwt_payload(credentials.credentials)
        if payload:
            return {
                "id": payload.get("sub", "unknown"),
                "email": payload.get("email", ""),
                "role": payload.get("user_metadata", {}).get("role", "membre"),
            }
        
        raise HTTPException(status_code=401, detail="Token invalide")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur validation token: {e}")
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")


def require_auth(user: dict = Depends(get_current_user)):
    """Dependency qui exige une authentification."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentification requise")
    return user


# ═══════════════════════════════════════════════════════════
# ENDPOINTS SANTÉ
# ═══════════════════════════════════════════════════════════


@app.get("/", tags=["Santé"])
async def root():
    """Point d'entrée racine."""
    return {
        "message": "API Assistant Matanne",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse, tags=["Santé"])
async def health_check():
    """Vérifie l'état de l'API et de la base de données."""
    db_status = "ok"
    
    try:
        from src.core.database import obtenir_contexte_db
        from sqlalchemy import text
        with obtenir_contexte_db() as session:
            session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"
    
    return HealthResponse(
        status="healthy" if db_status == "ok" else "degraded",
        version="1.0.0",
        database=db_status,
        timestamp=datetime.now()
    )


# ═══════════════════════════════════════════════════════════
# ENREGISTREMENT DES ROUTERS
# ═══════════════════════════════════════════════════════════


from src.api.routes import (
    recettes_router,
    inventaire_router,
    courses_router,
    planning_router,
)

app.include_router(recettes_router)
app.include_router(inventaire_router)
app.include_router(courses_router)
app.include_router(planning_router)


# ═══════════════════════════════════════════════════════════
# ENDPOINT IA (gardé ici car unique)
# ═══════════════════════════════════════════════════════════


@app.get("/api/v1/suggestions/recettes", tags=["IA"])
async def suggest_recettes(
    contexte: str = "repas équilibré",
    nombre: int = 3,
    user: dict = Depends(get_current_user)
):
    """Suggère des recettes via IA."""
    from src.api.limitation_debit import verifier_limite_debit_ia
    
    try:
        verifier_limite_debit_ia(user["id"])
        
        from src.services.recettes import get_recette_service
        service = get_recette_service()
        
        suggestions = service.suggerer_recettes_ia(
            contexte=contexte,
            nombre_suggestions=nombre
        )
        
        return {
            "suggestions": suggestions,
            "contexte": contexte,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suggestions IA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

