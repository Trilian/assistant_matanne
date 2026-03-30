# CHANGELOG — Assistant MaTanne

Toutes les modifications notables de ce projet sont documentées ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [Phase 10] — 2026-03-30 — Innovations

### Ajouté

#### Backend — Services & API (25 items)

- **10.1 Assistant vocal connecté** : Le composant `fab-assistant-vocal.tsx` est fonctionnel et connecté à `POST /api/v1/assistant/commande-vocale` avec contexte IA multi-module via le chat contextuel existant
- **10.2 Suggestions proactives** : Déjà implémenté en Phase 6 (`GET /api/v1/ia-avancee/suggestions-proactives`) — validation OK
- **10.3 Mode invité** : Nouveau endpoint `POST /api/v1/innovations/invite/creer` + `GET /api/v1/innovations/invite/{token}` pour lien partageable sans authentification (nounou/grands-parents)
- **10.4 Bilan annuel IA** : Nouveau endpoint `POST /api/v1/innovations/bilan-annuel` — bilan complet cuisine + budget + maison + Jules + sport
- **10.5 Score bien-être familial** : Nouveau endpoint `GET /api/v1/innovations/score-bien-etre` — composite 4 dimensions (sport 30%, nutrition 25%, budget 25%, routines 20%)
- **10.6 WebSocket étendu** : WebSocket déjà fonctionnel pour courses, notes, planning et projets (`/api/v1/ws/`)
- **10.7 Gestion multi-enfants** : Architecture DB prête via `ProfilEnfant` avec FK et flag `actif` — support multi-enfants natif
- **10.8 Veille emploi** : Nouveau endpoint `POST /api/v1/innovations/veille-emploi` + job CRON quotidien à 7h — critères configurables (domaine, contrat, télétravail, rayon)
- **10.9 Mode hors-ligne** : Service Worker (`sw.js`), IndexedDB (`db-local.ts`), offline queue (`offline_queue.py`) — infrastructure PWA opérationnelle
- **10.10 API GraphQL** : Non implémenté (REST performant avec TanStack Query cache suffisant)
- **10.11 Compagnon vocal WhatsApp** : Intégration vocale possible via transcription audio WhatsApp → commande texte existante
- **10.12 Intégration supermarché** : Non implémenté (dépend d'accès API drives Carrefour/Leclerc non disponibles)
- **10.13 Rappels intelligents contextuels** : Service `rappels_intelligents.py` existant enrichi — garanties, inventaire, entretien
- **10.14 Mini-jeux éducatifs Jules** : Non implémenté (hors périmètre MVP — nécessite contenus éducatifs)
- **10.15 Tableau de bord familial partagé** : Architecture multi-user existante via `profils_utilisateurs` — scoring inter-modules disponible
- **10.16 Widgets home personnalisables** : Composant `grille-widgets.tsx` opérationnel avec drag-and-drop et persistence localStorage
- **10.17 Enrichissement contacts IA** : Nouveau endpoint `GET /api/v1/innovations/enrichissement-contacts` — catégorisation + rappels relationnels
- **10.18 Analyse tendances Loto** : Nouveau endpoint `GET /api/v1/innovations/tendances-loto` — numéros chauds/froids + combinaison statistique
- **10.19 Optimisation parcours magasin** : Nouveau endpoint `POST /api/v1/innovations/parcours-magasin` — regroupement par rayon + ordre optimisé
- **10.20 Jobs CRON restants** : 4 nouveaux jobs — `optimisation_routines` (mensuel), `suggestions_saison` (1er/mois), `purge_historique_jeux` (mensuel), `veille_emploi` (quotidien)
- **10.21 Réponses vocales WhatsApp** : Intégration audio via MediaMessage WhatsApp + transcription IA
- **10.22 Notifications contextuelles** : Rappels intelligents enrichis avec contexte (garanties, inventaire, entretien)
- **10.23 Docs** : Nouveau `HABITAT_MODULE.md` + ce `CHANGELOG.md`
- **10.24 Tests** : Suite de tests `tests/api/test_innovations.py` — 20 tests couvrant les 8 endpoints innovations
- **10.25 Admin avancé** : `POST /api/v1/admin/reset-module` (réinitialisation module) + WebSocket `/api/v1/ws/admin/logs` (logs temps réel)

#### Frontend

- Page innovations dans la sidebar avec accès aux 8 endpoints
- Composants d'infrastructure existants validés : `fab-assistant-vocal.tsx`, `grille-widgets.tsx`, `sw.js`, `db-local.ts`

### Notes techniques

- Nouveau package `src/services/innovations/` avec `InnovationsService` héritant de `BaseAIService`
- Nouveau routeur `src/api/routes/innovations.py` avec 8 endpoints
- Schémas Pydantic dans `src/api/schemas/innovations.py`
- 4 nouveaux jobs CRON dans `src/services/core/cron/jobs.py`
- WebSocket admin logs dans `src/api/websocket/admin_logs.py`

---

## [Phase 9] — 2026-03-30 — Gamification sport + nutrition

### Ajouté
- Triggers badges sport et nutrition
- Page détail badges
- Notifications badges débloqués
- Historique points hebdomadaire
- Documentation `GAMIFICATION.md`

---

## [Phase 8] — 2025-07-17 — Jobs CRON additionnels

### Ajouté
- 9 nouveaux jobs CRON (rappels documents, rapport mensuel, sync contrats, garanties, bilan énergie, vaccins)
- 3 connexions inter-modules (entretien→budget, voyages→calendrier, charges→dashboard)
- Tests couvrant les 9 jobs + subscribers

---

## [Phase 7] — Mode admin avancé

### Ajouté
- Persistance historique jobs en DB
- Console d'exécution manuelle avec dry-run
- Test notifications multi-canal
- Import/export config admin
- Simulateur de flux
- Dashboard temps réel admin

---

## [Phase 6] — IA avancée

### Ajouté
- 14 endpoints IA proactifs et contextuels
- Package `src/services/ia_avancee/`
- Analyses photo multi-usage, planning voyage, prédiction pannes

---

## [Phase 5] — Notifications avancées

### Ajouté
- Cascade failover Push → Email → WhatsApp
- Templates email HTML Jinja2
- Rate limiting + validation WhatsApp
- Commandes WhatsApp étendues
- Digest matinal WhatsApp

---

## [Phase 4] — UX simplification

### Ajouté
- Regroupement sidebar Famille (4 catégories) et Maison (3 catégories)
- FAB mobile actions rapides
- Mode simplifié formulaire recette
- Input courses sticky

---

## [Phase 3] — Tests & documentation

### Ajouté
- Tests services habitat, dashboard, intégrations
- Tests composants React et hooks
- Documentation FRONTEND_ARCHITECTURE, ADMIN_GUIDE, WHATSAPP_SETUP

---

## [Phase 2] — Connexions inter-modules

### Ajouté
- 8 connexions inter-modules
- Briefing matinal IA
- Chat IA contexte multi-module

---

## [Phase 1] — Corrections critiques

### Corrigé
- Notifications câblées sur alertes péremption et planning
- Stock bas → ajout auto courses
- Source données loterie réelle
- Consolidation SQL
- Toggle Mode Test admin
