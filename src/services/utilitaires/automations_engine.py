"""Moteur d'automations LT-04 (règles "si -> alors")."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import (
    ActiviteGarmin,
    AnniversaireFamille,
    ArticleCourses,
    ArticleInventaire,
    AutomationRegle,
    Depense,
    DocumentFamille,
    EvenementPlanning,
    ListeCourses,
    Recette,
    TacheEntretien,
)
from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class MoteurAutomationsService:
    """Exécute les automations actives stockées en base."""

    @staticmethod
    def _assurer_liste_courses_active(db: Session) -> ListeCourses:
        liste = (
            db.query(ListeCourses)
            .filter(ListeCourses.archivee == False)  # noqa: E712
            .order_by(ListeCourses.id.asc())
            .first()
        )
        if liste is not None:
            return liste

        liste = ListeCourses(nom="Liste auto", archivee=False)
        db.add(liste)
        db.flush()
        return liste

    def _declenche_stock_bas(self, declencheur: dict[str, Any], db: Session) -> list[ArticleInventaire]:
        seuil = float(declencheur.get("seuil", 1))
        article_nom = (declencheur.get("article") or "").strip().lower()

        query = db.query(ArticleInventaire).filter(ArticleInventaire.quantite <= seuil)
        items = query.limit(20).all()
        if not article_nom:
            return items

        filtres = []
        for item in items:
            nom = (item.nom or "").lower()
            if article_nom in nom:
                filtres.append(item)
        return filtres

    def _declenche_peremption_proche(self, declencheur: dict[str, Any], db: Session) -> list[ArticleInventaire]:
        jours = int(declencheur.get("jours", 3) or 3)
        limite = datetime.now(UTC).date() + timedelta(days=max(1, jours))
        return (
            db.query(ArticleInventaire)
            .filter(
                ArticleInventaire.date_peremption.isnot(None),
                ArticleInventaire.date_peremption <= limite,
                ArticleInventaire.quantite > 0,
            )
            .limit(30)
            .all()
        )

    def _declenche_budget_depassement(self, declencheur: dict[str, Any], db: Session) -> list[dict[str, Any]]:
        seuil = float(declencheur.get("seuil", 300) or 300)
        maintenant = datetime.now(UTC)
        debut_mois = maintenant.date().replace(day=1)
        total = (
            db.query(Depense)
            .filter(Depense.date >= debut_mois, Depense.date <= maintenant.date())
            .with_entities(db.func.sum(Depense.montant))
            .scalar()
            or 0
        )
        if float(total) <= seuil:
            return []
        return [{"type": "budget_depassement", "total": float(total), "seuil": seuil}]

    def _declenche_meteo_alerte(self, declencheur: dict[str, Any]) -> list[dict[str, Any]]:
        mot_cle = str(declencheur.get("mot_cle", "pluie")).lower()
        try:
            from src.services.utilitaires.meteo_service import obtenir_meteo_service

            service = obtenir_meteo_service()
            previsions = service.get_previsions(nb_jours=2)
            if not previsions:
                return []

            alertes: list[dict[str, Any]] = []
            for prev in previsions:
                condition = str(getattr(prev, "condition", "")).lower()
                if mot_cle in condition or any(x in condition for x in ["orage", "neige", "vent"]):
                    alertes.append(
                        {
                            "date": str(getattr(prev, "date", "")),
                            "condition": getattr(prev, "condition", ""),
                        }
                    )
            return alertes
        except Exception:
            return []

    def _declenche_anniversaire_proche(self, declencheur: dict[str, Any], db: Session) -> list[AnniversaireFamille]:
        jours = int(declencheur.get("jours", 7) or 7)
        aujourd_hui = datetime.now(UTC).date()
        limite = aujourd_hui + timedelta(days=max(1, jours))
        return (
            db.query(AnniversaireFamille)
            .filter(
                AnniversaireFamille.date_anniversaire >= aujourd_hui,
                AnniversaireFamille.date_anniversaire <= limite,
            )
            .limit(20)
            .all()
        )

    def _declenche_tache_en_retard(self, db: Session) -> list[TacheEntretien]:
        aujourd_hui = datetime.now(UTC).date()
        return (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.fait == False,  # noqa: E712
                TacheEntretien.prochaine_fois.isnot(None),
                TacheEntretien.prochaine_fois < aujourd_hui,
            )
            .limit(30)
            .all()
        )

    def _declenche_garmin_inactivite(self, declencheur: dict[str, Any], db: Session) -> list[dict[str, Any]]:
        jours = int(declencheur.get("jours", 3) or 3)
        seuil = datetime.now(UTC) - timedelta(days=max(1, jours))
        rows = (
            db.query(ActiviteGarmin.user_id, db.func.max(ActiviteGarmin.date_debut))
            .group_by(ActiviteGarmin.user_id)
            .all()
        )
        return [
            {"user_id": int(user_id), "derniere_activite": str(derniere)}
            for user_id, derniere in rows
            if derniere is None or derniere < seuil
        ]

    def _declenche_document_expiration(self, declencheur: dict[str, Any], db: Session) -> list[DocumentFamille]:
        jours = int(declencheur.get("jours", 30) or 30)
        limite = datetime.now(UTC).date() + timedelta(days=max(1, jours))
        return (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.actif == True,  # noqa: E712
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= limite,
            )
            .limit(20)
            .all()
        )

    def _declenche_recette_sans_photo(self, db: Session) -> list[Recette]:
        return (
            db.query(Recette)
            .filter((Recette.url_image.is_(None)) | (Recette.url_image == ""))
            .limit(20)
            .all()
        )

    def _declenche_feedback_recette_negatif(
        self,
        declencheur: dict[str, Any],
        db: Session,
    ) -> list[Any]:
        from src.core.models.user_preferences import RetourRecette

        jours = int(declencheur.get("jours", 30) or 30)
        limite = datetime.now(UTC) - timedelta(days=max(1, jours))
        return (
            db.query(RetourRecette)
            .filter(
                RetourRecette.feedback == "dislike",
                RetourRecette.created_at >= limite,
            )
            .limit(20)
            .all()
        )

    def _declenche_planning_valide(self, declencheur: dict[str, Any], db: Session) -> list[Any]:
        from src.core.models.planning import Planning

        jours = int(declencheur.get("jours", 14) or 14)
        limite = datetime.now(UTC).date() - timedelta(days=max(1, jours))
        return (
            db.query(Planning)
            .filter(
                Planning.etat.in_(["valide", "actif"]),
                Planning.semaine_debut >= limite,
            )
            .limit(10)
            .all()
        )

    def _declenche_batch_termine(self, declencheur: dict[str, Any], db: Session) -> list[Any]:
        from src.core.models import SessionBatchCooking

        jours = int(declencheur.get("jours", 14) or 14)
        limite = datetime.now(UTC).date() - timedelta(days=max(1, jours))
        return (
            db.query(SessionBatchCooking)
            .filter(
                SessionBatchCooking.statut.in_(["terminee", "terminée", "termine"]),
                SessionBatchCooking.date_session >= limite,
            )
            .limit(10)
            .all()
        )

    def _executer_action_ajouter_courses(
        self,
        action: dict[str, Any],
        items: list[ArticleInventaire],
        db: Session,
    ) -> int:
        if not items:
            return 0

        quantite = float(action.get("quantite", 1))
        priorite = str(action.get("priorite", "haute"))

        liste = self._assurer_liste_courses_active(db)
        ajoutes = 0
        for item in items:
            deja = (
                db.query(ArticleCourses)
                .filter(
                    ArticleCourses.liste_id == liste.id,
                    ArticleCourses.ingredient_id == item.ingredient_id,
                    ArticleCourses.achete == False,  # noqa: E712
                )
                .first()
            )
            if deja is not None:
                continue

            db.add(
                ArticleCourses(
                    liste_id=liste.id,
                    ingredient_id=item.ingredient_id,
                    quantite_necessaire=max(0.1, quantite),
                    priorite=priorite,
                    achete=False,
                    suggere_par_ia=False,
                    notes="Ajout automatique via règle Si->Alors",
                )
            )
            ajoutes += 1

        return ajoutes

    def _executer_action_notifier(
        self,
        action: dict[str, Any],
        items: list[ArticleInventaire],
        user_id: int,
    ) -> int:
        titre = str(action.get("titre", "Automation exécutée"))
        if items:
            noms = ", ".join((item.nom or "article") for item in items[:5])
            message = str(action.get("message", f"Stock bas détecté: {noms}"))
        else:
            message = str(action.get("message", "Condition d'automation déclenchée."))

        dispatcher = get_dispatcher_notifications()
        resultats = dispatcher.envoyer(
            user_id=str(user_id),
            message=message,
            canaux=["ntfy", "push"],
            titre=titre,
        )
        if any(bool(v) for v in resultats.values()):
            return 1
        return 0

    def _executer_action_envoyer_telegram(self, action: dict[str, Any], user_id: int) -> int:
        dispatcher = get_dispatcher_notifications()
        resultats = dispatcher.envoyer(
            user_id=str(user_id),
            message=str(action.get("message", "Automation déclenchée.")),
            canaux=["telegram"],
            titre=str(action.get("titre", "Automation")),
        )
        return 1 if any(bool(v) for v in resultats.values()) else 0

    def _executer_action_envoyer_email(self, action: dict[str, Any], user_id: int) -> int:
        dispatcher = get_dispatcher_notifications()
        titre = str(action.get("titre", "Automation"))
        message = str(action.get("message", "Automation déclenchée."))
        resultats = dispatcher.envoyer(
            user_id=str(user_id),
            message=message,
            canaux=["email"],
            titre=titre,
            type_email="alerte_critique",
            alerte={"titre": titre, "message": message},
        )
        return 1 if any(bool(v) for v in resultats.values()) else 0

    def _executer_action_ajouter_au_planning(self, action: dict[str, Any], db: Session) -> int:
        date_debut = action.get("date_debut")
        if isinstance(date_debut, str) and date_debut:
            dt_debut = datetime.fromisoformat(date_debut)
        else:
            dt_debut = datetime.now(UTC)

        db.add(
            EvenementPlanning(
                titre=str(action.get("titre", "Tâche automatique")),
                description=str(action.get("description", "Ajouté par automation")),
                date_debut=dt_debut,
                date_fin=dt_debut + timedelta(minutes=int(action.get("duree_minutes", 30) or 30)),
                type_event=str(action.get("type_event", "autre")),
            )
        )
        return 1

    def _executer_action_creer_tache_maison(self, action: dict[str, Any], db: Session, user_id: int) -> int:
        db.add(
            TacheEntretien(
                nom=str(action.get("nom", "Tâche automation")),
                description=str(action.get("description", "Créée automatiquement")),
                categorie=str(action.get("categorie", "maintenance")),
                priorite=str(action.get("priorite", "normale")),
                prochaine_fois=datetime.now(UTC).date(),
                fait=False,
            )
        )
        if bool(action.get("notifier", False)):
            self._executer_action_notifier(
                {
                    "titre": str(action.get("titre_notification", "Nouvelle tâche entretien")),
                    "message": str(
                        action.get(
                            "message_notification",
                            "Une nouvelle tâche d’entretien a été créée automatiquement.",
                        )
                    ),
                },
                [],
                user_id,
            )
        return 1

    def _executer_action_generer_courses_planning(
        self,
        _action: dict[str, Any],
        items: list[Any],
        db: Session,
    ) -> int:
        from src.services.ia.bridges import obtenir_service_bridges

        service = obtenir_service_bridges()
        executions = 0
        for item in items:
            planning_id = getattr(item, "id", None)
            semaine_debut = getattr(item, "semaine_debut", None)
            if planning_id is None and isinstance(item, dict):
                planning_id = item.get("planning_id") or item.get("id")
                semaine_debut = item.get("semaine_debut")
            if not planning_id:
                continue
            resultat = service.generer_courses_auto_depuis_planning(
                int(planning_id),
                semaine_debut=semaine_debut,
                db=db,
            )
            if resultat.get("nb_articles", 0) > 0 or resultat.get("liste_id"):
                executions += 1
        return executions

    def _executer_action_pre_remplir_planning_batch(
        self,
        _action: dict[str, Any],
        items: list[Any],
        db: Session,
    ) -> int:
        from src.services.ia.bridges import obtenir_service_bridges

        service = obtenir_service_bridges()
        executions = 0
        for item in items:
            session_id = getattr(item, "id", None)
            if session_id is None and isinstance(item, dict):
                session_id = item.get("session_id") or item.get("id")
            if not session_id:
                continue
            resultat = service.pre_remplir_planning_depuis_batch(int(session_id), db=db)
            if resultat.get("nb_repas_mis_a_jour", 0) > 0 or resultat.get("planning_id"):
                executions += 1
        return executions

    def _executer_action_ajuster_suggestions_recette(
        self,
        action: dict[str, Any],
        items: list[Any],
        db: Session,
    ) -> int:
        from src.services.ia.bridges import obtenir_service_bridges

        service = obtenir_service_bridges()
        executions = 0
        note_defaut = action.get("seuil_note")
        for item in items:
            recette_id = getattr(item, "recette_id", None)
            feedback = getattr(item, "feedback", None)
            user_id = getattr(item, "user_id", None)
            if isinstance(item, dict):
                recette_id = recette_id or item.get("recette_id")
                feedback = feedback or item.get("feedback")
                user_id = user_id or item.get("user_id")
            if not recette_id:
                continue
            resultat = service.appliquer_feedback_recette_sur_suggestions(
                int(recette_id),
                note=int(note_defaut) if note_defaut is not None else None,
                feedback=str(feedback or "dislike"),
                user_id=str(user_id or "system"),
                db=db,
            )
            if resultat.get("recette_id"):
                executions += 1
        return executions

    def _executer_action_generer_rapport_pdf(self, action: dict[str, Any], user_id: int) -> int:
        dispatcher = get_dispatcher_notifications()
        resultats = dispatcher.envoyer(
            user_id=str(user_id),
            message=str(action.get("message", "Rapport PDF prêt à générer")),
            canaux=["ntfy"],
            titre="Rapport PDF",
        )
        return 1 if any(bool(v) for v in resultats.values()) else 0

    def _executer_action_mettre_a_jour_budget(self, action: dict[str, Any], db: Session) -> int:
        montant = float(action.get("montant", 0) or 0)
        if montant <= 0:
            return 0

        db.add(
            Depense(
                montant=montant,
                categorie=str(action.get("categorie", "autre")),
                description=str(action.get("description", "Ajustement budget automation")),
                date=datetime.now(UTC).date(),
            )
        )
        return 1

    @staticmethod
    def _executer_action_archiver(_action: dict[str, Any], regle: AutomationRegle) -> int:
        regle.active = False
        return 1

    def _evaluer_declencheur(self, declencheur: dict[str, Any], db: Session) -> list[Any]:
        type_declencheur = str(declencheur.get("type", "")).strip().lower()
        if type_declencheur == "stock_bas":
            return self._declenche_stock_bas(declencheur, db)
        if type_declencheur == "peremption_proche":
            return self._declenche_peremption_proche(declencheur, db)
        if type_declencheur == "budget_depassement":
            return self._declenche_budget_depassement(declencheur, db)
        if type_declencheur == "meteo_alerte":
            return self._declenche_meteo_alerte(declencheur)
        if type_declencheur == "anniversaire_proche":
            return self._declenche_anniversaire_proche(declencheur, db)
        if type_declencheur == "tache_en_retard":
            return self._declenche_tache_en_retard(db)
        if type_declencheur == "garmin_inactivite":
            return self._declenche_garmin_inactivite(declencheur, db)
        if type_declencheur == "document_expiration":
            return self._declenche_document_expiration(declencheur, db)
        if type_declencheur == "recette_sans_photo":
            return self._declenche_recette_sans_photo(db)
        if type_declencheur == "feedback_recette_negatif":
            return self._declenche_feedback_recette_negatif(declencheur, db)
        if type_declencheur == "planning_valide":
            return self._declenche_planning_valide(declencheur, db)
        if type_declencheur == "batch_termine":
            return self._declenche_batch_termine(declencheur, db)
        raise ValueError(f"Déclencheur non supporté: {type_declencheur}")

    def _executer_une_regle(self, regle: AutomationRegle, db: Session, *, dry_run: bool = False) -> dict[str, Any]:
        declencheur = regle.declencheur or {}
        action = regle.action or {}

        try:
            items = self._evaluer_declencheur(declencheur, db)
        except ValueError as exc:
            return {
                "success": False,
                "automation_id": regle.id,
                "message": str(exc),
                "executed": 0,
            }

        if not items:
            return {
                "success": True,
                "automation_id": regle.id,
                "message": "Condition non remplie",
                "executed": 0,
            }

        type_action = str(action.get("type", "")).strip().lower()
        executed = 0
        if type_action in {"ajouter_courses", "generer_liste_courses"}:
            executed = self._executer_action_ajouter_courses(action, items, db)
        elif type_action == "suggerer_recette":
            executed = self._executer_action_notifier(
                {
                    "titre": action.get("titre", "Suggestions recettes"),
                    "message": action.get("message", "Des ingrédients déclenchent une suggestion recette."),
                },
                items,
                regle.user_id,
            )
        elif type_action == "creer_tache_maison":
            executed = self._executer_action_creer_tache_maison(action, db, regle.user_id)
        elif type_action == "ajouter_au_planning":
            executed = self._executer_action_ajouter_au_planning(action, db)
        elif type_action == "mettre_a_jour_budget":
            executed = self._executer_action_mettre_a_jour_budget(action, db)
        elif type_action == "generer_rapport_pdf":
            executed = self._executer_action_generer_rapport_pdf(action, regle.user_id)
        elif type_action == "archiver":
            executed = self._executer_action_archiver(action, regle)
        elif type_action == "notifier":
            executed = self._executer_action_notifier(action, items, regle.user_id)
        elif type_action == "envoyer_telegram":
            executed = self._executer_action_envoyer_telegram(action, regle.user_id)
        elif type_action == "envoyer_email":
            executed = self._executer_action_envoyer_email(action, regle.user_id)
        elif type_action == "generer_courses_planning":
            executed = self._executer_action_generer_courses_planning(action, items, db)
        elif type_action == "pre_remplir_planning_batch":
            executed = self._executer_action_pre_remplir_planning_batch(action, items, db)
        elif type_action == "ajuster_suggestions_recette":
            executed = self._executer_action_ajuster_suggestions_recette(action, items, db)
        else:
            return {
                "success": False,
                "automation_id": regle.id,
                "message": f"Action non supportée: {type_action}",
                "executed": 0,
            }

        if not dry_run:
            regle.derniere_execution = datetime.utcnow()
            regle.execution_count = int(regle.execution_count or 0) + 1

        return {
            "success": True,
            "automation_id": regle.id,
            "message": "Automation exécutée" if not dry_run else "Automation simulée (dry-run)",
            "executed": executed,
            "items_declenches": len(items),
            "dry_run": dry_run,
        }

    @avec_gestion_erreurs(default_return={"executed": 0, "results": []})
    @avec_session_db
    def executer_automations_actives(self, db: Session | None = None) -> dict[str, Any]:
        if db is None:
            return {"executed": 0, "results": []}

        regles = (
            db.query(AutomationRegle)
            .filter(AutomationRegle.active == True)  # noqa: E712
            .order_by(AutomationRegle.id.asc())
            .all()
        )

        results: list[dict[str, Any]] = []
        for regle in regles:
            try:
                result = self._executer_une_regle(regle, db)
                results.append(result)
            except Exception as exc:  # pragma: no cover
                logger.exception("Erreur exécution automation %s", regle.id)
                results.append(
                    {
                        "success": False,
                        "automation_id": regle.id,
                        "message": str(exc),
                        "executed": 0,
                    }
                )

        db.commit()
        executed_count = sum(1 for r in results if r.get("success") and r.get("executed", 0) > 0)
        return {"executed": executed_count, "results": results, "total": len(results)}

    @avec_gestion_erreurs(default_return={"executed": 0, "results": [], "dry_run": True})
    @avec_session_db
    def executer_automations_actives_dry_run(self, db: Session | None = None) -> dict[str, Any]:
        """Simule l'exécution des automations actives sans persistance."""
        if db is None:
            return {"executed": 0, "results": [], "dry_run": True}

        regles = (
            db.query(AutomationRegle)
            .filter(AutomationRegle.active == True)  # noqa: E712
            .order_by(AutomationRegle.id.asc())
            .all()
        )

        results: list[dict[str, Any]] = []
        for regle in regles:
            try:
                results.append(self._executer_une_regle(regle, db, dry_run=True))
            except Exception as exc:  # pragma: no cover
                results.append(
                    {
                        "success": False,
                        "automation_id": regle.id,
                        "message": str(exc),
                        "executed": 0,
                        "dry_run": True,
                    }
                )

        db.rollback()
        executed_count = sum(1 for r in results if r.get("success") and r.get("executed", 0) > 0)
        return {"executed": executed_count, "results": results, "total": len(results), "dry_run": True}

    @avec_gestion_erreurs(default_return={"success": False, "message": "automation introuvable"})
    @avec_session_db
    def executer_automation_par_id(
        self,
        automation_id: int,
        user_id: int | None = None,
        dry_run: bool = False,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {"success": False, "message": "db indisponible"}

        regle = db.get(AutomationRegle, automation_id)
        if regle is None:
            return {"success": False, "message": "Automation introuvable"}
        if user_id is not None and int(regle.user_id) != int(user_id):
            return {"success": False, "message": "Automation introuvable"}
        if not regle.active:
            return {"success": False, "message": "Automation inactive"}

        result = self._executer_une_regle(regle, db, dry_run=dry_run)
        if dry_run:
            db.rollback()
        else:
            db.commit()
        return result


@service_factory("moteur_automations", tags={"automations", "utilitaires"})
def obtenir_moteur_automations_service() -> MoteurAutomationsService:
    return MoteurAutomationsService()

