"""
Tests unitaires pour habitat.py

Module: src.core.models.habitat
Contient: Furniture, HouseStock, MaintenanceTask, EcoAction
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from src.core.models.habitat import (
    Furniture,
    HouseStock,
    MaintenanceTask,
    EcoAction,
    FurnitureStatus,
    FurniturePriority,
    EcoActionType,
    RoomType,
)


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestFurnitureStatus:
    """Tests pour l'énumération FurnitureStatus."""

    def test_valeurs_disponibles(self):
        """Vérifie les statuts disponibles."""
        assert FurnitureStatus.SOUHAITE.value == "souhaite"
        assert FurnitureStatus.RECHERCHE.value == "recherche"
        assert FurnitureStatus.TROUVE.value == "trouve"
        assert FurnitureStatus.COMMANDE.value == "commande"
        assert FurnitureStatus.ACHETE.value == "achete"
        assert FurnitureStatus.ANNULE.value == "annule"


class TestFurniturePriority:
    """Tests pour l'énumération FurniturePriority."""

    def test_valeurs_disponibles(self):
        """Vérifie les priorités disponibles."""
        assert FurniturePriority.URGENT.value == "urgent"
        assert FurniturePriority.HAUTE.value == "haute"
        assert FurniturePriority.NORMALE.value == "normale"
        assert FurniturePriority.BASSE.value == "basse"
        assert FurniturePriority.PLUS_TARD.value == "plus_tard"


class TestEcoActionType:
    """Tests pour l'énumération EcoActionType."""

    def test_valeurs_disponibles(self):
        """Vérifie les types d'actions écologiques."""
        assert EcoActionType.LAVABLE.value == "lavable"
        assert EcoActionType.ENERGIE.value == "energie"
        assert EcoActionType.EAU.value == "eau"
        assert EcoActionType.DECHETS.value == "dechets"
        assert EcoActionType.ALIMENTATION.value == "alimentation"


class TestRoomType:
    """Tests pour l'énumération RoomType."""

    def test_pieces_principales(self):
        """Vérifie les pièces principales."""
        assert RoomType.SALON.value == "salon"
        assert RoomType.CUISINE.value == "cuisine"
        assert RoomType.CHAMBRE_PARENTALE.value == "chambre_parentale"
        assert RoomType.CHAMBRE_JULES.value == "chambre_jules"
        assert RoomType.GARAGE.value == "garage"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestFurniture:
    """Tests pour le modèle Furniture."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert Furniture.__tablename__ == "furniture"

    def test_creation_instance(self):
        """Test de création d'un meuble."""
        meuble = Furniture(
            nom="Canapé d'angle",
            piece="salon",
            prix_estime=Decimal("1200.00"),
            statut="recherche",
            priorite="haute",
        )
        assert meuble.nom == "Canapé d'angle"
        assert meuble.piece == "salon"
        assert meuble.prix_estime == Decimal("1200.00")
        assert meuble.statut == "recherche"
        assert meuble.priorite == "haute"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = Furniture.__table__.columns
        assert colonnes['statut'].default is not None
        assert colonnes['priorite'].default is not None

    def test_dimensions(self):
        """Test des dimensions optionnelles."""
        meuble = Furniture(
            nom="Armoire",
            piece="chambre_parentale",
            largeur_cm=120,
            hauteur_cm=200,
            profondeur_cm=60,
        )
        assert meuble.largeur_cm == 120
        assert meuble.hauteur_cm == 200
        assert meuble.profondeur_cm == 60

    def test_infos_achat(self):
        """Test des informations d'achat."""
        meuble = Furniture(
            nom="Billy",
            piece="bureau",
            magasin="IKEA",
            url="https://ikea.com/billy",
            reference="S49017020",
        )
        assert meuble.magasin == "IKEA"
        assert "ikea.com" in meuble.url
        assert meuble.reference == "S49017020"

    def test_repr(self):
        """Test de la représentation string."""
        meuble = Furniture(id=1, nom="Chaise", piece="cuisine")
        result = repr(meuble)
        assert "Furniture" in result
        assert "Chaise" in result
        assert "cuisine" in result


class TestHouseStock:
    """Tests pour le modèle HouseStock."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert HouseStock.__tablename__ == "house_stocks"

    def test_creation_instance(self):
        """Test de création d'un stock."""
        stock = HouseStock(
            nom="Ampoules LED E27",
            categorie="electricite",
            quantite=5,
            seuil_alerte=2,
            emplacement="Garage étagère 2",
        )
        assert stock.nom == "Ampoules LED E27"
        assert stock.categorie == "electricite"
        assert stock.quantite == 5
        assert stock.seuil_alerte == 2
        assert stock.emplacement == "Garage étagère 2"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = HouseStock.__table__.columns
        assert colonnes['quantite'].default is not None
        assert colonnes['unite'].default is not None
        assert colonnes['seuil_alerte'].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        stock = HouseStock(id=1, nom="Piles AA", quantite=10)
        result = repr(stock)
        assert "HouseStock" in result
        assert "Piles AA" in result
        assert "10" in result


class TestMaintenanceTask:
    """Tests pour le modèle MaintenanceTask."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert MaintenanceTask.__tablename__ == "maintenance_tasks"

    def test_creation_instance(self):
        """Test de création d'une tâche."""
        tache = MaintenanceTask(
            nom="Nettoyer les vitres",
            categorie="menage",
            piece="salon",
            frequence_jours=30,
            duree_minutes=45,
            responsable="mathieu",
        )
        assert tache.nom == "Nettoyer les vitres"
        assert tache.categorie == "menage"
        assert tache.frequence_jours == 30
        assert tache.duree_minutes == 45
        assert tache.responsable == "mathieu"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = MaintenanceTask.__table__.columns
        assert colonnes['duree_minutes'].default is not None
        assert colonnes['priorite'].default is not None
        assert colonnes['fait'].default is not None

    def test_tache_ponctuelle(self):
        """Test d'une tâche ponctuelle (sans fréquence)."""
        tache = MaintenanceTask(
            nom="Tri garage",
            categorie="rangement",
            frequence_jours=None,
        )
        assert tache.frequence_jours is None

    def test_repr(self):
        """Test de la représentation string."""
        tache = MaintenanceTask(id=1, nom="Tri médicaments", fait=False)
        result = repr(tache)
        assert "MaintenanceTask" in result
        assert "Tri médicaments" in result


class TestEcoAction:
    """Tests pour le modèle EcoAction."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert EcoAction.__tablename__ == "eco_actions"

    def test_creation_instance(self):
        """Test de création d'une action éco."""
        action = EcoAction(
            nom="Essuie-tout lavable",
            type_action="lavable",
            ancien_produit="Sopalin jetable",
            nouveau_produit="Essuie-tout bambou",
            cout_ancien_mensuel=Decimal("8.00"),
            cout_nouveau_initial=Decimal("25.00"),
            economie_mensuelle=Decimal("7.00"),
        )
        assert action.nom == "Essuie-tout lavable"
        assert action.type_action == "lavable"
        assert action.ancien_produit == "Sopalin jetable"
        assert action.economie_mensuelle == Decimal("7.00")

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = EcoAction.__table__.columns
        assert colonnes['actif'].default is not None

    def test_cout_initial_alias(self):
        """Test de l'alias cout_initial."""
        action = EcoAction(
            nom="Test",
            type_action="energie",
            cout_nouveau_initial=Decimal("50.00"),
        )
        # Property alias
        assert action.cout_initial == Decimal("50.00")
        
        # Setter alias
        action.cout_initial = Decimal("75.00")
        assert action.cout_nouveau_initial == Decimal("75.00")

    def test_repr(self):
        """Test de la représentation string."""
        action = EcoAction(id=1, nom="LED", type_action="energie")
        result = repr(action)
        assert "EcoAction" in result
        assert "LED" in result
        assert "energie" in result

