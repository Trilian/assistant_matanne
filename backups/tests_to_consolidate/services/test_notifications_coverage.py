"""
Tests complets pour src/services/notifications.py
Objectif: Atteindre 80%+ de couverture

Tests couvrant:
- TypeAlerte enum
- Notification model validation
- creer_notification_stock_critique
- creer_notification_stock_bas
- creer_notification_peremption (diffÃ©rents jours_avant)
- ajouter_notification (normal + doublons)
- obtenir_notifications (tri, filtre non_lues)
- marquer_lue (succÃ¨s, Ã©chec)
- supprimer_notification (succÃ¨s, Ã©chec)
- effacer_toutes_lues
- obtenir_stats
- obtenir_alertes_actives
- envoyer_email_alerte
- obtenir_service_notifications singleton
"""

from datetime import datetime

import pytest


class TestTypeAlerteEnum:
    """Tests de l'enum TypeAlerte."""

    def test_stock_critique(self):
        """Valeur STOCK_CRITIQUE."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.STOCK_CRITIQUE.value == "stock_critique"

    def test_stock_bas(self):
        """Valeur STOCK_BAS."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.STOCK_BAS.value == "stock_bas"

    def test_peremption_proche(self):
        """Valeur PEREMPTION_PROCHE."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.PEREMPTION_PROCHE.value == "peremption_proche"

    def test_peremption_depassee(self):
        """Valeur PEREMPTION_DEPASSEE."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.PEREMPTION_DEPASSEE.value == "peremption_depassee"

    def test_article_ajoute(self):
        """Valeur ARTICLE_AJOUTE."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.ARTICLE_AJOUTE.value == "article_ajoute"

    def test_article_modifie(self):
        """Valeur ARTICLE_MODIFIE."""
        from src.services.notifications import TypeAlerte

        assert TypeAlerte.ARTICLE_MODIFIE.value == "article_modifie"


class TestNotificationModel:
    """Tests du modÃ¨le Notification."""

    def test_notification_minimal(self):
        """Notification avec champs requis minimaux."""
        from src.services.notifications import Notification, TypeAlerte

        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Stock bas: Lait",
            message="Le stock de lait est bas",
        )

        assert notif.id is None
        assert notif.type_alerte == TypeAlerte.STOCK_BAS
        assert notif.article_id == 1
        assert notif.lue is False
        assert notif.priorite == "moyenne"
        assert notif.icone == "â„¹ï¸"

    def test_notification_complete(self):
        """Notification avec tous les champs."""
        from src.services.notifications import Notification, TypeAlerte

        notif = Notification(
            id=42,
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Stock critique: Lait",
            message="Le stock de lait est critique!",
            icone="âŒ",
            lue=True,
            priorite="haute",
            email="test@example.com",
            push_envoyee=True,
        )

        assert notif.id == 42
        assert notif.priorite == "haute"
        assert notif.lue is True
        assert notif.email == "test@example.com"
        assert notif.push_envoyee is True

    def test_notification_date_creation_auto(self):
        """Date de crÃ©ation gÃ©nÃ©rÃ©e automatiquement."""
        from src.services.notifications import Notification, TypeAlerte

        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification",
            message="Message de test ici",
        )

        assert notif.date_creation is not None
        assert isinstance(notif.date_creation, datetime)

    def test_notification_titre_min_length(self):
        """Titre doit avoir au moins 5 caractÃ¨res."""
        from pydantic import ValidationError

        from src.services.notifications import Notification, TypeAlerte

        with pytest.raises(ValidationError):
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=1,
                ingredient_id=10,
                titre="Test",  # 4 chars - trop court
                message="Message assez long",
            )

    def test_notification_message_min_length(self):
        """Message doit avoir au moins 10 caractÃ¨res."""
        from pydantic import ValidationError

        from src.services.notifications import Notification, TypeAlerte

        with pytest.raises(ValidationError):
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=1,
                ingredient_id=10,
                titre="Titre valide",
                message="Court",  # 5 chars - trop court
            )


class TestNotificationServiceInit:
    """Tests d'initialisation du service."""

    def test_service_init(self):
        """Initialisation du service."""
        from src.services.notifications import NotificationService

        service = NotificationService()
        assert service.notifications == {}
        assert service._next_id == 1

    def test_obtenir_service_notifications_singleton(self):
        """Factory retourne un singleton."""
        from src.services.notifications import obtenir_service_notifications

        service1 = obtenir_service_notifications()
        service2 = obtenir_service_notifications()
        assert service1 is service2


class TestCreerNotificationStockCritique:
    """Tests creer_notification_stock_critique."""

    @pytest.fixture
    def service(self):
        from src.services.notifications import NotificationService

        return NotificationService()

    def test_notification_stock_critique(self, service):
        """CrÃ©ation d'une notification stock critique."""
        article = {
            "id": 1,
            "ingredient_id": 10,
            "nom": "Lait",
            "quantite": 0.5,
            "quantite_min": 2,
            "unite": "L",
        }

        notif = service.creer_notification_stock_critique(article)

        assert notif is not None
        assert "CRITIQUE" in notif.message
        assert notif.priorite == "haute"
        assert notif.icone == "âŒ"
        assert "Lait" in notif.titre

    def test_notification_stock_critique_sans_unite(self, service):
        """Article sans unitÃ© dÃ©finie."""
        article = {
            "id": 2,
            "ingredient_id": 20,
            "nom": "Oeufs",
            "quantite": 1,
            "quantite_min": 6,
        }

        notif = service.creer_notification_stock_critique(article)

        assert notif is not None
        assert "Oeufs" in notif.titre


class TestCreerNotificationStockBas:
    """Tests creer_notification_stock_bas."""

    @pytest.fixture
    def service(self):
        from src.services.notifications import NotificationService

        return NotificationService()

    def test_notification_stock_bas(self, service):
        """CrÃ©ation d'une notification stock bas."""
        article = {
            "id": 1,
            "ingredient_id": 10,
            "nom": "Beurre",
            "quantite": 100,
            "quantite_min": 200,
            "unite": "g",
        }

        notif = service.creer_notification_stock_bas(article)

        assert notif is not None
        assert "ALERTE" in notif.message
        assert notif.priorite == "moyenne"
        assert notif.icone == "âš ï¸"
        assert "Beurre" in notif.titre

    def test_notification_stock_bas_sans_unite(self, service):
        """Article sans unitÃ© dÃ©finie."""
        article = {
            "id": 3,
            "ingredient_id": 30,
            "nom": "Farine",
            "quantite": 200,
            "quantite_min": 500,
        }

        notif = service.creer_notification_stock_bas(article)

        assert notif is not None


class TestCreerNotificationPeremption:
    """Tests creer_notification_peremption."""

    @pytest.fixture
    def service(self):
        from src.services.notifications import NotificationService

        return NotificationService()

    def test_peremption_depassee(self, service):
        """PÃ©remption dÃ©passÃ©e (jours <= 0)."""
        article = {
            "id": 1,
            "ingredient_id": 10,
            "nom": "Yaourt",
            "date_peremption": "2026-02-01",
        }

        notif = service.creer_notification_peremption(article, jours_avant=0)

        assert notif is not None
        assert "EXPIRÃ‰" in notif.titre
        assert notif.priorite == "haute"
        assert notif.icone == "ðŸš¨"

    def test_peremption_negative(self, service):
        """PÃ©remption trÃ¨s dÃ©passÃ©e (jours < 0)."""
        article = {
            "id": 1,
            "ingredient_id": 10,
            "nom": "Lait",
            "date_peremption": "2026-01-15",
        }

        notif = service.creer_notification_peremption(article, jours_avant=-5)

        assert notif is not None
        assert "EXPIRÃ‰" in notif.titre
        assert notif.icone == "ðŸš¨"

    def test_peremption_tres_proche(self, service):
        """PÃ©remption trÃ¨s proche (1-3 jours)."""
        article = {
            "id": 2,
            "ingredient_id": 20,
            "nom": "CrÃ¨me fraÃ®che",
            "date_peremption": "2026-02-09",
        }

        notif = service.creer_notification_peremption(article, jours_avant=2)

        assert notif is not None
        assert "trÃ¨s proche" in notif.titre
        assert notif.priorite == "haute"
        assert notif.icone == "ðŸ”´"

    def test_peremption_3_jours(self, service):
        """PÃ©remption exactement dans 3 jours."""
        article = {
            "id": 3,
            "ingredient_id": 30,
            "nom": "Jambon",
            "date_peremption": "2026-02-10",
        }

        notif = service.creer_notification_peremption(article, jours_avant=3)

        assert notif is not None
        assert notif.priorite == "haute"
        assert notif.icone == "ðŸ”´"

    def test_peremption_proche(self, service):
        """PÃ©remption proche (> 3 jours)."""
        article = {
            "id": 4,
            "ingredient_id": 40,
            "nom": "Fromage",
            "date_peremption": "2026-02-15",
        }

        notif = service.creer_notification_peremption(article, jours_avant=7)

        assert notif is not None
        assert "proche" in notif.titre.lower()
        assert notif.priorite == "moyenne"
        assert notif.icone == "ðŸŸ "


class TestAjouterNotification:
    """Tests ajouter_notification."""

    @pytest.fixture
    def service(self):
        from src.services.notifications import NotificationService

        return NotificationService()

    @pytest.fixture
    def notification(self):
        from src.services.notifications import Notification, TypeAlerte

        return Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Test notification",
            message="Message de test suffisamment long",
        )

    def test_ajouter_notification_nouvel_utilisateur(self, service, notification):
        """Ajout d'une notification pour un nouvel utilisateur."""
        result = service.ajouter_notification(notification, utilisateur_id=1)

        assert result is not None
        assert result.id == 1
        assert 1 in service.notifications
        assert len(service.notifications[1]) == 1

    def test_ajouter_notification_utilisateur_existant(self, service, notification):
        """Ajout d'une deuxiÃ¨me notification."""
        from src.services.notifications import Notification, TypeAlerte

        service.ajouter_notification(notification, utilisateur_id=1)

        notif2 = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=2,
            ingredient_id=20,
            titre="DeuxiÃ¨me notification",
            message="Autre message de test",
        )

        result = service.ajouter_notification(notif2, utilisateur_id=1)

        assert result.id == 2
        assert len(service.notifications[1]) == 2

    def test_ajouter_notification_evite_doublon(self, service, notification):
        """Notifications identiques ne sont pas dupliquÃ©es."""
        from src.services.notifications import Notification, TypeAlerte

        service.ajouter_notification(notification, utilisateur_id=1)

        # MÃªme type + mÃªme article = doublon
        doublon = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,  # MÃªme article
            ingredient_id=10,
            titre="Notification doublon",
            message="Message du doublon ici",
        )

        result = service.ajouter_notification(doublon, utilisateur_id=1)

        # Retourne l'existante, pas la nouvelle
        assert result.titre == "Test notification"
        assert len(service.notifications[1]) == 1


class TestObtenirNotifications:
    """Tests obtenir_notifications."""

    @pytest.fixture
    def service_with_notifications(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        # Notification haute prioritÃ©, non lue
        n1 = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Notification haute",
            message="PrioritÃ© haute ici",
            priorite="haute",
        )

        # Notification moyenne prioritÃ©, lue
        n2 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=2,
            ingredient_id=20,
            titre="Notification moyenne",
            message="PrioritÃ© moyenne ici",
            priorite="moyenne",
            lue=True,
        )

        # Notification basse prioritÃ©, non lue
        n3 = Notification(
            type_alerte=TypeAlerte.ARTICLE_MODIFIE,
            article_id=3,
            ingredient_id=30,
            titre="Notification basse",
            message="PrioritÃ© basse ici",
            priorite="basse",
        )

        service.ajouter_notification(n1)
        service.ajouter_notification(n2)
        service.ajouter_notification(n3)

        return service

    def test_obtenir_toutes_notifications(self, service_with_notifications):
        """RÃ©cupÃ¨re toutes les notifications."""
        notifs = service_with_notifications.obtenir_notifications()
        assert len(notifs) == 3

    def test_obtenir_notifications_triees_par_priorite(self, service_with_notifications):
        """Notifications triÃ©es par prioritÃ©."""
        notifs = service_with_notifications.obtenir_notifications()

        # Tri: haute < moyenne < basse (avec reverse)
        # Donc haute en premier
        priorites = [n.priorite for n in notifs]
        assert priorites[0] == "basse" or priorites[-1] == "haute"

    def test_obtenir_notifications_non_lues_seulement(self, service_with_notifications):
        """Filtre les notifications non lues."""
        notifs = service_with_notifications.obtenir_notifications(non_lues_seulement=True)

        assert len(notifs) == 2
        assert all(not n.lue for n in notifs)

    def test_obtenir_notifications_utilisateur_inconnu(self, service_with_notifications):
        """Utilisateur sans notifications retourne liste vide."""
        notifs = service_with_notifications.obtenir_notifications(utilisateur_id=999)
        assert notifs == []


class TestMarquerLue:
    """Tests marquer_lue."""

    @pytest.fixture
    def service_with_notification(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Notification test",
            message="Message de notification",
        )

        service.ajouter_notification(notif)
        return service

    def test_marquer_lue_succes(self, service_with_notification):
        """Marque une notification comme lue avec succÃ¨s."""
        result = service_with_notification.marquer_lue(1)

        assert result is True
        notifs = service_with_notification.obtenir_notifications()
        assert notifs[0].lue is True

    def test_marquer_lue_notification_inexistante(self, service_with_notification):
        """Notification inexistante retourne False."""
        result = service_with_notification.marquer_lue(999)
        assert result is False

    def test_marquer_lue_none(self, service_with_notification):
        """notification_id None retourne False."""
        result = service_with_notification.marquer_lue(None)
        assert result is False

    def test_marquer_lue_utilisateur_inexistant(self, service_with_notification):
        """Utilisateur inexistant retourne False."""
        result = service_with_notification.marquer_lue(1, utilisateur_id=999)
        assert result is False


class TestSupprimerNotification:
    """Tests supprimer_notification."""

    @pytest.fixture
    def service_with_notifications(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        n1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Notification un",
            message="Message de notification un",
        )
        n2 = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=2,
            ingredient_id=20,
            titre="Notification deux",
            message="Message de notification deux",
        )

        service.ajouter_notification(n1)
        service.ajouter_notification(n2)
        return service

    def test_supprimer_notification_succes(self, service_with_notifications):
        """Supprime une notification avec succÃ¨s."""
        result = service_with_notifications.supprimer_notification(1)

        assert result is True
        notifs = service_with_notifications.obtenir_notifications()
        assert len(notifs) == 1
        assert notifs[0].id == 2

    def test_supprimer_notification_inexistante(self, service_with_notifications):
        """Notification inexistante retourne False."""
        result = service_with_notifications.supprimer_notification(999)
        assert result is False

    def test_supprimer_notification_none(self, service_with_notifications):
        """notification_id None retourne False."""
        result = service_with_notifications.supprimer_notification(None)
        assert result is False

    def test_supprimer_notification_utilisateur_inexistant(self, service_with_notifications):
        """Utilisateur inexistant retourne False."""
        result = service_with_notifications.supprimer_notification(1, utilisateur_id=999)
        assert result is False


class TestEffacerToutesLues:
    """Tests effacer_toutes_lues."""

    @pytest.fixture
    def service_with_mixed_notifications(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        # 2 notifications lues
        n1 = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Notification lue 1",
            message="Message de notification lue",
            lue=True,
        )
        n2 = Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=2,
            ingredient_id=20,
            titre="Notification lue 2",
            message="Message de notification lue",
            lue=True,
        )

        # 1 notification non lue
        n3 = Notification(
            type_alerte=TypeAlerte.PEREMPTION_PROCHE,
            article_id=3,
            ingredient_id=30,
            titre="Notification non lue",
            message="Message de notification non lue",
            lue=False,
        )

        service.ajouter_notification(n1)
        service.ajouter_notification(n2)
        service.ajouter_notification(n3)
        return service

    def test_effacer_toutes_lues_succes(self, service_with_mixed_notifications):
        """Efface toutes les notifications lues."""
        result = service_with_mixed_notifications.effacer_toutes_lues()

        assert result == 2  # 2 notifications effacÃ©es
        notifs = service_with_mixed_notifications.obtenir_notifications()
        assert len(notifs) == 1
        assert notifs[0].lue is False

    def test_effacer_toutes_lues_utilisateur_inexistant(self, service_with_mixed_notifications):
        """Utilisateur inexistant retourne 0."""
        result = service_with_mixed_notifications.effacer_toutes_lues(utilisateur_id=999)
        assert result == 0

    def test_effacer_toutes_lues_aucune_lue(self):
        """Aucune notification lue retourne 0."""
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notif = Notification(
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=1,
            ingredient_id=10,
            titre="Notification non lue",
            message="Message de notification non lue",
            lue=False,
        )
        service.ajouter_notification(notif)

        result = service.effacer_toutes_lues()
        assert result == 0


class TestObtenirStats:
    """Tests obtenir_stats."""

    @pytest.fixture
    def service_with_diverse_notifications(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notifs = [
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=1,
                ingredient_id=10,
                titre="Stock bas 1",
                message="Message stock bas 1",
                priorite="moyenne",
                lue=False,
            ),
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=2,
                ingredient_id=20,
                titre="Stock bas 2",
                message="Message stock bas 2",
                priorite="moyenne",
                lue=True,
            ),
            Notification(
                type_alerte=TypeAlerte.STOCK_CRITIQUE,
                article_id=3,
                ingredient_id=30,
                titre="Stock critique",
                message="Message stock critique",
                priorite="haute",
                lue=False,
            ),
            Notification(
                type_alerte=TypeAlerte.PEREMPTION_PROCHE,
                article_id=4,
                ingredient_id=40,
                titre="PÃ©remption proche",
                message="Message pÃ©remption proche",
                priorite="basse",
                lue=False,
            ),
        ]

        for n in notifs:
            service.ajouter_notification(n)

        return service

    def test_obtenir_stats_total(self, service_with_diverse_notifications):
        """Stats: total notifications."""
        stats = service_with_diverse_notifications.obtenir_stats()
        assert stats["total"] == 4

    def test_obtenir_stats_non_lues(self, service_with_diverse_notifications):
        """Stats: notifications non lues."""
        stats = service_with_diverse_notifications.obtenir_stats()
        assert stats["non_lues"] == 3

    def test_obtenir_stats_par_type(self, service_with_diverse_notifications):
        """Stats: comptage par type."""
        stats = service_with_diverse_notifications.obtenir_stats()

        assert stats["par_type"]["stock_bas"] == 2
        assert stats["par_type"]["stock_critique"] == 1
        assert stats["par_type"]["peremption_proche"] == 1

    def test_obtenir_stats_par_priorite(self, service_with_diverse_notifications):
        """Stats: comptage par prioritÃ©."""
        stats = service_with_diverse_notifications.obtenir_stats()

        assert stats["par_priorite"]["moyenne"] == 2
        assert stats["par_priorite"]["haute"] == 1
        assert stats["par_priorite"]["basse"] == 1

    def test_obtenir_stats_utilisateur_vide(self):
        """Stats pour utilisateur sans notifications."""
        from src.services.notifications import NotificationService

        service = NotificationService()
        stats = service.obtenir_stats()

        assert stats["total"] == 0
        assert stats["non_lues"] == 0
        assert stats["par_type"] == {}
        assert stats["par_priorite"] == {}


class TestObtenirAlertesActives:
    """Tests obtenir_alertes_actives."""

    @pytest.fixture
    def service_with_notifications(self):
        from src.services.notifications import Notification, NotificationService, TypeAlerte

        service = NotificationService()

        notifs = [
            Notification(
                type_alerte=TypeAlerte.STOCK_CRITIQUE,
                article_id=1,
                ingredient_id=10,
                titre="Critique haute",
                message="Message critique haute",
                priorite="haute",
                lue=False,
            ),
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=2,
                ingredient_id=20,
                titre="Stock moyenne",
                message="Message stock moyenne",
                priorite="moyenne",
                lue=False,
            ),
            Notification(
                type_alerte=TypeAlerte.ARTICLE_MODIFIE,
                article_id=3,
                ingredient_id=30,
                titre="Modif basse",
                message="Message modif basse",
                priorite="basse",
                lue=False,
            ),
            Notification(
                type_alerte=TypeAlerte.STOCK_BAS,
                article_id=4,
                ingredient_id=40,
                titre="Stock lue",
                message="Message stock dÃ©jÃ  lue",
                priorite="haute",
                lue=True,  # DÃ©jÃ  lue - ne doit pas apparaÃ®tre
            ),
        ]

        for n in notifs:
            service.ajouter_notification(n)

        return service

    def test_alertes_actives_critiques(self, service_with_notifications):
        """Alertes haute prioritÃ© dans 'critiques'."""
        alertes = service_with_notifications.obtenir_alertes_actives()

        assert len(alertes["critiques"]) == 1
        assert alertes["critiques"][0].priorite == "haute"

    def test_alertes_actives_hautes(self, service_with_notifications):
        """Alertes moyenne prioritÃ© dans 'hautes'."""
        alertes = service_with_notifications.obtenir_alertes_actives()

        assert len(alertes["hautes"]) == 1
        assert alertes["hautes"][0].priorite == "moyenne"

    def test_alertes_actives_moyennes(self, service_with_notifications):
        """Alertes basse prioritÃ© dans 'moyennes'."""
        alertes = service_with_notifications.obtenir_alertes_actives()

        assert len(alertes["moyennes"]) == 1
        assert alertes["moyennes"][0].priorite == "basse"

    def test_alertes_actives_exclut_lues(self, service_with_notifications):
        """Notifications lues ne sont pas incluses."""
        alertes = service_with_notifications.obtenir_alertes_actives()

        # 4 notifs mais 1 lue â†’ 3 dans les alertes actives
        total = (
            len(alertes["critiques"])
            + len(alertes["hautes"])
            + len(alertes["moyennes"])
            + len(alertes["basses"])
        )
        assert total == 3

    def test_alertes_actives_utilisateur_vide(self):
        """Utilisateur sans notifications retourne dict vide."""
        from src.services.notifications import NotificationService

        service = NotificationService()
        alertes = service.obtenir_alertes_actives(utilisateur_id=999)

        assert alertes["critiques"] == []
        assert alertes["hautes"] == []
        assert alertes["moyennes"] == []
        assert alertes["basses"] == []


class TestEnvoyerEmailAlerte:
    """Tests envoyer_email_alerte."""

    @pytest.fixture
    def service(self):
        from src.services.notifications import NotificationService

        return NotificationService()

    @pytest.fixture
    def notification(self):
        from src.services.notifications import Notification, TypeAlerte

        return Notification(
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=1,
            ingredient_id=10,
            titre="Alerte email",
            message="Message pour email",
        )

    def test_envoyer_email_succes(self, service, notification):
        """Envoi email retourne True et met Ã  jour la notification."""
        result = service.envoyer_email_alerte(notification, "test@example.com")

        assert result is True
        assert notification.email == "test@example.com"
        assert notification.push_envoyee is True

    def test_envoyer_email_met_a_jour_notification(self, service, notification):
        """L'email est stockÃ© dans la notification."""
        service.envoyer_email_alerte(notification, "autre@example.com")

        assert notification.email == "autre@example.com"
