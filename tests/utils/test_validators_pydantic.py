"""
Tests pour src/core/validators_pydantic.py - SchÃ©mas Pydantic de validation.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from src.core.validators_pydantic import (
    EtapeInput,
    IngredientInput,
    IngredientStockInput,
    RecetteInput,
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    EntreeJournalInput,
    ProjetInput,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INGREDIENT INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIngredientInput:
    """Tests pour IngredientInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale valide."""
        ing = IngredientInput(nom="Tomate")
        
        assert ing.nom == "Tomate"
        assert ing.quantite is None
        assert ing.unite is None

    def test_valid_complete(self):
        """Test crÃ©ation complÃ¨te."""
        ing = IngredientInput(nom="farine", quantite=500, unite="g")
        
        assert ing.nom == "Farine"  # Capitalized
        assert ing.quantite == 500
        assert ing.unite == "g"

    def test_nom_cleaned(self):
        """Test nettoyage du nom."""
        ing = IngredientInput(nom="  tomate  ")
        assert ing.nom == "Tomate"

    def test_nom_empty_rejected(self):
        """Test nom vide rejetÃ©."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="")

    def test_nom_too_long_rejected(self):
        """Test nom trop long rejetÃ©."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="x" * 201)

    def test_quantite_negative_rejected(self):
        """Test quantitÃ© nÃ©gative rejetÃ©e."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="Test", quantite=-1)

    def test_quantite_zero_rejected(self):
        """Test quantitÃ© zÃ©ro rejetÃ©e (ge=0.01)."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="Test", quantite=0)

    def test_quantite_too_large_rejected(self):
        """Test quantitÃ© trop grande rejetÃ©e."""
        with pytest.raises(ValidationError):
            IngredientInput(nom="Test", quantite=10001)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ETAPE INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestEtapeInput:
    """Tests pour EtapeInput."""

    def test_valid_with_numero(self):
        """Test crÃ©ation avec numero."""
        etape = EtapeInput(numero=1, description="PrÃ©chauffer le four")
        
        assert etape.numero == 1
        assert etape.description == "PrÃ©chauffer le four"

    def test_valid_with_ordre(self):
        """Test crÃ©ation avec ordre (alias)."""
        etape = EtapeInput(ordre=2, description="MÃ©langer les ingrÃ©dients")
        
        assert etape.numero == 2  # ordre copiÃ© vers numero
        assert etape.ordre == 2

    def test_description_cleaned(self):
        """Test nettoyage description."""
        etape = EtapeInput(numero=1, description="  Test  ")
        assert etape.description == "Test"

    def test_description_too_short_rejected(self):
        """Test description trop courte rejetÃ©e (min=5)."""
        with pytest.raises(ValidationError):
            EtapeInput(numero=1, description="Test")  # 4 chars

    def test_description_too_long_rejected(self):
        """Test description trop longue rejetÃ©e."""
        with pytest.raises(ValidationError):
            EtapeInput(numero=1, description="x" * 1001)

    def test_neither_numero_nor_ordre_rejected(self):
        """Test sans numero ni ordre rejetÃ©."""
        with pytest.raises(ValidationError):
            EtapeInput(description="Valid description here")

    def test_duree_valid(self):
        """Test durÃ©e valide."""
        etape = EtapeInput(numero=1, description="Cuire", duree=30)
        assert etape.duree == 30

    def test_duree_too_long_rejected(self):
        """Test durÃ©e trop longue rejetÃ©e (max 1440 = 24h)."""
        with pytest.raises(ValidationError):
            EtapeInput(numero=1, description="Test step", duree=1441)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS RECETTE INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRecetteInput:
    """Tests pour RecetteInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        recette = RecetteInput(
            nom="Tarte",
            temps_preparation=30,
            temps_cuisson=45,
            ingredients=[IngredientInput(nom="Pomme")],
            etapes=[EtapeInput(numero=1, description="Couper les pommes")],
        )
        
        assert recette.nom == "Tarte"
        assert recette.portions == 4  # Default

    def test_nom_cleaned(self):
        """Test nettoyage nom."""
        recette = RecetteInput(
            nom="  tarte aux pommes  ",
            temps_preparation=30,
            temps_cuisson=45,
            ingredients=[IngredientInput(nom="Pomme")],
            etapes=[EtapeInput(numero=1, description="Couper les pommes")],
        )
        
        assert recette.nom == "Tarte aux pommes"

    def test_nom_too_short_rejected(self):
        """Test nom trop court rejetÃ© (min 2 after clean)."""
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="T",
                temps_preparation=30,
                temps_cuisson=45,
                ingredients=[IngredientInput(nom="Pomme")],
                etapes=[EtapeInput(numero=1, description="Couper les pommes")],
            )

    def test_saison_valid(self):
        """Test saison valide."""
        recette = RecetteInput(
            nom="Soupe",
            temps_preparation=20,
            temps_cuisson=30,
            ingredients=[IngredientInput(nom="LÃ©gume")],
            etapes=[EtapeInput(numero=1, description="Cuire la soupe")],
            saison="hiver",
        )
        
        assert recette.saison == "hiver"

    def test_saison_uppercase_normalized(self):
        """Test saison normalisÃ©e en minuscules."""
        recette = RecetteInput(
            nom="Salade",
            temps_preparation=10,
            temps_cuisson=0,
            ingredients=[IngredientInput(nom="Salade")],
            etapes=[EtapeInput(numero=1, description="Laver la salade")],
            saison="Ã‰TÃ‰",
        )
        
        assert recette.saison == "Ã©tÃ©"

    def test_saison_invalid_rejected(self):
        """Test saison invalide rejetÃ©e."""
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="Test",
                temps_preparation=10,
                temps_cuisson=10,
                ingredients=[IngredientInput(nom="Test")],
                etapes=[EtapeInput(numero=1, description="Test step here")],
                saison="invalid_season",
            )

    def test_temps_total_exceeded_rejected(self):
        """Test temps total > 24h rejetÃ©."""
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="Test",
                temps_preparation=1000,
                temps_cuisson=500,  # Total 1500 > 1440
                ingredients=[IngredientInput(nom="Test")],
                etapes=[EtapeInput(numero=1, description="Test step here")],
            )

    def test_no_ingredients_rejected(self):
        """Test sans ingrÃ©dients rejetÃ©."""
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="Test",
                temps_preparation=10,
                temps_cuisson=10,
                ingredients=[],
                etapes=[EtapeInput(numero=1, description="Test step here")],
            )

    def test_no_etapes_rejected(self):
        """Test sans Ã©tapes rejetÃ©."""
        with pytest.raises(ValidationError):
            RecetteInput(
                nom="Test",
                temps_preparation=10,
                temps_cuisson=10,
                ingredients=[IngredientInput(nom="Test")],
                etapes=[],
            )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS INGREDIENT STOCK INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestIngredientStockInput:
    """Tests pour IngredientStockInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        stock = IngredientStockInput(nom="Farine", quantite=1, unite="kg")
        
        assert stock.nom == "Farine"
        assert stock.quantite == 1
        assert stock.unite == "kg"

    def test_valid_complete(self):
        """Test crÃ©ation complÃ¨te."""
        stock = IngredientStockInput(
            nom="lait",
            quantite=2,
            unite="L",
            date_expiration=date(2025, 2, 1),
            localisation="frigo",
            prix_unitaire=1.5,
        )
        
        assert stock.nom == "Lait"
        assert stock.localisation == "Frigo"
        assert stock.prix_unitaire == 1.5

    def test_quantite_too_small_rejected(self):
        """Test quantitÃ© trop petite rejetÃ©e (ge=0.01)."""
        with pytest.raises(ValidationError):
            IngredientStockInput(nom="Test", quantite=0, unite="kg")

    def test_prix_negatif_rejected(self):
        """Test prix nÃ©gatif rejetÃ©."""
        with pytest.raises(ValidationError):
            IngredientStockInput(nom="Test", quantite=1, unite="kg", prix_unitaire=-1)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS REPAS INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRepasInput:
    """Tests pour RepasInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        repas = RepasInput(date=date(2025, 1, 15), type_repas="dÃ©jeuner")
        
        assert repas.date_repas == date(2025, 1, 15)
        assert repas.type_repas == "dÃ©jeuner"

    def test_valid_with_recette(self):
        """Test avec recette."""
        repas = RepasInput(
            date=date(2025, 1, 15),
            type_repas="dÃ®ner",
            recette_id=42,
        )
        
        assert repas.recette_id == 42

    def test_type_normalized(self):
        """Test type normalisÃ© en minuscules."""
        repas = RepasInput(date=date(2025, 1, 15), type_repas="DÃ‰JEUNER")
        assert repas.type_repas == "dÃ©jeuner"

    def test_type_invalid_rejected(self):
        """Test type invalide rejetÃ©."""
        with pytest.raises(ValidationError):
            RepasInput(date=date(2025, 1, 15), type_repas="brunch")

    def test_all_valid_types(self):
        """Test tous les types valides."""
        valid_types = ["petit_dÃ©jeuner", "dÃ©jeuner", "dÃ®ner", "goÃ»ter"]
        
        for type_repas in valid_types:
            repas = RepasInput(date=date(2025, 1, 15), type_repas=type_repas)
            assert repas.type_repas == type_repas


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ROUTINE INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRoutineInput:
    """Tests pour RoutineInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        routine = RoutineInput(
            nom="Routine du soir",
            pour_qui="Jules",
            frequence="quotidien",
        )
        
        assert routine.nom == "Routine du soir"
        assert routine.pour_qui == "Jules"
        assert routine.frequence == "quotidien"
        assert routine.is_active is True  # Default

    def test_nom_cleaned(self):
        """Test nettoyage nom."""
        routine = RoutineInput(
            nom="  routine matin  ",
            pour_qui="Jules",
            frequence="quotidien",
        )
        
        assert routine.nom == "Routine matin"

    def test_frequence_normalized(self):
        """Test frÃ©quence normalisÃ©e."""
        routine = RoutineInput(
            nom="Test",
            pour_qui="Jules",
            frequence="QUOTIDIEN",
        )
        
        assert routine.frequence == "quotidien"

    def test_frequence_invalid_rejected(self):
        """Test frÃ©quence invalide rejetÃ©e."""
        with pytest.raises(ValidationError):
            RoutineInput(
                nom="Test",
                pour_qui="Jules",
                frequence="bi-mensuel",
            )

    def test_all_valid_frequences(self):
        """Test toutes les frÃ©quences valides."""
        valid_freqs = ["quotidien", "hebdomadaire", "mensuel"]
        
        for freq in valid_freqs:
            routine = RoutineInput(nom="Test", pour_qui="Jules", frequence=freq)
            assert routine.frequence == freq


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TACHE ROUTINE INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTacheRoutineInput:
    """Tests pour TacheRoutineInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        tache = TacheRoutineInput(nom="Se brosser les dents")
        
        assert tache.nom == "Se brosser les dents"
        assert tache.heure is None

    def test_valid_with_heure(self):
        """Test avec heure."""
        tache = TacheRoutineInput(nom="Petit dÃ©jeuner", heure="08:00")
        
        assert tache.heure == "08:00"

    def test_heure_invalid_format_rejected(self):
        """Test format heure invalide rejetÃ©."""
        with pytest.raises(ValidationError):
            TacheRoutineInput(nom="Test", heure="8:00")  # Doit Ãªtre 08:00

    def test_heure_invalid_format_letters(self):
        """Test heure avec lettres rejetÃ©e."""
        with pytest.raises(ValidationError):
            TacheRoutineInput(nom="Test", heure="abc")

    def test_heure_valid_edge_case(self):
        """Test heure 25:00 passe le pattern (regex ne valide pas la plage)."""
        # Note: Le pattern regex ^\d{2}:\d{2}$ ne valide pas la plage horaire
        # 25:00 est acceptÃ© par le pattern car c'est 2 digits:2 digits
        tache = TacheRoutineInput(nom="Test", heure="25:00")
        assert tache.heure == "25:00"

    def test_nom_cleaned(self):
        """Test nettoyage nom."""
        tache = TacheRoutineInput(nom="  test  ")
        assert tache.nom == "Test"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENTREE JOURNAL INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestEntreeJournalInput:
    """Tests pour EntreeJournalInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        entree = EntreeJournalInput(
            domaine="santÃ©",
            titre="Visite mÃ©decin",
            contenu="Tout va bien",
        )
        
        assert entree.domaine == "santÃ©"
        assert entree.titre == "Visite mÃ©decin"

    def test_domaine_normalized(self):
        """Test domaine normalisÃ©."""
        entree = EntreeJournalInput(
            domaine="SANTÃ‰",
            titre="Test",
            contenu="Test contenu",
        )
        
        assert entree.domaine == "santÃ©"

    def test_domaine_invalid_rejected(self):
        """Test domaine invalide rejetÃ©."""
        with pytest.raises(ValidationError):
            EntreeJournalInput(
                domaine="invalid",
                titre="Test",
                contenu="Test",
            )

    def test_all_valid_domaines(self):
        """Test tous les domaines valides."""
        valid_domaines = ["santÃ©", "humeur", "dÃ©veloppement", "comportement"]
        
        for domaine in valid_domaines:
            entree = EntreeJournalInput(
                domaine=domaine,
                titre="Test",
                contenu="Contenu test",
            )
            assert entree.domaine == domaine

    def test_titre_cleaned(self):
        """Test nettoyage titre."""
        entree = EntreeJournalInput(
            domaine="santÃ©",
            titre="  test  ",
            contenu="Contenu",
        )
        
        assert entree.titre == "Test"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PROJET INPUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestProjetInput:
    """Tests pour ProjetInput."""

    def test_valid_minimal(self):
        """Test crÃ©ation minimale."""
        projet = ProjetInput(
            nom="RÃ©novation cuisine",
            categorie="Maison",
        )
        
        assert projet.nom == "RÃ©novation cuisine"
        assert projet.priorite == "moyenne"  # Default

    def test_priorite_normalized(self):
        """Test prioritÃ© normalisÃ©e."""
        projet = ProjetInput(
            nom="Test",
            categorie="Test",
            priorite="HAUTE",
        )
        
        assert projet.priorite == "haute"

    def test_priorite_invalid_rejected(self):
        """Test prioritÃ© invalide rejetÃ©e."""
        with pytest.raises(ValidationError):
            ProjetInput(
                nom="Test",
                categorie="Test",
                priorite="urgente",
            )

    def test_all_valid_priorites(self):
        """Test toutes les prioritÃ©s valides."""
        for priorite in ["basse", "moyenne", "haute"]:
            projet = ProjetInput(nom="Test", categorie="Test", priorite=priorite)
            assert projet.priorite == priorite

    def test_dates_valid(self):
        """Test dates valides."""
        projet = ProjetInput(
            nom="Test",
            categorie="Test",
            date_debut=date(2025, 1, 1),
            date_fin=date(2025, 6, 1),
        )
        
        assert projet.date_debut == date(2025, 1, 1)
        assert projet.date_fin_estimee == date(2025, 6, 1)

    def test_date_fin_before_debut_rejected(self):
        """Test date fin avant dÃ©but rejetÃ©e."""
        with pytest.raises(ValidationError):
            ProjetInput(
                nom="Test",
                categorie="Test",
                date_debut=date(2025, 6, 1),
                date_fin=date(2025, 1, 1),
            )

    def test_nom_cleaned(self):
        """Test nettoyage nom."""
        projet = ProjetInput(
            nom="  test projet  ",
            categorie="Test",
        )
        
        assert projet.nom == "Test projet"

