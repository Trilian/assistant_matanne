# Migration Streamlit → Next.js

> **⚠️ Référence historique** — Ce document retrace la migration effectuée de Streamlit vers Next.js. Le frontend est désormais entièrement Next.js 16.

## Vue d'ensemble

Migration de l'interface frontend de **Streamlit** (Python) vers **Next.js 16** (React/TypeScript) tout en conservant le backend Python (FastAPI) et la base de données Supabase PostgreSQL.

## Motivation

| Critère | Streamlit | Next.js |
|---|---|---|
| Performance démarrage | ~4s (chargement différé) | <1s (SSG + code splitting) |
| UX mobile | Limité (pas de PWA) | PWA installable, offline |
| Interactivité | Reruns complets | React state, temps réel |
| SEO | Aucun | SSG/SSR natif |
| Écosystème UI | Limité | shadcn/ui, Radix, Tailwind |
| Tests | Difficile | Vitest + Playwright |

## Architecture cible

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Next.js Frontend  │────▶│  FastAPI Backend  │────▶│  Supabase    │
│   (React, SSG)      │     │  (Python 3.13)   │     │  PostgreSQL  │
│   Port 3000         │     │  Port 8000       │     │              │
└─────────────────────┘     └──────────────────┘     └──────────────┘
```

## Décisions techniques

### 1. App Router (Next.js 16)
- Chaque module = dossier sous `src/app/(app)/`
- Layouts imbriqués pour sidebar + header
- `"use client"` sur chaque page interactive

### 2. Langue française
Tout le code TypeScript est en français : variables, fonctions, composants, hooks. Les noms de composants shadcn/ui restent en anglais (convention externe).

### 3. State management
- **TanStack Query v5** : cache serveur, refetch automatique, invalidation
- **Zustand 5** : état UI global (auth, notifications, préférences)
- **react-hook-form + Zod** : formulaires avec validation runtime

### 4. API client
- Instance Axios centralisée (`lib/api/client.ts`) avec intercepteurs JWT
- 1 fichier API par domaine (`lib/api/cuisine.ts`, `lib/api/famille.ts`, etc.)
- Extraction `.items` des réponses paginées backend

### 5. PWA
- Service Worker manuel dans `public/sw.js` (cache offline + push)
- Manifest dans `public/manifest.json`
- Icônes maskable 72px–512px

## Mapping des modules Streamlit → Next.js

| Module Streamlit | Route Next.js | Pages |
|---|---|---|
| `modules/accueil/` | `/` | Dashboard |
| `modules/cuisine/` | `/cuisine/*` | 8 pages (recettes, planning, courses…) |
| `modules/famille/` | `/famille/*` | 10 pages (jules, activités, routines…) |
| `modules/maison/` | `/maison/*` | 7 pages (projets, jardin, entretien…) |
| `modules/planning/` | `/planning/*` | 2 pages (calendrier, timeline) |
| `modules/jeux/` | `/jeux/*` | 3 pages (paris, loto, euromillions) |
| `modules/utilitaires/` | `/outils/*` | 5 pages (chat IA, notes, météo…) |
| `modules/parametres/` | `/parametres` | 1 page multi-onglets |

## Phases de migration

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Nettoyage code mort (gamification) | ✅ |
| 1 | Setup Next.js + infrastructure (60+ fichiers) | ✅ |
| 2 | API Backend FastAPI (6 schemas, 6 routes) | ✅ |
| 3 | Module Cuisine + Paramètres (12 fichiers) | ✅ |
| 4 | Module Famille (10 sous-pages) | ✅ |
| 5 | Modules Maison & Planning (9 pages) | ✅ |
| 6 | Modules Jeux & Outils (8 pages) | ✅ |
| 7 | Polish, PWA, Tests, Documentation | ✅ |

## Commandes

```bash
# Développement
cd frontend && npm run dev

# Build production
npm run build

# Tests unitaires
npm test              # watch
npm run test:run      # CI

# Tests E2E
npm run test:e2e

# Analyse bundle
npm run analyze

# Lint
npm run lint
```
