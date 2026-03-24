"""
Tests pour src/api/routes/famille.py

Tests unitaires des routes famille — enfants, activités, jalons,
budget, shopping, routines, anniversaires, événements familiaux.
"""

from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio(loop_scope="function")


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

ENFANT_TEST = {
    "id": 1,
    "name": "Jules",
    "date_of_birth": "2023-06-15",
    "gender": "M",
    "notes": "Petit bonhomme",
    "actif": True,
    "taille_vetements": {"haut": "3A", "bas": "3A"},
    "pointure": 24,
    "cree_le": "2025-01-01",
}

JALON_TEST = {
    "id": 1,
    "titre": "Premier pas",
    "description": "A marché tout seul",
    "categorie": "motricite",
    "date_atteint": "2024-06-15",
    "photo_url": None,
}

ACTIVITE_TEST = {
    "id": 1,
    "titre": "Sortie au parc",
    "description": "Parc de la Tête d'Or",
    "type_activite": "sortie",
    "date_prevue": "2026-05-15",
    "duree_heures": 3.0,
    "lieu": "Lyon",
    "statut": "planifié",
    "cout_estime": 20.0,
    "cout_reel": None,
}

ACTIVITE_NOUVELLE = {
    "titre": "Cinéma en famille",
    "type_activite": "sortie",
    "date_prevue": "2026-06-01",
    "lieu": "Pathé",
}

DEPENSE_TEST = {
    "id": 1,
    "date": "2026-03-15",
    "categorie": "loisirs",
    "description": "Cinéma",
    "montant": 35.0,
    "magasin": "Pathé",
    "est_recurrent": False,
}

ANNIVERSAIRE_TEST = {
    "id": 1,
    "nom_personne": "Mamie Françoise",
    "date_naissance": "1955-08-20",
    "relation": "grand_parent",
    "rappel_jours_avant": [7, 1, 0],
    "idees_cadeaux": "Livre, foulard",
    "historique_cadeaux": [],
    "notes": None,
    "actif": True,
    "age": 70,
    "jours_restants": 45,
    "cree_le": "2025-01-01",
}

EVENEMENT_TEST = {
    "id": 1,
    "titre": "Noël en famille",
    "date_evenement": "2026-12-25",
    "type_evenement": "fete",
    "recurrence": "annuelle",
    "rappel_jours_avant": 7,
    "notes": "Chez les grands-parents",
    "participants": ["Jules", "Maman", "Papa"],
    "actif": True,
    "cree_le": "2025-01-01",
}

ROUTINE_TEST = {
    "id": 1,
    "nom": "Routine du matin",
    "categorie": "matin",
    "actif": True,
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


class TestEndpointsExistent:
    """Vérifie que les endpoints famille existent (pas 404/405)."""

    @pytest.mark.parametrize(
        "method,path",
        [
            # Enfants
            ("GET", "/api/v1/famille/enfants"),
            ("GET", "/api/v1/famille/enfants/1"),
            # Jalons
            ("GET", "/api/v1/famille/enfants/1/jalons"),
            ("POST", "/api/v1/famille/enfants/1/jalons"),
            ("DELETE", "/api/v1/famille/enfants/1/jalons/1"),
            # Activités
            ("GET", "/api/v1/famille/activites"),
            ("GET", "/api/v1/famille/activites/1"),
            ("POST", "/api/v1/famille/activites"),
            ("PATCH", "/api/v1/famille/activites/1"),
            ("DELETE", "/api/v1/famille/activites/1"),
            # Budget
            ("GET", "/api/v1/famille/budget"),
            ("GET", "/api/v1/famille/budget/stats"),
            ("POST", "/api/v1/famille/budget"),
            ("DELETE", "/api/v1/famille/budget/1"),
            # Shopping
            ("GET", "/api/v1/famille/shopping"),
            # Routines
            ("GET", "/api/v1/famille/routines"),
            ("GET", "/api/v1/famille/routines/1"),
            ("POST", "/api/v1/famille/routines"),
            ("PATCH", "/api/v1/famille/routines/1"),
            ("DELETE", "/api/v1/famille/routines/1"),
            # Anniversaires
            ("GET", "/api/v1/famille/anniversaires"),
            ("GET", "/api/v1/famille/anniversaires/1"),
            ("POST", "/api/v1/famille/anniversaires"),
            ("PATCH", "/api/v1/famille/anniversaires/1"),
            ("DELETE", "/api/v1/famille/anniversaires/1"),
            # Événements
            ("GET", "/api/v1/famille/evenements"),
            ("POST", "/api/v1/famille/evenements"),
            ("PATCH", "/api/v1/famille/evenements/1"),
            ("DELETE", "/api/v1/famille/evenements/1"),
        ],
    )
    async def test_endpoint_existe(self, client, method, path):
        """L'endpoint existe (pas 404 ni 405)."""
        func = getattr(client, method.lower())
        if method == "POST" and "jalons" in path:
            response = await func(path, json={"titre": "test", "categorie": "autre"})
        elif method == "POST" and "activites" in path:
            response = await func(path, json={"titre": "test", "date_prevue": "2026-01-01"})
        elif method == "POST" and "budget" in path:
            response = await func(path, json={"categorie": "test", "montant": 10.0})
        elif method == "POST" and "routines" in path:
            response = await func(path, json={"nom": "test"})
        elif method == "POST" and "anniversaires" in path:
            response = await func(
                path,
                json={
                    "nom_personne": "Test",
                    "date_naissance": "2000-01-01",
                    "relation": "ami",
                },
            )
        elif method == "POST" and "evenements" in path:
            response = await func(
                path,
                json={
                    "titre": "Test",
                    "date_evenement": "2026-01-01",
                    "type_evenement": "fete",
                },
            )
        elif method in ("POST", "PATCH"):
            response = await func(path, json={"nom": "test"})
        else:
            response = await func(path)
        assert response.status_code not in (404, 405), (
            f"{method} {path} retourne {response.status_code}"
        )


# ═══════════════════════════════════════════════════════════
# TESTS — SCHEMAS PYDANTIC FAMILLE
# ═══════════════════════════════════════════════════════════


class TestSchemasFamille:
    """Tests schemas Pydantic pour le domaine famille."""

    def test_anniversaire_create_valide(self):
        from src.api.schemas.famille import AnniversaireCreate

        a = AnniversaireCreate(
            nom_personne="Mamie",
            date_naissance="1955-08-20",
            relation="grand_parent",
        )
        assert a.nom_personne == "Mamie"
        assert a.relation == "grand_parent"
        assert a.rappel_jours_avant == [7, 1, 0]

    def test_anniversaire_create_nom_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.famille import AnniversaireCreate

        with pytest.raises(ValidationError):
            AnniversaireCreate(
                nom_personne="",
                date_naissance="1955-08-20",
                relation="ami",
            )

    def test_anniversaire_patch_optionnel(self):
        from src.api.schemas.famille import AnniversairePatch

        p = AnniversairePatch(notes="Nouveau cadeau")
        assert p.notes == "Nouveau cadeau"
        assert p.nom_personne is None

    def test_evenement_create_valide(self):
        from src.api.schemas.famille import EvenementFamilialCreate

        e = EvenementFamilialCreate(
            titre="Noël",
            date_evenement="2026-12-25",
            type_evenement="fete",
        )
        assert e.titre == "Noël"
        assert e.recurrence == "unique"

    def test_evenement_create_titre_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.famille import EvenementFamilialCreate

        with pytest.raises(ValidationError):
            EvenementFamilialCreate(
                titre="",
                date_evenement="2026-12-25",
                type_evenement="fete",
            )

    def test_evenement_patch_optionnel(self):
        from src.api.schemas.famille import EvenementFamilialPatch

        p = EvenementFamilialPatch(recurrence="annuelle")
        assert p.recurrence == "annuelle"
        assert p.titre is None

    def test_anniversaire_response(self):
        from src.api.schemas.famille import AnniversaireResponse

        r = AnniversaireResponse(
            id=1,
            nom_personne="Mamie",
            date_naissance="1955-08-20",
            relation="grand_parent",
            age=70,
            jours_restants=45,
        )
        assert r.id == 1
        assert r.actif is True

    def test_evenement_response(self):
        from src.api.schemas.famille import EvenementFamilialResponse

        r = EvenementFamilialResponse(
            id=1,
            titre="Noël",
            date_evenement="2026-12-25",
            type_evenement="fete",
        )
        assert r.recurrence == "unique"
        assert r.rappel_jours_avant == 7


# ═══════════════════════════════════════════════════════════
# TESTS — FORMAT DES RÉPONSES
# ═══════════════════════════════════════════════════════════


class TestFormatsReponses:
    """Vérifie le format des réponses JSON des endpoints."""

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_enfants_format(self, mock_exec, mock_session, client):
        """La liste d'enfants retourne le bon format paginé."""
        mock_exec.side_effect = lambda fn: fn()
        mock_child = creer_mock(ENFANT_TEST)
        mock_child.date_of_birth = MagicMock()
        mock_child.date_of_birth.isoformat.return_value = "2023-06-15"
        mock_child.cree_le = None

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.count.return_value = 1
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_child
        ]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/enfants")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_activites_format(self, mock_exec, mock_session, client):
        """La liste d'activités retourne le bon format."""
        mock_exec.side_effect = lambda fn: fn()
        mock_act = creer_mock(ACTIVITE_TEST)
        mock_act.date_prevue = MagicMock()
        mock_act.date_prevue.isoformat.return_value = "2026-05-15"

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value = query
        query.count.return_value = 1
        query.offset.return_value.limit.return_value.all.return_value = [mock_act]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/activites")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_depenses_format(self, mock_exec, mock_session, client):
        """La liste de dépenses retourne le bon format paginé."""
        mock_exec.side_effect = lambda fn: fn()
        mock_dep = creer_mock(DEPENSE_TEST)
        mock_dep.date = MagicMock()
        mock_dep.date.isoformat.return_value = "2026-03-15"

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.count.return_value = 1
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_dep
        ]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/budget")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["montant"] == 35.0

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_anniversaires_format(self, mock_exec, mock_session, client):
        """La liste anniversaires retourne items triés par jours_restants."""
        mock_exec.side_effect = lambda fn: fn()
        mock_anniv = creer_mock(ANNIVERSAIRE_TEST)
        mock_anniv.date_naissance = MagicMock()
        mock_anniv.date_naissance.isoformat.return_value = "1955-08-20"
        mock_anniv.cree_le = MagicMock()
        mock_anniv.cree_le.isoformat.return_value = "2025-01-01"

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_anniv]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/anniversaires")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_evenements_format(self, mock_exec, mock_session, client):
        """La liste événements retourne items."""
        mock_exec.side_effect = lambda fn: fn()
        mock_evt = creer_mock(EVENEMENT_TEST)
        mock_evt.date_evenement = MagicMock()
        mock_evt.date_evenement.isoformat.return_value = "2026-12-25"
        mock_evt.cree_le = MagicMock()
        mock_evt.cree_le.isoformat.return_value = "2025-01-01"

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_evt]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/evenements")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
