"""
Mixin Statut & Liens inter-modules pour le service Inventaire Maison.

Contient les méthodes de gestion de statut des objets (à changer, à acheter)
et la création de liens vers les modules Courses et Budget.

Usage:
    class InventaireMaisonService(InventaireStatutMixin, BaseAIService):
        ...
"""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from .schemas import (
    ActionObjetResult,
    CategorieObjet,
    DemandeChangementObjet,
    LienObjetBudget,
    LienObjetCourses,
    ObjetAvecStatut,
    ObjetCreate,
    PrioriteRemplacement,
    StatutObjet,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

__all__ = ["InventaireStatutMixin"]


class InventaireStatutMixin:
    """Mixin fournissant la gestion des statuts d'objets et liens inter-modules.

    Accède via ``self`` aux méthodes de InventaireMaisonService:
    - self.ajouter_objet()

    Méthodes publiques:
    - changer_statut_objet() — change le statut + crée liens courses/budget
    - marquer_a_changer() — raccourci "à changer"
    - marquer_a_acheter() — raccourci "à acheter" (objet inexistant)
    - lister_objets_a_remplacer() — liste objets à remplacer/acheter
    """

    # ─────────────────────────────────────────────────────────
    # GESTION STATUT OBJETS (À changer/À acheter)
    # ─────────────────────────────────────────────────────────

    async def changer_statut_objet(
        self,
        demande: DemandeChangementObjet,
        db: Session | None = None,
    ) -> ActionObjetResult:
        """Change le statut d'un objet (à changer, à acheter, etc.).

        Cette méthode gère:
        - Le changement de statut de l'objet
        - La création optionnelle d'un article dans la liste de courses
        - La création optionnelle d'une dépense prévue dans le budget

        Args:
            demande: Données de la demande de changement
            db: Session DB optionnelle

        Returns:
            ActionObjetResult avec les liens créés
        """
        logger.info(
            f"Changement statut objet {demande.objet_id}: "
            f"{demande.ancien_statut} → {demande.nouveau_statut}"
        )

        lien_budget = None
        lien_courses = None
        erreurs = []

        try:
            # 1. Mettre à jour le statut de l'objet
            # TODO: Implémenter avec modèle ObjetMaison
            # Pour l'instant, simulation

            # 2. Si "à acheter", créer article liste courses
            if demande.ajouter_liste_courses and demande.nouveau_statut in [
                StatutObjet.A_ACHETER,
                StatutObjet.A_CHANGER,
            ]:
                lien_courses = await self._creer_article_courses_objet(
                    objet_id=demande.objet_id,
                    cout_estime=demande.cout_estime,
                )

            # 3. Si spécifié, créer dépense budget prévue
            if demande.ajouter_budget and demande.cout_estime:
                lien_budget = await self._creer_depense_budget_objet(
                    objet_id=demande.objet_id,
                    montant=demande.cout_estime,
                    date_prevue=demande.date_souhaitee,
                )

        except Exception as e:
            erreurs.append(str(e))
            logger.error(f"Erreur changement statut: {e}")

        return ActionObjetResult(
            succes=len(erreurs) == 0,
            objet_id=demande.objet_id,
            nouveau_statut=demande.nouveau_statut,
            message=(
                f"Statut mis à jour vers {demande.nouveau_statut.value}"
                if not erreurs
                else f"Erreurs: {', '.join(erreurs)}"
            ),
            lien_budget=lien_budget,
            lien_courses=lien_courses,
            erreurs=erreurs,
        )

    async def marquer_a_changer(
        self,
        objet_id: int,
        raison: str | None = None,
        cout_estime: Decimal | None = None,
        priorite: PrioriteRemplacement = PrioriteRemplacement.NORMALE,
        ajouter_budget: bool = True,
        db: Session | None = None,
    ) -> ActionObjetResult:
        """Raccourci pour marquer un objet "À changer".

        Args:
            objet_id: ID de l'objet
            raison: Raison du remplacement
            cout_estime: Coût estimé du remplacement
            priorite: Priorité du remplacement
            ajouter_budget: Ajouter au budget prévisionnel
            db: Session DB optionnelle

        Returns:
            ActionObjetResult
        """
        demande = DemandeChangementObjet(
            objet_id=objet_id,
            ancien_statut=StatutObjet.FONCTIONNE,  # Sera récupéré de la DB
            nouveau_statut=StatutObjet.A_CHANGER,
            raison=raison,
            priorite=priorite,
            cout_estime=cout_estime,
            ajouter_liste_courses=True,
            ajouter_budget=ajouter_budget,
        )
        return await self.changer_statut_objet(demande, db)

    async def marquer_a_acheter(
        self,
        nom_objet: str,
        piece_id: int,
        categorie: CategorieObjet = CategorieObjet.AUTRE,
        cout_estime: Decimal | None = None,
        priorite: PrioriteRemplacement = PrioriteRemplacement.NORMALE,
        ajouter_courses: bool = True,
        ajouter_budget: bool = True,
        db: Session | None = None,
    ) -> ActionObjetResult:
        """Ajoute un nouvel objet "À acheter" (n'existe pas encore).

        Ex: "Je veux ajouter une bibliothèque dans le salon"

        Args:
            nom_objet: Nom de l'objet à acheter
            piece_id: ID de la pièce destinataire
            categorie: Catégorie de l'objet
            cout_estime: Coût estimé
            priorite: Priorité de l'achat
            ajouter_courses: Ajouter à la liste de courses
            ajouter_budget: Ajouter au budget prévisionnel
            db: Session DB optionnelle

        Returns:
            ActionObjetResult avec l'objet créé
        """
        logger.info(f"Ajout objet à acheter: {nom_objet}")

        # 1. Créer l'objet avec statut "à acheter"
        objet = ObjetCreate(
            nom=nom_objet,
            categorie=categorie,
            statut=StatutObjet.A_ACHETER,
            priorite_remplacement=priorite,
            cout_remplacement_estime=cout_estime,
        )
        # TODO: Sauvegarder en DB et récupérer ID
        objet_id = self.ajouter_objet(objet, db)

        # 2. Créer la demande de changement avec liens
        demande = DemandeChangementObjet(
            objet_id=objet_id,
            ancien_statut=StatutObjet.A_ACHETER,  # Pas de changement
            nouveau_statut=StatutObjet.A_ACHETER,
            priorite=priorite,
            cout_estime=cout_estime,
            ajouter_liste_courses=ajouter_courses,
            ajouter_budget=ajouter_budget,
        )
        return await self.changer_statut_objet(demande, db)

    async def lister_objets_a_remplacer(
        self,
        db: Session | None = None,
    ) -> list[ObjetAvecStatut]:
        """Liste tous les objets à changer ou acheter.

        Returns:
            Liste des objets avec statut à remplacer/acheter
        """
        # TODO: Implémenter avec modèle ObjetMaison
        # Pour l'instant, retourne liste vide
        return []

    # ─────────────────────────────────────────────────────────
    # LIENS INTER-MODULES (Courses / Budget)
    # ─────────────────────────────────────────────────────────

    async def _creer_article_courses_objet(
        self,
        objet_id: int,
        cout_estime: Decimal | None,
    ) -> LienObjetCourses:
        """Crée un article de courses pour un objet à acheter."""
        # TODO: Appeler ServiceCourses.ajouter_article()
        logger.info(f"Création article courses pour objet {objet_id}")
        return LienObjetCourses(
            objet_id=objet_id,
            objet_nom="Objet placeholder",  # Récupérer de la DB
            article_courses_id=None,  # Sera rempli après création
            prix_estime=cout_estime,
        )

    async def _creer_depense_budget_objet(
        self,
        objet_id: int,
        montant: Decimal,
        date_prevue: date | None = None,
    ) -> LienObjetBudget:
        """Crée une dépense budget prévue pour un objet."""
        # TODO: Appeler BudgetService.ajouter_depense_prevue()
        logger.info(f"Création dépense budget pour objet {objet_id}: {montant}€")
        return LienObjetBudget(
            objet_id=objet_id,
            objet_nom="Objet placeholder",  # Récupérer de la DB
            depense_budget_id=None,  # Sera rempli après création
            montant_prevu=montant,
            date_prevue=date_prevue,
        )
