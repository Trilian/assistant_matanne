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
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import LogStatutObjet, ObjetMaison

        logger.info(
            f"Changement statut objet {demande.objet_id}: "
            f"{demande.ancien_statut} → {demande.nouveau_statut}"
        )

        lien_budget = None
        lien_courses = None
        erreurs = []

        def _update_objet(session: Session) -> None:
            # 1. Mettre à jour le statut de l'objet
            objet = session.query(ObjetMaison).filter(ObjetMaison.id == demande.objet_id).first()
            if objet:
                ancien_statut = objet.statut
                objet.statut = demande.nouveau_statut.value
                if demande.priorite:
                    objet.priorite_remplacement = demande.priorite.value
                if demande.cout_estime:
                    objet.prix_remplacement_estime = demande.cout_estime

                # Logger le changement
                log = LogStatutObjet(
                    objet_id=demande.objet_id,
                    ancien_statut=ancien_statut,
                    nouveau_statut=demande.nouveau_statut.value,
                    raison=demande.raison,
                    prix_estime=demande.cout_estime,
                    priorite=demande.priorite.value if demande.priorite else None,
                    ajoute_courses=demande.ajouter_liste_courses,
                    ajoute_budget=demande.ajouter_budget,
                )
                session.add(log)
                session.commit()
            else:
                raise ValueError(f"Objet {demande.objet_id} non trouvé")

        try:
            if db is None:
                with obtenir_contexte_db() as session:
                    _update_objet(session)
            else:
                _update_objet(db)

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
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison, PieceMaison

        def _impl(session: Session) -> list[ObjetAvecStatut]:
            objets = (
                session.query(ObjetMaison, PieceMaison.nom.label("piece_nom"))
                .join(PieceMaison, ObjetMaison.piece_id == PieceMaison.id)
                .filter(
                    ObjetMaison.statut.in_(
                        [
                            StatutObjet.A_CHANGER.value,
                            StatutObjet.A_ACHETER.value,
                            StatutObjet.A_REPARER.value,
                        ]
                    )
                )
                .all()
            )

            return [
                ObjetAvecStatut(
                    id=obj.ObjetMaison.id,
                    nom=obj.ObjetMaison.nom,
                    piece_id=obj.ObjetMaison.piece_id,
                    piece_nom=obj.piece_nom,
                    categorie=obj.ObjetMaison.categorie,
                    statut=StatutObjet(obj.ObjetMaison.statut),
                    priorite=(
                        PrioriteRemplacement(obj.ObjetMaison.priorite_remplacement)
                        if obj.ObjetMaison.priorite_remplacement
                        else PrioriteRemplacement.NORMALE
                    ),
                    cout_estime=obj.ObjetMaison.prix_remplacement_estime,
                )
                for obj in objets
            ]

        if db is None:
            with obtenir_contexte_db() as session:
                return _impl(session)
        return _impl(db)

    # ─────────────────────────────────────────────────────────
    # LIENS INTER-MODULES (Courses / Budget)
    # ─────────────────────────────────────────────────────────

    async def _creer_article_courses_objet(
        self,
        objet_id: int,
        cout_estime: Decimal | None,
    ) -> LienObjetCourses:
        """Crée un article de courses pour un objet à acheter.

        Args:
            objet_id: ID de l'objet à ajouter aux courses
            cout_estime: Coût estimé de l'achat

        Returns:
            LienObjetCourses avec l'ID de l'article créé
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import ArticleCourses, Ingredient
        from src.core.models.temps_entretien import ObjetMaison

        logger.info(f"Création article courses pour objet {objet_id}")

        with obtenir_contexte_db() as session:
            # Récupérer l'objet pour avoir son nom
            objet = session.query(ObjetMaison).filter(ObjetMaison.id == objet_id).first()
            if not objet:
                logger.warning(f"Objet {objet_id} non trouvé pour création article courses")
                return LienObjetCourses(
                    objet_id=objet_id,
                    objet_nom="Objet inconnu",
                    article_courses_id=None,
                    prix_estime=cout_estime,
                )

            # Créer ou trouver un ingrédient "placeholder" pour objets maison
            ingredient = (
                session.query(Ingredient).filter(Ingredient.nom.ilike(f"%{objet.nom}%")).first()
            )
            if not ingredient:
                ingredient = Ingredient(
                    nom=objet.nom,
                    categorie="maison",
                    unite="pcs",
                )
                session.add(ingredient)
                session.flush()

            # Vérifier si article existe déjà
            existant = (
                session.query(ArticleCourses)
                .filter(
                    ArticleCourses.ingredient_id == ingredient.id,
                    ArticleCourses.achete == False,
                )
                .first()
            )

            if existant:
                article_id = existant.id
                logger.info(f"Article courses existant trouvé: {article_id}")
            else:
                # Créer nouvel article courses
                article = ArticleCourses(
                    ingredient_id=ingredient.id,
                    quantite_necessaire=1,
                    notes=f"Objet maison - {objet.categorie or 'divers'}",
                    priorite="haute" if cout_estime and cout_estime > 100 else "normale",
                )
                session.add(article)
                session.commit()
                session.refresh(article)
                article_id = article.id
                logger.info(f"Article courses créé: {article_id}")

            return LienObjetCourses(
                objet_id=objet_id,
                objet_nom=objet.nom,
                article_courses_id=article_id,
                prix_estime=cout_estime,
            )

    async def _creer_depense_budget_objet(
        self,
        objet_id: int,
        montant: Decimal,
        date_prevue: date | None = None,
    ) -> LienObjetBudget:
        """Crée une dépense budget prévue pour un objet.

        Args:
            objet_id: ID de l'objet pour lequel créer une dépense
            montant: Montant prévu de la dépense
            date_prevue: Date prévue de l'achat (optionnel)

        Returns:
            LienObjetBudget avec l'ID de la dépense créée
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models.temps_entretien import ObjetMaison
        from src.services.famille.budget import get_budget_service
        from src.services.famille.budget.schemas import (
            CategorieDepense,
            Depense,
        )

        logger.info(f"Création dépense budget pour objet {objet_id}: {montant}€")

        with obtenir_contexte_db() as session:
            # Récupérer l'objet pour avoir son nom
            objet = session.query(ObjetMaison).filter(ObjetMaison.id == objet_id).first()
            objet_nom = objet.nom if objet else "Objet inconnu"

        # Créer la dépense via le service Budget
        budget_service = get_budget_service()

        depense = Depense(
            date=date_prevue or date.today(),
            montant=float(montant),
            categorie=CategorieDepense.MAISON,
            description=f"Achat prévu: {objet_nom}",
            magasin="",
            est_recurrente=False,
        )

        try:
            depense_creee = budget_service.ajouter_depense(depense)
            depense_id = depense_creee.id if depense_creee else None
            logger.info(f"Dépense budget créée: {depense_id}")
        except Exception as e:
            logger.error(f"Erreur création dépense budget: {e}")
            depense_id = None

        return LienObjetBudget(
            objet_id=objet_id,
            objet_nom=objet_nom,
            depense_budget_id=depense_id,
            montant_prevu=montant,
            date_prevue=date_prevue,
        )
