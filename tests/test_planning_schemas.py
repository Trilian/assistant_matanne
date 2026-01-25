"""
Tests Schémas Pydantic pour Planning

Validation complète des structures de données
✅ JourCompletSchema
✅ SemaineCompleSchema
✅ SemaineGenereeIASchema
✅ Contraintes et contexte

À lancer: pytest tests/test_planning_schemas.py -v
"""

import pytest
from datetime import date, datetime, timedelta
from pydantic import ValidationError

from src.services.planning_unified import (
    JourCompletSchema,
    SemaineCompleSchema,
    SemaineGenereeIASchema,
    ContexteFamilleSchema,
    ContraintesSchema,
)


# ═══════════════════════════════════════════════════════════
# TESTS: JOUR COMPLET SCHEMA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestJourCompletSchema:
    """Tests JourCompletSchema"""

    def test_jour_minimal(self):
        """Jour avec données minimales"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
        )

        assert jour.charge == "normal"
        assert jour.charge_score == 50
        assert jour.repas == []
        assert jour.activites == []

    def test_jour_complet(self):
        """Jour avec tous les champs"""
        today = date.today()

        jour = JourCompletSchema(
            date=today,
            charge="intense",
            charge_score=85,
            repas=[
                {
                    "type": "petit-déjeuner",
                    "recette": "Porridge",
                    "portions": 2,
                    "temps_total": 10,
                }
            ],
            activites=[
                {
                    "titre": "Sport",
                    "type": "fitness",
                    "pour_jules": False,
                    "budget": 0,
                }
            ],
            projets=[{"nom": "Projet A", "priorite": "haute"}],
            routines=[{"nom": "Yoga matinal", "ordre": 1}],
            events=[{"titre": "RDV", "type": "santé", "heure": "10:00"}],
            budget_jour=120.50,
            alertes=["Jour chargé"],
            notes="Notes du jour",
        )

        assert jour.date == today
        assert len(jour.repas) == 1
        assert len(jour.activites) == 1
        assert jour.charge_score == 85

    def test_charge_valide_faible(self):
        """Charge faible valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="faible",
            charge_score=25,
        )
        assert jour.charge == "faible"

    def test_charge_valide_normal(self):
        """Charge normal valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
        )
        assert jour.charge == "normal"

    def test_charge_valide_intense(self):
        """Charge intense valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="intense",
            charge_score=90,
        )
        assert jour.charge == "intense"

    def test_charge_invalide(self):
        """Charge invalide levée erreur"""
        with pytest.raises(ValidationError):
            JourCompletSchema(
                date=date.today(),
                charge="extremement_chargé",  # Invalide
                charge_score=50,
            )

    def test_charge_score_min(self):
        """Score charge à minimum (0)"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="faible",
            charge_score=0,
        )
        assert jour.charge_score == 0

    def test_charge_score_max(self):
        """Score charge à maximum (100)"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="intense",
            charge_score=100,
        )
        assert jour.charge_score == 100

    def test_charge_score_invalide_negatif(self):
        """Score charge négatif invalide"""
        with pytest.raises(ValidationError):
            JourCompletSchema(
                date=date.today(),
                charge="normal",
                charge_score=-10,
            )

    def test_charge_score_invalide_depassement(self):
        """Score charge > 100 invalide"""
        with pytest.raises(ValidationError):
            JourCompletSchema(
                date=date.today(),
                charge="normal",
                charge_score=150,
            )

    def test_budget_jour_positif(self):
        """Budget jour positif"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
            budget_jour=75.99,
        )
        assert jour.budget_jour == 75.99

    def test_budget_jour_zero(self):
        """Budget jour zéro"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
            budget_jour=0.0,
        )
        assert jour.budget_jour == 0.0

    def test_budget_jour_negatif_invalide(self):
        """Budget jour négatif invalide"""
        with pytest.raises(ValidationError):
            JourCompletSchema(
                date=date.today(),
                charge="normal",
                charge_score=50,
                budget_jour=-10.0,
            )

    def test_alertes_list(self):
        """List d'alertes valides"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="intense",
            charge_score=85,
            alertes=[
                "Jour très chargé",
                "Pas d'activité Jules",
                "Projet urgent",
            ],
        )
        assert len(jour.alertes) == 3

    def test_alertes_vide(self):
        """Alertes vides valide"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="faible",
            charge_score=20,
            alertes=[],
        )
        assert jour.alertes == []


# ═══════════════════════════════════════════════════════════
# TESTS: SEMAINE COMPLETE SCHEMA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSemaineCompleSchema:
    """Tests SemaineCompleSchema"""

    def test_semaine_minimal(self):
        """Semaine avec données minimales"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine = SemaineCompleSchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
        )

        assert semaine.charge_globale == "normal"
        assert len(semaine.jours) >= 1

    def test_semaine_7_jours(self):
        """Semaine 7 jours complets"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jours = {}
        for i in range(7):
            jour_date = debut + timedelta(days=i)
            jours[jour_date.isoformat()] = JourCompletSchema(
                date=jour_date,
                charge="normal",
                charge_score=50 + i * 5,
            )

        semaine = SemaineCompleSchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours=jours,
            charge_globale="normal",
        )

        assert len(semaine.jours) == 7

    def test_semaine_stats(self):
        """Semaine avec stats"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine = SemaineCompleSchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            stats_semaine={
                "total_repas": 12,
                "total_activites": 8,
                "total_events": 5,
                "charge_moyenne": 55,
                "budget_total": 300.50,
            },
            charge_globale="normal",
        )

        assert semaine.stats_semaine["total_repas"] == 12
        assert semaine.stats_semaine["budget_total"] == 300.50

    def test_charge_globale_valide(self):
        """Charge globale valide"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="intense",
            charge_score=80,
        )

        for charge in ["faible", "normal", "intense"]:
            semaine = SemaineCompleSchema(
                semaine_debut=debut,
                semaine_fin=debut + timedelta(days=6),
                jours={debut.isoformat(): jour},
                charge_globale=charge,
            )
            assert semaine.charge_globale == charge

    def test_charge_globale_invalide(self):
        """Charge globale invalide"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        with pytest.raises(ValidationError):
            SemaineCompleSchema(
                semaine_debut=debut,
                semaine_fin=debut + timedelta(days=6),
                jours={debut.isoformat(): jour},
                charge_globale="modéré",  # Invalide
            )

    def test_alertes_semaine(self):
        """Alertes semaine"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine = SemaineCompleSchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
            alertes_semaine=[
                "Semaine très budgétée",
                "Pas assez d'activité Jules",
            ],
        )

        assert len(semaine.alertes_semaine) == 2


# ═══════════════════════════════════════════════════════════
# TESTS: SEMAINE GÉNÉRÉE IA SCHEMA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSemaineGenereeIASchema:
    """Tests SemaineGenereeIASchema"""

    def test_semaine_generee_minimal(self):
        """Semaine générée IA minimale"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine_generee = SemaineGenereeIASchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
            raison="Optimisation équilibrée",
        )

        assert semaine_generee.raison == "Optimisation équilibrée"

    def test_semaine_generee_suggestions(self):
        """Semaine générée IA avec suggestions"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine_generee = SemaineGenereeIASchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
            raison="Optimisation",
            suggestions=[
                "Ajouter yoga mercredi",
                "Réduire surcharge samedi",
                "Augmenter temps famille",
            ],
        )

        assert len(semaine_generee.suggestions) == 3

    def test_semaine_generee_score_confiance(self):
        """Semaine générée IA avec score confiance"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        semaine_generee = SemaineGenereeIASchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
            raison="Optimisation",
            score_confiance=0.92,
        )

        assert 0 <= semaine_generee.score_confiance <= 1.0

    def test_semaine_generee_score_confiance_invalide(self):
        """Score confiance invalide levée erreur"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        with pytest.raises(ValidationError):
            SemaineGenereeIASchema(
                semaine_debut=debut,
                semaine_fin=debut + timedelta(days=6),
                jours={debut.isoformat(): jour},
                charge_globale="normal",
                raison="Optimisation",
                score_confiance=1.5,  # > 1.0
            )


# ═══════════════════════════════════════════════════════════
# TESTS: CONTEXTE FAMILLE SCHEMA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestContexteFamilleSchema:
    """Tests ContexteFamilleSchema"""

    def test_contexte_minimal(self):
        """Contexte minimal"""
        contexte = ContexteFamilleSchema(
            jules_age_mois=19,
        )
        assert contexte.jules_age_mois == 19

    def test_contexte_complet(self):
        """Contexte complet"""
        contexte = ContexteFamilleSchema(
            jules_age_mois=19,
            objectifs_sante=["Cardio", "Yoga"],
            preferences_repas=["Facile", "Rapide"],
            evenements_proches=["Anniversaire samedi"],
            constraints_budget=400.0,
        )

        assert contexte.jules_age_mois == 19
        assert len(contexte.objectifs_sante) == 2
        assert contexte.constraints_budget == 400.0

    def test_jules_age_valide_0(self):
        """Jules age minimum valide (0 mois)"""
        contexte = ContexteFamilleSchema(jules_age_mois=0)
        assert contexte.jules_age_mois == 0

    def test_jules_age_valide_5_ans(self):
        """Jules age valide (60 mois = 5 ans)"""
        contexte = ContexteFamilleSchema(jules_age_mois=60)
        assert contexte.jules_age_mois == 60

    def test_objectifs_sante_vide(self):
        """Objectifs santé vide valide"""
        contexte = ContexteFamilleSchema(
            jules_age_mois=19,
            objectifs_sante=[],
        )
        assert contexte.objectifs_sante == []

    def test_preferences_repas_list(self):
        """Préférences repas list"""
        contexte = ContexteFamilleSchema(
            jules_age_mois=19,
            preferences_repas=["Végétarien", "Sans gluten", "Sans arachides"],
        )
        assert len(contexte.preferences_repas) == 3


# ═══════════════════════════════════════════════════════════
# TESTS: CONTRAINTES SCHEMA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestContraintesSchema:
    """Tests ContraintesSchema"""

    def test_contraintes_minimal(self):
        """Contraintes minimales"""
        contraintes = ContraintesSchema()
        # Tous les champs ont des defaults
        assert contraintes is not None

    def test_contraintes_budget(self):
        """Contraintes avec budget"""
        contraintes = ContraintesSchema(
            budget=500.0,
        )
        assert contraintes.budget == 500.0

    def test_contraintes_energie(self):
        """Contraintes avec énergie"""
        for energie in ["basse", "normale", "haute"]:
            contraintes = ContraintesSchema(energie=energie)
            assert contraintes.energie == energie

    def test_contraintes_energie_invalide(self):
        """Contraintes énergie invalide"""
        with pytest.raises(ValidationError):
            ContraintesSchema(energie="extremement_basse")

    def test_contraintes_complexes(self):
        """Contraintes complexes"""
        contraintes = ContraintesSchema(
            budget=600.0,
            energie="basse",
            repas_rapides=True,
            activites_calmes=True,
            priorites=["Jules", "Santé"],
        )

        assert contraintes.budget == 600.0
        assert contraintes.repas_rapides is True
        assert len(contraintes.priorites) == 2

    def test_contraintes_budget_zero(self):
        """Contraintes budget zéro"""
        contraintes = ContraintesSchema(budget=0.0)
        assert contraintes.budget == 0.0

    def test_contraintes_budget_negatif_invalide(self):
        """Contraintes budget négatif invalide"""
        with pytest.raises(ValidationError):
            ContraintesSchema(budget=-100.0)


# ═══════════════════════════════════════════════════════════
# TESTS: COMPOSABILITÉ SCHÉMAS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestComposabiliteSchemas:
    """Tests composabilité et imbrication"""

    def test_jour_dans_semaine(self):
        """JourCompletSchema dans SemaineCompleSchema"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
            repas=[{"type": "dîner", "recette": "Pâtes"}],
        )

        semaine = SemaineCompleSchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
        )

        jour_recupere = semaine.jours[debut.isoformat()]
        assert jour_recupere.charge_score == 50
        assert len(jour_recupere.repas) == 1

    def test_semaine_avec_contexte(self):
        """Semaine générée IA avec contexte"""
        today = date.today()
        debut = today - timedelta(days=today.weekday())

        jour = JourCompletSchema(
            date=debut,
            charge="normal",
            charge_score=50,
        )

        contexte = ContexteFamilleSchema(
            jules_age_mois=19,
            objectifs_sante=["Cardio"],
        )

        # Les deux schémas peuvent coexister
        semaine_generee = SemaineGenereeIASchema(
            semaine_debut=debut,
            semaine_fin=debut + timedelta(days=6),
            jours={debut.isoformat(): jour},
            charge_globale="normal",
            raison="Optimisation santé",
        )

        assert semaine_generee.raison == "Optimisation santé"
        assert contexte.jules_age_mois == 19

    def test_export_json_jour(self):
        """Export JSON JourCompletSchema"""
        jour = JourCompletSchema(
            date=date.today(),
            charge="normal",
            charge_score=50,
        )

        json_data = jour.model_dump_json()
        assert isinstance(json_data, str)
        assert "charge" in json_data
        assert "50" in json_data


# ═══════════════════════════════════════════════════════════
# MARQUEURS
# ═══════════════════════════════════════════════════════════

pytest.mark.unit
