"""
Service inter-modules : Dashboard → Actions rapides.

NIM4: "Anomalie budget détectée" → clic → action directe dans le module.
Ajouter des deep links depuis les widgets dashboard + endpoints d'action rapide.
"""

import logging
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DashboardActionsRapidesInteractionService:
    """Service inter-modules Dashboard → Actions rapides (deep links)."""

    @avec_gestion_erreurs(default_return={})
    def generer_deeplinks_anomalies(
        self,
        *,
        anomalies: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Génère des deep links pour les anomalies détectées au dashboard.

        Convertit les alertes/anomalies en liens cliquables vers les modules concernés
        avec pré-remplissage des paramètres pour action rapide.

        Args:
            anomalies: Liste des anomalies détectées [{"type": str, "data": dict}]

        Returns:
            Dict avec deeplinks générés et actions rapides
        """
        anomalies = anomalies or []
        deeplinks = []

        for anomalie in anomalies:
            anomalie_type = anomalie.get("type", "").lower()
            data = anomalie.get("data", {})

            link = None
            action = None

            if "budget" in anomalie_type:
                # Anomalie budget → lien vers page budget
                action_type = data.get("action", "revoir")
                link = f"/app/famille/budget?anomalie={action_type}&montant={data.get('montant', 0)}"
                action = {
                    "type": "budget_anomaly",
                    "label": f"Budget: {data.get('categorie', 'N/A')} dépassé",
                    "urgence": "haute" if data.get("pourcentage_depassement", 0) > 20 else "standard",
                }

            elif "inventaire" in anomalie_type or "stock" in anomalie_type:
                # Anomalie stock → lien vers inventaire
                link = f"/app/cuisine/inventaire?filtre=critique&quantite_min={data.get('seuil', 1)}"
                action = {
                    "type": "stock_alert",
                    "label": f"Stock: {data.get('article', 'article')} critique",
                    "urgence": "haute",
                }

            elif "peremption" in anomalie_type:
                # Anomalie péremption → lien vers cuisine/recettes
                link = f"/app/cuisine/recettes?filtre=peremption&days_left={data.get('jours_restants', 0)}"
                action = {
                    "type": "expiration_alert",
                    "label": f"⏰ {data.get('nb_articles', 1)} article(s) expirant bientôt",
                    "urgence": "très haute",
                }

            elif "planning" in anomalie_type:
                # Anomalie planning → lien vers planning
                link = f"/app/planning?action=optimiser&semaine={data.get('semaine', 'actuelle')}"
                action = {
                    "type": "planning_optimization",
                    "label": f"Planning: Variété insuffisante la semaine",
                    "urgence": "moyen",
                }

            elif "energie" in anomalie_type:
                # Anomalie énergie → lien vers maison/énergie
                link = f"/app/maison/energie?vue=consommation&pic={data.get('pic_detecte', False)}"
                action = {
                    "type": "energy_anomaly",
                    "label": f"⚡ Pic consommation détecté ({data.get('kwh', 0)}kWh)",
                    "urgence": "standard",
                }

            elif "jardin" in anomalie_type:
                # Anomalie jardin → lien vers maison/jardin
                link = f"/app/maison/jardin?action=feedback&recoltes_non_utilisees={data.get('count', 0)}"
                action = {
                    "type": "garden_feedback",
                    "label": f"🌱 {data.get('count', 0)} récolte(s) non intégrée(s)",
                    "urgence": "basse",
                }

            elif "activites" in anomalie_type or "famille" in anomalie_type:
                # Anomalie famille → lien vers famille
                link = f"/app/famille/activites?action=resume&anomalie={data.get('type', 'trends')}"
                action = {
                    "type": "family_alert",
                    "label": f"Famille: {data.get('message', 'nouvelle info')}",
                    "urgence": "standard",
                }

            if link and action:
                deeplinks.append({
                    "anomalie_type": anomalie_type,
                    "deeplink": link,
                    "action": action,
                    "data_contexte": data,
                })

        logger.info(f"✅ Deep links générés: {len(deeplinks)} liens d'action rapide créés")

        return {
            "nb_anomalies": len(anomalies),
            "nb_deeplinks": len(deeplinks),
            "deeplinks": deeplinks,
            "message": f"{len(deeplinks)} action(s) rapide(s) disponible(s).",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def executer_action_rapide_dashboard(
        self,
        *,
        action_id: str,
        anomalie_data: dict | None = None,
        db=None,
    ) -> dict[str, Any]:
        """Exécute une action rapide depuis le dashboard.

        Permet de passer directement d'une anomalie détectée à une action
        (ex: ajouter au panier, modifier budget, etc).

        Args:
            action_id: Identifiant de l'action (ex: "budget_anomaly", "stock_alert")
            anomalie_data: Données contextes de l'anomalie
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec résultat de l'action exécutée
        """
        anomalie_data = anomalie_data or {}
        action_id_lower = action_id.lower()

        try:
            if action_id_lower == "budget_anomaly":
                # Action: réviser le budget de la catégorie
                from src.core.models.finances import BudgetFamille

                categorie = anomalie_data.get("categorie", "alimentation")
                montant_limite = anomalie_data.get("montant_limite", 500)

                # Dépréciation : créer un ajustement budgétaire
                ajustement = BudgetFamille(
                    date=anomalie_data.get("date"),
                    montant=-50,  # Ajustement par défaut
                    categorie=categorie,
                    description="Ajustement rapide depuis anomalie dashboard",
                    est_recurrent=False,
                )
                db.add(ajustement)
                db.commit()

                return {
                    "action_id": action_id,
                    "statut": "success",
                    "message": f"Ajustement budgétaire de -50€ appliqué à {categorie}",
                }

            elif action_id_lower == "stock_alert":
                # Action: ajouter article à la liste de courses
                from src.core.models.courses import ArticleCourses, ListeCourses

                ingredient_id = anomalie_data.get("article_id")  # Parfois nommé article_id
                if not ingredient_id:
                    return {"action_id": action_id, "statut": "error", "message": "Article non trouvé"}

                # Ajouter à la liste de courses par défaut (ID 1)
                article = db.query(ArticleCourses).filter(ArticleCourses.ingredient_id == ingredient_id).first()
                if not article:
                    liste = db.query(ListeCourses).filter(ListeCourses.id == 1).first()
                    if not liste:
                        return {"action_id": action_id, "statut": "error", "message": "Liste de courses non trouvée"}

                    # Créer un nouvel article de courses
                    article = ArticleCourses(
                        liste_id=liste.id,
                        ingredient_id=ingredient_id,
                        quantite_necessaire=1.0,
                        priorite="moyenne",
                        achete=False,
                    )
                    db.add(article)
                    db.commit()

                    return {
                        "action_id": action_id,
                        "statut": "success",
                        "message": f"Article ajouté à la liste de courses",
                    }
                else:
                    return {
                        "action_id": action_id,
                        "statut": "success",
                        "message": "Article déjà dans la liste de courses",
                    }

            elif action_id_lower == "expiration_alert":
                # Action: suggérer des recettes avec les articles expirant
                return {
                    "action_id": action_id,
                    "statut": "success",
                    "message": "Redirect vers page recettes (filtre articles expirant)",
                    "deeplink": "/app/cuisine/recettes?filtre=peremption",
                }

            elif action_id_lower == "planning_optimization":
                # Action: consulter optimisations du planning
                return {
                    "action_id": action_id,
                    "statut": "success",
                    "message": "Recommandations de variété générées",
                    "deeplink": "/app/planning?mode=optimisation",
                }

            else:
                return {
                    "action_id": action_id,
                    "statut": "error",
                    "message": f"Action '{action_id}' non reconnue",
                }

        except Exception as e:
            logger.error(f"❌ Erreur exécution action rapide {action_id}: {e}")
            return {
                "action_id": action_id,
                "statut": "error",
                "message": str(e),
            }


@service_factory("dashboard_actions_rapides", tags={"dashboard", "actions", "anomalies"})
def get_dashboard_actions_rapides_service() -> DashboardActionsRapidesInteractionService:
    """Factory pour le service inter-modules Dashboard→Actions rapides."""
    return DashboardActionsRapidesInteractionService()
