# Notifications

> Vue d'ensemble des canaux, préférences et points d'intégration du système de notifications.

---

## Canaux disponibles

Le projet utilise plusieurs canaux complémentaires:

- `ntfy.sh` pour les alertes immédiates simples
- Web Push pour les navigateurs enregistrés
- email pour les résumés et alertes longues
- WhatsApp pour certains rappels et résumés contextuels

---

## Architecture

Composants principaux:

- dispatcher: `src/services/core/notifications/notif_dispatcher.py`
- push web: `src/services/core/notifications/notif_web_core.py`
- ntfy: `src/services/core/notifications/notif_ntfy.py`
- email: `src/services/core/notifications/notif_email.py`
- whatsapp: `src/services/integrations/whatsapp.py`
- types et payloads: `src/services/core/notifications/types.py`
- préférences modèle: `src/core/models/notifications.py`
- historique modèle: `src/core/models/notifications_sprint_e.py` (table `historique_notifications`)
- administration et tests: `src/api/routes/admin.py`

Le dispatcher choisit les canaux en fonction :
1. Des canaux demandés explicitement par le code appelant
2. Du `_MAPPING_EVENEMENTS_CANAUX` (type d'événement → catégorie + canaux par défaut)
3. Des préférences utilisateur (`canaux_par_categorie`)
4. D'une séquence de failover automatique : push → ntfy → whatsapp → email

---

## Préférences utilisateur

Les préférences sont stockées dans `PreferenceNotification` avec notamment:

- activation des grandes familles d'alertes
- heures silencieuses
- modules actifs
- canal préféré
- `canaux_par_categorie`

Structure `canaux_par_categorie` attendue:

```json
{
  "rappels": ["push", "ntfy"],
  "alertes": ["push", "ntfy", "email"],
  "resumes": ["email"]
}
```

Interface frontend:

- page paramètres: `frontend/src/app/(app)/parametres/page.tsx`
- activation push navigateur
- configuration par catégorie de canaux

---

## Endpoints utiles

### Push web

| Méthode | Route | Usage |
|---------|-------|-------|
| `POST` | `/api/v1/push/subscribe` | enregistrer un abonnement |
| `DELETE` | `/api/v1/push/unsubscribe` | supprimer un abonnement |
| `GET` | `/api/v1/push/status` | connaître le statut courant |

### Admin

| Méthode | Route | Usage |
|---------|-------|-------|
| `POST` | `/api/v1/admin/notifications/test` | envoyer un message de test sur un canal |
| `POST` | `/api/v1/admin/notifications/test-all` | tester tous les canaux avec failover |

---

## Historique des notifications

Les notifications envoyées sont historisées dans la table `historique_notifications` (modèle `HistoriqueNotification`).

Colonnes : `user_id`, `canal`, `titre`, `message`, `type_evenement`, `categorie`, `lu`, `action_effectuee`, `metadata` (JSONB).

Le frontend peut utiliser cet historique pour afficher un centre de notifications.

---

## Cas d'usage déjà implémentés

Exemples confirmés dans le code:

- documents proches expiration -> notification ntfy
- jalon Jules ajouté -> suggestion d'activités + notification ntfy
- rappels famille -> WhatsApp
- rappel repas du soir -> ntfy + push
- rapport mensuel budget -> multi-canal
- jobs de stock bas -> ntfy

Les jobs planifiés s'appuient largement sur le dispatcher pour unifier l'envoi.

---

## Administration et tests

Depuis le module admin, il est possible de:

- envoyer un test `ntfy`
- envoyer un test `push`
- envoyer un test `email`
- envoyer un test `whatsapp`

Recommandation:

- tester chaque canal après changement de secret ou d'environnement
- conserver un utilisateur admin abonné au push pour les validations rapides

---

## Limitations actuelles

- Envoi WhatsApp dépend de l'environnement cible (clé Meta API requise)
- Le digest multi-canal pourrait être étendu à plus de cas d'usage

Les fonctionnalités de base (failover, throttling, historique) sont opérationnelles.