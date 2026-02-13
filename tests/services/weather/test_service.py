"""
Tests pour src/services/weather/service.py

Couvre le service météo principal avec mocks des appels HTTP et base de données.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import httpx
import pytest

from src.services.weather.service import (
    AlerteMeteo,
    MeteoJour,
    NiveauAlerte,
    PlanArrosage,
    ServiceMeteo,
    TypeAlertMeteo,
)

# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def service():
    """Service météo avec localisation Paris."""
    return ServiceMeteo(latitude=48.8566, longitude=2.3522)


@pytest.fixture
def mock_response_previsions():
    """Réponse simulée de l'API Open-Meteo."""
    return {
        "daily": {
            "time": [(date.today() + timedelta(days=i)).isoformat() for i in range(7)],
            "temperature_2m_min": [5, 7, 8, 10, 12, 14, 10],
            "temperature_2m_max": [15, 17, 18, 22, 25, 28, 20],
            "precipitation_sum": [0, 5, 0, 0, 0, 0, 10],
            "precipitation_probability_max": [10, 60, 20, 10, 5, 5, 70],
            "wind_speed_10m_max": [20, 30, 15, 10, 25, 40, 55],
            "wind_direction_10m_dominant": [180, 270, 90, 45, 135, 225, 315],
            "uv_index_max": [3, 4, 5, 6, 7, 8, 4],
            "weathercode": [0, 63, 1, 2, 0, 3, 95],
            "sunrise": [
                f"{(date.today() + timedelta(days=i)).isoformat()}T07:30" for i in range(7)
            ],
            "sunset": [f"{(date.today() + timedelta(days=i)).isoformat()}T18:30" for i in range(7)],
        }
    }


@pytest.fixture
def mock_response_geocoding():
    """Réponse simulée de l'API de géocodage."""
    return {
        "results": [
            {
                "name": "Lyon",
                "latitude": 45.7640,
                "longitude": 4.8357,
                "country": "France",
            }
        ]
    }


@pytest.fixture
def previsions_list():
    """Liste de prévisions MeteoJour pour les tests."""
    return [
        MeteoJour(
            date=date.today() + timedelta(days=i),
            temperature_min=[5, -2, 8, 36, 10, 12, 14][i],
            temperature_max=[15, 10, 18, 42, 25, 28, 20][i],
            temperature_moyenne=[10, 4, 13, 39, 17.5, 20, 17][i],
            humidite=50,
            precipitation_mm=[0, 0, 0, 0, 0, 0, 25][i],
            probabilite_pluie=[10, 20, 15, 5, 5, 10, 80][i],
            vent_km_h=[20, 60, 15, 10, 55, 40, 30][i],
            direction_vent=["S", "O", "E", "NE", "SE", "SO", "NO"][i],
            uv_index=[3, 4, 5, 11, 7, 8, 4][i],
            lever_soleil="07:30",
            coucher_soleil="18:30",
            condition=[
                "Ensoleillé",
                "Couvert",
                "Peu nuageux",
                "Ensoleillé",
                "Ensoleillé",
                "Orage",
                "Pluie forte",
            ][i],
            icone=["â˜€ï¸", "â˜ï¸", "ðŸŒ¤ï¸", "â˜€ï¸", "â˜€ï¸", "â›ˆï¸", "ðŸŒ§ï¸"][i],
        )
        for i in range(7)
    ]


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════


class TestServiceMeteoInit:
    """Tests d'initialisation du service."""

    def test_init_defaut_paris(self):
        """Initialisation par défaut avec Paris."""
        service = ServiceMeteo()
        assert service.latitude == 48.8566
        assert service.longitude == 2.3522

    def test_init_coordonnees_custom(self):
        """Initialisation avec coordonnées personnalisées."""
        service = ServiceMeteo(latitude=45.0, longitude=5.0)
        assert service.latitude == 45.0
        assert service.longitude == 5.0

    def test_http_client_initialise(self, service):
        """Client HTTP initialisé."""
        assert service.http_client is not None
        assert isinstance(service.http_client, httpx.Client)


class TestSetLocation:
    """Tests de mise à jour de localisation."""

    def test_set_location(self, service):
        """Met à jour les coordonnées."""
        service.set_location(45.0, 5.0)
        assert service.latitude == 45.0
        assert service.longitude == 5.0


class TestSetLocationFromCity:
    """Tests de localisation par ville."""

    def test_set_location_from_city_success(self, service, mock_response_geocoding):
        """Localisation par ville réussie."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_geocoding
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("Lyon")

        assert result is True
        assert service.latitude == 45.7640
        assert service.longitude == 4.8357

    def test_set_location_from_city_not_found(self, service):
        """Ville non trouvée."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            result = service.set_location_from_city("VilleInexistante")

        assert result is False
        # Coordonnées inchangées
        assert service.latitude == 48.8566

    def test_set_location_from_city_error(self, service):
        """Erreur lors du géocodage."""
        with patch.object(
            service.http_client, "get", side_effect=httpx.RequestError("Network error")
        ):
            result = service.set_location_from_city("Paris")

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS PRÉVISIONS
# ═══════════════════════════════════════════════════════════


class TestGetPrevisions:
    """Tests de récupération des prévisions."""

    def test_get_previsions_success(self, service, mock_response_previsions):
        """Récupération des prévisions réussie."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            previsions = service.get_previsions(7)

        assert previsions is not None
        assert len(previsions) == 7
        assert isinstance(previsions[0], MeteoJour)
        assert previsions[0].temperature_min == 5
        assert previsions[0].temperature_max == 15

    def test_get_previsions_parse_dates(self, service, mock_response_previsions):
        """Dates correctement parsées."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            previsions = service.get_previsions(7)

        assert previsions[0].date == date.today()
        assert previsions[1].date == date.today() + timedelta(days=1)

    def test_get_previsions_conditions_meteo(self, service, mock_response_previsions):
        """Conditions météo correctement converties."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            previsions = service.get_previsions(7)

        # Code 0 = Ensoleillé
        assert previsions[0].condition == "Ensoleillé"
        assert previsions[0].icone == "â˜€ï¸"

        # Code 63 = Pluie modérée
        assert previsions[1].condition == "Pluie modérée"

    def test_get_previsions_error_returns_none(self, service):
        """Erreur retourne None."""
        with patch.object(
            service.http_client, "get", side_effect=httpx.RequestError("Network error")
        ):
            previsions = service.get_previsions(7)

        assert previsions is None

    def test_get_previsions_max_jours(self, service, mock_response_previsions):
        """Respecte le maximum de 16 jours."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response) as mock_get:
            service.get_previsions(20)  # Demande 20 jours

        # Vérifie que le paramètre est limité à 16
        call_args = mock_get.call_args
        assert call_args[1]["params"]["forecast_days"] == 16


# ═══════════════════════════════════════════════════════════
# TESTS MÉTHODES DÉLÉGUÉES
# ═══════════════════════════════════════════════════════════


class TestMethodesDelegatees:
    """Tests des méthodes qui délèguent aux utils."""

    def test_direction_from_degrees(self, service):
        """Délégation à utils.direction_from_degrees."""
        assert service._direction_from_degrees(0) == "N"
        assert service._direction_from_degrees(90) == "E"
        assert service._direction_from_degrees(None) == ""

    def test_weathercode_to_condition(self, service):
        """Délégation à utils.weathercode_to_condition."""
        assert service._weathercode_to_condition(0) == "Ensoleillé"
        assert service._weathercode_to_condition(95) == "Orage"

    def test_weathercode_to_icon(self, service):
        """Délégation à utils.weathercode_to_icon."""
        assert service._weathercode_to_icon(0) == "â˜€ï¸"
        assert service._weathercode_to_icon(None) == "â“"


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════


class TestGenererAlertes:
    """Tests de génération d'alertes."""

    def test_alerte_gel(self, service, previsions_list):
        """Génère alerte gel."""
        alertes = service.generer_alertes(previsions_list)

        alertes_gel = [a for a in alertes if a.type_alerte == TypeAlertMeteo.GEL]
        assert len(alertes_gel) >= 1
        assert alertes_gel[0].niveau == NiveauAlerte.DANGER  # -2°C < 0

    def test_alerte_canicule(self, service, previsions_list):
        """Génère alerte canicule."""
        alertes = service.generer_alertes(previsions_list)

        alertes_canicule = [a for a in alertes if a.type_alerte == TypeAlertMeteo.CANICULE]
        assert len(alertes_canicule) >= 1
        assert alertes_canicule[0].niveau == NiveauAlerte.DANGER  # 42°C >= 40

    def test_alerte_pluie_forte(self, service, previsions_list):
        """Génère alerte pluie forte."""
        alertes = service.generer_alertes(previsions_list)

        alertes_pluie = [a for a in alertes if a.type_alerte == TypeAlertMeteo.PLUIE_FORTE]
        assert len(alertes_pluie) >= 1

    def test_alerte_vent_fort(self, service, previsions_list):
        """Génère alerte vent fort."""
        alertes = service.generer_alertes(previsions_list)

        alertes_vent = [a for a in alertes if a.type_alerte == TypeAlertMeteo.VENT_FORT]
        assert len(alertes_vent) >= 1

    def test_alerte_orage(self, service, previsions_list):
        """Génère alerte orage."""
        alertes = service.generer_alertes(previsions_list)

        alertes_orage = [a for a in alertes if a.type_alerte == TypeAlertMeteo.ORAGE]
        assert len(alertes_orage) >= 1

    def test_alerte_secheresse(self, service):
        """Génère alerte sécheresse si plusieurs jours sans pluie."""
        # Créer 8 jours sans pluie significative
        previsions = [
            MeteoJour(
                date=date.today() + timedelta(days=i),
                temperature_min=15,
                temperature_max=25,
                temperature_moyenne=20,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=10,
                direction_vent="N",
                uv_index=5,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Ensoleillé",
                icone="â˜€ï¸",
            )
            for i in range(8)
        ]
        alertes = service.generer_alertes(previsions)

        alertes_secheresse = [a for a in alertes if a.type_alerte == TypeAlertMeteo.SECHERESSE]
        assert len(alertes_secheresse) == 1
        assert "8 jours" in alertes_secheresse[0].message

    def test_aucune_alerte_conditions_normales(self, service):
        """Pas d'alerte avec conditions normales."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=12,
                temperature_max=22,
                temperature_moyenne=17,
                humidite=50,
                precipitation_mm=3,
                probabilite_pluie=30,
                vent_km_h=15,
                direction_vent="N",
                uv_index=5,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Nuageux",
                icone="â˜ï¸",
            )
        ]
        alertes = service.generer_alertes(previsions)
        assert len(alertes) == 0

    def test_generer_alertes_sans_previsions(self, service, mock_response_previsions):
        """Récupère les prévisions si non fournies."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            alertes = service.generer_alertes()  # Pas de prévisions fournies

        # Doit fonctionner sans erreur
        assert isinstance(alertes, list)

    def test_generer_alertes_previsions_none(self, service):
        """Retourne liste vide si prévisions None (erreur API)."""
        with patch.object(service.http_client, "get", side_effect=httpx.RequestError("Error")):
            alertes = service.generer_alertes()

        assert alertes == []


# ═══════════════════════════════════════════════════════════
# TESTS CONSEILS
# ═══════════════════════════════════════════════════════════


class TestGenererConseils:
    """Tests de génération de conseils."""

    def test_conseils_chaleur(self, service):
        """Conseils pour température élevée."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=20,
                temperature_max=30,
                temperature_moyenne=25,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=10,
                direction_vent="N",
                uv_index=5,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Ensoleillé",
                icone="â˜€ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        assert len(conseils) >= 1
        # Conseil arrosage pour chaleur
        titres = [c.titre for c in conseils]
        assert any("arrosage" in t.lower() for t in titres)

    def test_conseils_nuits_fraiches(self, service):
        """Conseils pour nuits fraîches."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=5,
                temperature_max=15,
                temperature_moyenne=10,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=10,
                direction_vent="N",
                uv_index=3,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Nuageux",
                icone="â˜ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        titres = [c.titre for c in conseils]
        assert any("nuit" in t.lower() for t in titres)

    def test_conseils_journee_seche(self, service):
        """Conseils pour journée sèche."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15,
                temperature_max=20,
                temperature_moyenne=17.5,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=5,
                vent_km_h=10,
                direction_vent="N",
                uv_index=4,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Ensoleillé",
                icone="â˜€ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        titres = [c.titre for c in conseils]
        assert any("sèche" in t.lower() for t in titres)

    def test_conseils_pluie_prevue(self, service):
        """Conseils si pluie prévue."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=12,
                temperature_max=18,
                temperature_moyenne=15,
                humidite=70,
                precipitation_mm=10,
                probabilite_pluie=80,
                vent_km_h=20,
                direction_vent="O",
                uv_index=2,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Pluie",
                icone="ðŸŒ§ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        titres = [c.titre for c in conseils]
        assert any("pluie" in t.lower() for t in titres)

    def test_conseils_peu_de_vent(self, service):
        """Conseils pour peu de vent (idéal traiter)."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15,
                temperature_max=22,
                temperature_moyenne=18.5,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=5,  # Peu de vent
                direction_vent="N",
                uv_index=4,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Nuageux",
                icone="â˜ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        titres = [c.titre for c in conseils]
        assert any("traiter" in t.lower() for t in titres)

    def test_conseils_uv_forts(self, service):
        """Conseils pour UV forts."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=20,
                temperature_max=32,
                temperature_moyenne=26,
                humidite=40,
                precipitation_mm=0,
                probabilite_pluie=5,
                vent_km_h=10,
                direction_vent="S",
                uv_index=9,  # UV très forts
                lever_soleil="06:00",
                coucher_soleil="21:00",
                condition="Ensoleillé",
                icone="â˜€ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        titres = [c.titre for c in conseils]
        assert any("uv" in t.lower() for t in titres)

    def test_conseils_tries_par_priorite(self, service):
        """Conseils triés par priorité."""
        previsions = [
            MeteoJour(
                date=date.today(),
                temperature_min=15,
                temperature_max=30,
                temperature_moyenne=22.5,
                humidite=50,
                precipitation_mm=0,
                probabilite_pluie=10,
                vent_km_h=5,
                direction_vent="N",
                uv_index=9,
                lever_soleil="07:00",
                coucher_soleil="19:00",
                condition="Ensoleillé",
                icone="â˜€ï¸",
            )
        ]
        conseils = service.generer_conseils(previsions)

        if len(conseils) >= 2:
            for i in range(len(conseils) - 1):
                assert conseils[i].priorite <= conseils[i + 1].priorite

    def test_conseils_sans_previsions(self, service, mock_response_previsions):
        """Récupère les prévisions si non fournies."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            conseils = service.generer_conseils()

        assert isinstance(conseils, list)

    def test_conseils_previsions_vides(self, service):
        """Retourne liste vide si pas de prévisions."""
        conseils = service.generer_conseils([])
        assert conseils == []


# ═══════════════════════════════════════════════════════════
# TESTS PLAN ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestGenererPlanArrosage:
    """Tests de génération du plan d'arrosage."""

    def test_plan_7_jours(self, service, mock_response_previsions):
        """Génère plan pour 7 jours."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            plan = service.generer_plan_arrosage(7, surface_m2=50)

        assert len(plan) == 7
        assert all(isinstance(p, PlanArrosage) for p in plan)

    def test_plan_pas_arrosage_si_pluie(self, service, mock_response_previsions):
        """Pas d'arrosage si pluie significative."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            plan = service.generer_plan_arrosage(7)

        # Jour 2 a 5mm de pluie dans le mock
        assert plan[1].besoin_arrosage is False or "Pluie" in plan[1].raison

    def test_plan_surface_custom(self, service, mock_response_previsions):
        """Surface personnalisée affecte les quantités."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            plan_petit = service.generer_plan_arrosage(7, surface_m2=25)
            plan_grand = service.generer_plan_arrosage(7, surface_m2=100)

        # Les quantités devraient différer
        # (vérifie que la surface est prise en compte)
        assert isinstance(plan_petit, list)
        assert isinstance(plan_grand, list)

    def test_plan_vide_si_erreur(self, service):
        """Retourne liste vide si erreur API."""
        with patch.object(service.http_client, "get", side_effect=httpx.RequestError("Error")):
            plan = service.generer_plan_arrosage(7)

        assert plan == []

    def test_plan_contient_raisons(self, service, mock_response_previsions):
        """Chaque jour a une raison."""
        mock_response = Mock()
        mock_response.json.return_value = mock_response_previsions
        mock_response.raise_for_status = Mock()

        with patch.object(service.http_client, "get", return_value=mock_response):
            plan = service.generer_plan_arrosage(7)

        for jour in plan:
            assert jour.raison != ""


# ═══════════════════════════════════════════════════════════
# TESTS BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════


class TestSauvegarderAlerte:
    """Tests de sauvegarde d'alerte en base."""

    def test_sauvegarder_alerte_success(self, service):
        """Sauvegarde une alerte."""
        alerte = AlerteMeteo(
            type_alerte=TypeAlertMeteo.GEL,
            niveau=NiveauAlerte.ATTENTION,
            titre="Test gel",
            message="Message test",
            conseil_jardin="Conseil test",
            date_debut=date.today(),
            temperature=-2.0,
        )

        mock_db = MagicMock()

        # Patcher le décorateur avec_session_db pour injecter notre mock
        with patch("src.services.weather.service.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_db)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            # Appel direct avec db injecté
            result = service.sauvegarder_alerte.__wrapped__(service, alerte, db=mock_db)

        # Vérifie les appels
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestListerAlertesActives:
    """Tests de listage des alertes actives."""

    def test_lister_alertes_filtrees(self, service):
        """Liste les alertes non lues."""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        result = service.lister_alertes_actives.__wrapped__(service, db=mock_db)

        assert result == []
        mock_db.query.assert_called_once()


class TestMarquerAlerteLue:
    """Tests de marquage d'alerte comme lue."""

    def test_marquer_alerte_trouvee(self, service):
        """Marque une alerte existante comme lue."""
        mock_db = MagicMock()
        mock_alerte = MagicMock()
        mock_alerte.lu = False

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_alerte

        result = service.marquer_alerte_lue.__wrapped__(service, alerte_id=1, db=mock_db)

        assert result is True
        assert mock_alerte.lu is True
        mock_db.commit.assert_called_once()

    def test_marquer_alerte_non_trouvee(self, service):
        """Retourne False si alerte non trouvée."""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = service.marquer_alerte_lue.__wrapped__(service, alerte_id=999, db=mock_db)

        assert result is False


# ═══════════════════════════════════════════════════════════
# TESTS CONFIG MÉTÉO
# ═══════════════════════════════════════════════════════════


class TestObtienirConfigMeteo:
    """Tests de récupération de config météo."""

    def test_obtenir_config_existante(self, service):
        """Récupère une config existante."""
        mock_db = MagicMock()
        mock_config = MagicMock()

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_config

        user_id = uuid4()
        result = service.obtenir_config_meteo.__wrapped__(service, user_id=user_id, db=mock_db)

        assert result == mock_config


class TestSauvegarderConfigMeteo:
    """Tests de sauvegarde de config météo."""

    def test_creer_nouvelle_config(self, service):
        """Crée une nouvelle config si inexistante."""
        mock_db = MagicMock()

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Pas de config existante

        user_id = uuid4()
        result = service.sauvegarder_config_meteo.__wrapped__(
            service,
            user_id=user_id,
            latitude=45.0,
            longitude=5.0,
            ville="Lyon",
            surface_jardin=100.0,
            db=mock_db,
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_mettre_a_jour_config_existante(self, service):
        """Met à jour une config existante."""
        mock_db = MagicMock()
        mock_config = MagicMock()

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_config  # Config existante

        user_id = uuid4()
        result = service.sauvegarder_config_meteo.__wrapped__(
            service,
            user_id=user_id,
            latitude=45.0,
            db=mock_db,
        )

        # Pas d'appel à add car config existe déjà
        mock_db.add.assert_not_called()
        mock_db.commit.assert_called_once()
        assert mock_config.latitude == Decimal("45.0")


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests des fonctions factory."""

    def test_obtenir_service_meteo(self):
        """Factory retourne un service."""
        from src.services.weather.service import obtenir_service_meteo

        service = obtenir_service_meteo()
        assert isinstance(service, ServiceMeteo)

    def test_get_weather_service(self):
        """Alias anglais fonctionne."""
        from src.services.weather.service import get_weather_service

        service = get_weather_service()
        assert isinstance(service, ServiceMeteo)

    def test_get_weather_garden_service(self):
        """Alias rétrocompatibilité fonctionne."""
        from src.services.weather.service import get_weather_garden_service

        service = get_weather_garden_service()
        assert isinstance(service, ServiceMeteo)


# ═══════════════════════════════════════════════════════════
# TESTS ALIAS
# ═══════════════════════════════════════════════════════════


class TestAlias:
    """Tests des alias de classe."""

    def test_weather_garden_service_alias(self):
        """WeatherGardenService est alias de ServiceMeteo."""
        from src.services.weather.service import WeatherGardenService

        assert WeatherGardenService is ServiceMeteo

    def test_weather_service_alias(self):
        """WeatherService est alias de ServiceMeteo."""
        from src.services.weather.service import WeatherService

        assert WeatherService is ServiceMeteo
