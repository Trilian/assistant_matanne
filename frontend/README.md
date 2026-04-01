# Assistant Matanne â€” Frontend Next.js

Frontend React du hub de gestion familiale **Assistant Matanne**.

## Stack technique

| Technologie | Version | RÃ´le |
| --- | --- | --- |
| Next.js | 16.2.1 | Framework React (App Router) |
| TypeScript | 5 | Typage statique |
| Tailwind CSS | v4 | Styles utilitaires |
| shadcn/ui | Radix UI | Composants UI accessibles |
| TanStack Query | v5 | Cache serveur & fetching |
| Zustand | 5 | Ã‰tat global client |
| react-hook-form + Zod | 7.x + 4.x | Formulaires & validation |
| Vitest + RTL | 4.x | Tests unitaires composants |
| Playwright | - | Tests E2E |

## DÃ©marrage rapide

```bash
# Installation
npm install

# DÃ©veloppement
npm run dev        # http://localhost:3000

# Build production
npm run build

# Tests
npm test           # Vitest (watch mode)
npm run test:run   # Vitest (une seule exÃ©cution)
npm run test:e2e   # Playwright E2E

# Analyse bundle
npm run analyze    # Ouvre le rapport dans le navigateur

# GÃ©nÃ©ration des types TypeScript depuis l'API (backend doit tourner sur :8000)
npm run generate-types    # â†’ src/types/api-generated.ts
```

## GÃ©nÃ©ration automatique des types TypeScript

Les types sont auto-gÃ©nÃ©rÃ©s depuis le schÃ©ma OpenAPI du backend (FastAPI) via [`openapi-typescript`](https://openapi-ts.dev/).

```bash
# 1. DÃ©marrer le backend
uvicorn src.api.main:app --reload --port 8000

# 2. GÃ©nÃ©rer les types
cd frontend
npm run generate-types
# Produit: src/types/api-generated.ts
```

Le fichier `src/types/api-generated.ts` est un artefact gÃ©nÃ©rÃ© (ne pas modifier manuellement).
Les types manuels dans `src/types/` restent utilisÃ©s pour les interfaces supplÃ©mentaires non couvertes par l'API.


## Variables d'environnement

Copier `.env.example` â†’ `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## Architecture

```
src/
â”œâ”€â”€ app/                    # Routes Next.js (App Router)
â”‚   â”œâ”€â”€ (app)/              # Layout authentifiÃ©
â”‚   â”‚   â”œâ”€â”€ cuisine/        # ðŸ½ï¸ Recettes, planning, courses, inventaire
â”‚   â”‚   â”œâ”€â”€ famille/        # ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦ Jules, activitÃ©s, routines, budgetâ€¦
â”‚   â”‚   â”œâ”€â”€ maison/         # ðŸ  Projets, jardin, charges, Ã©nergie
â”‚   â”‚   â”œâ”€â”€ planning/       # ðŸ“… Calendrier, timeline
â”‚   â”‚   â”œâ”€â”€ jeux/           # ðŸŽ® Paris sportifs, loto, euromillions
â”‚   â”‚   â”œâ”€â”€ outils/         # ðŸ› ï¸ Chat IA, notes, mÃ©tÃ©o, minuteur, convertisseur
â”‚   â”‚   â””â”€â”€ parametres/     # âš™ï¸ ParamÃ¨tres
â”‚   â”œâ”€â”€ (auth)/             # Pages connexion/inscription
â”‚   â””â”€â”€ layout.tsx          # Layout racine (providers, PWA)
â”œâ”€â”€ components/
â”‚   â”œâ”€â”€ ui/                 # Composants shadcn/ui
â”‚   â”œâ”€â”€ layout/             # Header, sidebar, navigation
â”‚   â””â”€â”€ enregistrement-sw.tsx  # Enregistrement Service Worker
â”œâ”€â”€ fournisseurs/           # Providers React (auth, query, theme)
â”œâ”€â”€ hooks/                  # Hooks personnalisÃ©s (utiliser-api, etc.)
â”œâ”€â”€ lib/
â”‚   â””â”€â”€ api/                # Clients API par domaine
â”œâ”€â”€ stores/                 # Stores Zustand
â””â”€â”€ types/                  # Interfaces TypeScript
```

## Modules (46 routes)

| Module | Routes | Description |
| --- | --- | --- |
| Cuisine | 8 | Recettes CRUD, planning repas, courses, inventaire, batch cooking, anti-gaspi |
| Famille | 9 | Suivi Jules, activitÃ©s, routines, budget, weekend, anniversairesâ€¦ |
| Maison | 7 | Projets, jardin, entretien, charges, dÃ©penses, Ã©nergie, stocks |
| Planning | 2 | Calendrier semaine + timeline |
| Jeux | 3 | Paris sportifs, loto, euromillions |
| Outils | 5 | Chat IA, notes, mÃ©tÃ©o, minuteur, convertisseur |
| ParamÃ¨tres | 1 | ParamÃ¨tres multi-onglets |

## PWA

L'application est installable sur mobile (iOS/Android) :
- Manifest : `public/manifest.json`
- Service Worker : `public/sw.js` (cache offline + push notifications)
- IcÃ´nes : `public/icons/` (72pxâ€“512px, maskable)

## Conventions

- **Langue** : tout le code est en **franÃ§ais** (noms de variables, fonctions, composants)
- **Composants shadcn/ui** : noms anglais conservÃ©s (convention bibliothÃ¨que)
- **API hooks** : `utiliserRequete()`, `utiliserMutation()`, `utiliserInvalidation()` depuis `@/hooks/utiliser-api`
- **Tests** : fichiers `.test.tsx` colocalisÃ©s avec les composants
