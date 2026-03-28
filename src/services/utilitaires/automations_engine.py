"""Moteur d'automations LT-04 (règles "si -> alors")."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import ArticleCourses, ArticleInventaire, AutomationRegle, ListeCourses
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

    def _executer_une_regle(self, regle: AutomationRegle, db: Session) -> dict[str, Any]:
        declencheur = regle.declencheur or {}
        action = regle.action or {}

        type_declencheur = str(declencheur.get("type", "")).strip().lower()
        if type_declencheur != "stock_bas":
            return {
                "success": False,
                "automation_id": regle.id,
                "message": f"Déclencheur non supporté: {type_declencheur}",
                "executed": 0,
            }

        items = self._declenche_stock_bas(declencheur, db)
        if not items:
            return {
                "success": True,
                "automation_id": regle.id,
                "message": "Condition non remplie",
                "executed": 0,
            }

        type_action = str(action.get("type", "")).strip().lower()
        executed = 0
        if type_action == "ajouter_courses":
            executed = self._executer_action_ajouter_courses(action, items, db)
        elif type_action == "notifier":
            executed = self._executer_action_notifier(action, items, regle.user_id)
        else:
            return {
                "success": False,
                "automation_id": regle.id,
                "message": f"Action non supportée: {type_action}",
                "executed": 0,
            }

        regle.derniere_execution = datetime.utcnow()
        regle.execution_count = int(regle.execution_count or 0) + 1

        return {
            "success": True,
            "automation_id": regle.id,
            "message": "Automation exécutée",
            "executed": executed,
            "items_declenches": len(items),
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

    @avec_gestion_erreurs(default_return={"success": False, "message": "automation introuvable"})
    @avec_session_db
    def executer_automation_par_id(
        self,
        automation_id: int,
        db: Session | None = None,
    ) -> dict[str, Any]:
        if db is None:
            return {"success": False, "message": "db indisponible"}

        regle = db.get(AutomationRegle, automation_id)
        if regle is None:
            return {"success": False, "message": "Automation introuvable"}
        if not regle.active:
            return {"success": False, "message": "Automation inactive"}

        result = self._executer_une_regle(regle, db)
        db.commit()
        return result


@service_factory("moteur_automations", tags={"automations", "utilitaires"})
def get_moteur_automations_service() -> MoteurAutomationsService:
    return MoteurAutomationsService()
