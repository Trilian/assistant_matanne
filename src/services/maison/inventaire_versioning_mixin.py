"""
Mixin Versioning & Travaux pour le service Inventaire Maison.

Contient les méthodes de versioning des pièces, planification de
réorganisation et suivi des coûts de travaux.

Usage:
    class InventaireMaisonService(InventaireVersioningMixin, BaseAIService):
        ...
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from .schemas import (
    ActionObjetResult,
    CoutTravauxPiece,
    ModificationPieceCreate,
    PieceVersion,
    PlanReorganisationPiece,
    ResumeTravauxMaison,
    StatutObjet,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

__all__ = ["InventaireVersioningMixin"]


class InventaireVersioningMixin:
    """Mixin fournissant le versioning de pièces et le suivi des travaux.

    Accède via ``self`` aux méthodes de InventaireMaisonService:
    - self.ajouter_objet()
    - self._creer_depense_budget_objet() (via InventaireStatutMixin)

    Méthodes publiques:
    - creer_version_piece() — snapshot d'une pièce
    - lister_versions_piece() — historique des versions
    - restaurer_version_piece() — restauration d'une version
    - planifier_reorganisation() — plan complet de réaménagement
    - ajouter_cout_travaux() — enregistrer un coût de travaux
    - obtenir_resume_travaux() — résumé global des travaux maison
    - lister_couts_par_piece() — coûts par pièce
    """

    # ─────────────────────────────────────────────────────────
    # VERSIONING PIÈCES
    # ─────────────────────────────────────────────────────────

    def creer_version_piece(
        self,
        piece_id: int,
        nom_version: str,
        modifications: list[ModificationPieceCreate] | None = None,
        commentaire: str | None = None,
        db: Session | None = None,
    ) -> PieceVersion:
        """Crée une nouvelle version d'une pièce (snapshot).

        Permet de garder un historique des réaménagements.

        Args:
            piece_id: ID de la pièce
            nom_version: Nom descriptif (ex: "Avant rénovation 2024")
            modifications: Liste des modifications effectuées
            commentaire: Commentaire libre
            db: Session DB optionnelle

        Returns:
            PieceVersion créée
        """
        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import VersionPiece

        logger.info(f"Création version pièce {piece_id}: {nom_version}")

        # Calculer coût total des modifications
        cout_total = Decimal("0")
        if modifications:
            cout_total = sum(m.cout_estime for m in modifications)

        def _impl(session: Session) -> PieceVersion:
            # Récupérer le numéro de version suivant
            max_version = (
                session.query(func.max(VersionPiece.version))
                .filter(VersionPiece.piece_id == piece_id)
                .scalar()
                or 0
            )
            new_version = max_version + 1

            # Créer la version en DB
            version_db = VersionPiece(
                piece_id=piece_id,
                version=new_version,
                type_modification="snapshot",
                titre=nom_version,
                description=commentaire,
                date_modification=datetime.now().date(),
                cout_total=cout_total,
            )
            session.add(version_db)
            session.commit()

            return PieceVersion(
                id=version_db.id,
                piece_id=piece_id,
                numero_version=new_version,
                date_creation=version_db.created_at or datetime.now(),
                nom_version=nom_version,
                modifications=modifications or [],
                cout_total_version=cout_total,
                commentaire=commentaire,
            )

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def lister_versions_piece(
        self,
        piece_id: int,
        db: Session | None = None,
    ) -> list[PieceVersion]:
        """Liste l'historique des versions d'une pièce.

        Args:
            piece_id: ID de la pièce
            db: Session DB optionnelle

        Returns:
            Liste des versions ordonnées par date
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import VersionPiece as VersionPieceDB

        def _impl(session: Session) -> list[PieceVersion]:
            versions = (
                session.query(VersionPieceDB)
                .filter(VersionPieceDB.piece_id == piece_id)
                .order_by(VersionPieceDB.date_modification.desc())
                .all()
            )
            return [
                PieceVersion(
                    id=v.id,
                    piece_id=v.piece_id,
                    numero_version=v.version,
                    date_creation=v.created_at or datetime.now(),
                    nom_version=v.titre,
                    modifications=[],
                    cout_total_version=v.cout_total or Decimal("0"),
                    commentaire=v.description,
                )
                for v in versions
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def restaurer_version_piece(
        self,
        piece_id: int,
        version_id: int,
        db: Session | None = None,
    ) -> bool:
        """Restaure une pièce à une version antérieure.

        Args:
            piece_id: ID de la pièce
            version_id: ID de la version à restaurer
            db: Session DB optionnelle

        Returns:
            True si restauration réussie
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import PieceMaison, VersionPiece

        logger.info(f"Restauration pièce {piece_id} vers version {version_id}")

        def _impl(session: Session) -> bool:
            # Récupérer la version à restaurer
            version = (
                session.query(VersionPiece)
                .filter(VersionPiece.id == version_id, VersionPiece.piece_id == piece_id)
                .first()
            )
            if not version:
                logger.error(f"Version {version_id} non trouvée pour pièce {piece_id}")
                return False

            # Récupérer la pièce
            piece = session.query(PieceMaison).filter(PieceMaison.id == piece_id).first()
            if not piece:
                logger.error(f"Pièce {piece_id} non trouvée")
                return False

            # Créer une nouvelle version "avant restauration"
            version_actuelle = VersionPiece(
                piece_id=piece_id,
                titre=f"Avant restauration vers v{version_id}",
                description="Sauvegarde automatique avant restauration",
                cout_total=Decimal("0"),
            )
            session.add(version_actuelle)

            # Restaurer les métadonnées de la version sauvegardée
            if version.titre:
                piece.nom = version.titre.replace("Version: ", "")
            if version.description:
                piece.notes = version.description

            session.commit()
            logger.info(f"Pièce {piece_id} restaurée vers version {version_id}")
            return True

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    async def planifier_reorganisation(
        self,
        plan: PlanReorganisationPiece,
        db: Session | None = None,
    ) -> ActionObjetResult:
        """Planifie une réorganisation complète d'une pièce.

        Crée automatiquement:
        - Une version "avant" de la pièce
        - Les articles à acheter dans la liste de courses
        - Le budget prévisionnel pour les travaux

        Args:
            plan: Plan de réorganisation
            db: Session DB optionnelle

        Returns:
            ActionObjetResult avec récapitulatif
        """
        logger.info(f"Planification réorganisation pièce {plan.piece_id}: {plan.nom_version}")

        erreurs = []

        try:
            # 1. Créer version "avant"
            self.creer_version_piece(
                piece_id=plan.piece_id,
                nom_version=f"Avant: {plan.nom_version}",
                db=db,
            )

            # 2. Créer les objets "à acheter"
            for objet in plan.objets_a_acheter:
                objet.statut = StatutObjet.A_ACHETER
                self.ajouter_objet(objet, db)

            # 3. Ajouter au budget si demandé
            if plan.ajouter_au_budget_global and plan.budget_total_estime > 0:
                await self._creer_depense_budget_objet(
                    objet_id=0,  # Lié à la pièce, pas un objet
                    montant=plan.budget_total_estime,
                    date_prevue=plan.date_fin_prevue,
                )

        except Exception as e:
            erreurs.append(str(e))

        return ActionObjetResult(
            succes=len(erreurs) == 0,
            objet_id=0,  # Pas d'objet spécifique
            nouveau_statut=StatutObjet.A_ACHETER,
            message=f"Réorganisation planifiée: {plan.nom_version}",
            erreurs=erreurs,
        )

    # ─────────────────────────────────────────────────────────
    # COÛTS TRAVAUX
    # ─────────────────────────────────────────────────────────

    def ajouter_cout_travaux(
        self,
        cout: CoutTravauxPiece,
        db: Session | None = None,
    ) -> int:
        """Enregistre un coût de travaux pour une pièce.

        Args:
            cout: Données du coût
            db: Session DB optionnelle

        Returns:
            ID du coût créé
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import CoutTravaux, VersionPiece

        logger.info(f"Ajout coût travaux pièce {cout.piece_id}: {cout.budget_prevu}€")

        def _impl(session: Session) -> int:
            # Trouver ou créer une version pour ce coût
            version = (
                session.query(VersionPiece)
                .filter(VersionPiece.piece_id == cout.piece_id)
                .order_by(VersionPiece.version.desc())
                .first()
            )

            if not version:
                # Créer une version par défaut
                version = VersionPiece(
                    piece_id=cout.piece_id,
                    version=1,
                    type_modification=cout.type_travaux.value,
                    titre=cout.description,
                    date_modification=cout.date_debut or datetime.now().date(),
                    cout_total=cout.budget_prevu,
                )
                session.add(version)
                session.flush()

            cout_db = CoutTravaux(
                version_id=version.id,
                categorie=cout.type_travaux.value,
                libelle=cout.description,
                montant=cout.budget_prevu,
                fournisseur=cout.fournisseur,
                date_paiement=cout.date_fin,
            )
            session.add(cout_db)
            session.commit()
            return cout_db.id

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def obtenir_resume_travaux(
        self,
        db: Session | None = None,
    ) -> ResumeTravauxMaison:
        """Obtient un résumé de tous les travaux maison.

        Args:
            db: Session DB optionnelle

        Returns:
            ResumeTravauxMaison avec totaux et statistiques
        """
        from sqlalchemy import func

        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import CoutTravaux, VersionPiece

        def _impl(session: Session) -> ResumeTravauxMaison:
            # Total budgets prévus
            total_prevu = session.query(func.sum(CoutTravaux.montant)).scalar() or Decimal("0")

            # Compter les versions par type (approximation du statut)
            versions = session.query(VersionPiece).all()
            travaux_total = len(versions)

            # Prévoir/en cours/terminé basé sur les dates
            from datetime import date

            aujourd_hui = date.today()
            en_cours = sum(
                1 for v in versions if v.date_modification and v.date_modification >= aujourd_hui
            )
            termines = travaux_total - en_cours

            return ResumeTravauxMaison(
                budget_total_prevu=Decimal(str(total_prevu)),
                budget_total_depense=Decimal(str(total_prevu)) * Decimal("0.5"),  # Estimation
                budget_restant=Decimal(str(total_prevu)) * Decimal("0.5"),
                travaux_en_cours=en_cours,
                travaux_planifies=0,
                travaux_termines=termines,
            )

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    def lister_couts_par_piece(
        self,
        piece_id: int,
        db: Session | None = None,
    ) -> list[CoutTravauxPiece]:
        """Liste les coûts de travaux pour une pièce.

        Args:
            piece_id: ID de la pièce
            db: Session DB optionnelle

        Returns:
            Liste des coûts de travaux
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import CoutTravaux, PieceMaison, VersionPiece

        def _impl(session: Session) -> list[CoutTravauxPiece]:
            # Query avec jointure
            couts = (
                session.query(CoutTravaux, VersionPiece, PieceMaison.nom.label("piece_nom"))
                .join(VersionPiece, CoutTravaux.version_id == VersionPiece.id)
                .join(PieceMaison, VersionPiece.piece_id == PieceMaison.id)
                .filter(VersionPiece.piece_id == piece_id)
                .all()
            )

            return [
                CoutTravauxPiece(
                    piece_id=piece_id,
                    piece_nom=c.piece_nom,
                    type_travaux=c.CoutTravaux.categorie,
                    description=c.CoutTravaux.libelle,
                    budget_prevu=c.CoutTravaux.montant,
                    budget_reel=c.CoutTravaux.montant,  # Même valeur si pas de suivi réel
                    date_fin=c.CoutTravaux.date_paiement,
                    fournisseur=c.CoutTravaux.fournisseur,
                )
                for c in couts
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)
