"""Tests ciblés des bridges inter-modules.

Ces tests couvrent les bridges ajoutés ou fiabilisés pour :
- I1 Planning validé → Courses auto
- I5 Entretien terminé → mise à jour de la fiche d'entretien
- I6 Batch cooking terminé → pré-remplissage du planning
- I10 Feedback recette → pondération/exclusion des suggestions
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from sqlalchemy.orm import Session


def _creer_recette_avec_ingredient(test_db: Session, nom: str = "Recette bridge"):
    from src.core.models import Ingredient, Recette
    from src.core.models.recettes import RecetteIngredient

    recette = Recette(
        nom=nom,
        description="Recette de test bridge",
        temps_preparation=20,
        temps_cuisson=15,
        portions=4,
        difficulte="facile",
        type_repas="dîner",
        saison="toute_année",
        categorie="Plat",
        compatible_batch=True,
    )
    ingredient = Ingredient(nom=f"Ingrédient {nom}", categorie="Épicerie", unite="pcs")
    test_db.add_all([recette, ingredient])
    test_db.commit()

    lien = RecetteIngredient(
        recette_id=recette.id,
        ingredient_id=ingredient.id,
        quantite=2.0,
        unite="pcs",
    )
    test_db.add(lien)
    test_db.commit()
    test_db.refresh(recette)
    test_db.refresh(ingredient)
    return recette, ingredient


@pytest.mark.integration
def test_generer_courses_auto_depuis_planning_cree_une_liste(test_db: Session) -> None:
    from src.core.models import ListeCourses, Planning, Repas
    from src.services.ia.inter_modules import obtenir_service_bridges

    recette, ingredient = _creer_recette_avec_ingredient(test_db, nom="Chili express")
    lundi = date.today() - timedelta(days=date.today().weekday())
    planning = Planning(
        nom="Semaine test bridges",
        semaine_debut=lundi,
        semaine_fin=lundi + timedelta(days=6),
        etat="valide",
    )
    test_db.add(planning)
    test_db.commit()

    repas = Repas(
        planning_id=planning.id,
        recette_id=recette.id,
        date_repas=lundi,
        type_repas="dîner",
    )
    test_db.add(repas)
    test_db.commit()

    service = obtenir_service_bridges()
    resultat = service.generer_courses_auto_depuis_planning(
        planning_id=planning.id,
        semaine_debut=planning.semaine_debut,
        db=test_db,
    )

    assert resultat["planning_id"] == planning.id
    assert resultat["liste_id"] is not None
    assert resultat["nb_articles"] >= 1

    liste = test_db.query(ListeCourses).filter(ListeCourses.id == resultat["liste_id"]).first()
    assert liste is not None
    assert len(liste.articles) >= 1
    assert any(article.ingredient_id == ingredient.id for article in liste.articles)


@pytest.mark.integration
def test_entretien_termine_met_a_jour_la_fiche_associee(test_db: Session) -> None:
    from src.core.models.habitat import TacheEntretien
    from src.core.models.maison_extensions import EntretienSaisonnier
    from src.services.ia.inter_modules import obtenir_service_bridges

    fiche = EntretienSaisonnier(
        nom="Révision chaudière",
        categorie="chauffage",
        saison="hiver",
        frequence="annuel",
    )
    tache = TacheEntretien(
        nom="Révision chaudière",
        categorie="maintenance",
        prochaine_fois=date.today(),
        fait=True,
    )
    test_db.add_all([fiche, tache])
    test_db.commit()

    resultat = obtenir_service_bridges().synchroniser_entretien_termine_vers_fiche(
        tache_id=tache.id,
        db=test_db,
    )
    test_db.refresh(fiche)

    assert resultat["tache_id"] == tache.id
    assert resultat["nb_fiches_mises_a_jour"] >= 1
    assert fiche.date_derniere_realisation == date.today()


@pytest.mark.integration
def test_batch_termine_pre_remplit_les_repas_du_planning(test_db: Session) -> None:
    from src.core.models import Planning, Repas, SessionBatchCooking
    from src.services.ia.inter_modules import obtenir_service_bridges

    recette, _ = _creer_recette_avec_ingredient(test_db, nom="Lasagnes batch")
    lundi = date.today() - timedelta(days=date.today().weekday())
    planning = Planning(
        nom="Planning batch",
        semaine_debut=lundi,
        semaine_fin=lundi + timedelta(days=6),
        etat="valide",
    )
    test_db.add(planning)
    test_db.commit()

    repas = Repas(
        planning_id=planning.id,
        recette_id=recette.id,
        date_repas=lundi + timedelta(days=1),
        type_repas="déjeuner",
        prepare=False,
    )
    session_batch = SessionBatchCooking(
        nom="Batch dimanche",
        date_session=lundi,
        duree_estimee=120,
        statut="terminee",
        planning_id=planning.id,
        recettes_selectionnees=[recette.id],
        robots_utilises=["Cookeo"],
    )
    test_db.add_all([repas, session_batch])
    test_db.commit()

    resultat = obtenir_service_bridges().pre_remplir_planning_depuis_batch(
        session_id=session_batch.id,
        db=test_db,
    )
    test_db.refresh(repas)

    assert resultat["session_id"] == session_batch.id
    assert resultat["nb_repas_mis_a_jour"] >= 1
    assert repas.prepare is True
    assert "batch" in (repas.notes or "").lower()


@pytest.mark.integration
def test_feedback_note_basse_exclut_la_recette(test_db: Session) -> None:
    from src.core.models.user_preferences import RetourRecette
    from src.services.cuisine.inter_module_inventaire_planning import (
        obtenir_service_inventaire_planning_interaction,
    )
    from src.services.ia.flux_utilisateur import enregistrer_feedback_semaine

    recette, _ = _creer_recette_avec_ingredient(test_db, nom="Recette peu aimée")

    resultat = enregistrer_feedback_semaine(
        feedbacks=[
            {
                "recette_id": recette.id,
                "note": 1,
                "commentaire": "À ne pas reproposer",
                "mange": False,
                "user_id": "u-bridges",
            }
        ],
        db=test_db,
    )

    assert resultat["nb_feedbacks"] == 1

    retour = (
        test_db.query(RetourRecette)
        .filter(RetourRecette.recette_id == recette.id, RetourRecette.user_id == "u-bridges")
        .first()
    )
    assert retour is not None
    assert retour.feedback == "dislike"

    exclusions = obtenir_service_inventaire_planning_interaction().filtrer_recettes_mal_notees(
        seuil_note=3,
        user_id="u-bridges",
        db=test_db,
    )
    ids_exclus = {item["recette_id"] for item in exclusions["recettes_exclues"]}
    assert recette.id in ids_exclus
