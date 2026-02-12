"""
Tests pour le service OCR de factures.

Couverture cible: >80%
- Modèles de données (DonneesFacture, ResultatOCR)
- Parser de réponses JSON
- Extraction OCR (avec mocks)
- Fonctions de détection manuelle
- Patterns de montants
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock
import json

from src.services.integrations.facture import (
    DonneesFacture,
    ResultatOCR,
    FactureOCRService,
    detecter_fournisseur,
    extraire_montant,
    PATTERNS_FOURNISSEURS,
    PATTERNS_MONTANTS,
    get_facture_ocr_service,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def service():
    """Instance du service pour les tests."""
    return FactureOCRService()


@pytest.fixture
def donnees_facture_valides():
    """Données de facture valides pour les tests."""
    return {
        "fournisseur": "EDF",
        "type_energie": "electricite",
        "montant_ttc": 156.78,
        "montant_ht": 130.65,
        "consommation": 1250,
        "unite_consommation": "kWh",
        "date_debut": "2025-01-01",
        "date_fin": "2025-01-31",
        "mois_facturation": 1,
        "annee_facturation": 2025,
        "numero_facture": "FA-2025-0001",
        "numero_client": "CLI-123456",
        "prix_kwh": 0.18,
        "abonnement": 15.50
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES DE DONNÃ‰ES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDonneesFacture:
    """Tests du modèle DonneesFacture."""

    def test_creation_minimale(self):
        """Test création avec champs requis uniquement."""
        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=100.0
        )
        assert donnees.fournisseur == "EDF"
        assert donnees.type_energie == "electricite"
        assert donnees.montant_ttc == 100.0
        assert donnees.confiance == 0.0
        assert donnees.erreurs == []

    def test_creation_complete(self, donnees_facture_valides):
        """Test création avec tous les champs."""
        # Convertir les dates
        data = donnees_facture_valides.copy()
        data["date_debut"] = date.fromisoformat(data["date_debut"])
        data["date_fin"] = date.fromisoformat(data["date_fin"])

        donnees = DonneesFacture(**data)
        
        assert donnees.fournisseur == "EDF"
        assert donnees.montant_ttc == 156.78
        assert donnees.consommation == 1250
        assert donnees.date_debut == date(2025, 1, 1)
        assert donnees.numero_facture == "FA-2025-0001"

    def test_valeurs_par_defaut(self):
        """Test des valeurs par défaut."""
        donnees = DonneesFacture(
            fournisseur="Inconnu",
            type_energie="autre",
            montant_ttc=0
        )
        
        assert donnees.montant_ht is None
        assert donnees.consommation is None
        assert donnees.unite_consommation == ""
        assert donnees.date_debut is None
        assert donnees.confiance == 0.0
        assert donnees.erreurs == []

    def test_erreurs_et_confiance(self):
        """Test gestion erreurs et confiance."""
        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=100.0,
            confiance=0.85,
            erreurs=["Consommation non trouvée", "Date incomplète"]
        )
        
        assert donnees.confiance == 0.85
        assert len(donnees.erreurs) == 2


class TestResultatOCR:
    """Tests du modèle ResultatOCR."""

    def test_succes(self):
        """Test résultat succès."""
        donnees = DonneesFacture(
            fournisseur="EDF",
            type_energie="electricite",
            montant_ttc=100.0
        )
        result = ResultatOCR(
            succes=True,
            donnees=donnees,
            texte_brut='{"fournisseur": "EDF"}',
            message="OK"
        )
        
        assert result.succes is True
        assert result.donnees is not None
        assert result.donnees.fournisseur == "EDF"

    def test_echec(self):
        """Test résultat échec."""
        result = ResultatOCR(
            succes=False,
            donnees=None,
            message="Erreur OCR"
        )
        
        assert result.succes is False
        assert result.donnees is None
        assert result.message == "Erreur OCR"

    def test_valeurs_par_defaut(self):
        """Test valeurs par défaut."""
        result = ResultatOCR()
        
        assert result.succes is True
        assert result.donnees is None
        assert result.texte_brut == ""
        assert result.message == ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PARSER DE RÃ‰PONSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestParserReponse:
    """Tests du parser JSON."""

    def test_parser_json_valide(self, service, donnees_facture_valides):
        """Test parsing JSON valide."""
        json_str = json.dumps(donnees_facture_valides)
        result = service._parser_reponse(json_str)
        
        assert isinstance(result, DonneesFacture)
        assert result.fournisseur == "EDF"
        assert result.montant_ttc == 156.78

    def test_parser_json_avec_markdown(self, service, donnees_facture_valides):
        """Test parsing JSON avec wrapper markdown."""
        json_str = f"```json\n{json.dumps(donnees_facture_valides)}\n```"
        result = service._parser_reponse(json_str)
        
        assert result.fournisseur == "EDF"
        assert result.montant_ttc == 156.78

    def test_parser_json_invalide(self, service):
        """Test parsing JSON invalide."""
        result = service._parser_reponse("ceci n'est pas du JSON")
        
        assert result.fournisseur == "Inconnu"
        assert result.type_energie == "autre"
        assert result.montant_ttc == 0
        assert len(result.erreurs) > 0
        assert "Erreur parsing" in result.erreurs[0]

    def test_parser_calcul_confiance_montant_manquant(self, service):
        """Test calcul confiance sans montant explicite (montant_ttc=0)."""
        # montant_ttc est requis, donc on teste avec montant_ttc=0 qui déclenche la pénalité
        data = {"fournisseur": "EDF", "type_energie": "electricite", "montant_ttc": 0}
        json_str = json.dumps(data)
        result = service._parser_reponse(json_str)
        
        # Montant 0 déclenche l'erreur "Montant TTC non trouvé"
        assert result.confiance < 1.0  # Pénalité pour montant manquant
        assert "Montant TTC non trouvé" in result.erreurs

    def test_parser_calcul_confiance_fournisseur_inconnu(self, service):
        """Test calcul confiance fournisseur inconnu."""
        data = {"fournisseur": "Inconnu", "type_energie": "autre", "montant_ttc": 100}
        json_str = json.dumps(data)
        result = service._parser_reponse(json_str)
        
        assert result.confiance < 1.0  # Pénalité pour fournisseur inconnu
        assert "Fournisseur non identifié" in result.erreurs

    def test_parser_calcul_confiance_consommation_manquante(self, service):
        """Test calcul confiance sans consommation."""
        data = {"fournisseur": "EDF", "type_energie": "electricite", "montant_ttc": 100}
        json_str = json.dumps(data)
        result = service._parser_reponse(json_str)
        
        assert "Consommation non trouvée" in result.erreurs

    def test_parser_dates_conversion(self, service):
        """Test conversion des dates."""
        data = {
            "fournisseur": "EDF",
            "type_energie": "electricite",
            "montant_ttc": 100,
            "date_debut": "2025-01-15",
            "date_fin": "2025-02-14"
        }
        json_str = json.dumps(data)
        result = service._parser_reponse(json_str)
        
        assert result.date_debut == date(2025, 1, 15)
        assert result.date_fin == date(2025, 2, 14)

    def test_parser_dates_invalides(self, service):
        """Test avec dates invalides."""
        data = {
            "fournisseur": "EDF",
            "type_energie": "electricite",
            "montant_ttc": 100,
            "date_debut": "invalide",
            "date_fin": "aussi-invalide"
        }
        json_str = json.dumps(data)
        result = service._parser_reponse(json_str)
        
        # Dates invalides deviennent None
        assert result.date_debut is None
        assert result.date_fin is None

    def test_parser_confiance_complete(self, service, donnees_facture_valides):
        """Test confiance maximale avec données complètes."""
        json_str = json.dumps(donnees_facture_valides)
        result = service._parser_reponse(json_str)
        
        # Avec toutes les données, confiance devrait être élevée
        assert result.confiance >= 0.7


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXTRACTION OCR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtractionOCR:
    """Tests de l'extraction OCR."""

    @pytest.mark.asyncio
    async def test_extraction_succes(self, service, donnees_facture_valides):
        """Test extraction réussie."""
        json_response = json.dumps(donnees_facture_valides)
        
        with patch.object(
            service.client,
            'chat_with_vision',
            new_callable=AsyncMock,
            return_value=json_response
        ):
            result = await service.extraire_donnees_facture("base64_image_data")
            
            assert result.succes is True
            assert result.donnees is not None
            assert result.donnees.fournisseur == "EDF"
            assert result.message == "Extraction réussie"

    @pytest.mark.asyncio
    async def test_extraction_erreur_api(self, service):
        """Test extraction avec erreur API."""
        with patch.object(
            service.client,
            'chat_with_vision',
            new_callable=AsyncMock,
            side_effect=Exception("API Error")
        ):
            result = await service.extraire_donnees_facture("base64_image_data")
            
            assert result.succes is False
            assert result.donnees is None
            assert "Erreur d'extraction" in result.message

    def test_extraction_sync(self, service, donnees_facture_valides):
        """Test version synchrone."""
        json_response = json.dumps(donnees_facture_valides)
        
        with patch.object(
            service.client,
            'chat_with_vision',
            new_callable=AsyncMock,
            return_value=json_response
        ):
            result = service.extraire_donnees_facture_sync("base64_image_data")
            
            assert result.succes is True
            assert result.donnees is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DÃ‰TECTION FOURNISSEUR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestDetectionFournisseur:
    """Tests de la détection de fournisseur."""

    def test_detecter_edf(self):
        """Test détection EDF."""
        texte = "Facture EDF Numéro 123456"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "EDF"
        assert type_energie == "electricite"

    def test_detecter_electricite_de_france(self):
        """Test détection Ã‰lectricité de France."""
        texte = "Ã‰LECTRICITÃ‰ DE FRANCE - Votre facture"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "EDF"
        assert type_energie == "electricite"

    def test_detecter_engie(self):
        """Test détection Engie."""
        texte = "ENGIE votre fournisseur de gaz"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "ENGIE"
        assert type_energie == "gaz"

    def test_detecter_gdf(self):
        """Test détection GDF (ancien Engie)."""
        texte = "Gaz de France - Facture mensuelle"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "ENGIE"
        assert type_energie == "gaz"

    def test_detecter_totalenergies(self):
        """Test détection TotalEnergies."""
        texte = "TotalEnergies - Votre facture électricité"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "TOTALENERGIES"
        assert type_energie == "electricite"

    def test_detecter_total_direct_energie(self):
        """Test détection Total Direct Energie."""
        texte = "Total Direct Energie - Facture"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "TOTALENERGIES"
        assert type_energie == "electricite"

    def test_detecter_veolia(self):
        """Test détection Veolia."""
        texte = "Veolia Eau - Consommation"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "VEOLIA"
        assert type_energie == "eau"

    def test_detecter_eau_de_paris(self):
        """Test détection Eau de Paris."""
        texte = "Eau de Paris - Facture d'eau"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "VEOLIA"
        assert type_energie == "eau"

    def test_detecter_suez(self):
        """Test détection Suez."""
        texte = "SUEZ - Votre facture eau"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "VEOLIA"
        assert type_energie == "eau"

    def test_detecter_inconnu(self):
        """Test fournisseur non reconnu."""
        texte = "Facture de quelque chose"
        nom, type_energie = detecter_fournisseur(texte)
        
        assert nom == "Inconnu"
        assert type_energie == "autre"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXTRACTION MONTANTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestExtractionMontants:
    """Tests de l'extraction des montants."""

    def test_extraire_montant_ttc(self):
        """Test extraction montant TTC."""
        texte = "Total Ã  payer: 156,78 â‚¬"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["montant_ttc"])
        
        assert montant == 156.78

    def test_extraire_montant_ttc_variante(self):
        """Test extraction montant TTC variante."""
        texte = "Total TTC 123.45â‚¬"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["montant_ttc"])
        
        assert montant == 123.45

    def test_extraire_consommation_kwh(self):
        """Test extraction consommation kWh."""
        texte = "Consommation: 1250 kWh"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["consommation_kwh"])
        
        assert montant == 1250.0

    def test_extraire_consommation_kwh_avec_espaces(self):
        """Test extraction consommation kWh avec espaces."""
        texte = "Votre consommation: 1 250 kWh"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["consommation_kwh"])
        
        assert montant == 1250.0

    def test_extraire_consommation_m3(self):
        """Test extraction consommation mÂ³."""
        texte = "Volume consommé: 45,5 mÂ³"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["consommation_m3"])
        
        assert montant == 45.5

    def test_extraire_consommation_m3_variante(self):
        """Test extraction consommation m3 (sans exposant)."""
        texte = "Consommation eau: 32.7 m3"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["consommation_m3"])
        
        assert montant == 32.7

    def test_extraire_montant_non_trouve(self):
        """Test montant non trouvé."""
        texte = "Pas de montant ici"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["montant_ttc"])
        
        assert montant is None

    def test_extraire_montant_invalide(self):
        """Test montant avec format invalide."""
        texte = "Total: ABC â‚¬"
        montant = extraire_montant(texte, PATTERNS_MONTANTS["montant_ttc"])
        
        assert montant is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS PATTERNS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPatterns:
    """Tests des patterns de détection."""

    def test_patterns_fournisseurs_exist(self):
        """Test que tous les patterns fournisseurs existent."""
        assert "edf" in PATTERNS_FOURNISSEURS
        assert "engie" in PATTERNS_FOURNISSEURS
        assert "totalenergies" in PATTERNS_FOURNISSEURS
        assert "veolia" in PATTERNS_FOURNISSEURS

    def test_patterns_fournisseurs_structure(self):
        """Test structure des patterns fournisseurs."""
        for nom, info in PATTERNS_FOURNISSEURS.items():
            assert "regex" in info
            assert "type" in info
            assert info["type"] in ["electricite", "gaz", "eau"]

    def test_patterns_montants_exist(self):
        """Test que tous les patterns montants existent."""
        assert "montant_ttc" in PATTERNS_MONTANTS
        assert "consommation_kwh" in PATTERNS_MONTANTS
        assert "consommation_m3" in PATTERNS_MONTANTS


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFactory:
    """Tests de la factory."""

    def test_get_facture_ocr_service(self):
        """Test obtention du service."""
        service = get_facture_ocr_service()
        assert isinstance(service, FactureOCRService)

    def test_factory_nouvelle_instance(self):
        """Test que la factory crée une nouvelle instance Ã  chaque appel."""
        s1 = get_facture_ocr_service()
        s2 = get_facture_ocr_service()
        # La factory crée une nouvelle instance Ã  chaque appel (pas de singleton)
        assert s1 is not s2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestServiceInit:
    """Tests d'initialisation du service."""

    def test_service_init(self, service):
        """Test initialisation correcte."""
        assert service is not None
        assert hasattr(service, 'client')
        assert hasattr(service, '_parser_reponse')

    def test_service_heritage(self, service):
        """Test que le service hérite de BaseAIService."""
        from src.services.base import BaseAIService
        assert isinstance(service, BaseAIService)
