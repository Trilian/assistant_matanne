"""Service assistant proactif déclenché par EventBus (I.15)."""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta
from typing import Any

from src.core.caching import obtenir_cache
from src.core.db import obtenir_contexte_db
from src.services.core.registry import service_factory
from src.services.ia_avancee import get_ia_avancee_service

logger = logging.getLogger(__name__)


class AssistantProactifService:
    """Génère des suggestions proactives selon contexte, météo et planning."""

    CLE_DERNIERES_SUGGESTIONS = "assistant_proactif:dernieres_suggestions"
    CLE_HISTORIQUE = "assistant_proactif:historique"
    TTL_SUGGESTIONS_S = 60 * 60 * 6
    THROTTLE_S = 60 * 10

    def traiter_evenement(self, event_type: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Traite un événement et met à jour les suggestions proactives."""
        data = data or {}
        if self._est_throttle(event_type):
            return {"status": "ignored", "reason": "throttled", "event_type": event_type}

        suggestions = self._suggestions_contextuelles(event_type=event_type, data=data)

        # Compléter avec l'IA avancée existante (déjà cacheée)
        try:
            ia = get_ia_avancee_service()
            ia_result = ia.generer_suggestions_proactives()
            if ia_result and ia_result.suggestions:
                for item in ia_result.suggestions[:3]:
                    suggestions.append(
                        {
                            "module": item.module,
                            "titre": item.titre,
                            "message": item.message,
                            "action_url": item.action_url,
                            "priorite": item.priorite,
                            "contexte": item.contexte,
                            "source": "ia_avancee",
                        }
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning("I.15: impossible de compléter via IA avancée: %s", e)

        suggestions = self._dedoublonner_limite(suggestions, limite=5)
        payload = {
            "event_type": event_type,
            "date_generation": date.today().isoformat(),
            "suggestions": suggestions,
        }

        cache = obtenir_cache()
        cache.set(
            self.CLE_DERNIERES_SUGGESTIONS,
            payload,
            ttl=self.TTL_SUGGESTIONS_S,
            tags=["assistant", "proactif", "ia"],
        )

        historique = cache.get(self.CLE_HISTORIQUE, default=[])
        if not isinstance(historique, list):
            historique = []
        historique.append(payload)
        historique = historique[-20:]
        cache.set(
            self.CLE_HISTORIQUE,
            historique,
            ttl=60 * 60 * 24,
            tags=["assistant", "proactif"],
        )

        return {"status": "updated", "event_type": event_type, "nb_suggestions": len(suggestions)}

    def obtenir_derniere_suggestion(self) -> dict[str, Any]:
        """Retourne la dernière suggestion proactive disponible."""
        payload = obtenir_cache().get(self.CLE_DERNIERES_SUGGESTIONS)
        if isinstance(payload, dict):
            return payload
        return {"event_type": None, "date_generation": None, "suggestions": []}

    def _est_throttle(self, event_type: str) -> bool:
        cache = obtenir_cache()
        cle = f"assistant_proactif:throttle:{event_type}"
        last = cache.get(cle)
        now = time.time()
        if isinstance(last, (int, float)) and now - float(last) < self.THROTTLE_S:
            return True
        cache.set(cle, now, ttl=self.THROTTLE_S, tags=["assistant", "proactif"])
        return False

    def _suggestions_contextuelles(self, event_type: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        event_lower = event_type.lower()

        if event_lower.startswith("meteo."):
            suggestions.extend(self._suggestions_meteo(data))

        if event_lower.startswith("planning."):
            suggestions.extend(self._suggestions_planning(data))

        if event_lower == "budget.depassement":
            suggestions.append(
                {
                    "module": "famille",
                    "titre": "Budget sous tension",
                    "message": "Le budget est en dépassement. Voulez-vous activer un mode courses essentielles ?",
                    "action_url": "/famille/budget",
                    "priorite": "haute",
                    "contexte": "Alerte budget",
                    "source": "eventbus",
                }
            )

        if not suggestions:
            suggestions.extend(self._suggestions_snapshot_global())

        return suggestions

    def _suggestions_meteo(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        condition = str(data.get("condition") or data.get("description") or "").lower()
        temperature = data.get("temperature")

        if "pluie" in condition:
            suggestions.append(
                {
                    "module": "famille",
                    "titre": "Pluie prévue: plan B intérieur",
                    "message": "Prévoir une activité intérieure avec Jules cet après-midi.",
                    "action_url": "/famille/activites",
                    "priorite": "normale",
                    "contexte": "Météo pluvieuse",
                    "source": "eventbus",
                }
            )
        if isinstance(temperature, (int, float)) and temperature >= 24:
            suggestions.append(
                {
                    "module": "cuisine",
                    "titre": "Menu été recommandé",
                    "message": "Il fait chaud: privilégier salades, fruits et hydratation.",
                    "action_url": "/cuisine/planning",
                    "priorite": "normale",
                    "contexte": "Température élevée",
                    "source": "eventbus",
                }
            )
        return suggestions

    def _suggestions_planning(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        charge = data.get("charge_score")

        if isinstance(charge, (int, float)) and charge >= 70:
            suggestions.append(
                {
                    "module": "planning",
                    "titre": "Semaine chargée détectée",
                    "message": "Déplacer 1 tâche non critique et anticiper les courses demain.",
                    "action_url": "/planning",
                    "priorite": "haute",
                    "contexte": "Charge planning élevée",
                    "source": "eventbus",
                }
            )

        if isinstance(charge, (int, float)) and charge <= 20:
            suggestions.append(
                {
                    "module": "famille",
                    "titre": "Créneau libre opportun",
                    "message": "Ajouter une activité famille sur un créneau léger cette semaine.",
                    "action_url": "/famille/activites",
                    "priorite": "basse",
                    "contexte": "Charge planning faible",
                    "source": "eventbus",
                }
            )
        return suggestions

    def _suggestions_snapshot_global(self) -> list[dict[str, Any]]:
        suggestions: list[dict[str, Any]] = []
        try:
            with obtenir_contexte_db() as session:
                from sqlalchemy import func

                from src.core.models import ArticleInventaire, Repas

                today = date.today()
                horizon = today + timedelta(days=3)

                repas_3j = (
                    session.query(func.count(Repas.id))
                    .filter(Repas.date_repas >= today, Repas.date_repas <= horizon)
                    .scalar()
                    or 0
                )
                stock_bas = (
                    session.query(func.count(ArticleInventaire.id))
                    .filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)
                    .scalar()
                    or 0
                )

                if int(repas_3j) < 3:
                    suggestions.append(
                        {
                            "module": "cuisine",
                            "titre": "Planning repas à compléter",
                            "message": "Moins de 3 repas planifiés sur 3 jours: générer un mini-menu.",
                            "action_url": "/cuisine/planning",
                            "priorite": "haute",
                            "contexte": "Planning court terme incomplet",
                            "source": "snapshot",
                        }
                    )

                if int(stock_bas) > 0:
                    suggestions.append(
                        {
                            "module": "cuisine",
                            "titre": "Stock bas détecté",
                            "message": f"{int(stock_bas)} produit(s) sous le seuil: préparer la liste de courses.",
                            "action_url": "/cuisine/courses",
                            "priorite": "normale",
                            "contexte": "Inventaire",
                            "source": "snapshot",
                        }
                    )
        except Exception as e:  # noqa: BLE001
            logger.warning("I.15: snapshot global indisponible: %s", e)

        return suggestions

    def _dedoublonner_limite(self, suggestions: list[dict[str, Any]], limite: int) -> list[dict[str, Any]]:
        dedup: list[dict[str, Any]] = []
        vus: set[tuple[str, str]] = set()
        for item in suggestions:
            cle = (str(item.get("module", "")), str(item.get("titre", "")))
            if cle in vus:
                continue
            vus.add(cle)
            dedup.append(item)
            if len(dedup) >= limite:
                break
        return dedup


@service_factory("assistant_proactif", tags={"assistant", "ia", "eventbus"})
def obtenir_service_assistant_proactif() -> AssistantProactifService:
    """Factory singleton du service assistant proactif."""
    return AssistantProactifService()
