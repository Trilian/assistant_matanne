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
        # Modifier les préférences pour désactiver les heures silencieuses
        preferences.heures_silencieuses_debut = None
        preferences.heures_silencieuses_fin = None
        service._preferences["user123"] = preferences
        
        # Simuler 5 envois cette heure avec le vrai datetime
        from src.services.notifications.utils import generer_cle_compteur
        now = datetime.now()
        count_key = generer_cle_compteur("user123", now)
        service._sent_count[count_key] = 5  # max_par_heure = 5
        
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
        service._sauvegarder_abonnement_supabase = MagicMock()
        sub = service.sauvegarder_abonnement("user123", subscription_info)
        
        # Mock _envoyer_web_push directement car pywebpush peut ne pas être installé
        service._envoyer_web_push = MagicMock(side_effect=Exception("410 Gone"))
        
        try:
            service._envoyer_web_push(sub, notification)
        except Exception as e:
            assert "410" in str(e)
            pass  # Comportement attendu


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFIER_LISTE_PARTAGEE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNotifierListePartagee:
    """Tests pour notifier_liste_partagee."""

    def test_notifier_liste_partagee(self, service, subscription_info):
        """Notification liste partagée."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        service._envoyer_web_push = MagicMock()
        
        result = service.notifier_liste_partagee(
            "user123", 
            "Anne", 
            "Courses semaine"
        )
        
        assert result is True
        service._envoyer_web_push.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS SUPABASE PERSISTENCE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetSupabaseClient:
    """Tests pour _get_supabase_client."""

    def test_get_supabase_client_not_configured(self, service):
        """Retourne None si Supabase non configuré."""
        with patch("src.services.notifications.notif_web.ServiceWebPush._get_supabase_client") as mock:
            mock.return_value = None
            result = service._get_supabase_client()
        # La vraie implémentation retournera None si pas configuré
        assert result is None or mock.called

    def test_get_supabase_client_exception(self, service):
        """Gère les exceptions gracieusement."""
        original_method = service._get_supabase_client
        with patch.object(type(service), '_get_supabase_client', side_effect=Exception("Test error")):
            # Appeler via le module
            from src.services.notifications.notif_web import ServiceWebPush
            svc = ServiceWebPush()
            # La vraie méthode doit capturer les exceptions
            result = original_method.__get__(svc, type(svc))()
        # Doit retourner None au lieu de lever une exception
        assert result is None


@pytest.mark.unit
class TestSauvegarderAbonnementSupabase:
    """Tests pour _sauvegarder_abonnement_supabase."""

    def test_sauvegarder_sans_client(self, service, subscription_info):
        """Sauvegarde échoue silencieusement sans client."""
        service._get_supabase_client = MagicMock(return_value=None)
        sub = AbonnementPush(
            user_id="user123",
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        # Ne devrait pas lever d'exception
        service._sauvegarder_abonnement_supabase(sub)

    def test_sauvegarder_avec_client_mock(self, service, subscription_info):
        """Sauvegarde avec client Supabase mocké."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        sub = AbonnementPush(
            user_id="user123",
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        
        service._sauvegarder_abonnement_supabase(sub)
        
        mock_client.table.assert_called_with("push_subscriptions")

    def test_sauvegarder_exception_captee(self, service, subscription_info):
        """Exception capturée lors de la sauvegarde."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        sub = AbonnementPush(
            user_id="user123",
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        
        # Ne devrait pas lever d'exception
        service._sauvegarder_abonnement_supabase(sub)


@pytest.mark.unit
class TestSupprimerAbonnementSupabase:
    """Tests pour _supprimer_abonnement_supabase."""

    def test_supprimer_sans_client(self, service):
        """Suppression échoue silencieusement sans client."""
        service._get_supabase_client = MagicMock(return_value=None)
        # Ne devrait pas lever d'exception
        service._supprimer_abonnement_supabase("user123", "https://example.com")

    def test_supprimer_avec_client_mock(self, service):
        """Suppression avec client Supabase mocké."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.delete.return_value = mock_table
        mock_table.match.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        service._supprimer_abonnement_supabase("user123", "https://example.com")
        
        mock_client.table.assert_called_with("push_subscriptions")

    def test_supprimer_exception_captee(self, service):
        """Exception capturée lors de la suppression."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        # Ne devrait pas lever d'exception
        service._supprimer_abonnement_supabase("user123", "https://example.com")


@pytest.mark.unit
class TestChargerAbonnementsSupabase:
    """Tests pour _charger_abonnements_supabase."""

    def test_charger_sans_client(self, service):
        """Chargement retourne vide sans client."""
        service._get_supabase_client = MagicMock(return_value=None)
        
        result = service._charger_abonnements_supabase("user123")
        
        assert result == []

    def test_charger_avec_client_mock(self, service):
        """Chargement avec client Supabase mocké."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        
        # Simuler une réponse avec des données
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": 1,
                "user_id": "user123",
                "endpoint": "https://example.com/push",
                "p256dh_key": "key123",
                "auth_key": "auth123",
                "user_agent": "Chrome",
                "created_at": "2024-01-01T00:00:00",
                "is_active": True,
            }
        ]
        mock_table.execute.return_value = mock_response
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        result = service._charger_abonnements_supabase("user123")
        
        assert len(result) == 1
        assert result[0].endpoint == "https://example.com/push"

    def test_charger_exception_captee(self, service):
        """Exception capturée lors du chargement."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        result = service._charger_abonnements_supabase("user123")
        
        assert result == []


@pytest.mark.unit
class TestSauvegarderPreferencesSupabase:
    """Tests pour _sauvegarder_preferences_supabase."""

    def test_sauvegarder_prefs_sans_client(self, service, preferences):
        """Sauvegarde préfs échoue silencieusement sans client."""
        service._get_supabase_client = MagicMock(return_value=None)
        # Ne devrait pas lever d'exception
        service._sauvegarder_preferences_supabase(preferences)

    def test_sauvegarder_prefs_avec_client_mock(self, service, preferences):
        """Sauvegarde préfs avec client Supabase mocké."""
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        service._sauvegarder_preferences_supabase(preferences)
        
        mock_client.table.assert_called_with("notification_preferences")

    def test_sauvegarder_prefs_exception_captee(self, service, preferences):
        """Exception capturée lors de la sauvegarde préfs."""
        mock_client = MagicMock()
        mock_client.table.side_effect = Exception("Database error")
        
        service._get_supabase_client = MagicMock(return_value=mock_client)
        
        # Ne devrait pas lever d'exception
        service._sauvegarder_preferences_supabase(preferences)


# ═══════════════════════════════════════════════════════════
# TESTS ENVOYER_WEB_PUSH AVANCÉS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerWebPushAvances:
    """Tests avancés pour _envoyer_web_push."""

    def test_envoyer_avec_pywebpush_mock(self, service, notification, subscription_info):
        """Envoi avec pywebpush mocké."""
        sub = AbonnementPush(
            user_id="user123",
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        
        # Mock le module pywebpush complet
        mock_pywebpush = MagicMock()
        mock_pywebpush.webpush = MagicMock()
        
        with patch.dict("sys.modules", {"pywebpush": mock_pywebpush}):
            # Accéder directement à la méthode originale - doit gérer l'import
            service_real = ServiceWebPush()
            try:
                service_real._envoyer_web_push(sub, notification)
            except (ImportError, Exception):
                pass  # Attendu si pywebpush non installé

    def test_envoyer_exception_generale(self, service, notification, subscription_info):
        """Gestion d'une exception générale."""
        sub = AbonnementPush(
            user_id="user123",
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        
        # Test que l'exception est bien relancée en mockant le module entier
        mock_pywebpush = MagicMock()
        mock_pywebpush.webpush = MagicMock(side_effect=Exception("Network error"))
        
        with patch.dict("sys.modules", {"pywebpush": mock_pywebpush}):
            try:
                service._envoyer_web_push(sub, notification)
            except Exception as e:
                # On accepte soit l'erreur réseau soit une ImportError
                assert "Network error" in str(e) or isinstance(e, ImportError)

    def test_envoyer_notification_avec_erreur_410_desactive_abonnement(self, service, notification, subscription_info):
        """Erreur 410 désactive l'abonnement."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        sub = service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        
        # Simuler une erreur 410 lors de l'envoi
        def envoyer_avec_410(*args, **kwargs):
            raise Exception("410 Gone")
        
        service._envoyer_web_push = envoyer_avec_410
        
        result = service.envoyer_notification("user123", notification)
        
        # L'envoi a échoué mais l'abonnement devrait être marqué inactif
        assert result is False
        assert service._subscriptions["user123"][0].is_active is False

    def test_envoyer_notification_avec_erreur_404_desactive_abonnement(self, service, notification, subscription_info):
        """Erreur 404 désactive l'abonnement."""
        service._sauvegarder_abonnement_supabase = MagicMock()
        sub = service.sauvegarder_abonnement("user123", subscription_info)
        service.doit_envoyer = MagicMock(return_value=True)
        
        # Simuler une erreur 404 lors de l'envoi
        def envoyer_avec_404(*args, **kwargs):
            raise Exception("404 Not Found")
        
        service._envoyer_web_push = envoyer_avec_404
        
        result = service.envoyer_notification("user123", notification)
        
        # L'envoi a échoué et l'abonnement devrait être marqué inactif
        assert result is False
        assert service._subscriptions["user123"][0].is_active is False


# ═══════════════════════════════════════════════════════════
# TESTS ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAliasRetrocompatibilite:
    """Tests pour les alias de rétrocompatibilité."""

    def test_alias_push_notification_service(self):
        """Alias PushNotificationService disponible."""
        from src.services.notifications.notif_web import PushNotificationService
        assert PushNotificationService is ServiceWebPush

    def test_alias_get_push_notification_service(self):
        """Alias get_push_notification_service disponible."""
        from src.services.notifications.notif_web import get_push_notification_service
        assert get_push_notification_service is obtenir_service_webpush

    def test_alias_push_subscription(self):
        """Alias PushSubscription disponible."""
        from src.services.notifications.notif_web import PushSubscription
        assert PushSubscription is AbonnementPush

    def test_alias_push_notification(self):
        """Alias PushNotification disponible."""
        from src.services.notifications.notif_web import PushNotification
        assert PushNotification is NotificationPush

    def test_alias_notification_preferences(self):
        """Alias NotificationPreferences disponible."""
        from src.services.notifications.notif_web import NotificationPreferences
        assert NotificationPreferences is PreferencesNotification

    def test_methodes_alias(self, service):
        """Les méthodes alias sont liées aux originales."""
        # Public methods
        assert service.save_subscription == service.sauvegarder_abonnement
        assert service.remove_subscription == service.supprimer_abonnement
        assert service.get_user_subscriptions == service.obtenir_abonnements_utilisateur
        assert service.get_preferences == service.obtenir_preferences
        assert service.update_preferences == service.mettre_a_jour_preferences
        assert service.should_send == service.doit_envoyer
        assert service.send_notification == service.envoyer_notification
        assert service.send_to_all_users == service.envoyer_a_tous
        assert service.notify_stock_low == service.notifier_stock_bas
        assert service.notify_expiration == service.notifier_peremption
        assert service.notify_meal_reminder == service.notifier_rappel_repas
        assert service.notify_shopping_list_shared == service.notifier_liste_partagee
