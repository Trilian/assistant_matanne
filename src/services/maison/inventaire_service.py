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
"""

import logging
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.core.ai import ClientIA
from src.core.database import obtenir_contexte_db
from src.services.base import BaseAIService

from .schemas import (
    ActionObjetResult,
    CategorieObjet,
    CoutTravauxPiece,
    DemandeChangementObjet,
    LienObjetBudget,
    LienObjetCourses,
    ModificationPieceCreate,
    ObjetAvecStatut,
    ObjetCreate,
    PieceCreate,
    PieceVersion,
    PlanReorganisationPiece,
    PrioriteRemplacement,
    ResultatRecherche,
    ResumeTravauxMaison,
    StatutObjet,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE INVENTAIRE MAISON
# ═══════════════════════════════════════════════════════════


class InventaireMaisonService(BaseAIService):
    """Service pour la gestion de l'inventaire maison.

    Fonctionnalités:
    - CRUD pièces, conteneurs, objets
    - Recherche sémantique "Où est..."
    - Calcul valeur assurance
    - Suggestions rangement IA

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
    # RECHERCHE "OÙ EST..."
    # ─────────────────────────────────────────────────────────

    async def rechercher(self, query: str, db: Session | None = None) -> ResultatRecherche | None:
        """Recherche un objet dans l'inventaire.

        Recherche intelligente combinant:
        - Correspondance exacte
        - Recherche floue (fautes, synonymes)
        - Suggestion IA si non trouvé

        Args:
            query: Recherche utilisateur (ex: "perceuse", "où est le tournevis")
            db: Session DB optionnelle

        Returns:
            ResultatRecherche ou None si non trouvé
        """
        # Nettoyer la query
        query_clean = self._nettoyer_query(query)

        if db is None:
            with obtenir_contexte_db() as session:
                return await self._rechercher_impl(session, query_clean)
        return await self._rechercher_impl(db, query_clean)

    async def _rechercher_impl(self, db: Session, query: str) -> ResultatRecherche | None:
        """Implémentation de la recherche."""
        # 1. Recherche exacte en DB
        # Note: Utilise les modèles Piece, Conteneur, ObjetMaison quand ils seront créés
        # Pour l'instant, simulation avec HouseStock
        from src.core.models import HouseStock

        # Recherche dans HouseStock (proxy pour ObjetMaison)
        objets = (
            db.query(HouseStock)
            .filter(
                or_(
                    HouseStock.nom.ilike(f"%{query}%"),
                    HouseStock.categorie.ilike(f"%{query}%"),
                )
            )
            .all()
        )

        if objets:
            obj = objets[0]
            return ResultatRecherche(
                objet_trouve=obj.nom,
                emplacement=obj.emplacement or "Non spécifié",
                piece=self._extraire_piece(obj.emplacement),
                conteneur=self._extraire_conteneur(obj.emplacement),
                quantite=obj.quantite,
                confiance=1.0,
                suggestions_similaires=[o.nom for o in objets[1:4]],
            )

        # 2. Si non trouvé, demander suggestion IA
        return await self._suggestion_ia(query)

    async def _suggestion_ia(self, query: str) -> ResultatRecherche | None:
        """Demande une suggestion à l'IA si objet non trouvé."""
        prompt = f"""L'utilisateur cherche "{query}" dans sa maison.
Suggère où ce type d'objet est généralement rangé.
Format JSON: {{"emplacement_suggere": "Garage, établi", "confiance": 0.6}}"""

        try:
            response = await self.call_with_cache(
                prompt=prompt,
                system_prompt="Tu es expert en organisation domestique",
                max_tokens=200,
            )
            import json

            data = json.loads(response)
            return ResultatRecherche(
                objet_trouve=query,
                emplacement=data.get("emplacement_suggere", "Inconnu"),
                piece="Suggestion IA",
                confiance=data.get("confiance", 0.5),
                suggestions_similaires=[],
            )
        except Exception as e:
            logger.warning(f"Suggestion IA échouée: {e}")
            return None

    def _nettoyer_query(self, query: str) -> str:
        """Nettoie la requête de recherche."""
        # Retirer "où est", "cherche", etc.
        mots_ignorés = ["où", "est", "sont", "les", "la", "le", "mon", "ma", "mes", "cherche"]
        mots = query.lower().split()
        mots_filtres = [m for m in mots if m not in mots_ignorés]
        return " ".join(mots_filtres) if mots_filtres else query

    def _extraire_piece(self, emplacement: str | None) -> str:
        """Extrait le nom de la pièce d'un emplacement."""
        if not emplacement:
            return "Non spécifié"
        # Format attendu: "Pièce, détail"
        return emplacement.split(",")[0].strip()

    def _extraire_conteneur(self, emplacement: str | None) -> str | None:
        """Extrait le conteneur d'un emplacement."""
        if not emplacement or "," not in emplacement:
            return None
        return emplacement.split(",", 1)[1].strip()

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
        # TODO: Implémenter avec modèle Piece
        logger.info(f"Création pièce: {piece.nom}")
        return 1  # Placeholder

    def lister_pieces(self, db: Session | None = None) -> list[dict]:
        """Liste toutes les pièces avec stats.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des pièces avec nombre d'objets
        """
        # TODO: Implémenter avec modèle Piece
        return []

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
        # TODO: Implémenter avec modèle ObjetMaison
        logger.info(f"Ajout objet: {objet.nom}")
        return 1  # Placeholder

    def deplacer_objet(
        self,
        objet_id: int,
        nouveau_conteneur_id: int,
        db: Session | None = None,
    ) -> bool:
        """Déplace un objet vers un autre conteneur.

        Args:
            objet_id: ID de l'objet
            nouveau_conteneur_id: ID du nouveau conteneur
            db: Session DB optionnelle

        Returns:
            True si déplacé avec succès
        """
        # TODO: Implémenter
        return True

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
        # TODO: Implémenter avec modèle ObjetMaison
        return Decimal("0")

    def calculer_valeur_totale(self, db: Session | None = None) -> dict[str, Decimal]:
        """Calcule la valeur totale par pièce et globale.

        Args:
            db: Session DB optionnelle

        Returns:
            Dict avec valeur par pièce et total
        """
        # TODO: Implémenter
        return {"total": Decimal("0")}

    def generer_inventaire_assurance(self, db: Session | None = None) -> list[dict]:
        """Génère un inventaire pour déclaration assurance.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des objets avec valeurs pour assurance
        """
        # TODO: Implémenter
        return []

    # ─────────────────────────────────────────────────────────
    # SUGGESTIONS RANGEMENT IA
    # ─────────────────────────────────────────────────────────

    async def suggerer_rangement(self, nom_objet: str, categorie: str | None = None) -> str:
        """Suggère où ranger un nouvel objet.

        Args:
            nom_objet: Nom de l'objet
            categorie: Catégorie optionnelle

        Returns:
            Suggestion de rangement
        """
        cat_txt = f" (catégorie: {categorie})" if categorie else ""

        prompt = f"""Où ranger "{nom_objet}"{cat_txt} dans une maison?
Donne l'emplacement idéal (pièce et type de rangement).
Sois pratique et logique."""

        return await self.call_with_cache(
            prompt=prompt,
            system_prompt="Tu es expert en organisation domestique Marie Kondo",
            max_tokens=200,
        )

    async def detecter_doublons(self, db: Session | None = None) -> list[dict]:
        """Détecte les objets en double dans l'inventaire.

        Args:
            db: Session DB optionnelle

        Returns:
            Liste des doublons potentiels
        """
        # TODO: Implémenter
        return []

    async def optimiser_rangement(self, piece_id: int, db: Session | None = None) -> list[str]:
        """Suggère des optimisations de rangement pour une pièce.

        Args:
            piece_id: ID de la pièce
            db: Session DB optionnelle

        Returns:
            Liste de suggestions d'optimisation
        """
        # TODO: Implémenter avec données réelles de la pièce
        return [
            "Regrouper les objets similaires",
            "Utiliser des boîtes étiquetées",
            "Désencombrer les objets inutilisés depuis 1 an",
        ]

    # ─────────────────────────────────────────────────────────
    # SCAN CODE-BARRES
    # ─────────────────────────────────────────────────────────

    def rechercher_par_code_barre(
        self, code_barre: str, db: Session | None = None
    ) -> ResultatRecherche | None:
        """Recherche un objet par son code-barres.

        Args:
            code_barre: Code-barres scanné
            db: Session DB optionnelle

        Returns:
            ResultatRecherche ou None
        """
        if db is None:
            with obtenir_contexte_db() as session:
                return self._recherche_code_barre_impl(session, code_barre)
        return self._recherche_code_barre_impl(db, code_barre)

    def _recherche_code_barre_impl(self, db: Session, code_barre: str) -> ResultatRecherche | None:
        """Implémentation recherche code-barres."""
        from src.core.models import HouseStock

        obj = (
            db.query(HouseStock)
            .filter(HouseStock.notes.contains(code_barre))  # Stocké dans notes pour l'instant
            .first()
        )

        if obj:
            return ResultatRecherche(
                objet_trouve=obj.nom,
                emplacement=obj.emplacement or "Non spécifié",
                piece=self._extraire_piece(obj.emplacement),
                quantite=obj.quantite,
                confiance=1.0,
            )

        return None

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
