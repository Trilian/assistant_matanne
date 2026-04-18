"""
Tests pour les améliorations du prompt de génération IA (Phases 3-5).

Phase 3: Injection légumes/fruits de saison, cohérence féculents
Phase 4: Cuisines du monde, diversité protéines
Phase 5: Adaptations Jules (section prompt)

Stratégie : on capture le prompt construit par generer_planning_ia
en mockant call_with_list_parsing_sync, puis on vérifie que les
sections attendues sont présentes.
"""

import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.cuisine.planning import ServicePlanning
from src.services.cuisine.planning.types import JourPlanning


@pytest.fixture
def service():
    """ServicePlanning avec client IA mocké."""
    with patch("src.services.cuisine.planning.service.obtenir_client_ia"):
        return ServicePlanning()


@pytest.fixture
def mock_db():
    """Session DB mockée."""
    mock = MagicMock()
    mock.add = MagicMock()
    mock.flush = MagicMock()
    mock.commit = MagicMock()
    mock.refresh = MagicMock()
    return mock


@pytest.fixture
def sept_jours_ia():
    """Retour IA minimal de 7 jours (pour que la génération complète ne plante pas)."""
    return [
        JourPlanning(jour=j, dejeuner="Plat déjeuner", diner="Plat dîner")
        for j in ["Lundi01", "Mardi02", "Mercredi", "Jeudi04", "Vendredi", "Samedi06", "Dimanche"]
    ]


def _capturer_prompt(service, mock_db, sept_jours_ia, preferences):
    """Appelle generer_planning_ia et retourne le prompt envoyé à l'IA."""
    prompt_capture = {}

    original_call = service.call_with_list_parsing_sync

    def capture_call(*, prompt, **kwargs):
        prompt_capture["prompt"] = prompt
        return sept_jours_ia

    with (
        patch.object(service, "call_with_list_parsing_sync", side_effect=capture_call),
        patch("src.services.cuisine.planning.service.Cache"),
    ):
        service.generer_planning_ia(
            semaine_debut=date(2026, 4, 13),
            preferences=preferences,
            db=mock_db,
        )

    return prompt_capture.get("prompt", "")


# ═══════════════════════════════════════════════════════════
# PHASE 3 — Injection légumes/fruits de saison
# ═══════════════════════════════════════════════════════════


class TestInjectionSaison:
    """Vérifie que les produits de saison sont injectés dans le prompt."""

    def test_legumes_saison_injectes_automatiquement(self, service, mock_db, sept_jours_ia):
        """Quand legumes_souhaites est vide, les légumes de saison d'avril sont injectés."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        # Avril => Asperge, Petit pois, Radis sont de saison (mois 4)
        assert "LÉGUMES DE SAISON" in prompt
        assert "AVRIL" in prompt
        assert "Asperge" in prompt
        assert "Petit pois" in prompt
        assert "Radis" in prompt

    def test_legumes_saison_non_injectes_si_legumes_souhaites(
        self, service, mock_db, sept_jours_ia
    ):
        """Quand l'utilisateur spécifie ses légumes, pas d'injection automatique."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"legumes_souhaites": ["Courgette", "Tomate"]},
        )

        # L'injection automatique ne doit pas se faire
        assert "LÉGUMES DE SAISON" not in prompt
        # Mais les légumes manuels sont présents
        assert "Courgette" in prompt
        assert "Tomate" in prompt

    def test_fruits_saison_injectes(self, service, mock_db, sept_jours_ia):
        """Les fruits de saison sont aussi injectés en avril."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        # Avril => Fraise est de saison (mois 4)
        assert "FRUITS DE SAISON" in prompt
        assert "Fraise" in prompt

    def test_saison_actuelle_dans_prompt(self, service, mock_db, sept_jours_ia):
        """La saison actuelle est indiquée pour guider les plats."""
        prompt = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"saison_actuelle": "printemps"}
        )

        assert "SAISON ACTUELLE : PRINTEMPS" in prompt

    def test_legumes_hors_saison_non_presents(self, service, mock_db, sept_jours_ia):
        """Les légumes hors saison en avril ne sont pas dans la liste de saison."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        # Tomate = mois [6,7,8,9,10] — pas en avril
        # Vérifier que Tomate n'est PAS dans la section "LÉGUMES DE SAISON"
        idx = prompt.find("LÉGUMES DE SAISON")
        if idx >= 0:
            # Prendre la section jusqu'à la prochaine section majeure
            section_fin = prompt.find("\n\n", idx + 1)
            if section_fin < 0:
                section_fin = idx + 500
            section_saison = prompt[idx:section_fin]
            assert "Tomate" not in section_saison


# ═══════════════════════════════════════════════════════════
# PHASE 3 — Cohérence féculents (Rule 18)
# ═══════════════════════════════════════════════════════════


class TestCoherenceFeculents:
    """Vérifie que les règles de cohérence féculents sont dans le prompt."""

    def test_rule_18_feculents_presente(self, service, mock_db, sept_jours_ia):
        """Le prompt contient la Rule 18 sur les féculents cohérents."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "FÉCULENTS" in prompt
        # Vérifier que des exemples de cohérence sont présents
        assert "semoule" in prompt.lower() or "couscous" in prompt.lower()
        assert "riz" in prompt.lower()

    def test_feculents_souhaites_dans_prompt(self, service, mock_db, sept_jours_ia):
        """Les féculents souhaités par l'utilisateur sont injectés."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"feculents_souhaites": ["Pâtes complètes", "Riz basmati"]},
        )

        assert "Pâtes complètes" in prompt
        assert "Riz basmati" in prompt
        assert "FÉCULENTS À PRIVILÉGIER" in prompt


# ═══════════════════════════════════════════════════════════
# PHASE 4 — Cuisines du monde
# ═══════════════════════════════════════════════════════════


class TestCuisinesDuMonde:
    """Vérifie l'injection des cuisines du monde dans le prompt."""

    def test_cuisines_souhaitees_dans_prompt(self, service, mock_db, sept_jours_ia):
        """Quand cuisines_souhaitees est rempli, la section apparaît."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"cuisines_souhaitees": ["Italien", "Japonais"]},
        )

        assert "CUISINES DU MONDE" in prompt
        assert "Italien" in prompt
        assert "Japonais" in prompt

    def test_cuisine_italienne_exemples(self, service, mock_db, sept_jours_ia):
        """La cuisine italienne inclut des exemples de plats."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"cuisines_souhaitees": ["Italien"]},
        )

        assert "risotto" in prompt.lower() or "osso buco" in prompt.lower()

    def test_cuisine_mexicaine_exemples(self, service, mock_db, sept_jours_ia):
        """La cuisine mexicaine inclut des exemples de plats."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"cuisines_souhaitees": ["Mexicain"]},
        )

        assert "fajitas" in prompt.lower() or "tacos" in prompt.lower()

    def test_pas_de_section_cuisines_si_vide(self, service, mock_db, sept_jours_ia):
        """Sans cuisines_souhaitees, la section n'apparaît pas."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "CUISINES DU MONDE À INTÉGRER" not in prompt

    def test_minimum_repas_cuisine(self, service, mock_db, sept_jours_ia):
        """La section demande 2-3 repas minimum d'inspiration."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"cuisines_souhaitees": ["Espagnol"]},
        )

        assert "2-3 repas" in prompt or "au moins 2" in prompt.lower()

    def test_cuisines_regionales_francaises(self, service, mock_db, sept_jours_ia):
        """Les cuisines régionales françaises sont supportées."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"cuisines_souhaitees": ["Breton"]},
        )

        assert "galettes" in prompt.lower() or "crêpes" in prompt.lower()


# ═══════════════════════════════════════════════════════════
# PHASE 4 — Diversité protéines
# ═══════════════════════════════════════════════════════════


class TestDiversiteProteines:
    """Vérifie que le prompt encourage la diversité protéique."""

    def test_oms_section_presente(self, service, mock_db, sept_jours_ia):
        """La section OMS/PNNS est dans le prompt."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "ÉQUILIBRE NUTRITIONNEL HEBDOMADAIRE" in prompt
        assert "PNNS" in prompt or "OMS" in prompt

    def test_variete_volaille(self, service, mock_db, sept_jours_ia):
        """Le prompt mentionne la diversité des volailles."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "Canard" in prompt
        assert "Dinde" in prompt
        assert "Pintade" in prompt

    def test_plats_plaisir_limites(self, service, mock_db, sept_jours_ia):
        """Le prompt mentionne les plats plaisir/pratique avec un max."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "PLAISIR" in prompt or "plaisir" in prompt
        assert "maximum 1 repas" in prompt.lower() or "max 1" in prompt.lower()

    def test_viande_rouge_configurable(self, service, mock_db, sept_jours_ia):
        """Le max viande rouge est paramétrable via les préférences."""
        prompt = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"viande_rouge_max": 3}
        )

        assert "maximum 3 repas" in prompt

    def test_poisson_blanc_configurable(self, service, mock_db, sept_jours_ia):
        """Le nombre de poissons blancs est paramétrable."""
        prompt = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"nb_poisson_blanc": 2}
        )

        assert "exactement 2 repas" in prompt.lower() or "POISSON BLANC : exactement 2" in prompt

    def test_vegetarien_configurable(self, service, mock_db, sept_jours_ia):
        """Le minimum végétarien est paramétrable."""
        prompt = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"nb_vegetarien": 3}
        )

        assert "Minimum 3 repas VÉGÉTARIEN" in prompt

    def test_charcuterie_limitee(self, service, mock_db, sept_jours_ia):
        """La charcuterie est limitée dans le prompt."""
        prompt = _capturer_prompt(service, mock_db, sept_jours_ia, {})

        assert "CHARCUTERIE" in prompt
        assert "150 g" in prompt


# ═══════════════════════════════════════════════════════════
# PHASE 5 — Adaptations Jules dans le prompt
# ═══════════════════════════════════════════════════════════


class TestAdaptationsJules:
    """Vérifie la section Jules dans le prompt."""

    def test_jules_present_dans_prompt(self, service, mock_db, sept_jours_ia):
        """Quand jules_present=True, la section Jules apparaît."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 24},
        )

        assert "JULES" in prompt
        assert "24 mois" in prompt

    def test_jules_absent_pas_de_section(self, service, mock_db, sept_jours_ia):
        """Quand jules_present=False, pas de section Jules."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": False},
        )

        # La section Jules ne doit pas être là
        assert "JULES (" not in prompt

    def test_jules_plats_adaptables_priorises(self, service, mock_db, sept_jours_ia):
        """Le prompt priorise les plats naturellement adaptables pour Jules."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 20},
        )

        assert "PRIORISER" in prompt
        assert "mijotés" in prompt or "gratins" in prompt or "soupes" in prompt

    def test_jules_poisson_cru_interdit(self, service, mock_db, sept_jours_ia):
        """Le prompt interdit le poisson cru quand Jules est présent."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 20},
        )

        assert "POISSON CRU INTERDIT" in prompt

    def test_jules_plat_jules_champs(self, service, mock_db, sept_jours_ia):
        """Le prompt décrit les champs plat_jules pour adaptations."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 20},
        )

        assert "plat_jules" in prompt
        assert "mixer" in prompt.lower() or "couper petit" in prompt.lower()

    def test_jules_noms_simples_sans_parentheses(self, service, mock_db, sept_jours_ia):
        """Le prompt exige des noms de plats simples sans parenthèses pour Jules."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 20},
        )

        assert "JAMAIS" in prompt
        assert "parenthèses" in prompt.lower() or "(sans sel)" in prompt

    def test_jules_eviter_fritures(self, service, mock_db, sept_jours_ia):
        """Le prompt demande d'éviter les fritures avec Jules."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {"jules_present": True, "jules_age_mois": 20},
        )

        assert "fritures" in prompt.lower() or "ÉVITER" in prompt


# ═══════════════════════════════════════════════════════════
# VALIDATION CROISÉE — Combinaison de features
# ═══════════════════════════════════════════════════════════


class TestCombinaisonFeatures:
    """Vérifie que toutes les features fonctionnent ensemble."""

    def test_toutes_sections_presentes(self, service, mock_db, sept_jours_ia):
        """Un prompt complet contient toutes les sections attendues."""
        prompt = _capturer_prompt(
            service,
            mock_db,
            sept_jours_ia,
            {
                "cuisines_souhaitees": ["Italien"],
                "jules_present": True,
                "jules_age_mois": 22,
                "saison_actuelle": "printemps",
                "nb_poisson_blanc": 1,
                "nb_poisson_gras": 1,
                "viande_rouge_max": 2,
                "nb_vegetarien": 2,
            },
        )

        # Toutes les sections majeures
        assert "CUISINES DU MONDE" in prompt
        assert "JULES" in prompt
        assert "SAISON ACTUELLE" in prompt
        assert "LÉGUMES DE SAISON" in prompt
        assert "ÉQUILIBRE NUTRITIONNEL" in prompt

    def test_restes_section_configurable(self, service, mock_db, sept_jours_ia):
        """La stratégie restes est présente quand autorisée."""
        prompt_avec = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"autoriser_restes": True}
        )
        prompt_sans = _capturer_prompt(
            service, mock_db, sept_jours_ia, {"autoriser_restes": False}
        )

        assert "4 PORTIONS" in prompt_avec
        assert "4 PORTIONS" not in prompt_sans
        assert "préparation fraîche" in prompt_sans.lower()
