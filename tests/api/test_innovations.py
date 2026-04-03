"""
Tests API pour les fonctionnalitÃ©s avancÃ©es.

Couvre les 8 endpoints du routeur innovations + admin reset + WebSocket logs.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Fixtures
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_innovations_service():
    """Mock du service InnovationsService."""
    with patch("src.api.routes.fonctionnalites_avancees._get_service") as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def auth_headers():
    """Headers d'authentification mock."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def admin_headers():
    """Headers d'authentification admin avec JWT valide."""
    from src.api.auth import creer_token_acces

    token = creer_token_acces(
        user_id="admin-1",
        email="admin@test.local",
        role="admin",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(app):
    """Client sync local pour tests endpoints sync/legacy."""
    with TestClient(app) as c:
        yield c


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.4 â€” BILAN ANNUEL
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBilanAnnuel:
    """Tests pour POST /api/v1/innovations/bilan-annuel."""

    def test_bilan_annuel_retourne_sections(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import BilanAnnuelResponse, SectionBilanAnnuel

        mock_innovations_service.generer_bilan_annuel.return_value = BilanAnnuelResponse(
            annee=2025,
            resume_global="Bonne annÃ©e familiale",
            sections=[SectionBilanAnnuel(titre="Cuisine", resume="150 recettes")],
            score_global=7.5,
            recommandations=["Planifier plus de repas"],
        )

        response = client.post(
            "/api/v1/innovations/bilan-annuel",
            json={"annee": 2025},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["annee"] == 2025
        assert len(data["sections"]) == 1

    def test_bilan_annuel_sans_annee(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import BilanAnnuelResponse

        mock_innovations_service.generer_bilan_annuel.return_value = BilanAnnuelResponse()

        response = client.post(
            "/api/v1/innovations/bilan-annuel",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_bilan_annuel_service_none(self, client, auth_headers, mock_innovations_service):
        mock_innovations_service.generer_bilan_annuel.return_value = None

        response = client.post(
            "/api/v1/innovations/bilan-annuel",
            json={"annee": 2024},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["annee"] == 0  # Default BilanAnnuelResponse


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.5 â€” SCORE BIEN-ÃŠTRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestScoreBienEtre:
    """Tests pour GET /api/v1/innovations/score-bien-etre."""

    def test_score_bien_etre_composite(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import DimensionBienEtre, ScoreBienEtreResponse

        mock_innovations_service.calculer_score_bien_etre.return_value = ScoreBienEtreResponse(
            score_global=72.5,
            niveau="bon",
            dimensions=[
                DimensionBienEtre(nom="Sport", score=80, poids=0.30),
                DimensionBienEtre(nom="Nutrition", score=65, poids=0.25),
            ],
            conseils=["Continuez le sport !"],
        )

        response = client.get("/api/v1/innovations/score-bien-etre", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["score_global"] == 72.5
        assert data["niveau"] == "bon"
        assert len(data["dimensions"]) == 2

    def test_score_bien_etre_service_none(self, client, auth_headers, mock_innovations_service):
        mock_innovations_service.calculer_score_bien_etre.return_value = None

        response = client.get("/api/v1/innovations/score-bien-etre", headers=auth_headers)
        assert response.status_code == 200


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.17 â€” ENRICHISSEMENT CONTACTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestEnrichissementContacts:
    """Tests pour GET /api/v1/innovations/enrichissement-contacts."""

    def test_enrichissement_contacts(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ContactEnrichi, EnrichissementContactsResponse

        mock_innovations_service.enrichir_contacts.return_value = EnrichissementContactsResponse(
            contacts_enrichis=[
                ContactEnrichi(
                    contact_id=1,
                    nom="Marie Dupont",
                    categorie_suggeree="Famille",
                    rappel_relationnel="Ã€ contacter",
                )
            ],
            nb_contacts_analyses=10,
            nb_contacts_sans_nouvelles=3,
        )

        response = client.get(
            "/api/v1/innovations/enrichissement-contacts", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_contacts_analyses"] == 10


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.18 â€” TENDANCES LOTO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTendancesLoto:
    """Tests pour GET /api/v1/innovations/tendances-loto."""

    def test_tendances_loto(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import AnalyseTendancesLotoResponse, TendanceLoto

        mock_innovations_service.analyser_tendances_loto.return_value = AnalyseTendancesLotoResponse(
            jeu="loto",
            nb_tirages_analyses=100,
            numeros_chauds=[TendanceLoto(numero=7, frequence=0.15, score_tendance=0.85)],
            combinaison_suggeree=[7, 12, 23, 31, 42],
            analyse_ia="Le numÃ©ro 7 est le plus frÃ©quent.",
        )

        response = client.get(
            "/api/v1/innovations/tendances-loto?jeu=loto", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jeu"] == "loto"
        assert len(data["numeros_chauds"]) == 1

    def test_tendances_euromillions(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import AnalyseTendancesLotoResponse

        mock_innovations_service.analyser_tendances_loto.return_value = AnalyseTendancesLotoResponse(
            jeu="euromillions"
        )

        response = client.get(
            "/api/v1/innovations/tendances-loto?jeu=euromillions", headers=auth_headers
        )
        assert response.status_code == 200


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.19 â€” PARCOURS MAGASIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestParcoursMagasin:
    """Tests pour POST /api/v1/innovations/parcours-magasin."""

    def test_parcours_magasin_optimise(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ParcoursOptimiseResponse

        mock_innovations_service.optimiser_parcours_magasin.return_value = ParcoursOptimiseResponse(
            articles_par_rayon={"Fruits": ["pommes", "bananes"], "Laitiers": ["lait"]},
            ordre_rayons=["Fruits", "Laitiers"],
            nb_articles=3,
            temps_estime_minutes=15,
        )

        response = client.post(
            "/api/v1/innovations/parcours-magasin",
            json={"liste_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_articles"] == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.8 â€” VEILLE EMPLOI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestVeilleEmploi:
    """Tests pour POST /api/v1/innovations/veille-emploi."""

    def test_veille_emploi_avec_criteres(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import OffreEmploi, VeilleEmploiResponse

        mock_innovations_service.executer_veille_emploi.return_value = VeilleEmploiResponse(
            offres=[
                OffreEmploi(
                    titre="RH Manager",
                    entreprise="Acme",
                    localisation="Lyon",
                    type_contrat="CDI",
                    mode_travail="hybride",
                    score_pertinence=0.9,
                )
            ],
            nb_offres_trouvees=1,
        )

        response = client.post(
            "/api/v1/innovations/veille-emploi",
            json={
                "domaine": "RH",
                "mots_cles": ["RH"],
                "type_contrat": ["CDI"],
                "mode_travail": ["hybride"],
                "rayon_km": 30,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_offres_trouvees"] == 1
        assert data["offres"][0]["titre"] == "RH Manager"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.3 â€” MODE INVITÃ‰
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestModeInvite:
    """Tests pour le mode invitÃ©."""

    def test_creer_lien_invite(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import LienInviteResponse

        mock_innovations_service.creer_lien_invite.return_value = LienInviteResponse(
            token="abc123",
            url="/invite/abc123",
            expire_dans_heures=48,
            modules_autorises=["repas", "routines"],
            nom_invite="Mamie FranÃ§oise",
        )

        response = client.post(
            "/api/v1/innovations/invite/creer",
            json={"nom_invite": "Mamie FranÃ§oise", "modules": ["repas", "routines"]},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "abc123"
        assert "repas" in data["modules_autorises"]

    def test_creer_lien_invite_module_invalide(self, client, auth_headers, mock_innovations_service):
        response = client.post(
            "/api/v1/innovations/invite/creer",
            json={"nom_invite": "Test", "modules": ["admin", "secret"]},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_acceder_invite_token_valide(self, client, mock_innovations_service):
        from src.services.innovations.types import DonneesInviteResponse

        mock_innovations_service.obtenir_donnees_invite.return_value = DonneesInviteResponse(
            enfant={"prenom": "Jules"},
            routines=[{"nom": "Routine du soir"}],
            repas_semaine=[{"date": "2026-03-30", "type": "dÃ©jeuner", "recette": "PÃ¢tes"}],
            contacts_urgence=[{"nom": "Dr. Martin", "telephone": "0601020304"}],
            notes="AccÃ¨s invitÃ©",
        )

        response = client.get("/api/v1/innovations/invite/abc123")
        assert response.status_code == 200
        data = response.json()
        assert data["enfant"]["prenom"] == "Jules"

    def test_acceder_invite_token_expire(self, client, mock_innovations_service):
        mock_innovations_service.obtenir_donnees_invite.return_value = None

        response = client.get("/api/v1/innovations/invite/expired-token")
        assert response.status_code == 404


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Innovations prioritaires â€” Innovations prioritaires
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestVacationModeInnovations:
    """Tests des endpoints Innovations prioritaires (mode vacances, insights, mÃ©tÃ©o contextuelle)."""

    def test_lire_mode_vacances(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ModeVacancesResponse

        mock_innovations_service.obtenir_mode_vacances.return_value = ModeVacancesResponse(
            actif=True,
            checklist_voyage_auto=True,
            courses_mode_compact=True,
            entretien_suspendu=True,
            recommandations=["Checklist voyage prÃªte"],
        )

        response = client.get("/api/v1/innovations/phasee/mode-vacances", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is True
        assert data["entretien_suspendu"] is True

    def test_configurer_mode_vacances(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ModeVacancesResponse

        mock_innovations_service.configurer_mode_vacances.return_value = ModeVacancesResponse(
            actif=False,
            checklist_voyage_auto=False,
            courses_mode_compact=False,
            entretien_suspendu=False,
            recommandations=["Mode vacances dÃ©sactivÃ©"],
        )

        response = client.post(
            "/api/v1/innovations/phasee/mode-vacances/config",
            json={"actif": False, "checklist_voyage_auto": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is False
        assert data["checklist_voyage_auto"] is False

    def test_insights_quotidiens_limites_a_deux(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import InsightQuotidien, InsightsQuotidiensResponse

        mock_innovations_service.generer_insights_quotidiens.return_value = InsightsQuotidiensResponse(
            date_reference="2026-04-02",
            limite_journaliere=2,
            nb_insights=2,
            insights=[
                InsightQuotidien(titre="Insight 1", message="A", module="cuisine"),
                InsightQuotidien(titre="Insight 2", message="B", module="maison"),
            ],
        )

        response = client.get(
            "/api/v1/innovations/phasee/insights-quotidiens?limite=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limite_journaliere"] == 2
        assert data["nb_insights"] <= 2

    def test_meteo_contextuelle_cross_module(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import MeteoContextuelleResponse, MeteoImpactModule

        mock_innovations_service.analyser_meteo_contextuelle.return_value = MeteoContextuelleResponse(
            ville="Paris",
            saison="printemps",
            temperature=18.5,
            description="Partiellement nuageux",
            modules=[
                MeteoImpactModule(module="cuisine", impact="Adapter les menus"),
                MeteoImpactModule(module="famille", impact="ActivitÃ©s int/ext"),
            ],
        )

        response = client.get("/api/v1/innovations/phasee/meteo-contextuelle", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ville"] == "Paris"
        assert len(data["modules"]) >= 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Innovations avancées â€” Innovations avancÃ©es
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLearningPreferencesInnovations:
    """Tests des endpoints Innovations avancées (prÃ©fÃ©rences, planification auto, batch IA, cartes, tablette)."""

    def test_preferences_apprises(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ApprentissagePreferencesResponse, PreferenceApprise

        mock_innovations_service.analyser_preferences_apprises.return_value = ApprentissagePreferencesResponse(
            semaines_analysees=3,
            influence_active=True,
            preferences_favorites=[
                PreferenceApprise(categorie="categorie_recette", valeur="poisson", score_confiance=0.82)
            ],
            ajustements_suggestions=["Prioriser les recettes poisson"],
        )

        response = client.get("/api/v1/innovations/phasee/s22/preferences-apprises", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["semaines_analysees"] >= 2
        assert data["influence_active"] is True

    def test_planification_hebdo_complete_auto(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import BlocPlanificationAuto, PlanificationHebdoCompleteResponse

        mock_innovations_service.generer_planification_hebdo_complete.return_value = PlanificationHebdoCompleteResponse(
            semaine_reference="2026-04-06",
            genere_en_un_clic=True,
            blocs=[
                BlocPlanificationAuto(titre="Repas semaine", items=["Saumon + legumes"]),
                BlocPlanificationAuto(titre="Liste de courses", items=["saumon", "courgettes"]),
            ],
            resume="Planning complet genere automatiquement",
        )

        response = client.get("/api/v1/innovations/phasee/s22/planification-auto", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["genere_en_un_clic"] is True
        assert len(data["blocs"]) >= 2

    def test_batch_cooking_intelligent(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import BatchCookingIntelligentResponse, EtapeBatchIntelligente

        mock_innovations_service.proposer_batch_cooking_intelligent.return_value = BatchCookingIntelligentResponse(
            session_nom="Batch intelligent 06/04",
            date_session="2026-04-05",
            recettes_cibles=["Curry doux", "Compote"],
            duree_estimee_totale_minutes=90,
            etapes=[EtapeBatchIntelligente(ordre=1, action="Preparer curry", duree_minutes=45)],
            conseils=["Paralleliser les cuissons"],
        )

        response = client.get("/api/v1/innovations/phasee/s22/batch-cooking-intelligent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["duree_estimee_totale_minutes"] > 0
        assert len(data["etapes"]) >= 1

    def test_generer_carte_visuelle(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import CarteVisuellePartageableResponse

        mock_innovations_service.generer_carte_visuelle_partageable.return_value = CarteVisuellePartageableResponse(
            type_carte="planning",
            format_image="image/svg+xml",
            filename="carte-planning.svg",
            contenu_base64="PHN2Zz48L3N2Zz4=",
            metadata={"theme": "magazine-familial"},
        )

        response = client.post(
            "/api/v1/innovations/phasee/s22/carte-visuelle",
            json={"type_carte": "planning", "titre": "Semaine famille"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["format_image"] == "image/svg+xml"
        assert len(data["contenu_base64"]) > 0

    def test_mode_tablette_magazine(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import CarteMagazineTablette, ModeTabletteMagazineResponse

        mock_innovations_service.obtenir_mode_tablette_magazine.return_value = ModeTabletteMagazineResponse(
            titre="Edition tablette",
            sous_titre="Vue magazine",
            cartes=[CarteMagazineTablette(titre="Score", valeur="78/100", action_url="/")],
        )

        response = client.get("/api/v1/innovations/phasee/s22/mode-tablette-magazine", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["titre"] == "Edition tablette"
        assert len(data["cartes"]) >= 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Innovations long terme â€” Innovations long terme
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTelegramEnergyInnovations:
    """Tests des endpoints Innovations long terme (Telegram conversationnel, prix auto, Ã©nergie temps-rÃ©el)."""

    def test_telegram_conversationnel(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import CommandeTelegram, TelegramConversationnelResponse

        mock_innovations_service.obtenir_capacites_telegram_conversationnelles.return_value = TelegramConversationnelResponse(
            actif=True,
            nb_commandes=6,
            commandes=[
                CommandeTelegram(commande="menu", action="Planning"),
                CommandeTelegram(commande="courses", action="Courses"),
            ],
        )

        response = client.get(
            "/api/v1/innovations/phasee/s23/telegram-conversationnel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is True
        assert data["nb_commandes"] >= 5

    def test_comparateur_prix_auto(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import ComparateurPrixAutomatiqueResponse, PrixIngredientCompare

        mock_innovations_service.analyser_comparateur_prix_automatique.return_value = ComparateurPrixAutomatiqueResponse(
            date_reference="2026-04-02",
            nb_ingredients_analyses=20,
            ingredients=[
                PrixIngredientCompare(
                    ingredient="tomate",
                    frequence_utilisation=12,
                    prix_historique_moyen_eur=2.5,
                    prix_marche_eur=2.0,
                    source_prix="openfoodfacts",
                    variation_pct=-20.0,
                    alerte_soldes=True,
                )
            ],
            nb_alertes=1,
            alertes=["tomate: baisse dÃ©tectÃ©e (20.0% vs historique)"],
        )

        response = client.get(
            "/api/v1/innovations/phasee/s23/comparateur-prix-auto?top_n=20",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_ingredients_analyses"] == 20
        assert data["nb_alertes"] >= 1

    def test_energie_temps_reel(self, client, auth_headers, mock_innovations_service):
        from src.services.innovations.types import EnergieTempsReelResponse

        mock_innovations_service.obtenir_tableau_bord_energie_temps_reel.return_value = EnergieTempsReelResponse(
            linky_connecte=True,
            source="linky",
            horodatage="2026-04-02T10:15:00Z",
            puissance_instantanee_w=3200.0,
            consommation_jour_estimee_kwh=11.5,
            consommation_mois_kwh=138.0,
            tendance="stable",
            alertes=[],
        )

        response = client.get(
            "/api/v1/innovations/phasee/s23/energie-temps-reel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in {"linky", "estimation_releves"}
        assert data["consommation_mois_kwh"] is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 10.25 â€” ADMIN RESET MODULE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAdminResetModule:
    """Tests pour POST /api/v1/admin/reset-module."""

    def test_reset_module_preview(self, client, admin_headers):
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = type("Params", (), {"ENV": "test"})()
            response = client.post(
                "/api/v1/admin/reset-module",
                json={"module": "courses", "confirmer": False},
                headers=admin_headers,
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "preview"
        assert "listes_courses" in data["tables_affectees"]

    def test_reset_module_invalide(self, client, admin_headers):
        with patch("src.core.config.obtenir_parametres") as mock_params:
            mock_params.return_value = type("Params", (), {"ENV": "test"})()
            response = client.post(
                "/api/v1/admin/reset-module",
                json={"module": "module_inexistant", "confirmer": True},
                headers=admin_headers,
            )
        assert response.status_code == 400


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests unitaires service InnovationsService
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestInnovationsServiceUnit:
    """Tests unitaires pour InnovationsService."""

    def test_evaluer_niveau_excellent(self):
        from src.services.innovations.service import InnovationsService

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            assert service._evaluer_niveau(85) == "excellent"

    def test_evaluer_niveau_attention(self):
        from src.services.innovations.service import InnovationsService

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            assert service._evaluer_niveau(30) == "attention"

    def test_generer_conseils_score_faible(self):
        from src.services.innovations.service import InnovationsService
        from src.services.innovations.types import DimensionBienEtre

        with patch.object(InnovationsService, "__init__", lambda x: None):
            service = InnovationsService()
            dimensions = [
                DimensionBienEtre(nom="Sport", score=30, detail="ActivitÃ© insuffisante"),
                DimensionBienEtre(nom="Nutrition", score=90, detail="Excellent"),
            ]
            conseils = service._generer_conseils(dimensions)
            assert len(conseils) >= 1
            assert "sport" in conseils[0].lower()
