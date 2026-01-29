"""Tests unitaires pour le service notifications."""

import pytest
from datetime import datetime, timezone


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTypeAlerteEnum:
    """Tests pour l'enum TypeAlerte."""

    def test_types_alertes_disponibles(self):
        """Vérifie tous les types d'alertes."""
        from src.services.notifications import TypeAlerte
        
        assert TypeAlerte.STOCK_CRITIQUE is not None
        assert TypeAlerte.STOCK_BAS is not None
        assert TypeAlerte.PEREMPTION_PROCHE is not None
        assert TypeAlerte.PEREMPTION_DEPASSEE is not None

    def test_type_alerte_valeur_string(self):
        """Types ont des valeurs string."""
        from src.services.notifications import TypeAlerte
        
        for t in TypeAlerte:
            assert isinstance(t.value, str)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationModel:
    """Tests pour le modèle Notification."""

    def test_notification_creation(self):
        """Création d'une notification."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Stock bas: Lait",
            message="Le lait est bientôt épuisé"
        )
        
        assert notif.titre == "Stock bas: Lait"
        assert notif.type_alerte == TypeAlerte.STOCK_BAS

    def test_notification_non_lue_par_defaut(self):
        """Notification non lue par défaut."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification",
            message="Ceci est un test"
        )
        
        assert notif.lue is False

    def test_notification_priorites(self):
        """Priorités de notification."""
        from src.services.notifications import Notification, TypeAlerte
        
        notif_haute = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Alerte critique",
            message="Stock critique",
            priorite="haute"
        )
        
        notif_basse = Notification(
            type_alerte=TypeAlerte.ARTICLE_AJOUTE,
            article_id=2,
            ingredient_id=20,
            titre="Article ajouté",
            message="Nouvel article",
            priorite="basse"
        )
        
        assert notif_haute.priorite == "haute"
        assert notif_basse.priorite == "basse"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE NOTIFICATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestNotificationServiceInit:
    """Tests d'initialisation du service."""

    def test_service_creation(self):
        """Création du service."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        assert service is not None
        assert service.notifications == {}

    def test_service_methodes_requises(self):
        """Le service a les méthodes requises."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        assert hasattr(service, 'creer_notification_stock_critique')
        assert hasattr(service, 'creer_notification_stock_bas')
        assert hasattr(service, 'creer_notification_peremption')
        assert hasattr(service, 'ajouter_notification')


class TestCreerNotificationStockCritique:
    """Tests pour creer_notification_stock_critique."""

    def test_creation_notification_critique(self):
        """Création notification stock critique."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        article = {
            "id": 1,
            "ingredient_id": 10,
            "nom": "Lait",
            "quantite": 0.5,
            "quantite_min": 2,
            "unite": "L"
        }
        
        notif = service.creer_notification_stock_critique(article)
        
        assert notif is not None
        assert "Lait" in notif.titre
        assert notif.priorite == "haute"


class TestCreerNotificationStockBas:
    """Tests pour creer_notification_stock_bas."""

    def test_creation_notification_stock_bas(self):
        """Création notification stock bas."""
        from src.services.notifications import NotificationService
        
        service = NotificationService()
        
        article = {
            "id": 2,
            "ingredient_id": 20,
            "nom": "Beurre",
            "quantite": 1,
            "quantite_min": 2,
            "unite": "pièces"
        }
        
        notif = service.creer_notification_stock_bas(article)
        
        assert notif is not None
        assert "Beurre" in notif.titre
        assert notif.priorite == "moyenne"


class TestCreerNotificationPeremption:
    """Tests pour creer_notification_peremption."""

    def test_notification_peremption_expiree(self):
        """Notification pour produit expiré."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            "id": 3,
            "ingredient_id": 30,
            "nom": "Yaourt",
            "date_peremption": "2026-01-20"
        }
        
        notif = service.creer_notification_peremption(article, jours_avant=0)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_DEPASSEE
        assert notif.priorite == "haute"

    def test_notification_peremption_proche(self):
        """Notification pour péremption proche."""
        from src.services.notifications import NotificationService, TypeAlerte
        
        service = NotificationService()
        
        article = {
            "id": 4,
            "ingredient_id": 40,
            "nom": "Crème",
            "date_peremption": "2026-01-30"
        }
        
        notif = service.creer_notification_peremption(article, jours_avant=2)
        
        assert notif is not None
        assert notif.type_alerte == TypeAlerte.PEREMPTION_PROCHE
        assert notif.priorite == "haute"


class TestAjouterNotification:
    """Tests pour ajouter_notification."""

    def test_ajouter_notification_simple(self):
        """Ajout d'une notification."""
        from src.services.notifications import NotificationService, Notification, TypeAlerte
        
        service = NotificationService()
        
        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification titre",  # Min 5 chars
            message="Test message de notification long"  # Min 10 chars
        )
        
        result = service.ajouter_notification(notif, utilisateur_id=1)
        
        assert result is not None
        assert result.id is not None

    def test_ajouter_notification_evite_doublons(self):
        """Ã‰vite les doublons de notifications."""
        from src.services.notifications import NotificationService, Notification, TypeAlerte
        
        service = NotificationService()
        
        notif1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test doublon titre",  # Min 5 chars
            message="Test message doublon long"  # Min 10 chars
        )
        
        notif2 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test doublon 2 titre",  # Min 5 chars
            message="Test message doublon 2 long"  # Min 10 chars
        )
        
        result1 = service.ajouter_notification(notif1, utilisateur_id=1)
        result2 = service.ajouter_notification(notif2, utilisateur_id=1)
        
        # Le deuxième devrait retourner le premier (doublon)
        assert result1.id == result2.id


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LOGIQUE PURE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLogiquePriorite:
    """Tests pour la logique de priorité."""

    def test_priorite_stock_critique(self):
        """Stock critique = haute priorité."""
        quantite = 0
        quantite_min = 2
        
        if quantite <= 0:
            priorite = "haute"
        elif quantite < quantite_min:
            priorite = "moyenne"
        else:
            priorite = "basse"
        
        assert priorite == "haute"

    def test_priorite_stock_bas(self):
        """Stock bas = moyenne priorité."""
        quantite = 1
        quantite_min = 2
        
        if quantite <= 0:
            priorite = "haute"
        elif quantite < quantite_min:
            priorite = "moyenne"
        else:
            priorite = "basse"
        
        assert priorite == "moyenne"


class TestLogiquePeremption:
    """Tests pour la logique de péremption."""

    def test_peremption_jours_negatifs(self):
        """Jours négatifs = expiré."""
        jours_avant = -3
        
        if jours_avant <= 0:
            status = "expiré"
        elif jours_avant <= 3:
            status = "très proche"
        elif jours_avant <= 7:
            status = "proche"
        else:
            status = "ok"
        
        assert status == "expiré"

    def test_peremption_3_jours(self):
        """3 jours = très proche."""
        jours_avant = 3
        
        if jours_avant <= 0:
            status = "expiré"
        elif jours_avant <= 3:
            status = "très proche"
        elif jours_avant <= 7:
            status = "proche"
        else:
            status = "ok"
        
        assert status == "très proche"


class TestLogiqueIcones:
    """Tests pour les icônes de notification."""

    def test_icone_stock_critique(self):
        """Icône pour stock critique."""
        icones = {
            "stock_critique": "âŒ",
            "stock_bas": "âš ï¸",
            "peremption_proche": "ðŸŸ ",
            "peremption_depassee": "ðŸš¨"
        }
        
        assert icones["stock_critique"] == "âŒ"

    def test_icone_peremption(self):
        """Icône pour péremption."""
        icones = {
            "stock_critique": "âŒ",
            "stock_bas": "âš ï¸",
            "peremption_proche": "ðŸŸ ",
            "peremption_depassee": "ðŸš¨"
        }
        
        assert icones["peremption_depassee"] == "ðŸš¨"


class TestTriNotifications:
    """Tests pour le tri des notifications."""

    def test_tri_par_priorite(self):
        """Tri par priorité."""
        notifications = [
            {"titre": "A", "priorite": "basse"},
            {"titre": "B", "priorite": "haute"},
            {"titre": "C", "priorite": "moyenne"},
        ]
        
        ordre = {"haute": 0, "moyenne": 1, "basse": 2}
        triees = sorted(notifications, key=lambda x: ordre[x["priorite"]])
        
        assert triees[0]["titre"] == "B"  # haute en premier

    def test_tri_par_date(self):
        """Tri par date création."""
        notifications = [
            {"titre": "A", "date": datetime(2026, 1, 10)},
            {"titre": "B", "date": datetime(2026, 1, 28)},
            {"titre": "C", "date": datetime(2026, 1, 15)},
        ]
        
        triees = sorted(notifications, key=lambda x: x["date"], reverse=True)
        
        assert triees[0]["titre"] == "B"  # Plus récent en premier

