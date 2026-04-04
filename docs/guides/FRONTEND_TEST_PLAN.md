# Plan complet — Tests unit frontend

## Objectif

Structurer une couverture de tests unitaires et d'intégration légère sur 3 axes:

- Hooks
- Stores Zustand
- Composants UI et pages critiques

## Périmètre prioritaire (ordre d'exécution)

1. Hooks métier critiques
2. Stores globaux
3. Composants extraits prioritaires
4. Pages avec état complexe

## 1) Hooks

### Hooks — Déjà couverts

- `frontend/src/__tests__/hooks/utiliser-crud-dialog.test.ts`
- `frontend/src/__tests__/hooks/utiliser-websocket.test.ts`

### Hooks — À compléter

- `frontend/src/crochets/utiliser-api.ts`
- `frontend/src/crochets/utiliser-auth.ts`
- `frontend/src/crochets/utiliser-stockage-local.ts`
- `frontend/src/crochets/utiliser-notifications-jeux.ts`

### Hooks — Cas à tester

- États `loading/error/success`
- Invalidation TanStack Query
- Comportement offline/localStorage
- Fallback navigateur non supporté

## 2) Stores Zustand

### Stores — Déjà couverts

- `frontend/src/magasins/store-auth.test.ts`
- `frontend/src/magasins/store-ui.test.ts`
- `frontend/src/magasins/store-notifications.test.ts`

### Stores — À compléter

- Scénarios inter-stores (auth + notifications)
- Persistance et rehydratation
- Reset global après logout

## 3) Composants prioritaires

### Nouveaux composants habitat

- `frontend/src/composants/habitat/grille-indicateurs-habitat.tsx`
- `frontend/src/composants/habitat/grille-blocs-habitat.tsx`
- `frontend/src/composants/habitat/filtres-marche-habitat.tsx`

### Nouveaux composants planning

- `frontend/src/composants/planning/timeline-semaine.tsx`
- `frontend/src/composants/planning/etat-vide-planning.tsx`

### Nouveaux composants paramètres

- `frontend/src/app/(app)/parametres/_composants/*.tsx`

### Composants — Cas à tester

- Rendu conditionnel
- Interactions utilisateur (click, switch, input)
- Callbacks (`onRefresh`, `onChange`, etc.)
- Accessibilité minimale (labels, rôles)

## 4) Pages critiques

### Priorité haute

- `frontend/src/app/(app)/parametres/page.tsx`
- `frontend/src/app/(app)/habitat/page.tsx`
- `frontend/src/app/(app)/habitat/marche/page.tsx`
- `frontend/src/app/(app)/planning/timeline/page.tsx`

### Stratégie

- Garder les tests de pages en "smoke + parcours principal"
- Déporter les assertions détaillées au niveau composant
- Mocker API clients/hook réseau systématiquement

## Matrice de couverture cible

| Zone | Actuel | Cible |
| ---- | ------ | -------------- |
| Hooks | moyen | élevé |
| Stores | moyen | élevé |
| Composants habitat/planning | faible | moyen/élevé |
| Page paramètres | faible | moyen |

## Commandes

```bash
cd frontend
npm test
npm test -- --runInBand
npm test -- parametres.test.tsx
npm test -- timeline.test.tsx
```

## Règles de qualité

- Un test = un comportement métier
- Éviter les snapshots globaux
- Préférer les assertions utilisateur (`screen.getByRole`, `screen.getByText`)
- Mocker les modules externes (Next router, APIs)
- Conserver les tests stables (pas de dépendance au temps réel sans mock)
