# Automations

> Documentation du moteur d'automatisation simple de type Si→Alors.

---

## Vue d'ensemble

Le moteur d'automations actuel permet d'exécuter des règles stockées en base à fréquence régulière.

Composants:

- routes API: `src/api/routes/automations.py`
- moteur: `src/services/utilitaires/automations_engine.py`
- exécution planifiée: job `automations_runner`

---

## Ce que le moteur supporte aujourd'hui

### Déclencheurs

- `stock_bas`

### Actions

- `ajouter_courses`
- `notifier`

### Exécution

- le job `automations_runner` passe toutes les 5 minutes
- seules les règles actives sont évaluées
- le moteur met à jour `derniere_execution` et incrémente `execution_count`

---

## API disponible

Routes principales:

- lister les automations de l'utilisateur
- créer une automation
- initialiser depuis les préférences historiques
- générer une règle à partir d'un prompt IA

Le module expose aussi un format structuré `RegleAutomationIA` pour les réponses générées par IA.

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

- un seul déclencheur réellement géré côté moteur
- seulement deux actions prises en charge
- pas d'historique détaillé persistant
- pas de dry-run
- pas de rollback

Ces limites sont déjà prévues dans le planning d'extension.

---

## Statut CRON et exécution

Le moteur d'automations est orchestré par le scheduler global de l'application.

Statut actuel:

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
