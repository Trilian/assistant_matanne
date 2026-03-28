# 🗓️ Planning d'implémentation — Assistant Matanne
> **Source** : `ANALYSE_COMPLETE.md` (mise à jour Sprint 5 — 28 mars 2026)
> **État global** : ~98% de couverture fonctionnelle
> **Légende efforts** : XS ≤ 1h | S = 2-4h | M = 1-2j | L = 3-5j

---

## État d'avancement global

| Sprint | Statut | Thème |
|--------|--------|-------|
| Sprints 1 + 4 + 5 + 6 | ✅ TERMINÉ | Bugs critiques push, features Jules, email, admin, cron, WhatsApp |
| Sprint 7 | ✅ TERMINÉ | SQL consolidation + bugs résiduels + tests + doc cleanup |
| Sprint 8 | 🔜 À FAIRE | Inter-modules + Dashboard avancé |
| Sprint 9 | 🔜 À FAIRE | WhatsApp sortant + IA avancée |
| Sprint 10 | ✅ MVP IMPLÉMENTÉ | Innovations (Garmin, gamification, voyage smart, automations) |

---

## ✅ Ce qui est déjà implémenté

### Bugs critiques (P-01 à P-03 + B-05)
- ✅ **P-01** — Push subscriptions persistées en DB (`NotificationPersistenceMixin`, `abonnements_push_vapid`)
- ✅ **P-02** — Endpoint `GET /push/vapid-public-key` exposé
- ✅ **P-03** — Jobs `digest_ntfy` (09h00) et `rappel_courses` (18h00) ajoutés à APScheduler
- ✅ **B-05** — Accès fragile `_subscriptions` remplacé par DB

### Features cuisine/famille/Jules (Sprint 4)
- ✅ **CT-09** — Bouton 🍼 Version Jules : `POST /recettes/{id}/version-jules` + `ServiceVersionRecetteJules` (171L)
- ✅ **CT-09** — Profil aliments exclus Jules : `GET/PUT /famille/jules/aliments-exclus`
- ✅ **CT-06** — Génération recette depuis photo : `POST /recettes/generer-depuis-photo` (Pixtral)
- ✅ **CT-05** — Coaching hebdo Jules : `GET /famille/jules/coaching-hebdo` (JulesAIService)
- ✅ **QW-02** — Recette Surprise : `GET /recettes/surprise` filtrée saison/frigo

### Notifications + Admin (Sprint 5)
- ✅ **CT-01** — `ServiceEmail` via Resend (`notif_email.py`, 230L) — reset mdp, verify, résumé hebdo, alertes, invitations
- ✅ **CT-01** — `DispatcherNotifications` multi-canal (`notif_dispatcher.py`, 185L)
- ✅ **CT-02** — Admin enrichi backend (`admin.py`, 425L) — jobs, notif test, cache stats/purge, liste users
- ✅ **CT-02** — `ServiceAudit` (354L), export CSV, stats
- ✅ **2FA TOTP** — `ServiceDeuxFacteurs` (125L) — `/2fa/enable`, `/2fa/verify-setup`, `/2fa/disable`, `/2fa/status`
- ✅ **WhatsApp** — Webhook entrant Meta Cloud API (`webhooks_whatsapp.py`, 296L) — réponse IA via Mistral
- ✅ **RouteurIA** — `core/ai/router.py` (704L) — routage multi-fournisseur avec `_ClassifieurComplexite`
- ✅ **Cache Redis L2** — `caching/redis.py` opérationnel (complète L1+L3)

### Cron jobs (Sprint 6)
- ✅ **CT-04** — Job `resume_hebdo` (Lundi 07h30) — ntfy + email
- ✅ **CT-03** — Job `push_contextuel_soir` (18h00) — planning demain + météo
- ✅ **10 jobs APScheduler** actifs (était 6)

---

## Sprint 7 — SQL consolidation + Bugs résiduels + Tests + Doc
> **Priorité** : 🟠 IMPORTANT | À faire maintenant

### SQL — P-04 à P-07

#### P-04 — Supprimer table `liste_cours` (doublon) _(XS)_
**Bug** : B-10 — doublon `liste_cours` / `listes_courses` dans `sql/INIT_COMPLET.sql`
- Supprimer le bloc `CREATE TABLE liste_cours`
- Remplacer tout `INSERT INTO liste_cours` par `INSERT INTO listes_courses`
- Vérifier les FK qui référencent `liste_cours`

#### P-05 — Déplacer inline ALTER TABLE en tête _(S)_
**Problème** : SQL-05 — colonnes ajoutées en bas via `ALTER TABLE ... ADD COLUMN`
- Rechercher tous les `ALTER TABLE xxx ADD COLUMN` en bas de `sql/INIT_COMPLET.sql`
- Intégrer chaque colonne directement dans le `CREATE TABLE` correspondant
- Supprimer les blocs `ALTER TABLE` devenus inutiles

#### P-06 — Absorber `sql/migrations/001|002|003.sql` _(S)_
1. `001_routine_moment_journee.sql` → `moment_journee VARCHAR(20)` + `jour_semaine INTEGER` dans `CREATE TABLE routines`
2. `002_standardize_user_id_uuid.sql` → corriger `user_id VARCHAR → UUID` dans 5 tables
3. `003_add_cotes_historique.sql` → ajouter `CREATE TABLE jeux_cotes_historique` + RLS dans section Jeux
4. **Supprimer** `sql/migrations/001*.sql`, `002*.sql`, `003*.sql`

#### P-07 — Absorber `alembic/versions/` + archiver Alembic _(S)_
1. `a1b2c3d4e5f6_initial_baseline.py` — baseline vide → **supprimer directement**
2. `f7e8d9c0b1a2_famille_refonte_phase1.py` → intégrer dans INIT_COMPLET :
   - `heure_debut TIME` dans `activites_famille`
   - `derniere_completion DATE` dans `routines`
   - `pour_qui`, `a_revendre`, `prix_revente_estime`, `vendu_le` dans `achats_famille`
   - `user_id UUID` + 8 colonnes JSONB dans `preferences_utilisateurs`
3. `c8d1e2f3a4b5_anniversaire_checklists.py` → intégrer :
   - Tables `checklists_anniversaire` + `items_checklist_anniversaire` + 7 index
4. **Supprimer** les 3 fichiers `alembic/versions/`
5. **Archiver/supprimer** `alembic.ini` et `alembic/`

**Validation post-absorption** — vérifier dans INIT_COMPLET que :
- [ ] `routines` : `moment_journee`, `jour_semaine`, `derniere_completion` présents
- [ ] `activites_famille` : `heure_debut TIME` présent
- [ ] `achats_famille` : 4 colonnes présentes
- [ ] `preferences_utilisateurs` : `user_id UUID` + 8 colonnes JSONB présentes
- [ ] `jeux_cotes_historique` : table + 3 index + RLS présents
- [ ] `checklists_anniversaire` + `items_checklist_anniversaire` : 2 tables + 7 index présents

---

### Bugs hauts résiduels

#### B-06 — `url_source` absent du modèle ORM Recette _(S)_
- `src/core/models/recettes.py` → ajouter `url_source: Mapped[str | None]`
- `sql/INIT_COMPLET.sql` → ajouter la colonne dans `CREATE TABLE recettes`

#### B-07 — `verifier_saison` silencieusement ignoré _(S)_
- `src/services/core/cron/jobs.py` → remplacer `logger.debug()` par `logger.warning()` si `hasattr()` est False
- Ajouter une vérification visible au démarrage de l'application

#### B-08 — `RepasPlanning` modèle manquant _(S)_
- Identifier le test `skip` dans `tests/api/test_routes_dashboard_jeux.py`
- Créer le modèle `RepasPlanning` manquant ou corriger la référence

#### B-11 — Lien sidebar "Calendriers" → 404 _(S)_
- `frontend/src/composants/disposition/barre-laterale.tsx` → supprimer ou corriger le lien vers `/famille/calendriers`
- Vérifier tous les autres liens de navigation pointant vers des pages inexistantes

#### B-12 — `RetourRecette.est_favori` vs `feedback` _(S)_
- Aligner `frontend/src/types/recettes.ts` : utiliser `feedback: "like" | "neutral" | "dislike"` OU
- Ajouter un champ calculé `est_favori: bool` dans le schéma Pydantic `RecetteResponse`

---

### Tests manquants

#### CT-12 — Test cohérence schéma ORM ↔ SQL _(S)_
**Fichier à créer** : `tests/sql/test_schema_coherence.py`
```python
def test_chaque_orm_a_un_create_table():
    """Vérifie que chaque __tablename__ ORM correspond à un CREATE TABLE dans INIT_COMPLET.sql."""
    import re
    from pathlib import Path
    from src.core.models import Base

    sql_content = Path("sql/INIT_COMPLET.sql").read_text()
    sql_tables = set(re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)", sql_content))

    for mapper in Base.registry.mappers:
        table_name = mapper.class_.__tablename__
        assert table_name in sql_tables, f"Table ORM '{table_name}' absente de INIT_COMPLET.sql"
```

#### CT-13 — Tests push notifications _(M)_
**Fichier à créer** : `tests/api/test_push_notifications.py`
- `test_subscribe_persisted_in_db` — POST /push/subscribe insère en DB
- `test_subscribe_survives_restart` — abonnements rechargés depuis DB
- `test_vapid_public_key_endpoint` — GET /push/vapid-public-key retourne une clé
- `test_ntfy_digest_scheduled` — `digest_ntfy` dans APScheduler
- `test_rappel_courses_scheduled` — `rappel_courses` dans APScheduler
- `test_unsubscribe_sets_actif_false` — désabonnement logique

#### CT-14 — Tests routes admin + RGPD _(M)_
**Fichier à créer** : `tests/api/test_admin_routes.py`
- `test_lister_users_admin_only`
- `test_lister_jobs_admin_only`
- `test_executer_job_admin_only`
- `test_export_rgpd_data`
- `test_delete_account_rgpd`

#### CT-07 — Tests famille (achats + garde) _(M)_
- `tests/api/test_famille_achats.py` : CRUD + suggestions IA (mock Mistral) + scoring + Vinted
- `tests/api/test_famille_garde.py` : config zones + semaines fermeture + jours-sans-crèche

---

### Nettoyage documentation

#### CT-15 — Supprimer `STATUS_PHASES.md` _(S)_
- Supprimer `STATUS_PHASES.md` (1004 lignes redondantes avec ANALYSE_COMPLETE.md)
- Modifier `ROADMAP.md` : retirer la référence
- Modifier `docs/INDEX.md` : retirer le lien, ajouter ANALYSE_COMPLETE.md comme référence principale

#### CT-16 — Nettoyer `ROADMAP.md` _(M)_
- Supprimer l'historique des sprints déjà livrés
- Supprimer la section "Système de Phases A-AC"
- Aligner la table "Priorités 2 semaines" sur la section 13 de ANALYSE_COMPLETE.md

#### CT-17 — Nettoyage `docs/` _(S)_
- Supprimer `docs/JEUX_AMELIORATIONS_PLAN.md` (jeux 100% complet)
- Supprimer `docs/JEUX_PLAN_VALIDATION.md`
- Supprimer `docs/guides/batch_cooking.md` (fichier vide)
- Supprimer `docs/markdown-preview.md` (debug)
- Mettre à jour `docs/INDEX.md`

#### CT-11 — Mettre à jour doc SQL _(S)_
- `docs/MIGRATION_GUIDE.md` → retirer workflow SQL-file, documenter "INIT_COMPLET only"
- Archiver ou supprimer `sql/migrations/README.md` et `alembic/README.md`

#### CT-08 — Index SQL manquants _(S)_
**Ajouter dans `sql/INIT_COMPLET.sql`** :
```sql
CREATE INDEX IF NOT EXISTS idx_recette_ingredients_ingredient_id ON recette_ingredients(ingredient_id);
CREATE INDEX IF NOT EXISTS idx_repas_planning_id ON repas(planning_id);
CREATE INDEX IF NOT EXISTS idx_articles_courses_liste_id ON articles_courses(liste_id);
CREATE INDEX IF NOT EXISTS idx_historique_inventaire_article_id ON historique_inventaire(article_id);
CREATE INDEX IF NOT EXISTS idx_jalons_profil_id ON jalons(profil_enfant_id);
CREATE INDEX IF NOT EXISTS idx_paris_user_date ON jeux_paris_sportifs(user_id, date_pari);
```

#### CT-10 — Audit tables orphelines ORM ↔ SQL _(M)_
- Lister les `__tablename__` de `src/core/models/voyage.py` → vérifier présence dans INIT_COMPLET
- Vérifier `journal_bord`, `sessions_travail`, `log_statut_objets` — ont-ils un modèle ORM ?
- Pour orphelines SQL sans ORM : créer le modèle ou supprimer la table
- Pour modèles ORM sans SQL : ajouter CREATE TABLE ou supprimer le modèle

#### CT-02-FE — Page frontend Admin Jobs _(S)_
**Manque** : `frontend/src/app/(app)/admin/jobs/page.tsx` non créée (backend opérationnel)
- Table des jobs : ID, libellé, schedule, dernier run, statut (✅/❌)
- Bouton ▶ "Exécuter maintenant" par ligne → `POST /admin/jobs/{id}/run`
- Toast confirmation + feedback statut
- Onglets dans la page admin : Logs | Jobs | Notifications test | Cache | Utilisateurs

---

## Sprint 8 — Inter-modules + Dashboard avancé
> **Priorité** : ⭐⭐⭐ HAUTE VALEUR

### MT-01 — Cellier ↔ Inventaire cuisine _(M)_
**Endpoint à créer** : `GET /api/v1/inventaire/consolide`
- Merge `ArticleInventaire` (cuisine) + `ArticleCellier` (maison) avec champ `source: "cuisine" | "cellier"`
- Générer la liste de courses depuis la vue consolidée (évite les doublons)

### MT-03 — Score bien-être global (IA-09) _(M)_
**Score 0–100** : diversité alimentaire (40%) + Nutri-Score moyen (30%) + activités sportives (30%)
- `src/services/dashboard/score_bienetre.py` (nouveau)
- `GET /api/v1/dashboard/score-bienetre`
- Widget jauge circulaire sur le dashboard + trend semaine précédente

### MT-04 — Alertes météo contextuelles cross-modules _(M)_
**Endpoint** : `GET /api/v1/dashboard/alertes-contextuelles`
- Charger météo Open-Meteo 48h (déjà intégré dans `/outils/meteo`)
- Évaluer gel/canicule/vent/pluie/pollen
- Générer alertes cross-modules (jardin, cuisine, Jules, maison extérieur) selon le tableau de ANALYSE_COMPLETE.md section 7
- Widget "Alertes contextuelles" sur le dashboard (max 3 simultanées)

### MT-06 — Widgets dashboard configurables _(L)_
- `GET/PUT /api/v1/dashboard/config` — stocker config dans `preferences_utilisateurs.config_dashboard` (JSONB)
- Frontend : mode "Configurer le dashboard" + drag & drop (dnd-kit) + sauvegarde

### MT-08 — Timeline vie familiale _(M)_
**Endpoint** : `GET /api/v1/famille/timeline`
- Agréger : jalons Jules, événements familiaux, projets maison complétés, matchs mémorables
- Page `frontend/src/app/(app)/famille/timeline/page.tsx` — visualisation chronologique, filtrable, export PDF

### MT-09 — OCR photo-frigo → auto-sync inventaire _(S)_
- `frontend/src/app/(app)/cuisine/inventaire/page.tsx` → bouton "Tout ajouter à l'inventaire" sur résultat OCR
- `POST /api/v1/inventaire/bulk` (import en lot, à créer/vérifier)
- Checkboxes par article avant import

### QW-01 — Widget météo sur dashboard _(XS)_
- Réutiliser l'API Open-Meteo déjà intégrée dans `/outils/meteo`
- Widget compact (température, icône, prévision 3j) dans le dashboard

### QW-06 — "Aujourd'hui dans l'histoire de la famille" _(S)_
- `GET /api/v1/famille/aujourd-hui-historique?date=...` → jalons + événements du même jour les années précédentes
- Widget dashboard / section famille

---

## Sprint 9 — WhatsApp sortant + IA avancée
> **Priorité** : ⭐⭐ MOYEN

### MT-02 — WhatsApp sortant proactif _(M)_
**Manque** : le webhook entrant est fait, mais pas les messages préemptifs
- Compléter `notif_whatsapp.py` ou utiliser Meta Cloud API `POST /messages`
- Cas d'usage : rappels crèche, liste courses partagée, rapport hebdo WhatsApp
- Intégrer dans `DispatcherNotifications` (canal `"whatsapp"`)

### MT-07 — Assistant vocal (IA-01) _(L)_
- Frontend : bouton microphone flottant (accessible depuis toutes les pages)
- Web Speech API → transcription texte
- `POST /api/v1/assistant/commande-vocale` → Mistral extrait l'intention → dispatch API interne
- Intentions à gérer :
  - "Ajoute [article] à la liste de courses" → `POST /courses/{id}/articles`
  - "Jules pèse [X] kg" → `POST /famille/jules/croissance`
  - "Rappelle-moi [action] [quand]" → `POST /maison/routines`

### Jobs cron restants (J-03 à J-11)

| ID | Schedule | Description | Effort |
|----|----------|-------------|--------|
| J-03 | Dim 20h00 | Génération planning semaine si vide → ntfy | S |
| J-04 | 06h00 quotidien | Alertes péremptions produits J+48h | S |
| J-07 | 1er du mois | Rapport mensuel budget famille+maison+jeux | M |
| J-08 | Ven 17h00 | Score weekend : activités météo prévues + Jules | S |
| J-09 | 1er du mois | Contrôle garanties/contrats expirant dans 3 mois | XS |
| J-10 | Mer 20h00 | Rapport jardin : arrosage + semis prévus | S |
| J-11 | Dim 20h00 | Score bien-être hebdo + alerte si dérive | S |

### IA avancée restante

| ID | Feature | Endpoint | Effort |
|----|---------|----------|--------|
| IA-04 | Planificateur vacances IA | `POST /famille/voyage/planifier-ia` | M |
| IA-05 | Anomalies financières cross-modules | `GET /dashboard/anomalies-financieres` | M |
| IA-07 | Optimisation budget courses IA | `GET /courses/optimiser-budget-ia` | M |
| IA-08 | Diagnostic maison photo (Pixtral) | `POST /maison/diagnostics/ia-photo` | M |

---

## Sprint 10 — Innovations & Long terme

### LT-01 — Intégration Garmin santé/sport _(L)_
- ✅ Sync Garmin automatique matinale (cron `garmin_sync_matinal`, 06h00)
- ✅ Endpoint recommandations dîner selon calories brûlées : `GET /api/v1/garmin/recommandation-diner`
- ✅ Contribution Garmin au score bien-être (`activites_garmin`, `calories_actives_garmin`)

### LT-02 — Gamification sport + alimentation _(M)_
- ✅ Persistance des points hebdo : table `points_utilisateurs`
- ✅ Persistance des badges : table `badges_utilisateurs`
- ✅ Recalcul hebdomadaire des points (cron `points_famille_hebdo`, dimanche 20h00)
- ✅ Page frontend dédiée : `/famille/gamification`

### LT-03 — Mode Voyage avec checklists intelligentes _(M)_
- ✅ Checklists proportionnelles au nombre de participants (scaling quantités)
- ✅ Génération de courses depuis checklists : `POST /api/v1/famille/voyages/{id}/generer-courses`
- ✅ Événement `voyage.en_cours` émis pour alléger planning/arrosage

### LT-04 — Automations "Si → Alors" _(L)_
- ✅ Table `automations` en DB
- ✅ Moteur d'exécution (déclencheur `stock_bas`, actions `ajouter_courses`/`notifier`)
- ✅ Exécution périodique APScheduler (job `automations_runner`, toutes les 5 min)
- ✅ Endpoint manuel : `POST /api/v1/automations/{id}/executer-maintenant`

---

## Suivi d'avancement

### ✅ Sprints terminés

**Bugs critiques (Sprint 1)**
- [x] P-01 — Persistance push subscriptions en DB
- [x] P-02 — Endpoint VAPID public key
- [x] P-03 — Scheduler ntfy digest + rappel courses
- [x] B-05 — Accès fragile `_subscriptions` remplacé

**Features Jules + Cuisine (Sprint 4)**
- [x] CT-09 — Bouton Version Jules + profil aliments exclus
- [x] CT-06 — Génération recette depuis photo (Pixtral)
- [x] CT-05 — Coaching hebdo Jules
- [x] QW-02 — Recette Surprise

**Notifications + Admin + 2FA (Sprint 5)**
- [x] CT-01 — ServiceEmail (Resend) + DispatcherNotifications
- [x] CT-02 — Admin backend enrichi (jobs, cache, users, audit)
- [x] WhatsApp webhook entrant
- [x] 2FA TOTP complet
- [x] RouteurIA multi-fournisseur
- [x] Cache Redis L2

**Cron jobs (Sprint 6)**
- [x] CT-04 — Job résumé hebdo (Lundi 07h30)
- [x] CT-03 — Job push contextuel soir (18h00)

---

### 🔜 Sprint 7 (prochain)

**SQL consolidation**
- [x] P-04 — Supprimer table `liste_cours` (doublon B-10)
- [x] P-05 — Déplacer inline ALTER TABLE en tête de CREATE TABLE
- [x] P-06 — Absorber `sql/migrations/001|002|003.sql` dans INIT_COMPLET
- [x] P-07 — Absorber `alembic/versions/` + archiver Alembic (`alembic.ini.bak`)

**Bugs hauts résiduels**
- [x] B-06 — `url_source` absent du modèle ORM Recette
- [x] B-07 — `verifier_saison` silencieusement ignoré
- [x] B-08 — `RepasPlanning` modèle manquant (test skip)
- [x] B-11 — Lien sidebar "Calendriers" → 404
- [x] B-12 — `est_favori` vs `feedback` TypeScript

**Tests manquants**
- [x] CT-12 — Test cohérence schéma ORM ↔ SQL
- [x] CT-13 — Tests push notifications (B-01/B-02/B-03)
- [x] CT-14 — Tests routes admin + RGPD
- [x] CT-07 — Tests famille achats + garde

**Documentation**
- [x] CT-11 — Mettre à jour `docs/MIGRATION_GUIDE.md`
- [x] CT-15 — Supprimer `STATUS_PHASES.md`
- [x] CT-16 — Nettoyer `ROADMAP.md`
- [x] CT-17 — Nettoyage `docs/` (fichiers Jeux obsolètes + vides)

**SQL + Admin**
- [x] CT-08 — Index manquants SQL (`idx_recette_ingredients_ingredient_id`, `idx_repas_planning_id`)
- [x] CT-10 — Audit tables orphelines ORM ↔ SQL + test de non-régression
- [x] CT-02-FE — Page frontend Admin Jobs (`/admin/jobs`)

---

### 🔜 Sprint 8

- [x] MT-01 — Cellier ↔ Inventaire cuisine (endpoint `/inventaire/consolide` + client TS `listerInventaireConsolide`)
- [x] MT-03 — Score bien-être global (service + route + widget dashboard jauge)
- [x] MT-04 — Alertes météo contextuelles cross-modules (route + widget dashboard)
- [x] MT-06 — Widgets dashboard configurables (config GET/PUT + toggles + localStorage)
- [x] MT-08 — Timeline vie familiale (route `/famille/timeline` + page frontend filtrable)
- [x] MT-09 — OCR photo-frigo → checkboxes sélection avant import via `/inventaire/bulk`
- [x] QW-01 — Widget météo sur dashboard (wttr.in Open-Meteo)
- [x] QW-06 — "Aujourd'hui dans l'histoire de la famille" (route + widget dashboard)

### ✅ Sprint 9

- [x] MT-02 — WhatsApp sortant proactif
- [x] MT-07 — Assistant vocal (Web Speech API → Mistral → API)
- [x] J-03 — Job Dim 20h00 (planning semaine vide)
- [x] J-04 — Job 06h00 (alertes péremptions)
- [x] J-07 — Rapport mensuel budget
- [x] J-08 — Score weekend
- [x] J-09 — Contrôle garanties/contrats
- [x] J-10 — Rapport jardin
- [x] J-11 — Score bien-être hebdo
- [x] IA-04 — Planificateur vacances IA
- [x] IA-05 — Anomalies financières cross-modules
- [x] IA-07 — Optimisation budget courses IA
- [x] IA-08 — Diagnostic maison photo (Pixtral)

### ✅ Sprint 10 (MVP implémenté)

- [x] LT-01 — Intégration Garmin santé/sport
- [x] LT-02 — Gamification sport + alimentation
- [x] LT-03 — Mode Voyage avec checklists intelligentes
- [x] LT-04 — Automations "Si → Alors"

---

## Dépendances entre items

```
P-06 + P-07 (absorber migrations SQL) ──→ CT-12 (test cohérence ORM ↔ SQL)
B-06 (url_source ORM) ────────────────→ CT-13 (tests push recettes)
CT-02-FE (admin jobs UI) ─────────────→ dépend de CT-02 backend ✅
MT-01 (cellier ↔ inventaire) ─────────→ courses consolidées (Sprint 8)
MT-03 (score bien-être) ──────────────→ MT-06 (widget dashboard)
MT-04 (alertes météo) ────────────────→ QW-01 (widget météo dashboard)
J-11 (score bien-être hebdo) ─────────→ MT-03 (service score déjà là)
LT-01 (Garmin) ───────────────────────→ MT-03 (activités sport → score bien-être)
```

---

*Plan mis à jour le 28 mars 2026 — GitHub Copilot*
*Référence : `ANALYSE_COMPLETE.md` (état post-Sprint 5)*
