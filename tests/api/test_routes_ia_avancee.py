"""
Tests pour src/api/routes/ia_avancee.py

Couvre les 14 endpoints IA avancée:
- disponibilité des routes
- payloads de base
- validation simple
- upload image (happy path + content-type invalide)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Client FastAPI avec auth/rate-limit bypassés pour tests de route."""
    from src.api.dependencies import require_auth
    from src.api.main import app
    from src.api.rate_limiting import verifier_limite_debit_ia

    async def _mock_auth() -> dict:
        return {"sub": "test-user", "role": "admin"}

    async def _mock_rate() -> dict:
        return {"allowed": True, "remaining": 999}

    app.dependency_overrides[require_auth] = _mock_auth
    app.dependency_overrides[verifier_limite_debit_ia] = _mock_rate

    yield TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides.pop(require_auth, None)
    app.dependency_overrides.pop(verifier_limite_debit_ia, None)


@pytest.fixture
def mock_service() -> MagicMock:
    """Service IA avancée mocké avec réponses minimales valides."""
    svc = MagicMock()

    svc.suggerer_achats.return_value = {
        "suggestions": [
            {
                "nom": "Lait",
                "raison": "Consommé régulièrement",
                "urgence": "normale",
                "frequence_achat_jours": 7,
                "quantite_suggeree": "2",
            }
        ],
        "nb_produits_analyses": 12,
        "periode_analyse_jours": 90,
    }

    svc.generer_planning_adaptatif.return_value = {
        "recommandations": ["Privilégier repas froids"],
        "repas_suggerees": [{"type": "dejeuner", "nom": "Salade"}],
        "activites_suggerees": [{"nom": "Lecture", "interieur": True}],
        "score_adaptation": 78,
        "contexte_utilise": {"meteo": "pluie"},
    }

    svc.diagnostiquer_plante_photo.return_value = {
        "nom_plante": "Monstera",
        "etat_general": "moyen",
        "problemes_detectes": ["feuilles jaunies"],
        "causes_probables": ["sur-arrosage"],
        "traitements_recommandes": ["réduire l'arrosage"],
        "arrosage_conseil": "1 fois/semaine",
        "exposition_conseil": "lumière indirecte",
        "confiance": 0.8,
    }

    svc.prevoir_depenses_fin_mois.return_value = {
        "depenses_actuelles": 600.0,
        "prevision_fin_mois": 1100.0,
        "budget_mensuel": 1200.0,
        "ecart_prevu": 100.0,
        "tendance": "stable",
        "postes_vigilance": [{"poste": "courses", "montant": 400}],
        "conseils_economies": ["éviter achats impulsifs"],
    }

    svc.suggerer_cadeaux.return_value = {
        "idees": [
            {
                "titre": "Puzzle",
                "description": "Puzzle 500 pièces",
                "fourchette_prix": "15-25€",
                "ou_acheter": "librairie",
                "pertinence": "haute",
                "raison": "aime les jeux calmes",
            }
        ],
        "destinataire": "Jules",
        "occasion": "anniversaire",
    }

    svc.analyser_photo_multi_usage.return_value = {
        "contexte_detecte": "document",
        "resume": "Facture détectée",
        "details": {"type": "facture", "montant": 42.5},
        "actions_suggerees": ["Archiver le document"],
        "confiance": 0.9,
    }

    svc.optimiser_routines.return_value = {
        "optimisations": [
            {
                "routine_concernee": "soir",
                "probleme_identifie": "temps écran long",
                "suggestion": "réduire de 20 min",
                "gain_estime": "20 min",
                "priorite": "moyenne",
            }
        ],
        "score_efficacite_actuel": 62,
        "score_efficacite_projete": 77,
    }

    svc.analyser_document_photo.return_value = {
        "type_document": "facture",
        "titre": "Facture EDF",
        "date_document": "2026-03-01",
        "emetteur": "EDF",
        "montant": 85.2,
        "informations_cles": ["Échéance 2026-03-30"],
        "categorie_suggeree": "energie",
        "actions_suggerees": ["Programmer le paiement"],
    }

    svc.estimer_travaux_photo.return_value = {
        "type_travaux": "plomberie",
        "description": "Changement siphon",
        "budget_min": 80.0,
        "budget_max": 180.0,
        "duree_estimee": "2 heures",
        "difficulte": "moyen",
        "diy_possible": True,
        "artisans_recommandes": ["Plombier local"],
        "materiaux_necessaires": [{"nom": "siphon", "quantite": 1}],
    }

    svc.generer_planning_voyage.return_value = {
        "destination": "Lyon",
        "duree_jours": 3,
        "budget_total_estime": 420.0,
        "jours": [
            {
                "jour": 1,
                "date": "2026-07-01",
                "activites": ["Vieux Lyon"],
                "repas_suggerees": ["Bouchon"],
                "budget_jour": 140.0,
                "conseils": ["Réserver à l'avance"],
            }
        ],
        "check_list_depart": ["Cartes d'identité"],
        "conseils_generaux": ["Transport en commun"],
        "adaptations_enfant": ["Pause toutes les 2h"],
    }

    svc.recommander_economies_energie.return_value = {
        "recommandations": [
            {
                "titre": "Baisser chauffage",
                "description": "-1°C la nuit",
                "economie_estimee": "8%",
                "cout_mise_en_oeuvre": "0€",
                "difficulte": "facile",
                "priorite": "haute",
                "categorie": "chauffage",
            }
        ],
        "consommation_actuelle_resume": "stable",
        "potentiel_economie_global": "10-15%",
    }

    svc.predire_pannes.return_value = {
        "predictions": [
            {
                "equipement": "Lave-linge",
                "risque": "moyen",
                "probabilite_pct": 45,
                "delai_estime": "6 mois",
                "signes_alerte": ["bruit anormal"],
                "maintenance_preventive": ["nettoyer filtre"],
                "cout_remplacement_estime": "400-600€",
            }
        ],
        "nb_equipements_analyses": 8,
        "score_sante_global": 74,
    }

    svc.generer_suggestions_proactives.return_value = {
        "suggestions": [
            {
                "module": "cuisine",
                "titre": "Préparer batch cooking",
                "message": "Temps libre dimanche",
                "action_url": "/cuisine/batch-cooking",
                "priorite": "normale",
                "contexte": "calendrier allégé",
            }
        ],
        "date_generation": "2026-03-30",
    }

    svc.adapter_planning_meteo.return_value = {
        "adaptations": [
            {
                "type_adaptation": "activites",
                "condition_meteo": "pluie",
                "recommandation": "activités intérieures",
                "impact": "moyen",
            }
        ],
        "meteo_resume": {"jour": "pluie"},
        "date_prevision": "2026-03-31",
    }

    return svc


class TestRoutesIAAvancee:
    """Tests d'intégration routeur IA avancée."""

    @pytest.mark.parametrize(
        "path,method,payload",
        [
            ("/api/v1/ia-avancee/suggestions-achats", "get", None),
            ("/api/v1/ia-avancee/planning-adaptatif", "post", {"meteo": {"etat": "pluie"}, "budget_restant": 180.0}),
            ("/api/v1/ia-avancee/prevision-depenses", "get", None),
            (
                "/api/v1/ia-avancee/idees-cadeaux",
                "post",
                {"nom": "Jules", "age": 5, "relation": "enfant", "budget_max": 40.0, "occasion": "anniversaire"},
            ),
            ("/api/v1/ia-avancee/optimisation-routines", "get", None),
            ("/api/v1/ia-avancee/planning-voyage", "post", {"destination": "Lyon", "duree_jours": 3, "budget_total": 450.0, "avec_enfant": True}),
            ("/api/v1/ia-avancee/recommandations-energie", "get", None),
            ("/api/v1/ia-avancee/prediction-pannes", "get", None),
            ("/api/v1/ia-avancee/suggestions-proactives", "get", None),
            (
                "/api/v1/ia-avancee/adaptations-meteo",
                "post",
                {"previsions_meteo": {"mardi": "pluie", "mercredi": "soleil"}},
            ),
        ],
    )
    def test_endpoints_json_ok(self, client: TestClient, mock_service: MagicMock, path: str, method: str, payload: dict | None):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get(path) if method == "get" else client.post(path, json=payload)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @pytest.mark.parametrize(
        "path,service_method",
        [
            ("/api/v1/ia-avancee/diagnostic-plante", "diagnostiquer_plante_photo"),
            ("/api/v1/ia-avancee/analyse-photo", "analyser_photo_multi_usage"),
            ("/api/v1/ia-avancee/analyse-document", "analyser_document_photo"),
            ("/api/v1/ia-avancee/estimation-travaux", "estimer_travaux_photo"),
        ],
    )
    def test_endpoints_upload_ok(self, client: TestClient, mock_service: MagicMock, path: str, service_method: str):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            files = {"file": ("image.jpg", b"fake-image-bytes", "image/jpeg")}
            if path.endswith("estimation-travaux"):
                response = client.post(path + "?description=fuite", files=files)
            else:
                response = client.post(path, files=files)

        assert response.status_code == 200
        assert getattr(mock_service, service_method).called

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/ia-avancee/diagnostic-plante",
            "/api/v1/ia-avancee/analyse-photo",
            "/api/v1/ia-avancee/analyse-document",
            "/api/v1/ia-avancee/estimation-travaux",
        ],
    )
    def test_upload_rejects_non_image(self, client: TestClient, mock_service: MagicMock, path: str):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            files = {"file": ("document.txt", b"hello", "text/plain")}
            response = client.post(path, files=files)

        assert response.status_code == 400
        assert "image" in response.text.lower()

    def test_validation_planning_adaptatif_budget_type(self, client: TestClient, mock_service: MagicMock):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.post(
                "/api/v1/ia-avancee/planning-adaptatif",
                json={"meteo": {"etat": "pluie"}, "budget_restant": "abc"},
            )
        assert response.status_code == 422

    def test_validation_idees_cadeaux_age_negative(self, client: TestClient, mock_service: MagicMock):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.post(
                "/api/v1/ia-avancee/idees-cadeaux",
                json={"nom": "Jules", "age": -1, "relation": "enfant", "budget_max": 20.0, "occasion": "anniversaire"},
            )
        assert response.status_code == 422

    def test_validation_suggestions_achats_query_bounds(self, client: TestClient, mock_service: MagicMock):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get("/api/v1/ia-avancee/suggestions-achats?jours=1")
        assert response.status_code == 422

    def test_validation_planning_voyage_duree_bounds(self, client: TestClient, mock_service: MagicMock):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.post(
                "/api/v1/ia-avancee/planning-voyage",
                json={"destination": "Lyon", "duree_jours": 0, "budget_total": 200.0, "avec_enfant": True},
            )
        assert response.status_code == 422

    def test_validation_adaptations_meteo_payload_required(self, client: TestClient, mock_service: MagicMock):
        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.post("/api/v1/ia-avancee/adaptations-meteo", json={})
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "path,method,payload,service_method",
        [
            ("/api/v1/ia-avancee/suggestions-achats", "get", None, "suggerer_achats"),
            (
                "/api/v1/ia-avancee/planning-adaptatif",
                "post",
                {"meteo": {"etat": "pluie"}, "budget_restant": 120.0},
                "generer_planning_adaptatif",
            ),
            ("/api/v1/ia-avancee/prevision-depenses", "get", None, "prevoir_depenses_fin_mois"),
            (
                "/api/v1/ia-avancee/idees-cadeaux",
                "post",
                {"nom": "Lina", "age": 8, "relation": "fille", "budget_max": 35.0, "occasion": "anniversaire"},
                "suggerer_cadeaux",
            ),
            ("/api/v1/ia-avancee/optimisation-routines", "get", None, "optimiser_routines"),
            ("/api/v1/ia-avancee/recommandations-energie", "get", None, "recommander_economies_energie"),
            ("/api/v1/ia-avancee/prediction-pannes", "get", None, "predire_pannes"),
            ("/api/v1/ia-avancee/suggestions-proactives", "get", None, "generer_suggestions_proactives"),
            (
                "/api/v1/ia-avancee/adaptations-meteo",
                "post",
                {"previsions_meteo": {"lundi": "pluie"}},
                "adapter_planning_meteo",
            ),
        ],
    )
    def test_none_fallback_endpoints_json_200(
        self,
        client: TestClient,
        mock_service: MagicMock,
        path: str,
        method: str,
        payload: dict | None,
        service_method: str,
    ):
        getattr(mock_service, service_method).return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get(path) if method == "get" else client.post(path, json=payload)

        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    @pytest.mark.parametrize(
        "path,service_method,with_file,payload",
        [
            ("/api/v1/ia-avancee/diagnostic-plante", "diagnostiquer_plante_photo", True, None),
            ("/api/v1/ia-avancee/analyse-photo", "analyser_photo_multi_usage", True, None),
            ("/api/v1/ia-avancee/analyse-document", "analyser_document_photo", True, None),
            ("/api/v1/ia-avancee/estimation-travaux", "estimer_travaux_photo", True, None),
            (
                "/api/v1/ia-avancee/planning-voyage",
                "generer_planning_voyage",
                False,
                {"destination": "Lyon", "duree_jours": 3, "budget_total": 350.0, "avec_enfant": True},
            ),
        ],
    )
    def test_none_fallback_endpoints_unavailable_503(
        self,
        client: TestClient,
        mock_service: MagicMock,
        path: str,
        service_method: str,
        with_file: bool,
        payload: dict | None,
    ):
        getattr(mock_service, service_method).return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            if with_file:
                files = {"file": ("image.jpg", b"fake-image-bytes", "image/jpeg")}
                if path.endswith("estimation-travaux"):
                    response = client.post(path + "?description=test", files=files)
                else:
                    response = client.post(path, files=files)
            else:
                response = client.post(path, json=payload)

        assert response.status_code == 503

    @pytest.mark.parametrize(
        "path,method,payload,service_method,expected_json",
        [
            (
                "/api/v1/ia-avancee/suggestions-achats",
                "get",
                None,
                "suggerer_achats",
                {
                    "suggestions": [],
                    "nb_produits_analyses": 0,
                    "periode_analyse_jours": 90,
                },
            ),
            (
                "/api/v1/ia-avancee/planning-adaptatif",
                "post",
                {"meteo": {"etat": "pluie"}, "budget_restant": 120.0},
                "generer_planning_adaptatif",
                {
                    "recommandations": [],
                    "repas_suggerees": [],
                    "activites_suggerees": [],
                    "score_adaptation": 0,
                    "contexte_utilise": {},
                },
            ),
            (
                "/api/v1/ia-avancee/prevision-depenses",
                "get",
                None,
                "prevoir_depenses_fin_mois",
                {
                    "depenses_actuelles": 0,
                    "prevision_fin_mois": 0,
                    "budget_mensuel": 0,
                    "ecart_prevu": 0,
                    "tendance": "stable",
                    "postes_vigilance": [],
                    "conseils_economies": [],
                },
            ),
            (
                "/api/v1/ia-avancee/idees-cadeaux",
                "post",
                {"nom": "Lina", "age": 8, "relation": "fille", "budget_max": 35.0, "occasion": "anniversaire"},
                "suggerer_cadeaux",
                {
                    "idees": [],
                    "destinataire": "",
                    "occasion": "anniversaire",
                },
            ),
            (
                "/api/v1/ia-avancee/optimisation-routines",
                "get",
                None,
                "optimiser_routines",
                {
                    "optimisations": [],
                    "score_efficacite_actuel": 0,
                    "score_efficacite_projete": 0,
                },
            ),
            (
                "/api/v1/ia-avancee/recommandations-energie",
                "get",
                None,
                "recommander_economies_energie",
                {
                    "recommandations": [],
                    "consommation_actuelle_resume": None,
                    "potentiel_economie_global": None,
                },
            ),
            (
                "/api/v1/ia-avancee/prediction-pannes",
                "get",
                None,
                "predire_pannes",
                {
                    "predictions": [],
                    "nb_equipements_analyses": 0,
                    "score_sante_global": 0,
                },
            ),
            (
                "/api/v1/ia-avancee/suggestions-proactives",
                "get",
                None,
                "generer_suggestions_proactives",
                {
                    "suggestions": [],
                    "date_generation": None,
                },
            ),
            (
                "/api/v1/ia-avancee/adaptations-meteo",
                "post",
                {"previsions_meteo": {"lundi": "pluie"}},
                "adapter_planning_meteo",
                {
                    "adaptations": [],
                    "meteo_resume": {},
                    "date_prevision": None,
                },
            ),
        ],
    )
    def test_none_fallback_payloads_exact(
        self,
        client: TestClient,
        mock_service: MagicMock,
        path: str,
        method: str,
        payload: dict | None,
        service_method: str,
        expected_json: dict,
    ):
        getattr(mock_service, service_method).return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get(path) if method == "get" else client.post(path, json=payload)

        assert response.status_code == 200
        assert response.json() == expected_json


# ═══════════════════════════════════════════════════════════
# TESTS — PILOTE AUTOMATIQUE
# ═══════════════════════════════════════════════════════════


class TestPiloteAutoRoutes:
    """Tests des endpoints pilote automatique."""

    def test_status(self, client: TestClient, mock_service: MagicMock):
        """GET /pilote-auto/status → 200."""
        mock_service.obtenir_mode_pilote_automatique.return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get("/api/v1/ia-avancee/pilote-auto/status")
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data

    def test_toggle_activation(self, client: TestClient, mock_service: MagicMock):
        """POST /pilote-auto/toggle → 200."""
        with patch(
            "src.services.ia_avancee.pilote_auto.configurer_mode_pilote_automatique",
            return_value=None,
        ):
            with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
                response = client.post(
                    "/api/v1/ia-avancee/pilote-auto/toggle",
                    json={"actif": True},
                )
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data

    def test_actions_recentes(self, client: TestClient, mock_service: MagicMock):
        """GET /pilote-auto/actions-recentes → 200."""
        mock_service.obtenir_mode_pilote_automatique.return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get("/api/v1/ia-avancee/pilote-auto/actions-recentes")
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data

    def test_actions_recentes_limite(self, client: TestClient, mock_service: MagicMock):
        """GET /actions-recentes?limite=5 → paramètre accepté."""
        mock_service.obtenir_mode_pilote_automatique.return_value = None

        with patch("src.api.routes.ia_avancee._get_service", return_value=mock_service):
            response = client.get("/api/v1/ia-avancee/pilote-auto/actions-recentes?limite=5")
        assert response.status_code == 200
