"""
Tests unitaires pour notifications.py

Module: src.core.models.notifications
Contient: PushSubscription, NotificationPreference
"""

from datetime import time

from src.core.models.notifications import (
    NotificationPreference,
    PushSubscription,
)

# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestPushSubscription:
    """Tests pour le modèle PushSubscription."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert PushSubscription.__tablename__ == "push_subscriptions"

    def test_creation_instance(self):
        """Test de création d'une subscription."""
        sub = PushSubscription(
            endpoint="https://push.example.com/abc123",
            p256dh_key="key123",
            auth_key="auth456",
        )
        assert sub.endpoint == "https://push.example.com/abc123"
        assert sub.p256dh_key == "key123"
        assert sub.auth_key == "auth456"

    def test_repr(self):
        """Test de la représentation string."""
        sub = PushSubscription(id=1, endpoint="https://test", p256dh_key="k", auth_key="a")
        result = repr(sub)
        assert "PushSubscription" in result


class TestNotificationPreference:
    """Tests pour le modèle NotificationPreference."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert NotificationPreference.__tablename__ == "notification_preferences"

    def test_creation_instance(self):
        """Test de création des préférences."""
        pref = NotificationPreference(
            courses_rappel=True,
            repas_suggestion=False,
            stock_alerte=True,
        )
        assert pref.courses_rappel is True
        assert pref.repas_suggestion is False
        assert pref.stock_alerte is True

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = NotificationPreference.__table__.columns
        # Toutes les notifications activées par défaut
        assert colonnes["courses_rappel"].default is not None
        assert colonnes["repas_suggestion"].default is not None
        assert colonnes["stock_alerte"].default is not None
        assert colonnes["meteo_alerte"].default is not None
        assert colonnes["budget_alerte"].default is not None
        # Heures silencieuses par défaut
        assert colonnes["quiet_hours_start"].default is not None
        assert colonnes["quiet_hours_end"].default is not None

    def test_heures_silencieuses_personnalisees(self):
        """Test des heures silencieuses personnalisées."""
        pref = NotificationPreference(
            quiet_hours_start=time(23, 0),
            quiet_hours_end=time(6, 30),
        )
        assert pref.quiet_hours_start == time(23, 0)
        assert pref.quiet_hours_end == time(6, 30)

    def test_repr(self):
        """Test de la représentation string."""
        pref = NotificationPreference(id=1)
        result = repr(pref)
        assert "NotificationPreference" in result
