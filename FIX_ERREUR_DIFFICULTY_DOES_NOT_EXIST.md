# ⚠️ Correction - Erreur SQL `column "difficulty" does not exist`

## 🔴 Problème

Le fichier SQL `009_create_all_tables_complete.sql` a des colonnes incorrectes qui ne correspondent pas aux vrais modèles Python.

```
ERROR: 42703: column "difficulty" does not exist
```

## ✅ Solution Recommandée

**N'utilisez PAS le fichier SQL directement !**

**Utilisez plutôt le script Python :**

```bash
python scripts/create_maison_tables.py
```

Ce script utilise les **vrais modèles SQLAlchemy** et crée les colonnes correctes.

---

## 🔧 Pourquoi ?

Le SQL manuel est **très difficile à maintenir** car :
- SQLAlchemy a 50+ colonnes personnalisées
- Les modèles changent fréquemment
- Il y a 24 tables avec des relations complexes

Le script Python `create_maison_tables.py` utilise `Base.metadata.create_all()` qui lit directement les modèles Python et crée les tables **exactement comme définies**.

---

## ⚡ Workflow correct

```bash
# 1. Configurer DATABASE_URL dans .env.local
# DATABASE_URL=postgresql://...

# 2. Exécuter le script (PAS le SQL)
python scripts/create_maison_tables.py

# Résultat:
# ✨ SUCCÈS! Toutes les tables sont créées.

# 3. Relancer l'app
streamlit run src/app.py
```

---

## 📝 Si vous voulez quand même utiliser SQL...

Vous devez corriger les colonnes pour chaque table.

**Exemple pour `recettes` :**

❌ **Incorrect :**
```sql
CREATE TABLE recettes (
    difficulty VARCHAR(20),  -- N'existe pas !
    ...
);
```

✅ **Correct :**
```sql
CREATE TABLE recettes (
    difficulte VARCHAR(50) NOT NULL DEFAULT 'moyen',  -- Correct !
    type_repas VARCHAR(50) NOT NULL DEFAULT 'dîner',
    est_rapide BOOLEAN DEFAULT FALSE,
    compatible_cookeo BOOLEAN DEFAULT FALSE,
    -- ... 20+ autres colonnes
);
```

Mais c'est **très long et sujet aux erreurs**.

---

## 🎯 Recommandation

**Utilisez TOUJOURS le script Python :**

```bash
python scripts/create_maison_tables.py
```

C'est la seule méthode **garante d'être 100% correcte** ! ✅

---

## 📚 Documentation

- [ACTION_IMMEDIATE_ERREUR_CALENDAR.md](ACTION_IMMEDIATE_ERREUR_CALENDAR.md) - Guide rapide
- [UTILISER_SQL_SUPABASE.md](UTILISER_SQL_SUPABASE.md) - Si vous insistez sur SQL
