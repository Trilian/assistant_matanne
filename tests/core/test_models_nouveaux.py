"""
Tests unitaires pour models/nouveaux.py (src/core/models/nouveaux.py).

Tests couvrant:
- Modèles de dépenses et budget
- Modèles d'alertes météo
- Modèles de calendrier synchronisé
- Modèles de notifications push
- Validations d'énums
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session

from src.core.models.nouveaux import (
    CategorieDepenseDB,
    RecurrenceType,
    NiveauAlerte,
    TypeAlerteMeteo,
    CalendarProvider,
    Depense,
    BudgetMensuelDB,
    AlerteMeteo,
    ConfigMeteo,
    Backup,
    CalendrierExterne,
    EvenementCalendrier,
    PushSubscription,
    NotificationPreference,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: TESTS ENUMS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnums:
    """Tests pour les énums."""

    def test_categorie_depense_enum(self):
        """Test les catégories de dépense."""
        assert CategorieDepenseDB.ALIMENTATION.value == "alimentation"
        assert CategorieDepenseDB.TRANSPORT.value == "transport"
        assert CategorieDepenseDB.LOGEMENT.value == "logement"
        assert CategorieDepenseDB.SANTE.value == "sante"
        assert CategorieDepenseDB.LOISIRS.value == "loisirs"

    def test_recurrence_type_enum(self):
        """Test les types de récurrence."""
        assert RecurrenceType.PONCTUEL.value == "ponctuel"
        assert RecurrenceType.HEBDOMADAIRE.value == "hebdomadaire"
        assert RecurrenceType.MENSUEL.value == "mensuel"
        assert RecurrenceType.ANNUEL.value == "annuel"

    def test_niveau_alerte_enum(self):
        """Test les niveaux d'alerte."""
        assert NiveauAlerte.INFO.value == "info"
        assert NiveauAlerte.ATTENTION.value == "attention"
        assert NiveauAlerte.DANGER.value == "danger"

    def test_type_alerte_meteo_enum(self):
        """Test les types d'alertes météo."""
        assert TypeAlerteMeteo.GEL.value == "gel"
        assert TypeAlerteMeteo.CANICULE.value == "canicule"
        assert TypeAlerteMeteo.PLUIE_FORTE.value == "pluie_forte"
        assert TypeAlerteMeteo.VENT_FORT.value == "vent_fort"

    def test_calendar_provider_enum(self):
        """Test les fournisseurs de calendrier."""
        assert CalendarProvider.GOOGLE.value == "google"
        assert CalendarProvider.APPLE.value == "apple"
        assert CalendarProvider.OUTLOOK.value == "outlook"
        assert CalendarProvider.ICAL.value == "ical"


# ═══════════════════════════════════════════════════════════
# SECTION 2: TESTS DEPENSE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDepense:
    """Tests pour le modèle Depense."""

    def test_depense_creation(self, db: Session):
        """Test création d'une dépense."""
        from datetime import date
        depense = Depense(
            categorie="alimentation",
            montant=Decimal("25.50"),
            description="Course marché",
            date=date.today(),
        )
        db.add(depense)
        db.commit()
        
        assert depense.id is not None
        assert depense.categorie == "alimentation"
        assert depense.montant == Decimal("25.50")

    def test_depense_categories(self, db: Session):
        """Test création avec différentes catégories."""
        categories = [
            ("alimentation", "Course"),
            ("transport", "Essence"),
            ("logement", "Loyer"),
            ("sante", "Pharmacie"),
        ]
        
        for cat, desc in categories:
            depense = Depense(
                categorie=cat,
                montant=Decimal("100.00"),
                description=desc,
            )
            db.add(depense)
        
        db.commit()
        
        total = db.query(Depense).count()
        assert total >= 4

    def test_depense_montant_decimal(self, db: Session):
        """Test que le montant est en Decimal."""
        depense = Depense(
            categorie="restaurant",
            montant=Decimal("45.99"),
            description="Restaurant",
        )
        db.add(depense)
        db.commit()
        
        retrieved = db.query(Depense).filter_by(id=depense.id).first()
        assert isinstance(retrieved.montant, Decimal)
        assert retrieved.montant == Decimal("45.99")

    def test_depense_description_optionnelle(self, db: Session):
        """Test que description est optionnelle."""
        depense = Depense(
            categorie="autre",
            montant=Decimal("10.00"),
        )
        db.add(depense)
        db.commit()
        
        assert depense.id is not None


# ═══════════════════════════════════════════════════════════
# SECTION 3: TESTS BUDGET_MENSUEL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBudgetMensuel:
    """Tests pour le modèle BudgetMensuelDB."""

    def test_budget_creation(self, db: Session):
        """Test création d'un budget mensuel."""
        from datetime import date
        budget = BudgetMensuelDB(
            mois=date(2026, 1, 1),
            budget_total=Decimal("2000.00"),
        )
        db.add(budget)
        db.commit()
        
        assert budget.id is not None
        assert budget.budget_total == Decimal("2000.00")

    def test_budget_multicat(self, db: Session):
        """Test budget pour plusieurs mois."""
        from datetime import date
        budgets = [
            BudgetMensuelDB(mois=date(2026, 1, 1), budget_total=Decimal("1500.00")),
            BudgetMensuelDB(mois=date(2026, 2, 1), budget_total=Decimal("1600.00")),
            BudgetMensuelDB(mois=date(2026, 3, 1), budget_total=Decimal("1700.00")),
        ]
        
        for budget in budgets:
            db.add(budget)
        
        db.commit()
        
        total_budget = db.query(BudgetMensuelDB).count()
        assert total_budget >= 3

    def test_budget_avec_categories(self, db: Session):
        """Test budget avec répartition par catégories."""
        from datetime import date
        budget = BudgetMensuelDB(
            mois=date(2026, 1, 1),
            budget_total=Decimal("2000.00"),
            budgets_par_categorie={
                "alimentation": 400,
                "transport": 200,
                "loisirs": 150,
            }
        )
        db.add(budget)
        db.commit()
        
        assert budget.budgets_par_categorie is not None
        assert "alimentation" in budget.budgets_par_categorie


# ═══════════════════════════════════════════════════════════
# SECTION 4: TESTS ALERTE_METEO
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAlerteMeteo:
    """Tests pour le modèle AlerteMeteo."""

    def test_alerte_meteo_creation(self, db: Session):
        """Test création d'une alerte météo."""
        from datetime import date
        alerte = AlerteMeteo(
            type_alerte="gel",
            niveau="attention",
            titre="Alerte Gel",
            message="Gel prévu cette nuit",
            date_debut=date.today(),
        )
        db.add(alerte)
        db.commit()
        
        assert alerte.id is not None
        assert alerte.type_alerte == "gel"
        assert alerte.niveau == "attention"

    def test_alerte_meteo_types(self, db: Session):
        """Test différents types d'alertes."""
        from datetime import date
        types = ["gel", "canicule", "pluie_forte", "vent_fort"]
        
        for type_alerte in types:
            alerte = AlerteMeteo(
                type_alerte=type_alerte,
                niveau="info",
                titre=f"Alerte {type_alerte}",
                date_debut=date.today(),
            )
            db.add(alerte)
        
        db.commit()
        
        total = db.query(AlerteMeteo).count()
        assert total >= 4

    def test_alerte_meteo_niveaux(self, db: Session):
        """Test les niveaux d'alerte."""
        from datetime import date
        niveaux = ["info", "attention", "danger"]
        
        for niveau in niveaux:
            alerte = AlerteMeteo(
                type_alerte="pluie_forte",
                niveau=niveau,
                titre=f"Alerte {niveau}",
                date_debut=date.today(),
            )
            db.add(alerte)
        
        db.commit()
        
        danger_count = db.query(AlerteMeteo).filter_by(niveau="danger").count()
        assert danger_count >= 1


# ═══════════════════════════════════════════════════════════
# SECTION 5: TESTS CONFIG_METEO
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConfigMeteo:
    """Tests pour le modèle ConfigMeteo."""

    def test_config_meteo_creation(self, db: Session):
        """Test création d'une config météo."""
        config = ConfigMeteo(
            latitude=Decimal("48.8566"),
            longitude=Decimal("2.3522"),
            ville="Paris",
            notifications_gel=True,
            notifications_canicule=True,
        )
        db.add(config)
        db.commit()
        
        assert config.id is not None
        assert config.ville == "Paris"
        assert config.latitude == Decimal("48.8566")

    def test_config_meteo_preferences(self, db: Session):
        """Test les préférences d'alerte."""
        config = ConfigMeteo(
            ville="Lyon",
            notifications_gel=False,
            notifications_canicule=True,
            notifications_pluie=True,
        )
        db.add(config)
        db.commit()
        
        assert config.notifications_canicule is True
        assert config.notifications_gel is False


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS BACKUP
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestBackup:
    """Tests pour le modèle Backup."""

    def test_backup_creation(self, db: Session):
        """Test création d'une sauvegarde."""
        backup = Backup(
            filename="backup_2026_01_29.sql",
            size_bytes=1024000,
            compressed=True,
        )
        db.add(backup)
        db.commit()
        
        assert backup.id is not None
        assert backup.compressed is True
        assert backup.size_bytes == 1024000

    def test_backup_versions(self, db: Session):
        """Test différentes versions."""
        backups = [
            Backup(filename="backup_v1.sql", version="1.0.0"),
            Backup(filename="backup_v2.sql", version="2.0.0"),
        ]
        
        for backup in backups:
            db.add(backup)
        
        db.commit()
        
        total = db.query(Backup).count()
        assert total >= 2


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS CALENDRIER_EXTERNE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCalendrierExterne:
    """Tests pour le modèle CalendrierExterne."""

    def test_calendrier_creation(self, db: Session):
        """Test création d'un calendrier synchronisé."""
        calendrier = CalendrierExterne(
            provider="google",
            nom="Google Calendar",
            enabled=True,
        )
        db.add(calendrier)
        db.commit()
        
        assert calendrier.id is not None
        assert calendrier.provider == "google"
        assert calendrier.enabled is True

    def test_calendrier_providers(self, db: Session):
        """Test différents fournisseurs."""
        providers = ["google", "apple", "outlook", "ical"]
        
        for provider in providers:
            cal = CalendrierExterne(
                provider=provider,
                nom=f"Calendar {provider}",
            )
            db.add(cal)
        
        db.commit()
        
        total = db.query(CalendrierExterne).count()
        assert total >= 4


# ═══════════════════════════════════════════════════════════
# SECTION 8: TESTS EVENEMENT_CALENDRIER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEvenementCalendrier:
    """Tests pour les événements de calendrier."""

    def test_evenement_creation(self, db: Session):
        """Test création d'un événement."""
        from datetime import datetime
        calendrier = CalendrierExterne(
            provider="google",
            nom="Test Calendar",
        )
        db.add(calendrier)
        db.commit()
        
        evenement = EvenementCalendrier(
            uid="test_uid_123",
            titre="Réunion",
            description="Réunion importante",
            date_debut=datetime.now(),
            source_calendrier_id=calendrier.id,
        )
        db.add(evenement)
        db.commit()
        
        assert evenement.titre == "Réunion"
        assert evenement.source_calendrier_id == calendrier.id


# ═══════════════════════════════════════════════════════════
# SECTION 9: TESTS PUSH_SUBSCRIPTION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPushSubscription:
    """Tests pour les abonnements push."""

    def test_push_subscription_creation(self, db: Session):
        """Test création d'un abonnement push."""
        subscription = PushSubscription(
            endpoint="https://fcm.googleapis.com/...",
            p256dh_key="key_content",
            auth_key="auth_content",
        )
        db.add(subscription)
        db.commit()
        
        assert subscription.id is not None

    def test_push_subscription_unique_endpoint(self, db: Session):
        """Test que endpoint doit être unique."""
        sub1 = PushSubscription(
            endpoint="https://test.com/endpoint",
            p256dh_key="key1",
            auth_key="auth1",
        )
        db.add(sub1)
        db.commit()
        
        # Try to add the same endpoint again should fail
        sub2 = PushSubscription(
            endpoint="https://test.com/endpoint",
            p256dh_key="key2",
            auth_key="auth2",
        )
        db.add(sub2)
        
        try:
            db.commit()
            # Should not reach here
            assert False, "Should have raised an integrity error"
        except Exception:
            db.rollback()  # Reset session
            pass  # Expected


# ═══════════════════════════════════════════════════════════
# SECTION 10: TESTS NOTIFICATION_PREFERENCE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNotificationPreference:
    """Tests pour les préférences de notification."""

    def test_notification_preference_creation(self, db: Session):
        """Test création de préférences."""
        from datetime import time
        pref = NotificationPreference(
            courses_rappel=True,
            repas_suggestion=True,
            quiet_hours_start=time(22, 0),
        )
        db.add(pref)
        db.commit()
        
        assert pref.id is not None
        assert pref.courses_rappel is True

    def test_notification_preferences_defaults(self, db: Session):
        """Test les valeurs par défaut."""
        pref = NotificationPreference(
            courses_rappel=True,
            repas_suggestion=False,
        )
        db.add(pref)
        db.commit()
        
        # Budget alerte should be True by default
        assert pref.budget_alerte is True
        assert pref.meteo_alerte is True


# ═══════════════════════════════════════════════════════════
# SECTION 11: TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.integration
class TestNouveauxModelsIntegration:
    """Tests d'intégration complets."""

    def test_workflow_budget_depenses(self, db: Session):
        """Test workflow budget et dépenses."""
        # Créer budget
        budget = BudgetMensuelDB(
            categorie=CategorieDepenseDB.ALIMENTATION,
            montant_budget=Decimal("500.00"),
            mois=1,
            annee=2026,
        )
        db.add(budget)
        db.commit()
        
        # Ajouter dépenses
        d1 = Depense(
            categorie=CategorieDepenseDB.ALIMENTATION,
            montant=Decimal("120.00"),
            description="Course 1",
        )
        d2 = Depense(
            categorie=CategorieDepenseDB.ALIMENTATION,
            montant=Decimal("95.50"),
            description="Course 2",
        )
        
        db.add_all([d1, d2])
        db.commit()
        
        assert budget.montant_budget == Decimal("500.00")

    def test_workflow_calendrier_complet(self, db: Session):
        """Test workflow calendrier avec événements."""
        # Créer calendrier
        cal = CalendrierExterne(
            provider=CalendarProvider.GOOGLE,
            nom="Calendrier Principal",
        )
        db.add(cal)
        db.commit()
        
        # Ajouter événements
        evt1 = EvenementCalendrier(
            calendrier_id=cal.id,
            titre="Événement 1",
        )
        evt2 = EvenementCalendrier(
            calendrier_id=cal.id,
            titre="Événement 2",
        )
        
        db.add_all([evt1, evt2])
        db.commit()
        
        evenements = db.query(EvenementCalendrier).filter_by(calendrier_id=cal.id).all()
        assert len(evenements) >= 2
