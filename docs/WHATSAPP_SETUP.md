# WhatsApp Setup — Assistant MaTanne (Deprecated)

> Documentation obsolète. La migration cible est Telegram Bot API.
> Utiliser en priorité `docs/TELEGRAM_SETUP.md`.

---

## Vue d'ensemble

L'intégration WhatsApp sert à:

- recevoir des messages utilisateurs (webhook)
- répondre via commandes conversationnelles
- envoyer des notifications/rappels

Fichiers clés:

- `src/api/routes/webhooks_whatsapp.py`
- `src/services/integrations/whatsapp.py`
- `src/api/routes/push.py` (orchestration notification)

---

## Pré-requis Meta

- Compte Meta Developer
- App Meta configurée
- Numéro WhatsApp Business vérifié
- Token d'accès long terme
- Verify token webhook

---

## Variables d'environnement

Exemple minimal (dans `.env.local`):

```env
WHATSAPP_VERIFY_TOKEN=change-me
WHATSAPP_ACCESS_TOKEN=change-me
WHATSAPP_PHONE_NUMBER_ID=1234567890
WHATSAPP_BUSINESS_ACCOUNT_ID=1234567890
```

Recommandations:

- ne jamais commiter ces valeurs
- rotation périodique du token
- utiliser les secrets de plateforme en production

---

## Configuration webhook Meta

URL webhook (GET + POST):

- `https://<votre-domaine>/api/v1/whatsapp/webhook`

Vérification:

1. Meta envoie `hub.mode`, `hub.verify_token`, `hub.challenge`
2. L'API compare avec `WHATSAPP_VERIFY_TOKEN`
3. Si OK: retourne `hub.challenge`

---

## Structure de la route

`src/api/routes/webhooks_whatsapp.py` expose:

- `GET /api/v1/whatsapp/webhook` : vérification Meta
- `POST /api/v1/whatsapp/webhook` : réception événements/messages

Le module inclut une machine d'état conversationnelle pour plusieurs intents (planning notamment).

---

## Tests rapides

### Vérifier l'endpoint GET

```bash
curl "http://localhost:8000/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=change-me&hub.challenge=12345"
```

Résultat attendu:

- `12345` si verify token correct

### Simuler un payload POST

Utiliser Postman/curl avec un payload Meta webhook simplifié et vérifier les logs backend.

---

## Commandes conversationnelles recommandées

Implémentées ou prévues selon phase:

- planning (valider/modifier/regénérer)
- rappels courts
- aide admin
- notifications multi-canal

---

## Sécurité et robustesse

- valider la signature Meta quand activée
- ajouter rate limiting des envois
- valider format des numéros
- logger les erreurs de parsing sans `pass` silencieux
- prévoir un fallback canal si WhatsApp indisponible

---

## Dépannage

### Meta ne valide pas le webhook

- vérifier URL publique
- vérifier verify token identique
- vérifier endpoint GET accessible sans auth

### Messages non reçus

- vérifier abonnement webhook Meta
- vérifier permissions app/numéro
- inspecter les logs de `webhooks_whatsapp.py`

### Messages sortants échouent

- vérifier access token
- vérifier phone number id
- vérifier quotas WhatsApp Business

---

## Checklist mise en production

- variables d'environnement en secrets
- webhook validé en HTTPS
- alerting sur erreurs webhook
- test de bout en bout entrant + sortant
- documentation des intents supportés
