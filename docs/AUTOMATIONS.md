# Automations

> Documentation du moteur d'automatisation Siâ†’Alors.
>
> **DerniÃ¨re mise Ã  jour** : 1er avril 2026

---

## Vue d'ensemble

Le moteur d'automations exÃ©cute des rÃ¨gles stockÃ©es en base Ã  frÃ©quence rÃ©guliÃ¨re.

Composants :

- routes API : `src/api/routes/automations.py`
- moteur : `src/services/utilitaires/automations_engine.py`
- exÃ©cution planifiÃ©e : job CRON `automations_runner` (toutes les 5 minutes)
- modÃ¨le ORM : `AutomationRegle`

---

## DÃ©clencheurs supportÃ©s (9)

| Type | Description |
| ------ | ------------- |
| `stock_bas` | Articles inventaire sous un seuil |
| `peremption_proche` | Articles arrivant Ã  pÃ©remption proche |
| `budget_depassement` | DÃ©penses du mois au-dessus d'un seuil |
| `meteo_alerte` | PrÃ©vision mÃ©tÃ©o contenant un mot-clÃ© (pluie, orage, neige, vent) |
| `anniversaire_proche` | Anniversaires dans une fenÃªtre de jours |
| `tache_en_retard` | TÃ¢ches d'entretien en retard |
| `garmin_inactivite` | InactivitÃ© Garmin au-delÃ  d'un seuil |
| `document_expiration` | Documents arrivant Ã  expiration |
| `recette_sans_photo` | Recettes sans image |

---

## Actions supportÃ©es (10)

| Type | Description |
| ------ | ------------- |
| `ajouter_courses` | Ajoute articles Ã  une liste de courses active |
| `generer_liste_courses` | Alias de `ajouter_courses` |
| `suggerer_recette` | Envoie une notification de suggestion recette |
| `creer_tache_maison` | CrÃ©e une tÃ¢che d'entretien |
| `ajouter_au_planning` | CrÃ©e un Ã©vÃ©nement planning |
| `mettre_a_jour_budget` | Ajoute une dÃ©pense d'ajustement budget |
| `generer_rapport_pdf` | Notifie qu'un rapport PDF est prÃªt |
| `archiver` | DÃ©sactive la rÃ¨gle aprÃ¨s exÃ©cution |
| `notifier` | Notification ntfy + push |
| `envoyer_whatsapp` | Notification WhatsApp |
| `envoyer_email` | Notification email |

---

## ExÃ©cution

- le job `automations_runner` passe toutes les 5 minutes
- seules les rÃ¨gles actives sont Ã©valuÃ©es
- le moteur met Ã  jour `derniere_execution` et incrÃ©mente `execution_count`
- support du **dry-run** global et par rÃ¨gle

MÃ©thodes principales :

- `executer_automations_actives()`
- `executer_automations_actives_dry_run()`
- `executer_automation_par_id()`

---

## API disponible

| MÃ©thode | Route | Usage |
| --------- | ------- | ------- |
| `GET` | `/api/v1/automations` | Lister les automations de l'utilisateur |
| `POST` | `/api/v1/automations/init` | Initialiser depuis les prÃ©fÃ©rences legacy |
| `POST` | `/api/v1/automations` | CrÃ©er une automation |
| `PUT` | `/api/v1/automations/{automation_id}` | Modifier une automation |
| `POST` | `/api/v1/automations/{automation_id}/simuler` | Simuler une automation |
| `POST` | `/api/v1/automations/{automation_id}/executer-maintenant` | ExÃ©cuter immÃ©diatement (`dry_run` optionnel) |
| `POST` | `/api/v1/automations/generer-ia` | GÃ©nÃ©rer une rÃ¨gle depuis un prompt IA |

Le module expose aussi un format structurÃ© `RegleAutomationIA` pour les rÃ©ponses IA.

---

## Exemple conceptuel

```json
{
  "nom": "Stock bas produits de base",
  "condition": {"type": "stock_bas", "seuil": 2},
  "action": {"type": "ajouter_courses", "quantite": 1},
  "parametres": {}
}
```

---

## Limitations actuelles

- pas d'historique dÃ©taillÃ© persistant par exÃ©cution d'automation
- pas de rollback mÃ©tier avancÃ©
- dÃ©clencheurs Ã©valuÃ©s en polling via CRON, pas en temps rÃ©el Ã©vÃ©nementiel

---

## Statut CRON et exÃ©cution

Le moteur d'automations est orchestrÃ© par le scheduler global de l'application via `automations_runner`.

Statut actuel : **opÃ©rationnel en production**

- jobs planifiÃ©s: 38+ au niveau plateforme
- job automation dÃ©diÃ©: `automations_runner`
- frÃ©quence recommandÃ©e: 5 minutes

Points de contrÃ´le opÃ©rationnels:

- visibilitÃ© des exÃ©cutions via routes admin jobs
- logs de derniÃ¨re exÃ©cution consultables
- relance manuelle possible pour diagnostic

---

## Extension prÃ©vue

DÃ©clencheurs supplÃ©mentaires ciblÃ©s:

- `document_expirant`
- `peremption_proche`
- `routine_en_retard`
- `seuil_budget_depasse`

Actions supplÃ©mentaires ciblÃ©es:

- `creer_tache_planning`
- `envoyer_email`
- `envoyer_whatsapp`
- `declencher_webhook`

AmÃ©liorations structurelles prÃ©vues:

- historique persistant des exÃ©cutions
- mode dry-run
- meilleure observabilitÃ© des erreurs par rÃ¨gle
