"""
Tests unitaires pour habitat.py

Module: src.core.models.habitat
Contient: Meuble, StockMaison, TacheEntretien, ActionEcologique
"""

from decimal import Decimal

from src.core.models.habitat import (
    ActionEcologique,
    Meuble,
    PrioriteMeuble,
    StatutMeuble,
    StockMaison,
    TacheEntretien,
    TypeActionEcologique,
    TypePiece,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestFurnitureStatus:
    """Tests pour l'énumération StatutMeuble."""

    def test_valeurs_disponibles(self):
        """Vérifie les statuts disponibles."""
        assert StatutMeuble.SOUHAITE.value == "souhaite"
        assert StatutMeuble.RECHERCHE.value == "recherche"
        assert StatutMeuble.TROUVE.value == "trouve"
        assert StatutMeuble.COMMANDE.value == "commande"
        assert StatutMeuble.ACHETE.value == "achete"
        assert StatutMeuble.ANNULE.value == "annule"


class TestFurniturePriority:
    """Tests pour l'énumération PrioriteMeuble."""

    def test_valeurs_disponibles(self):
        """Vérifie les priorités disponibles."""
        assert PrioriteMeuble.URGENT.value == "urgent"
        assert PrioriteMeuble.HAUTE.value == "haute"
        assert PrioriteMeuble.NORMALE.value == "normale"
        assert PrioriteMeuble.BASSE.value == "basse"
        assert PrioriteMeuble.PLUS_TARD.value == "plus_tard"


class TestEcoActionType:
    """Tests pour l'énumération TypeActionEcologique."""

    def test_valeurs_disponibles(self):
        """Vérifie les types d'actions écologiques."""
        assert TypeActionEcologique.LAVABLE.value == "lavable"
        assert TypeActionEcologique.ENERGIE.value == "energie"
        assert TypeActionEcologique.EAU.value == "eau"
        assert TypeActionEcologique.DECHETS.value == "dechets"
        assert TypeActionEcologique.ALIMENTATION.value == "alimentation"


class TestRoomType:
    """Tests pour l'énumération TypePiece."""

    def test_pieces_principales(self):
        """Vérifie les pièces principales."""
        assert TypePiece.SALON.value == "salon"
        assert TypePiece.CUISINE.value == "cuisine"
        assert TypePiece.CHAMBRE_PARENTALE.value == "chambre_parentale"
        assert TypePiece.CHAMBRE_JULES.value == "chambre_jules"
        assert TypePiece.GARAGE.value == "garage"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestFurniture:
    """Tests pour le modèle Meuble."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert Meuble.__tablename__ == "meubles"

    def test_creation_instance(self):
        """Test de création d'un meuble."""
        meuble = Meuble(
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
        colonnes = Meuble.__table__.columns
        assert colonnes["statut"].default is not None
        assert colonnes["priorite"].default is not None

    def test_dimensions(self):
        """Test des dimensions optionnelles."""
        meuble = Meuble(
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
        meuble = Meuble(
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
        meuble = Meuble(id=1, nom="Chaise", piece="cuisine")
        result = repr(meuble)
        assert "Meuble" in result
        assert "Chaise" in result
        assert "cuisine" in result


class TestHouseStock:
    """Tests pour le modèle StockMaison."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert StockMaison.__tablename__ == "stocks_maison"

    def test_creation_instance(self):
        """Test de création d'un stock."""
        stock = StockMaison(
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
        colonnes = StockMaison.__table__.columns
        assert colonnes["quantite"].default is not None
        assert colonnes["unite"].default is not None
        assert colonnes["seuil_alerte"].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        stock = StockMaison(id=1, nom="Piles AA", quantite=10)
        result = repr(stock)
        assert "StockMaison" in result
        assert "Piles AA" in result
        assert "10" in result


class TestMaintenanceTask:
    """Tests pour le modèle TacheEntretien."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert TacheEntretien.__tablename__ == "taches_entretien"

    def test_creation_instance(self):
        """Test de création d'une tâche."""
        tache = TacheEntretien(
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
        colonnes = TacheEntretien.__table__.columns
        assert colonnes["duree_minutes"].default is not None
        assert colonnes["priorite"].default is not None
        assert colonnes["fait"].default is not None

    def test_tache_ponctuelle(self):
        """Test d'une tâche ponctuelle (sans fréquence)."""
        tache = TacheEntretien(
            nom="Tri garage",
            categorie="rangement",
            frequence_jours=None,
        )
        assert tache.frequence_jours is None

    def test_repr(self):
        """Test de la représentation string."""
        tache = TacheEntretien(id=1, nom="Tri médicaments", fait=False)
        result = repr(tache)
        assert "TacheEntretien" in result
        assert "Tri médicaments" in result


class TestEcoAction:
    """Tests pour le modèle ActionEcologique."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert ActionEcologique.__tablename__ == "actions_ecologiques"

    def test_creation_instance(self):
        """Test de création d'une action éco."""
        action = ActionEcologique(
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
        colonnes = ActionEcologique.__table__.columns
        assert colonnes["actif"].default is not None

    def test_cout_nouveau_initial(self):
        """Test du champ cout_nouveau_initial."""
        action = ActionEcologique(
            nom="Test",
            type_action="energie",
            cout_nouveau_initial=Decimal("50.00"),
        )
        assert action.cout_nouveau_initial == Decimal("50.00")

        action.cout_nouveau_initial = Decimal("75.00")
        assert action.cout_nouveau_initial == Decimal("75.00")

    def test_repr(self):
        """Test de la représentation string."""
        action = ActionEcologique(id=1, nom="LED", type_action="energie")
        result = repr(action)
        assert "ActionEcologique" in result
        assert "LED" in result
        assert "energie" in result
