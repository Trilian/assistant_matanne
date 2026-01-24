# 🚀 Guide Déploiement Module Famille - Supabase

## 📋 Checklist rapide

- [ ] Lire ce guide complètement
- [ ] Générer la migration SQL
- [ ] Vérifier les modèles localement
- [ ] Exécuter la migration sur Supabase
- [ ] Tester l'app
- [ ] Valider les données

---

## 1️⃣ Avant de commencer

### Prérequis
- Compte Supabase actif
- Accès à Supabase Dashboard
- Connexion SQL Editor
- Données Jules existantes en base (ChildProfile)

### Fichiers à utiliser
```
📄 sql/001_add_famille_models.sql  ← MAIN (exécuter sur Supabase)
🐍 scripts/migration_famille.py     ← INFO (génère le SQL)
📊 tests/test_famille.py            ← TEST (valider localement)
```

---

## 2️⃣ Générer la migration SQL

### Option A: Automatique
```bash
cd /workspaces/assistant_matanne

# Générer et afficher la migration
python3 scripts/migration_famille.py

# Vérifier les imports
python3 -c "from src.modules.famille import *; print('✅ OK')"
```

### Option B: Manuel
Consulter directement: `sql/001_add_famille_models.sql`

---

## 3️⃣ Exécuter sur Supabase

### Étape 1: Ouvrir SQL Editor
1. Aller à https://supabase.com/dashboard
2. Sélectionner votre projet
3. Aller dans **SQL Editor** (menu gauche)
4. Cliquer **New Query**

### Étape 2: Copier le SQL
Copier **tout** le contenu de:
```
sql/001_add_famille_models.sql
```

### Étape 3: Exécuter
1. Coller le SQL dans l'éditeur
2. Cliquer **Run** (ou Ctrl+Enter)
3. Attendre la confirmation

### Résultat attendu
```
✅ CREATE TABLE milestones
✅ CREATE TABLE family_activities
✅ CREATE TABLE health_routines
✅ CREATE TABLE health_objectives
✅ CREATE TABLE health_entries
✅ CREATE TABLE family_budgets
✅ CREATE VIEW v_family_budget_monthly
✅ CREATE VIEW v_family_activities_week
✅ CREATE VIEW v_health_routines_active
✅ CREATE VIEW v_health_objectives_active
✅ INSERT INTO milestones (1 row)
```

---

## 4️⃣ Vérifier les tables

### Dans Supabase Dashboard

1. **Aller dans Database → Tables**
2. Vérifier les 6 tables existent:
   - [ ] milestones
   - [ ] family_activities
   - [ ] health_routines
   - [ ] health_objectives
   - [ ] health_entries
   - [ ] family_budgets

3. **Vérifier les colonnes** (exemple pour milestones):
   - [ ] id (BIGSERIAL)
   - [ ] child_id (FK)
   - [ ] titre (VARCHAR)
   - [ ] categorie (VARCHAR)
   - [ ] date_atteint (DATE)
   - [ ] photo_url (VARCHAR)
   - [ ] notes (TEXT)
   - [ ] cree_le (TIMESTAMP)

4. **Vérifier les indices** (Database → Tables → milestones → Indexes):
   - [ ] idx_milestones_child_id
   - [ ] idx_milestones_date_atteint
   - [ ] idx_milestones_categorie

---

## 5️⃣ Tester localement

### Tests unitaires
```bash
cd /workspaces/assistant_matanne

# Lancer les tests
pytest tests/test_famille.py -v

# Voir le résumé
pytest tests/test_famille.py --tb=short -q
```

**Résultat attendu:**
```
tests/test_famille.py::TestMilestones::test_create_milestone PASSED
tests/test_famille.py::TestMilestones::test_milestone_with_photo PASSED
tests/test_famille.py::TestMilestones::test_get_milestones_by_category PASSED
tests/test_famille.py::TestFamilyActivities::test_create_activity PASSED
tests/test_famille.py::TestFamilyActivities::test_mark_activity_complete PASSED
tests/test_famille.py::TestFamilyActivities::test_activity_budget PASSED
tests/test_famille.py::TestHealthRoutines::test_create_routine PASSED
tests/test_famille.py::TestHealthRoutines::test_routine_with_entries PASSED
tests/test_famille.py::TestHealthObjectives::test_create_objective PASSED
tests/test_famille.py::TestHealthObjectives::test_objective_progression PASSED
tests/test_famille.py::TestFamilyBudget::test_create_budget_entry PASSED
tests/test_famille.py::TestFamilyBudget::test_budget_by_category PASSED
tests/test_famille.py::TestFamilyBudget::test_budget_monthly PASSED
tests/test_famille.py::TestIntegration::test_full_week_scenario PASSED

======================== 14 passed in 0.23s ========================
```

### Tests de l'app
```bash
# Lancer l'app
streamlit run src/app.py

# Dans le navigateur:
# - Aller dans 👨‍👩‍👧‍👦 Famille
# - Cliquer 🏠 Hub Famille
# - Tester chaque section
```

---

## 6️⃣ Troubleshooting

### Erreur: "relation milestones does not exist"
**Cause:** Migration non exécutée sur Supabase
**Solution:** 
1. Vérifier que le SQL a été exécuté avec succès
2. Rafraîchir: Database → Tables → Refresh
3. Réexécuter si nécessaire

### Erreur: "Foreign key constraint failed"
**Cause:** child_id inexistant dans child_profiles
**Solution:**
1. Vérifier que Jules existe: `SELECT * FROM child_profiles WHERE name = 'Jules'`
2. Créer Jules si absent:
```sql
INSERT INTO child_profiles (name, date_of_birth, gender, notes, actif, cree_le)
VALUES ('Jules', '2024-06-22', 'M', 'Notre petit Jules', TRUE, NOW());
```

### Erreur: "integer out of range"
**Cause:** Valeur invalide (ex: note_energie > 10)
**Solution:** Vérifier les contraintes CHECK:
```sql
SELECT * FROM family_budgets WHERE montant <= 0;  -- Devrait être vide
SELECT * FROM health_entries WHERE note_energie > 10 OR note_energie < 1;  -- Vide
```

### Erreur: "Streamlit can't find the app.py"
**Cause:** Chemins incorrects
**Solution:**
```bash
cd /workspaces/assistant_matanne
streamlit run src/app.py
```

---

## 7️⃣ Validation finale

### Checklist avant production
- [ ] Toutes les 6 tables existent
- [ ] Les 4 views existent
- [ ] Les indices sont créés
- [ ] Les contraintes sont actives
- [ ] Tests unitaires passent
- [ ] Tests Streamlit OK
- [ ] Données Jules dans la base
- [ ] Connexion Supabase confirmée

### Données de test
```sql
-- Vérifier Jules existe
SELECT * FROM child_profiles WHERE name = 'Jules';
-- Devrait retourner 1 ligne

-- Vérifier jalon exemple
SELECT * FROM milestones WHERE child_id = (SELECT id FROM child_profiles WHERE name = 'Jules');
-- Devrait avoir au moins 1 jalon
```

---

## 8️⃣ Après le déploiement

### Utilisation
```bash
# Lancer l'app
streamlit run src/app.py

# Naviguer vers:
# 👨‍👩‍👧‍👦 Famille → 🏠 Hub Famille
```

### Sections disponibles
1. **👶 Jules (19 mois)**
   - Ajouter jalons
   - Voir activités recommandées
   - Liste d'achats

2. **💪 Santé & Sport**
   - Créer routines
   - Fixer objectifs
   - Suivre séances

3. **🎨 Activités Famille**
   - Planifier sorties
   - Idées d'activités
   - Budget

4. **🛍️ Shopping**
   - Liste centralisée
   - Idées d'achats
   - Suivi budget

### Premiers pas
1. Ajouter une routine sport
2. Planifier une activité
3. Ajouter un jalon Jules
4. Créer une entrée budget
5. Voir le suivi

---

## 📞 Aide

### Logs Supabase
Si erreur d'exécution, vérifier les logs:
1. Supabase Dashboard → Database → Logs
2. Chercher les erreurs récentes
3. Copier le message d'erreur

### Support communauté
- Supabase Discord: https://discord.supabase.io
- Issues GitHub: https://github.com/supabase/supabase/issues

### Documentation
- Supabase SQL: https://supabase.com/docs/guides/sql
- SQLAlchemy: https://docs.sqlalchemy.org/
- Streamlit: https://docs.streamlit.io/

---

## ✅ Déploiement réussi!

Une fois complété, vous avez:
- ✅ 6 nouvelles tables en Supabase
- ✅ 4 views pour requêtes rapides
- ✅ Module Famille fully fonctionnel
- ✅ Interface Streamlit complète
- ✅ Tests unitaires passants
- ✅ Documentation à jour

**Durée estimée:** 15-20 minutes

**Prochaines étapes:** Utiliser le module pour tracker Jules, santé et activités! 🎉

---

*Guide v1.0 - 24 janvier 2026*
