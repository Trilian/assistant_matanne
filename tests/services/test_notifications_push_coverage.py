"""
Tests complets pour src/services/notifications_push.py
Objectif: couverture >80%
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import date, timedelta
import asyncio


# ═══════════════════════════════════════════════════════════
# TESTS MODELES PYDANTIC
# ═══════════════════════════════════════════════════════════

class TestNotificationPushConfig:
    """Tests pour NotificationPushConfig model."""
    
    def test_config_default_values(self):
        """Test default values for config."""
        from src.services.notifications_push import NotificationPushConfig
        
        config = NotificationPushConfig()
        
        assert config.topic == "matanne-famille"
        assert config.actif is True
        assert config.rappels_taches is True
        assert config.rappels_courses is False
        assert config.heure_digest == 8
        assert config.jours_digest == [0, 1, 2, 3, 4, 5, 6]
    
    def test_config_custom_values(self):
        """Test custom values for config."""
        from src.services.notifications_push import NotificationPushConfig
        
        config = NotificationPushConfig(
            topic="custom-topic",
            actif=False,
            rappels_taches=False,
            rappels_courses=True,
            heure_digest=18,
            jours_digest=[0, 6]
        )
        
        assert config.topic == "custom-topic"
        assert config.actif is False
        assert config.rappels_taches is False
        assert config.rappels_courses is True
        assert config.heure_digest == 18
        assert config.jours_digest == [0, 6]
    
    def test_config_heure_bounds(self):
        """Test heure_digest bounds (0-23)."""
        from src.services.notifications_push import NotificationPushConfig
        from pydantic import ValidationError
        
        # Valid bounds
        config0 = NotificationPushConfig(heure_digest=0)
        assert config0.heure_digest == 0
        
        config23 = NotificationPushConfig(heure_digest=23)
        assert config23.heure_digest == 23
        
        # Invalid bounds
        with pytest.raises(ValidationError):
            NotificationPushConfig(heure_digest=-1)
        
        with pytest.raises(ValidationError):
            NotificationPushConfig(heure_digest=24)


class TestNotificationPush:
    """Tests pour NotificationPush model."""
    
    def test_notification_default_values(self):
        """Test default values for notification."""
        from src.services.notifications_push import NotificationPush
        
        notif = NotificationPush(titre="Test", message="Message test")
        
        assert notif.titre == "Test"
        assert notif.message == "Message test"
        assert notif.priorite == 3
        assert notif.tags == []
        assert notif.click_url is None
        assert notif.actions == []
    
    def test_notification_custom_values(self):
        """Test custom values for notification."""
        from src.services.notifications_push import NotificationPush
        
        notif = NotificationPush(
            titre="Alerte",
            message="Message urgent",
            priorite=5,
            tags=["warning", "calendar"],
            click_url="https://example.com",
            actions=[{"action": "view", "label": "Voir"}]
        )
        
        assert notif.titre == "Alerte"
        assert notif.message == "Message urgent"
        assert notif.priorite == 5
        assert notif.tags == ["warning", "calendar"]
        assert notif.click_url == "https://example.com"
        assert notif.actions == [{"action": "view", "label": "Voir"}]
    
    def test_notification_priorite_bounds(self):
        """Test priorite bounds (1-5)."""
        from src.services.notifications_push import NotificationPush
        from pydantic import ValidationError
        
        # Valid bounds
        notif1 = NotificationPush(titre="T", message="M", priorite=1)
        assert notif1.priorite == 1
        
        notif5 = NotificationPush(titre="T", message="M", priorite=5)
        assert notif5.priorite == 5
        
        # Invalid bounds
        with pytest.raises(ValidationError):
            NotificationPush(titre="T", message="M", priorite=0)
        
        with pytest.raises(ValidationError):
            NotificationPush(titre="T", message="M", priorite=6)


class TestResultatEnvoiPush:
    """Tests pour ResultatEnvoiPush model."""
    
    def test_resultat_success(self):
        """Test successful result."""
        from src.services.notifications_push import ResultatEnvoiPush
        
        res = ResultatEnvoiPush(
            succes=True,
            message="Notification envoyee",
            notification_id="abc123"
        )
        
        assert res.succes is True
        assert res.message == "Notification envoyee"
        assert res.notification_id == "abc123"
    
    def test_resultat_failure(self):
        """Test failure result."""
        from src.services.notifications_push import ResultatEnvoiPush
        
        res = ResultatEnvoiPush(succes=False, message="Erreur reseau")
        
        assert res.succes is False
        assert res.message == "Erreur reseau"
        assert res.notification_id is None


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION PUSH SERVICE
# ═══════════════════════════════════════════════════════════

class TestNotificationPushServiceInit:
    """Tests for service initialization."""
    
    def test_service_init_default_config(self):
        """Test service init with default config."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        assert service.config is not None
        assert service.config.topic == "matanne-famille"
        assert service.client is not None
    
    def test_service_init_custom_config(self):
        """Test service init with custom config."""
        from src.services.notifications_push import NotificationPushService, NotificationPushConfig
        
        config = NotificationPushConfig(topic="test-topic", actif=False)
        service = NotificationPushService(config=config)
        
        assert service.config.topic == "test-topic"
        assert service.config.actif is False


class TestNotificationPushServiceEnvoyer:
    """Tests for envoyer method."""
    
    @pytest.mark.asyncio
    async def test_envoyer_disabled_config(self):
        """Test envoyer when notifications disabled."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig, NotificationPush
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        
        notif = NotificationPush(titre="Test", message="Message")
        result = await service.envoyer(notif)
        
        assert result.succes is False
        assert "désactivées" in result.message
    
    @pytest.mark.asyncio
    async def test_envoyer_success(self):
        """Test successful notification send."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-123"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            notif = NotificationPush(titre="Test", message="Message")
            result = await service.envoyer(notif)
        
        assert result.succes is True
        assert result.notification_id == "notif-123"
        mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_envoyer_with_tags(self):
        """Test notification with tags."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-tags"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            notif = NotificationPush(
                titre="Test",
                message="Message",
                tags=["warning", "bell"]
            )
            result = await service.envoyer(notif)
        
        assert result.succes is True
        # Check headers contain tags
        call_kwargs = mock_post.call_args.kwargs
        assert "Tags" in call_kwargs["headers"]
        assert "warning,bell" == call_kwargs["headers"]["Tags"]
    
    @pytest.mark.asyncio
    async def test_envoyer_with_click_url(self):
        """Test notification with click URL."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-click"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            notif = NotificationPush(
                titre="Test",
                message="Message",
                click_url="https://example.com/action"
            )
            result = await service.envoyer(notif)
        
        call_kwargs = mock_post.call_args.kwargs
        assert "Click" in call_kwargs["headers"]
        assert call_kwargs["headers"]["Click"] == "https://example.com/action"
    
    @pytest.mark.asyncio
    async def test_envoyer_with_actions(self):
        """Test notification with actions."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "notif-actions"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            notif = NotificationPush(
                titre="Test",
                message="Message",
                actions=[{"action": "view", "label": "Voir"}]
            )
            result = await service.envoyer(notif)
        
        call_kwargs = mock_post.call_args.kwargs
        assert "Actions" in call_kwargs["headers"]
    
    @pytest.mark.asyncio
    async def test_envoyer_http_error(self):
        """Test handling of HTTP error response."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            notif = NotificationPush(titre="Test", message="Message")
            result = await service.envoyer(notif)
        
        assert result.succes is False
        assert "500" in result.message
    
    @pytest.mark.asyncio
    async def test_envoyer_exception(self):
        """Test handling of exception."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush
        )
        
        service = NotificationPushService()
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            notif = NotificationPush(titre="Test", message="Message")
            result = await service.envoyer(notif)
        
        assert result.succes is False
        assert "Network error" in result.message


class TestNotificationPushServiceSync:
    """Tests for sync methods."""
    
    def test_envoyer_sync(self):
        """Test synchronous send wrapper."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPush, NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        
        notif = NotificationPush(titre="Test", message="Message")
        result = service.envoyer_sync(notif)
        
        assert result.succes is False
        assert "désactivées" in result.message
    
    def test_test_connexion_sync(self):
        """Test synchronous connection test wrapper."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        
        result = service.test_connexion_sync()
        
        assert result.succes is False


class TestNotificationPushServiceDBQueries:
    """Tests for database query methods - requires DB connection."""
    
    @pytest.mark.skip(reason="Requires real DB - service init connects to DB")
    def test_obtenir_taches_en_retard_returns_list(self):
        """Test that obtenir_taches_en_retard returns a list (may be empty on error)."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        result = service.obtenir_taches_en_retard()
        assert isinstance(result, list)
    
    @pytest.mark.skip(reason="Requires real DB - service init connects to DB")
    def test_obtenir_taches_du_jour_returns_list(self):
        """Test that obtenir_taches_du_jour returns a list (may be empty on error)."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        result = service.obtenir_taches_du_jour()
        assert isinstance(result, list)
    
    @pytest.mark.skip(reason="Requires real DB - service init connects to DB")
    def test_obtenir_courses_urgentes_returns_list(self):
        """Test that obtenir_courses_urgentes returns a list (may be empty on error)."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        result = service.obtenir_courses_urgentes()
        assert isinstance(result, list)
    
    @pytest.mark.skip(reason="Requires real DB - service init connects to DB")
    def test_db_methods_have_decorators(self):
        """Test that DB methods have the right decorators applied."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        methods = [
            service.obtenir_taches_en_retard,
            service.obtenir_taches_du_jour,
            service.obtenir_courses_urgentes
        ]
        
        for method in methods:
            assert callable(method)
            result = method()
            assert isinstance(result, list)
    
    def test_db_methods_exist(self):
        """Test that DB methods exist and are callable."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        # These methods should exist
        assert hasattr(service, 'obtenir_taches_en_retard')
        assert hasattr(service, 'obtenir_taches_du_jour')
        assert hasattr(service, 'obtenir_courses_urgentes')
        
        # And be callable
        assert callable(service.obtenir_taches_en_retard)
        assert callable(service.obtenir_taches_du_jour)
        assert callable(service.obtenir_courses_urgentes)


class TestNotificationPushServiceAlerts:
    """Tests for alert notification methods."""
    
    @pytest.mark.asyncio
    async def test_envoyer_alerte_tache_retard_short(self):
        """Test alert for task with short delay."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        
        mock_task = Mock()
        mock_task.titre = "Nettoyer"
        mock_task.date_echeance = date.today() - timedelta(days=2)
        mock_task.description = "Description"
        
        result = await service.envoyer_alerte_tache_retard(mock_task)
        
        assert result.succes is False  # Disabled
    
    @pytest.mark.asyncio
    async def test_envoyer_alerte_tache_retard_medium(self):
        """Test alert for task with medium delay (3-7 days)."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_task = Mock()
        mock_task.titre = "Jardinage"
        mock_task.date_echeance = date.today() - timedelta(days=5)
        mock_task.description = None
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "alert-123"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await service.envoyer_alerte_tache_retard(mock_task)
        
        assert result.succes is True
        # Check priority was set to 4 for 3-7 days overdue
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Priority"] == "4"
    
    @pytest.mark.asyncio
    async def test_envoyer_alerte_tache_retard_long(self):
        """Test alert for task with long delay (>7 days)."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_task = Mock()
        mock_task.titre = "Maintenance"
        mock_task.date_echeance = date.today() - timedelta(days=10)
        mock_task.description = "Urgent"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "alert-urgent"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await service.envoyer_alerte_tache_retard(mock_task)
        
        assert result.succes is True
        # Check priority was set to 5 for >7 days overdue
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Priority"] == "5"


class TestNotificationPushServiceDigest:
    """Tests for daily digest method."""
    
    @pytest.mark.asyncio
    async def test_envoyer_digest_quotidien_no_tasks(self):
        """Test digest when no tasks."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[]):
            with patch.object(service, 'obtenir_taches_du_jour', return_value=[]):
                result = await service.envoyer_digest_quotidien()
        
        assert result.succes is True
        assert "tâches" in result.message
    
    @pytest.mark.asyncio
    async def test_envoyer_digest_quotidien_with_overdue(self):
        """Test digest with overdue tasks."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_task = Mock()
        mock_task.titre = "Retard Task"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "digest-123"}
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[mock_task]):
            with patch.object(service, 'obtenir_taches_du_jour', return_value=[]):
                with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
                    mock_post.return_value = mock_response
                    result = await service.envoyer_digest_quotidien()
        
        assert result.succes is True
        # Check priority is 4 when overdue tasks exist
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Priority"] == "4"
    
    @pytest.mark.asyncio
    async def test_envoyer_digest_quotidien_with_today_tasks(self):
        """Test digest with today's tasks only."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_task = Mock()
        mock_task.titre = "Today Task"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "digest-today"}
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[]):
            with patch.object(service, 'obtenir_taches_du_jour', return_value=[mock_task]):
                with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
                    mock_post.return_value = mock_response
                    result = await service.envoyer_digest_quotidien()
        
        assert result.succes is True
        # Check priority is 3 when no overdue tasks
        call_kwargs = mock_post.call_args.kwargs
        assert call_kwargs["headers"]["Priority"] == "3"


class TestNotificationPushServiceRappelCourses:
    """Tests for shopping reminder method."""
    
    @pytest.mark.asyncio
    async def test_envoyer_rappel_courses_no_urgent(self):
        """Test reminder when no urgent items."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        with patch.object(service, 'obtenir_courses_urgentes', return_value=[]):
            result = await service.envoyer_rappel_courses(nb_articles=5)
        
        assert result.succes is True
        assert "Pas de courses urgentes" in result.message
    
    @pytest.mark.asyncio
    async def test_envoyer_rappel_courses_with_items(self):
        """Test reminder with urgent items."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_item1 = Mock()
        mock_item1.nom = "Lait"
        mock_item2 = Mock()
        mock_item2.nom = "Pain"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "reminder-123"}
        
        with patch.object(service, 'obtenir_courses_urgentes', return_value=[mock_item1, mock_item2]):
            with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
                mock_post.return_value = mock_response
                result = await service.envoyer_rappel_courses(nb_articles=10)
        
        assert result.succes is True
        # Check message contains item names
        call_args = mock_post.call_args
        content = call_args.kwargs.get("content", call_args[1].get("content", ""))
        assert "Lait" in content or "lait" in content.lower()


class TestNotificationPushServiceTestConnexion:
    """Tests for connection test method."""
    
    @pytest.mark.asyncio
    async def test_test_connexion_success(self):
        """Test successful connection test."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-123"}
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await service.test_connexion()
        
        assert result.succes is True
    
    @pytest.mark.asyncio
    async def test_test_connexion_failure(self):
        """Test failed connection test."""
        from src.services.notifications_push import NotificationPushService
        
        service = NotificationPushService()
        
        with patch.object(service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Connection refused")
            result = await service.test_connexion()
        
        assert result.succes is False


class TestNotificationPushServiceURLs:
    """Tests for URL generation methods."""
    
    def test_get_subscribe_url(self):
        """Test subscription URL generation."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig
        )
        
        config = NotificationPushConfig(topic="test-topic")
        service = NotificationPushService(config=config)
        
        url = service.get_subscribe_url()
        
        assert url == "ntfy://test-topic"
    
    def test_get_web_url(self):
        """Test web URL generation."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig
        )
        
        config = NotificationPushConfig(topic="my-family")
        service = NotificationPushService(config=config)
        
        url = service.get_web_url()
        
        assert url == "https://ntfy.sh/my-family"
    
    def test_get_subscribe_qr_url(self):
        """Test QR code URL generation."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushConfig
        )
        
        config = NotificationPushConfig(topic="qr-topic")
        service = NotificationPushService(config=config)
        
        url = service.get_subscribe_qr_url()
        
        assert "api.qrserver.com" in url
        assert "qr-topic" in url


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATION PUSH SCHEDULER
# ═══════════════════════════════════════════════════════════

class TestNotificationPushScheduler:
    """Tests for NotificationPushScheduler class."""
    
    def test_scheduler_init(self):
        """Test scheduler initialization."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushScheduler
        )
        
        service = NotificationPushService()
        scheduler = NotificationPushScheduler(service)
        
        assert scheduler.service == service
        assert scheduler._running is False
    
    @pytest.mark.asyncio
    async def test_verifier_et_envoyer_alertes_no_tasks(self):
        """Test alert check with no overdue tasks."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushScheduler
        )
        
        service = NotificationPushService()
        scheduler = NotificationPushScheduler(service)
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[]):
            results = await scheduler.verifier_et_envoyer_alertes()
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_verifier_et_envoyer_alertes_with_tasks(self):
        """Test alert check with overdue tasks."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushScheduler,
            ResultatEnvoiPush, NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        scheduler = NotificationPushScheduler(service)
        
        mock_task = Mock()
        mock_task.titre = "Overdue Task"
        mock_task.date_echeance = date.today() - timedelta(days=3)
        mock_task.description = "Test"
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[mock_task]):
            results = await scheduler.verifier_et_envoyer_alertes()
        
        assert len(results) == 1
        assert results[0].succes is False  # Disabled config
    
    @pytest.mark.asyncio
    async def test_verifier_et_envoyer_alertes_max_5(self):
        """Test that max 5 alerts are sent."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushScheduler,
            NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        scheduler = NotificationPushScheduler(service)
        
        # Create 10 mock tasks
        mock_tasks = []
        for i in range(10):
            task = Mock()
            task.titre = f"Task {i}"
            task.date_echeance = date.today() - timedelta(days=i+1)
            task.description = None
            mock_tasks.append(task)
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=mock_tasks):
            results = await scheduler.verifier_et_envoyer_alertes()
        
        # Should only process first 5
        assert len(results) == 5
    
    def test_lancer_verification_sync(self):
        """Test synchronous verification launch."""
        from src.services.notifications_push import (
            NotificationPushService, NotificationPushScheduler,
            NotificationPushConfig
        )
        
        config = NotificationPushConfig(actif=False)
        service = NotificationPushService(config=config)
        scheduler = NotificationPushScheduler(service)
        
        with patch.object(service, 'obtenir_taches_en_retard', return_value=[]):
            results = scheduler.lancer_verification_sync()
        
        assert results == []


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════

class TestFactoryFunctions:
    """Tests for factory functions."""
    
    def test_get_notification_push_service_default(self):
        """Test factory with default config."""
        from src.services.notifications_push import get_notification_push_service
        
        service = get_notification_push_service()
        
        assert service is not None
        assert service.config.topic == "matanne-famille"
    
    def test_get_notification_push_service_custom(self):
        """Test factory with custom config."""
        from src.services.notifications_push import (
            get_notification_push_service, NotificationPushConfig
        )
        
        config = NotificationPushConfig(topic="custom", actif=False)
        service = get_notification_push_service(config=config)
        
        assert service.config.topic == "custom"
        assert service.config.actif is False
    
    def test_get_notification_push_scheduler(self):
        """Test scheduler factory."""
        from src.services.notifications_push import get_notification_push_scheduler
        
        scheduler = get_notification_push_scheduler()
        
        assert scheduler is not None
        assert scheduler.service is not None


# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTS
# ═══════════════════════════════════════════════════════════

class TestConstants:
    """Tests for module constants."""
    
    def test_ntfy_base_url(self):
        """Test NTFY base URL constant."""
        from src.services.notifications_push import NTFY_BASE_URL
        
        assert NTFY_BASE_URL == "https://ntfy.sh"
    
    def test_default_topic(self):
        """Test default topic constant."""
        from src.services.notifications_push import DEFAULT_TOPIC
        
        assert DEFAULT_TOPIC == "matanne-famille"
    
    def test_priority_mapping(self):
        """Test priority mapping constant."""
        from src.services.notifications_push import PRIORITY_MAPPING
        
        assert PRIORITY_MAPPING["urgente"] == 5
        assert PRIORITY_MAPPING["haute"] == 4
        assert PRIORITY_MAPPING["normale"] == 3
        assert PRIORITY_MAPPING["basse"] == 2
        assert PRIORITY_MAPPING["min"] == 1
