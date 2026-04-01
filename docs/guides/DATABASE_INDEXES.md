# Guide â€” Audit des Index de Base de DonnÃ©es

> **Mise Ã  jour** : Sprint H (Avril 2026)  
> **Scope** : PostgreSQL (Supabase) â€” 143 tables, ~80+ index existants  
> **Objectif** : Documenter l'Ã©tat des index, identifier les lacunes, recommander les ajouts prioritaires

---

## Ã‰tat actuel â€” Index existants par domaine

### Cuisine

| Table | Colonnes indexÃ©es | Type |
| ------- | ------------------- | ------ |
| `recettes` | `nom`, `type_repas`, `saison`, `categorie`, `est_rapide`, `est_vegetarien`, `compatible_bebe`, `compatible_batch`, `est_bio`, `est_local`, `compatible_cookeo`, `compatible_airfryer`, `compatible_monsieur_cuisine` | Simples |
| `plannings` | `semaine_debut`, `(actif, semaine_debut)` | Simple + ComposÃ© |
| `repas` | `(planning_id, date_repas)`, `(planning_id, type_repas)` | ComposÃ©s |
| `listes_courses` | `semaine_du`, `statut`, `(statut, semaine_du)` | Simples + ComposÃ© |
| `articles_courses` | `(liste_id, achete)`, `(liste_id, priorite)` | ComposÃ©s |
| `inventaire` | `(date_peremption, quantite)` WHERE NOT NULL | Partiel |
| `historique_inventaire` | `(ingredient_id, date_modification)` | ComposÃ© |
| `recette_ingredients` | `recette_id`, `ingredient_id` | Simples |
| `ingredients` | `categorie`, `saison` | Simples |
| `modeles_courses` | `nom`, `utilisateur_id`, `actif` | Simples |

### Jeux

| Table | Colonnes indexÃ©es | Type |
| ------- | ------------------- | ------ |
| `jeux_paris_sportifs` | `match_id`, `statut`, `cree_le`, `(match_id, cree_le)` | Simples + ComposÃ© |
| `jeux_bankroll_historique` | `(user_id, date DESC)` | ComposÃ© |
| `jeux_series` | `(type_jeu, championnat)`, `(type_jeu, marche)`, `(frequence * serie_actuelle)` | ComposÃ©s + Expression |
| `jeux_alertes` | `notifie`, `(resultat_verifie, resultat_correct)` | Simples + ComposÃ© |
| `jeux_tirages_loto` | `date_tirage DESC` | Simple |
| `jeux_tirages_euromillions` | `date_tirage DESC` | Simple |
| `jeux_grilles_euromillions` | `tirage_id`, `cree_le DESC` | Simples |
| `jeux_cotes_historique` | `match_id`, `timestamp_cote DESC`, `bookmaker` | Simples |

### SystÃ¨me

| Table | Colonnes indexÃ©es | Type |
| ------- | ------------------- | ------ |
| `historique_actions` | `user_id`, `action_type`, `cree_le DESC`, `(entity_type, entity_id)`, `(user_id, created_at)` | Simples + ComposÃ©s |
| `logs_securite` | `user_id`, `event_type`, `created_at`, `(event_type, created_at)`, `(user_id, created_at)` | Simples + ComposÃ©s |
| `evenements_planning` | `date_debut`, `type_event`, `(date_debut, type_event)`, `(date_debut, date_fin)` | Simples + ComposÃ©s |
| `etats_persistants` | `namespace`, `user_id` | Simples |
| `sauvegardes` | `user_id`, `cree_le` | Simples |
| `openfoodfacts_cache` | `code_barres` | Simple |
| `automations` | `user_id`, `active` | Simples |

---

## Lacunes identifiÃ©es â€” Index manquants recommandÃ©s

### PrioritÃ© HAUTE (requÃªtes frÃ©quentes sans index)

#### 1. `jeux_paris_sportifs(user_id)` â€” âš ï¸ MANQUANT

```sql
-- Toutes les routes GET /jeux/paris filtrent par user_id
CREATE INDEX IF NOT EXISTS ix_jeux_paris_user_id ON jeux_paris_sportifs(user_id);

-- Ou mieux, composÃ© pour les queries typiques (user + statut + date)
CREATE INDEX IF NOT EXISTS ix_jeux_paris_user_statut ON jeux_paris_sportifs(user_id, statut);
CREATE INDEX IF NOT EXISTS ix_jeux_paris_user_date ON jeux_paris_sportifs(user_id, cree_le DESC);
```

#### 2. `jeux_grilles_loto(user_id)`, `jeux_grilles_euromillions(user_id)` â€” âš ï¸ MANQUANT

```sql
CREATE INDEX IF NOT EXISTS ix_jeux_grilles_loto_user ON jeux_grilles_loto(user_id);
CREATE INDEX IF NOT EXISTS ix_jeux_grilles_euromillions_user ON jeux_grilles_euromillions(user_id);
```

#### 3. `projets_maison(user_id, statut)` â€” probable lacune

```sql
-- GET /maison/projets filtre par user_id + statut
CREATE INDEX IF NOT EXISTS ix_projets_maison_user_statut ON projets_maison(user_id, statut);
```

#### 4. `taches_maison(user_id, statut, priorite)` â€” probable lacune

```sql
CREATE INDEX IF NOT EXISTS ix_taches_maison_user_statut ON taches_maison(user_id, statut);
CREATE INDEX IF NOT EXISTS ix_taches_maison_user_priorite ON taches_maison(user_id, priorite);
```

#### 5. `activites_famille(user_id, date_debut)` â€” probable lacune

```sql
-- Toutes les requÃªtes planning famille filtrent par user + date
CREATE INDEX IF NOT EXISTS ix_activites_famille_user_date ON activites_famille(user_id, date_debut);
```

### PrioritÃ© MOYENNE

#### 6. Index partiels pour statuts frÃ©quents

```sql
-- Paris en attente uniquement â€” beaucoup plus petit que l'index complet
CREATE INDEX IF NOT EXISTS ix_jeux_paris_en_attente 
    ON jeux_paris_sportifs(user_id, cree_le DESC) 
    WHERE statut = 'en_attente';

-- Projets actifs uniquement
CREATE INDEX IF NOT EXISTS ix_projets_maison_actifs
    ON projets_maison(user_id, date_debut_prevue)
    WHERE statut NOT IN ('termine', 'abandonne');
```

#### 7. JSONB indexes pour colonnes mÃ©tadonnÃ©es

```sql
-- Si des colonnes JSONB comme `metadata` ou `details` sont frÃ©quemment requÃªtÃ©es
CREATE INDEX IF NOT EXISTS ix_recettes_metadata ON recettes USING GIN (metadata)
    WHERE metadata IS NOT NULL;
```

### PrioritÃ© BASSE (analytics, rarement exÃ©cutÃ©es)

```sql
-- RÃ©sumÃ© mensuel jeux : agrÃ©gations par mois
CREATE INDEX IF NOT EXISTS ix_jeux_paris_mois 
    ON jeux_paris_sportifs(user_id, date_trunc('month', cree_le));

-- Inventaire proches pÃ©remption (optimisation de la requÃªte anti-gaspillage)
CREATE INDEX IF NOT EXISTS ix_inventaire_peremption_proche
    ON inventaire(date_peremption ASC)
    WHERE date_peremption IS NOT NULL AND quantite > 0;
```

---

## ProcÃ©dure d'audit complet (EXPLAIN ANALYZE)

Pour valider les recommandations ci-dessus sur la DB de prod (Supabase), exÃ©cuter :

```sql
-- Activer le log des slow queries (>100ms)
ALTER SYSTEM SET log_min_duration_statement = 100;

-- Identifier les requÃªtes frÃ©quentes sans index
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN (
    'jeux_paris_sportifs', 'projets_maison', 'taches_maison', 
    'activites_famille', 'recettes', 'listes_courses'
)
ORDER BY tablename, n_distinct;

-- Identifier les seq scans sur tables volumineuses
SELECT relname, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables
ORDER BY seq_scan DESC
LIMIT 20;

-- Analyser une requÃªte spÃ©cifique
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM jeux_paris_sportifs 
WHERE user_id = 'uuid-here' AND statut = 'en_attente'
ORDER BY cree_le DESC
LIMIT 20;
```

---

## RÃ¨gles gÃ©nÃ©rales pour les nouveaux index

| RÃ¨gle | Justification |
| ------- | -------------- |
| Toujours indexer `user_id` sur les tables multi-utilisateurs | Filtre universel dans toutes les routes |
| Index composÃ© `(user_id, statut)` sur les tables avec workflow | Ã‰vite un seq scan sur des tables volumineuses |
| Colonnes de date en DESC sur les tables d'historique | ORDER BY date DESC est le cas d'usage 99% du temps |
| Ã‰viter d'indexer les colonnes boolÃ©ennes seules | Faible cardinalitÃ© â†’ peu utile, sauf en composÃ© |
| PrÃ©fÃ©rer les index partiels pour les statuts actifs | Plus petits â†’ plus rapides sur disque |
| Index GIN pour colonnes ARRAY et JSONB | PostgreSQL utilise B-tree par dÃ©faut (inefficace pour JSONB) |

---

## Ajouter un index

1. Ã‰diter `sql/schema/14_indexes.sql`
2. Utiliser la convention de nommage : `ix_{table}_{colonnes}` ou `idx_{table}_{colonnes}`
3. Toujours utiliser `CREATE INDEX IF NOT EXISTS`
4. RegÃ©nÃ©rer INIT_COMPLET.sql : `python scripts/db/regenerate_init.py`
5. Appliquer sur la DB de prod : copier la ligne CREATE INDEX et exÃ©cuter via Supabase SQL Editor
6. Logger dans `sql/migrations/` si c'est un changement incrÃ©mental

---

## RÃ©fÃ©rence â€” Tous les index (gÃ©nÃ©rÃ©s depuis sql/schema/)

Pour obtenir la liste complÃ¨te Ã  jour :

```bash
# Lister tous les index dÃ©finis dans le schÃ©ma
Select-String -Path "sql/schema/*.sql" -Pattern "CREATE INDEX" | ForEach-Object { $_.Line.Trim() }
```

```sql
-- Sur la DB PostgreSQL â€” index effectivement crÃ©Ã©s
SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```
