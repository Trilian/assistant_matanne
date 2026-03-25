# 📊 Guide Module Dashboard

> Tableau de bord familial avec métriques agrégées de tous les modules.

---

## Vue d'ensemble

Le **Dashboard** est la page d'accueil de l'application. Il agrège les données clés de chaque module pour offrir une vue synthétique de l'état familial.

**URL** : `/` (page d'accueil)  
**Service backend** : `src/services/dashboard/service.py`  
**Route API** : `src/api/routes/dashboard.py` (`/api/v1/dashboard`)  
**Frontend** : `frontend/src/app/(app)/page.tsx`

---

## Widgets

| Widget | Description | Source |
|--------|-------------|--------|
| Repas du jour | Repas planifiés (déjeuner, dîner) | Planning |
| Courses en attente | Nombre de listes non terminées | Courses |
| Tâches en retard | Tâches entretien/projets en retard | Maison |
| Anniversaires proches | Prochains anniversaires famille | Famille |
| Météo | Météo du jour + alertes | Intégrations |
| Budget mensuel | Dépenses vs budget, reste | Finances |
| Stock bas | Articles inventaire en quantité faible | Inventaire |
| Prochains événements | Événements planifiés cette semaine | Planning |

---

## API

| Méthode | URL | Description |
|---------|-----|-------------|
| GET | `/api/v1/dashboard` | Données agrégées du dashboard |
| GET | `/api/v1/dashboard/taches-retard` | Tâches en retard (limite configurable) |

---

## Architecture

```
Frontend (page.tsx)
  → GET /api/v1/dashboard
    → src/api/routes/dashboard.py
      → src/services/dashboard/service.py
        → Requêtes ORM sur : Repas, ListeCourses, Projet, TacheEntretien,
           AnniversaireFamille, Depense, BudgetMensuel, Inventaire
```

Le service dashboard utilise `@avec_cache(ttl=60)` pour les données agrégées (rafraîchissement chaque minute).

Voir [API_REFERENCE.md](../API_REFERENCE.md) pour la documentation complète.
