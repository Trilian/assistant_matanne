# 📚 Documentation Index — MaTanne

> **Dernière mise à jour** : 29 mars 2026 — Phase 4 Documentation

---

## Documents principaux

| Document | Description |
|----------|-------------|
| [../ANALYSE_COMPLETE.md](../ANALYSE_COMPLETE.md) | **Audit complet** (28 mars 2026) — état réel, bugs, dette tech, plan à long terme |
| [../PLANNING_IMPLEMENTATION.md](../PLANNING_IMPLEMENTATION.md) | **Planning d'implémentation** — sprints 1-9, tâches détaillées |
| [../ROADMAP.md](../ROADMAP.md) | **Feuille de route** — priorités moyen/long terme + principes |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Architecture technique (FastAPI + Next.js) |
| [API_REFERENCE.md](./API_REFERENCE.md) | Référence complète de l'API REST (242 endpoints) |
| [MODULES.md](./MODULES.md) | Carte des modules : fonctionnalités, routes, services, modèles |
| [SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md) | Documentation des services backend |
| [ERD_SCHEMA.md](./ERD_SCHEMA.md) | Schéma entité-relation de la DB (Mermaid) |
| [PATTERNS.md](./PATTERNS.md) | Patterns de code récurrents (résilience, cache, events) |
| [UI_COMPONENTS.md](./UI_COMPONENTS.md) | Composants UI Next.js / shadcn |
| [ADMIN_RUNBOOK.md](./ADMIN_RUNBOOK.md) | Procédures d'administration: jobs, cache, santé, utilisateurs |
| [CRON_JOBS.md](./CRON_JOBS.md) | Référence des tâches planifiées APScheduler |
| [NOTIFICATIONS.md](./NOTIFICATIONS.md) | Canaux, préférences, tests admin et limites actuelles |
| [INTER_MODULES.md](./INTER_MODULES.md) | Cartographie des flux inter-modules |
| [AI_SERVICES.md](./AI_SERVICES.md) | Référence des services IA et usages actuels |
| [AUTOMATIONS.md](./AUTOMATIONS.md) | Moteur d'automatisation Si→Alors |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | Pannes fréquentes et diagnostics rapides |
| [DEVELOPER_SETUP.md](./DEVELOPER_SETUP.md) | Installation développeur locale complète |
| [SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md) | Guide sessions DB |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Guide de déploiement (local, Docker, Railway, Vercel, Supabase) |
| [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) | Guide migration stack technique + workflow DB |
| [REDIS_SETUP.md](./REDIS_SETUP.md) | Configuration Redis (optionnel) |

## Guides par module

| Guide | Module | Description |
|-------|--------|-------------|
| [guides/cuisine/README.md](./guides/cuisine/README.md) | Cuisine | Recettes, planning repas, courses, inventaire, batch cooking, anti-gaspillage |
| [guides/famille/README.md](./guides/famille/README.md) | Famille | Jules, activités, routines, budget, weekend |
| [guides/maison/README.md](./guides/maison/README.md) | Maison | Projets, entretien, jardin, énergie, stocks |
| [guides/planning/README.md](./guides/planning/README.md) | Planning | Hub planning, timeline, calendriers |
| [guides/jeux/README.md](./guides/jeux/README.md) | Jeux | Paris sportifs, Loto, EuroMillions |
| [guides/outils/README.md](./guides/outils/README.md) | Outils | Chat IA, météo, convertisseur, minuteur, notes |
| [guides/dashboard/README.md](./guides/dashboard/README.md) | Dashboard | Tableau de bord, métriques agrégées |
| [guides/utilitaires/README.md](./guides/utilitaires/README.md) | Utilitaires | Scanner codes-barres, commandes vocales |

## Structure

```
docs/
├── INDEX.md                     ← Vous êtes ici
├── ARCHITECTURE.md              ← Architecture technique
├── API_REFERENCE.md             ← Documentation API REST
├── MODULES.md                   ← Carte des modules
├── SERVICES_REFERENCE.md        ← Documentation Services
├── ERD_SCHEMA.md                ← Schéma ERD
├── PATTERNS.md                  ← Patterns de code
├── UI_COMPONENTS.md             ← Composants UI Next.js
├── ADMIN_RUNBOOK.md             ← Opérations admin
├── CRON_JOBS.md                 ← Référence jobs planifiés
├── NOTIFICATIONS.md             ← Système de notifications
├── INTER_MODULES.md             ← Interactions cross-module
├── AI_SERVICES.md               ← Services IA
├── AUTOMATIONS.md               ← Automations Si→Alors
├── TROUBLESHOOTING.md           ← Diagnostic rapide
├── DEVELOPER_SETUP.md           ← Setup développeur
├── SQLALCHEMY_SESSION_GUIDE.md  ← Guide sessions DB
├── DEPLOYMENT.md                ← Guide déploiement
├── MIGRATION_GUIDE.md           ← Guide migration stack + workflow DB
├── REDIS_SETUP.md               ← Setup Redis
└── guides/
    ├── cuisine/README.md        ← Cuisine complet
    ├── famille/README.md        ← Famille complet
    ├── maison/README.md         ← Maison complet
    ├── planning/README.md       ← Planning complet
    ├── jeux/README.md           ← Jeux complet
    ├── outils/README.md         ← Outils complet
    ├── dashboard/README.md      ← Dashboard
    └── utilitaires/
        ├── README.md            ← Hub utilitaires
        ├── barcode.md           ← Scan code-barres
        └── vocal.md             ← Commandes vocales
```

## Démarrage rapide

```bash
# Backend FastAPI
python manage.py run              # http://localhost:8000

# Frontend Next.js
cd frontend && npm run dev        # http://localhost:3000

# Tests
python manage.py test_coverage    # Backend (pytest)
cd frontend && npm test           # Frontend (Vitest)
```

