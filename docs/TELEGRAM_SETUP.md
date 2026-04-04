# Telegram Setup — Assistant MaTanne

> Configuration de l'intégration Telegram Bot API pour les notifications conversationnelles.
> 100% gratuit — aucune limite de messages, pas de catégories payantes.

---

## Vue d'ensemble

L'intégration Telegram sert à :

- Recevoir des commandes utilisateur (via webhook)
- Répondre via messages conversationnels
- Envoyer des notifications proactives (digest matin, planning, courses, entretien...)
- Valider des actions via boutons interactifs (InlineKeyboard)

Fichiers clés :

- `src/services/integrations/telegram.py` — Client Telegram (envoi messages + boutons)
- `src/api/routes/webhooks_telegram.py` — Webhook réception (messages + callback_query)

---

## Étape 1 — Créer le bot via @BotFather

1. Ouvre **Telegram** (app mobile, desktop ou [web.telegram.org](https://web.telegram.org))
2. Cherche **@BotFather** dans la barre de recherche
3. Envoie `/start` puis `/newbot`
4. Choisis un **nom affiché** (ex: `Assistant Matanne`)
5. Choisis un **username** terminant par `bot` (ex: `assistant_matanne_bot`)
6. BotFather répond avec le **token** :

```
Done! Congratulations on your new bot.
Use this token to access the HTTP API:
123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

7. **Copie le token** — c'est ton `TELEGRAM_BOT_TOKEN`

### Commandes optionnelles via BotFather

```
/setdescription    → "Assistant familial Matanne — planning, courses, maison"
/setabouttext      → "Bot privé pour la gestion de la famille"
/setuserpic        → Envoyer une image de profil pour le bot
/setcommands       → Définir les commandes du bot :
    planning - Voir le planning de la semaine
    courses - Voir la liste de courses
    aide - Aide et commandes disponibles
```

---

## Étape 2 — Obtenir ton Chat ID

Le Chat ID identifie ta conversation avec le bot. Il est nécessaire pour que le bot t'envoie des messages proactifs.

### Méthode rapide

1. Envoie **n'importe quel message** à ton bot (ex: `Bonjour`)
2. Ouvre cette URL dans ton navigateur (remplace `TOKEN` par ton token) :

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

3. Dans la réponse JSON, trouve `"chat":{"id": 123456789}` — c'est ton **Chat ID**

### Exemple de réponse

```json
{
  "ok": true,
  "result": [
    {
      "update_id": 123,
      "message": {
        "chat": {
          "id": 123456789,      ← TON CHAT ID
          "first_name": "Prénom",
          "type": "private"
        },
        "text": "Bonjour"
      }
    }
  ]
}
```

> **Astuce** : Si `result` est vide, envoie d'abord un message au bot puis recharge l'URL.

---

## Étape 3 — Configurer les variables d'environnement

Ajoute dans `.env.local` (racine du projet) :

```env
# === Telegram Bot API ===
TELEGRAM_BOT_TOKEN=123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
TELEGRAM_CHAT_ID=123456789
```

> Ne jamais commiter ces valeurs. En production (Railway), les ajouter via le dashboard variables.

---

## Étape 4 — Configurer le webhook

Le webhook permet à Telegram d'envoyer les messages reçus à ton API.

### En développement (localhost)

Telegram ne peut pas envoyer vers `localhost`. Deux options :

**Option A — ngrok (recommandé pour dev)**

```bash
# Installer ngrok : https://ngrok.com/download
ngrok http 8000
# Copie l'URL HTTPS (ex: https://abc123.ngrok-free.app)
```

**Option B — Polling (pas de webhook, pour tests rapides)**

Le bot peut fonctionner sans webhook en mode polling. Non recommandé en production.

### Enregistrer le webhook

Remplacer `<TOKEN>` et `<URL>` :

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "<URL>/api/v1/telegram/webhook"}'
```

Exemple :

```bash
# Dev avec ngrok
curl -X POST "https://api.telegram.org/bot123:AAH.../setWebhook" \
  -d '{"url": "https://abc123.ngrok-free.app/api/v1/telegram/webhook"}'

# Production Railway
curl -X POST "https://api.telegram.org/bot123:AAH.../setWebhook" \
  -d '{"url": "https://assistant-matanne.railway.app/api/v1/telegram/webhook"}'
```

### Vérifier le webhook

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

Réponse attendue :

```json
{
  "ok": true,
  "result": {
    "url": "https://assistant-matanne.railway.app/api/v1/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## Étape 5 — Tester l'envoi

### Test rapide (sans lancer l'app)

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<CHAT_ID>", "text": "🚀 Bot Matanne connecté !", "parse_mode": "HTML"}'
```

Si tu reçois le message sur Telegram → le bot fonctionne.

> Pour la validation fonctionnelle complète du hub Telegram, voir aussi `docs/TELEGRAM_RECETTES.md`.

### Test avec boutons interactifs

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "<CHAT_ID>",
    "text": "🍽️ <b>Planning test</b>\n\nLundi : Poulet rôti\nMardi : Pâtes",
    "parse_mode": "HTML",
    "reply_markup": {
      "inline_keyboard": [
        [{"text": "✅ Valider", "callback_data": "planning_valider"}],
        [{"text": "✏️ Modifier", "callback_data": "planning_modifier"}],
        [{"text": "🔄 Régénérer", "callback_data": "planning_regenerer"}]
      ]
    }
  }'
```

---

## Structure des routes

`src/api/routes/webhooks_telegram.py` expose :

- `POST /api/v1/telegram/webhook` — Réception des updates Telegram

Types d'updates gérés :

| Type | Contenu | Action |
|------|---------|--------|
| `message` | Texte envoyé par l'utilisateur | Commande conversationnelle (planning, courses, aide) |
| `callback_query` | Clic sur un bouton InlineKeyboard | Validation/modification (planning_valider, courses_confirmer...) |

### Callback actions

| callback_data | Action |
|---------------|--------|
| `planning_valider` | Valide le planning brouillon → statut "validé" |
| `planning_modifier` | Passe en mode modification (attend un message texte) |
| `planning_regenerer` | Régénère un nouveau planning via IA |
| `courses_confirmer` | Confirme la liste de courses → statut "active" |
| `courses_ajouter` | Attend un message pour ajouter des articles |
| `courses_refaire` | Régénère la liste depuis le planning |
| `digest_courses` | Envoie la liste de courses du jour |
| `digest_detail` | Envoie le détail complet du briefing |
| `weekend_ok` | Confirme les suggestions weekend |
| `weekend_autres` | Demande d'autres suggestions |
| `entretien_fait` | Marque la tâche entretien comme faite |
| `entretien_plus_tard` | Reporte la tâche |

---

## Pourquoi Telegram Bot

- messages proactifs sans coût par message
- boutons interactifs sans fenêtre de 24h
- webhook simple à configurer
- format HTML suffisant pour les messages applicatifs

---

## Dépannage

### Le bot ne répond pas

1. Vérifier le token : `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Vérifier le webhook : `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Vérifier que l'endpoint `/api/v1/telegram/webhook` est accessible publiquement
4. Inspecter les logs : `logger.error` dans `webhooks_telegram.py`

### Messages proactifs non reçus

1. Vérifier `TELEGRAM_CHAT_ID` dans `.env.local`
2. Vérifier que tu as envoyé au moins 1 message au bot (Telegram l'exige)
3. Tester manuellement : `curl -X POST .../sendMessage -d '{"chat_id": "...", "text": "test"}'`

### Boutons ne fonctionnent pas

1. Vérifier que le webhook est configuré (les `callback_query` arrivent via webhook)
2. Vérifier que le handler appelle `answerCallbackQuery` dans les 10 secondes
3. Inspecter `callback_query.data` dans les logs

### Erreur 409 "Conflict: terminated by other getUpdates"

Le bot est en mode polling ET webhook en même temps. Supprimer le webhook si tu utilises polling :

```bash
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## Checklist mise en production

- [ ] Token bot dans les variables Railway (pas dans le code)
- [ ] Chat ID configuré
- [ ] Webhook enregistré avec l'URL Railway HTTPS
- [ ] Test envoi message proactif OK
- [ ] Test boutons interactifs OK
- [ ] Test digest matinal OK
- [ ] CRON jobs adaptés au canal Telegram
- [ ] Dispatcher notifications adapté (canal "telegram")
- [ ] Ancien code canal legacy supprimé
