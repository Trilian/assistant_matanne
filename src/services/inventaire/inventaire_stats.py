"""
Mixin Statistiques & Alertes pour le service inventaire.

Contient les méthodes de statistiques et notifications:
- Génération de notifications d'alertes
- Récupération des alertes actives
- Statistiques globales et par catégorie
- Articles à prélever en priorité (FIFO)
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from src.core.decorators import avec_gestion_erreurs

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class InventaireStatsMixin:
    """Mixin pour les statistiques et alertes de l'inventaire.

    Méthodes déléguées depuis ServiceInventaire:
    - generer_notifications_alertes
    - obtenir_alertes_actives
    - get_statistiques
    - get_stats_par_categorie
    - get_articles_a_prelever

    Utilise self.get_inventaire_complet() et self.get_alertes()
    du service principal (cooperative mixin pattern).
    """

    @avec_gestion_erreurs(default_return={})
    def generer_notifications_alertes(self) -> dict[str, Any]:
        """Génère les notifications d'alertes selon l'état de l'inventaire.

        Returns:
            Dict avec notifications créées par type
        """
        from src.services.core.notifications import obtenir_service_notifications

        service_notifs = obtenir_service_notifications()
        inventaire = self.get_inventaire_complet()
        stats = {
            "stock_critique": [],
            "stock_bas": [],
            "peremption_proche": [],
            "peremption_depassee": [],
        }

        # Vérifie chaque article
        for article_data in inventaire["articles"]:
            date_peremption = article_data.get("date_peremption")

            # Check stock critique
            if article_data.get("est_critique"):
                notif = service_notifs.creer_notification_stock_critique(article_data)
                if notif:
                    service_notifs.ajouter_notification(notif)
                    stats["stock_critique"].append(article_data["nom"])

            # Check stock bas
            elif article_data.get("est_stock_bas"):
                notif = service_notifs.creer_notification_stock_bas(article_data)
                if notif:
                    service_notifs.ajouter_notification(notif)
                    stats["stock_bas"].append(article_data["nom"])

            # Check péremption
            if date_peremption:
                jours_avant = (date_peremption - date.today()).days
                if jours_avant <= 7:  # Alerter si <= 7 jours
                    notif = service_notifs.creer_notification_peremption(article_data, jours_avant)
                    if notif:
                        service_notifs.ajouter_notification(notif)
                        if jours_avant <= 0:
                            stats["peremption_depassee"].append(article_data["nom"])
                        else:
                            stats["peremption_proche"].append(article_data["nom"])

        logger.info(
            f"📊 Notifications générées: "
            f"Critique={len(stats['stock_critique'])}, "
            f"Bas={len(stats['stock_bas'])}, "
            f"Péremption={len(stats['peremption_proche']) + len(stats['peremption_depassee'])}"
        )

        return stats

    @avec_gestion_erreurs(default_return=[])
    def obtenir_alertes_actives(self) -> list[dict[str, Any]]:
        """Récupère les alertes actives pour l'utilisateur.

        Returns:
            Liste des notifications non lues
        """
        from src.services.core.notifications import obtenir_service_notifications

        service_notifs = obtenir_service_notifications()
        notifs = service_notifs.obtenir_notifications(non_lues_seulement=True)

        return [
            {
                "id": notif.id,
                "titre": notif.titre,
                "message": notif.message,
                "icone": notif.icone,
                "type": notif.type_alerte.value,
                "priorite": notif.priorite,
                "article_id": notif.article_id,
                "date": notif.date_creation.isoformat(),
            }
            for notif in notifs
        ]

    @avec_gestion_erreurs(default_return={})
    def get_statistiques(self) -> dict[str, Any]:
        """Récupère statistiques complètes de l'inventaire.

        Returns:
            Dict with statistics and insights
        """
        inventaire = self.get_inventaire_complet()
        alertes = self.get_alertes()

        if not inventaire:
            return {"total_articles": 0}

        return {
            "total_articles": len(inventaire),
            "total_quantite": sum(a["quantite"] for a in inventaire),
            "emplacements": len(set(a["emplacement"] for a in inventaire if a["emplacement"])),
            "categories": len(set(a["ingredient_categorie"] for a in inventaire)),
            "alertes_totales": sum(len(v) for v in alertes.values()),
            "articles_critiques": len(alertes.get("critique", [])),
            "articles_stock_bas": len(alertes.get("stock_bas", [])),
            "articles_peremption": len(alertes.get("peremption_proche", [])),
            "derniere_maj": max((a.get("derniere_maj") for a in inventaire), default=None),
        }

    @avec_gestion_erreurs(default_return={})
    def get_stats_par_categorie(self) -> dict[str, dict[str, Any]]:
        """Récupère statistiques par catégorie.

        Returns:
            Dict with per-category statistics
        """
        inventaire = self.get_inventaire_complet()

        categories = {}
        for article in inventaire:
            cat = article["ingredient_categorie"]
            if cat not in categories:
                categories[cat] = {
                    "articles": 0,
                    "quantite_totale": 0,
                    "seuil_moyen": 0,
                    "critiques": 0,
                }

            categories[cat]["articles"] += 1
            categories[cat]["quantite_totale"] += article["quantite"]
            categories[cat]["seuil_moyen"] += article["quantite_min"]
            if article["statut"] == "critique":
                categories[cat]["critiques"] += 1

        # Calculer moyenne des seuils
        for cat in categories:
            if categories[cat]["articles"] > 0:
                categories[cat]["seuil_moyen"] /= categories[cat]["articles"]

        logger.info(f"📊 Statistics for {len(categories)} categories")
        return categories

    @avec_gestion_erreurs(default_return=[])
    def get_articles_a_prelever(self, date_limite: date | None = None) -> list[dict[str, Any]]:
        """Récupère articles à utiliser en priorité.

        Args:
            date_limite: Date limite de péremption (par défaut aujourd'hui + 3 jours)

        Returns:
            List of articles to use first (FIFO)
        """

        if date_limite is None:
            date_limite = date.today() + timedelta(days=3)

        inventaire = self.get_inventaire_complet()

        a_prelever = [
            a for a in inventaire if a["date_peremption"] and a["date_peremption"] <= date_limite
        ]

        # Trier par date de péremption (plus ancien d'abord)
        a_prelever.sort(key=lambda x: x["date_peremption"])

        return a_prelever


__all__ = [
    "InventaireStatsMixin",
]
