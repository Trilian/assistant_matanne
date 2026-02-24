"""
Accès base de données pour le module Charges.

Fait le pont entre l'UI (listes de dicts en session_state)
et la base de données (modèle SQLAlchemy DepenseMaison).
"""

import logging
from datetime import date
from decimal import Decimal

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import DepenseMaison

logger = logging.getLogger(__name__)

# Mapping type énergie → unité consommation
UNITES_PAR_TYPE = {
    "electricite": "kWh",
    "gaz": "kWh",
    "eau": "m³",
    "fioul": "L",
    "bois": "stères",
    "internet": None,
    "telephone": None,
    "assurance": None,
    "loyer": None,
}


# ═══════════════════════════════════════════════════════════
# CHARGEMENT DEPUIS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=[])
def charger_factures(session=None) -> list[dict]:
    """Charge toutes les factures depuis la DB.

    Convertit les DepenseMaison en dicts compatibles avec l'UI existante.
    """
    expenses = (
        session.query(DepenseMaison)
        .order_by(DepenseMaison.annee.desc(), DepenseMaison.mois.desc())
        .all()
    )

    factures = []
    for exp in expenses:
        factures.append(
            {
                "db_id": exp.id,
                "type": exp.categorie,
                "montant": float(exp.montant),
                "consommation": exp.consommation or 0.0,
                "date": f"{exp.annee}-{exp.mois:02d}-01",
                "fournisseur": exp.fournisseur,
                "date_ajout": exp.created_at.date().isoformat()
                if exp.created_at
                else date.today().isoformat(),
            }
        )

    logger.debug(f"Chargé {len(factures)} factures depuis la DB")
    return factures


# ═══════════════════════════════════════════════════════════
# ÉCRITURE VERS LA DB
# ═══════════════════════════════════════════════════════════


@avec_session_db
@avec_gestion_erreurs(default_return=None)
def ajouter_facture(facture: dict, session=None) -> dict | None:
    """Persiste une nouvelle facture en DB.

    Args:
        facture: Dict avec les données de la facture (format UI)

    Returns:
        Dict mis à jour avec db_id
    """
    # Parser la date pour extraire mois/année
    date_str = facture.get("date", date.today().isoformat())
    try:
        d = date.fromisoformat(date_str)
        mois = d.month
        annee = d.year
    except (ValueError, TypeError):
        mois = date.today().month
        annee = date.today().year

    type_energie = facture.get("type", "autre")
    unite = UNITES_PAR_TYPE.get(type_energie)

    expense = DepenseMaison(
        categorie=type_energie,
        mois=mois,
        annee=annee,
        montant=Decimal(str(facture.get("montant", 0))),
        consommation=facture.get("consommation"),
        unite_consommation=unite,
        fournisseur=facture.get("fournisseur"),
    )
    session.add(expense)
    session.commit()
    session.refresh(expense)

    facture["db_id"] = expense.id
    logger.info(f"Facture ajoutée en DB: {type_energie} {expense.montant}€ (id={expense.id})")
    return facture


@avec_session_db
@avec_gestion_erreurs(default_return=False)
def supprimer_facture(db_id: int, session=None) -> bool:
    """Supprime une facture de la DB.

    Args:
        db_id: ID en base de données

    Returns:
        True si succès
    """
    expense = session.query(DepenseMaison).filter(DepenseMaison.id == db_id).first()
    if expense:
        session.delete(expense)
        session.commit()
        logger.info(f"Facture supprimée: {expense.categorie} {expense.montant}€ (id={db_id})")
        return True
    return False
