# ⚡ ACTIONS IMMÉDIATE - Relancer l'application sans erreur

## 🚨 Erreur actuelle

```
relation "calendar_events" does not exist
```

## ✅ Solution : 3 étapes simples

---

## 1️⃣ Configurer Supabase

**Ouvrez** le fichier `.env.local` (créé pour vous à la racine)

**Remplissez cette ligne :**
```env
DATABASE_URL=
```

**Avec votre URL Supabase :**
```env
DATABASE_URL=postgresql://postgres.abc123:mypassword@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
```

### 📍 Où trouver cette URL ?

1. Allez à https://supabase.com/dashboard
2. Sélectionnez votre projet
3. Settings (⚙️) → Database
4. Copier "Connection string" (PostgreSQL)
5. Coller dans `.env.local`

**Besoin d'aide ?** Consultez [CONFIG_SUPABASE_RAPIDE.md](CONFIG_SUPABASE_RAPIDE.md)

---

## 2️⃣ Créer les tables manquantes

```bash
python scripts/create_maison_tables.py
```

**Attendez ce message :**
```
✨ SUCCÈS! Toutes les tables sont créées.
```

---

## 3️⃣ Relancer l'application

```bash
streamlit run src/app.py
```

**L'erreur doit disparaître !** ✅

---

## 📊 Cela crée :

Le script crée automatiquement **24 tables** :
- 5 tables Recettes
- 2 tables Courses
- 6 tables Famille
- 6 tables Maison (🏠 module)
- 3 tables Planning
- 1 table Batch Cooking
- 1 table Budget

---

## 🆘 Ça n'a pas marché ?

### Erreur: "Configuration DB manquante"
```
❌ DATABASE_URL est vide ou incorrecte dans .env.local
✅ Remplissez-la avec votre URL Supabase (voir étape 1)
```

### Erreur: "could not connect to server"
```
❌ L'URL Supabase est incorrecte
❌ Votre projet Supabase n'est pas accessible
✅ Vérifiez l'URL : postgresql://...@... (avec les 2 points @ et :port)
```

### Erreur: "relation X does not exist" persiste
```
❌ Le script n'a pas créé les tables
✅ Vérifiez que DATABASE_URL est remplie
✅ Relancez : python scripts/create_maison_tables.py
```

---

## 📚 Documentation complète

| Fichier | Pour qui |
|---------|----------|
| [CONFIG_SUPABASE_RAPIDE.md](CONFIG_SUPABASE_RAPIDE.md) | Lire si vous ne savez pas où obtenir DATABASE_URL |
| [SOLUTION_CALENDAR_EVENTS_ERROR.md](SOLUTION_CALENDAR_EVENTS_ERROR.md) | Lire si vous voulez comprendre l'erreur |
| [CHECKLIST_FINALE_MAISON.md](CHECKLIST_FINALE_MAISON.md) | Lire après le succès pour tester |

---

## ✨ That's it !

Après ces 3 étapes, le module Maison doit fonctionner parfaitement ! 🎉

Prochaine étape : Naviguer vers 🏠 **Maison** dans la barre latérale de l'app.
