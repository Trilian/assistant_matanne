"""
Service Achats Famille - Logique métier pour les achats familiaux.

Opérations:
- CRUD achats (lister, ajouter, marquer achété, supprimer)
- Filtrage par catégorie et groupe
- Statistiques et achats urgents
"""

import logging
from datetime import date as date_type
from typing import TypedDict

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import FamilyPurchase
from src.services.core.events.bus import obtenir_bus

logger = logging.getLogger(__name__)


class AchatsStatsDict(TypedDict):
    """Structure de données pour les statistiques d'achats."""

    en_attente: int
    achetes: int
    total_estime: float
    total_depense: float
    urgents: int


class ServiceAchatsFamille:
    """Service de gestion des achats familiaux.

    Sépare la logique métier (CRUD, stats) de la couche UI.
    Les constantes CATEGORIES et PRIORITES restent dans le module UI.
    """

    # ═══════════════════════════════════════════════════════════
    # LECTURE
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def lister_achats(
        self, achete: bool = False, db: Session | None = None
    ) -> list[FamilyPurchase]:
        """Liste tous les achats.

        Args:
            achete: True pour les achats effectués, False pour les en attente.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des achats correspondants.
        """
        assert db is not None
        return db.query(FamilyPurchase).filter(FamilyPurchase.achete == achete).all()

    @avec_session_db
    def lister_par_categorie(
        self, categorie: str, achete: bool = False, db: Session | None = None
    ) -> list[FamilyPurchase]:
        """Liste les achats par catégorie.

        Args:
            categorie: Clé de catégorie (ex: 'jules_vetements', 'nous_jeux').
            achete: True pour les achats effectués, False pour les en attente.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des achats de la catégorie, triés par priorité.
        """
        assert db is not None
        return (
            db.query(FamilyPurchase)
            .filter(
                FamilyPurchase.categorie == categorie,
                FamilyPurchase.achete == achete,
            )
            .order_by(FamilyPurchase.priorite)
            .all()
        )

    @avec_session_db
    def lister_par_groupe(
        self, categories: list[str], achete: bool = False, db: Session | None = None
    ) -> list[FamilyPurchase]:
        """Liste les achats par groupe (plusieurs catégories).

        Le mapping groupe → catégories se fait dans le module UI via CATEGORIES.
        Exemple: groupe 'jules' → ['jules_vetements', 'jules_jouets', 'jules_equipement']

        Args:
            categories: Liste des clés de catégories appartenant au groupe.
            achete: True pour les achats effectués, False pour les en attente.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des achats du groupe, triés par priorité.
        """
        assert db is not None
        return (
            db.query(FamilyPurchase)
            .filter(
                FamilyPurchase.categorie.in_(categories),
                FamilyPurchase.achete == achete,
            )
            .order_by(FamilyPurchase.priorite)
            .all()
        )

    @avec_session_db
    def get_stats(self, db: Session | None = None) -> AchatsStatsDict:
        """Calcule les statistiques des achats.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            AchatsStatsDict avec:
            - en_attente: Nombre d'achats en attente
            - achetes: Nombre d'achats effectués
            - total_estime: Somme des prix estimés (en attente)
            - total_depense: Somme des prix réels (achetés)
            - urgents: Nombre d'achats urgents ou haute priorité
        """
        assert db is not None
        en_attente = db.query(FamilyPurchase).filter(FamilyPurchase.achete == False).all()  # noqa: E712
        achetes = db.query(FamilyPurchase).filter(FamilyPurchase.achete == True).all()  # noqa: E712

        total_estime = sum(p.prix_estime or 0 for p in en_attente)
        total_depense = sum(p.prix_reel or p.prix_estime or 0 for p in achetes)
        urgents = len([p for p in en_attente if p.priorite in ("urgent", "haute")])

        return {
            "en_attente": len(en_attente),
            "achetes": len(achetes),
            "total_estime": total_estime,
            "total_depense": total_depense,
            "urgents": urgents,
        }

    @avec_session_db
    def get_urgents(self, limit: int = 5, db: Session | None = None) -> list[FamilyPurchase]:
        """Récupère les achats urgents pour le tableau de bord.

        Args:
            limit: Nombre maximum d'achats à retourner.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des achats urgents/haute priorité, triés par priorité.
        """
        assert db is not None
        return (
            db.query(FamilyPurchase)
            .filter(
                FamilyPurchase.achete == False,  # noqa: E712
                FamilyPurchase.priorite.in_(("urgent", "haute")),
            )
            .order_by(FamilyPurchase.priorite)
            .limit(limit)
            .all()
        )

    # ═══════════════════════════════════════════════════════════
    # ÉCRITURE
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def ajouter_achat(
        self,
        nom: str,
        categorie: str,
        priorite: str = "moyenne",
        prix_estime: float | None = None,
        taille: str | None = None,
        magasin: str | None = None,
        url: str | None = None,
        description: str | None = None,
        age_recommande_mois: int | None = None,
        suggere_par: str | None = None,
        db: Session | None = None,
    ) -> FamilyPurchase:
        """Ajoute un nouvel achat à la liste.

        Args:
            nom: Nom de l'article.
            categorie: Catégorie (ex: 'jules_vetements', 'nous_jeux').
            priorite: Niveau de priorité ('urgent', 'haute', 'moyenne', 'basse', 'optionnel').
            prix_estime: Prix estimé en euros.
            taille: Taille (pour vêtements).
            magasin: Magasin suggéré.
            url: Lien vers l'article.
            description: Description détaillée.
            age_recommande_mois: Âge recommandé en mois (pour jouets).
            suggere_par: Qui a suggéré ('anne', 'mathieu', 'ia').
            db: Session DB (injectée automatiquement).

        Returns:
            L'achat créé.
        """
        assert db is not None
        achat = FamilyPurchase(
            nom=nom,
            categorie=categorie,
            priorite=priorite,
            prix_estime=prix_estime,
            taille=taille,
            magasin=magasin,
            url=url,
            description=description,
            age_recommande_mois=age_recommande_mois,
            suggere_par=suggere_par,
            achete=False,
        )
        db.add(achat)
        db.commit()
        logger.info("Achat créé: %s (id=%d, catégorie=%s)", nom, achat.id, categorie)

        # Emit event after successful commit
        obtenir_bus().emettre(
            "achats.cree",
            {"id": achat.id, "nom": nom, "categorie": categorie, "priorite": priorite},
            source="ServiceAchatsFamille",
        )

        return achat

    @avec_session_db
    def marquer_achete(
        self,
        purchase_id: int,
        prix_reel: float | None = None,
        db: Session | None = None,
    ) -> bool:
        """Marque un achat comme effectué.

        Args:
            purchase_id: ID de l'achat.
            prix_reel: Prix réel payé (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            True si l'achat a été trouvé et mis à jour, False sinon.
        """
        assert db is not None
        achat = db.get(FamilyPurchase, purchase_id)
        if achat:
            achat.achete = True
            achat.date_achat = date_type.today()
            if prix_reel is not None:
                achat.prix_reel = prix_reel
            db.commit()
            logger.info(
                "Achat marqué comme acheté: id=%d, nom=%s, prix_reel=%s",
                purchase_id,
                achat.nom,
                prix_reel,
            )

            # Emit event after successful commit
            obtenir_bus().emettre(
                "achats.achete",
                {"id": purchase_id, "nom": achat.nom, "prix_reel": prix_reel},
                source="ServiceAchatsFamille",
            )

            return True
        logger.warning("Achat non trouvé pour marquer comme acheté: id=%d", purchase_id)
        return False

    @avec_session_db
    def supprimer_achat(self, purchase_id: int, db: Session | None = None) -> bool:
        """Supprime un achat.

        Args:
            purchase_id: ID de l'achat.
            db: Session DB (injectée automatiquement).

        Returns:
            True si supprimé, False si non trouvé.
        """
        assert db is not None
        achat = db.get(FamilyPurchase, purchase_id)
        if achat:
            nom = achat.nom
            db.delete(achat)
            db.commit()
            logger.info("Achat supprimé: id=%d, nom=%s", purchase_id, nom)

            # Emit event after successful commit
            obtenir_bus().emettre(
                "achats.supprime",
                {"id": purchase_id, "nom": nom},
                source="ServiceAchatsFamille",
            )

            return True
        logger.warning("Achat non trouvé pour suppression: id=%d", purchase_id)
        return False


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_instance: ServiceAchatsFamille | None = None


def obtenir_service_achats_famille() -> ServiceAchatsFamille:
    """Factory pour le service achats famille (singleton)."""
    global _instance
    if _instance is None:
        _instance = ServiceAchatsFamille()
    return _instance


# Alias anglais
get_achats_famille_service = obtenir_service_achats_famille
