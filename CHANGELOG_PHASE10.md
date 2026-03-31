# CHANGELOG — Phase 10 (Sprints G & H)

> Journal des changements techniques de la Phase 10.  
> Pour le changelog utilisateur, voir [CHANGELOG.md](../CHANGELOG.md).

---

## Sprint H — Consolidation technique & documentation (avril 2026)

### Base de données — Structure modulaire SQL

**H.1 — `sql/schema/` : Découpe de `INIT_COMPLET.sql`**
- Fichier `sql/INIT_COMPLET.sql` (5 000+ lignes) découpé en modules SQL numérotés dans `sql/schema/`
- Structure : `01_extensions.sql`, `02_types.sql`, `03_auth.sql`, `04_tables_auth.sql`, …, `14_indexes.sql`, `15_rls_policies.sql`, `16_triggers.sql`, `17_views.sql`, `18_functions.sql`, `19_seeds.sql`
- `INIT_COMPLET.sql` devient un fichier de référence statique (ne pas modifier directement)

**H.2 — `scripts/db/regenerate_init.py` : Régénérateur idempotent**
- Script qui reconstruit `INIT_COMPLET.sql` depuis `sql/schema/*.sql`
- Idempotent : peut être relancé sans risque
- Ajoute un header daté et le résumé des fichiers sources

**H.3 — Audit tables ORM orphelines**
- Vérification que tous les modèles ORM `src/core/models/` ont une table SQL correspondante
- Résultat : aucune table orpheline détectée

**H.4 — `docs/guides/DATABASE_INDEXES.md` : Audit des index**
- Nouveau fichier documentant tous les index existants (par domaine)
- Liste des index manquants classés par priorité (HIGH / MEDIUM / LOW)
- Procédure EXPLAIN ANALYZE et conventions de nommage

**H.5 — `docs/MIGRATION_GUIDE.md` : Workflow SQL-first documenté**
- Ajout de la section "Workflow SQL-first — Structure modulaire (Sprint H)"
- Couvre : workflow en 6 étapes, procédure de ré-initialisation, conventions SQL, script de vérification

### Organisation du code — Backend

**H.6 — `src/api/routes/jeux.py` → 4 fichiers**
- `jeux.py` (2 545 lignes) découpé en 4 modules :
  - `jeux_paris.py` (1 127 lignes) — Paris sportifs
  - `jeux_loto.py` (354 lignes) — Loto
  - `jeux_euromillions.py` (307 lignes) — Euromillions
  - `jeux_dashboard.py` (711 lignes) — Tableau de bord jeux
- `jeux.py` devient un agrégateur de 24 lignes
- Backup conservé : `jeux.py.bak`

**H.7 — Audit imports circulaires**
- Test d'import Python sur 21 modules (routes, services, core)
- Résultat : aucun import circulaire détecté

**H.8 — `docs/PATTERNS.md` : Conventions schémas Pydantic**
- Ajout de la section "Séparation des schémas Pydantic"
- Distingue `src/api/schemas/` (sérialisation HTTP) vs `src/core/validation/schemas/` (validation métier)
- Guide de décision + pattern d'héritage

**H.9 — `docs/TESTING_ADVANCED.md` : Conventions de nommage**
- Ajout de la section "Conventions de nommage des tests (Sprint H)"
- Structure cible des dossiers, règles de nommage, conventions classes/méthodes
- Liste des 9 fichiers ne respectant pas encore les conventions + recommandations de renommage

**H.10 — `scripts/archive/` : Archivage des scripts one-shot**
- Création du répertoire `scripts/archive/`
- Migration : `scripts/split_famille.py` → `scripts/archive/split_famille.py`
- Migration : `scripts/split_maison.py` → `scripts/archive/split_maison.py`

### Documentation — Nouveaux guides

**H.15 — `docs/guides/IA_AVANCEE.md`**
- Guide complet pour les 14 outils IA (endpoints, exemples requête/réponse, architecture)
- Architecture IA : rate limiting (10 req/min), cache sémantique, circuit breaker
- Limites et quotas, guide de dépannage

**H.16 — `docs/guides/SENTRY.md`**
- Guide d'intégration Sentry (setup, DSN, taux d'échantillonnage)
- Capture manuelle d'erreurs, Error Boundaries React, contexte utilisateur
- Configuration dev vs production

**H.17 — `docs/guides/DOCKER_PRODUCTION.md`**
- Guide Docker + Railway pour la production
- Commandes build/test local, staging docker-compose
- Déploiement Railway, tuning Gunicorn workers, bonnes pratiques sécurité

**H.18 — `docs/DESIGN_SYSTEM.md`**
- Référence design system complète
- 29 composants UI documentés (description + usage)
- Tokens CSS (couleurs, typographie), variantes Button, pattern Card, états de chargement

**H.19 — `CONTRIBUTING.md`**
- Guide de contribution et conventions de développement
- Git workflow (feature branches, Conventional Commits)
- Conventions Python (`fr`) + TypeScript, pattern complet d'ajout de feature (6 étapes)
- Checklist qualité avant PR

**H.20 — `CHANGELOG_PHASE10.md`** (ce fichier)

**H.21 — `docs/guides/PWA_OFFLINE.md`**
- Guide Service Worker (stratégies, précache, gestion versions)
- Manifest PWA, installation Android, mode offline
- Procédure de test offline (DevTools)

**H.22 — `docs/ARCHITECTURE.md` : Diagrammes Mermaid**
- Ajout diagramme global (Mermaid `graph TB`) : Clients → Vercel → Railway → Core → Services → Externes
- Ajout diagramme de flux requête API (Mermaid `sequenceDiagram`)
- Tableau des décisions d'architecture notables

---

## Sprint G — Simplifications UX & robustesse (mars 2026)

### Suppressions

- Module multi-tenant (`multi_tenant.py`) supprimé — inutilisé en production
- Fonctionnalité "jeu responsable" entièrement supprimée du codebase
- Anciens décorateurs `@cached` et `@avec_cache_multi` supprimés (remplacés par `@avec_cache`)

### Simplifications API

- Endpoints IA : rate limiting unifié (10 req/min) via middleware dédié
- Cache IA : `CacheIA` (cache sémantique) intégré dans `BaseAIService`
- Circuit breaker sur tous les appels Mistral AI

### Frontend

- Mise à jour Tailwind CSS → v4 (nouveau moteur CSS)
- Mise à jour Zod → 4.3.6
- Composants shadcn/ui : passage au nouveau registry v2

### Backend

- SQLAlchemy migrations : passage du système Alembic au système SQL-file custom
- `src/core/date_utils/` transformé en package (4 modules spécialisés)
- `src/core/decorators/` transformé en package (4 fichiers)
- `src/api/routes/` : découpe famille (2 fichiers) et maison (2 fichiers)

---

## Historique des phases précédentes

Pour les phases 1–9, voir :
- [CHANGELOG.md](../CHANGELOG.md)
- [PLANNING_IMPLEMENTATION.md](../PLANNING_IMPLEMENTATION.md)
