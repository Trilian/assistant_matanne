"""Mixin bridges cuisine — méthodes inter-modules liées à la cuisine."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db

if TYPE_CHECKING:
    pass


class CuisineBridgesMixin:
    """Bridges inter-modules liés à la cuisine (recettes, courses, planning, batch cooking)."""

    # ── B5.1: Récolte jardin → Suggestions recettes ────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def recolte_vers_recettes(self, element_nom: str, db: Session | None = None) -> list[dict]:
        """Cherche des recettes utilisant un ingrédient récolté au jardin."""
        from src.core.models.recettes import Ingredient, Recette

        recettes = (
            db.query(Recette)
            .join(Ingredient, Ingredient.recette_id == Recette.id)
            .filter(Ingredient.nom.ilike(f"%{element_nom}%"))
            .limit(10)
            .all()
        )

        return [
            {
                "id": r.id,
                "nom": r.nom,
                "description": r.description,
                "temps_total": r.temps_total,
            }
            for r in recettes
        ]

    # ── I1: Planning → Courses auto ────────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def generer_courses_auto_depuis_planning(
        self,
        planning_id: int,
        semaine_debut: date | str | None = None,
        db: Session | None = None,
    ) -> dict:
        """I1: génère automatiquement une liste de courses depuis un planning validé."""
        from sqlalchemy import func

        from src.core.models import (
            ArticleCourses,
            ArticleInventaire,
            Ingredient,
            ListeCourses,
            Planning,
        )
        from src.core.models.planning import Repas
        from src.core.models.recettes import RecetteIngredient

        planning = db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            return {}

        if isinstance(semaine_debut, str) and semaine_debut:
            try:
                semaine_ref = date.fromisoformat(semaine_debut)
            except ValueError:
                semaine_ref = planning.semaine_debut
        else:
            semaine_ref = semaine_debut or planning.semaine_debut

        nom_liste = f"Courses auto planning #{planning.id} ({semaine_ref.isoformat()})"
        liste = (
            db.query(ListeCourses)
            .filter(
                ListeCourses.nom == nom_liste,
                ListeCourses.archivee.is_(False),
            )
            .order_by(ListeCourses.id.desc())
            .first()
        )
        if liste is None:
            liste = ListeCourses(nom=nom_liste, archivee=False, etat="brouillon")
            db.add(liste)
            db.flush()

        repas_list = db.query(Repas).filter(Repas.planning_id == planning.id).all()
        recette_ids: set[int] = set()
        for repas in repas_list:
            for recette_id in (
                repas.recette_id,
                repas.entree_recette_id,
                repas.dessert_recette_id,
                repas.dessert_jules_recette_id,
            ):
                if recette_id:
                    recette_ids.add(recette_id)

        if not recette_ids:
            return {
                "planning_id": planning.id,
                "liste_id": liste.id,
                "nb_articles": 0,
                "articles_en_stock": 0,
                "message": "Aucune recette liée au planning validé.",
            }

        ingredients = (
            db.query(
                RecetteIngredient.ingredient_id,
                func.sum(RecetteIngredient.quantite).label("quantite_totale"),
                Ingredient.nom,
                Ingredient.categorie,
                Ingredient.unite,
            )
            .join(Ingredient, Ingredient.id == RecetteIngredient.ingredient_id)
            .filter(RecetteIngredient.recette_id.in_(recette_ids))
            .group_by(
                RecetteIngredient.ingredient_id,
                Ingredient.nom,
                Ingredient.categorie,
                Ingredient.unite,
            )
            .all()
        )

        nb_articles = 0
        articles_en_stock = 0

        for row in ingredients:
            quantite_voulue = float(row.quantite_totale or 1)
            inventaire = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == row.ingredient_id)
                .order_by(ArticleInventaire.quantite.desc())
                .first()
            )
            quantite_en_stock = float(getattr(inventaire, "quantite", 0) or 0)
            if quantite_en_stock >= quantite_voulue:
                articles_en_stock += 1
                continue

            quantite_a_acheter = max(0.1, quantite_voulue - quantite_en_stock)
            article = (
                db.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.ingredient_id == row.ingredient_id,
                    ArticleCourses.achete.is_(False),
                )
                .first()
            )

            if article:
                article.quantite_necessaire = (
                    float(article.quantite_necessaire or 0) + quantite_a_acheter
                )
                if not article.rayon_magasin:
                    article.rayon_magasin = row.categorie or "Autre"
                nb_articles += 1
                continue

            db.add(
                ArticleCourses(
                    liste_id=liste.id,
                    ingredient_id=row.ingredient_id,
                    quantite_necessaire=quantite_a_acheter,
                    rayon_magasin=row.categorie or "Autre",
                    priorite="moyenne",
                    suggere_par_ia=False,
                    notes=f"Ajout automatique depuis le planning #{planning.id}",
                )
            )
            nb_articles += 1

        db.commit()
        db.refresh(liste)

        return {
            "planning_id": planning.id,
            "liste_id": liste.id,
            "nom_liste": liste.nom,
            "nb_articles": nb_articles,
            "articles_en_stock": articles_en_stock,
            "semaine_debut": semaine_ref.isoformat() if semaine_ref else None,
            "message": f"{nb_articles} article(s) ajoutés à la liste auto.",
        }

    # ── I6: Batch cooking → Planning ───────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def pre_remplir_planning_depuis_batch(
        self,
        session_id: int,
        db: Session | None = None,
    ) -> dict:
        """I6: marque les repas du planning comme déjà préparés après un batch cooking."""
        from sqlalchemy import or_

        from src.core.models import SessionBatchCooking
        from src.core.models.planning import Repas

        session_batch = (
            db.query(SessionBatchCooking).filter(SessionBatchCooking.id == session_id).first()
        )
        if not session_batch:
            return {}

        recette_ids = [
            int(recette_id)
            for recette_id in (session_batch.recettes_selectionnees or [])
            if recette_id
        ]
        if not session_batch.planning_id or not recette_ids:
            return {
                "session_id": session_batch.id,
                "planning_id": session_batch.planning_id,
                "nb_repas_mis_a_jour": 0,
                "message": "Aucun repas à pré-remplir pour cette session.",
            }

        repas = (
            db.query(Repas)
            .filter(Repas.planning_id == session_batch.planning_id)
            .filter(
                or_(
                    Repas.recette_id.in_(recette_ids),
                    Repas.entree_recette_id.in_(recette_ids),
                    Repas.dessert_recette_id.in_(recette_ids),
                    Repas.dessert_jules_recette_id.in_(recette_ids),
                )
            )
            .all()
        )

        note_batch = (
            f"Préparé en batch le {(session_batch.date_session or date.today()).isoformat()}"
        )
        nb_mis_a_jour = 0
        for repas_item in repas:
            repas_item.prepare = True
            if note_batch not in (repas_item.notes or ""):
                repas_item.notes = (
                    note_batch if not repas_item.notes else f"{repas_item.notes}\n{note_batch}"
                )
            nb_mis_a_jour += 1

        db.commit()

        return {
            "session_id": session_batch.id,
            "planning_id": session_batch.planning_id,
            "nb_repas_mis_a_jour": nb_mis_a_jour,
            "message": f"{nb_mis_a_jour} repas pré-rempli(s) depuis le batch.",
        }

    # ── I10: Feedback recette → Suggestions ────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def appliquer_feedback_recette_sur_suggestions(
        self,
        recette_id: int,
        *,
        note: int | None = None,
        feedback: str | None = None,
        user_id: str | None = None,
        commentaire: str | None = None,
        db: Session | None = None,
    ) -> dict:
        """I10: convertit le feedback recette en signal exploitable pour les suggestions."""
        from src.core.models import Recette
        from src.core.models.user_preferences import RetourRecette

        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            return {}

        feedback_normalise = (feedback or "").strip().lower()
        if feedback_normalise not in {"like", "dislike", "neutral"}:
            if note is not None and int(note) <= 2:
                feedback_normalise = "dislike"
            elif note is not None and int(note) >= 4:
                feedback_normalise = "like"
            else:
                feedback_normalise = "neutral"

        utilisateur = user_id or "system"
        retour = (
            db.query(RetourRecette)
            .filter(RetourRecette.user_id == utilisateur, RetourRecette.recette_id == recette_id)
            .first()
        )
        if retour is None:
            retour = RetourRecette(
                user_id=utilisateur, recette_id=recette_id, feedback=feedback_normalise
            )
            db.add(retour)
        else:
            retour.feedback = feedback_normalise

        if note is not None:
            retour.contexte = f"note={int(note)}/5"
        if commentaire:
            retour.notes = commentaire[:1000]

        db.commit()

        poids = {"like": 2, "neutral": 0, "dislike": -3}[feedback_normalise]
        return {
            "recette_id": recette_id,
            "user_id": utilisateur,
            "feedback": feedback_normalise,
            "poids_suggestion": poids,
            "exclure_des_suggestions": feedback_normalise == "dislike",
        }

    # ── P3-A1: Terroir → Recettes régionales ───────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def terroir_vers_recettes(
        self, localisation: str | None = None, db: Session | None = None
    ) -> dict:
        """P3-A1: Suggère des recettes régionales basées sur la localisation du foyer."""
        from src.core.models.habitat_projet import CritereImmoHabitat
        from src.core.models.recettes import Recette

        region = localisation
        if not region:
            critere = (
                db.query(CritereImmoHabitat).filter(CritereImmoHabitat.actif.is_(True)).first()
            )
            if critere and critere.villes:
                region = (
                    critere.villes[0] if isinstance(critere.villes, list) else str(critere.villes)
                )
            elif critere and critere.departements:
                dep = (
                    critere.departements[0]
                    if isinstance(critere.departements, list)
                    else str(critere.departements)
                )
                region = dep

        if not region:
            region = "France"

        recettes = (
            db.query(Recette)
            .filter(
                Recette.categorie.ilike(f"%{region}%")
                | Recette.nom.ilike(f"%{region}%")
                | Recette.description.ilike(f"%{region}%")
            )
            .limit(10)
            .all()
        )

        recettes_liste = [
            {
                "id": r.id,
                "nom": r.nom,
                "categorie": r.categorie or "",
                "temps_preparation": r.temps_preparation,
            }
            for r in recettes
        ]

        return {
            "localisation": region,
            "region": region,
            "recettes_suggerees": recettes_liste,
            "nb_recettes": len(recettes_liste),
        }

    # ── P3-B3: Vérifier stock recette ──────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def verifier_stock_recette(self, recette_id: int, db: Session | None = None) -> dict:
        """P3-B3: Vérifie le stock pour une recette et retourne les manquants."""
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient, Recette, RecetteIngredient

        recette = db.query(Recette).filter(Recette.id == recette_id).first()
        if not recette:
            return {"recette_id": recette_id, "erreur": "Recette introuvable"}

        liens = (
            db.query(RecetteIngredient, Ingredient)
            .join(Ingredient, RecetteIngredient.ingredient_id == Ingredient.id)
            .filter(RecetteIngredient.recette_id == recette_id)
            .all()
        )

        ingredients_ok = []
        ingredients_manquants = []

        for lien, ing in liens:
            nom_normalise = (ing.nom or "").strip().lower()
            stock = (
                db.query(ArticleInventaire)
                .filter(ArticleInventaire.ingredient_id == ing.id)
                .first()
            )
            item = {"nom": ing.nom, "quantite_requise": lien.quantite, "unite": lien.unite}
            if stock and stock.quantite > 0:
                item["en_stock"] = True
                item["quantite_stock"] = float(stock.quantite)
                ingredients_ok.append(item)
            else:
                item["en_stock"] = False
                ingredients_manquants.append(item)

        nb_total = len(liens)
        nb_ok = len(ingredients_ok)
        taux = round((nb_ok / nb_total) * 100, 1) if nb_total > 0 else 0

        return {
            "recette_id": recette_id,
            "recette_nom": recette.nom,
            "ingredients_ok": ingredients_ok,
            "ingredients_manquants": ingredients_manquants,
            "taux_couverture": taux,
        }

    # ── E1: Planning repas ↔ Planning tâches maison ────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def detection_conflits_planning(
        self,
        nb_jours: int = 7,
        db: Session | None = None,
    ) -> dict:
        """E1: Détecte les conflits entre planning repas et tâches maison."""
        from datetime import timedelta

        from src.core.models.habitat import TacheEntretien
        from src.core.models.planning import Planning, Repas
        from src.core.models.recettes import Recette

        aujourd_hui = date.today()
        horizon = aujourd_hui + timedelta(days=nb_jours)

        planning = (
            db.query(Planning)
            .filter(
                Planning.semaine_debut <= horizon,
                Planning.semaine_fin >= aujourd_hui,
                Planning.statut == "actif",
            )
            .order_by(Planning.semaine_debut.desc())
            .first()
        )

        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois.between(aujourd_hui, horizon),
                TacheEntretien.fait.is_(False),
            )
            .all()
        )

        conflits = []
        suggestions = []

        if planning:
            repas_liste = db.query(Repas).filter(Repas.planning_id == planning.id).all()

            taches_par_date: dict[date, list[dict]] = {}
            for tache in taches:
                if tache.prochaine_fois:
                    d = tache.prochaine_fois
                    taches_par_date.setdefault(d, []).append(
                        {
                            "id": tache.id,
                            "nom": tache.nom,
                            "categorie": tache.categorie or "maison",
                            "priorite": tache.priorite if hasattr(tache, "priorite") else "normale",
                        }
                    )

            for repas in repas_liste:
                if not repas.date_repas:
                    continue
                repas_date = repas.date_repas
                if isinstance(repas_date, str):
                    try:
                        repas_date = date.fromisoformat(repas_date)
                    except ValueError:
                        continue

                if repas_date not in taches_par_date:
                    continue

                recette_id = repas.recette_id
                temps_total = None
                if recette_id:
                    recette = db.query(Recette).filter(Recette.id == recette_id).first()
                    if recette:
                        temps_total = recette.temps_total

                est_complexe = temps_total is not None and temps_total > 60

                taches_jour = taches_par_date[repas_date]
                conflit = {
                    "date": repas_date.isoformat(),
                    "repas": {
                        "id": repas.id,
                        "type_repas": repas.type_repas or "repas",
                        "recette_id": recette_id,
                        "temps_total": temps_total,
                        "complexe": est_complexe,
                    },
                    "taches_maison": taches_jour,
                    "niveau": "attention" if not est_complexe else "conflit",
                }
                conflits.append(conflit)

                if est_complexe:
                    suggestions.append(
                        f"🍽️ Le {repas_date.strftime('%d/%m')}: repas long ({temps_total} min) "
                        f"+ {len(taches_jour)} tâche(s) maison → préférer un repas rapide ou préparer en avance."
                    )

        nb_taches_libres = len(taches) - len({c["date"] for c in conflits})

        return {
            "periode": {"debut": aujourd_hui.isoformat(), "fin": horizon.isoformat()},
            "nb_conflits": len(conflits),
            "conflits": conflits,
            "suggestions": suggestions,
            "nb_taches_maison_periode": len(taches),
            "nb_taches_sans_conflit": nb_taches_libres,
            "planning_id": planning.id if planning else None,
        }

    # ── E3: Météo → Suggestions recettes ───────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def meteo_vers_recettes(
        self,
        conditions_meteo: dict,
        db: Session | None = None,
    ) -> dict:
        """E3: Suggère des recettes adaptées aux conditions météo."""
        from src.core.models.recettes import Recette

        temp = float(conditions_meteo.get("temperature", 15))
        pluie = float(conditions_meteo.get("precipitations_mm", 0))
        description = str(conditions_meteo.get("description", "")).lower()

        est_pluvieux = pluie > 5 or "pluie" in description or "rain" in description
        est_froid = temp < 12
        est_chaud = temp > 22
        est_tres_chaud = temp > 28

        if est_froid or est_pluvieux:
            mots_chauds = [
                "soupe",
                "potage",
                "gratin",
                "tajine",
                "pot-au-feu",
                "velouté",
                "ragoût",
                "daube",
                "blanquette",
                "mijoté",
            ]
            label_contexte = "Temps froid/pluvieux 🌧️"
            conseil = "Comfort food recommandé — repas chaud et réconfortant"
            emoji = "🍲"

            recettes = (
                db.query(Recette)
                .filter(
                    db.query(Recette)
                    .filter(
                        func.lower(Recette.nom).op("~")("|".join(mots_chauds))
                        | func.lower(Recette.description).op("~")("|".join(mots_chauds))
                        | func.lower(Recette.categorie).in_(["soupe", "plat chaud", "plat mijoté"])
                    )
                    .exists()
                )
                .filter(
                    func.lower(Recette.nom).op("~")("|".join(mots_chauds))
                    | func.lower(Recette.description).op("~")("|".join(mots_chauds))
                    | func.lower(Recette.categorie).in_(["soupe", "plat chaud", "plat mijoté"])
                )
                .limit(8)
                .all()
            )

            if not recettes:
                recettes = (
                    db.query(Recette)
                    .filter(
                        func.lower(Recette.categorie).in_(
                            ["soupe", "plat", "plat chaud", "entrée chaude"]
                        )
                    )
                    .limit(8)
                    .all()
                )
        elif est_tres_chaud:
            mots_frais = [
                "salade",
                "gazpacho",
                "taboulé",
                "carpaccio",
                "tartare",
                "ceviche",
                "wrap",
                "smoothie",
                "glace",
                "sorbet",
            ]
            label_contexte = "Grosse chaleur ☀️🔥"
            conseil = "Fraîcheur en priorité — pas de cuisson longue"
            emoji = "🥗"

            recettes = (
                db.query(Recette)
                .filter(
                    func.lower(Recette.nom).op("~")("|".join(mots_frais))
                    | func.lower(Recette.description).op("~")("|".join(mots_frais))
                    | func.lower(Recette.categorie).in_(
                        ["salade", "entrée froide", "dessert frais"]
                    )
                )
                .limit(8)
                .all()
            )

            if not recettes:
                recettes = (
                    db.query(Recette)
                    .filter(func.lower(Recette.categorie).in_(["salade", "entrée", "dessert"]))
                    .limit(8)
                    .all()
                )
        elif est_chaud:
            label_contexte = "Beau soleil ☀️"
            conseil = "Saison des repas légers et des grillades"
            emoji = "🌞"

            recettes = (
                db.query(Recette)
                .filter(
                    func.lower(Recette.type_repas).in_(["déjeuner", "dîner", "lunch"])
                    | func.lower(Recette.categorie).in_(["salade", "plat", "grillades"])
                )
                .limit(8)
                .all()
            )
        else:
            label_contexte = "Temps doux 🌤️"
            conseil = "Toutes recettes conviennent — faites-vous plaisir"
            emoji = "🍽️"
            recettes = db.query(Recette).order_by(Recette.id.desc()).limit(8).all()

        recettes_liste = [
            {
                "id": r.id,
                "nom": r.nom,
                "categorie": r.categorie or "",
                "type_repas": r.type_repas or "",
                "temps_total": r.temps_total,
            }
            for r in recettes
        ]

        return {
            "conditions_meteo": {
                "temperature": temp,
                "precipitations_mm": pluie,
                "description": conditions_meteo.get("description", ""),
                "label": label_contexte,
            },
            "conseil": conseil,
            "emoji": emoji,
            "recettes_suggerees": recettes_liste,
            "nb_recettes": len(recettes_liste),
        }
