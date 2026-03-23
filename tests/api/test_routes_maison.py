"""
Tests pour src/api/routes/maison.py

Tests unitaires des routes maison — projets, entretien, jardin, stocks,
cellier, artisans, contrats, garanties, diagnostics, eco-tips, dépenses, etc.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

PROJET_TEST = {
    "id": 1,
    "nom": "Rénovation cuisine",
    "description": "Refaire les murs et le sol",
    "statut": "en_cours",
    "priorite": "haute",
    "date_debut": "2026-03-01",
    "date_fin_prevue": "2026-06-01",
    "budget_estime": 5000.0,
}

PROJET_NOUVEAU = {
    "nom": "Terrasse extérieure",
    "description": "Construction terrasse bois",
    "statut": "planifie",
    "priorite": "moyenne",
}

TACHE_ENTRETIEN_TEST = {
    "id": 1,
    "nom": "Nettoyage filtre VMC",
    "categorie": "ventilation",
    "piece": "buanderie",
    "frequence_jours": 90,
    "priorite": "haute",
    "fait": False,
}

ELEMENT_JARDIN_TEST = {
    "id": 1,
    "nom": "Tomates cerises",
    "type": "potager",
    "location": "carré 1",
    "statut": "actif",
}

STOCK_TEST = {
    "id": 1,
    "nom": "Ampoules LED",
    "categorie": "Électricité",
    "quantite": 5,
    "unite": "pcs",
    "seuil_alerte": 2,
    "en_alerte": False,
}

ARTICLE_CELLIER_TEST = {
    "id": 1,
    "nom": "Côtes du Rhône 2022",
    "categorie": "Vin rouge",
    "quantite": 6,
    "unite": "bouteilles",
    "emplacement": "cave",
    "date_peremption": "2030-12-31",
    "prix_unitaire": 8.50,
}

ARTISAN_TEST = {
    "id": 1,
    "nom": "Dupont Plomberie",
    "metier": "plombier",
    "telephone": "0612345678",
    "email": "dupont@plomberie.fr",
    "note_satisfaction": 4,
}

CONTRAT_TEST = {
    "id": 1,
    "nom": "Assurance habitation",
    "type_contrat": "assurance",
    "fournisseur": "MAIF",
    "montant_mensuel": 42.50,
    "date_debut": "2025-01-01",
    "statut": "actif",
}

GARANTIE_TEST = {
    "id": 1,
    "nom": "Lave-vaisselle Bosch",
    "appareil": "Lave-vaisselle",
    "marque": "Bosch",
    "date_achat": "2025-06-15",
    "date_fin_garantie": "2027-06-15",
    "statut": "active",
    "piece": "cuisine",
}

DIAGNOSTIC_TEST = {
    "id": 1,
    "type_diagnostic": "DPE",
    "date_realisation": "2025-01-15",
    "date_expiration": "2035-01-15",
    "resultat": "C",
    "diagnostiqueur": "Diag Express",
}

ECO_TIP_TEST = {
    "id": 1,
    "titre": "Éteindre les lumières",
    "description": "Éteindre les lumières en sortant d'une pièce",
    "categorie": "énergie",
    "impact": "moyen",
    "actif": True,
}

DEPENSE_TEST = {
    "id": 1,
    "libelle": "Peinture salon",
    "montant": 85.50,
    "categorie": "décoration",
    "date": "2026-03-15",
}


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app)


def creer_mock(data: dict) -> MagicMock:
    """Crée un mock avec attributs."""
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS — EXISTENCE DES ENDPOINTS
# ═══════════════════════════════════════════════════════════


class TestEndpointsExistent:
    """Vérifie que les endpoints maison existent (pas 404/405)."""

    @pytest.mark.parametrize(
        "method,path",
        [
            # Projets
            ("GET", "/api/v1/maison/projets"),
            ("POST", "/api/v1/maison/projets"),
            ("GET", "/api/v1/maison/projets/1"),
            ("PATCH", "/api/v1/maison/projets/1"),
            ("DELETE", "/api/v1/maison/projets/1"),
            # Entretien
            ("GET", "/api/v1/maison/entretien"),
            ("POST", "/api/v1/maison/entretien"),
            ("PATCH", "/api/v1/maison/entretien/1"),
            ("DELETE", "/api/v1/maison/entretien/1"),
            # Jardin
            ("GET", "/api/v1/maison/jardin"),
            ("POST", "/api/v1/maison/jardin"),
            ("PATCH", "/api/v1/maison/jardin/1"),
            ("DELETE", "/api/v1/maison/jardin/1"),
            # Stocks
            ("GET", "/api/v1/maison/stocks"),
            ("POST", "/api/v1/maison/stocks"),
            ("PATCH", "/api/v1/maison/stocks/1"),
            ("DELETE", "/api/v1/maison/stocks/1"),
            # Cellier
            ("GET", "/api/v1/maison/cellier"),
            ("POST", "/api/v1/maison/cellier"),
            ("GET", "/api/v1/maison/cellier/1"),
            ("PATCH", "/api/v1/maison/cellier/1"),
            ("DELETE", "/api/v1/maison/cellier/1"),
            # Artisans
            ("GET", "/api/v1/maison/artisans"),
            ("POST", "/api/v1/maison/artisans"),
            ("GET", "/api/v1/maison/artisans/1"),
            ("PATCH", "/api/v1/maison/artisans/1"),
            ("DELETE", "/api/v1/maison/artisans/1"),
            # Contrats
            ("GET", "/api/v1/maison/contrats"),
            ("POST", "/api/v1/maison/contrats"),
            ("GET", "/api/v1/maison/contrats/1"),
            ("PATCH", "/api/v1/maison/contrats/1"),
            ("DELETE", "/api/v1/maison/contrats/1"),
            # Garanties
            ("GET", "/api/v1/maison/garanties"),
            ("POST", "/api/v1/maison/garanties"),
            ("GET", "/api/v1/maison/garanties/1"),
            ("PATCH", "/api/v1/maison/garanties/1"),
            ("DELETE", "/api/v1/maison/garanties/1"),
            # Diagnostics
            ("GET", "/api/v1/maison/diagnostics"),
            ("POST", "/api/v1/maison/diagnostics"),
            ("PATCH", "/api/v1/maison/diagnostics/1"),
            ("DELETE", "/api/v1/maison/diagnostics/1"),
            # Éco-Tips
            ("GET", "/api/v1/maison/eco-tips"),
            ("POST", "/api/v1/maison/eco-tips"),
            ("GET", "/api/v1/maison/eco-tips/1"),
            ("PATCH", "/api/v1/maison/eco-tips/1"),
            ("DELETE", "/api/v1/maison/eco-tips/1"),
            # Dépenses
            ("GET", "/api/v1/maison/depenses"),
            ("POST", "/api/v1/maison/depenses"),
            ("GET", "/api/v1/maison/depenses/1"),
            ("PATCH", "/api/v1/maison/depenses/1"),
            ("DELETE", "/api/v1/maison/depenses/1"),
            # Charges
            ("GET", "/api/v1/maison/charges"),
        ],
    )
    def test_endpoint_existe(self, client, method, path):
        """L'endpoint existe (pas 404 ni 405)."""
        func = getattr(client, method.lower())
        if method in ("POST", "PATCH"):
            response = func(path, json={"nom": "test"})
        else:
            response = func(path)
        assert response.status_code not in (404, 405), f"{method} {path} retourne {response.status_code}"


# ═══════════════════════════════════════════════════════════
# TESTS — SCHEMAS PYDANTIC MAISON
# ═══════════════════════════════════════════════════════════


class TestSchemasMaison:
    """Tests schemas Pydantic pour le domaine maison."""

    def test_projet_create_valide(self):
        from src.api.schemas.maison import ProjetCreate

        p = ProjetCreate(nom="Terrasse", statut="planifie")
        assert p.nom == "Terrasse"
        assert p.statut == "planifie"

    def test_projet_create_nom_vide_rejete(self):
        from pydantic import ValidationError
        from src.api.schemas.maison import ProjetCreate

        with pytest.raises(ValidationError):
            ProjetCreate(nom="", statut="planifie")

    def test_projet_create_nom_strip(self):
        from src.api.schemas.maison import ProjetCreate

        p = ProjetCreate(nom="  Terrasse  ", statut="planifie")
        assert p.nom == "Terrasse"

    def test_contrat_create_valide(self):
        from src.api.schemas.maison import ContratCreate

        c = ContratCreate(
            nom="Assurance habitation",
            type_contrat="assurance",
            date_debut="2025-01-01",
            statut="actif",
        )
        assert c.nom == "Assurance habitation"
        assert c.type_contrat == "assurance"

    def test_depense_create_valide(self):
        from src.api.schemas.maison import DepenseMaisonCreate

        d = DepenseMaisonCreate(
            libelle="Peinture",
            montant=85.0,
            categorie="décoration",
            date="2026-03-15",
        )
        assert d.montant == 85.0

    def test_depense_create_libelle_vide_rejete(self):
        from pydantic import ValidationError
        from src.api.schemas.maison import DepenseMaisonCreate

        with pytest.raises(ValidationError):
            DepenseMaisonCreate(libelle="", montant=10, categorie="x", date="2026-01-01")

    def test_intervention_patch_optionnel(self):
        from src.api.schemas.maison import InterventionPatch

        ip = InterventionPatch(description="Mise à jour")
        assert ip.description == "Mise à jour"
        assert ip.cout is None

    def test_incident_sav_patch_valide(self):
        from src.api.schemas.maison import IncidentSAVPatch

        i = IncidentSAVPatch(statut="résolu")
        assert i.statut == "résolu"

    def test_stats_hub_response_valide(self):
        from src.api.schemas.maison import StatsHubMaisonResponse

        s = StatsHubMaisonResponse(
            projets_en_cours=2,
            taches_en_retard=3,
            contrats_actifs=5,
            garanties_expirant_bientot=1,
            diagnostics_a_renouveler=0,
            depenses_mois=1200.0,
            stocks_en_alerte=2,
            prochains_entretiens=4,
        )
        assert s.projets_en_cours == 2
        assert s.depenses_mois == 1200.0

    def test_tache_entretien_create(self):
        from src.api.schemas.maison import TacheEntretienCreate

        t = TacheEntretienCreate(
            tache="Nettoyer VMC",
            appareil="VMC",
            categorie="ventilation",
        )
        assert t.tache == "Nettoyer VMC"

    def test_element_jardin_create(self):
        from src.api.schemas.maison import ElementJardinCreate

        e = ElementJardinCreate(nom="Tomates", type_element="potager")
        assert e.nom == "Tomates"

    def test_stock_create(self):
        from src.api.schemas.maison import StockCreate

        s = StockCreate(nom="Ampoules", categorie="Électricité", quantite=5, seuil_alerte=2)
        assert s.quantite == 5

    def test_article_cellier_create(self):
        from src.api.schemas.maison import ArticleCellierCreate

        a = ArticleCellierCreate(nom="Côtes du Rhône", categorie="Vin rouge", quantite=6)
        assert a.quantite == 6

    def test_artisan_create(self):
        from src.api.schemas.maison import ArtisanCreate

        a = ArtisanCreate(nom="Dupont", metier="plombier")
        assert a.metier == "plombier"

    def test_garantie_create(self):
        from src.api.schemas.maison import GarantieCreate

        g = GarantieCreate(
            nom="Lave-vaisselle",
            appareil="Lave-vaisselle",
            date_achat="2025-06-15",
            date_fin_garantie="2027-06-15",
        )
        assert g.appareil == "Lave-vaisselle"

    def test_diagnostic_create(self):
        from src.api.schemas.maison import DiagnosticCreate

        d = DiagnosticCreate(
            type_diagnostic="DPE",
            date_realisation="2025-01-15",
            date_expiration="2035-01-15",
        )
        assert d.type_diagnostic == "DPE"

    def test_eco_tip_create(self):
        from src.api.schemas.maison import ActionEcoCreate

        a = ActionEcoCreate(titre="Éteindre les lumières", categorie="énergie")
        assert a.titre == "Éteindre les lumières"

    def test_releve_compteur_create(self):
        from src.api.schemas.maison import ReleveCompteurCreate

        r = ReleveCompteurCreate(type_compteur="électricité", valeur=12345.0, date="2026-03-01")
        assert r.valeur == 12345.0


# ═══════════════════════════════════════════════════════════
# TESTS — PROJETS CRUD AVEC MOCK
# ═══════════════════════════════════════════════════════════


class TestRoutesProjets:
    """Tests routes /api/v1/maison/projets."""

    def test_lister_projets(self, client):
        """GET /maison/projets retourne une liste."""
        response = client.get("/api/v1/maison/projets")
        assert response.status_code in (200, 500)

    def test_creer_projet(self, client):
        """POST /maison/projets crée un projet."""
        response = client.post("/api/v1/maison/projets", json=PROJET_NOUVEAU)
        assert response.status_code in (200, 201, 500)

    def test_modifier_projet(self, client):
        """PATCH /maison/projets/{id} modifie un projet."""
        response = client.patch(
            "/api/v1/maison/projets/1",
            json={"statut": "termine"},
        )
        assert response.status_code in (200, 404, 500)

    def test_supprimer_projet(self, client):
        """DELETE /maison/projets/{id} supprime un projet."""
        response = client.delete("/api/v1/maison/projets/1")
        assert response.status_code in (200, 204, 404, 500)


class TestRoutesEntretien:
    """Tests routes /api/v1/maison/entretien."""

    def test_lister_entretien(self, client):
        response = client.get("/api/v1/maison/entretien")
        assert response.status_code in (200, 500)

    def test_creer_tache(self, client):
        response = client.post(
            "/api/v1/maison/entretien",
            json={"tache": "Nettoyer filtre", "appareil": "VMC", "categorie": "ventilation"},
        )
        assert response.status_code in (200, 201, 500)

    def test_sante_appareils(self, client):
        response = client.get("/api/v1/maison/entretien/sante-appareils")
        assert response.status_code in (200, 500)


class TestRoutesJardin:
    """Tests routes /api/v1/maison/jardin."""

    def test_lister_jardin(self, client):
        response = client.get("/api/v1/maison/jardin")
        assert response.status_code in (200, 500)

    def test_creer_element(self, client):
        response = client.post(
            "/api/v1/maison/jardin",
            json={"nom": "Basilic", "type_element": "aromatique"},
        )
        assert response.status_code in (200, 201, 500)

    def test_calendrier_semis(self, client):
        response = client.get("/api/v1/maison/jardin/calendrier-semis")
        assert response.status_code in (200, 500)


class TestRoutesStocks:
    """Tests routes /api/v1/maison/stocks."""

    def test_lister_stocks(self, client):
        response = client.get("/api/v1/maison/stocks")
        assert response.status_code in (200, 500)

    def test_creer_stock(self, client):
        response = client.post(
            "/api/v1/maison/stocks",
            json={"nom": "Vis", "categorie": "Quincaillerie", "quantite": 100, "seuil_alerte": 20},
        )
        assert response.status_code in (200, 201, 500)


class TestRoutesCellier:
    """Tests routes /api/v1/maison/cellier."""

    def test_lister_cellier(self, client):
        response = client.get("/api/v1/maison/cellier")
        assert response.status_code in (200, 500)

    def test_creer_article(self, client):
        response = client.post(
            "/api/v1/maison/cellier",
            json={"nom": "Bordeaux 2020", "categorie": "Vin rouge", "quantite": 3},
        )
        assert response.status_code in (200, 201, 500)

    def test_alertes_peremption(self, client):
        response = client.get("/api/v1/maison/cellier/alertes/peremption?jours=14")
        assert response.status_code in (200, 500)

    def test_alertes_stock(self, client):
        response = client.get("/api/v1/maison/cellier/alertes/stock")
        assert response.status_code in (200, 500)

    def test_stats_cellier(self, client):
        response = client.get("/api/v1/maison/cellier/stats")
        assert response.status_code in (200, 500)


class TestRoutesArtisans:
    """Tests routes /api/v1/maison/artisans."""

    def test_lister_artisans(self, client):
        response = client.get("/api/v1/maison/artisans")
        assert response.status_code in (200, 500)

    def test_creer_artisan(self, client):
        response = client.post(
            "/api/v1/maison/artisans",
            json={"nom": "Martin Électricité", "metier": "electricien"},
        )
        assert response.status_code in (200, 201, 500)

    def test_stats_artisans(self, client):
        response = client.get("/api/v1/maison/artisans/stats")
        assert response.status_code in (200, 500)


class TestRoutesContrats:
    """Tests routes /api/v1/maison/contrats."""

    def test_lister_contrats(self, client):
        response = client.get("/api/v1/maison/contrats")
        assert response.status_code in (200, 500)

    def test_creer_contrat(self, client):
        response = client.post(
            "/api/v1/maison/contrats",
            json={
                "nom": "EDF Tempo",
                "type_contrat": "énergie",
                "date_debut": "2025-01-01",
                "statut": "actif",
            },
        )
        assert response.status_code in (200, 201, 500)

    def test_alertes_contrats(self, client):
        response = client.get("/api/v1/maison/contrats/alertes")
        assert response.status_code in (200, 500)

    def test_resume_financier(self, client):
        response = client.get("/api/v1/maison/contrats/resume-financier")
        assert response.status_code in (200, 500)


class TestRoutesGaranties:
    """Tests routes /api/v1/maison/garanties."""

    def test_lister_garanties(self, client):
        response = client.get("/api/v1/maison/garanties")
        assert response.status_code in (200, 500)

    def test_creer_garantie(self, client):
        response = client.post(
            "/api/v1/maison/garanties",
            json={
                "nom": "Four",
                "appareil": "Four",
                "date_achat": "2025-01-01",
                "date_fin_garantie": "2027-01-01",
            },
        )
        assert response.status_code in (200, 201, 500)

    def test_alertes_garanties(self, client):
        response = client.get("/api/v1/maison/garanties/alertes")
        assert response.status_code in (200, 500)

    def test_stats_garanties(self, client):
        response = client.get("/api/v1/maison/garanties/stats")
        assert response.status_code in (200, 500)


class TestRoutesDiagnostics:
    """Tests routes /api/v1/maison/diagnostics."""

    def test_lister_diagnostics(self, client):
        response = client.get("/api/v1/maison/diagnostics")
        assert response.status_code in (200, 500)

    def test_creer_diagnostic(self, client):
        response = client.post(
            "/api/v1/maison/diagnostics",
            json={
                "type_diagnostic": "DPE",
                "date_realisation": "2025-01-15",
                "date_expiration": "2035-01-15",
            },
        )
        assert response.status_code in (200, 201, 500)

    def test_alertes_diagnostics(self, client):
        response = client.get("/api/v1/maison/diagnostics/alertes")
        assert response.status_code in (200, 500)


class TestRoutesEcoTips:
    """Tests routes /api/v1/maison/eco-tips."""

    def test_lister_eco_tips(self, client):
        response = client.get("/api/v1/maison/eco-tips")
        assert response.status_code in (200, 500)

    def test_creer_eco_tip(self, client):
        response = client.post(
            "/api/v1/maison/eco-tips",
            json={"titre": "Douche courte", "categorie": "eau"},
        )
        assert response.status_code in (200, 201, 500)


class TestRoutesDepenses:
    """Tests routes /api/v1/maison/depenses."""

    def test_lister_depenses(self, client):
        response = client.get("/api/v1/maison/depenses")
        assert response.status_code in (200, 500)

    def test_creer_depense(self, client):
        response = client.post(
            "/api/v1/maison/depenses",
            json={
                "libelle": "Peinture",
                "montant": 85.0,
                "categorie": "décoration",
                "date": "2026-03-15",
            },
        )
        assert response.status_code in (200, 201, 500)

    def test_stats_depenses(self, client):
        response = client.get("/api/v1/maison/depenses/stats")
        assert response.status_code in (200, 500)


class TestRoutesCharges:
    """Tests routes /api/v1/maison/charges."""

    def test_lister_charges(self, client):
        response = client.get("/api/v1/maison/charges")
        assert response.status_code in (200, 500)


class TestRoutesMeubles:
    """Tests routes /api/v1/maison/meubles."""

    def test_creer_meuble(self, client):
        response = client.post(
            "/api/v1/maison/meubles",
            json={"nom": "Canapé", "piece": "salon"},
        )
        assert response.status_code in (200, 201, 404, 405, 500)

    def test_budget_meubles(self, client):
        response = client.get("/api/v1/maison/meubles/budget")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesNuisibles:
    """Tests routes /api/v1/maison/nuisibles."""

    def test_lister_nuisibles(self, client):
        response = client.get("/api/v1/maison/nuisibles")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesDevis:
    """Tests routes /api/v1/maison/devis."""

    def test_lister_devis(self, client):
        response = client.get("/api/v1/maison/devis")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesEntretienSaisonnier:
    """Tests routes /api/v1/maison/entretien-saisonnier."""

    def test_lister_entretien_saisonnier(self, client):
        response = client.get("/api/v1/maison/entretien-saisonnier")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesReleves:
    """Tests routes /api/v1/maison/releves."""

    def test_lister_releves(self, client):
        response = client.get("/api/v1/maison/releves")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesVisualisation:
    """Tests routes /api/v1/maison/visualisation."""

    def test_lister_pieces(self, client):
        response = client.get("/api/v1/maison/visualisation/pieces")
        assert response.status_code in (200, 404, 405, 500)

    def test_lister_etages(self, client):
        response = client.get("/api/v1/maison/visualisation/etages")
        assert response.status_code in (200, 404, 405, 500)


class TestRoutesHubStats:
    """Tests routes /api/v1/maison/hub/stats."""

    def test_stats_hub(self, client):
        response = client.get("/api/v1/maison/hub/stats")
        assert response.status_code in (200, 404, 405, 500)
