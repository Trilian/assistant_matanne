# Performance

Reference perf backend/frontend.

## Indicateurs principaux

- Endpoints API detectes: 622.
- Jobs cron planifies: 68.
- Tables ORM: 143.
- Factories services: 169.

## Backend

- SQLAlchemy 2.0 + sessions encadrees.
- Cache multi-niveaux disponible (memoire/fichier + orchestration).
- Middleware ETag pour limiter les payloads repetes.
- Event bus pour decoupler sans bloquer la requete synchrone.

## Frontend

- Next.js 16 App Router.
- TanStack Query pour cache/revalidation.
- Zustand pour etat local UI.
- Composants UI factorises pour limiter duplication.

## Bonnes pratiques

- Eviter N+1 queries sur endpoints listes.
- Utiliser pagination sur listes volumineuses.
- Mettre en cache les calculs IA couteux.
- Deporter traitements lourds dans jobs cron.
- Mesurer p95/p99 avant optimisation ciblee.

## Tests charge / verification

- Utiliser endpoints metriques Prometheus + logs.
- Verifier les endpoints critiques: recettes, courses, famille, dashboard.
- Surveiller tokens IA et latences generation.
