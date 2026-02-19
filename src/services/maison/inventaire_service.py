"""
Service Inventaire Maison - Gestion des pièces, objets et recherche "Où est...".

Features:
- Hiérarchie Pièce → Conteneur → Objet
- Recherche IA "Où est ma perceuse?"
- Scan code-barres pour localisation
- Valeur assurance par pièce
- Suggestions rangement IA
- Gestion statut objets (à changer, à acheter)
- Versioning pièces et coûts travaux

Architecture:
    Les méthodes sont réparties en mixins pour maintenabilité:
    - InventaireRechercheMixin: recherche "où est", scan, suggestions IA
    - InventaireStatutMixin: statuts objets, liens courses/budget
    - InventaireVersioningMixin: versioning pièces, coûts travaux
"""

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.services.core.base import BaseAIService

from .inventaire_recherche_mixin import InventaireRechercheMixin
from .inventaire_statut_mixin import InventaireStatutMixin
from .inventaire_versioning_mixin import InventaireVersioningMixin
from .schemas import (
    ObjetCreate,
    PieceCreate,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE MAISON
# ═══════════════════════════════════════════════════════════


class InventaireMaisonService(
    InventaireRechercheMixin,
    InventaireStatutMixin,
    InventaireVersioningMixin,
    BaseAIService,
):
    """Service pour la gestion de l'inventaire maison.

    Fonctionnalités:
    - CRUD pièces, conteneurs, objets (ce fichier)
    - Recherche sémantique "Où est..." (InventaireRechercheMixin)
    - Gestion statuts et liens inter-modules (InventaireStatutMixin)
    - Versioning pièces et coûts travaux (InventaireVersioningMixin)
    - Calcul valeur assurance (ce fichier)

    Example:
        >>> service = get_inventaire_service()
        >>> result = await service.rechercher("perceuse")
        >>> print(f"Trouvé dans: {result.emplacement}")
    """

    def __init__(self, client: ClientIA | None = None):
        """Initialise le service inventaire.

        Args:
            client: Client IA optionnel
        """
        if client is None:
            client = ClientIA()
        super().__init__(
            client=client,
            cache_prefix="inventaire_maison",
            default_ttl=3600,
            service_name="inventaire_maison",
        )
        # Cache local des objets pour recherche rapide
        self._cache_objets: dict[str, dict] = {}

    # ─────────────────────────────────────────────────────────
    # GESTION PIÈCES
    # ─────────────────────────────────────────────────────────

    def creer_piece(self, piece: PieceCreate, db: Session | None = None) -> int:
        """Crée une nouvelle pièce.

        Args:
            piece: Données de la pièce
            db: Session DB optionnelle

        Returns:
            ID de la pièce créée
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PieceMaison

        def _impl(session: Session) -> int:
            # Convertir étage texte en entier
            etage_map = {"sous-sol": -1, "rdc": 0, "1er": 1, "2eme": 2, "grenier": 3}
            etage_int = etage_map.get(piece.etage.lower(), 0)

            piece_db = PieceMaison(
                nom=piece.nom,
                etage=etage_int,
                superficie_m2=piece.superficie_m2,
            )
            session.add(piece_db)
            session.commit()
            logger.info(f"Pièce créée: {piece.nom} (ID={piece_db.id})")
            return piece_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def lister_pieces(self, db: Session | None = None) -> list[dict]:
        """Liste toutes les pièces avec stats.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des pièces avec nombre d'objets
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PieceMaison

        def _impl(session: Session) -> list[dict]:
            pieces = session.query(PieceMaison).all()
            return [
                {
                    "id": p.id,
                    "nom": p.nom,
                    "etage": p.etage,
                    "superficie_m2": float(p.superficie_m2) if p.superficie_m2 else None,
                    "nb_objets": len(p.objets),
                }
                for p in pieces
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    # ─────────────────────────────────────────────────────────
    # GESTION OBJETS
    # ─────────────────────────────────────────────────────────

    def ajouter_objet(self, objet: ObjetCreate, db: Session | None = None) -> int:
        """Ajoute un objet à l'inventaire.

        Args:
            objet: Données de l'objet
            db: Session DB optionnelle

        Returns:
            ID de l'objet créé
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison

        def _impl(session: Session) -> int:
            objet_db = ObjetMaison(
                piece_id=objet.conteneur_id or 1,  # Default to first piece if not specified
                nom=objet.nom,
                categorie=objet.categorie.value if objet.categorie else None,
                statut=objet.statut.value if objet.statut else "fonctionne",
                priorite_remplacement=(
                    objet.priorite_remplacement.value if objet.priorite_remplacement else None
                ),
                date_achat=objet.date_achat,
                prix_achat=objet.prix_achat,
                prix_remplacement_estime=objet.cout_remplacement_estime,
                marque=objet.marque,
                modele=objet.modele,
                notes=objet.notes,
            )
            session.add(objet_db)
            session.commit()
            logger.info(f"Objet créé: {objet.nom} (ID={objet_db.id})")
            return objet_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def deplacer_objet(
        self,
        objet_id: int,
        nouveau_conteneur_id: int,
        db: Session | None = None,
    ) -> bool:
        """Déplace un objet vers un autre conteneur.

        Args:
            objet_id: ID de l'objet
            nouveau_conteneur_id: ID du nouveau conteneur (piece_id)
            db: Session DB optionnelle

        Returns:
            True si déplacé avec succès
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison

        def _impl(session: Session) -> bool:
            objet = session.query(ObjetMaison).filter(ObjetMaison.id == objet_id).first()
            if not objet:
                logger.warning(f"Objet {objet_id} non trouvé")
                return False
            objet.piece_id = nouveau_conteneur_id
            session.commit()
            logger.info(f"Objet {objet_id} déplacé vers pièce {nouveau_conteneur_id}")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    # ─────────────────────────────────────────────────────────
    # VALEUR ASSURANCE
    # ─────────────────────────────────────────────────────────

    def calculer_valeur_piece(self, piece_id: int, db: Session | None = None) -> Decimal:
        """Calcule la valeur totale des objets d'une pièce.

        Args:
            piece_id: ID de la pièce
            db: Session DB optionnelle

        Returns:
            Valeur totale en euros
        """
        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison

        def _impl(session: Session) -> Decimal:
            total = (
                session.query(func.sum(ObjetMaison.prix_achat))
                .filter(ObjetMaison.piece_id == piece_id)
                .scalar()
            )
            return Decimal(str(total or 0))

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def calculer_valeur_totale(self, db: Session | None = None) -> dict[str, Decimal]:
        """Calcule la valeur totale par pièce et globale.

        Args:
            db: Session DB optionnelle

        Returns:
            Dict avec valeur par pièce et total
        """
        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison, PieceMaison

        def _impl(session: Session) -> dict[str, Decimal]:
            # Agrégation par pièce
            resultats = (
                session.query(
                    PieceMaison.nom,
                    func.coalesce(func.sum(ObjetMaison.prix_achat), 0).label("total"),
                )
                .outerjoin(ObjetMaison, PieceMaison.id == ObjetMaison.piece_id)
                .group_by(PieceMaison.id, PieceMaison.nom)
                .all()
            )

            valeurs = {nom: Decimal(str(total)) for nom, total in resultats}
            valeurs["total"] = sum(valeurs.values(), Decimal("0"))
            return valeurs

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def generer_inventaire_assurance(self, db: Session | None = None) -> list[dict]:
        """Génère un inventaire pour déclaration assurance.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des objets avec valeurs pour assurance
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison, PieceMaison

        def _impl(session: Session) -> list[dict]:
            objets = (
                session.query(ObjetMaison, PieceMaison.nom.label("piece_nom"))
                .join(PieceMaison, ObjetMaison.piece_id == PieceMaison.id)
                .filter(ObjetMaison.prix_achat.isnot(None))
                .filter(ObjetMaison.prix_achat > 0)
                .all()
            )

            return [
                {
                    "id": obj.ObjetMaison.id,
                    "nom": obj.ObjetMaison.nom,
                    "piece": obj.piece_nom,
                    "categorie": obj.ObjetMaison.categorie,
                    "marque": obj.ObjetMaison.marque,
                    "modele": obj.ObjetMaison.modele,
                    "date_achat": (
                        obj.ObjetMaison.date_achat.isoformat()
                        if obj.ObjetMaison.date_achat
                        else None
                    ),
                    "prix_achat": float(obj.ObjetMaison.prix_achat),
                    "valeur_actuelle": float(
                        obj.ObjetMaison.prix_remplacement_estime or obj.ObjetMaison.prix_achat
                    ),
                }
                for obj in objets
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def obtenir_service_inventaire_maison(client: ClientIA | None = None) -> InventaireMaisonService:
    """Factory pour obtenir le service inventaire maison (convention française).

    Args:
        client: Client IA optionnel

    Returns:
        Instance de InventaireMaisonService
    """
    return InventaireMaisonService(client=client)


def get_inventaire_service(client: ClientIA | None = None) -> InventaireMaisonService:
    """Factory pour obtenir le service inventaire maison (alias anglais)."""
    return obtenir_service_inventaire_maison(client)
