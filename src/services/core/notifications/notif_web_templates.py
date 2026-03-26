"""
Templates de notifications prédéfinies.

Mixin fournissant les méthodes de notification prédéfinies
pour les différents types d'alertes.
"""

import logging

from src.services.core.notifications.types import (
    NotificationPush,
    TypeNotification,
)

logger = logging.getLogger(__name__)


class NotificationTemplatesMixin:
    """
    Mixin pour les notifications prédéfinies.

    Fournit des méthodes de haut niveau pour envoyer
    des notifications typées (stock bas, péremption, repas, etc.).
    """

    # ═══════════════════════════════════════════════════════════
    # NOTIFICATIONS PRÉDÉFINIES
    # ═══════════════════════════════════════════════════════════

    def notifier_stock_bas(self, user_id: str, nom_article: str, quantite: float):
        """Notifie un stock bas."""
        notification = NotificationPush(
            title="📦 Stock bas",
            body=f"{nom_article} est presque épuisé ({quantite} restant)",
            notification_type=TypeNotification.STOCK_BAS,
            url="/?module=cuisine.inventaire",
            tag=f"stock_{nom_article}",
            actions=[
                {"action": "add_to_cart", "title": "Ajouter aux courses"},
                {"action": "dismiss", "title": "Ignorer"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_peremption(
        self, user_id: str, nom_article: str, jours_restants: int, critique: bool = False
    ):
        """Notifie une péremption proche."""
        if jours_restants <= 0:
            title = "⚠️ Produit périmé!"
            body = f"{nom_article} a expiré!"
            notif_type = TypeNotification.PEREMPTION_CRITIQUE
        elif jours_restants == 1:
            title = "🔴 Péremption demain"
            body = f"{nom_article} expire demain"
            notif_type = (
                TypeNotification.PEREMPTION_CRITIQUE
                if critique
                else TypeNotification.PEREMPTION_ALERTE
            )
        else:
            title = "🟡 Péremption proche"
            body = f"{nom_article} expire dans {jours_restants} jours"
            notif_type = TypeNotification.PEREMPTION_ALERTE

        notification = NotificationPush(
            title=title,
            body=body,
            notification_type=notif_type,
            url="/?module=cuisine.inventaire&filter=expiring",
            tag=f"expiry_{nom_article}",
            require_interaction=critique,
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_rappel_repas(
        self, user_id: str, type_repas: str, nom_recette: str, temps_restant: str
    ):
        """Notifie un rappel de repas."""
        notification = NotificationPush(
            title=f"🍽️ {type_repas.title()} dans {temps_restant}",
            body=f"Au menu: {nom_recette}",
            notification_type=TypeNotification.RAPPEL_REPAS,
            url="/?module=planning",
            tag=f"meal_{type_repas}",
            actions=[
                {"action": "view_recipe", "title": "Voir la recette"},
                {"action": "dismiss", "title": "OK"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_liste_partagee(self, user_id: str, partage_par: str, nom_liste: str):
        """Notifie le partage d'une liste."""
        notification = NotificationPush(
            title="🛒 Liste partagée",
            body=f"{partage_par} a partagé la liste '{nom_liste}'",
            notification_type=TypeNotification.LISTE_PARTAGEE,
            url="/?module=cuisine.courses",
            actions=[
                {"action": "view", "title": "Voir"},
                {"action": "dismiss", "title": "Plus tard"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_rappel_famille(self, user_id: str, titre: str, message: str, url: str = "/?module=famille"):
        """Notifie un rappel famille (activité, jalon, rendez-vous médical...)."""
        notification = NotificationPush(
            title=f"👨‍👩‍👧 {titre}",
            body=message,
            notification_type=TypeNotification.RAPPEL_FAMILLE,
            url=url,
            tag=f"famille_{titre[:20].replace(' ', '_')}",
            actions=[
                {"action": "view", "title": "Voir"},
                {"action": "dismiss", "title": "Ignorer"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_alerte_serie_jeux(self, user_id: str, nb_defaites: int, mise_max: float = 0.0):
        """Alerte jeu responsable — série de défaites consécutives."""
        notification = NotificationPush(
            title="⚠️ Alerte jeu responsable",
            body=(
                f"{nb_defaites} défaites consécutives détectées. "
                + (f"Mise maximale recommandée : {mise_max:.0f} €. " if mise_max else "")
                + "Pensez à faire une pause."
            ),
            notification_type=TypeNotification.ALERTE_SERIE_DEFAITES,
            url="/?module=jeux.responsable",
            tag="jeux_serie_defaites",
            require_interaction=True,
            actions=[
                {"action": "view", "title": "Voir le bilan"},
                {"action": "pause", "title": "Pause 24h"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_alerte_predictive_maison(self, user_id: str, titre: str, message: str, url: str = "/?module=maison"):
        """Alerte prédictive maison (garantie expirant, entretien préventif, énergie anormale...)."""
        notification = NotificationPush(
            title=f"🏠 {titre}",
            body=message,
            notification_type=TypeNotification.ALERTE_PREDICTIVE_MAISON,
            url=url,
            tag=f"maison_pred_{titre[:20].replace(' ', '_')}",
            require_interaction=False,
            actions=[
                {"action": "view", "title": "Détails"},
                {"action": "dismiss", "title": "Compris"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    # ═══════════════════════════════════════════════════════════
    # ALIAS RÉTROCOMPATIBILITÉ
    # ═══════════════════════════════════════════════════════════

    notify_stock_low = notifier_stock_bas
    notify_expiration = notifier_peremption
    notify_meal_reminder = notifier_rappel_repas
    notify_shopping_list_shared = notifier_liste_partagee
