# Frontend Architecture — Assistant MaTanne

> Architecture frontend Next.js 16 + TypeScript du projet.

---

## Vue d'ensemble

Le frontend est une SPA Next.js (App Router) dans `frontend/`.

Pile principale:

- Next.js 16.2.1 (App Router)
- React 19
- TypeScript 5
- Tailwind CSS v4
- shadcn/ui
- TanStack Query v5
- Zustand 5
- react-hook-form + Zod

---

## Arborescence

- `frontend/src/app/` : routes App Router
- `frontend/src/composants/` : composants métiers + layout
- `frontend/src/composants/ui/` : primitives UI shadcn
- `frontend/src/bibliotheque/api/` : clients API par domaine
- `frontend/src/crochets/` : hooks réutilisables
- `frontend/src/magasins/` : stores Zustand
- `frontend/src/fournisseurs/` : providers (query, auth, theme)
- `frontend/src/types/` : types métier

---

## Routing App Router

Structure globale:

- `(auth)` : login / register / reset
- `(app)` : application protégée

Dans `(app)`, les hubs fonctionnels sont segmentés par domaine:

- cuisine
- famille
- maison
- habitat
- jeux
- planning
- outils
- paramètres
- admin

Le layout applicatif est partagé via `src/app/(app)/layout.tsx` et les composants de disposition (`coquille-app`, sidebar, nav mobile).

---

## Data fetching

TanStack Query est la couche standard pour les appels API:

- Requêtes: `utiliserRequete` (`src/crochets/utiliser-api.ts`)
- Mutations: `utiliserMutation`
- Invalidation: `utiliserInvalidation`

Client HTTP centralisé:

- `src/bibliotheque/api/client.ts`

Ce client gère:

- base URL
- injection JWT
- gestion standard des erreurs

---

## State management

Zustand gère l'état global léger:

- `store-auth.ts`
- `store-ui.ts`
- `store-notifications.ts`

Règle:

- état serveur -> TanStack Query
- état UI/session locale -> Zustand

---

## Formulaires et validation

Stack:

- `react-hook-form` pour la gestion du formulaire
- `zod` pour les schémas de validation

Exemple type:

1. Schéma Zod dans `src/bibliotheque/validateurs.ts`
2. Hook form avec `zodResolver`
3. Mutation API via `utiliserMutation`

---

## UI System

Le projet s'appuie sur:

- composants de base shadcn dans `src/composants/ui/`
- composants métier par domaine dans `src/composants/{domaine}/`

Recommandations:

- garder les composants UI purs dans `ui/`
- mettre la logique métier dans les composants domaine/pages
- privilégier composition à la duplication

---

## Temps réel

Deux hooks WebSocket sont présents:

- `utiliser-websocket.ts` (générique)
- `utiliser-websocket-courses.ts` (spécifique collaboration courses)

Usages:

- présence utilisateurs
- synchronisation d'état de listes
- événements live ciblés

---

## Tests frontend

Outils:

- Vitest + Testing Library
- Playwright (E2E)

Configuration:

- `frontend/vitest.config.ts`
- seuils coverage actuels: lignes 50%, fonctions 50%, branches 40%, statements 50%

Zones couvertes en phase 3:

- composants critiques (formulaire recette, plan 3D, heatmap cotes)
- hooks (CRUD dialog, websocket)

---

## Build et qualité

Commandes:

```bash
cd frontend
npm run lint
npm test
npx next build
```

---

## Bonnes pratiques projet

- Favoriser les types explicites dans `src/types/`
- Garder les clients API fins, sans logique d'UI
- Encapsuler les patterns répétitifs dans des hooks
- Éviter l'accès direct à `fetch` depuis les pages
- Documenter tout nouveau flux inter-module dans `docs/INTER_MODULES.md`
