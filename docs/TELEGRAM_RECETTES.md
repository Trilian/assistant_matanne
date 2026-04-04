# Recette Manuelle Telegram — Sprint 5

> Validation manuelle du hub mobile Telegram après implémentation du Sprint 5.
>
> Portée : commandes slash, menus, callbacks inline, réponses rapides, fallback conversationnel.

---

## Préparation

Avant de lancer la recette :

1. Vérifier que le backend tourne et que le webhook Telegram pointe vers `/api/v1/telegram/webhook`.
2. Vérifier que `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` sont configurés.
3. Ouvrir une conversation privée avec le bot.
4. Prévoir un groupe de test si l'on veut valider les commandes avec suffixe `@bot`.
5. Vérifier qu'il existe au moins un planning et une liste de courses pour les scénarios principaux.

Fichiers utiles :

- `src/api/routes/webhooks_telegram.py`
- `src/services/integrations/telegram.py`
- `src/services/utilitaires/briefing_matinal.py`

---

## Commandes Sprint 5

### `/aide`

Action : envoyer `/aide`

Attendu :

- affichage de la liste des commandes disponibles
- présence des boutons `Menu principal`, `Planning`, `Courses`

### `/menu`

Action : envoyer `/menu`

Attendu :

- affichage du menu principal
- boutons `Cuisine`, `Famille`, `Maison`, `Outils`, `Aide`

### `/planning`

Action : envoyer `/planning`

Attendu :

- affichage du planning de la semaine en un message formaté
- boutons `Valider`, `Modifier`, `Régénérer`, `Menu principal`

### `/planning@nom_du_bot`

Action : dans un groupe, envoyer `/planning@nom_du_bot`

Attendu :

- même comportement que `/planning`
- aucune erreur de parsing liée au suffixe `@bot`

### `/courses`

Action : envoyer `/courses`

Attendu :

- affichage de la liste de courses active
- boutons inline par article
- bouton `Confirmer`

### `/ajout lait`

Action : envoyer `/ajout lait`

Attendu :

- confirmation d'ajout dans la liste
- pas de duplication si l'article existe déjà et n'est pas acheté

### `/repas`

Action : envoyer `/repas`

Attendu :

- affichage du ou des repas du jour
- fallback propre si rien n'est planifié

### `/repas soir`

Action : envoyer `/repas soir`

Attendu :

- affichage ciblé du dîner uniquement

### `/jules`

Action : envoyer `/jules`

Attendu :

- résumé Jules du jour
- âge en mois
- prochains jalons si profil disponible

### `/maison`

Action : envoyer `/maison`

Attendu :

- liste des tâches maison prioritaires du jour
- fallback propre si aucune tâche n'est planifiée

### `/budget`

Action : envoyer `/budget`

Attendu :

- total du mois en cours
- top catégories si des dépenses existent

### `/meteo`

Action : envoyer `/meteo`

Attendu :

- météo du jour
- suggestion d'activité ou impact pratique si disponible

---

## Menus Et Callbacks

### Navigation menu principal

Actions :

1. ouvrir `/menu`
2. cliquer successivement `Cuisine`, `Famille`, `Maison`, `Outils`
3. cliquer `Menu principal` depuis chaque sous-menu

Attendu :

- chaque sous-menu affiche les bonnes actions rapides
- le retour au menu principal fonctionne à chaque fois

### Toggle d'article de courses

Actions :

1. envoyer `/courses`
2. cliquer sur un article non coché
3. recliquer sur le même article

Attendu :

- l'état passe de `☐` à `☑️`, puis l'inverse
- un feedback callback s'affiche
- la liste renvoyée reflète bien le nouvel état

### Validation planning par bouton

Actions :

1. envoyer `/planning`
2. cliquer `Valider`

Attendu :

- confirmation utilisateur
- planning validé si l'état initial est `brouillon`

### Régénération planning

Actions :

1. envoyer `/planning`
2. cliquer `Régénérer`

Attendu :

- message de régénération
- création d'un nouveau planning brouillon

### Confirmation liste de courses

Actions :

1. envoyer `/courses`
2. cliquer `Confirmer`

Attendu :

- confirmation utilisateur
- la liste passe à l'état attendu

---

## Réponses Rapides

### Validation par `OK`

Scénario planning :

1. envoyer `/planning`
2. répondre `OK`

Attendu :

- si l'état conversationnel `planning_validation` existe, le planning est validé

Scénario courses :

1. envoyer `/courses`
2. répondre `OK`

Attendu :

- si l'état conversationnel `courses_confirmation` existe, la liste est confirmée

### Variantes tolérées

Actions : envoyer `oui`, `go`, `vas-y`, `valide`

Attendu :

- comportement identique à `OK` quand un état conversationnel est actif

---

## Fallback Conversationnel

### Message repas libre

Action : envoyer `Qu'est-ce qu'on mange ce soir ?`

Attendu :

- réponse dîner via fallback historique

### Ajout naturel

Action : envoyer `Ajoute pain a la liste`

Attendu :

- ajout d'article via parsing texte naturel

### Activité du samedi

Action : envoyer `Activite samedi ?`

Attendu :

- activités prévues samedi ou suggestion par défaut

### Commande inconnue

Action : envoyer un texte non reconnu

Attendu :

- fallback vers l'aide interactive

---

## Briefing Matinal

Action : déclencher ou attendre l'envoi du briefing matinal Telegram.

Attendu :

- présence de la météo
- présence des repas du jour
- présence des tâches maison
- présence de la section Jules
- présence des alertes ou sections disponibles selon les données

---

## Vérifications Visuelles

Contrôler systématiquement :

1. l'affichage correct des accents, emojis et balises HTML Telegram
2. l'absence de boutons tronqués bloquants
3. l'absence de doublons de messages après callback
4. le bon support des commandes avec suffixe `@bot` en groupe

---

## En Cas D'Échec

1. Vérifier les logs backend du webhook Telegram.
2. Vérifier l'état conversationnel persistant dans `src/services/integrations/telegram.py`.
3. Vérifier la configuration webhook et le token dans `docs/TELEGRAM_SETUP.md`.
4. Rejouer la suite automatisée :

```bash
pytest tests/api/test_webhooks_telegram_endpoints.py tests/api/test_webhooks_telegram_callbacks.py -q
```

---

## Résultat Attendu De La Recette

La recette est considérée conforme si :

- toutes les commandes Sprint 5 répondent sans erreur
- les menus et callbacks Telegram fonctionnent
- les réponses rapides valident les flux prévus
- les fallbacks historiques restent opérationnels
- le briefing matinal enrichi est lisible et complet
