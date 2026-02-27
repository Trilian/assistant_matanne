"""
Service Visualisation Maison — CRUD pièces avec positions et données enrichies.

Fournit les opérations de lecture/écriture pour le plan 2D/3D de la maison:
- Chargement des pièces avec objets, travaux, entretien
- Sauvegarde des positions (drag & drop)
- Historique des travaux par pièce
- Statistiques globales

Usage:
    service = get_visualisation_service()
    pieces = service.obtenir_pieces_avec_details()
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES PIÈCES PAR DÉFAUT
# ═══════════════════════════════════════════════════════════

PIECES_DEFAUT = [
    {
        "nom": "Salon",
        "type_piece": "salon",
        "etage": 0,
        "superficie_m2": 25,
        "position_x": 20,
        "position_y": 20,
        "largeur_px": 200,
        "hauteur_px": 160,
    },
    {
        "nom": "Cuisine",
        "type_piece": "cuisine",
        "etage": 0,
        "superficie_m2": 15,
        "position_x": 240,
        "position_y": 20,
        "largeur_px": 160,
        "hauteur_px": 130,
    },
    {
        "nom": "Chambre parentale",
        "type_piece": "chambre_parentale",
        "etage": 1,
        "superficie_m2": 18,
        "position_x": 20,
        "position_y": 20,
        "largeur_px": 180,
        "hauteur_px": 150,
    },
    {
        "nom": "Chambre Jules",
        "type_piece": "chambre_jules",
        "etage": 1,
        "superficie_m2": 12,
        "position_x": 220,
        "position_y": 20,
        "largeur_px": 140,
        "hauteur_px": 120,
    },
    {
        "nom": "Salle de bain",
        "type_piece": "salle_de_bain",
        "etage": 1,
        "superficie_m2": 8,
        "position_x": 220,
        "position_y": 160,
        "largeur_px": 120,
        "hauteur_px": 100,
    },
    {
        "nom": "Entrée",
        "type_piece": "entree",
        "etage": 0,
        "superficie_m2": 6,
        "position_x": 420,
        "position_y": 20,
        "largeur_px": 80,
        "hauteur_px": 100,
    },
    {
        "nom": "WC",
        "type_piece": "wc",
        "etage": 0,
        "superficie_m2": 3,
        "position_x": 420,
        "position_y": 140,
        "largeur_px": 60,
        "hauteur_px": 60,
    },
    {
        "nom": "Garage",
        "type_piece": "garage",
        "etage": 0,
        "superficie_m2": 20,
        "position_x": 20,
        "position_y": 200,
        "largeur_px": 180,
        "hauteur_px": 140,
    },
]


class VisualisationService:
    """Service pour la visualisation 2D/3D des pièces de la maison."""

    # ─────────────────────────────────────────────────────────
    # LECTURE
    # ─────────────────────────────────────────────────────────

    @avec_cache(ttl=120)
    @avec_session_db
    def obtenir_pieces_avec_details(
        self, etage: int | None = None, db: Session | None = None
    ) -> list[dict]:
        """Charge les pièces avec objets, travaux et tâches d'entretien.

        Args:
            etage: Filtrer par étage (None = tous).
            db: Session injectée.

        Returns:
            Liste de dicts enrichis par pièce.
        """
        from src.core.models.temps_entretien import (
            CoutTravaux,
            ObjetMaison,
            PieceMaison,
            VersionPiece,
        )

        query = db.query(PieceMaison)
        if etage is not None:
            query = query.filter(PieceMaison.etage == etage)

        pieces = query.order_by(PieceMaison.etage, PieceMaison.nom).all()
        result = []

        for p in pieces:
            # Objets liés
            objets = p.objets or []
            nb_a_reparer = sum(
                1 for o in objets if o.statut in ("a_reparer", "a_changer", "hors_service")
            )

            # Travaux (versions)
            versions = (
                db.query(VersionPiece)
                .filter(VersionPiece.piece_id == p.id)
                .order_by(VersionPiece.date_modification.desc())
                .all()
            )

            cout_total = Decimal("0")
            for v in versions:
                couts = (
                    db.query(func.sum(CoutTravaux.montant))
                    .filter(CoutTravaux.version_id == v.id)
                    .scalar()
                )
                if couts:
                    cout_total += couts

            dernier_travail = versions[0] if versions else None

            # Tâches entretien (via type_piece match)
            taches_retard = 0
            try:
                from src.core.models.habitat import TacheEntretien

                taches = db.query(TacheEntretien).filter(TacheEntretien.piece == p.type_piece).all()
                for t in taches:
                    if hasattr(t, "prochaine_echeance") and t.prochaine_echeance:
                        if t.prochaine_echeance < date.today():
                            taches_retard += 1
            except Exception:
                pass

            # Déterminer l'état visuel
            etat = _calculer_etat_piece(nb_a_reparer, taches_retard, dernier_travail)

            result.append(
                {
                    "id": p.id,
                    "nom": p.nom,
                    "etage": p.etage,
                    "type_piece": p.type_piece or "autre",
                    "superficie_m2": float(p.superficie_m2) if p.superficie_m2 else 0,
                    "description": p.description or "",
                    "position_x": p.position_x,
                    "position_y": p.position_y,
                    "largeur_px": p.largeur_px,
                    "hauteur_px": p.hauteur_px,
                    # Enrichissements
                    "nb_objets": len(objets),
                    "nb_a_reparer": nb_a_reparer,
                    "nb_travaux": len(versions),
                    "cout_total_travaux": float(cout_total),
                    "dernier_travail": {
                        "titre": dernier_travail.titre,
                        "date": dernier_travail.date_modification.isoformat(),
                        "type": dernier_travail.type_modification,
                    }
                    if dernier_travail
                    else None,
                    "taches_retard": taches_retard,
                    "etat": etat,
                }
            )

        return result

    @avec_session_db
    def obtenir_etages_disponibles(self, db: Session | None = None) -> list[int]:
        """Retourne la liste des étages distincts."""
        from src.core.models.temps_entretien import PieceMaison

        etages = db.query(PieceMaison.etage).distinct().order_by(PieceMaison.etage).all()
        return [e[0] for e in etages]

    @avec_session_db
    def obtenir_historique_piece(self, piece_id: int, db: Session | None = None) -> list[dict]:
        """Retourne l'historique des travaux d'une pièce."""
        from src.core.models.temps_entretien import CoutTravaux, VersionPiece

        versions = (
            db.query(VersionPiece)
            .filter(VersionPiece.piece_id == piece_id)
            .order_by(VersionPiece.date_modification.desc())
            .all()
        )

        result = []
        for v in versions:
            couts = db.query(CoutTravaux).filter(CoutTravaux.version_id == v.id).all()
            result.append(
                {
                    "id": v.id,
                    "version": v.version,
                    "titre": v.titre,
                    "type_modification": v.type_modification,
                    "description": v.description,
                    "date_modification": v.date_modification.isoformat(),
                    "cout_total": float(v.cout_total) if v.cout_total else 0,
                    "photo_avant_url": v.photo_avant_url,
                    "photo_apres_url": v.photo_apres_url,
                    "couts_details": [
                        {
                            "categorie": c.categorie,
                            "libelle": c.libelle,
                            "montant": float(c.montant),
                            "fournisseur": c.fournisseur,
                        }
                        for c in couts
                    ],
                }
            )
        return result

    @avec_session_db
    def obtenir_objets_piece(self, piece_id: int, db: Session | None = None) -> list[dict]:
        """Retourne les objets/meubles d'une pièce."""
        from src.core.models.temps_entretien import ObjetMaison

        objets = db.query(ObjetMaison).filter(ObjetMaison.piece_id == piece_id).all()
        return [
            {
                "id": o.id,
                "nom": o.nom,
                "categorie": o.categorie,
                "statut": o.statut,
                "priorite_remplacement": o.priorite_remplacement,
                "prix_achat": float(o.prix_achat) if o.prix_achat else None,
                "marque": o.marque,
            }
            for o in objets
        ]

    # ─────────────────────────────────────────────────────────
    # ÉCRITURE
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def sauvegarder_positions(
        self, pieces_positions: list[dict], db: Session | None = None
    ) -> bool:
        """Sauvegarde les positions de toutes les pièces (bulk update).

        Args:
            pieces_positions: [{id, position_x, position_y, largeur_px, hauteur_px}]
        """
        from src.core.models.temps_entretien import PieceMaison

        try:
            for pp in pieces_positions:
                piece = db.query(PieceMaison).filter_by(id=pp["id"]).first()
                if piece:
                    piece.position_x = pp.get("position_x", piece.position_x)
                    piece.position_y = pp.get("position_y", piece.position_y)
                    piece.largeur_px = pp.get("largeur_px", piece.largeur_px)
                    piece.hauteur_px = pp.get("hauteur_px", piece.hauteur_px)
            db.commit()
            logger.info(f"✅ Positions sauvegardées pour {len(pieces_positions)} pièces")
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde positions: {e}")
            db.rollback()
            return False

    @avec_session_db
    def initialiser_pieces_defaut(self, db: Session | None = None) -> bool:
        """Crée les pièces par défaut si la table est vide."""
        from src.core.models.temps_entretien import PieceMaison

        try:
            count = db.query(PieceMaison).count()
            if count > 0:
                return False

            for p_data in PIECES_DEFAUT:
                piece = PieceMaison(**p_data)
                db.add(piece)
            db.commit()
            logger.info(f"✅ {len(PIECES_DEFAUT)} pièces par défaut créées")
            return True
        except Exception as e:
            logger.error(f"Erreur initialisation pièces: {e}")
            db.rollback()
            return False

    @avec_session_db
    def obtenir_stats_globales(self, db: Session | None = None) -> dict:
        """Statistiques globales pour le plan."""
        from src.core.models.temps_entretien import (
            CoutTravaux,
            ObjetMaison,
            PieceMaison,
            VersionPiece,
        )

        nb_pieces = db.query(PieceMaison).count()
        nb_objets = db.query(ObjetMaison).count()
        nb_travaux = db.query(VersionPiece).count()
        budget_total = db.query(func.sum(CoutTravaux.montant)).scalar() or 0

        return {
            "nb_pieces": nb_pieces,
            "nb_objets": nb_objets,
            "nb_travaux": nb_travaux,
            "budget_total": float(budget_total),
        }


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _calculer_etat_piece(
    nb_a_reparer: int,
    taches_retard: int,
    dernier_travail,
) -> str:
    """Détermine l'état visuel d'une pièce pour le plan 2D."""
    if nb_a_reparer > 2 or taches_retard > 3:
        return "critique"

    if dernier_travail:
        today = date.today()
        mois_ref = today.month - 3
        annee_ref = today.year
        if mois_ref < 1:
            mois_ref += 12
            annee_ref -= 1
        try:
            date_ref = today.replace(month=mois_ref, year=annee_ref)
        except ValueError:
            date_ref = today.replace(month=mois_ref, day=28, year=annee_ref)

        if dernier_travail.date_modification >= date_ref:
            return "travaux_recents"

    if nb_a_reparer > 0 or taches_retard > 0:
        return "attention"

    return "ok"


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_visualisation() -> VisualisationService:
    """Factory française pour le service visualisation."""
    return VisualisationService()


@service_factory("visualisation_maison", tags={"maison", "crud", "visualisation"})
def get_visualisation_service() -> VisualisationService:
    """Factory singleton pour le service visualisation maison."""
    return VisualisationService()
