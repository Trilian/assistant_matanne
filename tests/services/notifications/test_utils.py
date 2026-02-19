"""Tests pour src/services/notifications/utils.py - Fonctions utilitaires.

Couverture des fonctionnalités:
- Vérification des préférences de notification
- Gestion des heures silencieuses
- Construction de payloads
- Création de notifications prédéfinies
- Compteur et validation
"""

from datetime import datetime

import pytest

from src.services.core.notifications.types import TypeNotification
from src.services.core.notifications.utils import (
    # Alias rétrocompatibilité
    NotificationType,
    can_send_during_quiet_hours,
    construire_info_abonnement,
    # Payloads
    construire_payload_push,
    creer_notification_liste_partagee,
    creer_notification_peremption,
    creer_notification_rappel_activite,
    creer_notification_rappel_jalon,
    creer_notification_rappel_repas,
    # Notifications prédéfinies
    creer_notification_stock,
    doit_envoyer_notification,
    doit_reinitialiser_compteur,
    # Heures silencieuses
    est_heures_silencieuses,
    # Compteur
    generer_cle_compteur,
    is_quiet_hours,
    # Mapping et vérification
    obtenir_mapping_types_notification,
    parser_cle_compteur,
    peut_envoyer_pendant_silence,
    # Validation
    valider_abonnement,
    valider_preferences,
    verifier_type_notification_active,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def default_preferences():
    """Préférences par défaut."""
    return {
        "alertes_stock": True,
        "alertes_peremption": True,
        "rappels_repas": True,
        "rappels_activites": True,
        "mises_a_jour_courses": True,
        "rappels_famille": True,
        "mises_a_jour_systeme": False,
        "heures_silencieuses_debut": 22,
        "heures_silencieuses_fin": 7,
        "max_par_heure": 5,
    }


@pytest.fixture
def disabled_preferences():
    """Préférences avec certains types désactivés."""
    return {
        "alertes_stock": False,
        "alertes_peremption": True,
        "rappels_repas": False,
        "rappels_activites": True,
        "mises_a_jour_courses": False,
        "rappels_famille": True,
        "mises_a_jour_systeme": True,
        "heures_silencieuses_debut": None,
        "heures_silencieuses_fin": None,
        "max_par_heure": 10,
    }


# ═══════════════════════════════════════════════════════════
# TESTS MAPPING ET VÉRIFICATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestObtenirMappingTypesNotification:
    """Tests pour obtenir_mapping_types_notification."""

    def test_mapping_contient_types_principaux(self):
        """Les types principaux sont dans le mapping."""
        mapping = obtenir_mapping_types_notification()

        assert TypeNotification.STOCK_BAS in mapping
        assert TypeNotification.PEREMPTION_ALERTE in mapping
        assert TypeNotification.RAPPEL_REPAS in mapping

    def test_mapping_valeurs(self):
        """Les valeurs correspondent aux préférences utilisateur."""
        mapping = obtenir_mapping_types_notification()

        assert mapping[TypeNotification.STOCK_BAS] == "alertes_stock"
        assert mapping[TypeNotification.PEREMPTION_ALERTE] == "alertes_peremption"
        assert mapping[TypeNotification.RAPPEL_REPAS] == "rappels_repas"


@pytest.mark.unit
class TestVerifierTypeNotificationActive:
    """Tests pour verifier_type_notification_active."""

    def test_type_actif(self, default_preferences):
        """Type activé dans préférences."""
        result = verifier_type_notification_active(TypeNotification.STOCK_BAS, default_preferences)
        assert result is True

    def test_type_desactive(self, disabled_preferences):
        """Type désactivé dans préférences."""
        result = verifier_type_notification_active(TypeNotification.STOCK_BAS, disabled_preferences)
        assert result is False

    def test_type_string(self, default_preferences):
        """Type passé en string."""
        result = verifier_type_notification_active("stock_bas", default_preferences)
        assert result is True

    def test_type_inconnu_actif_par_defaut(self, default_preferences):
        """Type inconnu retourne True par défaut."""
        result = verifier_type_notification_active("type_inexistant", default_preferences)
        assert result is True

    def test_type_sans_preference_actif(self, default_preferences):
        """Type sans préférence associée retourne True."""
        result = verifier_type_notification_active(
            TypeNotification.SYNC_TERMINEE,
            {},  # Pas de préférences
        )
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS HEURES SILENCIEUSES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEstHeuresSilencieuses:
    """Tests pour est_heures_silencieuses."""

    def test_heure_dans_plage_normale(self):
        """Heure dans plage normale (1h-6h)."""
        assert est_heures_silencieuses(3, heure_debut=1, heure_fin=6) is True

    def test_heure_hors_plage_normale(self):
        """Heure hors plage normale."""
        assert est_heures_silencieuses(10, heure_debut=1, heure_fin=6) is False

    def test_heure_debut_plage(self):
        """Heure exacte de début."""
        assert est_heures_silencieuses(22, heure_debut=22, heure_fin=7) is True

    def test_heure_fin_plage_exclusive(self):
        """Heure de fin est exclusive."""
        assert est_heures_silencieuses(6, heure_debut=1, heure_fin=6) is False

    def test_plage_passant_minuit(self):
        """Plage passant par minuit (22h -> 7h)."""
        # Heures de nuit
        assert est_heures_silencieuses(23, heure_debut=22, heure_fin=7) is True
        assert est_heures_silencieuses(0, heure_debut=22, heure_fin=7) is True
        assert est_heures_silencieuses(5, heure_debut=22, heure_fin=7) is True
        # Heures de jour
        assert est_heures_silencieuses(8, heure_debut=22, heure_fin=7) is False
        assert est_heures_silencieuses(14, heure_debut=22, heure_fin=7) is False

    def test_pas_de_plage(self):
        """Pas de plage silencieuse définie."""
        assert est_heures_silencieuses(3, heure_debut=None, heure_fin=None) is False
        assert est_heures_silencieuses(3, heure_debut=None, heure_fin=7) is False
        assert est_heures_silencieuses(3, heure_debut=22, heure_fin=None) is False

    def test_heure_invalide(self):
        """Heure invalide (hors 0-23)."""
        assert est_heures_silencieuses(-1, heure_debut=22, heure_fin=7) is False
        assert est_heures_silencieuses(24, heure_debut=22, heure_fin=7) is False


@pytest.mark.unit
class TestPeutEnvoyerPendantSilence:
    """Tests pour peut_envoyer_pendant_silence."""

    def test_peremption_critique_peut_passer(self):
        """Les alertes critiques passent pendant le silence."""
        result = peut_envoyer_pendant_silence(TypeNotification.PEREMPTION_CRITIQUE)
        assert result is True

    def test_stock_bas_ne_passe_pas(self):
        """Stock bas ne passe pas pendant silence."""
        result = peut_envoyer_pendant_silence(TypeNotification.STOCK_BAS)
        assert result is False

    def test_rappel_repas_ne_passe_pas(self):
        """Rappel repas ne passe pas pendant silence."""
        result = peut_envoyer_pendant_silence(TypeNotification.RAPPEL_REPAS)
        assert result is False

    def test_type_string(self):
        """Type passé en string."""
        result = peut_envoyer_pendant_silence("expiration_critical")
        assert result is True

    def test_type_inconnu(self):
        """Type inconnu ne passe pas."""
        result = peut_envoyer_pendant_silence("type_inconnu")
        assert result is False


@pytest.mark.unit
class TestDoitEnvoyerNotification:
    """Tests pour doit_envoyer_notification."""

    def test_doit_envoyer_type_actif(self, default_preferences):
        """Doit envoyer si type actif."""
        result, raison = doit_envoyer_notification(
            TypeNotification.STOCK_BAS,
            default_preferences,
            heure_courante=10,  # Hors heures silencieuses
            nombre_envoyes_cette_heure=0,
        )
        assert result is True
        assert raison == ""

    def test_ne_pas_envoyer_type_desactive(self, disabled_preferences):
        """Ne pas envoyer si type désactivé."""
        result, raison = doit_envoyer_notification(
            TypeNotification.STOCK_BAS, disabled_preferences, heure_courante=10
        )
        assert result is False
        assert "désactivé" in raison

    def test_ne_pas_envoyer_heures_silencieuses(self, default_preferences):
        """Ne pas envoyer pendant heures silencieuses."""
        result, raison = doit_envoyer_notification(
            TypeNotification.STOCK_BAS,
            default_preferences,
            heure_courante=3,  # Dans plage silencieuse (22h-7h)
        )
        assert result is False
        assert "silencieuses" in raison

    def test_envoyer_critique_pendant_silence(self, default_preferences):
        """Envoyer critique même pendant silence."""
        result, raison = doit_envoyer_notification(
            TypeNotification.PEREMPTION_CRITIQUE,
            default_preferences,
            heure_courante=3,  # Dans plage silencieuse
        )
        assert result is True

    def test_limite_par_heure_atteinte(self, default_preferences):
        """Ne pas envoyer si limite par heure atteinte."""
        result, raison = doit_envoyer_notification(
            TypeNotification.STOCK_BAS,
            default_preferences,
            heure_courante=10,
            nombre_envoyes_cette_heure=5,  # max_par_heure = 5
        )
        assert result is False
        assert "Limite" in raison

    def test_heure_courante_auto(self, default_preferences):
        """Heure courante automatique si None."""
        # Doit s'exécuter sans erreur
        result, raison = doit_envoyer_notification(
            TypeNotification.STOCK_BAS, default_preferences, heure_courante=None
        )
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════
# TESTS CONSTRUCTION PAYLOADS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestConstruirePayloadPush:
    """Tests pour construire_payload_push."""

    def test_payload_minimal(self):
        """Payload avec données minimales."""
        notification = {"title": "Test", "body": "Corps du message"}

        payload = construire_payload_push(notification)

        assert "Test" in payload
        assert "Corps du message" in payload

    def test_payload_complet(self):
        """Payload avec toutes les données."""
        notification = {
            "title": "Alerte Stock",
            "body": "Lait presque épuisé",
            "icon": "/icon.png",
            "url": "/inventaire",
            "notification_type": "stock_bas",
            "tag": "stock_lait",
            "actions": [{"action": "ajouter", "title": "OK"}],
            "require_interaction": True,
        }

        payload = construire_payload_push(notification)

        assert "Alerte Stock" in payload
        assert "Lait presque épuisé" in payload
        assert "/icon.png" in payload

    def test_payload_avec_timestamp(self):
        """Payload avec timestamp datetime."""
        now = datetime(2024, 1, 15, 10, 30, 0)
        notification = {"title": "Test", "body": "Test", "timestamp": now}

        payload = construire_payload_push(notification)

        assert "2024-01-15" in payload


@pytest.mark.unit
class TestConstruireInfoAbonnement:
    """Tests pour construire_info_abonnement."""

    def test_construire_info_valide(self):
        """Construction avec données valides."""
        subscription = {
            "endpoint": "https://push.example.com/abc",
            "p256dh_key": "key123",
            "auth_key": "auth456",
        }

        info = construire_info_abonnement(subscription)

        assert info["endpoint"] == "https://push.example.com/abc"
        assert info["keys"]["p256dh"] == "key123"
        assert info["keys"]["auth"] == "auth456"

    def test_construire_info_vide(self):
        """Construction avec données vides."""
        info = construire_info_abonnement({})

        assert info["endpoint"] == ""
        assert info["keys"]["p256dh"] == ""
        assert info["keys"]["auth"] == ""


# ═══════════════════════════════════════════════════════════
# TESTS NOTIFICATIONS PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCreerNotificationStock:
    """Tests pour creer_notification_stock."""

    def test_notification_stock(self):
        """Création notification stock bas."""
        notif = creer_notification_stock("Lait", 0.5, "L")

        assert notif["title"] == "📦 Stock bas"
        assert "Lait" in notif["body"]
        assert "0.5 L" in notif["body"]
        assert notif["notification_type"] == TypeNotification.STOCK_BAS.value
        assert "inventaire" in notif["url"]

    def test_notification_stock_sans_unite(self):
        """Création notification stock sans unité."""
        notif = creer_notification_stock("Oeufs", 3)

        assert "3" in notif["body"]


@pytest.mark.unit
class TestCreerNotificationPeremption:
    """Tests pour creer_notification_peremption."""

    def test_peremption_expiree(self):
        """Notification produit expiré."""
        notif = creer_notification_peremption("Yaourt", -2)

        assert "périmé" in notif["title"].lower() or "périmé" in notif["body"].lower()
        assert notif["notification_type"] == TypeNotification.PEREMPTION_CRITIQUE.value

    def test_peremption_demain(self):
        """Notification péremption demain."""
        notif = creer_notification_peremption("Lait", 1)

        assert "demain" in notif["title"]
        assert "Lait" in notif["body"]

    def test_peremption_proche(self):
        """Notification péremption proche."""
        notif = creer_notification_peremption("Fromage", 5)

        assert "5 jours" in notif["body"]
        assert notif["notification_type"] == TypeNotification.PEREMPTION_ALERTE.value


@pytest.mark.unit
class TestCreerNotificationRappelRepas:
    """Tests pour creer_notification_rappel_repas."""

    def test_rappel_repas(self):
        """Création rappel repas."""
        notif = creer_notification_rappel_repas("Déjeuner", "Pâtes carbonara", "30 min")

        assert "Déjeuner" in notif["title"]
        assert "30 min" in notif["title"]
        assert "Pâtes carbonara" in notif["body"]
        assert notif["notification_type"] == TypeNotification.RAPPEL_REPAS.value


@pytest.mark.unit
class TestCreerNotificationListePartagee:
    """Tests pour creer_notification_liste_partagee."""

    def test_liste_partagee(self):
        """Création notification liste partagée."""
        notif = creer_notification_liste_partagee("Alice", "Courses weekend")

        assert "Alice" in notif["body"]
        assert "Courses weekend" in notif["body"]
        assert notif["notification_type"] == TypeNotification.LISTE_PARTAGEE.value


@pytest.mark.unit
class TestCreerNotificationRappelActivite:
    """Tests pour creer_notification_rappel_activite."""

    def test_rappel_activite_sans_lieu(self):
        """Rappel activité sans lieu."""
        notif = creer_notification_rappel_activite("Piscine", "1h")

        assert "Piscine" in notif["body"]
        assert "1h" in notif["body"]
        assert notif["notification_type"] == TypeNotification.RAPPEL_ACTIVITE.value

    def test_rappel_activite_avec_lieu(self):
        """Rappel activité avec lieu."""
        notif = creer_notification_rappel_activite("Piscine", "1h", lieu="Centre aquatique")

        assert "Centre aquatique" in notif["body"]


@pytest.mark.unit
class TestCreerNotificationRappelJalon:
    """Tests pour creer_notification_rappel_jalon."""

    def test_rappel_jalon(self):
        """Création rappel jalon enfant."""
        notif = creer_notification_rappel_jalon("Jules", "Motricité", "Premier pas")

        assert "Jules" in notif["title"]
        assert "Motricité" in notif["body"]
        assert "Premier pas" in notif["body"]
        assert notif["notification_type"] == TypeNotification.RAPPEL_JALON.value


# ═══════════════════════════════════════════════════════════
# TESTS COMPTEUR
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenererCleCompteur:
    """Tests pour generer_cle_compteur."""

    def test_generer_cle_avec_datetime(self):
        """Génère clé avec datetime fourni."""
        dt = datetime(2024, 1, 15, 14, 30)
        cle = generer_cle_compteur("user123", dt)

        assert cle == "user123_2024011514"

    def test_generer_cle_auto(self):
        """Génère clé avec datetime auto."""
        cle = generer_cle_compteur("user456")

        assert cle.startswith("user456_")
        assert len(cle) == len("user456_2024011514")


@pytest.mark.unit
class TestParserCleCompteur:
    """Tests pour parser_cle_compteur."""

    def test_parser_cle_valide(self):
        """Parse clé valide."""
        user_id, dt = parser_cle_compteur("user123_2024011514")

        assert user_id == "user123"
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 14

    def test_parser_cle_sans_underscore(self):
        """Parse clé sans underscore."""
        user_id, dt = parser_cle_compteur("user123")

        assert user_id == "user123"
        assert dt is None

    def test_parser_cle_datetime_invalide(self):
        """Parse clé avec datetime invalide."""
        user_id, dt = parser_cle_compteur("user123_invalid")

        assert user_id == "user123"
        assert dt is None


@pytest.mark.unit
class TestDoitReinitialiserCompteur:
    """Tests pour doit_reinitialiser_compteur."""

    def test_meme_heure(self):
        """Ne pas réinitialiser si même heure."""
        result = doit_reinitialiser_compteur("user_2024011514", "user_2024011514")
        assert result is False

    def test_heure_differente(self):
        """Réinitialiser si heure différente."""
        result = doit_reinitialiser_compteur("user_2024011514", "user_2024011515")
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestValiderAbonnement:
    """Tests pour valider_abonnement."""

    def test_abonnement_valide(self):
        """Abonnement valide."""
        subscription = {
            "endpoint": "https://push.example.com/abc",
            "keys": {
                "p256dh": "key123",
                "auth": "auth456",
            },
        }

        is_valid, error = valider_abonnement(subscription)

        assert is_valid is True
        assert error == ""

    def test_endpoint_manquant(self):
        """Endpoint manquant."""
        subscription = {"keys": {"p256dh": "key", "auth": "auth"}}

        is_valid, error = valider_abonnement(subscription)

        assert is_valid is False
        assert "Endpoint" in error

    def test_endpoint_non_https(self):
        """Endpoint non HTTPS."""
        subscription = {
            "endpoint": "http://push.example.com",
            "keys": {"p256dh": "key", "auth": "auth"},
        }

        is_valid, error = valider_abonnement(subscription)

        assert is_valid is False
        assert "HTTPS" in error

    def test_cle_p256dh_manquante(self):
        """Clé p256dh manquante."""
        subscription = {"endpoint": "https://push.example.com", "keys": {"auth": "auth"}}

        is_valid, error = valider_abonnement(subscription)

        assert is_valid is False
        assert "p256dh" in error

    def test_cle_auth_manquante(self):
        """Clé auth manquante."""
        subscription = {"endpoint": "https://push.example.com", "keys": {"p256dh": "key"}}

        is_valid, error = valider_abonnement(subscription)

        assert is_valid is False
        assert "auth" in error


@pytest.mark.unit
class TestValiderPreferences:
    """Tests pour valider_preferences."""

    def test_preferences_valides(self):
        """Préférences valides."""
        prefs = {
            "heures_silencieuses_debut": 22,
            "heures_silencieuses_fin": 7,
            "max_par_heure": 5,
        }

        is_valid, warnings = valider_preferences(prefs)

        assert is_valid is True
        assert len(warnings) == 0

    def test_heure_debut_invalide(self):
        """Heure début hors limites."""
        prefs = {"heures_silencieuses_debut": 25}

        is_valid, warnings = valider_preferences(prefs)

        assert is_valid is False
        assert any("debut" in w for w in warnings)

    def test_heure_fin_invalide(self):
        """Heure fin hors limites."""
        prefs = {"heures_silencieuses_fin": -1}

        is_valid, warnings = valider_preferences(prefs)

        assert is_valid is False
        assert any("fin" in w for w in warnings)

    def test_max_par_heure_trop_bas(self):
        """max_par_heure < 1."""
        prefs = {"max_par_heure": 0}

        is_valid, warnings = valider_preferences(prefs)

        assert is_valid is False
        assert any("max_par_heure" in w for w in warnings)

    def test_max_par_heure_eleve(self):
        """max_par_heure > 100 (warning)."""
        prefs = {"max_par_heure": 150}

        is_valid, warnings = valider_preferences(prefs)

        assert is_valid is False
        assert any("élevé" in w for w in warnings)


# ═══════════════════════════════════════════════════════════
# TESTS ALIAS RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAliasRetrocompatibilite:
    """Tests pour les alias de rétrocompatibilité."""

    def test_notification_type_alias(self):
        """NotificationType = TypeNotification."""
        assert NotificationType is TypeNotification

    def test_is_quiet_hours_alias(self):
        """is_quiet_hours = est_heures_silencieuses."""
        assert is_quiet_hours is est_heures_silencieuses

    def test_can_send_alias(self):
        """can_send_during_quiet_hours = peut_envoyer_pendant_silence."""
        assert can_send_during_quiet_hours is peut_envoyer_pendant_silence
