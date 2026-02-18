"""
Tests pour NotificationJeuxService - Gestion des notifications jeux.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.services.jeux.notification_service import (
    NiveauUrgence,
    NotificationJeux,
    NotificationJeuxService,
    TypeNotification,
    afficher_badge_notifications,
    afficher_liste_notifications,
    afficher_notification,
    get_notification_jeux_service,
)
from src.services.jeux.series_service import SEUIL_VALUE_ALERTE, SEUIL_VALUE_HAUTE

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def storage():
    """Dict servant de stockage en lieu de st.session_state."""
    return {}


@pytest.fixture
def service(storage):
    """Instance du service de notifications."""
    return NotificationJeuxService(storage=storage)


@pytest.fixture
def notification_exemple():
    """Une notification exemple."""
    return NotificationJeux(
        id="test_123",
        type=TypeNotification.OPPORTUNITE,
        titre="Test Notification",
        message="Message de test",
        urgence=NiveauUrgence.MOYENNE,
        type_jeu="paris",
        metadata={"value": 2.5},
    )


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION DATACLASS
# ═══════════════════════════════════════════════════════════


class TestNotificationJeux:
    """Tests de la dataclass NotificationJeux."""

    def test_creation(self, notification_exemple):
        """La notification est créée correctement."""
        assert notification_exemple.id == "test_123"
        assert notification_exemple.type == TypeNotification.OPPORTUNITE
        assert notification_exemple.lue is False

    def test_icone(self):
        """L'icône correspond au type."""
        notif = NotificationJeux(
            id="1",
            type=TypeNotification.ALERTE,
            titre="",
            message="",
            urgence=NiveauUrgence.HAUTE,
            type_jeu="paris",
        )
        assert notif.icone == "⚠️"

    def test_couleur_urgence(self):
        """La couleur correspond à l'urgence."""
        notif_haute = NotificationJeux(
            id="1",
            type=TypeNotification.INFO,
            titre="",
            message="",
            urgence=NiveauUrgence.HAUTE,
            type_jeu="paris",
        )
        assert "#FF4B4B" in notif_haute.couleur

        notif_basse = NotificationJeux(
            id="2",
            type=TypeNotification.INFO,
            titre="",
            message="",
            urgence=NiveauUrgence.BASSE,
            type_jeu="paris",
        )
        assert "#00C851" in notif_basse.couleur


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE CRÉATION
# ═══════════════════════════════════════════════════════════


class TestCreerNotification:
    """Tests de création de notifications."""

    def test_creer_notification_simple(self, service):
        """Créer une notification simple."""
        notif = service.creer_notification(
            type=TypeNotification.INFO,
            titre="Test",
            message="Message test",
            type_jeu="global",
        )

        assert notif.titre == "Test"
        assert notif.type == TypeNotification.INFO
        assert notif.urgence == NiveauUrgence.BASSE

    def test_creer_notification_ajoute_session(self, service):
        """La notification est ajoutée à la session."""
        service.creer_notification(
            type=TypeNotification.INFO,
            titre="Test",
            message="Message",
            type_jeu="paris",
        )

        assert len(service.notifications) == 1

    def test_limite_notifications(self, service):
        """Les notifications sont limitées."""
        # Créer plus que la limite
        for i in range(service.MAX_NOTIFICATIONS + 10):
            service.creer_notification(
                type=TypeNotification.INFO,
                titre=f"Test {i}",
                message="Message",
                type_jeu="paris",
            )

        assert len(service.notifications) <= service.MAX_NOTIFICATIONS


class TestCreerAlerteOpportunite:
    """Tests de création d'alertes opportunité."""

    def test_opportunite_haute(self, service):
        """Opportunité avec value haute = urgence haute."""
        notif = service.creer_alerte_opportunite(
            identifiant="More_2_5",
            value=SEUIL_VALUE_HAUTE + 0.5,
            serie=15,
            type_jeu="paris",
        )

        assert notif.urgence == NiveauUrgence.HAUTE
        assert "🟢" in notif.message

    def test_opportunite_moyenne(self, service):
        """Opportunité avec value moyenne = urgence moyenne."""
        notif = service.creer_alerte_opportunite(
            identifiant="BTTS_Yes",
            value=SEUIL_VALUE_ALERTE + 0.1,
            serie=10,
            type_jeu="paris",
        )

        assert notif.urgence == NiveauUrgence.MOYENNE
        assert "🟡" in notif.message

    def test_opportunite_metadata(self, service):
        """Les metadata sont correctement stockées."""
        notif = service.creer_alerte_opportunite(
            identifiant="Numéro7",
            value=2.8,
            serie=28,
            type_jeu="loto",
        )

        assert notif.metadata["value"] == 2.8
        assert notif.metadata["serie"] == 28


class TestCreerAlerteSync:
    """Tests de création d'alertes de synchronisation."""

    def test_sync_succes(self, service):
        """Sync réussie = notification basse."""
        notif = service.creer_alerte_sync(
            type_jeu="paris",
            succes=True,
            nb_maj=50,
            nb_alertes=3,
        )

        assert "✅" in notif.titre
        assert notif.urgence == NiveauUrgence.BASSE

    def test_sync_echec(self, service):
        """Sync échouée = notification haute."""
        notif = service.creer_alerte_sync(
            type_jeu="loto",
            succes=False,
            erreur="Timeout API",
        )

        assert "❌" in notif.titre
        assert notif.urgence == NiveauUrgence.HAUTE


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE LECTURE
# ═══════════════════════════════════════════════════════════


class TestLectureNotifications:
    """Tests de lecture des notifications."""

    def test_obtenir_non_lues(self, service):
        """Obtenir seulement les non lues."""
        # Créer 3 notifications
        for i in range(3):
            service.creer_notification(
                type=TypeNotification.INFO,
                titre=f"Test {i}",
                message="",
                type_jeu="paris",
            )

        # Marquer une comme lue
        service.notifications[0].lue = True

        non_lues = service.obtenir_non_lues()
        assert len(non_lues) == 2

    def test_obtenir_par_type(self, service):
        """Filtrer par type."""
        service.creer_notification(
            type=TypeNotification.OPPORTUNITE,
            titre="Opp",
            message="",
            type_jeu="paris",
        )
        service.creer_notification(
            type=TypeNotification.SYNC,
            titre="Sync",
            message="",
            type_jeu="paris",
        )

        opps = service.obtenir_par_type(TypeNotification.OPPORTUNITE)
        assert len(opps) == 1
        assert opps[0].titre == "Opp"

    def test_obtenir_par_jeu(self, service):
        """Filtrer par type de jeu."""
        service.creer_notification(
            type=TypeNotification.INFO,
            titre="Paris",
            message="",
            type_jeu="paris",
        )
        service.creer_notification(
            type=TypeNotification.INFO,
            titre="Loto",
            message="",
            type_jeu="loto",
        )

        paris = service.obtenir_par_jeu("paris")
        assert len(paris) == 1
        assert paris[0].titre == "Paris"

    def test_compter_non_lues(self, service):
        """Compter les non lues."""
        for i in range(5):
            service.creer_notification(
                type=TypeNotification.INFO,
                titre=f"Test {i}",
                message="",
                type_jeu="paris",
            )

        assert service.compter_non_lues() == 5


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE ACTIONS
# ═══════════════════════════════════════════════════════════


class TestActionsNotifications:
    """Tests des actions sur les notifications."""

    def test_marquer_lue(self, service):
        """Marquer une notification comme lue."""
        notif = service.creer_notification(
            type=TypeNotification.INFO,
            titre="Test",
            message="",
            type_jeu="paris",
        )

        result = service.marquer_lue(notif.id)

        assert result is True
        assert notif.lue is True

    def test_marquer_lue_introuvable(self, service):
        """Marquer lue une notification inexistante."""
        result = service.marquer_lue("inexistant_123")
        assert result is False

    def test_marquer_toutes_lues(self, service):
        """Marquer toutes comme lues."""
        for i in range(5):
            service.creer_notification(
                type=TypeNotification.INFO,
                titre=f"Test {i}",
                message="",
                type_jeu="paris",
            )

        count = service.marquer_toutes_lues()

        assert count == 5
        assert service.compter_non_lues() == 0

    def test_supprimer(self, service):
        """Supprimer une notification."""
        notif = service.creer_notification(
            type=TypeNotification.INFO,
            titre="Test",
            message="",
            type_jeu="paris",
        )

        result = service.supprimer(notif.id)

        assert result is True
        assert len(service.notifications) == 0

    def test_vider(self, service):
        """Vider toutes les notifications."""
        for i in range(5):
            service.creer_notification(
                type=TypeNotification.INFO,
                titre=f"Test {i}",
                message="",
                type_jeu="paris",
            )

        count = service.vider()

        assert count == 5
        assert len(service.notifications) == 0


# ═══════════════════════════════════════════════════════════
# TESTS TYPES ÉNUMÉRATIONS
# ═══════════════════════════════════════════════════════════


class TestEnumerations:
    """Tests des énumérations."""

    def test_type_notification_valeurs(self):
        """Tous les types de notification existent."""
        assert TypeNotification.OPPORTUNITE.value == "opportunite"
        assert TypeNotification.ALERTE.value == "alerte"
        assert TypeNotification.SYNC.value == "sync"
        assert TypeNotification.RAPPEL.value == "rappel"
        assert TypeNotification.INFO.value == "info"

    def test_niveau_urgence_valeurs(self):
        """Tous les niveaux d'urgence existent."""
        assert NiveauUrgence.HAUTE.value == "haute"
        assert NiveauUrgence.MOYENNE.value == "moyenne"
        assert NiveauUrgence.BASSE.value == "basse"


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


class TestNotificationFactory:
    """Tests de la factory."""

    def test_get_notification_jeux_service(self):
        """Factory retourne une instance."""
        import src.services.jeux._internal.notification_service as module

        # Inject a pre-built instance so the factory never calls _get_default_storage()
        module._notification_service_instance = NotificationJeuxService(storage={})

        try:
            service = get_notification_jeux_service()
            assert isinstance(service, NotificationJeuxService)
        finally:
            module._notification_service_instance = None
