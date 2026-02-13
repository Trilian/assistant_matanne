"""
Tests du package budget - Schémas Pydantic.

Tests de validation des modèles de données pour le budget familial.
"""

from datetime import date, datetime

from src.services.budget.schemas import (
    DEFAULT_USER_ID,
    BudgetMensuel,
    CategorieDepense,
    Depense,
    FactureMaison,
    FrequenceRecurrence,
    PrevisionDepense,
    ResumeFinancier,
)


class TestCategorieDepense:
    """Tests pour l'enum CategorieDepense."""

    def test_categories_principales(self):
        """Vérifie les catégories principales."""
        assert CategorieDepense.ALIMENTATION == "alimentation"
        assert CategorieDepense.COURSES == "courses"
        assert CategorieDepense.MAISON == "maison"
        assert CategorieDepense.SANTE == "santé"

    def test_categories_factures_maison(self):
        """Vérifie les catégories de factures."""
        assert CategorieDepense.GAZ == "gaz"
        assert CategorieDepense.ELECTRICITE == "electricite"
        assert CategorieDepense.EAU == "eau"
        assert CategorieDepense.LOYER == "loyer"

    def test_categorie_depuis_valeur(self):
        """Création depuis une valeur string."""
        cat = CategorieDepense("alimentation")
        assert cat == CategorieDepense.ALIMENTATION


class TestFrequenceRecurrence:
    """Tests pour l'enum FrequenceRecurrence."""

    def test_frequences_disponibles(self):
        """Vérifie les fréquences."""
        assert FrequenceRecurrence.PONCTUEL == "ponctuel"
        assert FrequenceRecurrence.MENSUEL == "mensuel"
        assert FrequenceRecurrence.ANNUEL == "annuel"


class TestDepense:
    """Tests pour le modèle Depense."""

    def test_creation_minimale(self):
        """Création avec les champs requis."""
        depense = Depense(montant=45.50, categorie=CategorieDepense.ALIMENTATION)

        assert depense.montant == 45.50
        assert depense.categorie == CategorieDepense.ALIMENTATION
        assert depense.date == date.today()
        assert depense.est_recurrente is False

    def test_creation_complete(self):
        """Création avec tous les champs."""
        depense = Depense(
            montant=150.00,
            categorie=CategorieDepense.COURSES,
            date=date(2026, 2, 10),
            description="Courses de la semaine",
            magasin="Carrefour",
            payeur="Marie",
            moyen_paiement="CB",
        )

        assert depense.montant == 150.00
        assert depense.description == "Courses de la semaine"
        assert depense.magasin == "Carrefour"
        assert depense.payeur == "Marie"

    def test_depense_recurrente(self):
        """Création d'une dépense récurrente."""
        depense = Depense(
            montant=50.00,
            categorie=CategorieDepense.LOYER,
            est_recurrente=True,
            frequence=FrequenceRecurrence.MENSUEL,
        )

        assert depense.est_recurrente is True
        assert depense.frequence == FrequenceRecurrence.MENSUEL

    def test_depense_remboursable(self):
        """Dépense avec remboursement."""
        depense = Depense(
            montant=75.00,
            categorie=CategorieDepense.SANTE,
            description="Consultation médecin",
            remboursable=True,
            rembourse=False,
        )

        assert depense.remboursable is True
        assert depense.rembourse is False

    def test_cree_le_auto(self):
        """La date de création est automatique."""
        depense = Depense(montant=10, categorie=CategorieDepense.AUTRE)

        assert depense.cree_le is not None
        assert isinstance(depense.cree_le, datetime)


class TestFactureMaison:
    """Tests pour le modèle FactureMaison."""

    def test_creation_facture(self):
        """Création d'une facture."""
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE, montant=85.50, mois=1, annee=2026
        )

        assert facture.montant == 85.50
        assert facture.mois == 1
        assert facture.annee == 2026

    def test_facture_avec_consommation(self):
        """Facture avec suivi consommation."""
        facture = FactureMaison(
            categorie=CategorieDepense.GAZ,
            montant=120.00,
            consommation=150.5,
            unite_consommation="m³",
            mois=12,
            annee=2025,
            fournisseur="Engie",
        )

        assert facture.consommation == 150.5
        assert facture.unite_consommation == "m³"
        assert facture.fournisseur == "Engie"

    def test_prix_unitaire_calcule(self):
        """Calcul du prix unitaire."""
        facture = FactureMaison(
            categorie=CategorieDepense.ELECTRICITE,
            montant=100.00,
            consommation=500.0,
            mois=2,
            annee=2026,
        )

        assert facture.prix_unitaire == 0.2  # 100/500 = 0.20€/kWh

    def test_prix_unitaire_sans_consommation(self):
        """Prix unitaire None si pas de consommation."""
        facture = FactureMaison(
            categorie=CategorieDepense.LOYER, montant=800.00, mois=2, annee=2026
        )

        assert facture.prix_unitaire is None

    def test_prix_unitaire_consommation_zero(self):
        """Prix unitaire None si consommation zéro."""
        facture = FactureMaison(
            categorie=CategorieDepense.EAU, montant=15.00, consommation=0, mois=2, annee=2026
        )

        assert facture.prix_unitaire is None

    def test_periode_formatee(self):
        """Période formatée correctement."""
        facture = FactureMaison(categorie=CategorieDepense.GAZ, montant=90.00, mois=3, annee=2026)

        assert facture.periode == "Mars 2026"

    def test_periode_tous_les_mois(self):
        """Vérifie le formatage pour tous les mois."""
        mois_attendus = [
            (1, "Janvier"),
            (2, "Février"),
            (3, "Mars"),
            (4, "Avril"),
            (5, "Mai"),
            (6, "Juin"),
            (7, "Juillet"),
            (8, "Août"),
            (9, "Septembre"),
            (10, "Octobre"),
            (11, "Novembre"),
            (12, "Décembre"),
        ]

        for num, nom in mois_attendus:
            facture = FactureMaison(
                categorie=CategorieDepense.EAU, montant=20.00, mois=num, annee=2026
            )
            assert nom in facture.periode


class TestBudgetMensuel:
    """Tests pour le modèle BudgetMensuel."""

    def test_creation_budget(self):
        """Création d'un budget."""
        budget = BudgetMensuel(
            mois=2, annee=2026, categorie=CategorieDepense.ALIMENTATION, budget_prevu=500.00
        )

        assert budget.budget_prevu == 500.00
        assert budget.depense_reelle == 0.0

    def test_pourcentage_utilise(self):
        """Calcul du pourcentage utilisé."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.COURSES,
            budget_prevu=400.00,
            depense_reelle=200.00,
        )

        assert budget.pourcentage_utilise == 50.0

    def test_pourcentage_utilise_depasse(self):
        """Pourcentage plafonné à 999 si dépassé."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=100.00,
            depense_reelle=500.00,
        )

        assert budget.pourcentage_utilise == 500.0

    def test_pourcentage_utilise_budget_zero(self):
        """Pourcentage 0 si budget zéro."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.AUTRE,
            budget_prevu=0.00,
            depense_reelle=100.00,
        )

        assert budget.pourcentage_utilise == 0.0

    def test_reste_disponible(self):
        """Calcul du reste disponible."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.VETEMENTS,
            budget_prevu=200.00,
            depense_reelle=75.00,
        )

        assert budget.reste_disponible == 125.00

    def test_reste_disponible_depasse(self):
        """Reste disponible 0 si dépassé."""
        budget = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.LOISIRS,
            budget_prevu=100.00,
            depense_reelle=150.00,
        )

        assert budget.reste_disponible == 0

    def test_est_depasse(self):
        """Détection budget dépassé."""
        budget_ok = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.00,
            depense_reelle=400.00,
        )

        budget_depasse = BudgetMensuel(
            mois=2,
            annee=2026,
            categorie=CategorieDepense.ALIMENTATION,
            budget_prevu=500.00,
            depense_reelle=600.00,
        )

        assert budget_ok.est_depasse is False
        assert budget_depasse.est_depasse is True


class TestResumeFinancier:
    """Tests pour le modèle ResumeFinancier."""

    def test_creation_resume(self):
        """Création d'un résumé financier."""
        resume = ResumeFinancier(mois=2, annee=2026, total_depenses=2500.00, total_budget=3000.00)

        assert resume.total_depenses == 2500.00
        assert resume.total_budget == 3000.00

    def test_resume_avec_categories(self):
        """Résumé avec détail par catégorie."""
        resume = ResumeFinancier(
            mois=2,
            annee=2026,
            depenses_par_categorie={"alimentation": 450.00, "courses": 200.00, "transport": 150.00},
        )

        assert resume.depenses_par_categorie["alimentation"] == 450.00
        assert len(resume.depenses_par_categorie) == 3

    def test_resume_avec_alertes(self):
        """Résumé avec catégories dépassées."""
        resume = ResumeFinancier(
            mois=2,
            annee=2026,
            categories_depassees=["loisirs", "vêtements"],
            categories_a_risque=["alimentation"],
        )

        assert "loisirs" in resume.categories_depassees
        assert "alimentation" in resume.categories_a_risque

    def test_resume_tendances(self):
        """Résumé avec tendances."""
        resume = ResumeFinancier(
            mois=2, annee=2026, variation_vs_mois_precedent=-5.2, moyenne_6_mois=2800.00
        )

        assert resume.variation_vs_mois_precedent == -5.2
        assert resume.moyenne_6_mois == 2800.00


class TestPrevisionDepense:
    """Tests pour le modèle PrevisionDepense."""

    def test_creation_prevision(self):
        """Création d'une prévision."""
        prev = PrevisionDepense(
            categorie=CategorieDepense.ALIMENTATION,
            montant_prevu=480.00,
            confiance=0.85,
            base_calcul="Moyenne des 3 derniers mois",
        )

        assert prev.montant_prevu == 480.00
        assert prev.confiance == 0.85
        assert "3 derniers mois" in prev.base_calcul

    def test_prevision_valeurs_defaut(self):
        """Valeurs par défaut des prévisions."""
        prev = PrevisionDepense(categorie=CategorieDepense.COURSES, montant_prevu=200.00)

        assert prev.confiance == 0.0
        assert prev.base_calcul == ""


class TestDefaultUserId:
    """Tests pour la constante DEFAULT_USER_ID."""

    def test_valeur_defaut(self):
        """Vérifie la valeur par défaut."""
        assert DEFAULT_USER_ID == "matanne"
