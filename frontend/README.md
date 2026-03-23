# Assistant Matanne — Frontend Next.js

Frontend React du hub de gestion familiale **Assistant Matanne**.

## Stack technique

| Technologie | Version | Rôle |
|---|---|---|
| Next.js | 16.2.1 | Framework React (App Router) |
| TypeScript | 5 | Typage statique |
| Tailwind CSS | v4 | Styles utilitaires |
| shadcn/ui | Radix UI | Composants UI accessibles |
| TanStack Query | v5 | Cache serveur & fetching |
| Zustand | 5 | État global client |
| react-hook-form + Zod | 7.x + 4.x | Formulaires & validation |
| Vitest + RTL | 4.x | Tests unitaires composants |
| Playwright | - | Tests E2E |

## Démarrage rapide

```bash
# Installation
npm install

# Développement
npm run dev        # http://localhost:3000

# Build production
npm run build

# Tests
npm test           # Vitest (watch mode)
npm run test:run   # Vitest (une seule exécution)
npm run test:e2e   # Playwright E2E

# Analyse bundle
npm run analyze    # Ouvre le rapport dans le navigateur
```

## Variables d'environnement

Copier `.env.example` → `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## Architecture

```
src/
├── app/                    # Routes Next.js (App Router)
│   ├── (app)/              # Layout authentifié
│   │   ├── cuisine/        # 🍽️ Recettes, planning, courses, inventaire
│   │   ├── famille/        # 👨‍👩‍👦 Jules, activités, routines, budget…
│   │   ├── maison/         # 🏠 Projets, jardin, charges, énergie
│   │   ├── planning/       # 📅 Calendrier, timeline
│   │   ├── jeux/           # 🎮 Paris sportifs, loto, euromillions
│   │   ├── outils/         # 🛠️ Chat IA, notes, météo, minuteur, convertisseur
│   │   └── parametres/     # ⚙️ Paramètres
│   ├── (auth)/             # Pages connexion/inscription
│   └── layout.tsx          # Layout racine (providers, PWA)
├── components/
│   ├── ui/                 # Composants shadcn/ui
│   ├── layout/             # Header, sidebar, navigation
│   └── enregistrement-sw.tsx  # Enregistrement Service Worker
├── fournisseurs/           # Providers React (auth, query, theme)
├── hooks/                  # Hooks personnalisés (utiliser-api, etc.)
├── lib/
│   └── api/                # Clients API par domaine
├── stores/                 # Stores Zustand
└── types/                  # Interfaces TypeScript
```

## Modules (46 routes)

| Module | Routes | Description |
|---|---|---|
| Cuisine | 8 | Recettes CRUD, planning repas, courses, inventaire, batch cooking, anti-gaspi |
| Famille | 10 | Suivi Jules, activités, routines, budget, weekend, album, anniversaires… |
| Maison | 7 | Projets, jardin, entretien, charges, dépenses, énergie, stocks |
| Planning | 2 | Calendrier semaine + timeline |
| Jeux | 3 | Paris sportifs, loto, euromillions |
| Outils | 5 | Chat IA, notes, météo, minuteur, convertisseur |
| Paramètres | 1 | Paramètres multi-onglets |

## PWA

L'application est installable sur mobile (iOS/Android) :
- Manifest : `public/manifest.json`
- Service Worker : `public/sw.js` (cache offline + push notifications)
- Icônes : `public/icons/` (72px–512px, maskable)

## Conventions

- **Langue** : tout le code est en **français** (noms de variables, fonctions, composants)
- **Composants shadcn/ui** : noms anglais conservés (convention bibliothèque)
- **API hooks** : `utiliserRequete()`, `utiliserMutation()`, `utiliserInvalidation()` depuis `@/hooks/utiliser-api`
- **Tests** : fichiers `.test.tsx` colocalisés avec les composants
