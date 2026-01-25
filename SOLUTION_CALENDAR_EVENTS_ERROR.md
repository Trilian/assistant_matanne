# 🔴 Erreur relation "calendar_events" does not exist - SOLUTION

## 🎯 Problème

L'application tente d'accéder à la table `calendar_events`, mais elle n'existe pas en base de données.

```
ErreurBaseDeDonnees: (psycopg2.errors.UndefinedTable) relation "calendar_events" does not exist
```

## 🔍 Cause racine

1. **Configuration BD manquante** ← C'EST LE PROBLÈME PRINCIPAL
   - Le fichier `.env.local` ne contient pas `DATABASE_URL`
   - L'application ne peut pas créer les tables automatiquement

2. **Tables jamais créées** (conséquence)
   - `calendar_events` n'existe pas
   - `projects` n'existe pas
   - `routines` n'existe pas
   - ... et 21 autres tables

---

## ✅ Solution en 3 étapes

### 1️⃣ Configurer Supabase dans `.env.local`

**Fichier créé :** `.env.local` à la racine du projet

Remplissez cette ligne :
```env
DATABASE_URL=postgresql://postgres.abc123:mypassword@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
```

**Comment obtenir cette URL ?**
→ Consultez [CONFIG_SUPABASE_RAPIDE.md](CONFIG_SUPABASE_RAPIDE.md)

### 2️⃣ Créer les tables

```bash
python scripts/create_maison_tables.py
```

Attendez le message :
```
✨ SUCCÈS! Toutes les tables sont créées.
```

### 3️⃣ Relancer l'application

```bash
streamlit run src/app.py
```

L'erreur `relation "calendar_events" does not exist` **doit disparaître** ! 🎉

---

## 📊 Tableau des tables créées

Le script crée ces 24 tables :

| # | Module | Tables |
|---|--------|--------|
| 1-5 | 🍽️ Recettes | recettes, ingredients, recette_ingredients, etapes_recettes, versions_recettes |
| 6-7 | 🛍️ Courses | articles_courses, articles_inventaire |
| 8-13 | 👨‍👩‍👧‍👦 Famille | child_profiles, wellbeing_entries, milestones, family_activities, health_routines, health_objectives |
| 14-19 | 🏠 Maison | projects, project_tasks, garden_items, garden_logs, routines, routine_tasks |
| 20-22 | 📅 Planning | calendar_events, plannings, repas |
| 23 | 👨‍🍳 Batch Cooking | batch_meals |
| 24 | 💰 Budget | family_budgets |

---

## 🛠️ Fichiers pour vous aider

| Fichier | Utilité |
|---------|---------|
| `.env.local` | Configuration BD (créé pour vous) |
| `CONFIG_SUPABASE_RAPIDE.md` | Guide pour configurer Supabase en 5 min |
| `CHECKLIST_FINALE_MAISON.md` | Test complet du module après |
| `GUIDE_CREATION_TABLES_COMPLETES.md` | Détails du script de création |

---

## 🚀 Ordre d'exécution exact

```
1. Ouvrir .env.local
   ↓
2. Ajouter DATABASE_URL (obtenu depuis Supabase)
   ↓
3. Sauvegarder le fichier
   ↓
4. Exécuter : python scripts/create_maison_tables.py
   ↓
5. Attendre le message de succès
   ↓
6. Exécuter : streamlit run src/app.py
   ↓
7. ✅ Erreur disparue !
```

---

## 💡 Pourquoi cette erreur ?

L'application Streamlit utilise SQLAlchemy ORM qui mapping automatiquement les modèles Python aux tables PostgreSQL.

**Mais** :
- Les modèles sont définis en Python (classe `CalendarEvent`)
- Les tables doivent exister en PostgreSQL
- Sans configuration BD, l'app ne peut pas créer les tables

Quand vous accédez au module Planning, il tente de lire `calendar_events` qui n'existe pas → Erreur !

---

## 📞 Questions récurrentes

**Q: Dois-je créer les tables manuellement en Supabase ?**
R: Non ! Le script `create_maison_tables.py` fait tout. Il suffit d'avoir la `DATABASE_URL`.

**Q: Peut-je utiliser SQLite local au lieu de Supabase ?**
R: Oui, mais vous devez utiliser une URL SQLite : `sqlite:///matanne.db`

**Q: L'erreur persiste après le script ?**
R: Vérifiez :
- Que `.env.local` a une `DATABASE_URL` correcte
- Que la connection Supabase est accessible
- Relancez l'app : `streamlit run src/app.py`

---

## ✨ Prochaine étape

Consultez [CONFIG_SUPABASE_RAPIDE.md](CONFIG_SUPABASE_RAPIDE.md) pour configurer Supabase ! ⚡
