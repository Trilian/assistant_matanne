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