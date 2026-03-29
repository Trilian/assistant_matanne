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
- types et payloads: `src/services/core/notifications/types.py`
- préférences modèle: `src/core/models/notifications.py`
- administration et tests: `src/api/routes/admin.py`

Le dispatcher choisit les canaux demandés et renvoie un résultat par canal.

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
| `POST` | `/api/v1/admin/notifications/test` | envoyer un message de test |

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

- pas encore de failover configurable entre canaux
- pas encore de digest centralisé multi-canal
- pas encore de throttling global anti-spam
- envoi WhatsApp à confirmer selon l'environnement cible

Ces points sont explicitement planifiés pour les phases notifications suivantes.