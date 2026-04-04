# EXPLAIN ANALYZE — Validation des index

> **Date**: 3 avril 2026
> **Objectif**: Valider que les 6 index ajoutés lors de la vague performance améliorent réellement les performances
> **Scope**: 10 requêtes critiques du parcours utilisateur
> **Prérequis**: Accès Supabase PostgreSQL + données réalistes (mini-seed ou copie d'export)

---

## 1. Vue d'ensemble

### Index ajoutés lors de la vague performance

| Index | Table | Colonne(s) | Type | Utilité |
|-------|-------|-----------|------|---------|
| `ix_garden_items_derniere_action` | `elements_jardin` | `derniere_action` | Single | Filtrer jardinage actif (< 30 jours) |
| `ix_furniture_date_achat` | `meubles` | `date_achat` | Single | Trier/filtrer meubles récents |
| `idx_objets_maison_date_achat` | `objets_maison` | `date_achat` | Single | Filtrer équipements par âge (garantie) |
| `ix_interventions_artisans_date` | `interventions_artisans` | `date_intervention` | Single | Timeline artisans |
| `ix_articles_cellier_date_achat` | `articles_cellier` | `date_achat` | Single | Rotation stock cellier (FIFO) |
| `ix_devis_date_validite` (partial) | `devis_comparatifs` | `date_validite WHERE IS NOT NULL` | Partial | Devis valides uniquement |

### Queries critiques à tester

Les 10 requêtes ci-dessous représentent les workflows les plus fréquents. Pour chaque query, l'index associé est noté.

---

## 2. Requêtes critique + EXPLAIN ANALYZE

### Query 1: Récupérer planning repas de la semaine (avec IA)

**Domaine**: Cuisine — Planning repas
**Utilisateur flow**: Page `/cuisine/planning` charge le planning hebdo + suggestions IA
**Index associé**: ❌ Pas d'index direct (JOIN sur recettes, articles_courses)
**Hypothèse**: Query côté métier (groupe ingredients, calcule nutrition)

```sql
EXPLAIN ANALYZE
SELECT r.id, r.nom, r.temps_preparation, r.debut_saison, r.fin_saison,
       COUNT(DISTINCT ar.id) as nb_ingredients,
       ROUND(AVG(ing.calories_pour_100g), 2) as calories_moyennes
    FROM recettes r
    LEFT JOIN articles_recettes ar ON r.id = ar.recette_id
    LEFT JOIN ingredients ing ON ar.ingredient_id = ing.id
    WHERE r.user_id = :user_id
      AND r.visibilite = 'prive'
    GROUP BY r.id, r.nom, r.temps_preparation, r.debut_saison, r.fin_saison
    ORDER BY r.date_creation DESC
    LIMIT 20;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Plan exécution : Seq Scan OK (petite table) OU Index Scan (user_id indexé ?)
- Est-ce que la jointure LEFT JOIN recalcule chaque fois, ou cache?
- Nombre de groupes vs. nombre de lignes (inflation memory?)
- Temps total < 50ms

---

### Query 2: Lister articles de courses pour une liste (temps réel WebSocket)

**Domaine**: Cuisine — Courses
**Utilisateur flow**: Page `/cuisine/courses` + collaboration WebSocket
**Index associé**: 📊 Pas d'index sur `listes_courses.id` (PK implicite), mais peut y avoir grouping lent
**Hypothèse**: Cette query s'exécute potentiellement 100× par heure (WebSocket updates)

```sql
EXPLAIN ANALYZE
SELECT ac.id, ac.nom, ac.quantite, ac.unite_volume, ac.categorie,
       ac.priorite, ac.acheteur_id, ac.checked,
       COUNT(*) OVER (WINDOW w AS (ORDER BY ac.priorite DESC, ac.date_creation)) as rang
    FROM articles_courses ac
    WHERE ac.liste_id = :liste_id
      AND ac.user_id = :user_id
      AND ac.checked = FALSE
    ORDER BY ac.priorite DESC, ac.date_creation DESC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Particularité WebSocket : même query x 100/h
- Plan : devrait être simple (liste_id idx OU seq scan si liste petite)
- Présence de WINDOW function : coût du calcul de rang?
- Temps total < 30ms

---

### Query 3: Rechercher recettes par nom / filtre (auto-complete frontend)

**Domaine**: Cuisine — Recettes
**Utilisateur flow**: Barre recherche "Tomate" → suggestions live (TanStack Query)
**Index associé**: ❌ Pas d'index TEXTE (mais ilike recherche)
**Opportunité**: Ajouter `ix_recettes_nom_gin` (GIN index) si perf dégradée

```sql
EXPLAIN ANALYZE
SELECT r.id, r.nom, r.duree_minutes, r.temps_preparation,
       (SELECT COUNT(*) FROM articles_recettes 
        WHERE recette_id = r.id) as nb_ingredientsvia
    FROM recettes r
    WHERE r.user_id = :user_id
      AND LOWER(r.nom) ILIKE LOWER(:'nom_search')
      AND r.visibilite = 'prive'
    ORDER BY r.date_creation DESC
    LIMIT 10;
```

**À vérifier dans EXPLAIN ANALYZE**:
- ILIKE sans index = Seq Scan probable (acceptable si < 1000 recettes)
- Subquery COUNT() : réexécutée pour cada ligne?
- Avec index GIN sur nom : Index Scan expected vs actual?
- Temps total < 50ms

---

### Query 4: Profil Jules — jalons + alimentation

**Domaine**: Famille — Jules
**Utilisateur flow**: Page `/famille/jules` charge le profil, les derniers jalons et le contexte repas
**Index associé**: 📊 `jalons(child_id, date_jalon)`
**Hypothèse**: flux centré sur le développement quotidien et l'alimentation, sans suivi anthropométrique

```sql
EXPLAIN ANALYZE
SELECT j.id,
       j.titre,
       j.categorie,
       j.date_jalon,
       j.description
  FROM jalons j
 WHERE j.child_id = :child_id
 ORDER BY j.date_jalon DESC
 LIMIT 30;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Index Scan sur `jalons.child_id` + tri par date
- LIMIT suffisant pour l'historique visible dans l'UI
- Temps total < 50ms acceptable

---

### Query 5: Dashboard — agrégations stats générales

**Domaine**: Core — Dashboard
**Utilisateur flow**: Page d'accueil `/` charge KPIs (4-5 agrégations)
**Index associé**: ❌ Pas d'index sur colonnes de grouping (mais peut utiliser user_id)
**Hypothèse**: Query BI lourde, exécutée 1× au load (acceptable < 500ms)

```sql
EXPLAIN ANALYZE
WITH budget_mois AS (
  SELECT EXTRACT(YEAR FROM date_depense) as annee,
         EXTRACT(MONTH FROM date_depense) as mois,
         SUM(montant) as total_depenses,
         COUNT(*) as nb_transactions
    FROM depenses_maison
    WHERE user_id = :user_id
      AND date_depense >= CURRENT_DATE - INTERVAL '3 months'
    GROUP BY annee, mois
)
SELECT * FROM budget_mois
ORDER BY annee DESC, mois DESC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Aggregate SUM() + COUNT() : plan optimal?
- Date filters : utilise-t-il index sur `date_depense`?
- CTE materialization vs inlining?
- Vol de données (3 mois = max 90-100 rows per user, acceptable)
- Temps total < 200ms

---

### Query 6: Jardin — éléments actifs (derniere_action < 30j)

**Domaine**: Maison — Jardin
**Utilisateur flow**: Page jardin affiche plantes actives + timeline
**Index associé**: ✅ `ix_garden_items_derniere_action` — NOUVELLEMENT AJOUTÉ
**Hypothèse**: Index utilisé directement pour filtrage rapide

```sql
EXPLAIN ANALYZE
SELECT ej.id, ej.nom, ej.type_plante, ej.emplacement, ej.derniere_action,
       EXTRACT(DAY FROM CURRENT_DATE - ej.derniere_action::date) as jours_inactivite,
       COUNT(rj.id) as nb_actions_recent
    FROM elements_jardin ej
    LEFT JOIN recoltes rj 
      ON ej.id = rj.plante_id
      AND rj.date_recolte >= CURRENT_DATE - INTERVAL '30 days'
    WHERE ej.user_id = :user_id
      AND ej.derniere_action >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY ej.id
    ORDER BY ej.derniere_action DESC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- **Index scan attendu** : `Index Scan using ix_garden_items_derniere_action` doit apparaître
- Plan sans index (hypothétique) : Seq Scan → ordre de grandeur plus lent
- LEFT JOIN recoltes : dénormaliser ou via ref intégrité?
- Temps total < 50ms (CRITÈRE: index working)

---

### Query 7: Maison — Projets actifs (Kanban)

**Domaine**: Maison — Projets
**Utilisateur flow**: Page Kanban `/maison/projets` groupe par statut
**Index associé**: ❌ Éventuel index sur `statut` (enum: 'à_faire', 'en_cours', 'complété')
**Hypothèse**: Petite table, GROUP BY statut probablement acceptable

```sql
EXPLAIN ANALYZE
SELECT p.statut,
       COUNT(*) as nb_projets,
       ROUND(AVG(EXTRACT(DAY FROM CURRENT_DATE - p.date_debut))::numeric, 1) as duree_moyenne_jours
    FROM projets p
    WHERE p.user_id = :user_id
      AND p.statut != 'complété'
    GROUP BY p.statut
    ORDER BY CASE 
             WHEN p.statut = 'à_faire' THEN 1
             WHEN p.statut = 'en_cours' THEN 2
             ELSE 3
            END;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Seq Scan acceptable si < 500 projets/user (typical: 20-50)
- GROUP BY statut : utilise Hash Aggregate OU Sort + Group Aggregate?
- Temps total < 30ms

---

### Query 8: Documents — alertes expiration

**Domaine**: Famille — Documents
**Utilisateur flow**: Dashboard affiche docs expirant dans 30j (notification warning)
**Index associé**: ❌ Pas d'index `date_expiration` (mais probablement devrait y en avoir)
**Opportunité**: Ajouter `ix_documents_date_expiration` si query lente

```sql
EXPLAIN ANALYZE
SELECT d.id, d.nom, d.type_document, d.date_expiration,
       EXTRACT(DAY FROM d.date_expiration - CURRENT_DATE) as jours_avant_expiration
    FROM documents d
    WHERE d.user_id = :user_id
      AND d.date_expiration IS NOT NULL
      AND d.date_expiration <= CURRENT_DATE + INTERVAL '30 days'
      AND d.date_expiration > CURRENT_DATE
    ORDER BY d.date_expiration ASC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Sans index : Seq Scan sur 200-500 docs (déja lent?)
- Avec index : Index Scan + Filter (plus rapide)
- Temps attendu < 50ms
- **Recommandation**: Ajouter index si Seq Scan > 40ms

---

### Query 9: Budget — dépenses par catégorie (drilling)

**Domaine**: Famille — Budget
**Utilisateur flow**: Page budget [`/famille/budget`] affiche graphique dépenses par catégorie mois-en-cours
**Index associé**: 📊 Pas d'index direct (mais JOIN sur categories possible)
**Hypothèse**: 50-200 dépenses/mois = acceptable Seq Scan

```sql
EXPLAIN ANALYZE
SELECT COALESCE(d.categorie, 'Non classé') as categorie,
       COUNT(*) as nb_depenses,
       SUM(d.montant) as total,
       ROUND(AVG(d.montant)::numeric, 2) as moyenne,
       ROUND((SUM(d.montant) * 100.0 / SUM(SUM(d.montant)) OVER ())::numeric, 1) as pct_total
    FROM depenses_maison d
    WHERE d.user_id = :user_id
      AND EXTRACT(YEAR FROM d.date_depense) = EXTRACT(YEAR FROM CURRENT_DATE)
      AND EXTRACT(MONTH FROM d.date_depense) = EXTRACT(MONTH FROM CURRENT_DATE)
    GROUP BY d.categorie
    ORDER BY total DESC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- WINDOW function SUM() OVER : coût en mémoire?
- COALESCE pour NULL categories : pédure bien?
- Temps total < 100ms

---

### Query 10: Activités — agenda familial (próximo week)

**Domaine**: Famille — Activités
**Utilisateur flow**: Dashboard `/famille/agenda` affiche events de la semaine prochaine
**Index associé**: ❌ Éventuel index sur `date_activite` (mais petit dataset)
**Hypothèse**: < 50 activités/semaine per famille, Seq Scan acceptable

```sql
EXPLAIN ANALYZE
SELECT a.id, a.nom, a.date_activite, a.heure_debut, a.responsable,
       a.lieu, a.statut,
       (SELECT COUNT(*) FROM participants_activite pa WHERE pa.activite_id = a.id) as nb_participants
    FROM activites a
    WHERE a.user_id = :user_id
      AND a.date_activite >= CURRENT_DATE
      AND a.date_activite < CURRENT_DATE + INTERVAL '7 days'
    ORDER BY a.date_activite ASC, a.heure_debut ASC;
```

**À vérifier dans EXPLAIN ANALYZE**:
- Subquery COUNT() : réexecutée x10+ fois? (inefficace)
- Alternative : denormaliser nb_participants ou LEFT JOIN Aggregation?
- Temps total < 50ms

---

## 3. Checklist de validation

### Avant exécution des EXPLAIN ANALYZE

- [ ] Accès Supabase Dashboard récupéré + authentification OK
- [ ] Database connectée avec données réalistes (mini-seed ou copie export)
- [ ] 6 indexes vérifiés présents dans PostgreSQL (`\di sql_schema`)
- [ ] Les query modifications mineures OK (ex: `:user_id` → UUID hard-coded pour test)

### Exécution (pour chaque query)

- [ ] Query exécutée avec `EXPLAIN ANALYZE` (full run + actual rows)
- [ ] Plan exécution capturé (JSON ou texte)
- [ ] Index utilisés validés (Index Scan présent où attendu ?)
- [ ] Temps réel noté (`Execution Time: X ms`)
- [ ] Seq Scan inattendu? Documenté pour optimisation future

### Validation post-exécution

- [ ] 10/10 queries exécutées sans erreur
- [ ] Aucune query > 500ms (sauf dashboard BI qui peut atteindre 300ms)
- [ ] **Index success rate** : 6 indexes utilisés dans 6-8 queries au minimum
- [ ] Aucun "Index Scan Backward" inutile
- [ ] Memory > 10MB? Documenté (query pathologique)
- [ ] Résultats cohérents avec business logic (colonnes présentes, calculs okay)

### Rapport final

- [ ] JSON/text des 10 EXPLAIN ANALYZE plans aggregés en `.sql` file
- [ ] Tableau récapitulatif : Query | Index Used | Execution Time | Recommendation
- [ ] Indexes utilisés avec succès : ✅ Valider en PLANNING_IMPLEMENTATION.md
- [ ] Index non utilisés : documenter pour la prochaine passe d'optimisation (peut être droppé ou réanalysé)
- [ ] Opportunities d'optimisation notées (ex: GIN index recettes nom si ILIKE lent)

---

## 4. Résultats attendus

### Scénarios optimistes (✅ objectifs de validation)

| Index | Query | Résultat attendu |
|-------|-------|------------------|
| `ix_garden_items_derniere_action` | Query 6 | **Index Scan** apparaît → Perf +40% vs Seq Scan |
| `ix_furniture_date_achat` | Query 7 (variant équipements) | **Index Scan** pour filtrer meubles récents |
| `idx_objets_maison_date_achat` | Query 8 (variant) | **Index Scan** pour garantie checks |
| `ix_interventions_artisans_date` | Variante timeline | **Index Scan** pour chronologie artisans |
| `ix_articles_cellier_date_achat` | FIFO inventory | **Index Scan** pour rotation stock |
| `ix_devis_date_validite` (partial) | Query dévis valides | **Index Scan** avec partial filter appliqué |

### Scénarios réalistes (⚠️ possible)

- Query 2 (courses) : Seq Scan si liste petite (< 50 articles) — OK
- Query 5 (dashboard) : Seq Scan sur depenses_maison si < 10000 rows total — OK
- Query 10 (activités) : Seq Scan acceptable, considérer LEFT JOIN Aggregation vs subquery COUNT()

### Blockers (❌ à résoudre)

- Aucun index utilisé dans queries 6/7/8 → Indexing strategy à revoir
- Query > 500ms en production (sauf BI) → Causes: missing index, bad JOIN, subquery explosion
- Memory > 50MB → Query pathologique (mauvaise cardinalité)

---

## 5. Suivi et documentation

### Stockage des résultats

Placer les fichiers EXPLAIN ANALYZE dans : `data/performance_queries/`

```
data/performance_queries/
├── 01_planning_repas.json
├── 02_articles_courses.json
├── 03_recherche_recettes.json
├── 04_jules_jalons_alimentation.json
├── 05_dashboard_stats.json
├── 06_jardin_actif.json
├── 07_projets_kanban.json
├── 08_documents_expiration.json
├── 09_budget_categories.json
├── 10_activites_agenda.json
└── RESULTATS_SYNTHESE.md
```

### Mise à jour PLANNING_IMPLEMENTATION.md

Après validation :
```markdown
## 2.2 Validation indexes
- [ ] `EXPLAIN ANALYZE` sur 10 queries critiques exécuté
- [x] **6/6 indexes utilisés avec succès** (après validation)
- [x] Aucune query > 300ms (sauf BI dashboard)
- [ ] Résultats documentés dans `data/performance_queries/`
```

---

## 6. Notes techniques

### Commandes PostgreSQL utiles

```sql
-- Lister tous les indexes
\di sql_schema

-- Afficher stats index (utilisation et taille)
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
  FROM pg_stat_user_indexes
  ORDER BY idx_scan DESC;

-- Vérifier index existence
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('elements_jardin', 'meubles', 'objets_maison', 
                    'interventions_artisans', 'articles_cellier', 'devis_comparatifs');

-- Benchmark before/after (activer/désactiver index)
-- ⚠️ ATTENTION : Nécessite role superuser
-- ALTER INDEX ix_garden_items_derniere_action UNUSABLE;  -- Désactiver
-- ANALYZE; -- Re-stat
-- EXPLAIN ANALYZE SELECT ...;
-- ALTER INDEX ix_garden_items_derniere_action REBUILD;  -- Réactiver
```

### Interprétation EXPLAIN ANALYZE

```
Seq Scan on elements_jardin ej  (cost=0.00..1250.00 rows=450 width=64)
  Filter: ((user_id = '123e4567...'::uuid) AND 
           (derniere_action >= (CURRENT_DATE - '30 days'::interval)))
  Rows: 25 (actual 100.000 ms)

↓ optimale

Index Scan using ix_garden_items_derniere_action on elements_jardin ej
  Index Cond: (derniere_action >= (CURRENT_DATE - '30 days'::interval))
  Filter: (user_id = '123e4567...'::uuid)
  Rows: 25 (actual 8.000 ms)
  →  Gain: 92% (100ms → 8ms)
```

---

**Mis à jour** : 3 avril 2026
**Prochaine étape** : Exécution sur Supabase cible (en attente du planificateur/utilisateur)
