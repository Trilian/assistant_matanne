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
