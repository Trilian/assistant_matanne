"""Tests pour src/services/notifications/inventaire.py - ServiceNotificationsInventaire.

Couverture des fonctionnalités:
- Création de notifications (stock critique, stock bas, péremption)
- Gestion des notifications (ajout, marquage lu, suppression)
- Statistiques et alertes
"""

import pytest

from src.services.core.notifications.inventaire import (
    Notification,
    NotificationService,
    ServiceNotificationsInventaire,
    obtenir_service_notifications,
    obtenir_service_notifications_inventaire,
)
from src.services.core.notifications.types import (
    NotificationInventaire,
    TypeAlerte,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Instance fraîche du service."""
    return ServiceNotificationsInventaire()


@pytest.fixture
def sample_article():
    """Article de test."""
    return {
        "id": 1,
        "ingredient_id": 10,
        "nom": "Lait",
        "quantite": 0.5,
        "quantite_min": 2.0,
        "unite": "L",
        "date_peremption": "2024-01-20",
    }


@pytest.fixture
def sample_article_critico():
    """Article critique."""
    return {
        "id": 2,
        "ingredient_id": 20,
        "nom": "Beurre",
        "quantite": 0.1,
        "quantite_min": 1.0,
        "unite": "kg",
    }


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServiceNotificationsInit:
    """Tests pour l'initialisation."""

    def test_init_service(self, service):
        """Vérifie que le service s'initialise correctement."""
        assert service is not None
        assert isinstance(service, ServiceNotificationsInventaire)
        assert service.notifications == {}
        assert service._next_id == 1

    def test_singleton_obtenir_service(self):
        """Test obtenir_service_notifications_inventaire retourne singleton."""
        import src.services.core.notifications.inventaire as module

        module._service_notifications_inventaire = None

        service1 = obtenir_service_notifications_inventaire()
        service2 = obtenir_service_notifications_inventaire()

        assert service1 is service2

        # Cleanup
        module._service_notifications_inventaire = None

    def test_alias_retrocompatibilite(self):
        """Test les alias de rétrocompatibilité."""
        assert NotificationService is ServiceNotificationsInventaire
        assert obtenir_service_notifications is obtenir_service_notifications_inventaire
        assert Notification is NotificationInventaire


# ═══════════════════════════════════════════════════════════
# TESTS CRÉATION NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCreerNotificationStockCritique:
    """Tests pour creer_notification_stock_critique."""

    def test_creer_notification_stock_critique(self, service, sample_article_critico):
        """Test création notification stock critique."""
        notif = service.creer_notification_stock_critique(sample_article_critico)

        assert notif is not None
        assert isinstance(notif, NotificationInventaire)
        assert notif.type_alerte == TypeAlerte.STOCK_CRITIQUE
        assert notif.article_id == 2
        assert notif.ingredient_id == 20
        assert "Beurre" in notif.titre
        assert notif.priorite == "haute"
        assert notif.icone == "❌"

    def test_notification_contient_details(self, service, sample_article_critico):
        """Test que la notification contient les détails de quantité."""
        notif = service.creer_notification_stock_critique(sample_article_critico)

        assert "0.1" in notif.message
        assert "kg" in notif.message
        assert "1.0" in notif.message


@pytest.mark.unit
class TestCreerNotificationStockBas:
    """Tests pour creer_notification_stock_bas."""

    def test_creer_notification_stock_bas(self, service, sample_article):
        """Test création notification stock bas."""
        notif = service.creer_notification_stock_bas(sample_article)

        assert notif is not None
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.article_id == 1
        assert "Lait" in notif.titre
        assert notif.priorite == "moyenne"
        assert notif.icone == "⚠️"


@pytest.mark.unit
class TestCreerNotificationPeremption:
    """Tests pour creer_notification_peremption."""

    def test_peremption_passee(self, service, sample_article):
        """Test notification produit périmé."""
        notif = service.creer_notification_peremption(sample_article, jours_avant=-2)

        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_DEPASSEE
        assert "EXPIRÉ" in notif.titre
        assert notif.priorite == "haute"
        assert notif.icone == "🚨"

    def test_peremption_tres_proche(self, service, sample_article):
        """Test notification péremption très proche (<= 3 jours)."""
        notif = service.creer_notification_peremption(sample_article, jours_avant=2)

        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert "très proche" in notif.titre
        assert notif.priorite == "haute"
        assert notif.icone == "🔴"

    def test_peremption_proche(self, service, sample_article):
        """Test notification péremption proche (> 3 jours)."""
        notif = service.creer_notification_peremption(sample_article, jours_avant=5)

        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert "proche" in notif.titre.lower()
        assert notif.priorite == "moyenne"
        assert notif.icone == "🟠"

    def test_peremption_zero_jours(self, service, sample_article):
        """Test notification pour jour même de péremption."""
        notif = service.creer_notification_peremption(sample_article, jours_avant=0)

        assert notif.type_alerte == TypeAlerte.PEREMPTION_DEPASSEE


# ═══════════════════════════════════════════════════════════
# TESTS GESTION NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAjouterNotification:
    """Tests pour ajouter_notification."""

    def test_ajouter_notification(self, service, sample_article):
        """Test ajout d'une notification."""
        notif = service.creer_notification_stock_bas(sample_article)
        result = service.ajouter_notification(notif)

        assert result is not None
        assert result.id >= 1
        assert 1 in service.notifications
        assert len(service.notifications[1]) == 1

    def test_ajouter_notification_utilisateur_specifique(self, service, sample_article):
        """Test ajout pour un utilisateur spécifique."""
        notif = service.creer_notification_stock_bas(sample_article)
        result = service.ajouter_notification(notif, utilisateur_id=42)

        assert 42 in service.notifications
        assert len(service.notifications[42]) == 1

    def test_eviter_doublons(self, service, sample_article):
        """Test que les doublons sont évités."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_bas(sample_article)

        service.ajouter_notification(notif1)
        result = service.ajouter_notification(notif2)

        # Devrait retourner la notif existante
        assert len(service.notifications[1]) == 1


@pytest.mark.unit
class TestObtenirNotifications:
    """Tests pour obtenir_notifications."""

    def test_obtenir_notifications_vide(self, service):
        """Test récupération sans notifications."""
        result = service.obtenir_notifications()

        assert result == []

    def test_obtenir_notifications_avec_notifs(
        self, service, sample_article, sample_article_critico
    ):
        """Test récupération avec notifications."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_critique(sample_article_critico)

        service.ajouter_notification(notif1)
        service.ajouter_notification(notif2)

        result = service.obtenir_notifications()

        assert len(result) == 2

    def test_obtenir_notifications_non_lues_seulement(
        self, service, sample_article, sample_article_critico
    ):
        """Test filtrage non lues."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_critique(sample_article_critico)

        notif1 = service.ajouter_notification(notif1)
        notif2 = service.ajouter_notification(notif2)

        # Marquer la première comme lue
        service.marquer_lue(notif1.id)

        result = service.obtenir_notifications(non_lues_seulement=True)

        assert len(result) == 1
        assert result[0].id == notif2.id

    def test_notifications_triees_par_priorite(
        self, service, sample_article, sample_article_critico
    ):
        """Test que les notifications sont triées par priorité."""
        # Ajouter d'abord stock bas (moyenne), puis critique (haute)
        notif_bas = service.creer_notification_stock_bas(sample_article)
        notif_critique = service.creer_notification_stock_critique(sample_article_critico)

        service.ajouter_notification(notif_bas)
        service.ajouter_notification(notif_critique)

        result = service.obtenir_notifications()

        # Priorité haute devrait venir après les basses
        # (car reverse=True et haute=0 est plus petit)
        assert result[0].priorite == "haute"


@pytest.mark.unit
class TestMarquerLue:
    """Tests pour marquer_lue."""

    def test_marquer_lue_succes(self, service, sample_article):
        """Test marquer une notification comme lue."""
        notif = service.creer_notification_stock_bas(sample_article)
        notif = service.ajouter_notification(notif)

        result = service.marquer_lue(notif.id)

        assert result is True

        # Vérifier que c'est bien marqué
        notifs = service.obtenir_notifications()
        assert notifs[0].lue is True

    def test_marquer_lue_id_inexistant(self, service):
        """Test avec ID inexistant."""
        result = service.marquer_lue(9999)

        assert result is False

    def test_marquer_lue_id_none(self, service):
        """Test avec ID None."""
        result = service.marquer_lue(None)

        assert result is False


@pytest.mark.unit
class TestSupprimerNotification:
    """Tests pour supprimer_notification."""

    def test_supprimer_notification_succes(self, service, sample_article):
        """Test suppression d'une notification."""
        notif = service.creer_notification_stock_bas(sample_article)
        notif = service.ajouter_notification(notif)

        result = service.supprimer_notification(notif.id)

        assert result is True
        assert len(service.notifications[1]) == 0

    def test_supprimer_notification_inexistante(self, service):
        """Test suppression notification inexistante."""
        result = service.supprimer_notification(9999)

        assert result is False

    def test_supprimer_notification_none(self, service):
        """Test suppression avec None."""
        result = service.supprimer_notification(None)

        assert result is False


@pytest.mark.unit
class TestEffacerToutesLues:
    """Tests pour effacer_toutes_lues."""

    def test_effacer_toutes_lues(self, service, sample_article, sample_article_critico):
        """Test effacer toutes les notifications lues."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_critique(sample_article_critico)

        notif1 = service.ajouter_notification(notif1)
        service.ajouter_notification(notif2)

        # Marquer la première comme lue
        service.marquer_lue(notif1.id)

        count = service.effacer_toutes_lues()

        assert count == 1
        assert len(service.notifications[1]) == 1

    def test_effacer_utilisateur_sans_notifs(self, service):
        """Test effacer pour utilisateur sans notifications."""
        count = service.effacer_toutes_lues(utilisateur_id=99)

        assert count == 0


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestObtenirStats:
    """Tests pour obtenir_stats."""

    def test_obtenir_stats_vide(self, service):
        """Test stats sans notifications."""
        stats = service.obtenir_stats()

        assert stats["total"] == 0
        assert stats["non_lues"] == 0
        assert stats["par_type"] == {}
        assert stats["par_priorite"] == {}

    def test_obtenir_stats_avec_notifs(self, service, sample_article, sample_article_critico):
        """Test stats avec notifications."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_critique(sample_article_critico)

        notif1 = service.ajouter_notification(notif1)
        service.ajouter_notification(notif2)

        # Marquer une comme lue
        service.marquer_lue(notif1.id)

        stats = service.obtenir_stats()

        assert stats["total"] == 2
        assert stats["non_lues"] == 1
        assert TypeAlerte.STOCK_BAS.value in stats["par_type"]
        assert "haute" in stats["par_priorite"]


@pytest.mark.unit
class TestObtenirAlertesActives:
    """Tests pour obtenir_alertes_actives."""

    def test_obtenir_alertes_actives(self, service, sample_article, sample_article_critico):
        """Test récupération alertes actives groupées."""
        notif1 = service.creer_notification_stock_bas(sample_article)
        notif2 = service.creer_notification_stock_critique(sample_article_critico)

        service.ajouter_notification(notif1)
        service.ajouter_notification(notif2)

        alertes = service.obtenir_alertes_actives()

        assert "critiques" in alertes
        assert "hautes" in alertes
        assert "moyennes" in alertes
        assert "basses" in alertes

        # Stock critique = priorité haute -> critiques
        assert len(alertes["critiques"]) == 1
        # Stock bas = priorité moyenne -> hautes
        assert len(alertes["hautes"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS EMAIL
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEnvoyerEmailAlerte:
    """Tests pour envoyer_email_alerte."""

    def test_envoyer_email_alerte(self, service, sample_article):
        """Test envoi email (stub)."""
        notif = service.creer_notification_stock_bas(sample_article)

        result = service.envoyer_email_alerte(notif, "test@example.com")

        assert result is True
        assert notif.email == "test@example.com"
        assert notif.push_envoyee is True
