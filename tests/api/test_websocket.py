"""
Tests d'intégration WebSocket pour la collaboration temps réel sur les courses.

Teste le module src/api/websocket_courses.py:
- Connexion / déconnexion
- Broadcast user_joined / user_left
- Actions valides (item_added, item_removed, item_checked, etc.)
- Ping / Pong
- Actions inconnues → erreur
- Isolation entre listes
- Liste des utilisateurs connectés
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _reset_ws_manager():
    """Réinitialise le ConnectionManager global entre chaque test."""
    import src.api.websocket_courses as ws_mod
    from src.api.websocket_courses import ConnectionManager, _manager

    ws_mod._manager = ConnectionManager()
    yield
    ws_mod._manager = ConnectionManager()


@pytest.fixture
def ws_client(app) -> TestClient:
    """TestClient dédié aux tests WebSocket."""
    return TestClient(app)


def _ws_url(liste_id: int, user_id: str, username: str = "Anonyme") -> str:
    """Construit l'URL WebSocket pour une liste de courses."""
    return f"/api/v1/ws/courses/{liste_id}?user_id={user_id}&username={username}"


# ═══════════════════════════════════════════════════════════
# CONNEXION / DÉCONNEXION
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketConnexion:
    """Tests de connexion et déconnexion basiques."""

    def test_connexion_recoit_users_list(self, ws_client: TestClient):
        """Un client qui se connecte reçoit la liste des utilisateurs."""
        with ws_client.websocket_connect(_ws_url(1, "user-1", "Anne")) as ws:
            data = ws.receive_json()
            assert data["type"] == "users_list"
            assert isinstance(data["users"], list)
            assert len(data["users"]) >= 1
            # L'utilisateur lui-même doit être dans la liste
            user_ids = [u["user_id"] for u in data["users"]]
            assert "user-1" in user_ids

    def test_connexion_multiple_clients(self, ws_client: TestClient):
        """Deux clients peuvent se connecter à la même liste."""
        with ws_client.websocket_connect(_ws_url(2, "user-a", "Anne")) as ws1:
            # ws1 reçoit users_list initial
            data1 = ws1.receive_json()
            assert data1["type"] == "users_list"

            with ws_client.websocket_connect(_ws_url(2, "user-b", "Marc")) as ws2:
                # ws1 reçoit user_joined pour user-b
                joined = ws1.receive_json()
                assert joined["type"] == "user_joined"
                assert joined["user_id"] == "user-b"
                assert joined["username"] == "Marc"

                # ws2 reçoit users_list avec les 2 users
                data2 = ws2.receive_json()
                assert data2["type"] == "users_list"
                assert len(data2["users"]) == 2

    def test_reconnexion_meme_utilisateur(self, ws_client: TestClient):
        """Un utilisateur peut se reconnecter avec le même user_id après déconnexion."""
        with ws_client.websocket_connect(_ws_url(22, "reco", "Reco")) as ws1:
            data1 = ws1.receive_json()
            assert data1["type"] == "users_list"
            assert len(data1["users"]) == 1

        # Nouvelle connexion avec le même user_id sur la même liste
        with ws_client.websocket_connect(_ws_url(22, "reco", "Reco")) as ws2:
            data2 = ws2.receive_json()
            assert data2["type"] == "users_list"
            # Le manager a bien nettoyé l'ancienne connexion
            assert len(data2["users"]) == 1
            assert data2["users"][0]["user_id"] == "reco"

            ws2.send_json({"action": "ping"})
            pong = ws2.receive_json()
            assert pong["type"] == "pong"


# ═══════════════════════════════════════════════════════════
# USER JOINED / USER LEFT
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketPresence:
    """Tests de gestion de présence."""

    def test_user_joined_broadcast(self, ws_client: TestClient):
        """Quand un 2e utilisateur rejoint, le 1er reçoit user_joined."""
        with ws_client.websocket_connect(_ws_url(3, "first", "Premier")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(3, "second", "Deuxième")) as ws2:
                ws2.receive_json()  # users_list

                joined = ws1.receive_json()
                assert joined["type"] == "user_joined"
                assert joined["user_id"] == "second"
                assert joined["username"] == "Deuxième"
                assert "timestamp" in joined

    @pytest.mark.skip(reason="Disconnect broadcast deadlocks in sync TestClient — tested manually")
    def test_user_left_broadcast(self, ws_client: TestClient):
        """Quand un utilisateur se déconnecte, les autres reçoivent user_left."""
        with ws_client.websocket_connect(_ws_url(4, "stayer", "Restant")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(4, "leaver", "Partant")) as ws2:
                ws2.receive_json()  # users_list
                ws1.receive_json()  # user_joined pour leaver

            # ws2 est fermé (sorti du with) → ws1 devrait recevoir user_left
            left = ws1.receive_json()
            assert left["type"] == "user_left"
            assert left["user_id"] == "leaver"
            assert left["username"] == "Partant"


# ═══════════════════════════════════════════════════════════
# ACTIONS VALIDES
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketActions:
    """Tests des actions de modification de liste."""

    def test_item_added_broadcast(self, ws_client: TestClient):
        """L'ajout d'un article est broadcasté aux autres clients."""
        with ws_client.websocket_connect(_ws_url(10, "sender", "Envoyeur")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(10, "receiver", "Receveur")) as ws2:
                ws2.receive_json()  # users_list
                ws1.receive_json()  # user_joined

                # sender envoie item_added
                ws1.send_json(
                    {
                        "action": "item_added",
                        "item": {"nom": "Tomates", "quantite": 3},
                    }
                )

                # receiver reçoit le sync
                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "item_added"
                assert sync["user_id"] == "sender"
                assert sync["username"] == "Envoyeur"
                assert sync["item"]["nom"] == "Tomates"
                assert "timestamp" in sync

    def test_item_removed_broadcast(self, ws_client: TestClient):
        """La suppression d'un article est broadcastée."""
        with ws_client.websocket_connect(_ws_url(11, "s", "S")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(11, "r", "R")) as ws2:
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({"action": "item_removed", "item_id": 42})

                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "item_removed"
                assert sync["item_id"] == 42

    def test_item_checked_broadcast(self, ws_client: TestClient):
        """Le cochage d'un article est broadcasté."""
        with ws_client.websocket_connect(_ws_url(12, "s", "S")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(12, "r", "R")) as ws2:
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({"action": "item_checked", "item_id": 7, "checked": True})

                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "item_checked"
                assert sync["item_id"] == 7
                assert sync["checked"] is True

    def test_item_updated_broadcast(self, ws_client: TestClient):
        """La mise à jour d'un article est broadcastée."""
        with ws_client.websocket_connect(_ws_url(13, "s", "S")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(13, "r", "R")) as ws2:
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json(
                    {
                        "action": "item_updated",
                        "item_id": 5,
                        "updates": {"quantite": 10},
                    }
                )

                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "item_updated"
                assert sync["item_id"] == 5

    def test_list_renamed_broadcast(self, ws_client: TestClient):
        """Le renommage de liste est broadcasté."""
        with ws_client.websocket_connect(_ws_url(14, "s", "S")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(14, "r", "R")) as ws2:
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({"action": "list_renamed", "new_name": "Ma liste"})

                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "list_renamed"
                assert sync["new_name"] == "Ma liste"

    def test_user_typing_broadcast(self, ws_client: TestClient):
        """L'indicateur de saisie est broadcasté."""
        with ws_client.websocket_connect(_ws_url(15, "s", "S")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(15, "r", "R")) as ws2:
                ws2.receive_json()
                ws1.receive_json()

                ws1.send_json({"action": "user_typing", "typing": True})

                sync = ws2.receive_json()
                assert sync["type"] == "sync"
                assert sync["action"] == "user_typing"

    def test_sender_does_not_receive_own_broadcast(self, ws_client: TestClient):
        """L'expéditeur ne reçoit pas son propre message broadcasté."""
        with ws_client.websocket_connect(_ws_url(16, "sender", "S")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(16, "other", "O")) as ws2:
                ws2.receive_json()  # users_list
                ws1.receive_json()  # user_joined

                ws1.send_json({"action": "item_added", "item": {"nom": "Lait"}})

                # ws2 reçoit le sync
                sync = ws2.receive_json()
                assert sync["type"] == "sync"

                # ws1 ne devrait PAS recevoir de sync
                # On envoie un ping pour vérifier que le prochain message est un pong
                ws1.send_json({"action": "ping"})
                pong = ws1.receive_json()
                assert pong["type"] == "pong"


# ═══════════════════════════════════════════════════════════
# PING / PONG
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketPingPong:
    """Tests du mécanisme de heartbeat."""

    def test_ping_retourne_pong(self, ws_client: TestClient):
        """Un ping retourne un pong personnel."""
        with ws_client.websocket_connect(_ws_url(20, "pinger", "P")) as ws:
            ws.receive_json()  # users_list

            ws.send_json({"action": "ping"})
            data = ws.receive_json()
            assert data["type"] == "pong"

    def test_ping_non_broadcast(self, ws_client: TestClient):
        """Un ping n'est pas broadcasté aux autres clients."""
        with ws_client.websocket_connect(_ws_url(21, "pinger", "P")) as ws1:
            ws1.receive_json()

            with ws_client.websocket_connect(_ws_url(21, "other", "O")) as ws2:
                ws2.receive_json()
                ws1.receive_json()  # user_joined

                ws1.send_json({"action": "ping"})
                pong = ws1.receive_json()
                assert pong["type"] == "pong"

                # ws2 ne reçoit rien — on vérifie via ping
                ws2.send_json({"action": "ping"})
                data = ws2.receive_json()
                assert data["type"] == "pong"


# ═══════════════════════════════════════════════════════════
# ACTIONS INCONNUES → ERREUR
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketErrors:
    """Tests de gestion des erreurs."""

    def test_action_inconnue_retourne_erreur(self, ws_client: TestClient):
        """Une action invalide retourne un message d'erreur."""
        with ws_client.websocket_connect(_ws_url(30, "user", "U")) as ws:
            ws.receive_json()  # users_list

            ws.send_json({"action": "action_inexistante"})
            data = ws.receive_json()
            assert data["type"] == "error"
            assert "action_inexistante" in data["message"]

    def test_action_vide_retourne_erreur(self, ws_client: TestClient):
        """Un message sans action retourne une erreur."""
        with ws_client.websocket_connect(_ws_url(31, "user", "U")) as ws:
            ws.receive_json()  # users_list

            ws.send_json({"data": "no action field"})
            data = ws.receive_json()
            assert data["type"] == "error"


# ═══════════════════════════════════════════════════════════
# ISOLATION ENTRE LISTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketIsolation:
    """Tests d'isolation entre listes différentes."""

    def test_messages_ne_traversent_pas_les_listes(self, ws_client: TestClient):
        """Les messages d'une liste ne sont pas reçus sur une autre liste."""
        with ws_client.websocket_connect(_ws_url(40, "user-a", "A")) as ws_liste40:
            ws_liste40.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(41, "user-b", "B")) as ws_liste41:
                ws_liste41.receive_json()  # users_list

                # Envoyer un message sur liste 40
                ws_liste40.send_json(
                    {
                        "action": "item_added",
                        "item": {"nom": "Beurre"},
                    }
                )

                # ws_liste41 ne reçoit rien — vérifier via ping
                ws_liste41.send_json({"action": "ping"})
                data = ws_liste41.receive_json()
                assert data["type"] == "pong"

    def test_user_joined_isole_par_liste(self, ws_client: TestClient):
        """Le user_joined n'est émis que sur la bonne liste."""
        with ws_client.websocket_connect(_ws_url(42, "observer", "Obs")) as ws_list42:
            ws_list42.receive_json()  # users_list

            # Un user rejoint une AUTRE liste (43)
            with ws_client.websocket_connect(_ws_url(43, "newcomer", "New")) as ws_list43:
                ws_list43.receive_json()  # users_list

                # ws_list42 ne reçoit PAS de user_joined
                ws_list42.send_json({"action": "ping"})
                data = ws_list42.receive_json()
                assert data["type"] == "pong"


# ═══════════════════════════════════════════════════════════
# USERS LIST
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketUsersList:
    """Tests de la liste d'utilisateurs connectés."""

    def test_users_list_contient_tous_les_connectes(self, ws_client: TestClient):
        """La users_list envoyée au dernier connecté contient tous les utilisateurs."""
        with ws_client.websocket_connect(_ws_url(50, "u1", "User1")) as ws1:
            ws1.receive_json()  # users_list pour u1

            with ws_client.websocket_connect(_ws_url(50, "u2", "User2")) as ws2:
                ws1.receive_json()  # user_joined u2

                with ws_client.websocket_connect(_ws_url(50, "u3", "User3")) as ws3:
                    ws1.receive_json()  # user_joined u3
                    ws2.receive_json()  # user_joined u3

                    # ws3 reçoit users_list avec 3 users
                    data = ws3.receive_json()
                    assert data["type"] == "users_list"
                    user_ids = {u["user_id"] for u in data["users"]}
                    assert user_ids == {"u1", "u2", "u3"}


# ═══════════════════════════════════════════════════════════
# EDGE CASES (Phase A - A5.5)
# ═══════════════════════════════════════════════════════════


@pytest.mark.websocket
class TestWebSocketEdgeCases:
    """Tests edge cases WebSocket : messages malformés, reconnexion, validation."""

    def test_message_objet_vide(self, ws_client: TestClient):
        """Un objet JSON vide (sans action) retourne une erreur."""
        with ws_client.websocket_connect(_ws_url(60, "user_bad", "Bad")) as ws:
            ws.receive_json()  # users_list
            ws.send_json({})
            data = ws.receive_json()
            assert data.get("type") == "error"

    def test_message_sans_action(self, ws_client: TestClient):
        """Un message sans champ 'action' retourne une erreur."""
        with ws_client.websocket_connect(_ws_url(61, "user_no_action", "NoAction")) as ws:
            ws.receive_json()  # users_list
            ws.send_json({"data": "sans action"})
            data = ws.receive_json()
            assert data.get("type") == "error"

    def test_action_item_added_sans_item(self, ws_client: TestClient):
        """Action item_added sans données d'item ne crash pas le serveur."""
        with ws_client.websocket_connect(_ws_url(62, "user_incomplete", "Inc")) as ws:
            ws.receive_json()  # users_list
            ws.send_json({"action": "item_added"})
            # Le serveur broadcast aux autres (personne ici), pas d'accusé pour l'expéditeur.
            # Vérifier que la connexion est toujours active via ping.
            ws.send_json({"action": "ping"})
            data = ws.receive_json()
            assert data.get("type") == "pong"

    def test_reconnexion_meme_user_remplace(self, ws_client: TestClient):
        """Reconnexion du même user_id remplace la connexion précédente."""
        with ws_client.websocket_connect(_ws_url(63, "reconn", "Reconn1")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(63, "reconn", "Reconn2")) as ws2:
                data = ws2.receive_json()
                assert data["type"] == "users_list"
                # Le user_id doit apparaître une seule fois
                user_ids = [u["user_id"] for u in data["users"]]
                assert user_ids.count("reconn") == 1

    def test_ping_pong_maintient_connexion(self, ws_client: TestClient):
        """Plusieurs ping/pong successifs maintiennent la connexion."""
        with ws_client.websocket_connect(_ws_url(64, "pinger", "Pinger")) as ws:
            ws.receive_json()  # users_list
            for _ in range(5):
                ws.send_json({"action": "ping"})
                data = ws.receive_json()
                assert data["type"] == "pong"

    def test_broadcast_multiple_actions_rapides(self, ws_client: TestClient):
        """Plusieurs actions rapides sont toutes broadcastées correctement."""
        with ws_client.websocket_connect(_ws_url(65, "fast1", "Fast1")) as ws1:
            ws1.receive_json()  # users_list

            with ws_client.websocket_connect(_ws_url(65, "fast2", "Fast2")) as ws2:
                ws1.receive_json()  # user_joined
                ws2.receive_json()  # users_list

                # Envoyer 3 actions rapides
                for i in range(3):
                    ws1.send_json({
                        "action": "item_added",
                        "item": {"nom": f"Article {i}", "quantite": 1},
                    })

                # ws2 doit recevoir les 3
                received = []
                for _ in range(3):
                    data = ws2.receive_json()
                    received.append(data)

                assert len(received) == 3
                assert all(d.get("type") == "sync" for d in received)
                assert all(d.get("action") == "item_added" for d in received)
