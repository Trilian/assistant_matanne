"""Tests ciblés pour le dispatcher notifications."""

from src.services.core.notifications.notif_dispatcher import DispatcherNotifications


class DispatcherTestable(DispatcherNotifications):
    """Double de test évitant les appels externes."""

    def __init__(self):
        super().__init__()
        self.push_result = False
        self.ntfy_result = False
        self.telegram_result = False
        self.email_result = False
        self.calls: list[str] = []
        self._prefs: dict[str, dict] = {}

    def _envoyer_push(self, user_id: str, message: str, **kwargs):
        self.calls.append("push")
        return self.push_result

    def _envoyer_ntfy(self, message: str, **kwargs):
        self.calls.append("ntfy")
        return self.ntfy_result

    def _envoyer_telegram(self, message: str, **kwargs):
        self.calls.append("telegram")
        return self.telegram_result

    def _envoyer_email(self, user_id: str, message: str, **kwargs):
        self.calls.append("email")
        return self.email_result

    def _recuperer_preferences_notifications(self, user_id: str):
        return self._prefs.get(user_id, {})


def test_failover_push_vers_telegram():
    """Si push échoue, le failover envoie sur Telegram puis stoppe au succès."""
    dispatcher = DispatcherTestable()
    dispatcher.push_result = False
    dispatcher.telegram_result = True
    dispatcher.email_result = True  # ne doit pas être tenté car Telegram réussit

    resultats = dispatcher.envoyer(
        user_id="matanne",
        message="Alerte test",
        canaux=["push"],
        strategie="failover",
    )

    assert resultats.get("push") is False
    assert resultats.get("telegram") is True
    assert "email" not in dispatcher.calls


def test_resolution_canaux_depuis_mapping_et_preferences():
    """Le routing combine mapping événement + préférences canaux par catégorie."""
    dispatcher = DispatcherTestable()
    dispatcher._prefs["u1"] = {
        "canaux_par_categorie": {
            "alertes": ["telegram", "email"],
        },
        "canal_prefere": "push",
    }

    canaux = dispatcher._resoudre_canaux(
        user_id="u1",
        canaux=None,
        type_evenement="tache_entretien_urgente",
        categorie=None,
    )

    assert canaux == ["telegram", "email"]


def test_throttling_bascule_en_digest():
    """Au-delà de la limite horaire, la notification est mise en digest."""
    dispatcher = DispatcherTestable()
    dispatcher.ntfy_result = True
    dispatcher._prefs["u2"] = {
        "modules_actifs": {"max_par_heure": 1, "mode_digest": False},
        "canal_prefere": "ntfy",
    }

    # Premier envoi autorisé
    first = dispatcher.envoyer(user_id="u2", message="Premier", canaux=["ntfy"])
    assert first.get("ntfy") is True

    # Deuxième envoi dans la même heure => digest
    second = dispatcher.envoyer(user_id="u2", message="Second", canaux=["ntfy"])
    assert second == {"digest": True}
    assert len(dispatcher._digest_queue["u2"]) == 1


def test_mode_digest_force_file_attente_sur_non_alertes():
    """Quand mode_digest est actif, les rappels passent en digest directement."""
    dispatcher = DispatcherTestable()
    dispatcher.ntfy_result = True
    dispatcher._prefs["u3"] = {
        "modules_actifs": {"max_par_heure": 5, "mode_digest": True},
        "canaux_par_categorie": {"rappels": ["ntfy"]},
        "canal_prefere": "ntfy",
    }

    resultats = dispatcher.envoyer_evenement(
        user_id="u3",
        type_evenement="rappel_courses",
        message="Pense aux courses",
    )

    assert resultats == {"digest": True}
    assert len(dispatcher._digest_queue["u3"]) == 1


def test_envoyer_evenement_failover_jusqu_telegram():
    """En mode failover, l'envoi s'arrete au premier canal qui reussit."""
    dispatcher = DispatcherTestable()
    dispatcher.push_result = False
    dispatcher.ntfy_result = False
    dispatcher.telegram_result = True
    dispatcher.email_result = True  # Ne doit pas etre tente apres succes Telegram

    resultats = dispatcher.envoyer_evenement(
        user_id="u4",
        type_evenement="echec_cron_job",
        message="Le cron digest a echoue",
    )

    assert resultats.get("push") is False
    assert resultats.get("ntfy") is False
    assert resultats.get("telegram") is True
    assert "email" not in dispatcher.calls


def test_vider_digest_envoie_resume_et_nettoie_file():
    """La vidange digest envoie un resume puis purge la file si succes."""
    dispatcher = DispatcherTestable()
    dispatcher.email_result = False
    dispatcher.telegram_result = True

    dispatcher._digest_queue["u5"] = [
        {"message": "Alerte 1"},
        {"message": "Alerte 2"},
    ]

    resultats = dispatcher.vider_digest("u5")

    assert resultats.get("telegram") is True
    assert dispatcher._digest_queue["u5"] == []
