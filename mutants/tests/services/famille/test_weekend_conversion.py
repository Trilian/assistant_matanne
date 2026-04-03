from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.models import ActiviteFamille, ActiviteWeekend
from src.services.famille.weekend import ServiceWeekend


def test_convertir_weekend_en_activite_famille(db: Session):
    service = ServiceWeekend()

    activite_weekend = ActiviteWeekend(
        titre="Sortie parc",
        type_activite="parc",
        date_prevue=date.today() + timedelta(days=2),
        duree_estimee_h=2.0,
        lieu="Parc municipal",
        participants=["Jules", "Anne"],
        cout_estime=0.0,
        statut="planifie",
    )
    db.add(activite_weekend)
    db.commit()
    db.refresh(activite_weekend)

    activite_famille_id = service.convertir_en_activite_famille(activite_weekend.id, db=db)

    assert activite_famille_id is not None
    creee = db.get(ActiviteFamille, activite_famille_id)
    assert creee is not None
    assert creee.titre == activite_weekend.titre
    assert creee.type_activite == activite_weekend.type_activite


def test_convertir_weekend_en_activite_famille_idempotent(db: Session):
    service = ServiceWeekend()

    activite_weekend = ActiviteWeekend(
        titre="Cinema famille",
        type_activite="cinema",
        date_prevue=date.today() + timedelta(days=3),
        duree_estimee_h=2.0,
        lieu="Cinema centre",
        participants=["Jules", "Mathieu"],
        cout_estime=12.0,
        statut="planifie",
    )
    db.add(activite_weekend)
    db.commit()
    db.refresh(activite_weekend)

    premier_id = service.convertir_en_activite_famille(activite_weekend.id, db=db)
    second_id = service.convertir_en_activite_famille(activite_weekend.id, db=db)

    assert premier_id == second_id


def test_convertir_weekend_en_activite_famille_introuvable(db: Session):
    service = ServiceWeekend()

    result = service.convertir_en_activite_famille(999999, db=db)

    assert result is None
