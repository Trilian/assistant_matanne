"""
Test unitaire pour les fonctionnalités avancées jeux.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal


# -----------------------------------------------------------------------------
# PHASE T: Heatmap cotes bookmakers
# -----------------------------------------------------------------------------


def test_cote_historique_model():
    """Test creation modele CoteHistorique."""
    from src.core.models import CoteHistorique, Match, Equipe
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from src.core.models.base import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Creer equipes et match
        eq1 = Equipe(nom="PSG", championnat="Ligue 1")
        eq2 = Equipe(nom="Lyon", championnat="Ligue 1")
        session.add_all([eq1, eq2])
        session.flush()

        match = Match(
            equipe_domicile_id=eq1.id,
            equipe_exterieur_id=eq2.id,
            championnat="Ligue 1",
            date_match=datetime.now().date(),
        )
        session.add(match)
        session.flush()

        # Creer historique cotes
        cote1 = CoteHistorique(
            match_id=match.id,
            cote=1.85,
            marche="1",
            cote_domicile=1.85,
            cote_nul=3.40,
            cote_exterieur=4.20,
            bookmaker="betclic",
        )
        session.add(cote1)
        session.commit()

        # Verifier
        assert cote1.id is not None
        assert cote1.cote_domicile == 1.85
        assert cote1.bookmaker == "betclic"


# -----------------------------------------------------------------------------
# PHASE U: Generateur grilles IA & Analyse
# -----------------------------------------------------------------------------


def test_generer_grille_ia_ponderee():
    """Test generateur grilles IA pondere."""
    from src.services.jeux import obtenir_jeux_ai_service

    stats = {
        5: {"freq": 12, "ecart": 2, "dernier": "2026-03-20"},
        12: {"freq": 8, "ecart": 5, "dernier": "2026-03-15"},
        23: {"freq": 15, "ecart": 1, "dernier": "2026-03-25"},
        34: {"freq": 3, "ecart": 20, "dernier": "2026-01-10"},
        45: {"freq": 6, "ecart": 10, "dernier": "2026-02-15"},
    }

    service = obtenir_jeux_ai_service()
    grille = service.generer_grille_ia_ponderee(stats, mode="equilibre")

    assert "numeros" in grille
    assert "numero_chance" in grille
    assert "analyse" in grille
    assert "confiance" in grille

    assert len(grille["numeros"]) == 5
    assert all(1 <= n <= 49 for n in grille["numeros"])
    assert 1 <= grille["numero_chance"] <= 10
    assert 0 <= grille["confiance"] <= 1


def test_analyser_grille_joueur():
    """Test analyse grille joueur IA."""
    from src.services.jeux import obtenir_jeux_ai_service

    stats = {n: {"freq": 10, "ecart": 5} for n in range(1, 50)}

    service = obtenir_jeux_ai_service()
    analyse = service.analyser_grille_joueur(
        numeros=[5, 12, 23, 34, 45],
        numero_chance=7,
        stats_frequences=stats,
    )

    assert "note" in analyse
    assert "points_forts" in analyse
    assert "points_faibles" in analyse
    assert "recommandations" in analyse
    assert "appreciation" in analyse

    assert 0 <= analyse["note"] <= 10
    assert isinstance(analyse["points_forts"], list)
    assert isinstance(analyse["points_faibles"], list)


def test_valider_grille():
    """Test validation format grille."""
    from src.services.jeux._internal.ai_service import JeuxAIService

    service = JeuxAIService()

    # Grille valide
    assert service._valider_grille({
        "numeros": [5, 12, 23, 34, 45],
        "numero_chance": 7,
    }) == True

    # Pas assez de numeros
    assert service._valider_grille({
        "numeros": [5, 12, 23],
        "numero_chance": 7,
    }) == False

    # Doublons
    assert service._valider_grille({
        "numeros": [5, 5, 23, 34, 45],
        "numero_chance": 7,
    }) == False

    # Numero hors bornes
    assert service._valider_grille({
        "numeros": [5, 12, 23, 34, 55],
        "numero_chance": 7,
    }) == False


# -----------------------------------------------------------------------------
# PHASE W: Notifications Web Push resultats
# -----------------------------------------------------------------------------


def test_notifier_pari_gagne():
    """Test template notification pari gagne."""
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    service = obtenir_push_notification_service()
    
    # Mock envoyer_notification
    envois = []
    def mock_envoyer(user_id, notif):
        envois.append((user_id, notif))
        return True
    
    service.envoyer_notification = mock_envoyer

    result = service.notifier_pari_gagne(
        "user123",
        "PSG 3-1 Lyon",
        gain=25.50,
        cote=2.55,
    )

    assert result is True
    assert len(envois) == 1
    user_id, notif = envois[0]
    assert user_id == "user123"
    assert "🎉" in notif.title
    assert "25.50" in notif.body
    assert notif.notification_type.value == "jeux_pari_gagne"


def test_notifier_resultat_loto():
    """Test template notification resultat loto."""
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    service = obtenir_push_notification_service()
    
    envois = []
    def mock_envoyer(user_id, notif):
        envois.append((user_id, notif))
        return True
    
    service.envoyer_notification = mock_envoyer

    # Gain potentiel
    service.notifier_resultat_loto("user123", nb_numeros_trouves=4, chance_trouvee=True, gain=50.0)
    assert len(envois) == 1
    assert "🎰" in envois[0][1].title
    assert envois[0][1].notification_type.value == "jeux_loto_gain"

    # Resultat moyen
    envois.clear()
    service.notifier_resultat_loto("user123", nb_numeros_trouves=2, chance_trouvee=False)
    assert len(envois) == 1
    assert envois[0][1].notification_type.value == "jeux_loto_resultat"


def test_type_notification_enum():
    """Test ajout types notifications jeux."""
    from src.services.core.notifications.types import TypeNotification

    assert "RESULTAT_PARI_GAGNE" in TypeNotification.__members__
    assert "RESULTAT_PARI_PERDU" in TypeNotification.__members__
    assert "RESULTAT_LOTO" in TypeNotification.__members__
    assert "RESULTAT_LOTO_GAIN" in TypeNotification.__members__

    assert TypeNotification.RESULTAT_PARI_GAGNE.value == "jeux_pari_gagne"
    assert TypeNotification.RESULTAT_LOTO_GAIN.value == "jeux_loto_gain"


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_ai_client():
    """Mock ClientIA pour eviter appels Mistral reels."""
    from unittest.mock import MagicMock
    from src.core.ai import ClientIA

    client = MagicMock(spec=ClientIA)
    client.generer.return_value = '{"numeros": [5, 12, 23, 34, 45], "numero_chance": 7, "analyse": "Test", "confiance": 0.6}'
    return client

