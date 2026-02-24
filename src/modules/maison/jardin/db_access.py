"""
Accès base de données pour le module Jardin.

Fait le pont entre l'UI (listes de dicts en session_state)
et la base de données (modèles SQLAlchemy ElementJardin/JournalJardin).
"""

import logging
import re
from datetime import date

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import ElementJardin, JournalJardin

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DEPUIS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=[])
def charger_plantes_jardin(session=None) -> list[dict]:
    """Charge les plantes du jardin depuis la DB.

    Convertit les ElementJardin en dicts compatibles avec l'UI existante.
    """
    items = (
        session.query(ElementJardin)
        .filter(ElementJardin.statut == "actif")
        .order_by(ElementJardin.cree_le.desc())
        .all()
    )

    plantes = []
    for item in items:
        plantes.append(
            {
                "db_id": item.id,
                "plante_id": item.nom,
                "surface_m2": 1.0,  # Non stocké en DB, valeur par défaut
                "quantite": 1,
                "zone": item.location or "",
                "semis_fait": item.statut == "actif",
                "plante_en_terre": item.date_plantation is not None,
                "date_ajout": item.cree_le.date().isoformat()
                if item.cree_le
                else date.today().isoformat(),
                "categorie": item.type,
            }
        )

    logger.debug(f"Chargé {len(plantes)} plantes jardin depuis la DB")
    return plantes


@avec_session_db
@avec_gestion_erreurs(default_return=[])
def charger_recoltes_jardin(session=None) -> list[dict]:
    """Charge l'historique des récoltes depuis la DB.

    Convertit les JournalJardin (action='récolte') en dicts compatibles.
    """
    logs = (
        session.query(JournalJardin)
        .filter(JournalJardin.action == "récolte")
        .order_by(JournalJardin.date.desc())
        .all()
    )

    recoltes = []
    for log in logs:
        # Retrouver le nom de plante si possible
        plante_id = ""
        if log.garden_item:
            plante_id = log.garden_item.nom

        # Extraire quantité des notes si possible (format: "X.X kg")
        quantite_kg = 0.0
        if log.notes:
            try:
                # Tenter d'extraire un nombre des notes
                match = re.search(r"([\d.]+)\s*kg", log.notes)
                if match:
                    quantite_kg = float(match.group(1))
            except (ValueError, AttributeError):
                pass

        recoltes.append(
            {
                "db_id": log.id,
                "plante_id": plante_id,
                "quantite_kg": quantite_kg,
                "date": log.date.isoformat(),
                "notes": log.notes or "",
            }
        )

    logger.debug(f"Chargé {len(recoltes)} récoltes depuis la DB")
    return recoltes


# ═══════════════════════════════════════════════════════════
# ÉCRITURE VERS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=None)
def ajouter_plante_jardin(plante: dict, session=None) -> dict | None:
    """Persiste une nouvelle plante en DB.

    Args:
        plante: Dict avec données de la plante (format UI)

    Returns:
        Dict mis à jour avec db_id
    """
    item = ElementJardin(
        nom=plante.get("plante_id", "Inconnue"),
        type=plante.get("categorie", "légume"),
        location=plante.get("zone"),
        statut="actif",
        date_plantation=date.today() if plante.get("plante_en_terre") else None,
        notes=None,
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    plante["db_id"] = item.id
    logger.info(f"Plante jardin ajoutée en DB: {item.nom} (id={item.id})")
    return plante


@avec_session_db
@avec_gestion_erreurs(default_return=False)
def mettre_a_jour_plante_jardin(db_id: int, updates: dict, session=None) -> bool:
    """Met à jour une plante en DB (semis, plantation, etc.).

    Args:
        db_id: ID en base de données
        updates: Dict des champs à mettre à jour

    Returns:
        True si succès
    """
    item = session.query(ElementJardin).filter(ElementJardin.id == db_id).first()
    if not item:
        return False

    if updates.get("plante_en_terre") and not item.date_plantation:
        item.date_plantation = date.today()

    if "zone" in updates:
        item.location = updates["zone"]

    session.commit()
    logger.info(f"Plante jardin mise à jour: {item.nom} (id={db_id})")
    return True


@avec_session_db
@avec_gestion_erreurs(default_return=False)
def supprimer_plante_jardin(db_id: int, session=None) -> bool:
    """Supprime une plante du jardin.

    Args:
        db_id: ID en base de données

    Returns:
        True si succès
    """
    item = session.query(ElementJardin).filter(ElementJardin.id == db_id).first()
    if item:
        session.delete(item)
        session.commit()
        logger.info(f"Plante jardin supprimée: {item.nom} (id={db_id})")
        return True
    return False


@avec_session_db
@avec_gestion_erreurs(default_return=None)
def ajouter_recolte_jardin(recolte: dict, session=None) -> dict | None:
    """Enregistre une récolte en DB.

    Args:
        recolte: Dict avec données de la récolte

    Returns:
        Dict mis à jour avec db_id
    """
    # Trouver l'item jardin correspondant
    garden_item_id = None
    plante_id = recolte.get("plante_id", "")
    if plante_id:
        item = (
            session.query(ElementJardin)
            .filter(
                ElementJardin.nom == plante_id,
                ElementJardin.statut == "actif",
            )
            .first()
        )
        if item:
            garden_item_id = item.id

    quantite = recolte.get("quantite_kg", 0)
    notes_str = f"{quantite} kg"
    if recolte.get("notes"):
        notes_str += f" - {recolte['notes']}"

    log = JournalJardin(
        garden_item_id=garden_item_id,
        date=date.fromisoformat(recolte.get("date", date.today().isoformat())),
        action="récolte",
        notes=notes_str,
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    recolte["db_id"] = log.id
    logger.info(f"Récolte enregistrée en DB: {plante_id} {quantite}kg (id={log.id})")
    return recolte
