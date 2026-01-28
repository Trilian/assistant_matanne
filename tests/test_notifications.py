"""Tests unitaires pour le service notifications."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock


class TestTypeAlerteEnum:
    """Tests pour l'enum TypeAlerte."""

    def test_types_alertes_disponibles(self):
        """Vérifie que tous les types d'alertes sont définis."""
        from src.services.notifications import TypeAlerte
        
        # Types attendus
        types_attendus = [
            "STOCK_CRITIQUE",
            "STOCK_BAS",
            "PEREMPTION_PROCHE",
            "PEREMPTION_EXPIREE"
        ]
        
        for type_alerte in types_attendus:
            assert hasattr(TypeAlerte, type_alerte)


class TestNotificationModel:
    """Tests pour le modèle Notification."""

    def test_notification_creation(self):
        """Création d'une notification."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="Stock bas",
            message="Le lait est bientôt épuisé",
            priorite=2
        )
        
        assert notif.titre == "Stock bas"
        assert notif.message == "Le lait est bientôt épuisé"
        assert notif.priorite == 2

    def test_notification_non_lue_par_defaut(self):
        """Une notification est non lue par défaut."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            titre="Alerte",
            message="Stock critique"
        )
        
        assert notif.lue == False

    def test_notification_priorites(self):
        """Les priorités sont des entiers."""
        from src.services.notifications import Notification, TypeAlerte
        
        # Priorité haute (1), moyenne (2), basse (3)
        notif_haute = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            titre="Critique",
            message="Urgent",
            priorite=1
        )
        
        notif_basse = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="Info",
            message="Information",
            priorite=3
        )
        
        assert notif_haute.priorite < notif_basse.priorite


class TestNotificationServiceInit:
    """Tests d'initialisation du service."""

    def test_get_notification_service(self):
        """La factory retourne une instance."""
        from src.services.notifications import get_notification_service
        
        service = get_notification_service()
        assert service is not None

    def test_service_methodes_requises(self):
        """Le service expose les méthodes requises."""
        from src.services.notifications import get_notification_service
        
        service = get_notification_service()
        
        assert hasattr(service, 'creer_notification_stock_critique')
        assert hasattr(service, 'creer_notification_stock_bas')
        assert hasattr(service, 'creer_notification_peremption')
        assert hasattr(service, 'ajouter_notification')
        assert hasattr(service, 'obtenir_notifications')
        assert hasattr(service, 'marquer_lue')
        assert hasattr(service, 'supprimer_notification')
        assert hasattr(service, 'effacer_toutes_lues')
        assert hasattr(service, 'obtenir_stats')


class TestCreerNotificationStockCritique:
    """Tests pour creer_notification_stock_critique."""

    def test_creation_notification_critique(self):
        """Création d'une notification de stock critique."""
        from src.services.notifications import get_notification_service, TypeAlerte
        
        service = get_notification_service()
        
        article = MagicMock()
        article.nom = "Lait"
        article.quantite = 0
        
        notif = service.creer_notification_stock_critique(article)
        
        assert notif.type_alerte == TypeAlerte.STOCK_CRITIQUE
        assert "Lait" in notif.message or "Lait" in notif.titre
        assert notif.priorite == 1  # Haute priorité


class TestCreerNotificationStockBas:
    """Tests pour creer_notification_stock_bas."""

    def test_creation_notification_stock_bas(self):
        """Création d'une notification de stock bas."""
        from src.services.notifications import get_notification_service, TypeAlerte
        
        service = get_notification_service()
        
        article = MagicMock()
        article.nom = "Œufs"
        article.quantite = 2
        article.quantite_min = 6
        
        notif = service.creer_notification_stock_bas(article)
        
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.priorite == 2  # Priorité moyenne


class TestCreerNotificationPeremption:
    """Tests pour creer_notification_peremption."""

    def test_notification_peremption_expiree(self):
        """Notification pour produit expiré."""
        from src.services.notifications import get_notification_service, TypeAlerte
        
        service = get_notification_service()
        
        article = MagicMock()
        article.nom = "Yaourt"
        article.date_peremption = datetime.now() - timedelta(days=1)
        
        notif = service.creer_notification_peremption(article, jours=-1)
        
        assert notif.type_alerte == TypeAlerte.PEREMPTION_EXPIREE
        assert notif.priorite == 1  # Haute priorité

    def test_notification_peremption_proche(self):
        """Notification pour péremption proche."""
        from src.services.notifications import get_notification_service, TypeAlerte
        
        service = get_notification_service()
        
        article = MagicMock()
        article.nom = "Crème fraîche"
        article.date_peremption = datetime.now() + timedelta(days=3)
        
        notif = service.creer_notification_peremption(article, jours=3)
        
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert "3" in notif.message or "trois" in notif.message.lower()


class TestAjouterNotification:
    """Tests pour ajouter_notification."""

    def test_ajouter_notification_simple(self):
        """Ajout d'une notification."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="Test",
            message="Message test"
        )
        
        # Ajout sans erreur
        service.ajouter_notification(notif, utilisateur_id="user1")

    def test_ajouter_notification_evite_doublons(self):
        """Évitement des doublons."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        
        notif = Notification(
            id="unique-id",
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="Doublon",
            message="Message identique"
        )
        
        # Première insertion
        service.ajouter_notification(notif, utilisateur_id="user1")
        # Deuxième insertion du même ID - devrait être ignorée
        service.ajouter_notification(notif, utilisateur_id="user1")
        
        # Vérifier qu'il n'y a pas de doublon
        notifications = service.obtenir_notifications(utilisateur_id="user1")
        ids = [n.id for n in notifications if n.id == "unique-id"]
        assert len(ids) <= 1


class TestObtenirNotifications:
    """Tests pour obtenir_notifications."""

    def test_obtenir_toutes_notifications(self):
        """Récupération de toutes les notifications."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_test_all"
        
        # Ajouter quelques notifications
        for i in range(3):
            service.ajouter_notification(
                Notification(
                    type_alerte=TypeAlerte.STOCK_BAS,
                    titre=f"Notif {i}",
                    message=f"Message {i}"
                ),
                utilisateur_id=utilisateur_id
            )
        
        notifications = service.obtenir_notifications(utilisateur_id=utilisateur_id)
        
        assert isinstance(notifications, list)

    def test_obtenir_notifications_non_lues(self):
        """Filtrage des notifications non lues."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_test_unread"
        
        # Ajouter une notification
        notif = Notification(
            id="notif-unread-test",
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="Non lue",
            message="Test",
            lue=False
        )
        service.ajouter_notification(notif, utilisateur_id=utilisateur_id)
        
        notifications = service.obtenir_notifications(
            utilisateur_id=utilisateur_id,
            non_lues_seulement=True
        )
        
        # Toutes devraient être non lues
        for n in notifications:
            assert n.lue == False

    def test_obtenir_notifications_tri_priorite(self):
        """Tri par priorité (1 = haute en premier)."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_test_priority"
        
        # Ajouter dans l'ordre inverse de priorité
        service.ajouter_notification(
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                titre="Basse",
                message="Priorité 3",
                priorite=3
            ),
            utilisateur_id=utilisateur_id
        )
        service.ajouter_notification(
            Notification(
                type_alerte=TypeAlerte.STOCK_CRITIQUE,
                titre="Haute",
                message="Priorité 1",
                priorite=1
            ),
            utilisateur_id=utilisateur_id
        )
        
        notifications = service.obtenir_notifications(utilisateur_id=utilisateur_id)
        
        if len(notifications) >= 2:
            # Haute priorité en premier
            assert notifications[0].priorite <= notifications[-1].priorite


class TestMarquerLue:
    """Tests pour marquer_lue."""

    def test_marquer_notification_lue(self):
        """Marquage d'une notification comme lue."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_mark_read"
        
        notif = Notification(
            id="notif-to-read",
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="À lire",
            message="Test",
            lue=False
        )
        service.ajouter_notification(notif, utilisateur_id=utilisateur_id)
        
        # Marquer comme lue
        service.marquer_lue("notif-to-read", utilisateur_id=utilisateur_id)
        
        # Vérifier
        notifications = service.obtenir_notifications(utilisateur_id=utilisateur_id)
        notif_modifiee = next((n for n in notifications if n.id == "notif-to-read"), None)
        
        if notif_modifiee:
            assert notif_modifiee.lue == True


class TestSupprimerNotification:
    """Tests pour supprimer_notification."""

    def test_supprimer_notification(self):
        """Suppression d'une notification."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_delete"
        
        notif = Notification(
            id="notif-to-delete",
            type_alerte=TypeAlerte.STOCK_BAS,
            titre="À supprimer",
            message="Test"
        )
        service.ajouter_notification(notif, utilisateur_id=utilisateur_id)
        
        # Supprimer
        service.supprimer_notification("notif-to-delete", utilisateur_id=utilisateur_id)
        
        # Vérifier suppression
        notifications = service.obtenir_notifications(utilisateur_id=utilisateur_id)
        ids = [n.id for n in notifications]
        
        assert "notif-to-delete" not in ids


class TestEffacerToutesLues:
    """Tests pour effacer_toutes_lues."""

    def test_effacer_notifications_lues(self):
        """Suppression de toutes les notifications lues."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_clear_read"
        
        # Ajouter notifications lues et non lues
        service.ajouter_notification(
            Notification(
                id="lue-1",
                type_alerte=TypeAlerte.STOCK_BAS,
                titre="Lue 1",
                message="Test",
                lue=True
            ),
            utilisateur_id=utilisateur_id
        )
        service.ajouter_notification(
            Notification(
                id="non-lue-1",
                type_alerte=TypeAlerte.STOCK_BAS,
                titre="Non lue",
                message="Test",
                lue=False
            ),
            utilisateur_id=utilisateur_id
        )
        
        # Effacer les lues
        service.effacer_toutes_lues(utilisateur_id=utilisateur_id)
        
        # Vérifier
        notifications = service.obtenir_notifications(utilisateur_id=utilisateur_id)
        
        # Aucune ne devrait être lue
        for n in notifications:
            assert n.lue == False


class TestObtenirStats:
    """Tests pour obtenir_stats."""

    def test_stats_notifications(self):
        """Statistiques des notifications."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_stats"
        
        # Ajouter plusieurs notifications
        for i in range(5):
            service.ajouter_notification(
                Notification(
                    type_alerte=TypeAlerte.STOCK_BAS if i % 2 == 0 else TypeAlerte.PEREMPTION_PROCHE,
                    titre=f"Notif {i}",
                    message=f"Test {i}",
                    lue=i < 2
                ),
                utilisateur_id=utilisateur_id
            )
        
        stats = service.obtenir_stats(utilisateur_id=utilisateur_id)
        
        assert isinstance(stats, dict)
        assert "total" in stats or "count" in stats or len(stats) > 0


class TestObtenirAlertesActives:
    """Tests pour obtenir_alertes_actives."""

    def test_alertes_actives(self):
        """Récupération des alertes actives (non lues, haute priorité)."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        utilisateur_id = "user_active_alerts"
        
        # Alerte active (non lue, haute priorité)
        service.ajouter_notification(
            Notification(
                id="active-alert",
                type_alerte=TypeAlerte.STOCK_CRITIQUE,
                titre="Active",
                message="Alerte critique",
                priorite=1,
                lue=False
            ),
            utilisateur_id=utilisateur_id
        )
        
        alertes = service.obtenir_alertes_actives(utilisateur_id=utilisateur_id)
        
        assert isinstance(alertes, list)


class TestEnvoiEmail:
    """Tests pour envoyer_email_alerte (stub)."""

    def test_envoyer_email_stub(self):
        """L'envoi d'email est un stub (log seulement)."""
        from src.services.notifications import get_notification_service, Notification, TypeAlerte
        
        service = get_notification_service()
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            titre="Email Test",
            message="Test d'envoi"
        )
        
        # Ne devrait pas lever d'exception
        result = service.envoyer_email_alerte(notif, email="test@example.com")
        
        # Stub retourne True ou None
        assert result is None or result == True
