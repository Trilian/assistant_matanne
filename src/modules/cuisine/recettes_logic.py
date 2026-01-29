"""
Logique métier du module Recettes (sans UI Streamlit).
Fonctions pures testables indépendamment de Streamlit.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.core.database import get_db_context
from src.services.recettes import get_recette_service
from src.core.models import Recette, Repas


# ═══════════════════════════════════════════════════════════
# LOGIQUE RECETTES - LECTURE
# ═══════════════════════════════════════════════════════════

def get_toutes_recettes(db: Optional[Session] = None) -> List[Recette]:
    """Récupère toutes les recettes."""
    with get_db_context() as session:
        service = get_recette_service(session)
        return session.query(Recette).all()


def get_recette_by_id(recette_id: int, db: Optional[Session] = None) -> Optional[Recette]:
    """Récupère une recette par son ID."""
    with get_db_context() as session:
        return session.query(Recette).filter(Recette.id == recette_id).first()


def rechercher_recettes(
    query: str,
    categorie: Optional[str] = None,
    difficulte: Optional[str] = None,
    temps_max: Optional[int] = None,
    db: Optional[Session] = None
) -> List[Recette]:
    """Recherche recettes avec filtres."""
    with get_db_context() as session:
        q = session.query(Recette)
        
        if query:
            q = q.filter(Recette.nom.ilike(f"%{query}%"))
        if categorie:
            q = q.filter(Recette.categorie == categorie)
        if difficulte:
            q = q.filter(Recette.difficulte == difficulte)
        if temps_max:
            q = q.filter(Recette.temps_preparation <= temps_max)
        
        return q.all()


def get_recettes_par_categorie(categorie: str, db: Optional[Session] = None) -> List[Recette]:
    """Récupère recettes d'une catégorie."""
    with get_db_context() as session:
        return session.query(Recette).filter(Recette.categorie == categorie).all()


def get_recettes_favorites(db: Optional[Session] = None) -> List[Recette]:
    """Récupère les recettes favorites."""
    with get_db_context() as session:
        return session.query(Recette).filter(Recette.favorite == True).all()


# ═══════════════════════════════════════════════════════════
# LOGIQUE RECETTES - CRÉATION/MODIFICATION
# ═══════════════════════════════════════════════════════════

def creer_recette(
    nom: str,
    ingredients: List[str],
    instructions: List[str],
    categorie: str = "autre",
    difficulte: str = "moyenne",
    temps_preparation: int = 30,
    portions: int = 4,
    calories: Optional[int] = None,
    db: Optional[Session] = None
) -> Recette:
    """Crée une nouvelle recette."""
    with get_db_context() as session:
        service = get_recette_service(session)
        
        recette = Recette(
            nom=nom,
            ingredients=ingredients,
            instructions=instructions,
            categorie=categorie,
            difficulte=difficulte,
            temps_preparation=temps_preparation,
            portions=portions,
            calories=calories
        )
        
        session.add(recette)
        session.commit()
        session.refresh(recette)
        return recette


def mettre_a_jour_recette(
    recette_id: int,
    updates: Dict[str, Any],
    db: Optional[Session] = None
) -> Optional[Recette]:
    """Met à jour une recette existante."""
    with get_db_context() as session:
        recette = session.query(Recette).filter(Recette.id == recette_id).first()
        
        if not recette:
            return None
        
        for key, value in updates.items():
            if hasattr(recette, key):
                setattr(recette, key, value)
        
        session.commit()
        session.refresh(recette)
        return recette


def supprimer_recette(recette_id: int, db: Optional[Session] = None) -> bool:
    """Supprime une recette."""
    with get_db_context() as session:
        recette = session.query(Recette).filter(Recette.id == recette_id).first()
        
        if not recette:
            return False
        
        session.delete(recette)
        session.commit()
        return True


def toggle_favorite(recette_id: int, db: Optional[Session] = None) -> bool:
    """Toggle le statut favori d'une recette."""
    with get_db_context() as session:
        recette = session.query(Recette).filter(Recette.id == recette_id).first()
        
        if not recette:
            return False
        
        recette.favorite = not recette.favorite
        session.commit()
        return recette.favorite


# ═══════════════════════════════════════════════════════════
# LOGIQUE PLANNING REPAS
# ═══════════════════════════════════════════════════════════

def get_planning_semaine(date_debut: date, date_fin: date, db: Optional[Session] = None) -> List[Repas]:
    """Récupère le planning de repas pour une période."""
    with get_db_context() as session:
        return session.query(Repas).filter(
            Repas.date_repas >= date_debut,
            Repas.date_repas <= date_fin
        ).all()


def ajouter_repas_planning(
    recette_id: int,
    date_repas: date,
    type_repas: str = "diner",
    db: Optional[Session] = None
) -> Repas:
    """Ajoute un repas au planning."""
    with get_db_context() as session:
        repas = Repas(
            recette_id=recette_id,
            date_repas=date_repas,
            type_repas=type_repas
        )
        
        session.add(repas)
        session.commit()
        session.refresh(repas)
        return repas


# ═══════════════════════════════════════════════════════════
# LOGIQUE CALCULS & STATISTIQUES
# ═══════════════════════════════════════════════════════════

def calculer_cout_recette(recette: Recette, prix_ingredients: Dict[str, float]) -> float:
    """Calcule le coût estimé d'une recette."""
    cout_total = 0.0
    
    for ingredient in recette.ingredients:
        # Recherche de l'ingrédient dans le dictionnaire des prix
        for nom_ingredient, prix in prix_ingredients.items():
            if nom_ingredient.lower() in ingredient.lower():
                cout_total += prix
                break
    
    return round(cout_total, 2)


def calculer_calories_portion(recette: Recette) -> Optional[float]:
    """Calcule les calories par portion."""
    if not recette.calories or not recette.portions:
        return None
    
    return round(recette.calories / recette.portions, 2)


def get_statistiques_recettes(db: Optional[Session] = None) -> Dict[str, Any]:
    """Calcule les statistiques sur les recettes."""
    with get_db_context() as session:
        recettes = session.query(Recette).all()
        
        if not recettes:
            return {
                "total": 0,
                "par_categorie": {},
                "par_difficulte": {},
                "temps_moyen": 0,
                "favorites": 0
            }
        
        stats = {
            "total": len(recettes),
            "par_categorie": {},
            "par_difficulte": {},
            "temps_moyen": sum(r.temps_preparation or 0 for r in recettes) / len(recettes),
            "favorites": sum(1 for r in recettes if r.favorite)
        }
        
        # Par catégorie
        for recette in recettes:
            cat = recette.categorie or "autre"
            stats["par_categorie"][cat] = stats["par_categorie"].get(cat, 0) + 1
        
        # Par difficulté
        for recette in recettes:
            diff = recette.difficulte or "moyenne"
            stats["par_difficulte"][diff] = stats["par_difficulte"].get(diff, 0) + 1
        
        return stats


def valider_recette(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Valide les données d'une recette."""
    if not data.get("nom"):
        return False, "Le nom est requis"
    
    if not data.get("ingredients") or len(data["ingredients"]) == 0:
        return False, "Au moins un ingrédient est requis"
    
    if not data.get("instructions") or len(data["instructions"]) == 0:
        return False, "Au moins une instruction est requise"
    
    if data.get("temps_preparation", 0) < 0:
        return False, "Le temps de préparation doit être positif"
    
    if data.get("portions", 0) <= 0:
        return False, "Le nombre de portions doit être supérieur à 0"
    
    return True, None
