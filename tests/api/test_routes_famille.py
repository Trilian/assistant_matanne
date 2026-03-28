"""
Tests pour src/api/routes/famille.py.

Les tests API utilisent uniquement le router famille afin d'eviter
les erreurs d'import d'autres modules FastAPI non lies a ce fichier.
"""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
import pytest
import pytest_asyncio


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

ACTIVITE_TEST = {
    "id": 1,
    "titre": "Sortie au parc",
    "description": "Parc de la Tete d'Or",
    "type_activite": "sortie",
    "date_prevue": "2026-05-15",
    "duree_heures": 3.0,
    "lieu": "Lyon",
    "statut": "planifie",
    "cout_estime": 20.0,
    "cout_reel": None,
}

DEPENSE_TEST = {
    "id": 1,
    "date": "2026-03-15",
    "categorie": "loisirs",
    "description": "Cinema",
    "montant": 35.0,
    "magasin": "Pathe",
    "est_recurrent": False,
}

ANNIVERSAIRE_TEST = {
    "id": 1,
    "nom_personne": "Mamie Francoise",
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
    "titre": "Noel en famille",
    "date_evenement": "2026-12-25",
    "type_evenement": "fete",
    "recurrence": "annuelle",
    "rappel_jours_avant": 7,
    "notes": "Chez les grands-parents",
    "participants": ["Jules", "Maman", "Papa"],
    "actif": True,
    "cree_le": "2025-01-01",
}

ACHAT_TEST = {
    "id": 1,
    "nom": "Pull Jules",
    "categorie": "jules_vetements",
    "priorite": "haute",
    "prix_estime": 25.0,
    "prix_reel": None,
    "taille": "3A",
    "magasin": None,
    "url": None,
    "description": None,
    "age_recommande_mois": None,
    "suggere_par": None,
    "achete": False,
    "date_achat": None,
    "pour_qui": "jules",
    "a_revendre": True,
    "prix_revente_estime": 10.0,
    "vendu_le": None,
}


def creer_mock(data: dict) -> MagicMock:
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


@pytest_asyncio.fixture
async def client():
    import httpx

    from src.api.dependencies import require_auth
    from src.api.routes.famille import router

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "admin"}

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestEndpointsExistent:
    @pytest.mark.parametrize(
        "method,path",
        [
            ("GET", "/api/v1/famille/enfants"),
            ("GET", "/api/v1/famille/enfants/1"),
            ("GET", "/api/v1/famille/enfants/1/jalons"),
            ("POST", "/api/v1/famille/enfants/1/jalons"),
            ("DELETE", "/api/v1/famille/enfants/1/jalons/1"),
            ("GET", "/api/v1/famille/activites"),
            ("GET", "/api/v1/famille/activites/1"),
            ("POST", "/api/v1/famille/activites"),
            ("PATCH", "/api/v1/famille/activites/1"),
            ("DELETE", "/api/v1/famille/activites/1"),
            ("GET", "/api/v1/famille/budget"),
            ("GET", "/api/v1/famille/budget/stats"),
            ("POST", "/api/v1/famille/budget"),
            ("DELETE", "/api/v1/famille/budget/1"),
            ("GET", "/api/v1/famille/shopping"),
            ("GET", "/api/v1/famille/routines"),
            ("GET", "/api/v1/famille/routines/1"),
            ("POST", "/api/v1/famille/routines"),
            ("PATCH", "/api/v1/famille/routines/1"),
            ("DELETE", "/api/v1/famille/routines/1"),
            ("GET", "/api/v1/famille/anniversaires"),
            ("GET", "/api/v1/famille/anniversaires/1"),
            ("POST", "/api/v1/famille/anniversaires"),
            ("PATCH", "/api/v1/famille/anniversaires/1"),
            ("DELETE", "/api/v1/famille/anniversaires/1"),
            ("GET", "/api/v1/famille/evenements"),
            ("POST", "/api/v1/famille/evenements"),
            ("PATCH", "/api/v1/famille/evenements/1"),
            ("DELETE", "/api/v1/famille/evenements/1"),
            ("GET", "/api/v1/famille/achats"),
            ("POST", "/api/v1/famille/achats"),
            ("POST", "/api/v1/famille/achats/1/achete"),
            ("POST", "/api/v1/famille/achats/1/vendu"),
            ("GET", "/api/v1/famille/achats/1/prefill-revente"),
            ("POST", "/api/v1/famille/achats/1/annonce-lbc"),
            ("POST", "/api/v1/famille/achats/1/annonce-vinted"),
            ("GET", "/api/v1/famille/anniversaires/1/checklist-auto"),
            ("POST", "/api/v1/famille/anniversaires/1/checklist-auto/synchroniser"),
            ("GET", "/api/v1/famille/anniversaires/1/checklists"),
            ("POST", "/api/v1/famille/anniversaires/1/checklists/1/items"),
            ("POST", "/api/v1/famille/anniversaires/1/checklists/1/items/1/vers-achats"),
            ("POST", "/api/v1/famille/weekend/1/convertir-activite"),
        ],
    )
    def test_endpoint_existe(self, method, path):
        from src.api.routes.famille import router

        assert any(
            route.path_regex.match(path) and method in route.methods
            for route in router.routes
            if hasattr(route, "methods")
        ), f"Route introuvable: {method} {path}"


class TestSchemasFamille:
    def test_anniversaire_create_valide(self):
        from src.api.schemas.famille import AnniversaireCreate

        item = AnniversaireCreate(
            nom_personne="Mamie",
            date_naissance="1955-08-20",
            relation="grand_parent",
        )
        assert item.rappel_jours_avant == [7, 1, 0]

    def test_anniversaire_create_nom_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.famille import AnniversaireCreate

        with pytest.raises(ValidationError):
            AnniversaireCreate(nom_personne="", date_naissance="1955-08-20", relation="ami")

    def test_anniversaire_patch_optionnel(self):
        from src.api.schemas.famille import AnniversairePatch

        item = AnniversairePatch(notes="Nouveau cadeau")
        assert item.nom_personne is None

    def test_evenement_create_valide(self):
        from src.api.schemas.famille import EvenementFamilialCreate

        item = EvenementFamilialCreate(
            titre="Noel",
            date_evenement="2026-12-25",
            type_evenement="fete",
        )
        assert item.recurrence == "unique"

    def test_evenement_create_titre_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.famille import EvenementFamilialCreate

        with pytest.raises(ValidationError):
            EvenementFamilialCreate(titre="", date_evenement="2026-12-25", type_evenement="fete")

    def test_evenement_patch_optionnel(self):
        from src.api.schemas.famille import EvenementFamilialPatch

        item = EvenementFamilialPatch(recurrence="annuelle")
        assert item.titre is None

    def test_anniversaire_response(self):
        from src.api.schemas.famille import AnniversaireResponse

        item = AnniversaireResponse(
            id=1,
            nom_personne="Mamie",
            date_naissance="1955-08-20",
            relation="grand_parent",
            age=70,
            jours_restants=45,
        )
        assert item.actif is True

    def test_evenement_response(self):
        from src.api.schemas.famille import EvenementFamilialResponse

        item = EvenementFamilialResponse(
            id=1,
            titre="Noel",
            date_evenement="2026-12-25",
            type_evenement="fete",
        )
        assert item.rappel_jours_avant == 7


@pytest.mark.asyncio
class TestFormatsReponses:
    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_enfants_format(self, mock_exec, mock_session, client):
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
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_child]
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
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_dep]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/budget")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["montant"] == 35.0

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_anniversaires_format(self, mock_exec, mock_session, client):
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
        assert "items" in response.json()

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_evenements_format(self, mock_exec, mock_session, client):
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
        assert "items" in response.json()


@pytest.mark.asyncio
class TestAchatsFormats:
    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_lister_achats_format(self, mock_exec, mock_session, client):
        mock_exec.side_effect = lambda fn: fn()
        mock_achat = creer_mock(ACHAT_TEST)

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value = query
        query.count.return_value = 1
        query.offset.return_value.limit.return_value.all.return_value = [mock_achat]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/achats")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


@pytest.mark.asyncio
class TestPrefillRevente:
    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_prefill_vetements_retourne_vinted(self, mock_exec, mock_session, client):
        mock_exec.side_effect = lambda fn: fn()
        mock_achat = creer_mock({**ACHAT_TEST, "categorie": "jules_vetements", "prix_reel": 30.0})

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        session.query.return_value.filter.return_value.first.return_value = mock_achat
        session.query.return_value.filter.return_value.filter.return_value.first.return_value = None
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/achats/1/prefill-revente")
        assert response.status_code == 200
        data = response.json()
        assert data["plateforme"] == "vinted"
        assert data["prix_suggere"] == pytest.approx(12.0)

    @patch("src.api.routes.famille.executer_avec_session")
    @patch("src.api.routes.famille.executer_async")
    async def test_prefill_electronique_retourne_lbc(self, mock_exec, mock_session, client):
        mock_exec.side_effect = lambda fn: fn()
        mock_achat = creer_mock({**ACHAT_TEST, "categorie": "electronique", "prix_reel": 100.0})

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        session.query.return_value.filter.return_value.first.return_value = mock_achat
        session.query.return_value.filter.return_value.filter.return_value.first.return_value = None
        mock_session.return_value = ctx

        response = await client.get("/api/v1/famille/achats/1/prefill-revente")
        assert response.status_code == 200
        assert response.json()["plateforme"] == "lbc"


class TestSchemasAchat:
    def test_achat_create_valide(self):
        from src.api.schemas.famille import AchatCreate

        item = AchatCreate(nom="Pull Jules", categorie="jules_vetements")
        assert item.nom == "Pull Jules"
        assert item.pour_qui == "famille"
        assert item.a_revendre is False

    def test_achat_create_nom_vide_rejete(self):
        from pydantic import ValidationError

        from src.api.schemas.famille import AchatCreate

        with pytest.raises(ValidationError):
            AchatCreate(nom="", categorie="jules_vetements")

    def test_achat_patch_optionnel(self):
        from src.api.schemas.famille import AchatPatch

        item = AchatPatch(priorite="urgente")
        assert item.nom is None

    def test_prefill_revente_response_valide(self):
        from src.api.schemas.famille import PrefillReventeResponse

        item = PrefillReventeResponse(
            achat_id=1,
            plateforme="vinted",
            plateforme_libelle="Vinted",
            taille="3A",
            prix_suggere=12.0,
            pour_qui="jules",
            raisons=["Vetements -> Vinted"],
        )
        assert item.plateforme == "vinted"
        assert item.raisons


class TestSubscribersIntelligents:
    def test_anniversaire_proche_subscriber_enregistre(self):
        import src.services.core.events.bus as bus_mod
        import src.services.core.events.subscribers as sub_mod
        from src.services.core.events.subscribers import _proposer_checklist_anniversaire_proche

        bus_mod._bus_instance = None
        sub_mod._subscribers_enregistres = False
        sub_mod.enregistrer_subscribers()

        bus = bus_mod.obtenir_bus()
        handlers = [
            sub.handler
            for topic, subs in bus._souscriptions.items()
            if topic == "anniversaire.proche"
            for sub in subs
        ]
        assert _proposer_checklist_anniversaire_proche in handlers

    def test_preferences_mise_a_jour_subscriber_enregistre(self):
        import src.services.core.events.bus as bus_mod
        import src.services.core.events.subscribers as sub_mod
        from src.services.core.events.subscribers import _invalider_cache_suggestions_achats

        bus_mod._bus_instance = None
        sub_mod._subscribers_enregistres = False
        sub_mod.enregistrer_subscribers()

        bus = bus_mod.obtenir_bus()
        handlers = [
            sub.handler
            for topic, subs in bus._souscriptions.items()
            if topic == "preferences.mise_a_jour"
            for sub in subs
        ]
        assert _invalider_cache_suggestions_achats in handlers

    def test_invalider_anniversaires_appel_cache(self):
        from src.services.core.events.bus import EvenementDomaine
        from src.services.core.events.subscribers import _invalider_cache_anniversaires

        cache = MagicMock()
        cache.invalidate.side_effect = [1, 2]
        event = EvenementDomaine(type="anniversaire.modifie", data={}, source="test")

        with patch("src.core.caching.obtenir_cache", return_value=cache):
            _invalider_cache_anniversaires(event)

        cache.invalidate.assert_any_call(pattern="anniversaires")
        cache.invalidate.assert_any_call(pattern="checklists_anniversaire")


@pytest.mark.asyncio
class TestWeekendConversionRoute:
    @patch("src.api.routes.famille.executer_async")
    @patch("src.services.famille.weekend.obtenir_service_weekend")
    async def test_convertir_weekend_en_activite_succes(self, mock_obtenir_service, mock_exec, client):
        mock_exec.side_effect = lambda fn: fn()
        mock_service = MagicMock()
        mock_service.convertir_en_activite_famille.return_value = 42
        mock_obtenir_service.return_value = mock_service

        response = await client.post("/api/v1/famille/weekend/10/convertir-activite")

        assert response.status_code == 200
        data = response.json()
        assert data["succes"] is True
        assert data["weekend_id"] == 10
        assert data["activite_famille_id"] == 42

    @patch("src.api.routes.famille.executer_async")
    @patch("src.services.famille.weekend.obtenir_service_weekend")
    async def test_convertir_weekend_en_activite_introuvable(self, mock_obtenir_service, mock_exec, client):
        mock_exec.side_effect = lambda fn: fn()
        mock_service = MagicMock()
        mock_service.convertir_en_activite_famille.return_value = None
        mock_obtenir_service.return_value = mock_service

        response = await client.post("/api/v1/famille/weekend/999/convertir-activite")

        assert response.status_code == 404
        assert response.json()["detail"] == "Activite weekend introuvable"
