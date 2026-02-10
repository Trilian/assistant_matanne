"""
API REST FastAPI pour l'Assistant Matanne.

Fournit un accès programmatique aux fonctionnalités:
- Recettes (CRUD)
- Inventaire
- Plannings
- Courses

Lancer avec: uvicorn src.api.main:app --reload
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query, Security, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, field_validator

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

# CORS sécurisé - domaines autorisés uniquement
import os
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

# Rate Limiting Middleware
from src.api.rate_limiting import RateLimitMiddleware, rate_limit, check_ai_rate_limit
app.add_middleware(RateLimitMiddleware)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC
# ═══════════════════════════════════════════════════════════


class RecetteBase(BaseModel):
    """Schéma de base pour une recette."""
    nom: str
    description: str | None = None
    temps_preparation: int = Field(15, description="Minutes", ge=0)
    temps_cuisson: int = Field(0, description="Minutes", ge=0)
    portions: int = Field(4, ge=1)
    difficulte: str = "moyen"
    categorie: str | None = None
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide que le nom n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


class RecetteCreate(RecetteBase):
    """Schéma pour créer une recette."""
    ingredients: list[dict] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecetteResponse(RecetteBase):
    """Schéma de réponse pour une recette."""
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    
    model_config = {"from_attributes": True}


class InventaireItemBase(BaseModel):
    """Schéma de base pour un article d'inventaire."""
    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    date_peremption: datetime | None = None
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide que le nom n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()
    
    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float) -> float:
        """Valide que la quantité est positive."""
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        if v == 0:
            raise ValueError("La quantité doit être supérieure à 0")
        return v


class InventaireItemCreate(InventaireItemBase):
    """Schéma pour créer un article."""
    code_barres: str | None = None
    emplacement: str | None = None


class InventaireItemResponse(InventaireItemBase):
    """Schéma de réponse pour un article."""
    id: int
    code_barres: str | None = None
    created_at: datetime | None = None
    
    model_config = {"from_attributes": True}


class PlanningBase(BaseModel):
    """Schéma de base pour un planning."""
    nom: str = "Planning de la semaine"
    date_debut: datetime
    date_fin: datetime | None = None


class RepasBase(BaseModel):
    """Schéma de base pour un repas."""
    type_repas: str  # petit_dejeuner, dejeuner, diner, gouter
    date: datetime
    recette_id: int | None = None
    notes: str | None = None
    
    @field_validator("type_repas")
    @classmethod
    def validate_type_repas(cls, v: str) -> str:
        """Valide que le type de repas est valide."""
        valid_types = ["petit_déjeuner", "petit_dejeuner", "déjeuner", "dejeuner", "dîner", "diner", "goûter", "gouter"]
        if v not in valid_types:
            raise ValueError(f"Type de repas invalide. Doit être parmi: {', '.join(valid_types)}")
        return v


class CourseItemBase(BaseModel):
    """Schéma pour un article de liste de courses."""
    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    coche: bool = False
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide que le nom n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()
    
    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v: float) -> float:
        """Valide que la quantité est positive."""
        if v < 0:
            raise ValueError("La quantité ne peut pas être négative")
        return v


class ListeCoursesResponse(BaseModel):
    """Réponse pour une liste de courses."""
    id: int
    nom: str
    items: list[CourseItemBase]
    created_at: datetime | None = None


class CourseListCreate(BaseModel):
    """Schéma pour créer une liste de courses."""
    nom: str = Field("Liste de courses", min_length=1)
    
    @field_validator("nom")
    @classmethod
    def validate_nom(cls, v: str) -> str:
        """Valide que le nom n'est pas vide."""
        if not v or not v.strip():
            raise ValueError("Le nom ne peut pas être vide")
        return v.strip()


class RepasCreate(RepasBase):
    """Schéma pour créer un repas."""
    pass


class RepasResponse(RepasBase):
    """Schéma de réponse pour un repas."""
    id: int
    created_at: datetime | None = None
    
    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    """Réponse paginée générique."""
    items: list
    total: int
    page: int
    page_size: int
    pages: int


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
    """
    Valide le token JWT Supabase et retourne l'utilisateur.
    
    En mode développement, retourne un utilisateur par défaut si pas de token.
    """
    if not credentials:
        # Mode développement - utilisateur par défaut
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            return {"id": "dev", "email": "dev@local", "role": "admin"}
        raise HTTPException(status_code=401, detail="Token requis")
    
    try:
        from src.services.auth import get_auth_service
        
        auth = get_auth_service()
        
        # Valider le token JWT via Supabase
        user = auth.validate_token(credentials.credentials)
        
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "role": user.role.value,
                "nom": user.nom,
                "prenom": user.prenom,
            }
        
        # Fallback: décoder le JWT pour extraire les infos
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
# ENDPOINTS: SANTÉ
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
        from src.core.database import get_db_context
        with get_db_context() as session:
            session.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {e}"
    
    return HealthResponse(
        status="healthy" if db_status == "ok" else "degraded",
        version="1.0.0",
        database=db_status,
        timestamp=datetime.now()
    )


# ═══════════════════════════════════════════════════════════
# ENDPOINTS: RECETTES
# ═══════════════════════════════════════════════════════════


@app.get("/api/v1/recettes", tags=["Recettes"])
async def list_recettes(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    categorie: str | None = None,
    search: str | None = None,
    user: dict = Depends(get_current_user)
):
    """
    Liste les recettes avec pagination et filtres.
    
    - **page**: Numéro de page (défaut: 1)
    - **page_size**: Taille de page (défaut: 20, max: 100)
    - **categorie**: Filtrer par catégorie
    - **search**: Recherche par nom
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import Recette
        from sqlalchemy import func
        
        with get_db_context() as session:
            query = session.query(Recette)
            
            if categorie:
                query = query.filter(Recette.categorie == categorie)
            
            if search:
                query = query.filter(Recette.nom.ilike(f"%{search}%"))
            
            total = query.count()
            
            items = (
                query
                .order_by(Recette.nom)
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )
            
            return {
                "items": [
                    RecetteResponse.model_validate(r).model_dump()
                    for r in items
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
            
    except Exception as e:
        logger.error(f"Erreur liste recettes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/recettes/{recette_id}", response_model=RecetteResponse, tags=["Recettes"])
async def get_recette(recette_id: int = Path(..., gt=0), user: dict = Depends(get_current_user)):
    """Récupère une recette par son ID."""
    try:
        from src.core.database import get_db_context
        from src.core.models import Recette
        
        with get_db_context() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")
            
            return RecetteResponse.model_validate(recette)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur récupération recette: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/recettes", response_model=RecetteResponse, tags=["Recettes"])
async def create_recette(data: RecetteCreate, user: dict = Depends(require_auth)):
    """Crée une nouvelle recette."""
    try:
        from src.core.database import get_db_context
        from src.core.models import Recette
        
        with get_db_context() as session:
            recette = Recette(
                nom=data.nom,
                description=data.description,
                temps_preparation=data.temps_preparation,
                temps_cuisson=data.temps_cuisson,
                portions=data.portions,
                difficulte=data.difficulte,
                categorie=data.categorie,
            )
            session.add(recette)
            session.commit()
            session.refresh(recette)
            
            return RecetteResponse.model_validate(recette)
            
    except Exception as e:
        logger.error(f"Erreur création recette: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v1/recettes/{recette_id}", response_model=RecetteResponse, tags=["Recettes"])
async def update_recette(
    data: RecetteCreate,
    recette_id: int = Path(..., gt=0),
    user: dict = Depends(require_auth)
):
    """Met à jour une recette existante."""
    try:
        from src.core.database import get_db_context
        from src.core.models import Recette
        
        with get_db_context() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")
            
            for key, value in data.model_dump(exclude_unset=True).items():
                if hasattr(recette, key):
                    setattr(recette, key, value)
            
            session.commit()
            session.refresh(recette)
            
            return RecetteResponse.model_validate(recette)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur mise à jour recette: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/recettes/{recette_id}", tags=["Recettes"])
async def delete_recette(recette_id: int = Path(..., gt=0), user: dict = Depends(require_auth)):
    """Supprime une recette."""
    try:
        from src.core.database import get_db_context
        from src.core.models import Recette
        
        with get_db_context() as session:
            recette = session.query(Recette).filter(Recette.id == recette_id).first()
            
            if not recette:
                raise HTTPException(status_code=404, detail="Recette non trouvée")
            
            session.delete(recette)
            session.commit()
            
            return {"message": "Recette supprimée", "id": recette_id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression recette: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ENDPOINTS: INVENTAIRE
# ═══════════════════════════════════════════════════════════



# Dépendances nommées pour override facile en test
def get_session_override():
    return None
def get_model_override():
    return None
def get_response_model_override():
    return None

@app.get("/api/v1/inventaire", tags=["Inventaire"])
async def list_inventaire(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    categorie: str | None = None,
    expiring_soon: bool = False,
    user: dict = Depends(get_current_user),
):
    """
    Liste les articles de l'inventaire.
    
    - **expiring_soon**: Filtrer les articles qui expirent dans les 7 jours
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import ArticleInventaire
        from datetime import timedelta
        from sqlalchemy.orm import joinedload

        with get_db_context() as session:
            query = session.query(ArticleInventaire).options(joinedload(ArticleInventaire.ingredient))

            if categorie:
                query = query.filter(ArticleInventaire.ingredient.has(categorie=categorie))

            if expiring_soon:
                limit_date = datetime.now() + timedelta(days=7)
                query = query.filter(
                    ArticleInventaire.date_peremption != None,
                    ArticleInventaire.date_peremption <= limit_date
                )

            total = query.count()

            items = (
                query
                .offset((page - 1) * page_size)
                .limit(page_size)
                .all()
            )

            def format_item(item):
                return {
                    "id": item.id,
                    "nom": item.ingredient.nom if item.ingredient else "",
                    "quantite": item.quantite,
                    "unite": item.ingredient.unite if item.ingredient else None,
                    "categorie": item.ingredient.categorie if item.ingredient else None,
                    "date_peremption": item.date_peremption,
                    "code_barres": item.code_barres,
                    "created_at": item.derniere_maj,
                }

            return {
                "items": [format_item(i) for i in items],
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }

    except Exception as e:
        logger.error(f"Erreur liste inventaire: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/inventaire", response_model=InventaireItemResponse, tags=["Inventaire"])
async def create_inventaire_item(
    data: InventaireItemCreate,
    user: dict = Depends(require_auth)
):
    """Ajoute un article à l'inventaire."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ArticleInventaire, Ingredient
        
        with get_db_context() as session:
            # Créer ou récupérer l'ingrédient
            ingredient = session.query(Ingredient).filter(Ingredient.nom == data.nom).first()
            if not ingredient:
                ingredient = Ingredient(
                    nom=data.nom,
                    categorie=data.categorie,
                    unite=data.unite or "pcs"
                )
                session.add(ingredient)
                session.flush()
            
            # Créer l'article d'inventaire
            item = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=data.quantite,
                emplacement=data.emplacement,
                date_peremption=data.date_peremption,
                code_barres=data.code_barres,
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            
            # Préparer la réponse
            return {
                "id": item.id,
                "nom": ingredient.nom,
                "quantite": item.quantite,
                "unite": data.unite,
                "categorie": ingredient.categorie,
                "date_peremption": item.date_peremption,
                "code_barres": item.code_barres,
                "created_at": item.derniere_maj,
            }
            
    except Exception as e:
        logger.error(f"Erreur création article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/inventaire/barcode/{code}", tags=["Inventaire"])
async def get_by_barcode(code: str, user: dict = Depends(get_current_user)):
    """Recherche un article par code-barres."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ArticleInventaire
        
        with get_db_context() as session:
            item = (
                session.query(ArticleInventaire)
                .filter(ArticleInventaire.code_barres == code)
                .first()
            )
            
            if item:
                return InventaireItemResponse.model_validate(item)
            
            # Essayer de chercher dans une API externe
            return {"found": False, "barcode": code, "message": "Article non trouvé"}
            
    except Exception as e:
        logger.error(f"Erreur recherche barcode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ENDPOINTS: COURSES
# ═══════════════════════════════════════════════════════════


@app.get("/api/v1/courses", tags=["Courses"])
async def list_courses(
    active_only: bool = True,
    user: dict = Depends(get_current_user)
):
    """Liste les listes de courses."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ListeCourses
        
        with get_db_context() as session:
            query = session.query(ListeCourses)
            
            if active_only:
                query = query.filter(ListeCourses.archivee == False)
            
            listes = query.order_by(ListeCourses.created_at.desc()).all()
            
            return {
                "items": [
                    {
                        "id": l.id,
                        "nom": l.nom,
                        "items_count": len(l.articles) if hasattr(l, 'articles') else 0,
                        "created_at": l.created_at,
                    }
                    for l in listes
                ]
            }
            
    except Exception as e:
        logger.error(f"Erreur liste courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/courses", tags=["Courses"])
async def create_liste_courses(
    nom: str = "Ma liste",
    user: dict = Depends(require_auth)
):
    """Crée une nouvelle liste de courses."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ListeCourses
        
        with get_db_context() as session:
            liste = ListeCourses(nom=nom)
            session.add(liste)
            session.commit()
            session.refresh(liste)
            
            return {"id": liste.id, "nom": liste.nom, "message": "Liste créée"}
            
    except Exception as e:
        logger.error(f"Erreur création liste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/courses/{liste_id}/items", tags=["Courses"])
async def add_course_item(
    item: CourseItemBase,
    liste_id: int = Path(..., gt=0),
    user: dict = Depends(require_auth)
):
    """Ajoute un article à une liste de courses."""
    try:
        from src.core.database import get_db_context
        from src.core.models import ListeCourses, ArticleCourses
        
        with get_db_context() as session:
            liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
            
            if not liste:
                raise HTTPException(status_code=404, detail="Liste non trouvée")
            
            article = ArticleCourses(
                liste_id=liste_id,
                nom=item.nom,
                quantite=item.quantite,
                unite=item.unite,
                categorie=item.categorie,
                coche=item.coche,
            )
            session.add(article)
            session.commit()
            
            return {"message": "Article ajouté", "item": item.model_dump()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur ajout article: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ENDPOINTS: PLANNING
# ═══════════════════════════════════════════════════════════


@app.get("/api/v1/planning/semaine", tags=["Planning"])
async def get_planning_semaine(
    date: datetime | None = None,
    user: dict = Depends(get_current_user)
):
    """
    Récupère le planning de la semaine.
    
    - **date**: Date de référence (défaut: aujourd'hui)
    """
    try:
        from src.core.database import get_db_context
        from src.core.models import Planning, Repas
        from datetime import timedelta
        
        ref_date = date or datetime.now()
        
        # Trouver le lundi de la semaine
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=7)
        
        with get_db_context() as session:
            repas = (
                session.query(Repas)
                .filter(Repas.date_repas >= start, Repas.date_repas < end)
                .order_by(Repas.date_repas, Repas.type_repas)
                .all()
            )
            
            # Organiser par jour
            planning = {}
            for r in repas:
                jour = r.date_repas.strftime("%A %d/%m")
                if jour not in planning:
                    planning[jour] = []
                planning[jour].append({
                    "type": r.type_repas,
                    "recette_id": r.recette_id,
                    "notes": r.notes,
                })
            
            return {
                "semaine_du": start.strftime("%d/%m/%Y"),
                "semaine_au": (end - timedelta(days=1)).strftime("%d/%m/%Y"),
                "planning": planning
            }
            
    except Exception as e:
        logger.error(f"Erreur planning semaine: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/planning/repas", tags=["Planning"])
async def add_repas(repas: RepasBase, user: dict = Depends(require_auth)):
    """Ajoute un repas au planning."""
    try:
        from datetime import date, timedelta
        from src.core.database import get_db_context
        from src.core.models import Repas, Planning, Recette
        
        with get_db_context() as session:
            # Convertir la date du repas (datetime) en date
            repas_date = repas.date.date() if isinstance(repas.date, datetime) else repas.date
            
            # Valider que la recette existe si recette_id est fourni
            if repas.recette_id:
                recette = session.query(Recette).filter(Recette.id == repas.recette_id).first()
                if not recette:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Recette avec ID {repas.recette_id} n'existe pas"
                    )
            
            # Calculer la semaine pour trouver/créer le Planning
            # Trouve le lundi de la semaine
            semaine_debut = repas_date - timedelta(days=repas_date.weekday())
            semaine_fin = semaine_debut + timedelta(days=6)
            
            # Chercher ou créer le Planning pour cette semaine
            planning = session.query(Planning).filter(
                Planning.semaine_debut == semaine_debut,
                Planning.semaine_fin == semaine_fin
            ).first()
            
            if not planning:
                planning = Planning(
                    nom=f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
                    semaine_debut=semaine_debut,
                    semaine_fin=semaine_fin,
                    actif=True
                )
                session.add(planning)
                session.flush()  # Flush pour obtenir l'ID
            
            new_repas = Repas(
                planning_id=planning.id,
                type_repas=repas.type_repas,
                date_repas=repas_date,
                recette_id=repas.recette_id,
                notes=repas.notes,
            )
            session.add(new_repas)
            session.commit()
            
            return {"message": "Repas ajouté", "id": new_repas.id}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur ajout repas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ENDPOINTS: SUGGESTIONS IA
# ═══════════════════════════════════════════════════════════


@app.get("/api/v1/suggestions/recettes", tags=["IA"])
async def get_suggestions(
    type_repas: str | None = None,
    personnes: int = 4,
    temps_max: int | None = None,
    user: dict = Depends(get_current_user)
):
    """
    Obtient des suggestions de recettes basées sur l'inventaire et l'historique.
    
    - **type_repas**: dejeuner, diner, etc.
    - **personnes**: Nombre de personnes
    - **temps_max**: Temps de préparation maximum en minutes
    """
    try:
        from src.services.suggestions_ia import get_suggestions_ia_service
        
        service = get_suggestions_ia_service()
        
        # Construire le contexte
        contexte = service.construire_contexte(
            type_repas=type_repas or "dîner",
            nb_personnes=personnes,
            temps_minutes=temps_max or 60
        )
        
        # Obtenir les suggestions
        suggestions = service.suggerer_recettes(contexte, nb_suggestions=5)
        
        return {
            "contexte": contexte.model_dump() if contexte else {},
            "suggestions": [s.model_dump() for s in suggestions]
        }
        
    except Exception as e:
        logger.error(f"Erreur suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
