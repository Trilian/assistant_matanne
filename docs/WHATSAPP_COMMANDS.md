# WhatsApp Commands (Deprecated)

Documentation obsolète des commandes conversationnelles WhatsApp.
Référence active: commandes Telegram via le webhook `/api/v1/telegram/webhook`.

## Endpoints webhook

- `GET /api/v1/whatsapp/webhook`: verification Meta.
- `POST /api/v1/whatsapp/webhook`: reception des messages.

Implementation: `src/api/routes/webhooks_whatsapp.py`.

## Types de messages traites

- `interactive`: boutons et listes.
- `text`: commandes texte libres.

## Actions boutons

- `planning_valider`
- `planning_modifier`
- `planning_regenerer`
- `digest_courses`
- `digest_detail`
- `courses_tout_acheter`
- `courses_partager`
- `entretien_fait`
- `cmd_*` (routage commande texte)

## Commandes texte

- `menu`, `planning`, `semaine`
- `ce soir`, `diner`
- `courses`, `liste`
- `frigo`, `stock`, `inventaire`
- `jules`
- `ajouter <article>`
- `budget`
- `anniversaires`
- `recette <nom>`
- `taches`
- `meteo`
- `jardin`
- `energie`
- `entretien`
- `aide`

## Machine d'etat simplifiee

1. Entree message (text/interactive).
2. Resolution intention (commande ou action bouton).
3. Appel service metier (planning/courses/famille/maison).
4. Reponse texte WhatsApp.

## Bonnes pratiques

- Rester idempotent pour les actions critiques.
- Journaliser action + sender anonymise.
- Garder un fallback `aide` explicite en cas de commande inconnue.
