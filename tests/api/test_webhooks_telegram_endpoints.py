"""Tests d'intégration des endpoints Telegram et smoke tests de flux."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


class TestEndpointsTelegramEnvoi:
    """Tests des endpoints d'envoi Telegram."""

    def test_envoyer_planning_telegram_ok(self, client: TestClient):
        with patch("src.api.utils.executer_async", new_callable=AsyncMock) as mock_execute:
            with patch(
                "src.services.integrations.telegram.envoyer_planning_semaine",
                new_callable=AsyncMock,
            ) as mock_envoyer:
                mock_execute.return_value = {
                    "planning_id": 42,
                    "contenu": "Lundi: Pâtes\nMardi: Poisson",
                }
                mock_envoyer.return_value = True

                response = client.post(
                    "/api/v1/telegram/envoyer-planning",
                    json={"planning_id": 42},
                )

        assert response.status_code == 200
        assert response.json()["message"] == "planning_envoye"
        assert response.json()["id"] == 42
        mock_envoyer.assert_awaited_once_with(
            "Lundi: Pâtes\nMardi: Poisson",
            planning_id=42,
        )

    def test_envoyer_courses_telegram_ok(self, client: TestClient):
        with patch("src.api.utils.executer_async", new_callable=AsyncMock) as mock_execute:
            with patch(
                "src.services.integrations.telegram.envoyer_liste_courses_partagee",
                new_callable=AsyncMock,
            ) as mock_envoyer:
                mock_execute.return_value = {
                    "liste_id": 15,
                    "nom_liste": "Courses semaine",
                    "articles": ["Lait", "Pommes", "Pâtes"],
                }
                mock_envoyer.return_value = True

                response = client.post(
                    "/api/v1/telegram/envoyer-courses",
                    json={"liste_id": 15},
                )

        assert response.status_code == 200
        assert response.json()["message"] == "courses_envoyees"
        assert response.json()["id"] == 15
        mock_envoyer.assert_awaited_once_with(
            ["Lait", "Pommes", "Pâtes"],
            nom_liste="Courses semaine",
            liste_id=15,
        )

    def test_envoyer_planning_telegram_echec_envoi(self, client: TestClient):
        with patch("src.api.utils.executer_async", new_callable=AsyncMock) as mock_execute:
            with patch(
                "src.services.integrations.telegram.envoyer_planning_semaine",
                new_callable=AsyncMock,
            ) as mock_envoyer:
                mock_execute.return_value = {
                    "planning_id": 42,
                    "contenu": "Planning test",
                }
                mock_envoyer.return_value = False

                response = client.post(
                    "/api/v1/telegram/envoyer-planning",
                    json={"planning_id": 42},
                )

        assert response.status_code == 502


class TestSmokeFluxPlanningCoursesTelegram:
    """Smoke test du flux planning -> courses via Telegram."""

    def test_flux_complet_envoi_puis_callbacks(self, client: TestClient):
        callback_planning = {
            "update_id": 1001,
            "callback_query": {
                "id": "callback_123",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "planning_valider:42",
                "message": {"message_id": 100, "date": 1234567890, "chat": {"id": 123456}},
            },
        }
        callback_courses = {
            "update_id": 2001,
            "callback_query": {
                "id": "callback_201",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "courses_confirmer:15",
                "message": {"message_id": 101, "date": 1234567891, "chat": {"id": 123456}},
            },
        }

        execute_results = [
            {"planning_id": 42, "contenu": "Lundi: Pâtes"},
            {"message": "Planning validé", "id": 42, "status": 200},
            {"liste_id": 15, "nom_liste": "Courses semaine", "articles": ["Lait", "Pain"]},
            {"message": "Liste confirmée", "id": 15, "status": 200},
        ]

        with patch("src.api.utils.executer_async", new_callable=AsyncMock) as mock_execute:
            with patch(
                "src.services.integrations.telegram.envoyer_planning_semaine",
                new_callable=AsyncMock,
            ) as mock_planning:
                with patch(
                    "src.services.integrations.telegram.envoyer_liste_courses_partagee",
                    new_callable=AsyncMock,
                ) as mock_courses:
                    with patch(
                        "src.services.integrations.telegram.repondre_callback_query",
                        new_callable=AsyncMock,
                    ) as mock_callback:
                        with patch(
                            "src.services.integrations.telegram.modifier_message",
                            new_callable=AsyncMock,
                        ):
                            mock_execute.side_effect = execute_results
                            mock_planning.return_value = True
                            mock_courses.return_value = True

                            response_envoi_planning = client.post(
                                "/api/v1/telegram/envoyer-planning",
                                json={"planning_id": 42},
                            )
                            response_callback_planning = client.post(
                                "/api/v1/telegram/webhook",
                                json=callback_planning,
                            )
                            response_envoi_courses = client.post(
                                "/api/v1/telegram/envoyer-courses",
                                json={"liste_id": 15},
                            )
                            response_callback_courses = client.post(
                                "/api/v1/telegram/webhook",
                                json=callback_courses,
                            )

        assert response_envoi_planning.status_code == 200
        assert response_callback_planning.status_code == 200
        assert response_envoi_courses.status_code == 200
        assert response_callback_courses.status_code == 200
        assert mock_callback.await_count == 2


class TestTelegramCommandes:
    """Tests ciblés sur les commandes Telegram de base."""

    def test_commande_planning_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3001,
            "message": {
                "message_id": 201,
                "date": 1234567892,
                "chat": {"id": 123456},
                "text": "/planning",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_planning_commande",
            new_callable=AsyncMock,
        ) as mock_planning:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_planning.assert_awaited_once_with("123456")

    def test_reponse_rapide_ok_declenche_validation(self, client: TestClient):
        payload = {
            "update_id": 3002,
            "message": {
                "message_id": 202,
                "date": 1234567893,
                "chat": {"id": 123456},
                "text": "OK",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_reponse_rapide_ok",
            new_callable=AsyncMock,
        ) as mock_ok:
            mock_ok.return_value = True
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_ok.assert_awaited_once_with("123456")

    def test_commande_planning_avec_suffixe_bot_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3005,
            "message": {
                "message_id": 205,
                "date": 1234567896,
                "chat": {"id": 123456},
                "text": "/planning@assistant_matanne_bot",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_planning_commande",
            new_callable=AsyncMock,
        ) as mock_planning:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_planning.assert_awaited_once_with("123456")

    def test_callback_menu_route_vers_handler(self, client: TestClient):
        payload = {
            "update_id": 3003,
            "callback_query": {
                "id": "callback_menu_1",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "menu_cuisine",
                "message": {
                    "message_id": 203,
                    "date": 1234567894,
                    "chat": {"id": 123456},
                },
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_callback_menu",
            new_callable=AsyncMock,
        ) as mock_menu:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_menu.assert_awaited_once_with("menu_cuisine", "callback_menu_1", "123456")

    def test_callback_toggle_article_route_vers_handler(self, client: TestClient):
        payload = {
            "update_id": 3004,
            "callback_query": {
                "id": "callback_courses_1",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "courses_toggle_article:18",
                "message": {
                    "message_id": 204,
                    "date": 1234567895,
                    "chat": {"id": 123456},
                },
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_callback_toggle_article",
            new_callable=AsyncMock,
        ) as mock_toggle:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_toggle.assert_awaited_once_with(
            "courses_toggle_article:18",
            "callback_courses_1",
            "123456",
        )


class TestTelegramCommandesEnrichies:
    """Tests ciblés sur les commandes Telegram enrichies."""

    def test_commande_inventaire_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3101,
            "message": {
                "message_id": 211,
                "date": 1234567900,
                "chat": {"id": 123456},
                "text": "/inventaire",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_inventaire_commande",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_recette_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3102,
            "message": {
                "message_id": 212,
                "date": 1234567901,
                "chat": {"id": 123456},
                "text": "/recette gratin dauphinois",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_recette_commande",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456", "gratin dauphinois")

    def test_commande_rappels_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3103,
            "message": {
                "message_id": 213,
                "date": 1234567902,
                "chat": {"id": 123456},
                "text": "/rappels",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_rappels_groupes",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_batch_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 31031,
            "message": {
                "message_id": 2131,
                "date": 12345679021,
                "chat": {"id": 123456},
                "text": "/batch",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_resume_batch_cooking",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_jardin_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 31032,
            "message": {
                "message_id": 2132,
                "date": 12345679022,
                "chat": {"id": 123456},
                "text": "/jardin",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_resume_jardin",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_energie_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 31033,
            "message": {
                "message_id": 2133,
                "date": 12345679023,
                "chat": {"id": 123456},
                "text": "/energie",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_resume_energie",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_timer_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3104,
            "message": {
                "message_id": 214,
                "date": 1234567903,
                "chat": {"id": 123456},
                "text": "/timer 15",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._lancer_minuteur_telegram",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456", "15")

    def test_commande_note_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3105,
            "message": {
                "message_id": 215,
                "date": 1234567904,
                "chat": {"id": 123456},
                "text": "/note penser au drive",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._creer_note_rapide_telegram",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456", "penser au drive")

    def test_callback_article_statut_route_vers_handler(self, client: TestClient):
        payload = {
            "update_id": 3106,
            "callback_query": {
                "id": "callback_courses_2",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "courses_action:reporter:18",
                "message": {
                    "message_id": 216,
                    "date": 1234567905,
                    "chat": {"id": 123456},
                },
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_callback_action_article",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("courses_action:reporter:18", "callback_courses_2", "123456")

    def test_callback_sondage_repas_route_vers_handler(self, client: TestClient):
        payload = {
            "update_id": 3107,
            "callback_query": {
                "id": "callback_repas_1",
                "from": {"id": 123456, "is_bot": False},
                "chat_instance": "1234567890",
                "data": "repas_sondage:soir",
                "message": {
                    "message_id": 217,
                    "date": 1234567906,
                    "chat": {"id": 123456},
                },
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_callback_sondage_repas",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("repas_sondage:soir", "callback_repas_1", "123456")

    def test_commande_courses_live_declenche_le_handler_courses(self, client: TestClient):
        payload = {
            "update_id": 3108,
            "message": {
                "message_id": 218,
                "date": 1234567907,
                "chat": {"id": 123456},
                "text": "/courses_live",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_courses_commande",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_ajouter_course_declenche_le_handler_ajout(self, client: TestClient):
        payload = {
            "update_id": 3109,
            "message": {
                "message_id": 219,
                "date": 1234567908,
                "chat": {"id": 123456},
                "text": "/ajouter_course fraises",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._ajouter_article_liste",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456", "fraises")

    def test_commande_weekend_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3110,
            "message": {
                "message_id": 220,
                "date": 1234567909,
                "chat": {"id": 123456},
                "text": "/weekend",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_resume_weekend",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_rapport_declenche_le_handler(self, client: TestClient):
        payload = {
            "update_id": 3111,
            "message": {
                "message_id": 221,
                "date": 1234567910,
                "chat": {"id": 123456},
                "text": "/rapport",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_rapport_hebdo",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_commande_photo_declenche_le_handler_aide(self, client: TestClient):
        payload = {
            "update_id": 3112,
            "message": {
                "message_id": 222,
                "date": 1234567911,
                "chat": {"id": 123456},
                "text": "/photo",
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._envoyer_aide_photo_telegram",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456")

    def test_message_photo_route_vers_handler_ia(self, client: TestClient):
        payload = {
            "update_id": 3113,
            "message": {
                "message_id": 218,
                "date": 1234567907,
                "chat": {"id": 123456},
                "photo": [
                    {"file_id": "file_small", "width": 90, "height": 90},
                    {"file_id": "file_large", "width": 1280, "height": 720},
                ],
            },
        }

        with patch(
            "src.api.routes.webhooks_telegram._traiter_photo_frigo_telegram",
            new_callable=AsyncMock,
        ) as mock_handler:
            response = client.post("/api/v1/telegram/webhook", json=payload)

        assert response.status_code == 200
        mock_handler.assert_awaited_once_with("123456", payload["message"]["photo"])