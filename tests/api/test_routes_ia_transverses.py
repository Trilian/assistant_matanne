"""
Tests API pour les routes IA transverses stabilisées par domaine métier.

Couvre les endpoints `recettes`, `famille`, `dashboard`, `rapports`, `courses`,
`planning`, `habitat` et `jeux` qui délèguent au service `src.services.ia_avancee`.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# Fixtures


@pytest.fixture
def mock_innovations_service():
    """Mock du service InnovationsService via la factory actuelle."""
    with patch("src.services.ia_avancee.get_innovations_service") as mock:
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
    """Client sync local pour les routes IA transverses stabilisées."""
    with TestClient(app) as c:
        yield c


# Bilan annuel


class TestBilanAnnuel:
    """Tests pour POST /api/v1/rapports/bilan-annuel."""

    def test_bilan_annuel_retourne_sections(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import BilanAnnuelResponse, SectionBilanAnnuel

        mock_innovations_service.generer_bilan_annuel.return_value = BilanAnnuelResponse(
            annee=2025,
            resume_global="Bonne année familiale",
            sections=[SectionBilanAnnuel(titre="Cuisine", resume="150 recettes")],
            score_global=7.5,
            recommandations=["Planifier plus de repas"],
        )

        response = client.post(
            "/api/v1/rapports/bilan-annuel",
            json={"annee": 2025},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["annee"] == 2025
        assert len(data["sections"]) == 1

    def test_bilan_annuel_sans_annee(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import BilanAnnuelResponse

        mock_innovations_service.generer_bilan_annuel.return_value = BilanAnnuelResponse()

        response = client.post(
            "/api/v1/rapports/bilan-annuel",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 200

    def test_bilan_annuel_service_none(self, client, auth_headers, mock_innovations_service):
        mock_innovations_service.generer_bilan_annuel.return_value = None

        response = client.post(
            "/api/v1/rapports/bilan-annuel",
            json={"annee": 2024},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["annee"] == 0  # Default BilanAnnuelResponse


# Score bien-être


class TestScoreBienEtre:
    """Tests pour GET /api/v1/rapports/score-bien-etre."""

    def test_score_bien_etre_composite(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import DimensionBienEtre, ScoreBienEtreResponse

        mock_innovations_service.calculer_score_bien_etre.return_value = ScoreBienEtreResponse(
            score_global=72.5,
            niveau="bon",
            dimensions=[
                DimensionBienEtre(nom="Sport", score=80, poids=0.30),
                DimensionBienEtre(nom="Nutrition", score=65, poids=0.25),
            ],
            conseils=["Continuez le sport !"],
        )

        response = client.get("/api/v1/rapports/score-bien-etre", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["score_global"] == 72.5
        assert data["niveau"] == "bon"
        assert len(data["dimensions"]) == 2

    def test_score_bien_etre_service_none(self, client, auth_headers, mock_innovations_service):
        mock_innovations_service.calculer_score_bien_etre.return_value = None

        response = client.get("/api/v1/rapports/score-bien-etre", headers=auth_headers)
        assert response.status_code == 200


# Enrichissement contacts


class TestEnrichissementContacts:
    """Tests pour GET /api/v1/famille/enrichissement-contacts."""

    def test_enrichissement_contacts(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ContactEnrichi, EnrichissementContactsResponse

        mock_innovations_service.enrichir_contacts.return_value = EnrichissementContactsResponse(
            contacts_enrichis=[
                ContactEnrichi(
                    contact_id=1,
                    nom="Marie Dupont",
                    categorie_suggeree="Famille",
                    rappel_relationnel="À contacter",
                )
            ],
            nb_contacts_analyses=10,
            nb_contacts_sans_nouvelles=3,
        )

        response = client.get(
            "/api/v1/famille/enrichissement-contacts", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_contacts_analyses"] == 10


# Tendances Loto et EuroMillions


class TestTendancesLoto:
    """Tests pour GET /api/v1/jeux/tendances-loto."""

    def test_tendances_loto(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import AnalyseTendancesLotoResponse, TendanceLoto

        mock_innovations_service.analyser_tendances_loto.return_value = AnalyseTendancesLotoResponse(
            jeu="loto",
            nb_tirages_analyses=100,
            numeros_chauds=[TendanceLoto(numero=7, frequence=0.15, score_tendance=0.85)],
            combinaison_suggeree=[7, 12, 23, 31, 42],
            analyse_ia="Le numéro 7 est le plus fréquent.",
        )

        response = client.get(
            "/api/v1/jeux/tendances-loto?jeu=loto", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["jeu"] == "loto"
        assert len(data["numeros_chauds"]) == 1

    def test_tendances_euromillions(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import AnalyseTendancesLotoResponse

        mock_innovations_service.analyser_tendances_loto.return_value = AnalyseTendancesLotoResponse(
            jeu="euromillions"
        )

        response = client.get(
            "/api/v1/jeux/tendances-loto?jeu=euromillions", headers=auth_headers
        )
        assert response.status_code == 200


# Parcours magasin


class TestParcoursMagasin:
    """Tests pour POST /api/v1/courses/parcours-magasin."""

    def test_parcours_magasin_optimise(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ParcoursOptimiseResponse

        mock_innovations_service.optimiser_parcours_magasin.return_value = ParcoursOptimiseResponse(
            articles_par_rayon={"Fruits": ["pommes", "bananes"], "Laitiers": ["lait"]},
            ordre_rayons=["Fruits", "Laitiers"],
            nb_articles=3,
            temps_estime_minutes=15,
        )

        response = client.post(
            "/api/v1/courses/parcours-magasin",
            json={"liste_id": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_articles"] == 3


# Veille emploi


class TestVeilleEmploi:
    """Tests pour POST /api/v1/famille/veille-emploi."""

    def test_veille_emploi_avec_criteres(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import OffreEmploi, VeilleEmploiResponse

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
            "/api/v1/famille/veille-emploi",
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


# Mode invité


class TestModeInvite:
    """Tests pour le mode invité."""

    def test_creer_lien_invite(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import LienInviteResponse

        mock_innovations_service.creer_lien_invite.return_value = LienInviteResponse(
            token="abc123",
            url="/invite/abc123",
            expire_dans_heures=48,
            modules_autorises=["repas", "routines"],
            nom_invite="Mamie Françoise",
        )

        response = client.post(
            "/api/v1/rapports/invite/creer",
            json={"nom_invite": "Mamie Françoise", "modules": ["repas", "routines"]},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "abc123"
        assert "repas" in data["modules_autorises"]

    def test_creer_lien_invite_module_invalide(self, client, auth_headers, mock_innovations_service):
        response = client.post(
            "/api/v1/rapports/invite/creer",
            json={"nom_invite": "Test", "modules": ["admin", "secret"]},
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_acceder_invite_token_valide(self, client, mock_innovations_service):
        from src.services.ia_avancee.types_central import DonneesInviteResponse

        mock_innovations_service.obtenir_donnees_invite.return_value = DonneesInviteResponse(
            enfant={"prenom": "Jules"},
            routines=[{"nom": "Routine du soir"}],
            repas_semaine=[{"date": "2026-03-30", "type": "déjeuner", "recette": "Pâtes"}],
            contacts_urgence=[{"nom": "Dr. Martin", "telephone": "0601020304"}],
            notes="Accès invité",
        )

        response = client.get("/api/v1/rapports/invite/abc123")
        assert response.status_code == 200
        data = response.json()
        assert data["enfant"]["prenom"] == "Jules"

    def test_acceder_invite_token_expire(self, client, mock_innovations_service):
        mock_innovations_service.obtenir_donnees_invite.return_value = None

        response = client.get("/api/v1/rapports/invite/expired-token")
        assert response.status_code == 404


# Modes famille et météo


class TestVacationModeTransverse:
    """Tests des endpoints métier pour le mode vacances, les insights et la météo contextuelle."""

    def test_lire_mode_vacances(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ModeVacancesResponse

        mock_innovations_service.obtenir_mode_vacances.return_value = ModeVacancesResponse(
            actif=True,
            checklist_voyage_auto=True,
            courses_mode_compact=True,
            entretien_suspendu=True,
            recommandations=["Checklist voyage prête"],
        )

        response = client.get("/api/v1/famille/mode-vacances", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is True
        assert data["entretien_suspendu"] is True

    def test_configurer_mode_vacances(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ModeVacancesResponse

        mock_innovations_service.configurer_mode_vacances.return_value = ModeVacancesResponse(
            actif=False,
            checklist_voyage_auto=False,
            courses_mode_compact=False,
            entretien_suspendu=False,
            recommandations=["Mode vacances désactivé"],
        )

        response = client.post(
            "/api/v1/famille/mode-vacances/config",
            json={"actif": False, "checklist_voyage_auto": False},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is False
        assert data["checklist_voyage_auto"] is False

    def test_insights_quotidiens_limites_a_deux(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import InsightQuotidien, InsightsQuotidiensResponse

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
            "/api/v1/dashboard/insights-quotidiens?limite=2",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["limite_journaliere"] == 2
        assert data["nb_insights"] <= 2

    def test_meteo_contextuelle_cross_module(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import MeteoContextuelleResponse, MeteoImpactModule

        mock_innovations_service.analyser_meteo_contextuelle.return_value = MeteoContextuelleResponse(
            ville="Paris",
            saison="printemps",
            temperature=18.5,
            description="Partiellement nuageux",
            modules=[
                MeteoImpactModule(module="cuisine", impact="Adapter les menus"),
                MeteoImpactModule(module="famille", impact="Activités int/ext"),
            ],
        )

        response = client.get("/api/v1/dashboard/meteo-contextuelle", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["ville"] == "Paris"
        assert len(data["modules"]) >= 2


# Préférences, planification et batch


class TestLearningPreferencesTransverses:
    """Tests des endpoints IA transverses liés aux préférences, à la planification et au batch."""

    def test_preferences_apprises(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ApprentissagePreferencesResponse, PreferenceApprise

        mock_innovations_service.analyser_preferences_apprises.return_value = ApprentissagePreferencesResponse(
            semaines_analysees=3,
            influence_active=True,
            preferences_favorites=[
                PreferenceApprise(categorie="categorie_recette", valeur="poisson", score_confiance=0.82)
            ],
            ajustements_suggestions=["Prioriser les recettes poisson"],
        )

        response = client.get("/api/v1/preferences/preferences-apprises", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["semaines_analysees"] >= 2
        assert data["influence_active"] is True

    def test_saisonnalite_intelligente(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import SaisonnaliteIntelligenteResponse

        mock_innovations_service.appliquer_saisonnalite_intelligente.return_value = SaisonnaliteIntelligenteResponse(
            mois_courant="avril",
            ingredients_saison=["asperges", "radis"],
            recettes_recommandees=["Salade printanière"],
            conseils_achat=["Privilégier les légumes locaux"],
        )

        response = client.get("/api/v1/recettes/saisonnalite-intelligente", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["mois_courant"] == "avril"
        assert "asperges" in data["ingredients_saison"]

    def test_planification_hebdo_complete_auto(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import BlocPlanificationAuto, PlanificationHebdoCompleteResponse

        mock_innovations_service.generer_planification_hebdo_complete.return_value = PlanificationHebdoCompleteResponse(
            semaine_reference="2026-04-06",
            genere_en_un_clic=True,
            blocs=[
                BlocPlanificationAuto(titre="Repas semaine", items=["Saumon + legumes"]),
                BlocPlanificationAuto(titre="Liste de courses", items=["saumon", "courgettes"]),
            ],
            resume="Planning complet genere automatiquement",
        )

        response = client.get("/api/v1/planning/planification-auto", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["genere_en_un_clic"] is True
        assert len(data["blocs"]) >= 2

    def test_batch_cooking_intelligent(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import BatchCookingIntelligentResponse, EtapeBatchIntelligente

        mock_innovations_service.proposer_batch_cooking_intelligent.return_value = BatchCookingIntelligentResponse(
            session_nom="Batch intelligent 06/04",
            date_session="2026-04-05",
            recettes_cibles=["Curry doux", "Compote"],
            duree_estimee_totale_minutes=90,
            etapes=[EtapeBatchIntelligente(ordre=1, action="Preparer curry", duree_minutes=45)],
            conseils=["Paralleliser les cuissons"],
        )

        response = client.get("/api/v1/batch-cooking/intelligent", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["duree_estimee_totale_minutes"] > 0
        assert len(data["etapes"]) >= 1

    def test_generer_carte_visuelle(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import CarteVisuellePartageableResponse

        mock_innovations_service.generer_carte_visuelle_partageable.return_value = CarteVisuellePartageableResponse(
            type_carte="planning",
            format_image="image/svg+xml",
            filename="carte-planning.svg",
            contenu_base64="PHN2Zz48L3N2Zz4=",
            metadata={"theme": "magazine-familial"},
        )

        response = client.post(
            "/api/v1/rapports/carte-visuelle",
            json={"type_carte": "planning", "titre": "Semaine famille"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["format_image"] == "image/svg+xml"
        assert len(data["contenu_base64"]) > 0

    def test_mode_tablette_magazine(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import CarteMagazineTablette, ModeTabletteMagazineResponse

        mock_innovations_service.obtenir_mode_tablette_magazine.return_value = ModeTabletteMagazineResponse(
            titre="Edition tablette",
            sous_titre="Vue magazine",
            cartes=[CarteMagazineTablette(titre="Score", valeur="78/100", action_url="/")],
        )

        response = client.get("/api/v1/rapports/mode-tablette-magazine", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["titre"] == "Edition tablette"
        assert len(data["cartes"]) >= 1


# Fonctions transverses long terme


class TestTelegramEnergyTransverses:
    """Tests des endpoints métier liés à Telegram, aux prix auto et à l'énergie temps réel."""

    def test_telegram_conversationnel(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import CommandeTelegram, TelegramConversationnelResponse

        mock_innovations_service.obtenir_capacites_telegram_conversationnelles.return_value = TelegramConversationnelResponse(
            actif=True,
            nb_commandes=6,
            commandes=[
                CommandeTelegram(commande="menu", action="Planning"),
                CommandeTelegram(commande="courses", action="Courses"),
            ],
        )

        response = client.get(
            "/api/v1/dashboard/telegram-conversationnel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["actif"] is True
        assert data["nb_commandes"] >= 5

    def test_comparateur_prix_auto(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import ComparateurPrixAutomatiqueResponse, PrixIngredientCompare

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
            alertes=["tomate: baisse détectée (20.0% vs historique)"],
        )

        response = client.get(
            "/api/v1/courses/comparateur-prix-auto?top_n=20",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nb_ingredients_analyses"] == 20
        assert data["nb_alertes"] >= 1

    def test_energie_temps_reel(self, client, auth_headers, mock_innovations_service):
        from src.services.ia_avancee.types_central import EnergieTempsReelResponse

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
            "/api/v1/habitat/energie-temps-reel",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["source"] in {"linky", "estimation_releves"}
        assert data["consommation_mois_kwh"] is not None


class TestSuppressionPrefixeInnovations:
    """Vérifie que l'ancien namespace `/api/v1/innovations` n'est plus exposé."""

    def test_prefixe_innovations_retourne_404(self, client, auth_headers):
        response = client.get("/api/v1/innovations/score-bien-etre", headers=auth_headers)
        assert response.status_code == 404



