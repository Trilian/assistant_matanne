# Automations

> Documentation du moteur d'automatisation Si→Alors.
>
> **Dernière mise à jour** : 1er avril 2026

---

## Vue d'ensemble

Le moteur d'automations exécute des règles stockées en base à fréquence régulière.

Composants :

- routes API : `src/api/routes/automations.py`
- moteur : `src/services/utilitaires/automations_engine.py`
- exécution planifiée : job CRON `automations_runner` (toutes les 5 minutes)
- modèle ORM : `AutomationRegle`

---

## Déclencheurs supportés (9)

| Type | Description |
|------|-------------|
| `stock_bas` | Articles inventaire sous un seuil |
| `peremption_proche` | Articles arrivant à péremption proche |
| `budget_depassement` | Dépenses du mois au-dessus d'un seuil |
| `meteo_alerte` | Prévision météo contenant un mot-clé (pluie, orage, neige, vent) |
| `anniversaire_proche` | Anniversaires dans une fenêtre de jours |
| `tache_en_retard` | Tâches d'entretien en retard |
| `garmin_inactivite` | Inactivité Garmin au-delà d'un seuil |
| `document_expiration` | Documents arrivant à expiration |
| `recette_sans_photo` | Recettes sans image |

---

## Actions supportées (10)

| Type | Description |
|------|-------------|
| `ajouter_courses` | Ajoute articles à une liste de courses active |
| `generer_liste_courses` | Alias de `ajouter_courses` |
| `suggerer_recette` | Envoie une notification de suggestion recette |
| `creer_tache_maison` | Crée une tâche d'entretien |
| `ajouter_au_planning` | Crée un événement planning |
| `mettre_a_jour_budget` | Ajoute une dépense d'ajustement budget |
| `generer_rapport_pdf` | Notifie qu'un rapport PDF est prêt |
| `archiver` | Désactive la règle après exécution |
| `notifier` | Notification ntfy + push |
| `envoyer_whatsapp` | Notification WhatsApp |
| `envoyer_email` | Notification email |

---

## Exécution

- le job `automations_runner` passe toutes les 5 minutes
- seules les règles actives sont évaluées
- le moteur met à jour `derniere_execution` et incrémente `execution_count`
- support du **dry-run** global et par règle

Méthodes principales :

- `executer_automations_actives()`
- `executer_automations_actives_dry_run()`
- `executer_automation_par_id()`

---

## API disponible

| Méthode | Route | Usage |
|---------|-------|-------|
| `GET` | `/api/v1/automations` | Lister les automations de l'utilisateur |
| `POST` | `/api/v1/automations/init` | Initialiser depuis les préférences legacy |
| `POST` | `/api/v1/automations` | Créer une automation |
| `PUT` | `/api/v1/automations/{automation_id}` | Modifier une automation |
| `POST` | `/api/v1/automations/{automation_id}/simuler` | Simuler une automation |
| `POST` | `/api/v1/automations/{automation_id}/executer-maintenant` | Exécuter immédiatement (`dry_run` optionnel) |
| `POST` | `/api/v1/automations/generer-ia` | Générer une règle depuis un prompt IA |

Le module expose aussi un format structuré `RegleAutomationIA` pour les réponses IA.

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

- pas d'historique détaillé persistant par exécution d'automation
- pas de rollback métier avancé
- déclencheurs évalués en polling via CRON, pas en temps réel événementiel

---

## Statut CRON et exécution

Le moteur d'automations est orchestré par le scheduler global de l'application via `automations_runner`.

Statut actuel : **opérationnel en production**

- jobs planifiés: 38+ au niveau plateforme
- job automation dédié: `automations_runner`
- fréquence recommandée: 5 minutes

Points de contrôle opérationnels:

- visibilité des exécutions via routes admin jobs
- logs de dernière exécution consultables
- relance manuelle possible pour diagnostic

---

## Extension prévue

Déclencheurs supplémentaires ciblés:

- `document_expirant`
- `peremption_proche`
- `routine_en_retard`
- `seuil_budget_depasse`

Actions supplémentaires ciblées:

- `creer_tache_planning`
- `envoyer_email`
- `envoyer_whatsapp`
- `declencher_webhook`

Améliorations structurelles prévues:

- historique persistant des exécutions
- mode dry-run
- meilleure observabilité des erreurs par règle
