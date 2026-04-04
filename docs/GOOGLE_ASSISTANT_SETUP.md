# Google Assistant Setup — Assistant MaTanne

> Configuration de l'integration Google Assistant (intents + fulfillment webhook).

---

## Vue d'ensemble

L'integration Google Assistant permet:

- de lister les intents supportes cote backend
- d'executer les intents via API interne
- de brancher un webhook fulfillment (Dialogflow CX/ES ou Actions)

Fichiers cles:

- `src/api/routes/assistant.py`
- `frontend/src/app/(app)/outils/google-assistant/page.tsx`
- `frontend/src/bibliotheque/api/assistant.ts`

---

## Endpoints disponibles

### Intents supportes

- `GET /api/v1/assistant/google-assistant/intents`

Retourne la liste des intents, slots requis et action attendue.

### Execution d'intent (interne)

- `POST /api/v1/assistant/google-assistant/executer`

Payload:

```json
{
  "intent": "courses_ajouter_article",
  "slots": {"article": "lait"},
  "langue": "fr-FR"
}
```

### Webhook fulfillment (Google Assistant)

- `POST /api/v1/assistant/google-assistant/webhook`

Le webhook accepte les formats usuels (`intent.displayName`, `queryResult.intent.displayName`, `sessionInfo.parameters`).

---

## Variables d'environnement

Ajouter dans `.env.local` (recommande):

```env
GOOGLE_ASSISTANT_WEBHOOK_SECRET=change-me
# Optionnel pour embeddings externes utilises par cache semantique IA
MISTRAL_EMBEDDINGS_MODEL=mistral-embed
```

Si `GOOGLE_ASSISTANT_WEBHOOK_SECRET` est defini, le header suivant devient obligatoire:

- `x-assistant-secret: <valeur>`

---

## Configuration Dialogflow (resume)

1. Creer un webhook vers:
- `https://<votre-domaine>/api/v1/assistant/google-assistant/webhook`

2. Activer le webhook sur les intents concernes.

3. Mapper les parametres vers `sessionInfo.parameters` (ou `queryResult.parameters`).

4. Cote backend, les intents supportes actuels sont:
- `courses_ajouter_article`
- `planning_resume_demain`
- `routines_creer_rappel`

---

## Tests rapides

### 1) Lister les intents

```bash
curl -X GET "http://localhost:8000/api/v1/assistant/google-assistant/intents" \
  -H "Authorization: Bearer <token>"
```

### 2) Executer un intent via API interne

```bash
curl -X POST "http://localhost:8000/api/v1/assistant/google-assistant/executer" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "courses_ajouter_article",
    "slots": {"article": "pommes"},
    "langue": "fr-FR"
  }'
```

### 3) Simuler un payload webhook fulfillment

```bash
curl -X POST "http://localhost:8000/api/v1/assistant/google-assistant/webhook" \
  -H "Content-Type: application/json" \
  -H "x-assistant-secret: change-me" \
  -d '{
    "intent": {"displayName": "planning_resume_demain"},
    "sessionInfo": {"parameters": {}},
    "languageCode": "fr"
  }'
```

Reponse attendue:
- champ `fulfillment_response.messages[0].text.text[0]`
- metadonnees dans `sessionInfo.parameters`

---

## UI de test dans l'app

Une page de test est disponible dans le module Outils:

- `/outils/google-assistant`

Elle permet de:

- charger dynamiquement les intents backend
- saisir des slots JSON
- executer l'intent et afficher la reponse

---

## Securite et bonnes pratiques

- Toujours definir `GOOGLE_ASSISTANT_WEBHOOK_SECRET` en production.
- Utiliser HTTPS uniquement pour le webhook public.
- Monitorer les erreurs 4xx/5xx sur `/google-assistant/webhook`.
- Limiter les intents a des actions idempotentes quand possible.
- Journaliser les intents executes sans stocker de donnees sensibles.

---

## Depannage

### 401 sur le webhook

- verifier `GOOGLE_ASSISTANT_WEBHOOK_SECRET`
- verifier le header `x-assistant-secret`

### Intent "non supporte"

- verifier le nom exact de l'intent dans Dialogflow
- comparer avec `GET /google-assistant/intents`

### Slots manquants

- le backend renvoie les `slots_requis` et `slots_manquants`
- verifier le mapping des parametres cote agent Google

---

## Checklist mise en production

- secret webhook configure
- endpoint public en HTTPS
- intent mapping verifie en preprod
- tests curl webhook + executeur OK
- supervision des erreurs activee
