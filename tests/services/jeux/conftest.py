"""Fixtures pour tests jeux — création de données de test matchs/équipes."""

from datetime import date

import pytest

from src.core.models.jeux import Equipe, Match


def creer_match_test(session, match_id: int) -> Match:
    """Crée un match de test avec ses équipes si nécessaire.

    Retourne le match existant s'il est déjà en base.
    """
    existing = session.query(Match).filter(Match.id == match_id).first()
    if existing is not None:
        return existing

    equipe_dom_id = match_id * 10 + 1
    equipe_ext_id = match_id * 10 + 2

    for equipe_id, suffixe in ((equipe_dom_id, "DOM"), (equipe_ext_id, "EXT")):
        if not session.query(Equipe).filter(Equipe.id == equipe_id).first():
            session.add(
                Equipe(id=equipe_id, nom=f"Equipe {suffixe} {match_id}", championnat="Test")
            )

    session.flush()

    match = Match(
        id=match_id,
        equipe_domicile_id=equipe_dom_id,
        equipe_exterieur_id=equipe_ext_id,
        championnat="Test",
        date_match=date.today(),
        joue=False,
    )
    session.add(match)
    session.flush()
    return match
