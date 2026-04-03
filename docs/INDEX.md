# Documentation Index - MaTanne

> Derniere mise a jour : 2 avril 2026.
> Statut : index aligne avec la documentation consolidee et les mises a jour du planning.

## Documents principaux

| Document | Description | Statut |
| --- | --- | --- |
| [../ANALYSE_COMPLETE.md](../ANALYSE_COMPLETE.md) | audit complet et etat reel du projet | reference |
| [../PLANNING_IMPLEMENTATION.md](../PLANNING_IMPLEMENTATION.md) | plan d'implementation detaille issu de l'analyse | mis a jour |
| [../ROADMAP.md](../ROADMAP.md) | feuille de route produit et principes | mis a jour |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | architecture FastAPI + Next.js | current |
| [API_REFERENCE.md](./API_REFERENCE.md) | reference API REST | current |
| [API_SCHEMAS.md](./API_SCHEMAS.md) | inventaire des schemas Pydantic | current |
| [MODULES.md](./MODULES.md) | carte des modules et perimetres | current |
| [SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md) | reference des services backend | current |
| [ERD_SCHEMA.md](./ERD_SCHEMA.md) | schema entite-relation | current |
| [DATA_MODEL.md](./DATA_MODEL.md) | vue fonctionnelle du modele de donnees | current |
| [EVENT_BUS.md](./EVENT_BUS.md) | catalogue des evenements domaine et subscribers | mis a jour 2026-04-01 |
| [SECURITY.md](./SECURITY.md) | securite applicative | current |
| [PATTERNS.md](./PATTERNS.md) | patterns backend et frontend recurrents | current |
| [UI_COMPONENTS.md](./UI_COMPONENTS.md) | composants UI Next.js et shadcn | current |
| [MONITORING.md](./MONITORING.md) | monitoring et observabilite | current |
| [ADMIN_RUNBOOK.md](./ADMIN_RUNBOOK.md) | procedures d'administration et endpoints | mis a jour 2026-04-01 |
| [CRON_JOBS.md](./CRON_JOBS.md) | reference APScheduler et historique d'execution | mis a jour 2026-04-01 |
| [CRON_DEVELOPMENT.md](./CRON_DEVELOPMENT.md) | guide de creation d un job CRON (schedule, logs, dry run) | nouveau 2026-04-02 |
| [NOTIFICATIONS.md](./NOTIFICATIONS.md) | canaux, preferences, failover et limites | mis a jour 2026-04-01 |
| [INTER_MODULES.md](./INTER_MODULES.md) | cartographie des flux inter-modules | mis a jour 2026-04-01 |
| [INTER_MODULES_GUIDE.md](./INTER_MODULES_GUIDE.md) | guide de creation de bridges inter-modules | nouveau 2026-04-02 |
| [AI_SERVICES.md](./AI_SERVICES.md) | reference des services IA | current |
| [AI_INTEGRATION_GUIDE.md](./AI_INTEGRATION_GUIDE.md) | guide d integration pour creer un service IA BaseAIService | nouveau 2026-04-02 |
| [TELEGRAM_SETUP.md](./TELEGRAM_SETUP.md) | configuration bot Telegram et webhook | mis a jour 2026-04-03 |
| [WHATSAPP_COMMANDS.md](./WHATSAPP_COMMANDS.md) | commandes conversationnelles WhatsApp (obsolete, migration Telegram) | legacy |
| [PERFORMANCE.md](./PERFORMANCE.md) | performance et capacite | current |
| [CHANGELOG_MODULES.md](./CHANGELOG_MODULES.md) | historique transversal par phase, sprint et domaine | mis a jour 2026-04-01 |
| [AUTOMATIONS.md](./AUTOMATIONS.md) | moteur Si Alors, triggers, actions et API | mis a jour 2026-04-01 |
| [TESTING.md](./TESTING.md) | guide unifie backend, frontend, E2E, contrat et charge | nouveau 2026-04-01 |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | diagnostics rapides et pannes frequentes | current |
| [DEVELOPER_SETUP.md](./DEVELOPER_SETUP.md) | installation developpeur locale | current |
| [SQLALCHEMY_SESSION_GUIDE.md](./SQLALCHEMY_SESSION_GUIDE.md) | guide sessions base de donnees | current |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | deploiement local, Docker, Railway, Vercel, Supabase | current |
| [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) | migrations stack et workflow DB | current |
| [REDIS_SETUP.md](./REDIS_SETUP.md) | configuration Redis optionnelle | current |
| [GOOGLE_ASSISTANT_SETUP.md](./GOOGLE_ASSISTANT_SETUP.md) | integration Google Assistant | current |

## Guides par module

| Guide | Module | Description |
| --- | --- | --- |
| [guides/cuisine/README.md](./guides/cuisine/README.md) | Cuisine | recettes, planning repas, courses, inventaire, batch cooking, anti-gaspillage |
| [guides/famille/README.md](./guides/famille/README.md) | Famille | Jules, activites, routines, budget, weekend |
| [guides/maison/README.md](./guides/maison/README.md) | Maison | projets, entretien, jardin, energie, stocks |
| [guides/planning/README.md](./guides/planning/README.md) | Planning | hub planning, timeline, calendriers |
| [guides/jeux/README.md](./guides/jeux/README.md) | Jeux | paris sportifs, loto, Euromillions |
| [guides/outils/README.md](./guides/outils/README.md) | Outils | chat IA, meteo, convertisseur, minuteur, notes |
| [guides/dashboard/README.md](./guides/dashboard/README.md) | Dashboard | tableau de bord et metriques agregees |
| [guides/utilitaires/README.md](./guides/utilitaires/README.md) | Utilitaires | scanner codes-barres, commandes vocales |
| [guides/RECIPE_FLOW.md](./guides/RECIPE_FLOW.md) | Guide utilisateur | flux recette de bout en bout |
| [guides/FAMILY_FLOW.md](./guides/FAMILY_FLOW.md) | Guide utilisateur | flux famille de bout en bout |
| [USER_FLOWS.md](./USER_FLOWS.md) | Guide utilisateur | parcours cibles cuisine, famille, maison, jeux |

## References a consulter en priorite

1. [../ANALYSE_COMPLETE.md](../ANALYSE_COMPLETE.md) pour l'etat reel et les constats.
2. [../PLANNING_IMPLEMENTATION.md](../PLANNING_IMPLEMENTATION.md) pour l'ordre d'execution et les statuts.
3. [CRON_JOBS.md](./CRON_JOBS.md), [NOTIFICATIONS.md](./NOTIFICATIONS.md), [ADMIN_RUNBOOK.md](./ADMIN_RUNBOOK.md), [INTER_MODULES.md](./INTER_MODULES.md), [EVENT_BUS.md](./EVENT_BUS.md) pour les couches transverses.
4. [TESTING.md](./TESTING.md) pour la verification locale et la couverture de tests.

## Demarrage rapide

```bash
python manage.py run
cd frontend && npm run dev
python manage.py test_coverage
cd frontend && npm test
```
