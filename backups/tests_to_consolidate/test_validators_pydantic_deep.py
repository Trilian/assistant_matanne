# -*- coding: utf-8 -*-
"""
Tests supplÃ©mentaires pour validators_pydantic.py

Cible les lignes non couvertes: 136-138, 171, 175, 211-213, 241-251, 
275, 281-286, 301, 326-331, 336, 361, 367-372, 377-383
"""
import pytest
from datetime import date
from pydantic import ValidationError


class TestRecetteInputValidators:
    """Tests pour les validateurs de RecetteInput."""
    
    def test_recette_nom_trop_court(self):
        """Nom avec moins de 2 caractÃ¨res lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="A",  # Trop court
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="dÃ©jeuner"
            )
        assert "au moins 2 caractÃ¨res" in str(exc_info.value)
    
    def test_recette_difficulte_invalide(self):
        """DifficultÃ© invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="Tarte aux pommes",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="expert",  # Invalide
                type_repas="dÃ©jeuner"
            )
        assert "DifficultÃ© invalide" in str(exc_info.value)
    
    def test_recette_type_repas_invalide(self):
        """Type de repas invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="Tarte aux pommes",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="collation"  # Invalide
            )
        assert "Type de repas invalide" in str(exc_info.value)
    
    def test_recette_saison_invalide(self):
        """Saison invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="Tarte aux pommes",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="dÃ©jeuner",
                saison="pluvieuse"  # Invalide
            )
        assert "Saison invalide" in str(exc_info.value)
    
    def test_recette_saison_none(self):
        """Saison None est acceptÃ©e."""
        from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
        
        recette = RecetteInput(
            nom="Tarte aux pommes",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile",
            type_repas="dÃ©jeuner",
            ingredients=[IngredientInput(nom="Pommes", quantite=3, unite="piÃ¨ces")],
            etapes=[EtapeInput(numero=1, description="PrÃ©parer les pommes")],
            saison=None
        )
        assert recette.saison is None
    
    def test_recette_saison_valide(self):
        """Saison valide est normalisÃ©e."""
        from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
        
        recette = RecetteInput(
            nom="Tarte aux pommes",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile",
            type_repas="dÃ©jeuner",
            ingredients=[IngredientInput(nom="Pommes", quantite=3, unite="piÃ¨ces")],
            etapes=[EtapeInput(numero=1, description="PrÃ©parer les pommes")],
            saison="Ã‰TÃ‰"  # En majuscules
        )
        assert recette.saison == "Ã©tÃ©"


class TestIngredientInput:
    """Tests pour IngredientInput."""
    
    def test_nom_nettoye(self):
        """Nom est nettoyÃ© et capitalisÃ©."""
        from src.core.validators_pydantic import IngredientInput
        
        ingredient = IngredientInput(
            nom="  farine  ",
            quantite=2.5,
            unite="kg"
        )
        assert ingredient.nom == "Farine"
    
    def test_quantite_valide(self):
        """QuantitÃ© valide est acceptÃ©e."""
        from src.core.validators_pydantic import IngredientInput
        
        ingredient = IngredientInput(
            nom="Sucre",
            quantite=1.0,
            unite="kg"
        )
        assert ingredient.quantite == 1.0


class TestRepasInput:
    """Tests pour RepasInput."""
    
    def test_type_repas_valide(self):
        """Type de repas valide est normalisÃ©."""
        from src.core.validators_pydantic import RepasInput
        
        repas = RepasInput(
            date=date.today(),
            type_repas="DÃ‰JEUNER",
            portions=4
        )
        assert repas.type_repas == "dÃ©jeuner"
    
    def test_type_repas_invalide(self):
        """Type de repas invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RepasInput
        
        with pytest.raises(ValidationError) as exc_info:
            RepasInput(
                date=date.today(),
                type_repas="brunch",  # Invalide
                portions=4
            )
        assert "Type invalide" in str(exc_info.value)


class TestRoutineInput:
    """Tests pour RoutineInput."""
    
    def test_frequence_valide(self):
        """FrÃ©quence valide est normalisÃ©e."""
        from src.core.validators_pydantic import RoutineInput
        
        routine = RoutineInput(
            nom="Routine matin",
            description="Routine quotidienne",
            pour_qui="Jules",
            frequence="QUOTIDIEN"
        )
        assert routine.frequence == "quotidien"
    
    def test_frequence_invalide(self):
        """FrÃ©quence invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import RoutineInput
        
        with pytest.raises(ValidationError) as exc_info:
            RoutineInput(
                nom="Routine matin",
                description="Description",
                pour_qui="Jules",
                frequence="annuel"  # Invalide
            )
        assert "FrÃ©quence invalide" in str(exc_info.value)


class TestTacheRoutineInput:
    """Tests pour TacheRoutineInput."""
    
    def test_nom_nettoye(self):
        """Nom est nettoyÃ© et capitalisÃ©."""
        from src.core.validators_pydantic import TacheRoutineInput
        
        tache = TacheRoutineInput(
            nom="  se brosser les dents  ",
            heure="08:00"
        )
        assert tache.nom == "Se brosser les dents"
    
    def test_heure_format_invalide(self):
        """Format heure invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import TacheRoutineInput
        
        with pytest.raises(ValidationError):
            TacheRoutineInput(
                nom="TÃ¢che",
                heure="8h30"  # Format invalide
            )


class TestEntreeJournalInput:
    """Tests pour EntreeJournalInput."""
    
    def test_domaine_valide(self):
        """Domaine valide est normalisÃ©."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        entree = EntreeJournalInput(
            domaine="SANTÃ‰",
            titre="Ma journÃ©e",
            contenu="Contenu de l'entrÃ©e"
        )
        assert entree.domaine == "santÃ©"
    
    def test_domaine_invalide(self):
        """Domaine invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        with pytest.raises(ValidationError) as exc_info:
            EntreeJournalInput(
                domaine="travail",  # Invalide
                titre="Ma journÃ©e",
                contenu="Contenu"
            )
        assert "Domaine invalide" in str(exc_info.value)
    
    def test_titre_nettoye(self):
        """Titre est nettoyÃ© et capitalisÃ©."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        entree = EntreeJournalInput(
            domaine="humeur",
            titre="  ma super journÃ©e  ",
            contenu="Contenu"
        )
        assert entree.titre == "Ma super journÃ©e"


class TestProjetInput:
    """Tests pour ProjetInput."""
    
    def test_priorite_valide(self):
        """PrioritÃ© valide est normalisÃ©e."""
        from src.core.validators_pydantic import ProjetInput
        
        projet = ProjetInput(
            nom="RÃ©novation cuisine",
            description="Refaire la cuisine",
            categorie="renovation",
            priorite="HAUTE"
        )
        assert projet.priorite == "haute"
    
    def test_priorite_invalide(self):
        """PrioritÃ© invalide lÃ¨ve une erreur."""
        from src.core.validators_pydantic import ProjetInput
        
        with pytest.raises(ValidationError) as exc_info:
            ProjetInput(
                nom="Projet",
                description="Description",
                categorie="travaux",
                priorite="urgente"  # Invalide
            )
        assert "PrioritÃ© invalide" in str(exc_info.value)
    
    def test_dates_invalides(self):
        """Date fin avant date dÃ©but lÃ¨ve une erreur."""
        from src.core.validators_pydantic import ProjetInput
        
        with pytest.raises(ValidationError) as exc_info:
            ProjetInput(
                nom="Projet",
                description="Description",
                categorie="travaux",
                priorite="haute",
                date_debut=date(2026, 6, 1),
                date_fin_estimee=date(2026, 5, 1)  # Avant date_debut
            )
        assert "date de fin doit Ãªtre aprÃ¨s" in str(exc_info.value)
    
    def test_dates_valides(self):
        """Dates valides sont acceptÃ©es."""
        from src.core.validators_pydantic import ProjetInput
        
        projet = ProjetInput(
            nom="Projet",
            description="Description",
            categorie="travaux",
            priorite="moyenne",
            date_debut=date(2026, 5, 1),
            date_fin_estimee=date(2026, 6, 1)
        )
        assert projet.date_debut < projet.date_fin_estimee
    
    def test_nom_nettoye(self):
        """Nom du projet est nettoyÃ©."""
        from src.core.validators_pydantic import ProjetInput
        
        projet = ProjetInput(
            nom="  rÃ©novation salle de bain  ",
            description="Description",
            categorie="renovation",
            priorite="basse"
        )
        assert projet.nom == "RÃ©novation salle de bain"
