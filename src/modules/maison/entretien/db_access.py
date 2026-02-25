"""
Accès base de données pour le module Entretien.

Fait le pont entre l'UI (listes de dicts en session_state)
et la base de données (modèles SQLAlchemy TacheEntretien/StockMaison).
"""

import logging
from datetime import date

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import TacheEntretien

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DEPUIS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=[])
def charger_objets_entretien(session=None) -> list[dict]:
    """Charge les équipements d'entretien depuis la DB.

    Convertit les TacheEntretien en dicts compatibles avec l'UI existante.

    Returns:
        Liste de dicts au format attendu par l'UI
    """
    tasks = (
        session.query(TacheEntretien)
        .filter(TacheEntretien.fait.is_(False))
        .order_by(TacheEntretien.cree_le.desc())
        .all()
    )

    objets = []
    for task in tasks:
        objets.append(
            {
                "db_id": task.id,
                "objet_id": task.nom,
                "categorie_id": task.categorie,
                "piece": task.piece or "",
                "piece_id": task.piece or "",
                "nom_perso": task.description,
                "date_achat": None,
                "marque": None,
                "date_ajout": task.cree_le.date().isoformat()
                if task.cree_le
                else date.today().isoformat(),
                "frequence_jours": task.frequence_jours,
                "duree_minutes": task.duree_minutes,
                "responsable": task.responsable,
                "priorite": task.priorite,
            }
        )

    logger.debug(f"Chargé {len(objets)} objets entretien depuis la DB")
    return objets


@avec_session_db
@avec_gestion_erreurs(default_return=[])
def charger_historique_entretien(session=None) -> list[dict]:
    """Charge l'historique des tâches complétées depuis la DB.

    Returns:
        Liste de dicts au format attendu par l'UI
    """
    tasks = (
        session.query(TacheEntretien)
        .filter(TacheEntretien.fait.is_(True))
        .order_by(TacheEntretien.modifie_le.desc())
        .all()
    )

    historique = []
    for task in tasks:
        historique.append(
            {
                "db_id": task.id,
                "objet_id": task.nom,
                "tache_nom": task.nom,
                "date": task.derniere_fois.isoformat()
                if task.derniere_fois
                else date.today().isoformat(),
                "categorie_id": task.categorie,
                "piece": task.piece or "",
            }
        )

    logger.debug(f"Chargé {len(historique)} entrées historique entretien depuis la DB")
    return historique


# ═══════════════════════════════════════════════════════════
# ÉCRITURE VERS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=None)
def ajouter_objet_entretien(objet: dict, session=None) -> dict | None:
    """Persiste un nouvel objet d'entretien en DB.

    Args:
        objet: Dict avec les données de l'objet (format UI)

    Returns:
        Dict mis à jour avec db_id, ou None en cas d'erreur
    """
    task = TacheEntretien(
        nom=objet.get("objet_id", "Sans nom"),
        description=objet.get("nom_perso"),
        categorie=objet.get("categorie_id", "divers"),
        piece=objet.get("piece_id") or objet.get("piece"),
        frequence_jours=objet.get("frequence_jours"),
        duree_minutes=objet.get("duree_minutes", 30),
        responsable=objet.get("responsable"),
        priorite=objet.get("priorite", "normale"),
        fait=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    objet["db_id"] = task.id
    logger.info(f"Objet entretien ajouté en DB: {task.nom} (id={task.id})")
    return objet


@avec_session_db
@avec_gestion_erreurs(default_return=False)
def marquer_tache_faite(objet_id: str, tache_nom: str, session=None) -> bool:
    """Marque une tâche comme faite en DB et met à jour la date.

    Args:
        objet_id: Identifiant de l'objet
        tache_nom: Nom de la tâche complétée

    Returns:
        True si succès
    """
    task = (
        session.query(TacheEntretien)
        .filter(
            TacheEntretien.nom == objet_id,
            TacheEntretien.fait.is_(False),
        )
        .first()
    )

    if task:
        task.fait = True
        task.derniere_fois = date.today()
        session.commit()
        logger.info(f"Tâche entretien marquée faite: {tache_nom}")
        return True

    # Pas de tâche existante — créer une entrée historique
    new_task = TacheEntretien(
        nom=tache_nom,
        categorie="divers",
        fait=True,
        derniere_fois=date.today(),
    )
    session.add(new_task)
    session.commit()
    logger.info(f"Tâche entretien créée et marquée faite: {tache_nom}")
    return True


@avec_session_db
@avec_gestion_erreurs(default_return=False)
def supprimer_objet_entretien(db_id: int, session=None) -> bool:
    """Supprime un objet d'entretien de la DB.

    Args:
        db_id: ID en base de données

    Returns:
        True si succès
    """
    task = session.query(TacheEntretien).filter(TacheEntretien.id == db_id).first()
    if task:
        session.delete(task)
        session.commit()
        logger.info(f"Objet entretien supprimé: {task.nom} (id={db_id})")
        return True
    return False
