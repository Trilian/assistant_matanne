"""
Tests pour src/api/routes/utilitaires.py

Tests unitaires des routes utilitaires — notes, journal, contacts,
liens, mots de passe maison, énergie.
"""

from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

NOTE_TEST = {
    "id": 1,
    "titre": "Liste à faire",
    "contenu": "Acheter du pain",
    "categorie": "taches",
    "couleur": "#ff0000",
    "epingle": True,
    "est_checklist": False,
    "items_checklist": None,
    "tags": ["urgent"],
    "archive": False,
    "cree_le": "2025-06-01",
}

JOURNAL_TEST = {
    "id": 1,
    "date_entree": "2025-06-01",
    "contenu": "Belle journée en famille",
    "humeur": "joyeux",
    "energie": 8,
    "gratitudes": ["Soleil", "Santé"],
    "tags": ["famille"],
    "cree_le": "2025-06-01",
}

CONTACT_TEST = {
    "id": 1,
    "nom": "Dr. Martin",
    "categorie": "santé",
    "specialite": "Pédiatre",
    "telephone": "0612345678",
    "email": "martin@sante.fr",
    "adresse": "10 rue Santé, Lyon",
    "horaires": "9h-18h",
    "favori": True,
}

LIEN_TEST = {
    "id": 1,
    "titre": "Documentation Next.js",
    "url": "https://nextjs.org/docs",
    "categorie": "dev",
    "description": "Doc officielle",
    "tags": ["dev", "react"],
    "favori": True,
}

MOT_DE_PASSE_TEST = {
    "id": 1,
    "nom": "WiFi maison",
    "categorie": "reseau",
    "identifiant": "MonWiFi",
    "valeur_chiffree": "encrypted_xxx",
    "notes": "Box Orange",
}

RELEVE_ENERGIE_TEST = {
    "id": 1,
    "type_energie": "electricite",
    "mois": 6,
    "annee": 2025,
    "valeur_compteur": 12345.0,
    "consommation": 320.5,
    "unite": "kWh",
    "montant": 52.80,
    "notes": None,
}


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def client():
    """Client HTTP léger pour tester les routes."""
    import httpx

    from src.api.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def creer_mock(data: dict) -> MagicMock:
    """Crée un mock avec attributs depuis un dict."""
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS — EXISTENCE DES ENDPOINTS
# ═══════════════════════════════════════════════════════════


@pytest.mark.asyncio(loop_scope="function")
class TestEndpointsExistent:
    """Vérifie que les endpoints utilitaires existent (pas 404/405)."""

    @pytest.mark.parametrize(
        "method,path",
        [
            # Notes
            ("GET", "/api/v1/utilitaires/notes"),
            ("POST", "/api/v1/utilitaires/notes"),
            ("PATCH", "/api/v1/utilitaires/notes/1"),
            ("DELETE", "/api/v1/utilitaires/notes/1"),
            # Journal
            ("GET", "/api/v1/utilitaires/journal"),
            ("POST", "/api/v1/utilitaires/journal"),
            ("PATCH", "/api/v1/utilitaires/journal/1"),
            ("DELETE", "/api/v1/utilitaires/journal/1"),
            # Contacts
            ("GET", "/api/v1/utilitaires/contacts"),
            ("POST", "/api/v1/utilitaires/contacts"),
            ("PATCH", "/api/v1/utilitaires/contacts/1"),
            ("DELETE", "/api/v1/utilitaires/contacts/1"),
            # Liens
            ("GET", "/api/v1/utilitaires/liens"),
            ("POST", "/api/v1/utilitaires/liens"),
            ("PATCH", "/api/v1/utilitaires/liens/1"),
            ("DELETE", "/api/v1/utilitaires/liens/1"),
            # Mots de passe
            ("GET", "/api/v1/utilitaires/passwords"),
            ("POST", "/api/v1/utilitaires/passwords"),
            ("PATCH", "/api/v1/utilitaires/passwords/1"),
            ("DELETE", "/api/v1/utilitaires/passwords/1"),
            # Énergie
            ("GET", "/api/v1/utilitaires/energie"),
            ("POST", "/api/v1/utilitaires/energie"),
            ("PATCH", "/api/v1/utilitaires/energie/1"),
            ("DELETE", "/api/v1/utilitaires/energie/1"),
        ],
    )
    async def test_endpoint_existe(self, client, method, path):
        """L'endpoint existe (pas 404 ni 405)."""
        func = getattr(client, method.lower())
        if method == "POST" and "notes" in path:
            response = await func(path, json={"titre": "Test"})
        elif method == "POST" and "journal" in path:
            response = await func(
                path, json={"date_entree": "2025-01-01", "contenu": "Test"}
            )
        elif method == "POST" and "contacts" in path:
            response = await func(path, json={"nom": "Test"})
        elif method == "POST" and "liens" in path:
            response = await func(
                path, json={"titre": "Test", "url": "https://example.com"}
            )
        elif method == "POST" and "passwords" in path:
            response = await func(
                path, json={"nom": "Test", "valeur": "secret123"}
            )
        elif method == "POST" and "energie" in path:
            response = await func(
                path,
                json={"type_energie": "electricite", "mois": 1, "annee": 2025},
            )
        elif method in ("POST", "PATCH"):
            response = await func(path, json={"nom": "test"})
        else:
            response = await func(path)
        assert response.status_code not in (404, 405), (
            f"{method} {path} retourne {response.status_code}"
        )


# ═══════════════════════════════════════════════════════════
# TESTS — SCHEMAS PYDANTIC UTILITAIRES
# ═══════════════════════════════════════════════════════════


class TestSchemasUtilitaires:
    """Tests schemas Pydantic pour le domaine utilitaires."""

    def test_note_create_valide(self):
        from src.api.schemas.utilitaires import NoteCreate

        n = NoteCreate(titre="Ma note", contenu="Contenu")
        assert n.titre == "Ma note"
        assert n.epingle is False

    def test_note_create_titre_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import NoteCreate

        with pytest.raises(ValidationError):
            NoteCreate(titre="")

    def test_note_patch_optionnel(self):
        from src.api.schemas.utilitaires import NotePatch

        p = NotePatch(epingle=True)
        assert p.epingle is True
        assert p.titre is None

    def test_journal_create_valide(self):
        from src.api.schemas.utilitaires import JournalCreate

        j = JournalCreate(date_entree="2025-06-01", contenu="Belle journée")
        assert j.contenu == "Belle journée"
        assert j.energie is None

    def test_journal_create_contenu_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import JournalCreate

        with pytest.raises(ValidationError):
            JournalCreate(date_entree="2025-06-01", contenu="")

    def test_journal_energie_hors_bornes_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import JournalCreate

        with pytest.raises(ValidationError):
            JournalCreate(date_entree="2025-06-01", contenu="test", energie=11)

    def test_contact_create_valide(self):
        from src.api.schemas.utilitaires import ContactCreate

        c = ContactCreate(nom="Dr. Martin", categorie="santé")
        assert c.nom == "Dr. Martin"
        assert c.favori is False

    def test_contact_create_nom_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import ContactCreate

        with pytest.raises(ValidationError):
            ContactCreate(nom="")

    def test_lien_create_valide(self):
        from src.api.schemas.utilitaires import LienCreate

        l = LienCreate(titre="Google", url="https://google.com")
        assert l.titre == "Google"
        assert l.favori is False

    def test_lien_create_url_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import LienCreate

        with pytest.raises(ValidationError):
            LienCreate(titre="Test", url="")

    def test_motdepasse_create_valide(self):
        from src.api.schemas.utilitaires import MotDePasseCreate

        m = MotDePasseCreate(nom="WiFi", valeur="secret")
        assert m.nom == "WiFi"
        assert m.categorie == "autre"

    def test_motdepasse_create_valeur_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import MotDePasseCreate

        with pytest.raises(ValidationError):
            MotDePasseCreate(nom="WiFi", valeur="")

    def test_energie_create_valide(self):
        from src.api.schemas.utilitaires import EnergieCreate

        e = EnergieCreate(type_energie="electricite", mois=6, annee=2025)
        assert e.unite == "kWh"
        assert e.montant is None

    def test_energie_type_invalide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import EnergieCreate

        with pytest.raises(ValidationError):
            EnergieCreate(type_energie="fioul", mois=6, annee=2025)

    def test_energie_mois_hors_bornes_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.utilitaires import EnergieCreate

        with pytest.raises(ValidationError):
            EnergieCreate(type_energie="gaz", mois=13, annee=2025)


# ═══════════════════════════════════════════════════════════
# TESTS — FORMAT DES RÉPONSES
# ═══════════════════════════════════════════════════════════


@pytest.mark.asyncio(loop_scope="function")
class TestFormatsReponses:
    """Vérifie le format des réponses JSON des endpoints."""

    @patch("src.api.routes.utilitaires.executer_avec_session")
    @patch("src.api.routes.utilitaires.executer_async")
    async def test_lister_notes_format(self, mock_exec, mock_session, client):
        """La liste de notes retourne le bon format."""
        mock_exec.side_effect = lambda fn: fn()
        mock_note = creer_mock(NOTE_TEST)
        mock_note.cree_le = MagicMock()
        mock_note.cree_le.isoformat.return_value = "2025-06-01"

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_note]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/utilitaires/notes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["titre"] == "Liste à faire"

    @patch("src.api.routes.utilitaires.executer_avec_session")
    @patch("src.api.routes.utilitaires.executer_async")
    async def test_lister_contacts_format(self, mock_exec, mock_session, client):
        """La liste de contacts retourne items triés par favori."""
        mock_exec.side_effect = lambda fn: fn()
        mock_contact = creer_mock(CONTACT_TEST)

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_contact]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/utilitaires/contacts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["nom"] == "Dr. Martin"

    @patch("src.api.routes.utilitaires.executer_avec_session")
    @patch("src.api.routes.utilitaires.executer_async")
    async def test_lister_energie_format(self, mock_exec, mock_session, client):
        """La liste de relevés énergie retourne le bon format."""
        mock_exec.side_effect = lambda fn: fn()
        mock_releve = creer_mock(RELEVE_ENERGIE_TEST)

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_releve]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/utilitaires/energie")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["type_energie"] == "electricite"

    @patch("src.api.routes.utilitaires.executer_avec_session")
    @patch("src.api.routes.utilitaires.executer_async")
    async def test_creer_mot_de_passe_chiffre_la_valeur(self, mock_exec, mock_session, client):
        """La création chiffre la valeur en clair avant stockage."""
        from src.api.auth import _obtenir_api_secret
        from src.services.utilitaires.service import MotsDePasseService

        mock_exec.side_effect = lambda fn: fn()

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        session.add.side_effect = lambda instance: setattr(session, "dernier_mdp", instance)
        session.refresh.side_effect = lambda instance: setattr(instance, "id", 7)
        mock_session.return_value = ctx

        response = await client.post(
            "/api/v1/utilitaires/passwords",
            json={"nom": "WiFi invité", "categorie": "reseau", "valeur": "super-secret"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valeur_chiffree"] != "super-secret"
        assert session.dernier_mdp.valeur_chiffree == data["valeur_chiffree"]
        assert (
            MotsDePasseService().dechiffrer(data["valeur_chiffree"], _obtenir_api_secret())
            == "super-secret"
        )

    @patch("src.api.routes.utilitaires.executer_avec_session")
    @patch("src.api.routes.utilitaires.executer_async")
    async def test_modifier_mot_de_passe_rechiffre_la_valeur(self, mock_exec, mock_session, client):
        """Une mise à jour de valeur remplace le secret clair par une valeur chiffrée."""
        from src.api.auth import _obtenir_api_secret
        from src.services.utilitaires.service import MotsDePasseService

        mock_exec.side_effect = lambda fn: fn()
        mdp = creer_mock(MOT_DE_PASSE_TEST)

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        session.query.return_value.filter.return_value.first.return_value = mdp
        session.refresh.side_effect = lambda instance: instance
        mock_session.return_value = ctx

        response = await client.patch(
            "/api/v1/utilitaires/passwords/1",
            json={"valeur": "nouveau-secret", "notes": "Mis à jour"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valeur_chiffree"] != "nouveau-secret"
        assert data["notes"] == "Mis à jour"
        assert (
            MotsDePasseService().dechiffrer(data["valeur_chiffree"], _obtenir_api_secret())
            == "nouveau-secret"
        )


# ═══════════════════════════════════════════════════════════
# TESTS — MÉMO VOCAL
# ═══════════════════════════════════════════════════════════


@pytest.mark.asyncio(loop_scope="function")
class TestMemoVocalRoute:
    """Tests POST /api/v1/utilitaires/memos/vocal"""

    @pytest.mark.asyncio
    async def test_memo_vocal_success(self, client):
        """Classification mémo vocal → 200."""
        from src.services.utilitaires.memo_vocal import MemoClassifie

        mock_svc = MagicMock()
        mock_svc.transcrire_et_classer.return_value = MemoClassifie(
            module="courses",
            action="ajouter",
            contenu="lait, pain",
            tags=["alimentation"],
            destination_url="/cuisine/courses",
            confiance=0.92,
        )

        with patch(
            "src.services.utilitaires.memo_vocal.get_memo_vocal_service",
            return_value=mock_svc,
        ):
            response = await client.post(
                "/api/v1/utilitaires/memos/vocal",
                json={"texte": "Acheter du lait et du pain"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "courses"
        assert data["destination_url"] == "/cuisine/courses"
