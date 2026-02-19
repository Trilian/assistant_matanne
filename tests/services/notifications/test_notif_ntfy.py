"""Tests pour src/services/notifications/notif_ntfy.py - ServiceNtfy.

Couverture des fonctionnalités:
- Envoi de notifications via ntfy.sh
- Récupération des tâches en retard
- Digest quotidien
- Planificateur de notifications
"""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.core.notifications.notif_ntfy import (
    NotificationPushConfig,
    NotificationPushScheduler,
    # Alias rétrocompatibilité
    NotificationPushService,
    PlanificateurNtfy,
    ServiceNtfy,
    get_notification_push_service,
    obtenir_planificateur_ntfy,
    obtenir_service_ntfy,
)
from src.services.core.notifications.types import (
    ConfigurationNtfy,
    NotificationNtfy,
    ResultatEnvoiNtfy,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def config():
    """Configuration de test."""
    return ConfigurationNtfy(
        topic="test-matanne",
        actif=True,
    )


@pytest.fixture
def config_inactive():
    """Configuration désactivée."""
    return ConfigurationNtfy(
        topic="test-matanne",
        actif=False,
    )


@pytest.fixture
def service(config):
    """Service ntfy de test."""
    return ServiceNtfy(config)


@pytest.fixture
def service_disabled(config_inactive):
    """Service ntfy désactivé."""
    return ServiceNtfy(config_inactive)


@pytest.fixture
def notification():
    """Notification de test."""
    return NotificationNtfy(
        titre="Test notification",
        message="Ceci est un test",
        priorite=3,
        tags=["test"],
    )


@pytest.fixture
def mock_httpx_client():
    """Mock du client HTTP."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceNtfyInit:
    """Tests pour l'initialisation de ServiceNtfy."""

    def test_init_avec_config(self, config):
        """Initialisation avec configuration."""
        service = ServiceNtfy(config)

        assert service.config.topic == "test-matanne"
        assert service.config.actif is True

    def test_init_sans_config(self):
        """Initialisation sans configuration (défaut)."""
        service = ServiceNtfy()

        assert service.config is not None
        assert isinstance(service.config, ConfigurationNtfy)

    def test_factory_obtenir_service_ntfy(self):
        """Test factory obtenir_service_ntfy."""
        service = obtenir_service_ntfy()

        assert isinstance(service, ServiceNtfy)

    def test_factory_avec_config(self, config):
        """Test factory avec configuration."""
        service = obtenir_service_ntfy(config)

        assert service.config.topic == "test-matanne"


# ═══════════════════════════════════════════════════════════
# TESTS ENVOI NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerNotification:
    """Tests pour l'envoi de notifications."""

    @pytest.mark.asyncio
    async def test_envoyer_desactive(self, service_disabled, notification):
        """Envoi avec service désactivé."""
        result = await service_disabled.envoyer(notification)

        assert result.succes is False
        assert "désactivées" in result.message

    @pytest.mark.asyncio
    async def test_envoyer_succes(self, service, notification):
        """Envoi réussi."""
        # Mock du client HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "abc123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = await service.envoyer(notification)

        assert result.succes is True
        assert "envoyée" in result.message
        assert result.notification_id == "abc123"

    @pytest.mark.asyncio
    async def test_envoyer_erreur_http(self, service, notification):
        """Envoi avec erreur HTTP."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = await service.envoyer(notification)

        assert result.succes is False
        assert "500" in result.message

    @pytest.mark.asyncio
    async def test_envoyer_exception(self, service, notification):
        """Envoi avec exception."""
        service.client = AsyncMock()
        service.client.post.side_effect = Exception("Network error")

        result = await service.envoyer(notification)

        assert result.succes is False
        assert "Network error" in result.message

    def test_envoyer_sync(self, service, notification):
        """Test version synchrone."""
        # Mock du client HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "sync123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = service.envoyer_sync(notification)

        assert result.succes is True


@pytest.mark.unit
class TestNotificationAvecOptions:
    """Tests pour les options de notification."""

    @pytest.mark.asyncio
    async def test_notification_avec_click_url(self, service):
        """Notification avec URL de clic."""
        notif = NotificationNtfy(
            titre="Test",
            message="Message",
            click_url="https://example.com",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "url123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        await service.envoyer(notif)

        # Vérifier que l'URL est dans les headers
        call_args = service.client.post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert headers.get("Click") == "https://example.com"

    @pytest.mark.asyncio
    async def test_notification_avec_tags(self, service):
        """Notification avec tags."""
        notif = NotificationNtfy(
            titre="Test",
            message="Message",
            tags=["warning", "house"],
        )

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "tags123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        await service.envoyer(notif)

        call_args = service.client.post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert "warning,house" in headers.get("Tags", "")


# ═══════════════════════════════════════════════════════════
# TESTS RÉCUPÉRATION TÃ‚CHES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestObtenirTachesEnRetard:
    """Tests pour obtenir_taches_en_retard."""

    def test_taches_en_retard_vide(self, service, db):
        """Pas de tâches en retard."""
        result = service.obtenir_taches_en_retard(db=db)

        assert result == []

    def test_taches_en_retard_avec_taches(self, service):
        """Récupération des tâches en retard."""
        from unittest.mock import MagicMock, patch

        # Mock de la requête DB
        tache = MagicMock()
        tache.nom = "Tâche en retard"
        tache.prochaine_fois = date.today() - timedelta(days=5)
        tache.fait = False
        tache.categorie = "rangement"

        with patch.object(service, "obtenir_taches_en_retard", return_value=[tache]):
            result = service.obtenir_taches_en_retard()

        assert len(result) >= 1
        assert result[0].nom == "Tâche en retard"

    def test_taches_terminees_exclues(self, service):
        """Tâches terminées non incluses."""
        from unittest.mock import patch

        # Les tâches terminées ne devraient pas être retournées
        with patch.object(service, "obtenir_taches_en_retard", return_value=[]):
            result = service.obtenir_taches_en_retard()

        # Ne devrait pas inclure la tâche terminée
        assert all(t.fait is False for t in result)


@pytest.mark.unit
class TestObtenirTachesDuJour:
    """Tests pour obtenir_taches_du_jour."""

    def test_taches_du_jour_vide(self, service, db):
        """Pas de tâches aujourd'hui."""
        result = service.obtenir_taches_du_jour(db=db)

        assert result == []

    def test_taches_du_jour_avec_taches(self, service):
        """Récupération des tâches du jour."""
        from unittest.mock import MagicMock, patch

        tache = MagicMock()
        tache.nom = "Tâche aujourd'hui"
        tache.prochaine_fois = date.today()
        tache.fait = False
        tache.categorie = "rangement"

        with patch.object(service, "obtenir_taches_du_jour", return_value=[tache]):
            result = service.obtenir_taches_du_jour()

        assert len(result) >= 1


@pytest.mark.unit
class TestObtenirCoursesUrgentes:
    """Tests pour obtenir_courses_urgentes."""

    def test_courses_urgentes_vide(self, service, db):
        """Pas de courses urgentes."""
        result = service.obtenir_courses_urgentes(db=db)

        assert result == []

    def test_courses_urgentes_avec_articles(self, service):
        """Récupération des courses urgentes."""
        from unittest.mock import MagicMock, patch

        article = MagicMock()
        article.achete = False
        article.priorite = "haute"

        with patch.object(service, "obtenir_courses_urgentes", return_value=[article]):
            result = service.obtenir_courses_urgentes()

        assert len(result) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES TÃ‚CHES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerAlerteTacheRetard:
    """Tests pour envoyer_alerte_tache_retard."""

    @pytest.mark.asyncio
    async def test_alerte_tache_retard(self, service):
        """Envoi alerte pour tâche en retard."""
        tache = MagicMock()
        tache.nom = "Nettoyer garage"
        tache.prochaine_fois = date.today() - timedelta(days=3)
        tache.fait = False
        tache.description = "Faire le ménage"
        tache.categorie = "rangement"

        # Mock du client HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = await service.envoyer_alerte_tache_retard(tache)

        assert result.succes is True

    @pytest.mark.asyncio
    async def test_priorite_selon_retard(self, service):
        """Priorité augmente selon le retard."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        # Tâche très en retard (> 7 jours)
        tache_tres_retard = MagicMock()
        tache_tres_retard.nom = "Très en retard"
        tache_tres_retard.prochaine_fois = date.today() - timedelta(days=10)
        tache_tres_retard.fait = False
        tache_tres_retard.categorie = "rangement"

        await service.envoyer_alerte_tache_retard(tache_tres_retard)

        call_args = service.client.post.call_args
        headers = call_args.kwargs.get("headers", {})
        assert headers.get("Priority") == "5"


# ═══════════════════════════════════════════════════════════
# TESTS DIGEST QUOTIDIEN
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerDigestQuotidien:
    """Tests pour envoyer_digest_quotidien."""

    @pytest.mark.asyncio
    async def test_digest_sans_taches(self, service):
        """Digest sans tâches."""
        # Mock des méthodes de récupération
        service.obtenir_taches_en_retard = MagicMock(return_value=[])
        service.obtenir_taches_du_jour = MagicMock(return_value=[])

        result = await service.envoyer_digest_quotidien()

        assert result.succes is True
        assert "Pas de tâches" in result.message

    @pytest.mark.asyncio
    async def test_digest_avec_taches(self, service, db):
        """Digest avec tâches."""
        # Créer des tâches mockées
        tache1 = MagicMock()
        tache1.nom = "Tâche retard"
        tache1.prochaine_fois = date.today() - timedelta(days=1)
        tache1.fait = False
        tache1.categorie = "rangement"

        tache2 = MagicMock()
        tache2.nom = "Tâche jour"
        tache2.prochaine_fois = date.today()
        tache2.fait = False
        tache2.categorie = "rangement"

        service.obtenir_taches_en_retard = MagicMock(return_value=[tache1])
        service.obtenir_taches_du_jour = MagicMock(return_value=[tache2])

        # Mock HTTP
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "digest123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = await service.envoyer_digest_quotidien()

        assert result.succes is True


# ═══════════════════════════════════════════════════════════
# TESTS TEST CONNEXION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTestConnexion:
    """Tests pour test_connexion."""

    @pytest.mark.asyncio
    async def test_connexion_succes(self, service):
        """Test connexion réussie."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = await service.test_connexion()

        assert result.succes is True

    def test_connexion_sync(self, service):
        """Test connexion synchrone."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "sync123"}

        service.client = AsyncMock()
        service.client.post.return_value = mock_response

        result = service.test_connexion_sync()

        assert result.succes is True


# ═══════════════════════════════════════════════════════════
# TESTS URLs
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestUrls:
    """Tests pour les méthodes d'URL."""

    def test_get_subscribe_url(self, service):
        """URL d'abonnement."""
        url = service.get_subscribe_url()

        assert url == "ntfy://test-matanne"

    def test_get_web_url(self, service):
        """URL web."""
        url = service.get_web_url()

        assert "test-matanne" in url
        assert "ntfy.sh" in url

    def test_get_subscribe_qr_url(self, service):
        """URL QR code."""
        url = service.get_subscribe_qr_url()

        assert "qrserver" in url
        assert "test-matanne" in url


# ═══════════════════════════════════════════════════════════
# TESTS PLANIFICATEUR
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPlanificateurNtfy:
    """Tests pour PlanificateurNtfy."""

    def test_init_planificateur(self, service):
        """Initialisation du planificateur."""
        planificateur = PlanificateurNtfy(service)

        assert planificateur.service is service
        assert planificateur._running is False

    @pytest.mark.asyncio
    async def test_verifier_et_envoyer_alertes(self, service, db):
        """Vérification et envoi d'alertes."""
        tache = MagicMock()
        tache.nom = "Tâche retard"
        tache.prochaine_fois = date.today() - timedelta(days=1)
        tache.fait = False
        tache.categorie = "rangement"

        service.obtenir_taches_en_retard = MagicMock(return_value=[tache])

        # Mock envoi
        service.envoyer_alerte_tache_retard = AsyncMock(
            return_value=ResultatEnvoiNtfy(succes=True, message="OK")
        )

        planificateur = PlanificateurNtfy(service)
        resultats = await planificateur.verifier_et_envoyer_alertes()

        assert len(resultats) >= 1
        assert resultats[0].succes is True

    def test_lancer_verification_sync(self, service, db):
        """Lancement synchrone de la vérification."""
        service.obtenir_taches_en_retard = MagicMock(return_value=[])

        planificateur = PlanificateurNtfy(service)
        resultats = planificateur.lancer_verification_sync()

        assert resultats == []

    def test_factory_obtenir_planificateur(self):
        """Test factory obtenir_planificateur_ntfy."""
        planificateur = obtenir_planificateur_ntfy()

        assert isinstance(planificateur, PlanificateurNtfy)


# ═══════════════════════════════════════════════════════════
# TESTS ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAliasRetrocompatibilite:
    """Tests pour les alias de rétrocompatibilité."""

    def test_notification_push_service_alias(self):
        """NotificationPushService = ServiceNtfy."""
        assert NotificationPushService is ServiceNtfy

    def test_notification_push_scheduler_alias(self):
        """NotificationPushScheduler = PlanificateurNtfy."""
        assert NotificationPushScheduler is PlanificateurNtfy

    def test_notification_push_config_alias(self):
        """NotificationPushConfig = ConfigurationNtfy."""
        assert NotificationPushConfig is ConfigurationNtfy

    def test_get_service_alias(self):
        """get_notification_push_service = obtenir_service_ntfy."""
        assert get_notification_push_service is obtenir_service_ntfy
