# -*- coding: utf-8 -*-
"""
Tests supplémentaires pour validators_pydantic.py

Cible les lignes non couvertes: 136-138, 171, 175, 211-213, 241-251, 
275, 281-286, 301, 326-331, 336, 361, 367-372, 377-383
"""
import pytest
from datetime import date
from pydantic import ValidationError


class TestRecetteInputValidators:
    """Tests pour les validateurs de RecetteInput."""
    
    def test_recette_nom_trop_court(self):
        """Nom avec moins de 2 caractères lève une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="A",  # Trop court
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="déjeuner"
            )
        assert "au moins 2 caractères" in str(exc_info.value)
    
    def test_recette_difficulte_invalide(self):
        """Difficulté invalide lève une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="Tarte aux pommes",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="expert",  # Invalide
                type_repas="déjeuner"
            )
        assert "Difficulté invalide" in str(exc_info.value)
    
    def test_recette_type_repas_invalide(self):
        """Type de repas invalide lève une erreur."""
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
        """Saison invalide lève une erreur."""
        from src.core.validators_pydantic import RecetteInput
        
        with pytest.raises(ValidationError) as exc_info:
            RecetteInput(
                nom="Tarte aux pommes",
                temps_preparation=10,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="déjeuner",
                saison="pluvieuse"  # Invalide
            )
        assert "Saison invalide" in str(exc_info.value)
    
    def test_recette_saison_none(self):
        """Saison None est acceptée."""
        from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
        
        recette = RecetteInput(
            nom="Tarte aux pommes",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile",
            type_repas="déjeuner",
            ingredients=[IngredientInput(nom="Pommes", quantite=3, unite="pièces")],
            etapes=[EtapeInput(numero=1, description="Préparer les pommes")],
            saison=None
        )
        assert recette.saison is None
    
    def test_recette_saison_valide(self):
        """Saison valide est normalisée."""
        from src.core.validators_pydantic import RecetteInput, IngredientInput, EtapeInput
        
        recette = RecetteInput(
            nom="Tarte aux pommes",
            temps_preparation=10,
            temps_cuisson=20,
            portions=4,
            difficulte="facile",
            type_repas="déjeuner",
            ingredients=[IngredientInput(nom="Pommes", quantite=3, unite="pièces")],
            etapes=[EtapeInput(numero=1, description="Préparer les pommes")],
            saison="ÉTÉ"  # En majuscules
        )
        assert recette.saison == "été"


class TestIngredientInput:
    """Tests pour IngredientInput."""
    
    def test_nom_nettoye(self):
        """Nom est nettoyé et capitalisé."""
        from src.core.validators_pydantic import IngredientInput
        
        ingredient = IngredientInput(
            nom="  farine  ",
            quantite=2.5,
            unite="kg"
        )
        assert ingredient.nom == "Farine"
    
    def test_quantite_valide(self):
        """Quantité valide est acceptée."""
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
        """Type de repas valide est normalisé."""
        from src.core.validators_pydantic import RepasInput
        
        repas = RepasInput(
            date=date.today(),
            type_repas="DÉJEUNER",
            portions=4
        )
        assert repas.type_repas == "déjeuner"
    
    def test_type_repas_invalide(self):
        """Type de repas invalide lève une erreur."""
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
        """Fréquence valide est normalisée."""
        from src.core.validators_pydantic import RoutineInput
        
        routine = RoutineInput(
            nom="Routine matin",
            description="Routine quotidienne",
            pour_qui="Jules",
            frequence="QUOTIDIEN"
        )
        assert routine.frequence == "quotidien"
    
    def test_frequence_invalide(self):
        """Fréquence invalide lève une erreur."""
        from src.core.validators_pydantic import RoutineInput
        
        with pytest.raises(ValidationError) as exc_info:
            RoutineInput(
                nom="Routine matin",
                description="Description",
                pour_qui="Jules",
                frequence="annuel"  # Invalide
            )
        assert "Fréquence invalide" in str(exc_info.value)


class TestTacheRoutineInput:
    """Tests pour TacheRoutineInput."""
    
    def test_nom_nettoye(self):
        """Nom est nettoyé et capitalisé."""
        from src.core.validators_pydantic import TacheRoutineInput
        
        tache = TacheRoutineInput(
            nom="  se brosser les dents  ",
            heure="08:00"
        )
        assert tache.nom == "Se brosser les dents"
    
    def test_heure_format_invalide(self):
        """Format heure invalide lève une erreur."""
        from src.core.validators_pydantic import TacheRoutineInput
        
        with pytest.raises(ValidationError):
            TacheRoutineInput(
                nom="Tâche",
                heure="8h30"  # Format invalide
            )


class TestEntreeJournalInput:
    """Tests pour EntreeJournalInput."""
    
    def test_domaine_valide(self):
        """Domaine valide est normalisé."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        entree = EntreeJournalInput(
            domaine="SANTÉ",
            titre="Ma journée",
            contenu="Contenu de l'entrée"
        )
        assert entree.domaine == "santé"
    
    def test_domaine_invalide(self):
        """Domaine invalide lève une erreur."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        with pytest.raises(ValidationError) as exc_info:
            EntreeJournalInput(
                domaine="travail",  # Invalide
                titre="Ma journée",
                contenu="Contenu"
            )
        assert "Domaine invalide" in str(exc_info.value)
    
    def test_titre_nettoye(self):
        """Titre est nettoyé et capitalisé."""
        from src.core.validators_pydantic import EntreeJournalInput
        
        entree = EntreeJournalInput(
            domaine="humeur",
            titre="  ma super journée  ",
            contenu="Contenu"
        )
        assert entree.titre == "Ma super journée"


class TestProjetInput:
    """Tests pour ProjetInput."""
    
    def test_priorite_valide(self):
        """Priorité valide est normalisée."""
        from src.core.validators_pydantic import ProjetInput
        
        projet = ProjetInput(
            nom="Rénovation cuisine",
            description="Refaire la cuisine",
            categorie="renovation",
            priorite="HAUTE"
        )
        assert projet.priorite == "haute"
    
    def test_priorite_invalide(self):
        """Priorité invalide lève une erreur."""
        from src.core.validators_pydantic import ProjetInput
        
        with pytest.raises(ValidationError) as exc_info:
            ProjetInput(
                nom="Projet",
                description="Description",
                categorie="travaux",
                priorite="urgente"  # Invalide
            )
        assert "Priorité invalide" in str(exc_info.value)
    
    def test_dates_invalides(self):
        """Date fin avant date début lève une erreur."""
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
        assert "date de fin doit être après" in str(exc_info.value)
    
    def test_dates_valides(self):
        """Dates valides sont acceptées."""
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
        """Nom du projet est nettoyé."""
        from src.core.validators_pydantic import ProjetInput
        
        projet = ProjetInput(
            nom="  rénovation salle de bain  ",
            description="Description",
            categorie="renovation",
            priorite="basse"
        )
        assert projet.nom == "Rénovation salle de bain"
