"""
Tests pour src/core/offline.py
Couvre :
- OperationEnAttente (to_dict, from_dict)
- StatutConnexion, TypeOperation enums
- GestionnaireConnexion (statut, connexion, vérification)
- FileAttenteHorsLigne (queue operations)
- SynchroniseurHorsLigne (sync operations)
- avec_mode_hors_ligne décorateur
- Composants UI (afficher_statut_connexion, afficher_panneau_sync)
"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.core.offline import (
    FileAttenteHorsLigne,
    GestionnaireConnexion,
    OperationEnAttente,
    StatutConnexion,
    SynchroniseurHorsLigne,
    TypeOperation,
    afficher_panneau_sync,
    afficher_statut_connexion,
    avec_mode_hors_ligne,
)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Tests Enum et DataClass de base
# ═══════════════════════════════════════════════════════════════════════════════


class TestEnums:
    """Tests pour les enums StatutConnexion et TypeOperation."""

    def test_statut_connexion_online(self):
        """Vérifie StatutConnexion.ONLINE."""
        assert StatutConnexion.ONLINE == "online"
        assert StatutConnexion.ONLINE.value == "online"

    def test_statut_connexion_offline(self):
        """Vérifie StatutConnexion.OFFLINE."""
        assert StatutConnexion.OFFLINE == "offline"

    def test_statut_connexion_connecting(self):
        """Vérifie StatutConnexion.CONNECTING."""
        assert StatutConnexion.CONNECTING == "connecting"

    def test_statut_connexion_error(self):
        """Vérifie StatutConnexion.ERROR."""
        assert StatutConnexion.ERROR == "error"

    def test_type_operation_create(self):
        """Vérifie TypeOperation.CREATE."""
        assert TypeOperation.CREATE == "create"

    def test_type_operation_update(self):
        """Vérifie TypeOperation.UPDATE."""
        assert TypeOperation.UPDATE == "update"

    def test_type_operation_delete(self):
        """Vérifie TypeOperation.DELETE."""
        assert TypeOperation.DELETE == "delete"


class TestOperationEnAttente:
    """Tests pour la dataclass OperationEnAttente."""

    def test_creation_defaults(self):
        """Vérifie la création avec valeurs par défaut."""
        op = OperationEnAttente()
        assert op.id is not None
        assert len(op.id) == 12
        assert op.operation_type == TypeOperation.CREATE
        assert op.model_name == ""
        assert op.data == {}
        assert isinstance(op.created_at, datetime)
        assert op.retry_count == 0
        assert op.last_error is None

    def test_creation_avec_valeurs(self):
        """Vérifie la création avec valeurs personnalisées."""
        op = OperationEnAttente(
            model_name="Recette",
            data={"nom": "Tarte"},
            operation_type=TypeOperation.UPDATE,
            retry_count=2,
            last_error="Erreur test",
        )
        assert op.model_name == "Recette"
        assert op.data == {"nom": "Tarte"}
        assert op.operation_type == TypeOperation.UPDATE
        assert op.retry_count == 2
        assert op.last_error == "Erreur test"

    def test_to_dict(self):
        """Vérifie la sérialisation en dict."""
        op = OperationEnAttente(
            model_name="Test",
            data={"a": 1},
            operation_type=TypeOperation.UPDATE,
        )
        d = op.to_dict()
        assert d["model_name"] == "Test"
        assert d["operation_type"] == "update"  # Enum value
        assert isinstance(d["created_at"], str)
        assert d["data"] == {"a": 1}
        assert "id" in d

    def test_to_dict_avec_erreur(self):
        """Vérifie to_dict avec last_error."""
        op = OperationEnAttente(
            model_name="Test",
            last_error="Connection timeout",
            retry_count=3,
        )
        d = op.to_dict()
        assert d["last_error"] == "Connection timeout"
        assert d["retry_count"] == 3

    def test_from_dict(self):
        """Vérifie la désérialisation depuis dict."""
        data = {
            "id": "abc123",
            "operation_type": "delete",
            "model_name": "Inventaire",
            "data": {"item_id": 42},
            "created_at": "2024-01-15T10:30:00",
            "retry_count": 1,
            "last_error": "Previous error",
        }
        op = OperationEnAttente.from_dict(data)
        assert op.id == "abc123"
        assert op.operation_type == TypeOperation.DELETE
        assert op.model_name == "Inventaire"
        assert op.data == {"item_id": 42}
        assert op.retry_count == 1
        assert op.last_error == "Previous error"

    def test_from_dict_minimal(self):
        """Vérifie from_dict avec données minimales."""
        data = {}
        op = OperationEnAttente.from_dict(data)
        assert op.id is not None
        assert op.operation_type == TypeOperation.CREATE
        assert op.model_name == ""
        assert op.data == {}

    def test_from_dict_sans_created_at(self):
        """Vérifie from_dict sans created_at utilise datetime.now()."""
        data = {"model_name": "Test"}
        op = OperationEnAttente.from_dict(data)
        assert isinstance(op.created_at, datetime)

    def test_roundtrip_to_from_dict(self):
        """Vérifie le roundtrip to_dict -> from_dict."""
        original = OperationEnAttente(
            model_name="Courses",
            data={"items": [1, 2, 3]},
            operation_type=TypeOperation.CREATE,
            retry_count=0,
        )
        d = original.to_dict()
        restored = OperationEnAttente.from_dict(d)

        assert restored.id == original.id
        assert restored.model_name == original.model_name
        assert restored.data == original.data
        assert restored.operation_type == original.operation_type


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Tests GestionnaireConnexion
# ═══════════════════════════════════════════════════════════════════════════════


class TestGestionnaireConnexion:
    """Tests pour GestionnaireConnexion."""

    def setup_method(self):
        """Reset session_state avant chaque test."""
        self.mock_session = {}

    @patch("src.core.offline.st")
    def test_obtenir_statut_defaut(self, mock_st):
        """Vérifie le statut par défaut est ONLINE."""
        mock_st.session_state = {}
        status = GestionnaireConnexion.obtenir_statut()
        assert status == StatutConnexion.ONLINE

    @patch("src.core.offline.st")
    def test_obtenir_statut_depuis_session(self, mock_st):
        """Vérifie que le statut est lu depuis session_state."""
        mock_st.session_state = {GestionnaireConnexion.SESSION_KEY: StatutConnexion.OFFLINE}
        status = GestionnaireConnexion.obtenir_statut()
        assert status == StatutConnexion.OFFLINE

    @patch("src.core.offline.st")
    def test_set_status(self, mock_st):
        """Vérifie set_status met à jour session_state."""
        mock_st.session_state = {}
        GestionnaireConnexion.set_status(StatutConnexion.ERROR)
        assert mock_st.session_state[GestionnaireConnexion.SESSION_KEY] == StatutConnexion.ERROR

    @patch("src.core.offline.st")
    def test_est_en_ligne_true(self, mock_st):
        """Vérifie est_en_ligne retourne True quand ONLINE."""
        mock_st.session_state = {GestionnaireConnexion.SESSION_KEY: StatutConnexion.ONLINE}
        assert GestionnaireConnexion.est_en_ligne() is True

    @patch("src.core.offline.st")
    def test_est_en_ligne_false(self, mock_st):
        """Vérifie est_en_ligne retourne False quand OFFLINE."""
        mock_st.session_state = {GestionnaireConnexion.SESSION_KEY: StatutConnexion.OFFLINE}
        assert GestionnaireConnexion.est_en_ligne() is False

    @patch("src.core.offline.st")
    @patch("src.core.offline.verifier_connexion", create=True)
    def test_verifier_connexion_succes(self, mock_verifier, mock_st):
        """Vérifie verifier_connexion avec succès."""
        mock_st.session_state = {}

        with patch("src.core.offline.GestionnaireConnexion.est_en_ligne", return_value=True):
            with patch.dict(
                "sys.modules", {"src.core.database": MagicMock(verifier_connexion=lambda: True)}
            ):
                # Force check avec force=True pour bypass le cache
                result = GestionnaireConnexion.verifier_connexion(force=True)
                assert mock_st.session_state[GestionnaireConnexion.SESSION_KEY] in [
                    StatutConnexion.ONLINE,
                    StatutConnexion.CONNECTING,
                ]

    @patch("src.core.offline.st")
    def test_verifier_connexion_skip_recent(self, mock_st):
        """Vérifie que la vérification récente est skippée."""
        import time

        mock_st.session_state = {
            GestionnaireConnexion.SESSION_KEY: StatutConnexion.ONLINE,
            GestionnaireConnexion.LAST_CHECK_KEY: time.time(),
        }
        # Sans force, devrait retourner le statut en cache
        result = GestionnaireConnexion.verifier_connexion(force=False)
        assert result is True

    @patch("src.core.offline.st")
    def test_gerer_erreur_connexion(self, mock_st):
        """Vérifie gerer_erreur_connexion met le statut à OFFLINE."""
        mock_st.session_state = {}
        GestionnaireConnexion.gerer_erreur_connexion(Exception("Connection lost"))
        assert mock_st.session_state[GestionnaireConnexion.SESSION_KEY] == StatutConnexion.OFFLINE


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Tests FileAttenteHorsLigne
# ═══════════════════════════════════════════════════════════════════════════════


class TestFileAttenteHorsLigne:
    """Tests pour FileAttenteHorsLigne (queue offline)."""

    @patch("src.core.offline.st")
    def test_get_queue_empty(self, mock_st):
        """Vérifie _get_queue retourne liste vide par défaut."""
        mock_st.session_state = {}
        with patch.object(FileAttenteHorsLigne, "_load_from_file", return_value=[]):
            queue = FileAttenteHorsLigne._get_queue()
            assert queue == []

    @patch("src.core.offline.st")
    def test_get_queue_from_session(self, mock_st):
        """Vérifie _get_queue lit depuis session_state."""
        mock_st.session_state = {
            FileAttenteHorsLigne.SESSION_KEY: [{"id": "123", "model_name": "Test"}]
        }
        queue = FileAttenteHorsLigne._get_queue()
        assert len(queue) == 1
        assert queue[0]["id"] == "123"

    @patch("src.core.offline.st")
    def test_set_queue(self, mock_st):
        """Vérifie _set_queue met à jour session et fichier."""
        mock_st.session_state = {}
        with patch.object(FileAttenteHorsLigne, "_save_to_file") as mock_save:
            FileAttenteHorsLigne._set_queue([{"id": "abc"}])
            assert mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY] == [{"id": "abc"}]
            mock_save.assert_called_once()

    @patch("src.core.offline.st")
    def test_add_operation(self, mock_st):
        """Vérifie add() ajoute une opération à la queue."""
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: []}
        with patch.object(FileAttenteHorsLigne, "_save_to_file"):
            op = FileAttenteHorsLigne.add(
                TypeOperation.CREATE,
                "Recette",
                {"nom": "Tarte aux pommes"},
            )
            assert op.model_name == "Recette"
            assert op.operation_type == TypeOperation.CREATE
            assert op.data == {"nom": "Tarte aux pommes"}
            assert len(mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY]) == 1

    @patch("src.core.offline.st")
    def test_obtenir_en_attente(self, mock_st):
        """Vérifie obtenir_en_attente retourne des OperationEnAttente."""
        mock_st.session_state = {
            FileAttenteHorsLigne.SESSION_KEY: [
                {"id": "op1", "operation_type": "create", "model_name": "Test", "data": {}},
                {"id": "op2", "operation_type": "update", "model_name": "Test2", "data": {}},
            ]
        }
        ops = FileAttenteHorsLigne.obtenir_en_attente()
        assert len(ops) == 2
        assert isinstance(ops[0], OperationEnAttente)
        assert ops[0].id == "op1"
        assert ops[1].id == "op2"

    @patch("src.core.offline.st")
    def test_obtenir_nombre(self, mock_st):
        """Vérifie obtenir_nombre retourne le bon compte."""
        mock_st.session_state = {
            FileAttenteHorsLigne.SESSION_KEY: [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        }
        assert FileAttenteHorsLigne.obtenir_nombre() == 3

    @patch("src.core.offline.st")
    def test_remove_operation(self, mock_st):
        """Vérifie remove() supprime une opération."""
        mock_st.session_state = {
            FileAttenteHorsLigne.SESSION_KEY: [
                {"id": "op1", "model_name": "Test1"},
                {"id": "op2", "model_name": "Test2"},
            ]
        }
        with patch.object(FileAttenteHorsLigne, "_save_to_file"):
            result = FileAttenteHorsLigne.remove("op1")
            assert result is True
            assert len(mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY]) == 1
            assert mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY][0]["id"] == "op2"

    @patch("src.core.offline.st")
    def test_remove_inexistant(self, mock_st):
        """Vérifie remove() retourne False si ID inexistant."""
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "op1"}]}
        with patch.object(FileAttenteHorsLigne, "_save_to_file"):
            result = FileAttenteHorsLigne.remove("op_inexistant")
            assert result is False

    @patch("src.core.offline.st")
    def test_mettre_a_jour_tentative(self, mock_st):
        """Vérifie mettre_a_jour_tentative incrémente retry_count."""
        mock_st.session_state = {
            FileAttenteHorsLigne.SESSION_KEY: [{"id": "op1", "retry_count": 0, "last_error": None}]
        }
        with patch.object(FileAttenteHorsLigne, "_save_to_file"):
            FileAttenteHorsLigne.mettre_a_jour_tentative("op1", "Timeout error")
            op = mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY][0]
            assert op["retry_count"] == 1
            assert op["last_error"] == "Timeout error"

    @patch("src.core.offline.st")
    def test_clear(self, mock_st):
        """Vérifie clear() vide la queue et retourne le count."""
        mock_st.session_state = {FileAttenteHorsLigne.SESSION_KEY: [{"id": "1"}, {"id": "2"}]}
        with patch.object(FileAttenteHorsLigne, "_save_to_file"):
            count = FileAttenteHorsLigne.clear()
            assert count == 2
            assert mock_st.session_state[FileAttenteHorsLigne.SESSION_KEY] == []

    def test_ensure_cache_dir(self):
        """Vérifie _ensure_cache_dir crée le dossier."""
        with patch.object(Path, "mkdir") as mock_mkdir:
            FileAttenteHorsLigne._ensure_cache_dir()
            # Le dossier parent doit être créé
            mock_mkdir.assert_called()

    def test_load_from_file_not_exists(self):
        """Vérifie _load_from_file retourne [] si fichier inexistant."""
        with patch.object(Path, "exists", return_value=False):
            result = FileAttenteHorsLigne._load_from_file()
            assert result == []

    def test_load_from_file_exists(self):
        """Vérifie _load_from_file charge depuis fichier."""
        test_data = [{"id": "test1", "model_name": "Test"}]
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(test_data))):
                result = FileAttenteHorsLigne._load_from_file()
                assert result == test_data

    def test_load_from_file_error(self):
        """Vérifie _load_from_file retourne [] en cas d'erreur."""
        with patch.object(Path, "exists", return_value=True):
            with patch("builtins.open", side_effect=OSError("Read error")):
                result = FileAttenteHorsLigne._load_from_file()
                assert result == []

    def test_save_to_file(self):
        """Vérifie _save_to_file écrit dans le fichier."""
        test_data = [{"id": "test1"}]
        with patch.object(FileAttenteHorsLigne, "_ensure_cache_dir"):
            m = mock_open()
            with patch("builtins.open", m):
                FileAttenteHorsLigne._save_to_file(test_data)
                m.assert_called_once()

    def test_save_to_file_error(self):
        """Vérifie _save_to_file gère les erreurs."""
        with patch.object(FileAttenteHorsLigne, "_ensure_cache_dir"):
            with patch("builtins.open", side_effect=OSError("Write error")):
                # Ne devrait pas lever d'exception
                FileAttenteHorsLigne._save_to_file([{"id": "test"}])


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Tests SynchroniseurHorsLigne
# ═══════════════════════════════════════════════════════════════════════════════


class TestSynchroniseurHorsLigne:
    """Tests pour SynchroniseurHorsLigne."""

    @patch("src.core.offline.GestionnaireConnexion")
    def test_sync_all_pas_en_ligne(self, mock_conn):
        """Vérifie sync_all retourne erreur si pas en ligne."""
        mock_conn.est_en_ligne.return_value = False
        result = SynchroniseurHorsLigne.sync_all()
        assert result["success"] == 0
        assert result["failed"] == 0
        assert "Pas de connexion" in result["errors"]

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_sync_all_queue_vide(self, mock_queue, mock_conn):
        """Vérifie sync_all avec queue vide."""
        mock_conn.est_en_ligne.return_value = True
        mock_queue.obtenir_en_attente.return_value = []

        result = SynchroniseurHorsLigne.sync_all()
        assert result["success"] == 0
        assert result["failed"] == 0
        assert result["errors"] == []

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_sync_all_avec_callback(self, mock_queue, mock_conn):
        """Vérifie sync_all appelle le callback de progression."""
        mock_conn.est_en_ligne.return_value = True
        mock_queue.obtenir_en_attente.return_value = [
            OperationEnAttente(id="op1", model_name="test", data={}),
        ]

        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        with patch.object(SynchroniseurHorsLigne, "_sync_operation", return_value=True):
            result = SynchroniseurHorsLigne.sync_all(progress_callback=progress_callback)
            assert len(progress_calls) == 1
            assert progress_calls[0] == (1, 1)

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_sync_all_succes(self, mock_queue, mock_conn):
        """Vérifie sync_all avec opérations réussies."""
        mock_conn.est_en_ligne.return_value = True
        mock_queue.obtenir_en_attente.return_value = [
            OperationEnAttente(id="op1", model_name="recette", data={}),
            OperationEnAttente(id="op2", model_name="recette", data={}),
        ]

        with patch.object(SynchroniseurHorsLigne, "_sync_operation", return_value=True):
            result = SynchroniseurHorsLigne.sync_all()
            assert result["success"] == 2
            assert result["failed"] == 0
            assert mock_queue.remove.call_count == 2

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_sync_all_echec(self, mock_queue, mock_conn):
        """Vérifie sync_all avec opérations échouées."""
        mock_conn.est_en_ligne.return_value = True
        mock_queue.obtenir_en_attente.return_value = [
            OperationEnAttente(id="op1", model_name="test", data={}),
        ]

        mock_queue.mettre_a_jour_tentative = MagicMock()

        with patch.object(SynchroniseurHorsLigne, "_sync_operation", return_value=False):
            result = SynchroniseurHorsLigne.sync_all()
            assert result["success"] == 0
            assert result["failed"] == 1

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_sync_all_exception(self, mock_queue, mock_conn):
        """Vérifie sync_all gère les exceptions."""
        mock_conn.est_en_ligne.return_value = True
        mock_queue.obtenir_en_attente.return_value = [
            OperationEnAttente(id="op1", model_name="test", data={}),
        ]
        mock_queue.mettre_a_jour_tentative = MagicMock()

        with patch.object(
            SynchroniseurHorsLigne, "_sync_operation", side_effect=Exception("Sync error")
        ):
            result = SynchroniseurHorsLigne.sync_all()
            assert result["failed"] == 1
            assert len(result["errors"]) == 1

    def test_sync_operation_modele_non_supporte(self):
        """Vérifie _sync_operation retourne False pour modèle non supporté."""
        op = OperationEnAttente(model_name="modele_inconnu", data={})
        result = SynchroniseurHorsLigne._sync_operation(op)
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Tests avec_mode_hors_ligne décorateur
# ═══════════════════════════════════════════════════════════════════════════════


class TestAvecModeHorsLigne:
    """Tests pour le décorateur avec_mode_hors_ligne."""

    @patch("src.core.offline.GestionnaireConnexion")
    def test_decorateur_online_execute_fonction(self, mock_conn):
        """Vérifie que le décorateur exécute la fonction si online."""
        mock_conn.est_en_ligne.return_value = True

        @avec_mode_hors_ligne("recette", TypeOperation.CREATE)
        def creer_recette(data):
            return {"id": 1, **data}

        result = creer_recette(data={"nom": "Tarte"})
        assert result == {"id": 1, "nom": "Tarte"}

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_decorateur_offline_met_en_queue(self, mock_queue, mock_conn):
        """Vérifie que le décorateur met en queue si offline."""
        mock_conn.est_en_ligne.return_value = False
        mock_queue.add.return_value = OperationEnAttente(
            model_name="recette", data={"nom": "Tarte"}
        )

        @avec_mode_hors_ligne("recette", TypeOperation.CREATE)
        def creer_recette(data):
            return {"id": 1, **data}

        result = creer_recette(data={"nom": "Tarte"})
        assert result["_offline"] is True
        mock_queue.add.assert_called_once()

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_decorateur_erreur_connexion_offline(self, mock_queue, mock_conn):
        """Vérifie que le décorateur bascule en queue sur erreur connexion."""
        # D'abord online, puis erreur
        mock_conn.est_en_ligne.return_value = True
        mock_conn.gerer_erreur_connexion = MagicMock()
        mock_queue.add.return_value = OperationEnAttente(model_name="test", data={})

        @avec_mode_hors_ligne("test")
        def fonction_qui_echoue(data):
            raise Exception("connection timeout")

        # La fonction lève une exception "connection" donc bascule en mode offline
        result = fonction_qui_echoue(data={"test": 1})
        mock_conn.gerer_erreur_connexion.assert_called()

    @patch("src.core.offline.GestionnaireConnexion")
    def test_decorateur_erreur_non_connexion_propage(self, mock_conn):
        """Vérifie que les erreurs non-connexion sont propagées."""
        mock_conn.est_en_ligne.return_value = True

        @avec_mode_hors_ligne("test")
        def fonction_erreur(data):
            raise ValueError("Validation error")

        with pytest.raises(ValueError, match="Validation error"):
            fonction_erreur(data={})

    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_decorateur_avec_args_positionnels(self, mock_queue, mock_conn):
        """Vérifie le décorateur avec arguments positionnels."""
        mock_conn.est_en_ligne.return_value = False
        mock_queue.add.return_value = OperationEnAttente(data={"test": 1})

        @avec_mode_hors_ligne("test")
        def fonction(premier_arg):
            return premier_arg

        result = fonction({"test": 1})
        assert result["_offline"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Tests Composants UI
# ═══════════════════════════════════════════════════════════════════════════════


class TestComposantsUI:
    """Tests pour les composants UI (afficher_statut_connexion, afficher_panneau_sync)."""

    @patch("src.core.offline.st")
    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_statut_connexion_online(self, mock_queue, mock_conn, mock_st):
        """Vérifie l'affichage du statut ONLINE."""
        mock_conn.obtenir_statut.return_value = StatutConnexion.ONLINE
        mock_queue.obtenir_nombre.return_value = 0

        afficher_statut_connexion()

        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "En ligne" in call_args
        assert "🟢" in call_args

    @patch("src.core.offline.st")
    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_statut_connexion_offline(self, mock_queue, mock_conn, mock_st):
        """Vérifie l'affichage du statut OFFLINE."""
        mock_conn.obtenir_statut.return_value = StatutConnexion.OFFLINE
        mock_queue.obtenir_nombre.return_value = 0

        afficher_statut_connexion()

        call_args = mock_st.markdown.call_args[0][0]
        assert "Hors ligne" in call_args
        assert "🔴" in call_args

    @patch("src.core.offline.st")
    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_statut_connexion_avec_pending(self, mock_queue, mock_conn, mock_st):
        """Vérifie l'affichage avec opérations en attente."""
        mock_conn.obtenir_statut.return_value = StatutConnexion.ONLINE
        mock_queue.obtenir_nombre.return_value = 5

        afficher_statut_connexion()

        call_args = mock_st.markdown.call_args[0][0]
        assert "5" in call_args  # Badge avec le nombre

    @patch("src.core.offline.st")
    @patch("src.core.offline.GestionnaireConnexion")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_statut_connexion_connecting(self, mock_queue, mock_conn, mock_st):
        """Vérifie l'affichage du statut CONNECTING."""
        mock_conn.obtenir_statut.return_value = StatutConnexion.CONNECTING
        mock_queue.obtenir_nombre.return_value = 0

        afficher_statut_connexion()

        call_args = mock_st.markdown.call_args[0][0]
        assert "Connexion..." in call_args
        assert "🟡" in call_args

    @patch("src.core.offline.st")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_panneau_sync_vide(self, mock_queue, mock_st):
        """Vérifie l'affichage du panneau quand queue vide."""
        mock_queue.obtenir_nombre.return_value = 0
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        afficher_panneau_sync()

        mock_st.expander.assert_called_once()
        assert "0 en attente" in mock_st.expander.call_args[0][0]

    @patch("src.core.offline.st")
    @patch("src.core.offline.FileAttenteHorsLigne")
    def test_afficher_panneau_sync_avec_operations(self, mock_queue, mock_st):
        """Vérifie l'affichage du panneau avec opérations."""
        mock_queue.obtenir_nombre.return_value = 3
        mock_queue.obtenir_en_attente.return_value = [
            OperationEnAttente(id="op1", model_name="Test", operation_type=TypeOperation.CREATE),
            OperationEnAttente(
                id="op2",
                model_name="Test2",
                operation_type=TypeOperation.UPDATE,
                retry_count=1,
                last_error="Err",
            ),
        ]

        # Mock context manager
        mock_expander = MagicMock()
        mock_st.expander.return_value = mock_expander
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        afficher_panneau_sync()

        assert "3 en attente" in mock_st.expander.call_args[0][0]
