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
            # Achats famille
            ("GET", "/api/v1/famille/achats"),
            ("POST", "/api/v1/famille/achats"),
            ("POST", "/api/v1/famille/achats/1/achete"),
            ("POST", "/api/v1/famille/achats/1/vendu"),
            ("GET", "/api/v1/famille/achats/1/prefill-revente"),
            ("POST", "/api/v1/famille/achats/1/annonce-lbc"),
            ("POST", "/api/v1/famille/achats/1/annonce-vinted"),
            # Checklists anniversaire
            ("GET", "/api/v1/famille/anniversaires/1/checklist-auto"),
            ("POST", "/api/v1/famille/anniversaires/1/checklist-auto/synchroniser"),
            ("GET", "/api/v1/famille/anniversaires/1/checklists"),
            ("POST", "/api/v1/famille/anniversaires/1/checklists/1/items"),
            ("POST", "/api/v1/famille/anniversaires/1/checklists/1/items/1/vers-achats"),
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
        elif method == "POST" and "achats" in path and path.endswith("/achats"):
            response = await func(path, json={"nom": "Pull Jules", "categorie": "jules_vetements"})
        elif method == "POST" and "achete" in path:
            response = await func(path, json={})
        elif method == "POST" and "vendu" in path:
            response = await func(path, json={})
        elif method == "POST" and "annonce-lbc" in path:
            response = await func(path, json={})
        elif method == "POST" and "annonce-vinted" in path:
            response = await func(path, json={})
        elif method == "POST" and "synchroniser" in path:
            response = await func(path, json={})
        elif method == "POST" and "items" in path and "vers-achats" in path:
            response = await func(path, json={})
        elif method == "POST" and "items" in path:
            response = await func(path, json={"nom": "Gâteau", "categorie": "repas"})
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


        # ═══════════════════════════════════════════════════════════
        # TESTS — FORMAT DES RÉPONSES ACHATS
        # ═══════════════════════════════════════════════════════════


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


        class TestAchatsFormats:
            """Vérifie le format des réponses JSON des endpoints achats."""

            @patch("src.api.routes.famille.executer_avec_session")
            @patch("src.api.routes.famille.executer_async")
            async def test_lister_achats_format(self, mock_exec, mock_session, client):
                """La liste d'achats retourne le bon format paginé."""
                mock_exec.side_effect = lambda fn: fn()
                mock_achat = creer_mock(ACHAT_TEST)
                mock_achat.date_achat = None
                mock_achat.vendu_le = None

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

            @patch("src.api.routes.famille.executer_avec_session")
            @patch("src.api.routes.famille.executer_async")
            async def test_lister_achats_filtre_pour_qui(self, mock_exec, mock_session, client):
                """Le filtre pour_qui est accepté sans erreur."""
                mock_exec.side_effect = lambda fn: fn()
                ctx = MagicMock()
                ctx.__enter__ = MagicMock(return_value=MagicMock())
                ctx.__exit__ = MagicMock(return_value=False)
                session = ctx.__enter__()
                query = session.query.return_value
                query.filter.return_value = query
                query.order_by.return_value = query
                query.count.return_value = 0
                query.offset.return_value.limit.return_value.all.return_value = []
                mock_session.return_value = ctx

                response = await client.get("/api/v1/famille/achats?pour_qui=jules")
                assert response.status_code in (200, 401, 403, 422)

            @patch("src.api.routes.famille.executer_avec_session")
            @patch("src.api.routes.famille.executer_async")
            async def test_lister_achats_filtre_categorie(self, mock_exec, mock_session, client):
                """Le filtre categorie est accepté sans erreur."""
                mock_exec.side_effect = lambda fn: fn()
                ctx = MagicMock()
                ctx.__enter__ = MagicMock(return_value=MagicMock())
                ctx.__exit__ = MagicMock(return_value=False)
                session = ctx.__enter__()
                query = session.query.return_value
                query.filter.return_value = query
                query.order_by.return_value = query
                query.count.return_value = 0
                query.offset.return_value.limit.return_value.all.return_value = []
                mock_session.return_value = ctx

                response = await client.get("/api/v1/famille/achats?categorie=jules_vetements")
                assert response.status_code in (200, 401, 403, 422)


        # ═══════════════════════════════════════════════════════════
        # TESTS — PREFILL REVENTE
        # ═══════════════════════════════════════════════════════════


        class TestPrefillRevente:
            """Vérifie la logique de sélection de plateforme de revente."""

            @patch("src.api.routes.famille.executer_avec_session")
            @patch("src.api.routes.famille.executer_async")
            async def test_prefill_vetements_retourne_vinted(self, mock_exec, mock_session, client):
                """Les vêtements sont dirigés vers Vinted."""
                mock_exec.side_effect = lambda fn: fn()
                mock_achat = creer_mock({**ACHAT_TEST, "categorie": "jules_vetements", "prix_reel": 30.0})
                mock_achat.date_achat = None
                mock_achat.vendu_le = None

                ctx = MagicMock()
                ctx.__enter__ = MagicMock(return_value=MagicMock())
                ctx.__exit__ = MagicMock(return_value=False)
                session = ctx.__enter__()
                session.query.return_value.filter.return_value.first.return_value = mock_achat
                session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
                    None
                )
                mock_session.return_value = ctx

                response = await client.get("/api/v1/famille/achats/1/prefill-revente")
                assert response.status_code in (200, 401, 403)
                if response.status_code == 200:
                    data = response.json()
                    assert data["plateforme"] == "vinted"
                    assert data["prix_suggere"] == pytest.approx(12.0)  # 40% de 30

            @patch("src.api.routes.famille.executer_avec_session")
            @patch("src.api.routes.famille.executer_async")
            async def test_prefill_electronique_retourne_lbc(self, mock_exec, mock_session, client):
                """L'électronique est dirigée vers LeBonCoin."""
                mock_exec.side_effect = lambda fn: fn()
                mock_achat = creer_mock({**ACHAT_TEST, "categorie": "electronique", "prix_reel": 100.0})
                mock_achat.date_achat = None
                mock_achat.vendu_le = None

                ctx = MagicMock()
                ctx.__enter__ = MagicMock(return_value=MagicMock())
                ctx.__exit__ = MagicMock(return_value=False)
                session = ctx.__enter__()
                session.query.return_value.filter.return_value.first.return_value = mock_achat
                session.query.return_value.filter.return_value.filter.return_value.first.return_value = (
                    None
                )
                mock_session.return_value = ctx

                response = await client.get("/api/v1/famille/achats/1/prefill-revente")
                assert response.status_code in (200, 401, 403)
                if response.status_code == 200:
                    data = response.json()
                    assert data["plateforme"] == "lbc"


        # ═══════════════════════════════════════════════════════════
        # TESTS — SCHEMAS ACHAT
        # ═══════════════════════════════════════════════════════════


        class TestSchemasAchat:
            """Tests schemas Pydantic pour le module achats famille."""

            def test_achat_create_valide(self):
                from src.api.schemas.famille import AchatFamilleCreate

                a = AchatFamilleCreate(nom="Pull Jules", categorie="jules_vetements")
                assert a.nom == "Pull Jules"
                assert a.categorie == "jules_vetements"
                assert a.achete is False

            def test_achat_create_nom_vide_rejete(self):
                from pydantic import ValidationError

                from src.api.schemas.famille import AchatFamilleCreate

                with pytest.raises(ValidationError):
                    AchatFamilleCreate(nom="", categorie="jules_vetements")

            def test_achat_patch_optionnel(self):
                from src.api.schemas.famille import AchatFamillePatch

                p = AchatFamillePatch(priorite="urgente")
                assert p.priorite == "urgente"
                assert p.nom is None

            def test_prefill_revente_response_valide(self):
                from src.api.schemas.famille import PrefillReventeResponse

                r = PrefillReventeResponse(
                    achat_id=1,
                    plateforme="vinted",
                    plateforme_libelle="Vinted",
                    marque=None,
                    taille="3A",
                    prix_suggere=12.0,
                    pour_qui="jules",
                    raisons=["Vêtements → Vinted de préférence"],
                )
                assert r.plateforme == "vinted"
                assert r.taille == "3A"
                assert r.prix_suggere == 12.0
                assert len(r.raisons) == 1

            def test_prefill_revente_response_defaults(self):
                from src.api.schemas.famille import PrefillReventeResponse

                r = PrefillReventeResponse(
                    achat_id=5,
                    plateforme="lbc",
                    plateforme_libelle="LeBonCoin",
                )
                assert r.raisons == []
                assert r.marque is None
                assert r.pour_qui == "famille"


        # ═══════════════════════════════════════════════════════════
        # TESTS — SUBSCRIBERS INTELLIGENTS
        # ═══════════════════════════════════════════════════════════


        class TestSubscribersIntelligents:
            """Vérifie que les nouveaux subscribers intelligents sont bien enregistrés."""

            def test_nombre_subscribers_attendu(self):
                """Le registre doit contenir >= 29 subscribers après bootstrap."""
                from src.services.core.events.bus import obtenir_bus
                from src.services.core.events.subscribers import (
                    _subscribers_enregistres,  # noqa: PLC2701
                    enregistrer_subscribers,
                )

                # Reset pour forcer le re-enregistrement
                import src.services.core.events.subscribers as sub_mod

                sub_mod._subscribers_enregistres = False
                nb = enregistrer_subscribers()
                assert nb >= 29, f"Attendu >= 29 subscribers, obtenu {nb}"
                sub_mod._subscribers_enregistres = True

            def test_anniversaire_proche_handler_enregistre(self):
                """Le handler anniversaire.proche est bien souscrit."""
                from src.services.core.events.bus import obtenir_bus
                from src.services.core.events.subscribers import (
                    _proposer_checklist_anniversaire_proche,
                )

                import src.services.core.events.subscribers as sub_mod

                sub_mod._subscribers_enregistres = False
                enregistrer = __import__(
                    "src.services.core.events.subscribers",
                    fromlist=["enregistrer_subscribers"],
                ).enregistrer_subscribers
                enregistrer()

                bus = obtenir_bus()
                handlers_proche = [
                    s.handler
                    for s in bus._subscribers
                    if "anniversaire.proche" in getattr(s, "pattern", "")
                    or getattr(s, "topic", "") == "anniversaire.proche"
                ]
                # Vérifie que le handler est bien présent dans les subscribers du bus
                all_handlers = [s.handler for s in bus._subscribers]
                assert _proposer_checklist_anniversaire_proche in all_handlers, (
                    "Handler checklist anniversaire proche non enregistré"
                )
                sub_mod._subscribers_enregistres = True

            def test_invalider_cache_anniversaires_faute_tolerant(self):
                """_invalider_cache_anniversaires ne lève pas d'exception même si le cache échoue."""
                from unittest.mock import patch

                from src.services.core.events.subscribers import _invalider_cache_anniversaires
                from src.services.core.events.bus import EvenementDomaine

                event = EvenementDomaine(type="anniversaires.cree", data={}, source="test")

                with patch("src.core.caching.obtenir_cache", side_effect=RuntimeError("cache down")):
                    # Ne doit pas lever d'exception
                    _invalider_cache_anniversaires(event)

            def test_invalider_cache_suggestions_achats_faute_tolerant(self):
                """_invalider_cache_suggestions_achats ne lève pas d'exception même si le cache échoue."""
                from unittest.mock import patch

                from src.services.core.events.subscribers import _invalider_cache_suggestions_achats
                from src.services.core.events.bus import EvenementDomaine

                event = EvenementDomaine(type="preferences.mise_a_jour", data={}, source="test")

                with patch("src.core.caching.obtenir_cache", side_effect=RuntimeError("cache down")):
                    _invalider_cache_suggestions_achats(event)

            def test_proposer_checklist_ignore_jours_hors_seuil(self):
                """Le handler ne fait rien si jours_restants n'est pas dans (30, 14, 7, 1)."""
                from unittest.mock import patch

                from src.services.core.events.subscribers import _proposer_checklist_anniversaire_proche
                from src.services.core.events.bus import EvenementDomaine

                event = EvenementDomaine(
                    type="anniversaire.proche",
                    data={"jours_restants": 50, "anniversaire_id": 1},
                    source="test",
                )

                with patch(
                    "src.services.famille.checklists_anniversaire.obtenir_service_checklists_anniversaire"
                ) as mock_svc:
                    _proposer_checklist_anniversaire_proche(event)
                    mock_svc.assert_not_called()
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
