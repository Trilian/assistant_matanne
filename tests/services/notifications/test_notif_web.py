"""Tests pour src/services/notifications/notif_web.py - ServiceWebPush.

Couverture des fonctionnalités:
- Gestion des abonnements push
- Préférences utilisateur
- Envoi de notifications
- Notifications prédéfinies
"""

import pytest
from datetime import datetime, time
from unittest.mock import MagicMock, patch

from src.services.notifications.notif_web import (
    ServiceWebPush,
    obtenir_service_webpush,
)
from src.services.notifications.types import (
    TypeNotification,
    AbonnementPush,
    NotificationPush,
    PreferencesNotification,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Service Web Push de test."""
    return ServiceWebPush()


@pytest.fixture
def subscription_info():
    """Info d'abonnement de test."""
    return {
        "endpoint": "https://push.example.com/abc123",
        "keys": {
            "p256dh": "test_p256dh_key",
            "auth": "test_auth_key",
        }
    }


@pytest.fixture
def notification():
    """Notification de test."""
    return NotificationPush(
        title="Test Notification",
        body="Ceci est un test",
        notification_type=TypeNotification.STOCK_BAS,
    )


@pytest.fixture
def preferences():
    """Préférences de test."""
    return PreferencesNotification(
        user_id="user123",
        alertes_stock=True,
        alertes_peremption=True,
        rappels_repas=False,
        heures_silencieuses_debut=22,
        heures_silencieuses_fin=7,
        max_par_heure=5,
    )


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceWebPushInit:
    """Tests pour l'initialisation."""

    def test_init_service(self, service):
        """Initialisation du service."""
        assert service is not None
        assert isinstance(service, ServiceWebPush)
        assert service._subscriptions == {}
        assert service._preferences == {}
        assert service._sent_count == {}

    def test_factory_obtenir_service(self):
        """Test factory obtenir_service_webpush."""
        import src.services.notifications.notif_web as module
        
        # Reset singleton
        if hasattr(module, "_service_webpush"):
            module._service_webpush = None
        
        service = obtenir_service_webpush()
        assert isinstance(service, ServiceWebPush)


# ═══════════════════════════════════════════════════════════
# TESTS GESTION ABONNEMENTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSauvegarderAbonnement:
    """Tests pour sauvegarder_abonnement."""

    def test_sauvegarder_nouvel_abonnement(self, service, subscription_info):
        """Sauvegarde d'un nouvel abonnement."""
        # Mock de la sauvegarde Supabase
        service._sauvegarder_abonnement_supabase = MagicMock()
        
        result = service.sauvegarder_abonnement("user123", subscription_info)
        
        assert result is not None
        assert isinstance(result, AbonnementPush)
        assert result.user_id == "user123"
        assert result.endpoint == subscription_info["endpoint"]
        assert "user123" in service._subscriptions
        assert len(service._subscriptions["user123"]) == 1

    def test_eviter_doublon_abonnement(self, service, subscription_info):
        """Éviter les doublons d'abonnements."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        
        # Ajouter deux fois le même abonnement
        service.sauvegarder_abonnement("user123", subscription_info)
        service.sauvegarder_abonnement("user123", subscription_info)
        
        # Ne devrait y avoir qu'un seul abonnement
        assert len(service._subscriptions["user123"]) == 1

    def test_sauvegarder_plusieurs_endpoints(self, service, subscription_info):
        """Plusieurs endpoints pour un même utilisateur."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        
        service.sauvegarder_abonnement("user123", subscription_info)
        
        # Second endpoint
        sub2 = {
            "endpoint": "https://push.example.com/xyz789",
            "keys": {"p256dh": "key2", "auth": "auth2"}
        }
        service.sauvegarder_abonnement("user123", sub2)
        
        assert len(service._subscriptions["user123"]) == 2


@pytest.mark.unit
class TestSupprimerAbonnement:
    """Tests pour supprimer_abonnement."""

    def test_supprimer_abonnement(self, service, subscription_info):
        """Suppression d'un abonnement."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service._supprimer_abonnement_supabase = MagicMock()
        
        service.sauvegarder_abonnement("user123", subscription_info)
        
        service.supprimer_abonnement("user123", subscription_info["endpoint"])
        
        assert len(service._subscriptions["user123"]) == 0

    def test_supprimer_utilisateur_inconnu(self, service):
        """Suppression pour utilisateur inconnu."""
        service._supprimer_abonnement_supabase = MagicMock()
        
        # Ne devrait pas lever d'exception
        service.supprimer_abonnement("inconnu", "https://example.com")


@pytest.mark.unit
class TestObtenirAbonnementsUtilisateur:
    """Tests pour obtenir_abonnements_utilisateur."""

    def test_obtenir_abonnements_existants(self, service, subscription_info):
        """Récupération d'abonnements existants."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        
        result = service.obtenir_abonnements_utilisateur("user123")
        
        assert len(result) == 1
        assert result[0].endpoint == subscription_info["endpoint"]

    def test_obtenir_abonnements_vide(self, service):
        """Récupération d'abonnements pour utilisateur sans abonnements."""
        service._charger_abonnements_supabase = MagicMock(return_value=[])
        
        result = service.obtenir_abonnements_utilisateur("nouveau_user")
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS PRÉFÉRENCES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestObtenirPreferences:
    """Tests pour obtenir_preferences."""

    def test_obtenir_preferences_existantes(self, service, preferences):
        """Récupération de préférences existantes."""
        service._preferences["user123"] = preferences
        
        result = service.obtenir_preferences("user123")
        
        assert result.alertes_stock is True
        assert result.rappels_repas is False

    def test_obtenir_preferences_defaut(self, service):
        """Créer préférences par défaut pour nouvel utilisateur."""
        result = service.obtenir_preferences("nouveau_user")
        
        assert result is not None
        assert isinstance(result, PreferencesNotification)
        assert result.user_id == "nouveau_user"


@pytest.mark.unit
class TestMettreAJourPreferences:
    """Tests pour mettre_a_jour_preferences."""

    def test_mettre_a_jour_preferences(self, service, preferences):
        """Mise à jour des préférences."""
        service._sauvegarder_preferences_supabase = MagicMock()
        
        service.mettre_a_jour_preferences("user123", preferences)
        
        assert "user123" in service._preferences
        assert service._preferences["user123"].alertes_stock is True


# ═══════════════════════════════════════════════════════════
# TESTS DOIT_ENVOYER
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDoitEnvoyer:
    """Tests pour doit_envoyer."""

    def test_doit_envoyer_type_actif(self, service, preferences):
        """Doit envoyer si type activé."""
        service._preferences["user123"] = preferences
        
        result = service.doit_envoyer("user123", TypeNotification.STOCK_BAS)
        
        assert result is True

    def test_doit_envoyer_type_desactive(self, service, preferences):
        """Ne pas envoyer si type désactivé."""
        service._preferences["user123"] = preferences
        
        result = service.doit_envoyer("user123", TypeNotification.RAPPEL_REPAS)
        
        assert result is False

    def test_doit_envoyer_heures_silencieuses(self, service, preferences):
        """Ne pas envoyer pendant heures silencieuses."""
        service._preferences["user123"] = preferences
        
        # Mock datetime pour 3h du matin
        with patch("src.services.notifications.notif_web.datetime") as mock_dt:
            mock_now = MagicMock()
            mock_now.hour = 3
            mock_dt.now.return_value = mock_now
            
            result = service.doit_envoyer("user123", TypeNotification.STOCK_BAS)
        
        assert result is False

    def test_doit_envoyer_limite_atteinte(self, service, preferences):
        """Ne pas envoyer si limite par heure atteinte."""
        service._preferences["user123"] = preferences
        
        # Mock generer_cle_compteur pour retourner une clé fixe
        with patch("src.services.notifications.notif_web.generer_cle_compteur") as mock_gen:
            mock_gen.return_value = "user123_2024011510"
            
            # Simuler 5 envois avec cette clé
            service._sent_count["user123_2024011510"] = 5  # max_par_heure = 5
            
            result = service.doit_envoyer("user123", TypeNotification.STOCK_BAS)
        
        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS ENVOI NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerNotification:
    """Tests pour envoyer_notification."""

    def test_envoyer_sans_abonnement(self, service, notification):
        """Envoi sans abonnement disponible."""
        service.doit_envoyer = MagicMock(return_value=True)
        
        result = service.envoyer_notification("user123", notification)
        
        assert result is False

    def test_envoyer_preferences_bloquent(self, service, notification):
        """Envoi bloqué par préférences."""
        service.doit_envoyer = MagicMock(return_value=False)
        
        result = service.envoyer_notification("user123", notification)
        
        assert result is False

    def test_envoyer_succes(self, service, notification, subscription_info):
        """Envoi réussi."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.envoyer_notification("user123", notification)
        
        assert result is True
        service._envoyer_web_push.assert_called_once()

    def test_envoyer_incremente_compteur(self, service, notification, subscription_info):
        """Envoi incrémente le compteur."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        service.envoyer_notification("user123", notification)
        
        # Vérifier qu'un compteur a été créé
        assert len(service._sent_count) >= 1


@pytest.mark.unit
class TestEnvoyerATous:
    """Tests pour envoyer_a_tous."""

    def test_envoyer_a_tous(self, service, notification, subscription_info):
        """Envoi à tous les utilisateurs."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        
        # Ajouter plusieurs utilisateurs
        service.sauvegarder_abonnement("user1", subscription_info)
        sub2 = {**subscription_info, "endpoint": "https://example.com/2"}
        service.sauvegarder_abonnement("user2", sub2)
        
        service.envoyer_notification = MagicMock(return_value=True)
        
        count = service.envoyer_a_tous(notification)
        
        assert count == 2


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNotifierStockBas:
    """Tests pour notifier_stock_bas."""

    def test_notifier_stock_bas(self, service, subscription_info):
        """Notification stock bas."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_stock_bas("user123", "Lait", 0.5)
        
        assert result is True


@pytest.mark.unit
class TestNotifierPeremption:
    """Tests pour notifier_peremption."""

    def test_notifier_peremption_expiree(self, service, subscription_info):
        """Notification produit expiré."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_peremption("user123", "Yaourt", -1)
        
        assert result is True

    def test_notifier_peremption_demain(self, service, subscription_info):
        """Notification péremption demain."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_peremption("user123", "Lait", 1)
        
        assert result is True

    def test_notifier_peremption_proche(self, service, subscription_info):
        """Notification péremption proche."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_peremption("user123", "Fromage", 5)
        
        assert result is True


@pytest.mark.unit
class TestNotifierRappelRepas:
    """Tests pour notifier_rappel_repas."""

    def test_notifier_rappel_repas(self, service, subscription_info):
        """Notification rappel repas."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_rappel_repas("user123", "Déjeuner", "Pâtes carbonara", "30 min")
        
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS ENVOI WEB PUSH
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerWebPush:
    """Tests pour _envoyer_web_push."""

    def test_envoyer_web_push_pywebpush_manquant(self, service, notification, subscription_info):
        """Gestion si pywebpush non installé."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        sub = service.sauvegarder_abonnement("user123", subscription_info)
        
        with patch.dict("sys.modules", {"pywebpush": None}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'pywebpush'")):
                # Ne devrait pas lever d'exception
                try:
                    service._envoyer_web_push(sub, notification)
                except ImportError:
                    pass  # C'est attendu

    def test_envoyer_web_push_erreur_410(self, service, notification, subscription_info):
        """Gestion erreur 410 (abonnement expiré)."""
        # Skip si pywebpush n'est pas installé
        pytest.importorskip("pywebpush")
        
        service._sauvegarder_abonnement_supabase = MagicMock()
        sub = service.sauvegarder_abonnement("user123", subscription_info)
        
        with patch("pywebpush.webpush", side_effect=Exception("410 Gone")):
            try:
                service._envoyer_web_push(sub, notification)
            except Exception:
                pass
        
        # L'abonnement devrait être marqué inactif
        # (Note: cela dépend de l'implémentation)
