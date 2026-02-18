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
        logger.info(f"Création version pièce {piece_id}: {nom_version}")

        # Calculer coût total des modifications
        cout_total = Decimal("0")
        if modifications:
            cout_total = sum(m.cout_estime for m in modifications)

        # TODO: Sauvegarder en DB
        # Pour l'instant, retourne version simulée
        return PieceVersion(
            id=1,
            piece_id=piece_id,
            numero_version=1,
            date_creation=datetime.now(),
            nom_version=nom_version,
            modifications=modifications or [],
            cout_total_version=cout_total,
            commentaire=commentaire,
        )

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
        # TODO: Implémenter avec modèle PieceVersion
        return []

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
        # TODO: Implémenter
        logger.info(f"Restauration pièce {piece_id} vers version {version_id}")
        return True

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
        logger.info(f"Ajout coût travaux pièce {cout.piece_id}: {cout.budget_prevu}€")
        # TODO: Sauvegarder en DB
        return 1

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
        # TODO: Implémenter avec données réelles
        return ResumeTravauxMaison(
            budget_total_prevu=Decimal("5000"),
            budget_total_depense=Decimal("2500"),
            budget_restant=Decimal("2500"),
            travaux_en_cours=1,
            travaux_planifies=2,
            travaux_termines=3,
        )

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
        # TODO: Implémenter avec données réelles
        return []
