"""
Tests unitaires pour StatsPersonnellesService — ROI, win rate, patterns.

Utilise la fixture conftest `db` (SQLite in-memory) pour les tests avec session.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.services.jeux.stats_personnelles import StatsPersonnellesService


@pytest.fixture
def service():
    return StatsPersonnellesService()


@pytest.fixture
def paris_en_base(db):
    """Insère des paris de test dans la base SQLite."""
    from src.core.models.jeux import PariSportif, Equipe, Match

    # Créer équipes et match
    eq1 = Equipe(nom="PSG", championnat="Ligue 1")
    eq2 = Equipe(nom="OM", championnat="Ligue 1")
    db.add_all([eq1, eq2])
    db.flush()

    match = Match(
        equipe_domicile_id=eq1.id,
        equipe_exterieur_id=eq2.id,
        championnat="Ligue 1",
        date_match=datetime.now().date(),
    )
    db.add(match)
    db.flush()

    # Paris résolus
    paris = [
        PariSportif(
            match_id=match.id, type_pari="1N2", prediction="1",
            cote=1.8, mise=10, gain=18, statut="gagne",
            user_id=1, cree_le=datetime.now() - timedelta(days=5),
        ),
        PariSportif(
            match_id=match.id, type_pari="1N2", prediction="2",
            cote=2.5, mise=10, gain=0, statut="perdu",
            user_id=1, cree_le=datetime.now() - timedelta(days=3),
        ),
        PariSportif(
            match_id=match.id, type_pari="1N2", prediction="N",
            cote=3.0, mise=10, gain=30, statut="gagne",
            user_id=1, cree_le=datetime.now() - timedelta(days=1),
        ),
    ]
    db.add_all(paris)
    db.commit()
    return paris


class TestCalculerRoiGlobal:
    """Tests du calcul ROI global."""

    def test_roi_avec_paris(self, service, paris_en_base, db):
        """ROI calculé correctement à partir de paris gagnés/perdus."""
        with patch("src.services.jeux.stats_personnelles.get_bankroll_manager") as mock_bm:
            mock_manager = MagicMock()
            # ROI = (48-30)/30 * 100 = 60%
            mock_manager.calculer_roi.return_value = 60.0
            mock_bm.return_value = mock_manager

            result = service.calculer_roi_global(user_id=1, jours=30, session=db)

            assert result["gains_totaux"] == 48.0  # 18 + 30
            assert result["mises_totales"] == 30.0  # 10 * 3
            assert result["roi"] == 60.0
            assert result["nb_paris"] == 3

    def test_roi_sans_paris(self, service, db):
        """Pas de paris → ROI 0."""
        with patch("src.services.jeux.stats_personnelles.get_bankroll_manager") as mock_bm:
            mock_manager = MagicMock()
            mock_manager.calculer_roi.return_value = 0.0
            mock_bm.return_value = mock_manager

            result = service.calculer_roi_global(user_id=999, jours=30, session=db)
            assert result["roi"] == 0.0
            assert result["nb_paris"] == 0


class TestCalculerWinRate:
    """Tests du win rate."""

    def test_win_rate_avec_paris(self, service, paris_en_base, db):
        """Win rate = gagnés / total résolus."""
        result = service.calculer_win_rate(user_id=1, jours=30, session=db)

        assert result["nb_total"] == 3
        assert result["nb_gagnants"] == 2
        assert result["win_rate_global"] == pytest.approx(66.67, abs=0.1)
        assert result["win_rate_paris"] == pytest.approx(66.67, abs=0.1)

    def test_win_rate_sans_paris(self, service, db):
        """Pas de paris → win rate 0."""
        result = service.calculer_win_rate(user_id=999, jours=30, session=db)
        assert result["win_rate_global"] == 0.0
        assert result["nb_total"] == 0
