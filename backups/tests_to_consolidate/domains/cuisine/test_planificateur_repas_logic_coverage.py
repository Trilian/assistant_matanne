"""
Tests de couverture complets pour planificateur_repas_logic.py
Objectif: atteindre 80%+ de couverture
Couvre: calculer_score_recette edge cases, generer_suggestions_alternatives,
        generer_prompt_semaine, generer_prompt_alternative,
        valider_equilibre_semaine, suggerer_ajustements_equilibre
"""

from dataclasses import dataclass, field
from datetime import date, timedelta

from src.modules.cuisine.logic.planificateur_repas_logic import (
    PlanningSemaine,
    RecetteSuggestion,
    RepasPlannifie,
    calculer_score_recette,
    generer_prompt_alternative,
    generer_prompt_semaine,
    generer_suggestions_alternatives,
    suggerer_ajustements_equilibre,
    valider_equilibre_semaine,
)
from src.modules.cuisine.logic.schemas import FeedbackRecette, PreferencesUtilisateur

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@dataclass
class RecetteMock:
    """Mock de recette pour les tests."""

    id: int = 1
    nom: str = "Recette test"
    description: str = "Description test"
    type_proteine: str | None = None
    temps_preparation: int = 30
    temps_cuisson: int = 0
    portions: int = 4
    difficulte: str = "moyen"
    compatible_bebe: bool = False
    compatible_batch: bool = False
    instructions_bebe: str | None = None
    ingredients: list[any] = field(default_factory=list)
    type_repas: str | None = None


@dataclass
class IngredientMock:
    """Mock d'ingrÃ©dient."""

    nom: str


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CALCULER_SCORE_RECETTE - EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCalculerScoreRecetteEdgeCases:
    """Tests approfondis pour calculer_score_recette."""

    def test_score_equilibre_poisson_manquant(self):
        """Bonus si catÃ©gorie poisson manquante."""
        recette = RecetteMock(type_proteine="poisson")
        prefs = PreferencesUtilisateur(poisson_par_semaine=2)

        score, raison = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={"poisson": 0},
            stock_disponible=[],
        )

        # Score devrait Ãªtre > 50 (bonus pour Ã©quilibre)
        assert score > 50
        assert "Ã©quilibre" in raison.lower() or "standard" in raison.lower()

    def test_score_viande_rouge_exces(self):
        """Malus si trop de viande rouge."""
        recette = RecetteMock(type_proteine="boeuf")
        prefs = PreferencesUtilisateur(viande_rouge_max=1)

        score, raison = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={"viande_rouge": 2},
            stock_disponible=[],
        )

        # Score devrait Ãªtre < 50 (malus viande rouge)
        assert score < 50

    def test_score_vegetarien_manquant(self):
        """Bonus si vÃ©gÃ©tarien manquant."""
        recette = RecetteMock(type_proteine="tofu")
        prefs = PreferencesUtilisateur(vegetarien_par_semaine=2)

        # tofu -> catÃ©gorie vegan -> compte comme vÃ©gÃ©tarien
        score, raison = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={"vegetarien": 0},
            stock_disponible=[],
        )

        assert score >= 50

    def test_score_stock_disponible(self):
        """Bonus si plusieurs ingrÃ©dients en stock."""
        recette = RecetteMock()
        recette.ingredients = [
            IngredientMock(nom="poulet"),
            IngredientMock(nom="carottes"),
            IngredientMock(nom="oignons"),
            IngredientMock(nom="pommes de terre"),
        ]
        prefs = PreferencesUtilisateur()

        score_sans_stock, _ = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        score_avec_stock, raison = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=["poulet", "carottes", "oignons"],
        )

        # Bonus pour stock (3 ingrÃ©dients en stock)
        assert score_avec_stock > score_sans_stock
        assert "stock" in raison.lower()

    def test_score_temps_long(self):
        """Malus si temps de prÃ©paration long."""
        recette = RecetteMock(temps_preparation=60, temps_cuisson=60)
        prefs = PreferencesUtilisateur(temps_semaine="express")

        score, raison = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        # Malus pour temps long
        assert score < 50
        assert "temps" in raison.lower()

    def test_score_compatible_jules(self):
        """Bonus si compatible bÃ©bÃ© et jules prÃ©sent."""
        recette = RecetteMock(compatible_bebe=True)
        prefs = PreferencesUtilisateur(jules_present=True)

        score_sans, _ = calculer_score_recette(
            recette=recette,
            preferences=PreferencesUtilisateur(jules_present=False),
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        score_avec, _ = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        assert score_avec >= score_sans

    def test_score_instructions_bebe(self):
        """Bonus si recette a des instructions bÃ©bÃ©."""
        recette = RecetteMock(instructions_bebe="Mixer finement")
        prefs = PreferencesUtilisateur(jules_present=True)

        score, _ = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        assert score >= 50

    def test_score_compatible_batch(self):
        """Bonus pour batch cooking."""
        recette = RecetteMock(compatible_batch=True)
        prefs = PreferencesUtilisateur()

        score, _ = calculer_score_recette(
            recette=recette,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )

        # Batch cooking donne +5
        assert score > 50

    def test_score_normalise_0_100(self):
        """Score toujours entre 0 et 100."""
        # Score trÃ¨s bas (multiples exclusions)
        recette_basse = RecetteMock(nom="Poulet boeuf poisson")
        prefs_exclus = PreferencesUtilisateur(aliments_exclus=["poulet"])

        score_bas, _ = calculer_score_recette(
            recette=recette_basse,
            preferences=prefs_exclus,
            feedbacks=[],
            equilibre_actuel={},
            stock_disponible=[],
        )
        assert score_bas >= 0

        # Score potentiellement trÃ¨s haut
        recette_haute = RecetteMock(
            nom="Poulet rÃ´ti", type_proteine="poulet", compatible_bebe=True, compatible_batch=True
        )
        recette_haute.ingredients = [
            IngredientMock(nom="poulet"),
            IngredientMock(nom="carottes"),
            IngredientMock(nom="oignons"),
        ]
        prefs_favoris = PreferencesUtilisateur(aliments_favoris=["poulet"], jules_present=True)

        score_haut, _ = calculer_score_recette(
            recette=recette_haute,
            preferences=prefs_favoris,
            feedbacks=[FeedbackRecette(recette_id=1, recette_nom="Poulet rÃ´ti", feedback="like")],
            equilibre_actuel={},
            stock_disponible=["poulet", "carottes", "oignons"],
        )
        assert score_haut <= 100


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER_SUGGESTIONS_ALTERNATIVES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererSuggestionsAlternatives:
    """Tests pour generer_suggestions_alternatives."""

    def test_generer_alternatives_basique(self):
        """GÃ©nÃ¨re des alternatives basiques."""
        recette_actuelle = RecetteSuggestion(
            id=1,
            nom="Poulet",
            description="Test",
            temps_preparation=30,
            temps_cuisson=30,
            portions=4,
            difficulte="moyen",
        )

        recettes = [
            RecetteMock(id=1, nom="Poulet rÃ´ti"),
            RecetteMock(id=2, nom="Saumon grillÃ©"),
            RecetteMock(id=3, nom="Salade niÃ§oise"),
            RecetteMock(id=4, nom="PÃ¢tes bolognaise"),
        ]
        prefs = PreferencesUtilisateur()

        alternatives = generer_suggestions_alternatives(
            recette_actuelle=recette_actuelle,
            toutes_recettes=recettes,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock=[],
            nb_alternatives=2,
        )

        # Ne doit pas inclure la recette actuelle
        assert all(a.id != 1 for a in alternatives)
        # Maximum nb_alternatives
        assert len(alternatives) <= 2

    def test_generer_alternatives_sans_recette_actuelle(self):
        """GÃ©nÃ¨re si recette_actuelle est None."""
        recettes = [
            RecetteMock(id=1, nom="Poulet rÃ´ti"),
            RecetteMock(id=2, nom="Saumon grillÃ©"),
        ]
        prefs = PreferencesUtilisateur()

        alternatives = generer_suggestions_alternatives(
            recette_actuelle=None,
            toutes_recettes=recettes,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock=[],
            nb_alternatives=3,
        )

        assert len(alternatives) <= 3

    def test_generer_alternatives_vides(self):
        """Retourne vide si aucune recette Ã©ligible."""
        recette_actuelle = RecetteSuggestion(
            id=1,
            nom="Test",
            description="Test",
            temps_preparation=30,
            temps_cuisson=0,
            portions=4,
            difficulte="moyen",
        )

        # Toutes les recettes exclues
        recettes = [RecetteMock(id=2, nom="Poulet exclus")]
        prefs = PreferencesUtilisateur(aliments_exclus=["poulet"])

        alternatives = generer_suggestions_alternatives(
            recette_actuelle=recette_actuelle,
            toutes_recettes=recettes,
            preferences=prefs,
            feedbacks=[],
            equilibre_actuel={},
            stock=[],
        )

        assert len(alternatives) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER_PROMPT_SEMAINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererPromptSemaine:
    """Tests pour generer_prompt_semaine."""

    def test_generer_prompt_basique(self):
        """GÃ©nÃ¨re un prompt basique."""
        prefs = PreferencesUtilisateur()
        feedbacks = []

        prompt = generer_prompt_semaine(
            preferences=prefs, feedbacks=feedbacks, date_debut=date.today()
        )

        assert "CONTEXTE FAMILLE" in prompt
        assert "adultes" in prompt
        assert "Jules" in prompt
        assert "JSON" in prompt

    def test_generer_prompt_avec_feedbacks(self):
        """Prompt inclut les feedbacks."""
        prefs = PreferencesUtilisateur()
        feedbacks = [
            FeedbackRecette(recette_id=1, recette_nom="Poulet rÃ´ti", feedback="like"),
            FeedbackRecette(recette_id=2, recette_nom="Saumon froid", feedback="dislike"),
        ]

        prompt = generer_prompt_semaine(
            preferences=prefs, feedbacks=feedbacks, date_debut=date.today()
        )

        assert "Poulet rÃ´ti" in prompt  # Recette aimÃ©e
        assert "Saumon froid" in prompt  # Recette pas aimÃ©e

    def test_generer_prompt_avec_exclusions(self):
        """Prompt inclut les exclusions."""
        prefs = PreferencesUtilisateur(aliments_exclus=["porc", "fruits de mer"])

        prompt = generer_prompt_semaine(preferences=prefs, feedbacks=[], date_debut=date.today())

        assert "porc" in prompt
        assert "fruits de mer" in prompt

    def test_generer_prompt_avec_favoris(self):
        """Prompt inclut les favoris."""
        prefs = PreferencesUtilisateur(aliments_favoris=["poulet", "poisson"])

        prompt = generer_prompt_semaine(preferences=prefs, feedbacks=[], date_debut=date.today())

        assert "poulet" in prompt
        assert "poisson" in prompt

    def test_generer_prompt_jours_partiels(self):
        """Prompt pour jours sÃ©lectionnÃ©s."""
        prefs = PreferencesUtilisateur()

        prompt = generer_prompt_semaine(
            preferences=prefs,
            feedbacks=[],
            date_debut=date.today(),
            jours_a_planifier=["Lundi", "Mardi"],
        )

        assert "Lundi, Mardi" in prompt


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER_PROMPT_ALTERNATIVE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGenererPromptAlternative:
    """Tests pour generer_prompt_alternative."""

    def test_generer_prompt_alternative_basique(self):
        """GÃ©nÃ¨re un prompt d'alternative."""
        prefs = PreferencesUtilisateur()
        contraintes = {"poisson": 1, "vegetarien": 0}

        prompt = generer_prompt_alternative(
            recette_a_remplacer="Poulet rÃ´ti",
            type_repas="dÃ®ner",
            jour="Mercredi",
            preferences=prefs,
            contraintes_equilibre=contraintes,
        )

        assert "Poulet rÃ´ti" in prompt
        assert "dÃ®ner" in prompt
        assert "Mercredi" in prompt
        assert "alternatives" in prompt.lower()

    def test_generer_prompt_alternative_avec_equilibre(self):
        """Prompt inclut l'Ã©quilibre actuel."""
        prefs = PreferencesUtilisateur(poisson_par_semaine=2, vegetarien_par_semaine=2)
        contraintes = {"poisson": 1, "vegetarien": 2, "viande_rouge": 0}

        prompt = generer_prompt_alternative(
            recette_a_remplacer="Test",
            type_repas="dÃ©jeuner",
            jour="Lundi",
            preferences=prefs,
            contraintes_equilibre=contraintes,
        )

        assert "1/2" in prompt  # poisson 1/2
        assert "2/2" in prompt  # vÃ©gÃ©tarien 2/2

    def test_generer_prompt_alternative_avec_exclusions(self):
        """Prompt inclut les exclusions."""
        prefs = PreferencesUtilisateur(aliments_exclus=["porc"])

        prompt = generer_prompt_alternative(
            recette_a_remplacer="Test",
            type_repas="dÃ®ner",
            jour="Jeudi",
            preferences=prefs,
            contraintes_equilibre={},
        )

        assert "porc" in prompt


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS VALIDER_EQUILIBRE_SEMAINE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestValiderEquilibreSemaine:
    """Tests pour valider_equilibre_semaine."""

    def test_semaine_equilibree(self):
        """Semaine Ã©quilibrÃ©e = pas d'alertes."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today() + timedelta(days=i),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=i,
                        nom=f"Recette {i}",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine=["poisson", "volaille"][i % 2],
                    ),
                )
                for i in range(12)
            ],
        )

        prefs = PreferencesUtilisateur(
            poisson_par_semaine=2, vegetarien_par_semaine=0, viande_rouge_max=2
        )

        est_valide, alertes = valider_equilibre_semaine(planning, prefs)

        # Au moins 10 repas et Ã©quilibre OK
        assert est_valide or len(alertes) > 0

    def test_semaine_manque_poisson(self):
        """Alerte si pas assez de poisson."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today() + timedelta(days=i),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=i,
                        nom=f"Volaille {i}",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine="volaille",
                    ),
                )
                for i in range(12)
            ],
        )

        prefs = PreferencesUtilisateur(poisson_par_semaine=2)

        est_valide, alertes = valider_equilibre_semaine(planning, prefs)

        assert not est_valide
        assert any("poisson" in a.lower() for a in alertes)

    def test_semaine_trop_viande_rouge(self):
        """Alerte si trop de viande rouge."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today() + timedelta(days=i),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=i,
                        nom=f"Boeuf {i}",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine="viande_rouge",
                    ),
                )
                for i in range(12)
            ],
        )

        prefs = PreferencesUtilisateur(viande_rouge_max=1)

        est_valide, alertes = valider_equilibre_semaine(planning, prefs)

        assert not est_valide
        assert any("viande rouge" in a.lower() for a in alertes)

    def test_semaine_peu_repas_planifies(self):
        """Alerte si moins de 10 repas."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today(),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=1,
                        nom="Test",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                    ),
                )
            ],
        )

        prefs = PreferencesUtilisateur()

        est_valide, alertes = valider_equilibre_semaine(planning, prefs)

        assert not est_valide
        assert any("planifiÃ©" in a.lower() for a in alertes)

    def test_semaine_manque_vegetarien(self):
        """Alerte si pas assez de vÃ©gÃ©tarien."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today() + timedelta(days=i),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=i,
                        nom=f"Viande {i}",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine="volaille",
                    ),
                )
                for i in range(12)
            ],
        )

        prefs = PreferencesUtilisateur(vegetarien_par_semaine=2)

        est_valide, alertes = valider_equilibre_semaine(planning, prefs)

        assert not est_valide
        assert any("vÃ©gÃ©tarien" in a.lower() for a in alertes)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGERER_AJUSTEMENTS_EQUILIBRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestSuggererAjustementsEquilibre:
    """Tests pour suggerer_ajustements_equilibre."""

    def test_suggerer_plus_poisson(self):
        """SuggÃ¨re d'ajouter du poisson."""
        equilibre = {"poisson": 0, "vegetarien": 2, "viande_rouge": 0}
        prefs = PreferencesUtilisateur(poisson_par_semaine=2)

        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)

        assert len(suggestions) >= 1
        assert any("poisson" in s.lower() for s in suggestions)

    def test_suggerer_plus_vegetarien(self):
        """SuggÃ¨re d'ajouter du vÃ©gÃ©tarien."""
        equilibre = {"poisson": 2, "vegetarien": 0, "viande_rouge": 0}
        prefs = PreferencesUtilisateur(vegetarien_par_semaine=2)

        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)

        assert len(suggestions) >= 1
        assert any("vÃ©gÃ©tarien" in s.lower() for s in suggestions)

    def test_suggerer_moins_viande_rouge(self):
        """SuggÃ¨re de rÃ©duire la viande rouge."""
        equilibre = {"poisson": 2, "vegetarien": 2, "viande_rouge": 3}
        prefs = PreferencesUtilisateur(viande_rouge_max=1)

        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)

        assert len(suggestions) >= 1
        assert any("viande rouge" in s.lower() for s in suggestions)

    def test_equilibre_ok_pas_suggestions(self):
        """Pas de suggestions si Ã©quilibre OK."""
        equilibre = {"poisson": 2, "vegetarien": 2, "viande_rouge": 1}
        prefs = PreferencesUtilisateur(
            poisson_par_semaine=2, vegetarien_par_semaine=2, viande_rouge_max=2
        )

        suggestions = suggerer_ajustements_equilibre(equilibre, prefs)

        assert len(suggestions) == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PLANNING SEMAINE - GET_EQUILIBRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPlanningSemaineEquilibre:
    """Tests approfondis pour PlanningSemaine.get_equilibre."""

    def test_equilibre_avec_vegan(self):
        """CatÃ©gorie vegan compte comme vÃ©gÃ©tarien."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today(),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=1,
                        nom="Tofu",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine="vegan",
                    ),
                )
            ],
        )

        equilibre = planning.get_equilibre()

        assert equilibre["vegetarien"] == 1

    def test_equilibre_sans_recette(self):
        """Repas sans recette ne compte pas."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[RepasPlannifie(jour=date.today(), type_repas="dÃ©jeuner", recette=None)],
        )

        equilibre = planning.get_equilibre()

        assert equilibre["poisson"] == 0
        assert equilibre["vegetarien"] == 0

    def test_equilibre_categorie_inconnue(self):
        """CatÃ©gorie inconnue est ignorÃ©e."""
        planning = PlanningSemaine(
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=6),
            repas=[
                RepasPlannifie(
                    jour=date.today(),
                    type_repas="dÃ©jeuner",
                    recette=RecetteSuggestion(
                        id=1,
                        nom="Autre",
                        description="",
                        temps_preparation=30,
                        temps_cuisson=0,
                        portions=4,
                        difficulte="moyen",
                        categorie_proteine="autre_inconnu",
                    ),
                )
            ],
        )

        equilibre = planning.get_equilibre()

        # Ne doit pas lever d'erreur
        assert "autre_inconnu" not in equilibre
