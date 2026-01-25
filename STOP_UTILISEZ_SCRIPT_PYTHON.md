# ⚠️ STOP - Ne pas utiliser le fichier SQL !

## 🔴 Le problème

```
ERROR: 42703: column "nom" does not exist
```

Le fichier `sql/009_create_all_tables_complete.sql` **NE CORRESPOND PAS** aux vrais modèles SQLAlchemy.

C'est un problème fondamental : essayer de créer manuellement le SQL pour 24 tables avec 100+ colonnes est **une mauvaise idée**.

---

## ✅ La solution : Utilisez le script Python

```bash
python scripts/create_maison_tables.py
```

**Pourquoi c'est mieux :**

| Aspect | Script Python | SQL Manuel |
|--------|---------------|-----------|
| Colonnes correctes | ✅ 100% (du code) | ❌ Erreurs constantes |
| Facilité à maintenir | ✅ Auto-synchro | ❌ À jour manuellement |
| Relations FK | ✅ Parfaites | ❌ Risques d'erreurs |
| Indices | ✅ Complets | ❌ À mettre à jour |
| Contraintes CHECK | ✅ Toutes | ❌ Oubliées |

---

## 🚀 Workflow correct (3 étapes)

### 1️⃣ Configurer DATABASE_URL

Ouvrez `.env.local` et remplissez :
```env
DATABASE_URL=postgresql://postgres.[project]:[password]@aws-0-region.pooler.supabase.com:6543/postgres
```

### 2️⃣ Créer les tables avec Python

```bash
python scripts/create_maison_tables.py
```

Vous devez voir :
```
🎉 RÉSUMÉ: 24/24 tables créées
✨ SUCCÈS! Toutes les tables sont créées.
```

### 3️⃣ Relancer l'app

```bash
streamlit run src/app.py
```

---

## ❌ Pourquoi le SQL est mauvais

Le fichier SQL essaie d'être "générique" mais les modèles Python ont **des tonnes de colonnes personnalisées** :

### Exemple : Table `ingredients`

**Ce que dit le SQL :**
```sql
CREATE TABLE ingredients (
    nom VARCHAR(200),
    unite_default VARCHAR(20),
    calories_per_100g FLOAT
);
```

**Ce que dit le modèle Python :**
```python
class Ingredient(Base):
    nom: Mapped[str]
    categorie: Mapped[str]
    unite: Mapped[str]  # ← "unite", pas "unite_default" !
    # calories_per_100g n'existe pas du tout !
```

❌ Mismatch => Erreur SQL !

---

## 🎯 Résumé

| ❌ NE FAITES PAS | ✅ FAITES CELA |
|------------------|----------------|
| Utiliser SQL manuel | `python scripts/create_maison_tables.py` |
| Copier-coller SQL | Laisser Python lire les modèles |
| Corriger les colonnes | Code Python = source de vérité |

---

## 🔗 Documentation

- [ACTION_IMMEDIATE_ERREUR_CALENDAR.md](ACTION_IMMEDIATE_ERREUR_CALENDAR.md) - Guide rapide complet
- [FIX_ERREUR_DIFFICULTY_DOES_NOT_EXIST.md](FIX_ERREUR_DIFFICULTY_DOES_NOT_EXIST.md) - Explication détaillée

**Commencez par exécuter :**
```bash
python scripts/create_maison_tables.py
```

C'est la SEULE méthode garantie de fonctionner ! ✅
