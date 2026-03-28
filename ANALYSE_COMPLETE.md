# 🔍 Analyse Complète — Assistant Matanne
> **Date** : 27 mars 2026 | **Auteur** : GitHub Copilot  
> **État global** : ~96% de couverture fonctionnelle sur 28 phases

---

## 📋 Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [Architecture & inventaire technique](#2-architecture--inventaire-technique)
3. [Analyse module par module](#3-analyse-module-par-module)
4. [Bugs & régressions identifiés](#4-bugs--régressions-identifiés)
5. [Manques & features incomplètes](#5-manques--features-incomplètes)
6. [SQL — Consolidation & état actuel](#6-sql--consolidation--état-actuel)
7. [Interactions intra-modules & inter-modules](#7-interactions-intra-modules--inter-modules)
8. [Axes d'intégration IA](#8-axes-dintégration-ia)
9. [Jobs automatiques — Planning cron](#9-jobs-automatiques--planning-cron)
10. [Notifications — WhatsApp, Mail, Push](#10-notifications--whatsapp-mail-push)
11. [Mode Admin / Déclenchement manuel](#11-mode-admin--déclenchement-manuel)
12. [Axes d'innovation identifiés](#12-axes-dinnovation-identifiés)
13. [Synthèse & roadmap recommandée](#13-synthèse--roadmap-recommandée)

---

## 1. Résumé exécutif

### L'application en chiffres

| Indicateur | Valeur |
|---|---|
| **Modules fonctionnels** | 8 (Cuisine, Famille, Maison, Jeux, Planning, Outils, Admin, Dashboard) |
| **Endpoints API** | ~300+ réels (aucun 501 détecté) |
| **Pages frontend** | ~60 pages Next.js (App Router) |
| **Tables SQL** | ~130 tables |
| **Services backend** | ~200+ fichiers Python dans `src/services/` |
| **Modèles ORM** | 128+ classes SQLAlchemy dans 28 fichiers |
| **Tests** | 197 fichiers (141 backend + 46 frontend unit + 10 E2E Playwright) |
| **Couverture phases** | 24/28 complètes, 3 quasi-complètes, 1 partielle |

### Points forts

- ✅ **Architecture robuste** : FastAPI + SQLAlchemy 2.0 + Pydantic v2, cache multi-niveaux, circuit breaker, rate limiting
- ✅ **IA bien intégrée** : Mistral (texte) + Pixtral (vision) présents dans 15+ services
- ✅ **Modules Famille, Jeux, Maison** : 100% fonctionnels avec IA contextuelle
- ✅ **Infrastructure prod-ready** : Sentry, Prometheus, CI/CD 8 workflows, PWA offline, 2FA TOTP, RGPD, WebSockets

### Problèmes critiques

- 🔴 **Push subscriptions en mémoire vive** : toutes les souscriptions Web Push sont perdues à chaque redémarrage
- 🔴 **Aucun canal email/SMS/WhatsApp** : seule combinaison ntfy.sh + Web Push disponible
- 🔴 **Digest ntfy jamais déclenché** : service implémenté mais pas schedulé

---

## 2. Architecture & inventaire technique

### Stack technologique

```
Backend
├── Python 3.13+ / FastAPI
├── SQLAlchemy 2.0 ORM + Pydantic v2
├── Mistral AI (texte) + Pixtral (vision)
├── APScheduler (cron) — 6 jobs actifs
├── ntfy.sh + Web Push VAPID (notifications)
├── Redis (L2 cache optionnel)
└── Supabase PostgreSQL (production)

Frontend
├── Next.js 16.2 (App Router + Turbopack)
├── TypeScript 5 + Tailwind CSS v4 + shadcn/ui
├── TanStack Query v5 (data fetching + cache)
├── Zustand 5 (state global)
├── React Hook Form 7 + Zod 4.3 (validation)
└── PWA + IndexedDB (offline)

Infrastructure
├── 8 GitHub Actions workflows
├── Dockerfile + Docker Compose staging
├── Sentry (FE + BE) — conditionnel avec DSN
├── Prometheus + métriques custom
└── Alembic (migrations — 3 fichiers)
```

### WebSockets actifs

| Channel | Path | Usage |
|---|---|---|
| Courses | `/ws/courses` | Collaboration temps réel listes de courses |
| Planning | `/ws/planning` | Sync planning semaine multi-utilisateurs |
| Notes | `/ws/notes` | Édition collaborative de notes |
| Projets | `/ws/projets` | Suivi projets maison en temps réel |

### Cron jobs existants

| Job ID | Schedule | Action |
|---|---|---|
| `rappels_famille` | 07h00 quotidien | Anniversaires, documents, crèche, jalons |
| `rappels_maison` | 08h00 quotidien | Garanties, contrats, entretien |
| `rappels_generaux` | 08h30 quotidien | Inventaire, garanties générales |
| `entretien_saisonnier` | Lundi 06h00 | Création tâches entretien saisonnières |
| `push_quotidien` | 09h00 quotidien | Web Push alertes urgentes + jeux |
| `enrichissement_catalogues` | 1er du mois 03h00 | Enrichissement IA 4 catalogues JSON |

---

## 3. Analyse module par module

### 🍽️ Cuisine

**État** : ~72% complet | Backend solide, quelques features UI manquantes

#### Ce qui est implémenté ✅
- CRUD recettes complet (import URL, PDF, enrichissement auto nutrition/bio/robots)
- Planning semaine IA (Mistral) avec suggestions contextuelles météo
- Listes de courses + génération depuis planning + collaboration WebSocket
- Inventaire avec badges Open Food Facts (Nutri-Score, Éco-Score, NOVA)
- Photo frigo OCR Pixtral (identification ingrédients zones identifiées)
- Anti-gaspillage : score hebdo + historique + trophées gamification
- Batch cooking : sessions, étapes par robot, préparations surgelées
- Stepper "Ma Semaine" 4 étapes (Planning → Inventaire → Courses → Récap)
- Import PDF recette avec enrichissement (calories, tags, robots)
- Page /cuisine/nutrition : histogramme quotidien + KPIs macros

#### Ce qui manque ❌
- **Profil diététique structuré** : objectifs calories/macros personnalisables par utilisateur (stockés en DB)
- **Badge nutrition sur cartes recettes** : afficher les macros calculées dans la liste recettes
- **OCR photo-frigo → sync inventaire automatique** : le bouton "ajouter à l'inventaire" existe mais l'auto-sync continu n'est pas implémenté
- **Onboarding "Ma Semaine"** : popup première utilisation guidant l'utilisateur sur le stepper
- **Table nutrition incomplète** : 47 ingrédients couverts sur ~200+ ciblés → calcul macro silencieusement incomplet pour beaucoup de recettes
- **Rappels jour-par-jour cuisine** : push quotidien "ce soir tu prépares X" basé sur planning  
- **Saisonnalité enrichie inventaire** : affichage des produits de saison disponibles au marché

#### Bugs ⚠️
- `RetourRecette` utilise `feedback='like'|'neutral'` pour les favoris, mais les types TypeScript frontend utilisent `est_favori: boolean` → potentielle désynchronisation si le champ est lu directement
- `url_source` absent du modèle ORM `Recette` mais attendu dans `RecetteResponse` (retourne `None` systématiquement)

---

### 👨‍👩‍👦 Famille

**État** : ~97% complet | Module le plus avancé

#### Ce qui est implémenté ✅
- Hub famille contextuel (Aujourd'hui/À venir/Suggestions IA)
- Suivi Jules : jalons de développement, croissance (poids/taille vs normes OMS), carnet de santé
- Activités : CRUD + suggestions IA auto-préfill + météo contexte  
- Routines : matin/soir avec complétion rapide et streak
- Budget : CRUD + analyse IA anomalies + prédictions + OCR tickets
- Achats famille : onglets par personne, scoring IA, suggestions Vinted, annonces LBC générées par IA
- Anniversaires : CRUD + checklist auto générée (invitations, gâteau, cadeaux...)
- Config Garde : zones, semaines fermeture crèche, jours-sans-crèche planning
- Weekend suggestions IA : activités, météo, séjours
- Contacts, Documents, Calendriers (Google OAuth)

#### Ce qui manque ❌
- **Album photo** : page `redirect("/famille")` intentionnel, service supprimé — fonctionnalité absente
- **Journal de famille** : idem redirect, supprimé — pas de mémoire narrative de la famille
- **Tests famille** : `tests/api/test_famille_achats.py` et `test_famille_garde.py` marqués "À FAIRE" dans le roadmap
- **Partage de planning avec la crèche** : le lien "jours sans crèche" génère les dates mais aucun export ou contact de la crèche
- **Suivi diversification Jules** : service `diversification.py` existe mais aucune page UI dédiée

---

### 🏡 Maison

**État** : ~95% complet | Très riche, seul jardin IA enrichi manquant

#### Ce qui est implémenté ✅
- Hub contextuel maison (briefing quotidien + alertes actives)
- 152 endpoints : projets, routines, entretien prédictif, jardin, stocks cellier, meubles, artisans, contrats, garanties (+prédictions panne IA), diagnostics, estimations, eco-conseils, devis, visualisation pièces
- Ménage : planning hebdomadaire IA + tâches ponctuelles
- Énergie : releves, tendances, prévisions IA, conseils économies
- Artisan assistant IA (chat maison)
- Gamification entretien (points, badges)
- Visualisation pièces avec objets et historique

#### Ce qui manque ❌
- **Suggestions jardin IA enrichies** (Phase AB) : au-delà des règles catalogue, pas de génération IA contextuelle saisonnière
- **Cellier ↔ inventaire cuisine** : pas de synchronisation entre le cellier maison et l'inventaire cuisine (doublons potentiels)
- **Budget ménager global** : pas de synthèse finances maison + famille sur un même tableau
- **Maintenance prédictive étendue** : prédictions panne sur garanties ✅, mais pas sur objets maison non garantis

---

### 🎮 Jeux

**État** : 100% complet ✅

#### Ce qui est implémenté ✅
- Dashboard value-bets + KPIs bankroll
- Paris sportifs : CRUD + stats + prédictions IA + analyse patterns + value-bets
- Loto + Euromillions : tirages, grilles, stats, génération IA pondérée, numéros en retard
- Performance : ROI détaillé + breakdown par sport/championnat
- Jeu responsable : suivi mensuel, limites, auto-exclusion
- OCR tickets loto (Pixtral)
- Historique des cotes
- Séries de victoires/défaites avec alertes

#### Ce qui manque ❌
- **Scraping automatique des cotes** : les cotes sont saisies manuellement, pas de connexion à une API bookmaker (Oddsportal, The Odds API…)
- **Alertes en temps réel matchs live** : notifications push pendant un match pour un pari en cours
- **Statistiques avancées par équipe** : possession, xG, forme à domicile/extérieur (données football.api)

---

### 📅 Planning général

**État** : ~80% complet

#### Ce qui est implémenté ✅
- Planning repas semaine + génération IA
- Nutrition hebdo (macros par jour)
- Export iCal
- "Ma Semaine" unifiée (repas + activités + matchs + tâches maison)
- Timeline page

#### Ce qui manque ❌
- **Vue calendrier mensuelle aggregée** : tous les événements (famille + maison + jeux) sur un même calendrier
- **Rappels push cuisine** : "Ce soir : Poulet rôti (45min de préparation)" → non implémenté
- **Conflits de planning** : `ServiceConflits` existe mais non exposé en frontend
- **Intégration Google Calendar bidirectionnelle** : OAuth ✅, mais sync des événements Planning vers Google non testé de bout en bout

---

### 🎯 Dashboard

**État** : ~85% complet

#### Ce qui est implémenté ✅
- Widgets : Stock critique, Repas du jour, Prochaines activités, Budget famille, Jeux performances, Rappels
- Actions rapides contextuelles
- `GET /api/v1/dashboard/cuisine` : données cuisine agrégées

#### Ce qui manque ❌
- **Widgets configurables** : drag & drop, choix des métriques affichées (roadmap ouvert)
- **Score de santé global** : indicateur synthétique (bien-être famille + maison + budget)
- **Météo intégrée au dashboard** : la météo est dans `/outils/meteo` mais pas dans le dashboard principal

---

### 🛠️ Outils

**État** : ~90% complet

#### Ce qui est implémenté ✅
- Chat IA Mistral multi-contexte (cuisine, maison, famille, jeux, général)
- Convertisseur unités (masse, volume, températures)
- Minuteur multi (cuisine)
- Notes + Journal + Contacts + Liens favoris + Mots de passe maison
- Météo (Open-Meteo)
- Nutritionniste IA : histogramme hebdo + chat Mistral nutrition + KPIs macros

#### Ce qui manque ❌
- **Partage de notes** : les notes sont privées, pas de partage famille
- **Notes vocales** : dictaphone → texte (Web Speech API ou Whisper)
- **Outils contextuels** : le convertisseur existe sur la page recette mais pas dans les autres contextes où il serait utile (inventaire, courses)

---

### 🔐 Admin

**État** : Basique mais fonctionnel

#### Ce qui est implémenté ✅
- Page admin `/admin` protégée par rôle
- Audit logs : liste, stats, export CSV
- Backup DB : CLI script + GitHub Actions workflow

#### Ce qui manque ❌
- **Gestion utilisateurs** : pas de liste/modification/suppression d'utilisateurs depuis l'admin UI
- **Tableau de bord monitoring** : métriques Prometheus exposées mais pas visualisées dans l'UI
- **Déclenchement manuel de jobs** : aucun bouton "lancer le cron maintenant" (voir section 11)

---

## 4. Bugs & régressions identifiés

### 🔴 Critiques

| # | Bug | Localisation | Impact |
|---|---|---|---|
| B-01 | **Push subscriptions perdues au redémarrage** : `_subscriptions` stockées en dict en mémoire dans `NotifWebCoreService`, pas de table DB dédiée | `src/services/core/notifications/notif_web_core.py` | Toutes les souscriptions Web Push cassées après chaque déploiement |
| B-02 | **Pas d'endpoint VAPID public key** : le frontend a besoin de la clé publique VAPID pour s'abonner — aucun `GET /api/v1/push/vapid-public-key` n'est exposé | `src/api/routes/push.py` | PWA notifications impossibles sans config manuelle |
| B-03 | **Digest ntfy et rappel courses jamais schedulés** : `envoyer_digest_quotidien()` et `envoyer_rappel_courses()` sont dans `ServiceNtfy` mais n'apparaissent dans aucun job APScheduler | `src/services/core/cron/jobs.py`, `notif_ntfy.py` | Feature entière morte |

### 🟠 Hauts

| # | Bug | Localisation | Impact |
|---|---|---|---|
| B-04 | **Cache L1 non partagé** : en mode multi-workers (Uvicorn + Gunicorn), chaque process a son propre L1. Sans Redis configuré, les workers se désynchronisent | `src/core/caching/orchestrator.py` | Données périmées affichées selon le worker |
| B-05 | **Accès direct attribut privé** : `_job_push_quotidien` lit `push_service._subscriptions` — couplage fragile à la structure interne | `src/services/core/cron/jobs.py` | Cron silencieusement cassé si l'implémentation interne change |
| B-06 | **`url_source` absent du modèle Recette** : le schéma `RecetteResponse` retourne toujours `None` pour `url_source` mais l'UI attend une URL cliquable | `src/core/models/recettes.py`, `src/api/schemas/recettes.py` | Lien "source" non fonctionnel sur les recettes importées depuis URL |
| B-07 | **`verifier_saison` silencieusement ignoré** : le cron entretien saisonnier vérifie `hasattr()` mais ne log qu'en DEBUG si absent → aucun feedback si le service ne démarre pas | `src/services/core/cron/jobs.py` | Maintenance saisonnière silencieusement inactive |
| B-08 | **`RepasPlanning` modèle manquant** : 1 test dashboard est `skip` car le modèle n'est pas défini | `tests/api/test_routes_dashboard_jeux.py` | Couverture test incomplète |

### 🟡 Moyens

| # | Bug | Localisation | Impact |
|---|---|---|---|
| B-09 | **Favicon/manifest Push** : le `manifest.json` ne définit pas les champs `gcm_sender_id`/`background_sync` nécessaires pour certains navigateurs | `frontend/public/manifest.json` | Comportement push instable sur Chrome Android |
| B-10 | **Table `liste_cours` en doublon** : SQL contient à la fois `liste_cours` et `listes_courses` (coquille) | `sql/INIT_COMPLET.sql` | Confusion dans les requêtes directes SQL |
| B-11 | **Album/Journal frontend subsistent** : les pages effectuent des `redirect()` mais le lien sidebar existe encore pour "Calendriers" qui pointe vers `/famille/calendriers` inexistant | `frontend/src/composants/disposition/barre-laterale.tsx` | 404 potentiel |
| B-12 | **`RetourRecette.est_favori` vs `feedback`** : ORM utilise `feedback='like'`, les types TypeScript utilisent `est_favori: boolean` | `frontend/src/types/recettes.ts` | Désync si la propriété est lue directement |

### 🟢 Mineurs / Cosmétiques

| # | Bug | Localisation |
|---|---|---|
| B-13 | **Nutrition table 47/200+ ingrédients** : calcul macro silencieusement incomplet | `data/reference/nutrition_table.json` |
| B-14 | **L3 cache jamais écrit** : `persistent=False` par défaut → L3 lecture seule seulement | `src/core/caching/orchestrator.py` |
| B-15 | **Playwright tests CI** : uniquement `--project=chromium`, aucun test Firefox/WebKit en CI | `.github/workflows/frontend-tests.yml` |
| B-16 | **Sprint11 connu** : `asyncio_mode=strict` requis, `pytestmark` manquant dans certains nouveaux fichiers de test | `pytest.ini`, tests récents |

---

## 5. Manques & features incomplètes

### 🍽️ Cuisine — lacunes

| Feature | Effort | Impact |
|---|---|---|
| Profil diététique structuré (objectifs calories/macros per user) | M | ⭐⭐⭐ |
| OCR photo-frigo → auto-ajout inventaire sans confirmation | S | ⭐⭐⭐ |
| Rappels push "soir cuisine" : "Ce soir tu prépares X" | S | ⭐⭐⭐ |
| Badge nutrition sur cartes recettes (liste + hub) | S | ⭐⭐ |
| Table nutrition étendue (200+ ingrédients vs 47 actuels) | M | ⭐⭐ |
| Onboarding Ma Semaine (popup first-use) | S | ⭐⭐ |
| Partage de liste de courses avec invité (lien ou QR code) | M | ⭐⭐ |
| Historique prix articles (suivi inflation) | M | ⭐⭐ |
| Scan code-barres continu (stream caméra) pour inventaire | L | ⭐⭐ |
| Génération automatique recette à partir d'une photo plat (Pixtral) | M | ⭐⭐⭐ |

### 👨‍👩‍👦 Famille — lacunes

| Feature | Effort | Impact |
|---|---|---|
| Diversification alimentaire Jules (UI dédiée) | M | ⭐⭐⭐ |
| Journal de famille (texte + photos — supprimé à remettre ?) | L | ⭐⭐ |
| Album photo avec timeline (supprimé) | L | ⭐⭐ |
| Export/partage planning Jules (crèche, médecin) | S | ⭐⭐ |
| Tests famille (achats, garde) | M | ⭐⭐ |
| Rappels médicaux Jules (vaccins, RDV) en push | S | ⭐⭐⭐ |
| Suivi poids/taille des adultes (santé famille globale) | M | ⭐⭐ |

### 🏡 Maison — lacunes

| Feature | Effort | Impact |
|---|---|---|
| Cellier ↔ Inventaire cuisine : synchronisation | M | ⭐⭐⭐ |
| Budget ménager global : vue agrégée maison + famille | M | ⭐⭐ |
| Suggestions jardin IA saisonnières enrichies | S | ⭐⭐ |
| Comparateur énergie (historique vs voisins ou indices nationaux) | L | ⭐⭐ |

### 📊 Dashboard — lacunes

| Feature | Effort | Impact |
|---|---|---|
| Widgets drag & drop configurables | L | ⭐⭐⭐ |
| Score de bien-être synthétique (Famille + Maison + Budget) | M | ⭐⭐⭐ |
| Météo intégrée (widget dashboard) | S | ⭐⭐ |
| Activité récente / fil d'événements (timeline) | M | ⭐⭐ |

### 🔔 Notifications — lacunes importantes

| Feature | Effort | Impact |
|---|---|---|
| Persistance Push subscriptions en DB | S | 🔴 CRITIQUE |
| Endpoint VAPID public key | XS | 🔴 CRITIQUE |
| Canal email (reset password, invitations, résumés hebdo) | L | ⭐⭐⭐ |
| Canal WhatsApp (récapitulatifs + commandes vocales) | L | ⭐⭐⭐ |
| ntfy digest quotidien schedulé | XS | ⭐⭐⭐ |
| Rappel courses ntfy (push vers mobile) | XS | ⭐⭐⭐ |

---

## 6. SQL — Consolidation & état actuel

### État du schéma

Le fichier `sql/INIT_COMPLET.sql` (v3.0, 4416 lignes) est **l'unique source de vérité** en mode développement. Il est **idempotent** (`DROP TABLE ... CASCADE` en tête) et peut être ré-exécuté sans danger dans Supabase SQL Editor.

### Structure du schéma

```
sql/
├── INIT_COMPLET.sql     ← Schéma complet + RLS + indexes + triggers + inline migrations
└── migrations/          ← Fichiers de migration SQL (dev, non utilisés actuellement)
```

### Incohérences et points à consolider

| # | Problème | Tables concernées | Action recommandée |
|---|---|---|---|
| SQL-01 | **Doublon `liste_cours` vs `listes_courses`** | `liste_cours`, `listes_courses` | Supprimer `liste_cours` (coquille) et vérifier tous les `INSERT INTO liste_cours` |
| SQL-02 | **Colonnes `user_id` manquantes** | Certaines tables de liaison N:M n'ont pas de `user_id` → RLS trop permissif | Auditer les tables sans `user_id` + RLS |
| SQL-03 | **Tables orphelines sans modèle ORM** | `journal_bord`, `sessions_travail`, `log_statut_objets` (à vérifier) | Mapper via ORM ou supprimer |
| SQL-04 | **Tables ORM sans SQL** | `voyage.py`, `album.py` (supprimé) modèles ORM restants sans `CREATE TABLE` dans INIT_COMPLET | Nettoyer les deux sens |
| SQL-05 | **Inline migrations en bas de fichier** | `ALTER TABLE recettes ADD COLUMN ...` en bas de INIT_COMPLET | Déplacer en tête dans les sections `CREATE TABLE` correspondantes |
| SQL-06 | **Index manquants** | `recette_ingredients(ingredient_id)`, `repas(planning_id)`, `articles_modeles(modele_id)` | Ajouter pour les JOINs les plus fréquents |
| SQL-07 | **Contraintes FK non nommées** | `REFERENCES users(id)` sans `CONSTRAINT fk_xxx` | Nommer pour faciliter les erreurs de debug |
| SQL-08 | **Pas de partition temporelle** | `historique_inventaire`, `historique_action`, `audit_logs` grossissent indéfiniment | Envisager partition par année ou TTL trigger |

### Recommandation SQL (mode dev)

Puisque tu es en dev et que tu ne veux pas de migrations, voici le processus recommandé :

```bash
# Pour ajouter une colonne :
# 1. Modifier src/core/models/xxx.py (ajout mapped_column)
# 2. Modifier sql/INIT_COMPLET.sql à l'endroit exact du CREATE TABLE
# 3. Ré-exécuter INIT_COMPLET.sql dans Supabase SQL Editor (idempotent)
# 4. Commit une seule fois les 2 changements ensemble

# Vérification rapide de cohérence ORM ↔ SQL :
grep -h "__tablename__" src/core/models/*.py | sort > /tmp/orm_tables.txt
grep "^CREATE TABLE" sql/INIT_COMPLET.sql | sort > /tmp/sql_tables.txt
diff /tmp/orm_tables.txt /tmp/sql_tables.txt
```

---

## 7. Interactions intra-modules & inter-modules

### Interactions existantes (déjà câblées)

```
Planning ←→ Courses       : generer_depuis_planning (liste auto depuis menu de la semaine)
Planning ←→ Inventaire    : suggestions tiennent compte du stock disponible
Planning ←→ Batch Cooking : générer session batch depuis un planning
Inventaire ←→ Anti-gaspi  : produits proches péremption → suggestions recettes
Photo-frigo ←→ Suggestions : image → identification → recettes avec ingrédients détectés
Famille/Budget ←→ Dashboard: budget disponible → widget dashboard
Jeux/Bankroll ←→ Jeux/Responsable : limites financières → alertes paris
Maison/Énergie ←→ Maison/Finances : relèves → dépenses énergie
Famille/Config ←→ Planning : jours sans crèche → planning famille
```

### Interactions à créer (haute valeur)

#### 🔗 Cellier ↔ Inventaire Cuisine
**Problème** : Le cellier (`ArticleCellier`) et l'inventaire cuisine (`ArticleInventaire`) sont deux silos séparés avec des données similaires (produits alimentaires, quantités).  
**Solution** : Ajouter un champ `source: "cellier"|"cuisine"` dans la vue unifiée, ou créer un endpoint `/api/v1/inventaire/consolide` qui merge les deux.  
**Bénéfice** : Une seule liste de courses générée tenant compte de tout le stock maison.

#### 🔗 Anti-gaspillage ↔ Planning
**Problème** : La semaine suivante est plannifiée sans regard aux produits qui périment.  
**Solution** : Ajouter un step "Urgences anti-gaspi" dans le stepper Ma Semaine — propose d'inclure les recettes qui useront les produits à risque.  
**API** : `POST /api/v1/planning/generer?inclure_antigaspi=true`

#### 🔗 Jeux/Bankroll ↔ Famille/Budget
**Problème** : Les pertes/gains de paris ne sont pas reflétés dans le budget familial.  
**Solution** : Un bouton "Importer résultat du mois" dans Budget Famille qui additionne `somme_pertes_mois` des paris en `ArticleBudget` catégorie "loisirs/jeux".  
**API** : `GET /api/v1/famille/budget/import-jeux-mois`

#### 🔗 Jules/Santé ↔ Planning Cuisine
**Problème** : Les repas de Jules ne sont pas planifiés en tenant compte de son âge et allergies.  
**Solution** : Le planning génère une colonne "Jules" selon le profil enfant (`ProfilEnfant .date_naissance`, allergènes). Recettes filtrées `compatible_bebe=True` pour moins de 2 ans.  
**API** : Modifier `POST /api/v1/planning/generer` pour accepter `pour_jules: bool`.

#### 🔗 Maison/Entretien ↔ Routines
**Problème** : Les routines ménagères et les tâches d'entretien sont dans deux silos différents.  
**Solution** : Vue unifiée "À faire ce week-end" qui fusionnerait routines en retard + tâches entretien urgentes + tâches jardin.  
**API** : `GET /api/v1/maison/planning-weekend`

#### 🔗 Dashboard ↔ Météo ↔ Planning
**Problème** : La météo influence les activités, le jardin, le planning cuisine mais n'est pas centralisée dans le dashboard.  
**Solution** : Widget météo sur le dashboard avec contexte (pluie → suggestions cuisine dedans, soleil → rappel arrosage jardin, grand froid → emprunter manteau Jules).  
**Déjà partiel** : `suggestions-rapides` cuisine utilise la météo, à étendre au dashboard.

#### 🔗 Anniversaires ↔ Budget Famille ↔ Courses
**Problème** : Quand Jules a un anniversaire, il faut budget + liste de courses + invitations → silo actuel.  
**Solution** : Depuis une fiche anniversaire, générer en 1 clic : budget prévisionnel + liste de courses (gâteau, déco, goûter) + événement calendrier.  
**API** : `POST /api/v1/famille/anniversaires/{id}/preparer-evenement`

#### 🔗 Recherche globale ↔ Tous modules
**Existant** : `/api/v1/recherche/global` cherche recettes, projets, activités, notes, contacts.  
**Manquant** : Recettes dans planning, garanties, artisans, documents famille absents de la recherche.  
**Solution** : Étendre le handler de recherche avec 5 requêtes parallèles supplémentaires.

#### 🔗 Export PDF ↔ Tous modules
**Existant** : Export PDF courses, planning, recettes, budget.  
**Manquant** : Export "Rapport mensuel famille" (activités Jules + budget + anniversaires du mois) et "Carnet de bord maison" (entretiens, dépenses, projets).

---

## 8. Axes d'intégration IA

### IA déjà intégrée (ne pas dupliquer)

| Module | Service IA | Modèle |
|---|---|---|
| Planning repas | `ServiceSuggestions.suggerer_menus()` | Mistral Large |
| Photo frigo | `MultiModalAIService` | Pixtral 12B (vision) |
| Batch cooking | `ServiceBatchCooking.generer_planning_robot()` | Mistral Large |
| Anti-gaspillage | `ServiceSuggestions.anti_gaspillage()` | Mistral Large |
| Budget famille | `AnalyseBudgetIA` + anomalies | Mistral Large |
| Activités Jules | `JulesAIService` | Mistral Large |
| Weekend | `WeekendAIService` | Mistral Large |
| Achats famille | `AchatsIA.suggestions_enrichies()` + Vinted + LBC | Mistral Large |
| Projets maison | `ProjetsIAMixin.estimer_budget()` | Mistral Large |
| Garanties | Prédictions pannes | Mistral Large |
| Jeux | `JeuxAIService.suggerer_strategies()` | Mistral Large |
| Loto/Euromillions | Grilles IA pondérées | Mistral Large |
| Import recettes | Enrichissement nutrition/bio/robots | Mistral Large |
| Chat général | Multi-contexte (cuisine/maison/famille/jeux) | Mistral Large |
| OCR tickets | `ticket_caisse.py` (Pixtral) | Pixtral 12B |
| Résumé hebdo famille | `ServiceResumeHebdo` | Mistral Large |

### Nouveaux axes IA à implémenter

#### 🤖 IA-01 : Assistant vocal (Speech-to-Text → Action)
**Concept** : Dictaphone dans l'app → transcription Whisper → interprétation Mistral pour effectuer des actions.  
**Exemples** :
- "Ajoute du lait à la liste de courses" → `POST /api/v1/courses/{id}/articles`
- "J'ai pesé Jules, 11,4 kg" → `POST /api/v1/famille/jules/croissance`
- "Rappelle-moi d'appeler le plombier mardi" → `POST /api/v1/maison/routines`

**Stack** : Web Speech API (navigateur, gratuit) ou `whisper-tiny` local → Mistral pour extraction d'intention → dispatch vers API.  
**Effort** : L — nécessite mapping intention → API.

#### 🤖 IA-02 : Génération recette depuis photo plat
**Concept** : Photo d'un plat restaurant/magazine → Pixtral identifie → Mistral génère la recette complète.  
**API** : `POST /api/v1/recettes/generer-depuis-photo` (multipart image → RecetteResponse).  
**Effort** : S — déjà du code Pixtral dans `multimodal.py`, c'est une variation du prompt.

#### 🤖 IA-03 : Résumé hebdo intelligent multi-modules
**Concept** : Chaque lundi matin, générer un résumé personnalisé de la semaine : recettes cuisinées, budget dépensé, activités Jules, paris réussis/perdus, tâches maison faites, jardin = état.  
**Canal** : ntfy + email (si configuré).  
**API** : `POST /api/v1/dashboard/resume-semaine` (déclenché par cron + manuellement).  
**Effort** : M.

#### 🤖 IA-04 : Planificateur de vacances IA
**Concept** : "On part en Bretagne 5 jours avec Jules (22 mois)" → IA génère : planning d'activités, liste de courses adaptée, checklist voyage (déjà service `voyage.py`), budget prévisionnel.  
**API** : `POST /api/v1/famille/voyage/planifier-ia`.  
**Effort** : M — services voyage et checklist existent.

#### 🤖 IA-05 : Détection d'anomalies financières inter-modules
**Concept** : Analyser en cross-module toutes les dépenses (maison + famille + jeux) pour détecter patterns inhabituels ("tes dépenses courses ont augmenté de 35% ce mois").  
**API** : `GET /api/v1/dashboard/anomalies-financieres`.  
**Effort** : M.

#### 🤖 IA-06 : Coaching santé Jules proactif
**Concept** : Basé sur les mesures de croissance Julius (poids/taille), diversification, activités et normes OMS → message hebdo d'un "pédiatre IA" contextuel.  
**API** : `GET /api/v1/famille/jules/coaching-hebdo`.  
**Effort** : S — `JulesAIService` existe déjà.

#### 🤖 IA-07 : Optimisation budget courses IA
**Concept** : Analyser l'historique d'achat + les prix habituels → suggérer les substitutions économiques ("Remplace noix de cajou par noix de Grenoble, économie estimée 3€/semaine").  
**API** : `GET /api/v1/courses/optimiser-budget-ia`.  
**Effort** : M.

#### 🤖 IA-08 : Vision pour diagnostic maison
**Concept** : Uploader une photo d'un problème maison (fissure, humidité, panne) → Pixtral identifie le type de problème → Mistral génère diagnostic + devis estimatif + recommandations artisans.  
**API** : `POST /api/v1/maison/diagnostics/ia-photo`.  
**Effort** : M.

#### 🤖 IA-09 : Score bien-être familial global
**Concept** : Un indicateur 0-100 calculé chaque semaine à partir de : diversité alimentaire, activités Jules, budget équilibré, tâches maison à jour, sommeil (si Garmin connecté). Trend hebdomadaire.  
**API** : `GET /api/v1/dashboard/score-bienetre`.  
**Effort** : M.

#### 🤖 IA-10 : Suggestions proactives contextuelles (Push IA)
**Concept** : À 18h chaque jour, analyser le contexte (planning demain, météo, stock) et envoyer 1 notification personnalisée : "Demain il fait -5°, pense à décongeler le poulet" ou "Jules n'a pas eu d'activité artiste cette semaine".  
**Canal** : ntfy / Web Push.  
**Effort** : M — nécessite orchestrateur de contexte journalier.

---

## 9. Jobs automatiques — Planning cron

### Jobs existants (rappel)

| Schedule | Job | Statut |
|---|---|---|
| 07h00 | Rappels famille (anniversaires, jalons, crèche) | ✅ Actif |
| 08h00 | Rappels maison (garanties, contrats, entretien) | ✅ Actif |
| 08h30 | Rappels généraux (inventaire, alertes) | ✅ Actif |
| 09h00 | Push quotidien (urgences + jeux) | ✅ Actif |
| Lundi 06h00 | Entretien saisonnier | ✅ Actif |
| 1er mois 03h00 | Enrichissement catalogues JSON (IA) | ✅ Actif |

### Jobs à créer

| ID | Schedule | Description | Canal notification | Effort |
|---|---|---|---|---|
| J-01 | **Lundi 07h30** | **Résumé hebdo complet** : recettes cuisinées, budget, activités Jules, tâches maison faites, gains/pertes jeux | ntfy digest + email (si dispo) | M |
| J-02 | **18h00 quotidien** | **Push contextuel IA** : "Ce soir tu prépares X (45min)" + recommandations météo | ntfy / Web Push | M |
| J-03 | **Dimanche 20h00** | **Génération planning semaine suivante** IA si le planning est vide | ntfy ("Ton planning est vide, génère-le ?") | S |
| J-04 | **06h00 quotidien** | **Alerte péremptions** : produits expirant dans 48h → suggère recettes | ntfy / Web Push | S |
| J-05 | **09h00 quotidien** | **digest ntfy** (déjà implémenté, juste **scheduler** le cron) | ntfy | XS |
| J-06 | **18h00 quotidien** | **Rappel courses urgentes** (déjà implémenté, juste **scheduler**) | ntfy | XS |
| J-07 | **1er du mois** | **Rapport mensuel budget** : synthèse famille + maison + jeux + recommandations IA | ntfy / email | M |
| J-08 | **Vendredi 17h00** | **Score weekend** : suggestions activités basées météo des 2 prochains jours + état Jules | ntfy | S |
| J-09 | **1er du mois** | **Contrôle garanties et contrats** : rappels expirations dans les 3 prochains mois | ntfy / email | XS (déjà 08h00 maison, à enrichir) |
| J-10 | **Mercredi 20h00** | **Rapport jardin** : arrosage, semis prévus cette semaine selon données météo | ntfy | S |
| J-11 | **Hebdo dimanche** | **Sync cotes paris sportifs** depuis une API externe (si abonnement) | Interne | L |
| J-12 | **Quotidien 07h00** | **Score bien-être Jules** : alerte si dérive courbe OMS | ntfy vers parents | S |

---

## 10. Notifications — WhatsApp, Mail, Push

### État actuel

| Canal | Service | Statut | Couverture |
|---|---|---|---|
| **ntfy.sh** | `ServiceNtfy` | ✅ Implémenté | Maison, tâches, digest (pas schedulé) |
| **Web Push (VAPID)** | `NotifWebCoreService` | 🔴 Critique (en-mémoire) | Famille, jeux, maison |
| **Email** | — | ❌ Absent | Rien |
| **SMS** | — | ❌ Absent | Rien |
| **WhatsApp** | — | ❌ Absent | Rien |

### Plan notifications complet

#### Canal Email (Priorité HAUTE)

**Stack recommandée** : `Resend` (API email moderne, quota gratuit 3000/mois, SDK Python simple)  
ou alternative : `Brevo` (ex-Sendinblue), `Postmark`, ou SMTP Supabase natif.

```python
# Exemple d'intégration Resend
# pip install resend
import resend
resend.api_key = os.environ["RESEND_API_KEY"]

resend.Emails.send({
    "from": "matanne@votredomaine.fr",
    "to": ["user@example.com"],
    "subject": "Ton planning de la semaine 🍽️",
    "html": "<html>...</html>"
})
```

**Cas d'usage email** :
- Reset de mot de passe (actuellement absent du flow auth)
- Vérification email à l'inscription
- Résumé hebdo famille (optionnel, désactivable)
- Rapport mensuel budget
- Alerte critique (expiration garantie importante, stock nul sur article prioritaire)
- Invitation d'un autre membre famille

**Fichiers à créer** :
- `src/services/core/notifications/notif_email.py` — `ServiceEmail`
- Intégrer dans `src/api/routes/auth.py` (reset password, verify email)
- Ajouter dans cron J-01 (résumé hebdo)

#### Canal WhatsApp (Priorité MOYENNE)

**Stack recommandée** : **WhatsApp Business API via Twilio** ou **Meta Cloud API** (gratuit pour les 1000 premiers messages/mois).

**Alternative simple** : `ntfy.sh` est déjà installé et couvre le push mobile — WhatsApp est un nice-to-have.

**Cas d'usage WhatsApp** :
- Commandes vocales converties en actions ("Ajoute du lait aux courses" → WhatsApp → webhook → API)
- Partage de liste de courses avec un autre téléphone sans app installée
- Rapport hebdo qui se lit dans WhatsApp sans ouvrir l'app
- Rappels crèche (jours sans crèche cette semaine)

```python
# Exemple Twilio WhatsApp
# pip install twilio
from twilio.rest import Client
client = Client(account_sid, auth_token)
message = client.messages.create(
    from_="whatsapp:+14155238886",
    body="🛒 Ta liste de courses: lait, pain, yaourt",
    to="whatsapp:+33600000000"
)
```

**Webhook entrant WhatsApp → actions** :
```
POST /api/v1/webhooks/whatsapp
→ Extraire message texte
→ Mistral : interpréter intention (ajouter courses, rappel, info météo...)
→ Dispatcher vers API interne correspondante
→ Répondre avec confirmation
```

**Fichiers à créer** :
- `src/services/core/notifications/notif_whatsapp.py`
- `src/api/routes/webhooks.py` : ajouter route `/whatsapp` (webhook entrant Twilio)

#### Correctifs Push urgents (Priorité CRITIQUE)

```python
# CORRECTION B-01 : Persistance DB des subscriptions
# Ajouter dans src/core/models/notifications.py :
class AbonnementPush(Base):
    __tablename__ = "abonnements_push"
    id: Mapped[int]
    user_id: Mapped[str]
    endpoint: Mapped[str]  # URL unique VAPID
    p256dh: Mapped[str]    # Clé publique navigateur
    auth: Mapped[str]      # Token auth
    cree_le: Mapped[datetime]
    actif: Mapped[bool] = True

# + dans notif_web_core.py : charger/sauvegarder depuis DB au lieu de dict en mémoire
```

```python
# CORRECTION B-02 : Exposer la clé VAPID publique
# Dans push.py ajouter :
@router.get("/vapid-public-key")
async def get_vapid_public_key():
    return {"public_key": settings.VAPID_PUBLIC_KEY}
```

---

## 11. Mode Admin / Déclenchement manuel

### Concept

Un **panneau admin étendu** accessible uniquement avec `role == "admin"`, permettant de déclencher manuellement tout job ou action automatique. Invisible pour les utilisateurs normaux. Essentiel en développement pour tester sans attendre la plage horaire.

### Architecture recommandée

#### Backend — Route admin étendue

```python
# src/api/routes/admin.py — Ajouter ces endpoints :

# Lister tous les jobs disponibles
@router.get("/jobs", response_model=list[JobInfoResponse])
async def lister_jobs(user: dict = Depends(require_role("admin"))):
    """Retourne tous les jobs APScheduler disponibles + dernier run + statut"""

# Déclencher un job manuellement
@router.post("/jobs/{job_id}/run")
async def executer_job(job_id: str, user: dict = Depends(require_role("admin"))):
    """Exécute immédiatement le job désigné"""
    jobs_disponibles = {
        "rappels_famille": _job_rappels_famille,
        "rappels_maison": _job_rappels_maison,
        "push_quotidien": _job_push_quotidien,
        "digest_ntfy": ServiceNtfy.envoyer_digest_quotidien,
        "rappel_courses": ServiceNtfy.envoyer_rappel_courses,
        "enrichissement_catalogues": _job_enrichissement_catalogues,
        "resume_hebdo": ServiceResumeHebdo.generer_resume,
        "score_bienetre": CalculScoreBienetre.calculer,
        ...
    }
    if job_id not in jobs_disponibles:
        raise HTTPException(404, f"Job inconnu : {job_id}")
    await executer_async(jobs_disponibles[job_id])
    return {"status": "executed", "job_id": job_id, "executed_at": datetime.utcnow()}

# Envoyer une notification test
@router.post("/notifications/test")
async def envoyer_notification_test(
    canal: str,  # "ntfy" | "push" | "email" | "whatsapp"
    message: str,
    user: dict = Depends(require_role("admin"))
):
    """Envoie une notif test sur le canal demandé"""

# Recalculer les alertes inventaire maintenant
@router.post("/actions/recalculer-alertes")
async def recalculer_alertes(user: dict = Depends(require_role("admin"))):
    """Force le recalcul de toutes les alertes inventaire/maison"""

# Purger les caches
@router.post("/cache/purge")
async def purger_cache(pattern: str = "*", user: dict = Depends(require_role("admin"))):
    """Invalide le cache selon un pattern"""
```

#### Frontend — Page admin étendue

```typescript
// Ajouter dans frontend/src/app/(app)/admin/page.tsx

// Onglet "Jobs"
const { data: jobs } = useQuery({ queryKey: ['admin-jobs'], queryFn: listerJobs })

// Bouton par job :
<Button onClick={() => executerJob(job.id)} variant="outline">
  ▶ Exécuter maintenant
</Button>
// + badge dernière exécution + statut (success/error)

// Onglet "Notifications test"
// Formulaire : canal (ntfy/push/email) + message + bouton envoyer

// Onglet "Cache"
// Bouton purge par module + stats (hits/misses)

// Onglet "Utilisateurs" (nouveau)
// Liste des comptes, modification rôle, désactivation
```

### Jobs disponibles dans le panneau admin

| ID | Libellé affiché | Catégorie |
|---|---|---|
| `rappels_famille` | Rappels famille (anniversaires, crèche...) | Famille |
| `rappels_maison` | Rappels maison (garanties, contrats...) | Maison |
| `push_quotidien` | Push quotidien (alertes urgentes) | Notifications |
| `digest_ntfy` | Digest ntfy quotidien | Notifications |
| `rappel_courses` | Rappel courses urgentes | Courses |
| `entretien_saisonnier` | Entretien saisonnier | Maison |
| `enrichissement_catalogues` | Enrichissement catalogues IA | IA |
| `resume_hebdo` | Résumé hebdomadaire famille | Famille |
| `peremptions_urgentes` | Alertes péremptions J+48h | Inventaire |
| `score_bienetre` | Score bien-être global | Dashboard |
| `sync_cotes` | Sync cotes paris (externe) | Jeux |

---

## 12. Axes d'innovation identifiés

### 🚀 Innovations haute valeur

#### Innovation-01 : Écosystème d'automations type "IFTTT"
**Concept** : Interface visuelle "Si [déclencheur] → alors [action]" configurable.  
**Exemples** :
- "Si stock lait < 2 → Ajouter 6 laits aux courses"
- "Si demain > 3°C → Rappel arroser jardin"
- "Si pari gagné > 50€ → Ajouter à budget loisirs"
- "Si Jules a médecin → Ajouter en absent à la crèche"

**Stack** : Table `automations` en DB + moteur de règles simplifié + APScheduler.  
**Effort** : L mais très haute valeur.

#### Innovation-02 : Timeline de vie familiale
**Concept** : Visualisation chronologique de tous les événements importants : naissance Jules, premiers pas, anniversaires, rénovations maison, voyages, victoires sportives.  
**Source** : Jalons Jules + Événements familiaux + Projets maison + Matchs mémorables.  
**Effort** : M.

#### Innovation-03 : Budget prédictif annuel
**Concept** : Basé sur l'historique, prédire les dépenses des 12 prochains mois et alerter sur les gros postes à venir (vacances, rentrée scolaire, révision chaudière...).  
**Effort** : M.

#### Innovation-04 : Mode "Congé" et "Voyage" auto-adapté
**Concept** : Déclarer "On est en vacances du 15 au 22 juillet" → l'app désactive certains rappels (pas de rappel arrosage si jardin géré par un voisin), génère la checklist voyage, adapte le planning cuisine (repas voyage/snacks).  
**Effort** : M.

#### Innovation-05 : Connexion Garmin / santé adultes
**Concept** : Les modèles Garmin existent (`GarminToken`, `ResumeQuotidienGarmin`). Activer l'intégration pour : calories brûlées → recommandations repas du soir ; qualité sommeil → conseil récupération Jules.  
**Effort** : L (OAuth Garmin Connect + webhook daily sync).

#### Innovation-06 : Mode "Budget Famille Serré"
**Concept** : Activer un mode "budget contrainte" qui : filtre les recettes par coût/portion, suggère substitutions moins chères, compare prix entre magasins, génère un plan de repas sous Budget N€/semaine.  
**Effort** : M.

#### Innovation-07 : Gamification famille complète
**Concept** : Étendre la gamification (déjà présente sur entretien maison) à toute la famille : points pour routines complétées, défis hebdo, badges "Zéro gaspi cette semaine", tableau de bord points famille.  
**Effort** : M — `ServiceGamification` existe dans `src/services/core/gamification.py`.

#### Innovation-08 : Scan reçus et factures automatique
**Concept** : Uploader une photo de ticket de caisse → Pixtral extrait : montant, date, catégorie, articles → intégration automatique dans :
- Budget famille si supermarché
- Garanties si achat électroménager
- Inventaire si produits reconnus

**Déjà partiel** : scan ticket courses (OCR Pixtral) existe, à étendre.

### 💡 Petites innovations rapides (Quick wins)

| # | Idée | Effort | Impact |
|---|---|---|---|
| QW-01 | Widget météo sur dashboard (déjà API météo existante) | XS | ⭐⭐⭐ |
| QW-02 | Bouton "Recette Surprise" aléatoire filtrée par saison + frigo | XS | ⭐⭐⭐ |
| QW-03 | Partage liste de courses par QR code (lien temporaire) | S | ⭐⭐⭐ |
| QW-04 | Compteur de jours depuis dernière cuisine de chaque recette | XS | ⭐⭐ |
| QW-05 | Estimation temps de préparation en fonction du niveau de la recette | XS | ⭐⭐ |
| QW-06 | "Aujourd'hui dans l'histoire de la famille" (événements passés ce jour) | S | ⭐⭐⭐ |
| QW-07 | Mode sombre/clair forcé selon heure (auto après 21h) | XS | ⭐⭐ |
| QW-08 | Impression optimisée recette (CSS print) | XS | ⭐⭐ |
| QW-09 | Synchronisation planning → Apple Calendar (iCal existant) | S | ⭐⭐ |
| QW-10 | Score anti-gaspi hebdo partageable (image générée) | S | ⭐⭐ |

---

## 13. Synthèse & roadmap recommandée

### Priorités immédiates (< 1 semaine)

| # | Action | Effort | Catégorie |
|---|---|---|---|
| P-01 | **Fixer B-01** : persistance push subscriptions en DB | S | 🔴 Bug critique |
| P-02 | **Fixer B-02** : endpoint `GET /push/vapid-public-key` | XS | 🔴 Bug critique |
| P-03 | **Fixer B-03** : scheduler ntfy digest + rappel courses | XS | 🟠 Bug haut |
| P-04 | **SQL-01** : supprimer table `liste_cours` (doublon) | XS | 🟠 SQL |
| P-05 | **SQL-05** : déplacer inline ALTER TABLE en tête de CREATE TABLE | S | 🟠 SQL |

### Court terme (1-3 semaines)

| # | Action | Effort | Catégorie |
|---|---|---|---|
| CT-01 | **Canal email** : service `ServiceEmail` + reset password + verify | L | 📧 Notifications |
| CT-02 | **Mode Admin étendu** : panneau jobs + trigger manuel | M | 🔧 Admin |
| CT-03 | **Job J-02** : push contextuel soir (planning demain + météo) | M | ⏱️ Cron |
| CT-04 | **Job J-01** : résumé hebdo lundi matin | M | ⏱️ Cron |
| CT-05 | **IA-06** : coaching hebdo Jules () | S | 🤖 IA |
| CT-06 | **IA-02** : recette depuis photo (variation Pixtral) | S | 🤖 IA |
| CT-07 | **F-01** (Famille) : tests achats + garde | M | ✅ Tests |
| CT-08 | **SQL-06** : index manquants sur relations fréquentes | S | SQL |

### Moyen terme (1-2 mois)

| # | Action | Effort | Catégorie |
|---|---|---|---|
| MT-01 | **Interaction** Cellier ↔ Inventaire cuisine | M | 🔗 Inter-modules |
| MT-02 | **Canal WhatsApp** + webhook entrant | L | 📱 Notifications |
| MT-03 | **Profil diététique structuré** (Phase H complète) | M | 🍽️ Cuisine |
| MT-04 | **Dashboard score bien-être** (IA-09) | M | 📊 Dashboard |
| MT-05 | **Innovation-01** : Automations "Si → Alors" | L | 🚀 Innovation |
| MT-06 | **Widgets dashboard configurables** | L | 📊 Dashboard |
| MT-07 | **IA-01** : Assistant vocal (Speech-to-Text → Action) | L | 🤖 IA |
| MT-08 | **Innovation-02** : Timeline vie familiale | M | 🚀 Innovation |
| MT-09 | **OCR photo-frigo** auto-sync inventaire (Phase K complète) | S | 🍽️ Cuisine |

### Long terme (3+ mois)

| # | Action | Effort | Catégorie |
|---|---|---|---|
| LT-01 | **Innovation-05** : Connexion Garmin santé adultes | L | 🚀 |
| LT-02 | **Innovation-06** : Mode Budget Serré complet | M | 🚀 |
| LT-03 | **Innovation-07** : Gamification famille complète | M | 🚀 |
| LT-04 | **Innovation-04** : Mode Congé/Voyage auto-adapté | M | 🚀 |
| LT-05 | **Diversification alimentaire Jules** (UI dédiée) | M | 👶 Famille |

---

## Annexe A — Résumé des alertes SQL

```sql
-- Doublon tables à nettoyer
DROP TABLE IF EXISTS liste_cours;  -- garder listes_courses

-- Index manquants à ajouter dans INIT_COMPLET.sql
CREATE INDEX IF NOT EXISTS idx_recette_ingredients_ingredient_id ON recette_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_repas_planning_id ON repas(planning_id);
CREATE INDEX IF NOT EXISTS idx_articles_courses_liste_id ON articles_courses(liste_id);
CREATE INDEX IF NOT EXISTS idx_historique_inventaire_article_id ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS idx_jalons_profil_id ON jalons(profil_enfant_id);
CREATE INDEX IF NOT EXISTS idx_paris_user_date ON jeux_paris_sportifs(user_id, date_pari);

-- Table Push Subscriptions manquante
CREATE TABLE IF NOT EXISTS abonnements_push_vapid (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint TEXT UNIQUE NOT NULL,
    p256dh TEXT NOT NULL,
    auth_key TEXT NOT NULL,
    user_agent TEXT,
    actif BOOLEAN DEFAULT TRUE,
    cree_le TIMESTAMPTZ DEFAULT NOW(),
    dernier_ping TIMESTAMPTZ
);
ALTER TABLE abonnements_push_vapid ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Utilisateur voit ses abonnements" ON abonnements_push_vapid
    FOR ALL USING (auth.uid() = user_id);
```

---

## Annexe B — Résumé des fichiers à créer

| Fichier | Contenu | Priorité |
|---|---|---|
| `src/services/core/notifications/notif_email.py` | `ServiceEmail` avec Resend ou SMTP | 🟠 CT-01 |
| `src/services/core/notifications/notif_whatsapp.py` | Client Twilio WhatsApp | 🟡 MT-02 |
| `src/services/core/notifications/notif_dispatcher.py` | Dispatcher multi-canal (email/push/ntfy/whatsapp) | 🟠 CT-01 |
| `src/api/routes/admin.py` (enrichi) | +endpoints jobs, notif-test, cache, users | 🟠 CT-02 |
| `src/services/core/automations/` | Moteur "Si → Alors" | 🟡 MT-01 |
| `frontend/src/app/(app)/admin/jobs/page.tsx` | UI déclenchement manuel des jobs | 🟠 CT-02 |
| `src/services/famille/diversification_ui.py` | Service UI diversification Jules | 🟡 LT-05 |

---

*Rapport généré le 27 mars 2026 — GitHub Copilot*
