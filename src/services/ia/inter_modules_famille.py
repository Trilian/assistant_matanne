"""Mixin bridges famille — méthodes inter-modules liées à la famille."""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db

if TYPE_CHECKING:
    pass


class FamilleBridgesMixin:
    """Bridges inter-modules liés à la famille (budget, documents, anniversaires, voyages)."""

    # ── B5.3: Documents expirés → Dashboard alerte ─────────

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def documents_expires_alertes(self, jours_avant: int = 30, db: Session | None = None) -> list[dict]:
        """Liste les documents qui expirent bientôt ou sont déjà expirés."""
        from src.core.models import DocumentFamille

        seuil = date.today() + timedelta(days=jours_avant)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.actif.is_(True),
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= seuil,
            )
            .order_by(DocumentFamille.date_expiration)
            .all()
        )

        return [
            {
                "id": d.id,
                "titre": d.titre,
                "categorie": d.categorie,
                "membre_famille": d.membre_famille,
                "date_expiration": str(d.date_expiration),
                "jours_restants": d.jours_avant_expiration,
                "est_expire": d.est_expire,
                "niveau": "critique" if d.est_expire else (
                    "urgent" if d.jours_avant_expiration and d.jours_avant_expiration <= 7 else "attention"
                ),
            }
            for d in documents
        ]

    # ── B5.2: Budget anomalie → Notification ────────────────

    def verifier_anomalies_budget_et_notifier(self) -> list[dict]:
        """Vérifie les anomalies budgétaires et émet des événements."""
        from src.services.ia.prevision_budget import obtenir_service_prevision_budget
        from src.services.core.events import obtenir_bus

        service = obtenir_service_prevision_budget()
        anomalies = service.detecter_anomalies_budget(seuil_pct=80)

        bus = obtenir_bus()
        for anomalie in anomalies:
            bus.emettre("budget.depassement", {
                "categorie": anomalie["categorie"],
                "depense": anomalie["depense"],
                "budget_ref": anomalie["budget_ref"],
                "pourcentage": anomalie["pourcentage"],
                "niveau": anomalie["niveau"],
            })

        return anomalies

    # ── B5.7: Anniversaire → Menu festif ────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def anniversaire_vers_menu_festif(
        self,
        jours_horizon: int = 14,
        db: Session | None = None,
    ) -> dict:
        """Suggère un menu festif pour l'anniversaire le plus proche."""
        from src.core.models import AnniversaireFamille
        from src.core.models.recettes import Recette

        anniversaires = sorted(
            [a for a in db.query(AnniversaireFamille).all() if 0 <= a.jours_restants <= jours_horizon],
            key=lambda anniversaire: anniversaire.jours_restants,
        )
        if not anniversaires:
            return {}

        cible = anniversaires[0]
        recettes = (
            db.query(Recette)
            .filter(
                func.lower(Recette.nom).contains("gateau")
                | func.lower(Recette.nom).contains("gâteau")
                | func.lower(Recette.nom).contains("tarte")
                | func.lower(Recette.categorie).contains("dessert")
            )
            .limit(6)
            .all()
        )

        suggestions = [
            {
                "id": recette.id,
                "nom": recette.nom,
                "categorie": recette.categorie,
                "type_repas": recette.type_repas,
                "temps_total": recette.temps_total,
            }
            for recette in recettes
        ]
        if not suggestions:
            suggestions = [
                {"id": None, "nom": "Gâteau maison festif", "categorie": "Dessert", "type_repas": "dessert", "temps_total": 90},
                {"id": None, "nom": "Buffet apéritif familial", "categorie": "Plat", "type_repas": "dîner", "temps_total": 45},
            ]

        return {
            "anniversaire": {
                "id": cible.id,
                "nom_personne": cible.nom_personne,
                "jours_restants": cible.jours_restants,
                "age": cible.age,
            },
            "menu_festif": suggestions,
        }

    # ── Jalon → Événement familial ─────────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def jalon_vers_evenement_familial(
        self,
        jalon_id: int,
        db: Session | None = None,
    ) -> dict:
        """Crée un événement familial à partir d'un jalon Jules."""
        from src.core.models.famille import EvenementFamilial, Jalon, ProfilEnfant

        jalon = db.query(Jalon).filter(Jalon.id == jalon_id).first()
        if not jalon:
            return {}

        enfant = db.query(ProfilEnfant).filter(ProfilEnfant.id == jalon.child_id).first()
        titre = f"Jalon Jules: {jalon.titre}"

        evenement = (
            db.query(EvenementFamilial)
            .filter(
                EvenementFamilial.titre == titre,
                EvenementFamilial.date_evenement == jalon.date_atteint,
                EvenementFamilial.type_evenement == "jalon_jules",
            )
            .first()
        )

        if evenement is None:
            evenement = EvenementFamilial(
                titre=titre,
                date_evenement=jalon.date_atteint,
                type_evenement="jalon_jules",
                recurrence="unique",
                notes=jalon.description or jalon.notes,
                participants=[enfant.name] if enfant else ["Jules"],
            )
            db.add(evenement)
            db.commit()
            db.refresh(evenement)

        return {
            "jalon_id": jalon.id,
            "evenement_id": evenement.id,
            "titre": evenement.titre,
            "date_evenement": evenement.date_evenement.isoformat(),
        }

    # ── I4: Budget mensuel → Rapport famille ───────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def integrer_budget_mensuel_dans_rapport(
        self,
        *,
        mois: int | None = None,
        annee: int | None = None,
        db: Session | None = None,
    ) -> dict:
        """I4: résume le budget du mois pour l'injecter dans le rapport famille."""
        from src.core.models.famille import BudgetFamille

        aujourd_hui = date.today()
        mois_cible = mois or aujourd_hui.month
        annee_cible = annee or aujourd_hui.year

        lignes = (
            db.query(BudgetFamille)
            .filter(
                func.extract("month", BudgetFamille.date) == mois_cible,
                func.extract("year", BudgetFamille.date) == annee_cible,
            )
            .all()
        )
        total = round(sum(float(ligne.montant or 0) for ligne in lignes), 2)
        repartition: dict[str, float] = {}
        for ligne in lignes:
            categorie = ligne.categorie or "autre"
            repartition[categorie] = round(repartition.get(categorie, 0.0) + float(ligne.montant or 0), 2)

        return {
            "mois": mois_cible,
            "annee": annee_cible,
            "total_depenses": total,
            "nb_lignes": len(lignes),
            "repartition": repartition,
        }

    # ── I9: Retour voyage → Résumé dépenses ───────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def resumer_depenses_retour_voyage(
        self,
        voyage_id: int | None = None,
        db: Session | None = None,
    ) -> dict:
        """I9: produit un résumé synthétique du budget d'un voyage terminé."""
        from src.core.models.voyage import Voyage

        query = db.query(Voyage)
        if voyage_id is not None:
            query = query.filter(Voyage.id == voyage_id)
        else:
            query = query.filter(Voyage.statut.in_(["termine", "terminé", "en_cours"]))

        voyage = query.order_by(Voyage.date_retour.desc()).first()
        if not voyage:
            return {}

        budget_prevu = float(voyage.budget_prevu or 0)
        budget_reel = float(voyage.budget_reel or 0)
        ecart = round(budget_reel - budget_prevu, 2)
        return {
            "voyage_id": voyage.id,
            "titre": voyage.titre,
            "destination": voyage.destination,
            "budget_prevu": budget_prevu,
            "budget_reel": budget_reel,
            "ecart_budget": ecart,
            "statut": voyage.statut,
        }

    # ── P3-A2: Budget unifié famille + maison ──────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def budget_unifie(self, mois: int | None = None, annee: int | None = None, db: Session | None = None) -> dict:
        """P3-A2: Agrège budget famille + charges maison en vue unifiée."""
        from src.core.models.famille import BudgetFamille
        from src.core.models.finances import DepenseMaison

        aujourd_hui = date.today()
        mois_cible = mois or aujourd_hui.month
        annee_cible = annee or aujourd_hui.year

        lignes_famille = (
            db.query(BudgetFamille)
            .filter(
                func.extract("month", BudgetFamille.date) == mois_cible,
                func.extract("year", BudgetFamille.date) == annee_cible,
            )
            .all()
        )
        details_famille: dict[str, float] = {}
        for ligne in lignes_famille:
            cat = ligne.categorie or "autre"
            details_famille[cat] = round(details_famille.get(cat, 0.0) + float(ligne.montant or 0), 2)
        total_famille = round(sum(details_famille.values()), 2)

        lignes_maison = (
            db.query(DepenseMaison)
            .filter(
                DepenseMaison.mois == mois_cible,
                DepenseMaison.annee == annee_cible,
            )
            .all()
        )
        details_maison: dict[str, float] = {}
        for ligne in lignes_maison:
            cat = ligne.categorie or "autre"
            details_maison[cat] = round(details_maison.get(cat, 0.0) + float(ligne.montant or 0), 2)
        total_maison = round(sum(details_maison.values()), 2)

        mois_prec = mois_cible - 1 if mois_cible > 1 else 12
        annee_prec = annee_cible if mois_cible > 1 else annee_cible - 1
        total_prec_famille = float(
            db.query(func.coalesce(func.sum(BudgetFamille.montant), 0))
            .filter(
                func.extract("month", BudgetFamille.date) == mois_prec,
                func.extract("year", BudgetFamille.date) == annee_prec,
            )
            .scalar()
        )
        total_prec_maison = float(
            db.query(func.coalesce(func.sum(DepenseMaison.montant), 0))
            .filter(DepenseMaison.mois == mois_prec, DepenseMaison.annee == annee_prec)
            .scalar()
        )
        total_prec = total_prec_famille + total_prec_maison
        total_unifie = round(total_famille + total_maison, 2)
        evolution_pct = round(((total_unifie - total_prec) / total_prec) * 100, 1) if total_prec > 0 else None

        return {
            "mois": mois_cible,
            "annee": annee_cible,
            "total_famille": total_famille,
            "total_maison": total_maison,
            "total_unifie": total_unifie,
            "details_famille": [{"categorie": k, "montant": v} for k, v in sorted(details_famille.items())],
            "details_maison": [{"categorie": k, "montant": v} for k, v in sorted(details_maison.items())],
            "evolution_pct": evolution_pct,
        }

    # ── P3-A3: Impact déménagement ─────────────────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def impact_demenagement(self, scenario_id: int, db: Session | None = None) -> dict:
        """P3-A3: Évalue l'impact familial d'un scénario de déménagement."""
        from src.core.models.famille import ActiviteFamille, ProfilEnfant
        from src.core.models.habitat_projet import CritereScenarioHabitat, ScenarioHabitat

        scenario = db.query(ScenarioHabitat).filter(ScenarioHabitat.id == scenario_id).first()
        if not scenario:
            return {"erreur": "Scénario introuvable"}

        enfants = db.query(ProfilEnfant).filter(ProfilEnfant.actif.is_(True)).all()
        activites = db.query(ActiviteFamille).limit(20).all()
        criteres = (
            db.query(CritereScenarioHabitat)
            .filter(CritereScenarioHabitat.scenario_id == scenario_id)
            .all()
        )

        impacts = []
        for enfant in enfants:
            age_mois = None
            if enfant.date_of_birth:
                delta = date.today() - enfant.date_of_birth
                age_mois = delta.days // 30
            impacts.append({
                "domaine": "enfant",
                "sujet": enfant.name,
                "detail": f"Changement d'environnement pour {enfant.name}"
                + (f" ({age_mois} mois)" if age_mois else ""),
                "severite": "moyenne",
            })

        for act in activites:
            impacts.append({
                "domaine": "activite",
                "sujet": act.titre if hasattr(act, "titre") else str(act),
                "detail": "Activité potentiellement à réorganiser après déménagement",
                "severite": "faible",
            })

        notes = [float(c.note) for c in criteres if c.note is not None]
        score_global = round(sum(notes) / len(notes), 1) if notes else None

        return {
            "scenario_nom": scenario.nom,
            "impacts": impacts,
            "score_global": score_global,
            "recommandation": "Scénario favorable" if score_global and score_global >= 7 else "À évaluer en détail",
            "details": {
                "budget_estime": float(scenario.budget_estime) if scenario.budget_estime else None,
                "surface_m2": float(scenario.surface_finale_m2) if scenario.surface_finale_m2 else None,
                "nb_chambres": scenario.nb_chambres,
                "avantages": scenario.avantages or [],
                "inconvenients": scenario.inconvenients or [],
            },
        }

    # ── E5: Anniversaire → Suggestion cadeau IA ────────────

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def anniversaire_vers_cadeau_ia(
        self,
        anniversaire_id: int | None = None,
        jours_horizon: int = 30,
        db: Session | None = None,
    ) -> dict:
        """E5: Génère des suggestions de cadeaux IA pour un anniversaire."""
        from src.core.models.famille import AnniversaireFamille, BudgetFamille

        if anniversaire_id:
            anniversaire = db.query(AnniversaireFamille).filter(
                AnniversaireFamille.id == anniversaire_id,
                AnniversaireFamille.actif.is_(True),
            ).first()
        else:
            anniversaires = db.query(AnniversaireFamille).filter(
                AnniversaireFamille.actif.is_(True)
            ).all()
            proches = sorted(
                [a for a in anniversaires if 0 <= a.jours_restants <= jours_horizon],
                key=lambda a: a.jours_restants,
            )
            anniversaire = proches[0] if proches else None

        if not anniversaire:
            return {}

        age = anniversaire.age
        relation = anniversaire.relation or "inconnu"
        idees_existantes = (anniversaire.idees_cadeaux or "").strip()
        historique = anniversaire.historique_cadeaux or []

        budget_reference_map = {
            "enfant": 50.0,
            "parent": 80.0,
            "grand_parent": 60.0,
            "conjoint": 100.0,
            "ami": 30.0,
            "collègue": 20.0,
        }
        budget_estime = budget_reference_map.get(relation.lower(), 40.0)

        mois_actuel = date.today().month
        annee_actuelle = date.today().year
        depenses_mois = float(
            db.query(func.coalesce(func.sum(BudgetFamille.montant), 0))
            .filter(
                func.extract("month", BudgetFamille.date) == mois_actuel,
                func.extract("year", BudgetFamille.date) == annee_actuelle,
            )
            .scalar()
        )

        suggestions_par_profil: list[dict] = []

        if age < 3:
            suggestions_par_profil = [
                {"nom": "Éveil sensoriel — tapis d'éveil", "budget_estime": 35, "categorie": "jouet"},
                {"nom": "Coffret livres en tissu", "budget_estime": 20, "categorie": "livre"},
                {"nom": "Hochet en bois naturel", "budget_estime": 15, "categorie": "jouet"},
                {"nom": "Coffret de bain bébé", "budget_estime": 25, "categorie": "soin"},
            ]
        elif age < 6:
            suggestions_par_profil = [
                {"nom": "Jeu de construction Duplo/Lego", "budget_estime": 40, "categorie": "jouet"},
                {"nom": "Vélo ou trottinette adaptée", "budget_estime": 60, "categorie": "sport"},
                {"nom": "Abonnement médiathèque + livres", "budget_estime": 25, "categorie": "livre"},
                {"nom": "Kit peinture / activités créatives", "budget_estime": 20, "categorie": "créatif"},
            ]
        elif age < 12:
            suggestions_par_profil = [
                {"nom": "Jeu de société famille", "budget_estime": 35, "categorie": "jeu"},
                {"nom": "Livre de la série préférée", "budget_estime": 15, "categorie": "livre"},
                {"nom": "Activité sportive (stage, cours)", "budget_estime": 50, "categorie": "sport"},
                {"nom": "Kit LEGO thématique", "budget_estime": 45, "categorie": "jouet"},
            ]
        elif relation in ("ami", "collègue"):
            suggestions_par_profil = [
                {"nom": "Coffret thé ou café artisanal", "budget_estime": 20, "categorie": "gastronomie"},
                {"nom": "Livre de cuisine ou romans", "budget_estime": 18, "categorie": "livre"},
                {"nom": "Bon cadeau restaurant/spa", "budget_estime": 30, "categorie": "experience"},
                {"nom": "Objet déco personnalisé", "budget_estime": 25, "categorie": "maison"},
            ]
        else:
            suggestions_par_profil = [
                {"nom": "Bon cadeau expérience (sortie, atelier)", "budget_estime": budget_estime, "categorie": "experience"},
                {"nom": "Coffret gastronomie / dégustation", "budget_estime": 40, "categorie": "gastronomie"},
                {"nom": "Livre coup de cœur", "budget_estime": 20, "categorie": "livre"},
                {"nom": "Loisir ou hobby (selon centres d'intérêt)", "budget_estime": budget_estime, "categorie": "loisir"},
            ]

        cadeaux_recents = {c.get("cadeau", "").lower() for c in historique[-3:]}
        suggestions = [
            s for s in suggestions_par_profil
            if s["nom"].lower() not in cadeaux_recents
        ]

        return {
            "anniversaire": {
                "id": anniversaire.id,
                "nom_personne": anniversaire.nom_personne,
                "age": age,
                "relation": relation,
                "jours_restants": anniversaire.jours_restants,
                "date_anniversaire": anniversaire.prochain_anniversaire.isoformat(),
            },
            "budget_estime": budget_estime,
            "depenses_mois_en_cours": depenses_mois,
            "idees_existantes": idees_existantes or None,
            "historique_recents": historique[-3:] if historique else [],
            "suggestions_cadeaux": suggestions,
            "nb_suggestions": len(suggestions),
            "conseil": (
                f"Budget recommandé pour un·e {relation} : {budget_estime:.0f}€. "
                + (f"Idées notées : {idees_existantes}. " if idees_existantes else "")
                + ("Pensez à vérifier l'historique pour éviter les doublons." if historique else "")
            ),
        }
