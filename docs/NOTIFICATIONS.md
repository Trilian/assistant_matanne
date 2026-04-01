# Notifications

> Système de notifications multi-canal unifié avec failover, throttling, digest et préférences utilisateur.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Architecture

### Composants

| Composant | Fichier | Rôle |
| ----------- | --------- | ------ |
| **Dispatcher** | `src/services/core/notifications/notif_dispatcher.py` | Routeur central vers tous les canaux |
| **Types** | `src/services/core/notifications/types.py` | Enums, modèles Pydantic, constantes |
| **ntfy** | `src/services/core/notifications/notif_ntfy.py` | Push ntfy.sh |
| **Push Web** | `src/services/core/notifications/notif_web_core.py` | Web Push VAPID |
| **Email** | `src/services/core/notifications/notif_email.py` | Email via Resend |
| **WhatsApp** | `src/services/integrations/whatsapp.py` | WhatsApp via Meta Cloud API |
| **Templates push** | `src/services/core/notifications/notif_web_templates.py` | Templates push prédéfinies |
| **Persistence** | `src/services/core/notifications/notif_web_persistence.py` | Stockage abonnements push |
| **Inventaire** | `src/services/core/notifications/inventaire.py` | Alertes inventaire locales |
| **Templates email** | `src/services/core/notifications/templates/` | Templates Jinja2 HTML |

### Modèles ORM

| Modèle | Table | Fichier |
| -------- | ------- | --------- |
| `AbonnementPush` | `abonnements_push` | `src/core/models/notifications.py` |
| `PreferenceNotification` | `preferences_notifications` | `src/core/models/notifications.py` |
| `WebhookAbonnement` | `webhooks_abonnements` | `src/core/models/notifications.py` |
| `HistoriqueNotification` | `historique_notifications` | `src/core/models/notifications_sprint_e.py` |

---

## Canaux disponibles

| Canal | Fournisseur | Usage | Variables d'environnement |
| ------- | ------------- | ------- | -------------------------- |
| **ntfy** | [ntfy.sh](https://ntfy.sh) | Push alertes immédiates (topic: `matanne-famille`) | Topic par défaut dans `types.py` |
| **push** | Web Push API (VAPID) | Notifications navigateur | `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_EMAIL` |
| **email** | [Resend](https://resend.com) | Résumés, rapports, alertes longues | `RESEND_API_KEY`, `EMAIL_FROM`, `FRONTEND_URL` |
| **whatsapp** | Meta Cloud API | Rappels contextuels, digests (1000 conv/mois tier gratuit) | `META_WHATSAPP_TOKEN`, `META_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_USER_NUMBER` |

---

## Chaîne de failover

Le dispatcher implémente un **failover en cascade** pour la fiabilité :

```python
_FALLBACK_CANAUX = {
    "push":     ["ntfy", "whatsapp", "email"],
    "ntfy":     ["push", "whatsapp", "email"],
    "whatsapp": ["push", "email"],
    "email":    ["push", "ntfy"],
}
```

- `strategie="failover"` → essaie chaque canal en séquence, **s'arrête au premier succès**
- `strategie="parallel"` (défaut) → tente tous les canaux, retourne tous les résultats

---

## Résolution des canaux

Le dispatcher résout les canaux dans cet **ordre de priorité** :

1. **Requête explicite** : paramètre `canaux=["push", "email"]`
2. **Mapping événement** : `_MAPPING_EVENEMENTS_CANAUX[type_evenement]` → catégorie + canaux défaut
3. **Préférences utilisateur** : `canaux_par_categorie` du profil (stocké en DB)
4. **Intersection** : si mapping ET préférences existent → intersection + extras
5. **Fallback** : `canal_prefere` de l'utilisateur (défaut: `"push"`)
6. **Défaut** : `["ntfy", "push"]`

### Mapping événement → canaux

```python
_MAPPING_EVENEMENTS_CANAUX = {
    "peremption_j2":             {"categorie": "alertes",  "canaux": ["push", "ntfy"]},
    "rappel_courses":            {"categorie": "rappels",  "canaux": ["push", "ntfy", "whatsapp"]},
    "resume_hebdo":              {"categorie": "resumes",  "canaux": ["whatsapp", "email"]},
    "rapport_budget_mensuel":    {"categorie": "resumes",  "canaux": ["email"]},
    "anniversaire_j7":           {"categorie": "rappels",  "canaux": ["push", "ntfy", "whatsapp"]},
    "tache_entretien_urgente":   {"categorie": "alertes",  "canaux": ["push", "ntfy", "whatsapp"]},
    # ... 10+ mappings configurés
}
```

Catégories : `rappels`, `alertes`, `resumes`

---

## Throttling et mode digest

### Limite par utilisateur

- **Max par heure** : 5 (configurable dans `modules_actifs`)
- **Suivi en mémoire** : `_compteurs_heure[user_id][YYYYMMDDHH]`
- Quand la limite est atteinte → les notifications sont bufferisées dans la file digest

### File digest

- File en mémoire : `_digest_queue[user_id]`
- **Les alertes contournent toujours le digest** (envoi immédiat)
- Les rappels/résumés peuvent être digérés si `mode_digest=true`
- `dispatcher.vider_digest(user_id)` consolide les ~10 derniers messages et envoie via failover
- Job CRON `digest_notifications_queue` flush automatiquement toutes les 2h

---

## Types de notification (TypeNotification)

```python
# Inventaire
STOCK_BAS, PEREMPTION_ALERTE, PEREMPTION_CRITIQUE

# Planning
RAPPEL_REPAS, RAPPEL_ACTIVITE

# Courses
LISTE_PARTAGEE, LISTE_MISE_A_JOUR

# Famille
RAPPEL_JALON, RAPPEL_SANTE, RAPPEL_FAMILLE

# Jeux
RESULTAT_PARI_GAGNE, RESULTAT_PARI_PERDU, RESULTAT_LOTO, RESULTAT_LOTO_GAIN

# Maison
ALERTE_PREDICTIVE_MAISON, ALERTE_GARANTIE

# Gamification
BADGE_DEBLOQUE

# Système
MISE_A_JOUR_SYSTEME, SYNC_TERMINEE
```

---

## Templates

### Templates email (Jinja2)

| Template | Usage |
| ---------- | ------- |
| `base.html` | Template de base (styling) |
| `reset_password.html` | Lien de réinitialisation |
| `verification_email.html` | Vérification email à l'inscription |
| `resume_hebdo.html` | Résumé familial hebdomadaire |
| `rapport_mensuel.html` | Rapport budget mensuel |
| `alerte_critique.html` | Alertes critiques (stock = 0, urgence) |
| `invitation_famille.html` | Invitation membre famille |
| `digest.html` | Digest de notifications bufferisées |

### Templates push prédéfinies

| Fonction | Icône | Usage |
| ---------- | ------- | ------- |
| `notifier_stock_bas()` | 📦 | Stock bas |
| `notifier_peremption()` | ⚠️ | Alertes péremption |
| `notifier_rappel_repas()` | 🍽️ | Rappels repas |
| `notifier_liste_partagee()` | 🛒 | Liste courses partagée |
| `notifier_rappel_famille()` | 👨‍👩‍👧 | Rappels famille |
| `notifier_alerte_predictive_maison()` | 🏠 | Alertes maison |
| `notifier_pari_gagne()` | 🎉 | Pari gagné |

---

## Préférences utilisateur

Stockées dans `PreferenceNotification` :

```json
{
  "user_id": "uuid-xxx",
  "canal_prefere": "push",
  "canaux_par_categorie": {
    "rappels": ["push", "ntfy"],
    "alertes": ["push", "ntfy", "email"],
    "resumes": ["email"]
  },
  "modules_actifs": {
    "max_par_heure": 5,
    "mode_digest": false
  },
  "quiet_hours_start": 22,
  "quiet_hours_end": 7
}
```

Interface frontend : page paramètres `frontend/src/app/(app)/parametres/page.tsx`

---

## Rate limiting WhatsApp

- **Par destinataire** : 10 messages/heure
- **Global quotidien** : 100 messages/jour
- Persisté dans la table `etats_persistants` avec fenêtre glissante 48h

---

## Endpoints API

### Push Web

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/push/vapid-public-key` | Clé publique VAPID |
| `POST` | `/api/v1/push/subscribe` | Enregistrer abonnement navigateur |
| `DELETE` | `/api/v1/push/unsubscribe` | Supprimer abonnement |
| `GET` | `/api/v1/push/status` | Nombre d'abonnements |

### Webhooks sortants

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/webhooks` | Créer webhook sortant |
| `GET` | `/api/v1/webhooks` | Lister webhooks utilisateur |
| `GET` | `/api/v1/webhooks/{id}` | Détail webhook |
| `PUT` | `/api/v1/webhooks/{id}` | Modifier webhook |
| `DELETE` | `/api/v1/webhooks/{id}` | Supprimer webhook |
| `POST` | `/api/v1/webhooks/{id}/test` | Tester connectivité |

### WhatsApp (réception)

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/whatsapp/webhook` | Vérification Meta (challenge) |
| `POST` | `/api/v1/whatsapp/webhook` | Réception messages + réponses boutons |

### Admin notifications

| Méthode | Route | Usage |
| --------- | ------- | ------- |
| `POST` | `/api/v1/admin/notifications/test` | Test sur un canal |
| `POST` | `/api/v1/admin/notifications/test-all` | Test multi-canal avec failover |
| `GET` | `/api/v1/admin/notifications/channels` | Canaux configurés + statut |
| `GET` | `/api/v1/admin/notifications/queue` | File d'attente digest |
| `POST` | `/api/v1/admin/notifications/queue/{user_id}/retry` | Forcer envoi digest |
| `DELETE` | `/api/v1/admin/notifications/queue/{user_id}` | Vider file d'attente |

---

## Historique des notifications

Les notifications envoyées sont historisées dans `historique_notifications`.

Colonnes : `user_id`, `canal`, `titre`, `message`, `type_evenement`, `categorie`, `lu`, `action_effectuee`, `metadata` (JSONB).

---

## Exemples d'utilisation

```python
from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

dispatcher = get_dispatcher_notifications()

# 1. Envoi avec canaux explicites
resultats = dispatcher.envoyer(
    user_id="user123",
    message="Stock alerte !",
    canaux=["push", "ntfy"],
    titre="⚠️ Alert",
)
# → {"push": True, "ntfy": True}

# 2. Envoi basé sur événement (routage auto + failover)
resultats = dispatcher.envoyer_evenement(
    user_id="user123",
    type_evenement="peremption_j2",
    message="Yaourt expire demain",
    priorite=4,
    tags=["warning"],
)

# 3. Envoi forcé (bypass throttling)
resultats = dispatcher.envoyer(
    user_id="user123",
    message="URGENT",
    forcer=True,
)

# 4. Email avec template
resultats = dispatcher.envoyer(
    user_id="user123",
    message={"titre": "Budget", "data": {...}},
    canaux=["email"],
    type_email="rapport_mensuel",
    email="user@example.com",
)

# 5. Gestion file digest
pending = dispatcher.lister_users_digest_pending()
dispatcher.vider_digest("user1")
```

---

## Patterns de conception

| Pattern | Lieu | Usage |
| --------- | ------ | ------- |
| **Service Factory** | `get_dispatcher_notifications()` | Singleton via registre |
| **Mixin Composition** | `ServiceWebPush` | Canal modulaire (templates + persistence) |
| **Strategy** | `strategie="parallel\|failover"` | Algorithmes d'envoi interchangeables |
| **Template Method** | `notifier_*()` | Builders push prédéfinis |
| **In-Memory Queue** | `_digest_queue` + `_compteurs_heure` | Pas de dépendance DB pour le throttling |
| **Best-Effort** | Chargement préférences | Dégradation silencieuse si DB indisponible |

---

## Résilience

- Tous les envois canal wrappés en `try-except` → log erreur, retourne `False`
- Failover garantit au moins un succès si configuré
- File digest préserve les messages throttlés (pas de perte)
- Rate limits WhatsApp vérifiés en DB d'abord, fallback in-memory
- Config email manquante → skip gracieux du canal email
