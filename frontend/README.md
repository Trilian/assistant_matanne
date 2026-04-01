# Assistant Matanne - Frontend Next.js

Frontend React du hub de gestion familiale **Assistant Matanne**.

## Stack technique

| Technologie | Version | R�le |
| --- | --- | --- |
| Next.js | 16.2.1 | Framework React (App Router) |
| TypeScript | 5 | Typage statique |
| Tailwind CSS | v4 | Styles utilitaires |
| shadcn/ui | Radix UI | Composants UI accessibles |
| TanStack Query | v5 | Cache serveur & fetching |
| Zustand | 5 | �tat global client |
| react-hook-form + Zod | 7.x + 4.x | Formulaires & validation |
| Vitest + RTL | 4.x | Tests unitaires composants |
| Playwright | - | Tests E2E |

## D�marrage rapide

```bash
# Installation
npm install

# D�veloppement
npm run dev        # http://localhost:3000

# Build production
npm run build

# Tests
npm test           # Vitest (watch mode)
npm run test:run   # Vitest (une seule ex�cution)
npm run test:e2e   # Playwright E2E

# Analyse bundle
npm run analyze    # Ouvre le rapport dans le navigateur

# G�n�ration des types TypeScript depuis l'API (backend doit tourner sur :8000)
npm run generate-types    # ? src/types/api-generated.ts
```

## G�n�ration automatique des types TypeScript

Les types sont auto-g�n�r�s depuis le sch�ma OpenAPI du backend (FastAPI) via [`openapi-typescript`](https://openapi-ts.dev/).

```bash
# 1. D�marrer le backend
uvicorn src.api.main:app --reload --port 8000

# 2. G�n�rer les types
cd frontend
npm run generate-types
# Produit: src/types/api-generated.ts
```

Le fichier `src/types/api-generated.ts` est un artefact g�n�r� (ne pas modifier manuellement).
Les types manuels dans `src/types/` restent utilis�s pour les interfaces suppl�mentaires non couvertes par l'API.


## Variables d'environnement

Copier `.env.example` ? `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

## Architecture

```
src/
??? app/                    # Routes Next.js (App Router)
?   ??? (app)/              # Layout authentifi�
?   ?   ??? cuisine/        # ??? Recettes, planning, courses, inventaire
?   ?   ??? famille/        # ???????? Jules, activit�s, routines, budget.
?   ?   ??? maison/         # ?? Projets, jardin, charges, �nergie
?   ?   ??? planning/       # ?? Calendrier, timeline
?   ?   ??? jeux/           # ?? Paris sportifs, loto, euromillions
?   ?   ??? outils/         # ??? Chat IA, notes, m�t�o, minuteur, convertisseur
?   ?   ??? parametres/     # ?? Param�tres
?   ??? (auth)/             # Pages connexion/inscription
?   ??? layout.tsx          # Layout racine (providers, PWA)
??? components/
?   ??? ui/                 # Composants shadcn/ui
?   ??? layout/             # Header, sidebar, navigation
?   ??? enregistrement-sw.tsx  # Enregistrement Service Worker
??? fournisseurs/           # Providers React (auth, query, theme)
??? hooks/                  # Hooks personnalis�s (utiliser-api, etc.)
??? lib/
?   ??? api/                # Clients API par domaine
??? stores/                 # Stores Zustand
??? types/                  # Interfaces TypeScript
```

## Modules (46 routes)

| Module | Routes | Description |
| --- | --- | --- |
| Cuisine | 8 | Recettes CRUD, planning repas, courses, inventaire, batch cooking, anti-gaspi |
| Famille | 9 | Suivi Jules, activit�s, routines, budget, weekend, anniversaires. |
| Maison | 7 | Projets, jardin, entretien, charges, d�penses, �nergie, stocks |
| Planning | 2 | Calendrier semaine + timeline |
| Jeux | 3 | Paris sportifs, loto, euromillions |
| Outils | 5 | Chat IA, notes, m�t�o, minuteur, convertisseur |
| Param�tres | 1 | Param�tres multi-onglets |

## PWA

L'application est installable sur mobile (iOS/Android) :
- Manifest : `public/manifest.json`
- Service Worker : `public/sw.js` (cache offline + push notifications)
- Ic�nes : `public/icons/` (72px-512px, maskable)

## Conventions

- **Langue** : tout le code est en **fran�ais** (noms de variables, fonctions, composants)
- **Composants shadcn/ui** : noms anglais conserv�s (convention biblioth�que)
- **API hooks** : `utiliserRequete()`, `utiliserMutation()`, `utiliserInvalidation()` depuis `@/hooks/utiliser-api`
- **Tests** : fichiers `.test.tsx` colocalis�s avec les composants
