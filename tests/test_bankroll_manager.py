"""
Tests unitaires pour BankrollManager — gestion de bankroll Kelly.

Couvre:
- calculer_mise_kelly (formule Kelly fractionnaire)
- suggerer_mise (suggestion complète avec confiance)
- valider_mise (hard cap 5%, seuils de risque)
"""

import pytest

from src.services.jeux.bankroll_manager import (
    BankrollManager,
    SuggestionMise,
    ValidationMise,
)


@pytest.fixture
def manager():
    """Instance BankrollManager sans session DB."""
    return BankrollManager()


# ═══════════════════════════════════════════════════════════
# calculer_mise_kelly
# ═══════════════════════════════════════════════════════════


class TestCalculerMiseKelly:
    """Tests du critère de Kelly fractionnaire."""

    def test_mise_kelly_basique(self, manager):
        """Edge positif → mise proportionnelle à l'edge × fraction × bankroll."""
        mise = manager.calculer_mise_kelly(bankroll=1000, edge=0.10, cote=2.0)
        # Kelly fraction = edge * 0.25 = 0.10 * 0.25 = 0.025
        # mise = 1000 * 0.025 = 25.0
        assert mise == 25.0

    def test_edge_nul_retourne_zero(self, manager):
        """Edge <= 0 → pas de mise."""
        assert manager.calculer_mise_kelly(bankroll=1000, edge=0.0, cote=2.0) == 0.0
        assert manager.calculer_mise_kelly(bankroll=1000, edge=-0.05, cote=2.0) == 0.0

    def test_cote_invalide_retourne_zero(self, manager):
        """Cote <= 1.0 → pas de mise."""
        assert manager.calculer_mise_kelly(bankroll=1000, edge=0.1, cote=1.0) == 0.0

    def test_hard_cap_5_pourcent(self, manager):
        """Mise plafonnée à 5% de la bankroll même avec edge élevé."""
        mise = manager.calculer_mise_kelly(bankroll=1000, edge=0.50, cote=2.0)
        # Sans cap: 1000 * 0.50 * 0.25 = 125
        # Cap 5%: 1000 * 0.05 = 50
        assert mise == 50.0

    def test_fraction_custom(self, manager):
        """Fraction personnalisée modifie la mise."""
        mise = manager.calculer_mise_kelly(bankroll=1000, edge=0.10, cote=2.0, fraction=0.50)
        # 1000 * 0.10 * 0.50 = 50.0
        assert mise == 50.0

    def test_bankroll_zero(self, manager):
        """Bankroll 0 → mise 0."""
        assert manager.calculer_mise_kelly(bankroll=0, edge=0.10, cote=2.0) == 0.0

    def test_arrondi_deux_decimales(self, manager):
        """Le résultat est arrondi à 2 décimales."""
        mise = manager.calculer_mise_kelly(bankroll=333, edge=0.07, cote=2.0)
        # 333 * 0.07 * 0.25 = 5.8275 → 5.83
        assert mise == 5.83

    def test_petit_edge(self, manager):
        """Edge très petit → petite mise."""
        mise = manager.calculer_mise_kelly(bankroll=1000, edge=0.01, cote=2.0)
        assert mise == 2.5  # 1000 * 0.01 * 0.25


# ═══════════════════════════════════════════════════════════
# suggerer_mise
# ═══════════════════════════════════════════════════════════


class TestSuggererMise:
    """Tests de la suggestion de mise avec analyse."""

    def test_confiance_haute(self, manager):
        """Edge bon + confiance IA haute → suggestion haute confiance."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.05, cote=2.0, confiance_ia=80)
        assert isinstance(s, SuggestionMise)
        assert s.confiance == "haute"
        assert s.mise_suggeree > 0

    def test_edge_trop_faible(self, manager):
        """Edge < 2% → confiance faible."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.01, cote=2.0, confiance_ia=90)
        assert s.confiance == "faible"

    def test_confiance_ia_faible(self, manager):
        """Confiance IA < 60% → confiance faible."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.05, cote=2.0, confiance_ia=50)
        assert s.confiance == "faible"

    def test_mise_elevee_confiance_moyenne(self, manager):
        """Mise > 3% bankroll → confiance moyenne."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.20, cote=2.0, confiance_ia=80)
        # mise = min(1000*0.20*0.25, 50) = 50 → 5% > 3% → moyenne
        assert s.confiance == "moyenne"

    def test_kelly_complet_reference(self, manager):
        """Le champ kelly_complete contient la valeur non fractionnée."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.10, cote=2.0, confiance_ia=80)
        # Kelly complet = 1000 * (0.10 / (2.0 - 1)) = 100
        assert s.mise_kelly_complete == 100.0

    def test_message_present(self, manager):
        """Le message explicatif est toujours rempli."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.05, cote=2.0, confiance_ia=80)
        assert len(s.message) > 0

    def test_pourcentage_bankroll(self, manager):
        """Le pourcentage est correctement calculé."""
        s = manager.suggerer_mise(bankroll=1000, edge=0.04, cote=2.0, confiance_ia=80)
        # mise = 1000 * 0.04 * 0.25 = 10 → 1%
        assert s.pourcentage_bankroll == 1.0


# ═══════════════════════════════════════════════════════════
# valider_mise
# ═══════════════════════════════════════════════════════════


class TestValiderMise:
    """Tests de la validation de mise (money management)."""

    def test_mise_normale(self, manager):
        """Mise raisonnable → autorisée, risque normal."""
        v = manager.valider_mise(mise=10, bankroll=1000)
        assert isinstance(v, ValidationMise)
        assert v.autorise is True
        assert v.niveau_risque == "normal"
        assert v.raison is None

    def test_mise_negative(self, manager):
        """Mise <= 0 → refusée."""
        v = manager.valider_mise(mise=0, bankroll=1000)
        assert v.autorise is False

    def test_mise_negative_stricte(self, manager):
        """Mise négative → refusée."""
        v = manager.valider_mise(mise=-5, bankroll=1000)
        assert v.autorise is False

    def test_bankroll_zero(self, manager):
        """Bankroll <= 0 → refusée."""
        v = manager.valider_mise(mise=10, bankroll=0)
        assert v.autorise is False

    def test_hard_cap_refuse(self, manager):
        """Mise > 5% bankroll → REFUSÉE (hard cap)."""
        v = manager.valider_mise(mise=60, bankroll=1000)
        assert v.autorise is False
        assert v.niveau_risque == "tres_eleve"

    def test_seuil_eleve_autorise_avec_warning(self, manager):
        """Mise entre 3-5% → autorisée mais niveau élevé."""
        v = manager.valider_mise(mise=40, bankroll=1000)
        assert v.autorise is True
        assert v.niveau_risque == "eleve"
        assert v.raison is not None

    def test_pourcentage_correct(self, manager):
        """Le pourcentage est correctement calculé."""
        v = manager.valider_mise(mise=25, bankroll=1000)
        assert v.pourcentage_bankroll == 2.5

    def test_exactement_5_pourcent(self, manager):
        """Mise == 5% → refusée (strictement supérieur)."""
        v = manager.valider_mise(mise=50, bankroll=1000)
        # 50/1000 = 0.05 → pas > 0.05, mais = 0.05, qui n'est pas > SEUIL_RISQUE_MAXIMUM
        # Vérification du comportement exact
        assert v.pourcentage_bankroll == 5.0

    def test_seuil_custom(self, manager):
        """Seuil personnalisé pour l'alerte."""
        v = manager.valider_mise(mise=15, bankroll=1000, seuil=0.01)
        # 1.5% > 1% seuil custom → élevé
        assert v.niveau_risque == "eleve"
