# ⚡ Configuration Rapide Supabase - 5 minutes

## 🚀 Étape 1 : Créer un compte Supabase (si pas encore fait)

1. Allez à https://supabase.com/
2. Cliquez **Sign Up**
3. Créez un compte (GitHub, Google, ou email)

---

## 📋 Étape 2 : Obtenir vos Credentials Supabase

### Dans le Dashboard Supabase :

1. **Ouvrez votre projet** (ou créez-en un)
2. **Settings** (roue ⚙️ en bas à gauche)
3. **Database** (dans le menu)
4. **Connection String** (vous voyez une section "Connection String")

Vous voyez plusieurs options :
- **PostgreSQL** ← Prenez celle-ci !
- Prisma
- URI
- psql
- etc.

### Format de l'URL PostgreSQL

Copie-la, elle ressemble à :
```
postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Exemple réel :**
```
postgresql://postgres.abc123def456:gH7jK9L2mN4pQrS5tU@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
```

---

## 🔧 Étape 3 : Configurer le fichier `.env.local`

1. **Ouvrez** `.env.local` à la racine du projet
2. **Trouvez la ligne :** `DATABASE_URL=`
3. **Collez votre URL :**
   ```env
   DATABASE_URL=postgresql://postgres.abc123:mypassword@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
   ```
4. **Sauvegardez** (Ctrl+S)

**Résultat :**
```
✅ DATABASE_URL=postgresql://postgres.abc123:mypassword@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
```

---

## ⏳ Étape 4 : Créer les tables

Maintenant que la BD est configurée, créez toutes les tables :

```bash
python scripts/create_maison_tables.py
```

Vous devez voir :
```
📊 Initialisation de la base de données...
✅ Connexion BD établie

🔧 CRÉATION DE TOUTES LES TABLES
═════════════════════════════════════════════════════════════════════════════

🍽️  RECETTES
  ✅ recettes                        (12 colonnes)
  ...

🎉 RÉSUMÉ: 24/24 tables créées
✨ SUCCÈS! Toutes les tables sont créées.
```

---

## 🚀 Étape 5 : Lancer l'application

```bash
streamlit run src/app.py
```

L'app s'ouvre à http://localhost:8501

---

## ❌ Dépannage

### Erreur: "relation 'calendar_events' does not exist"
→ Vous n'avez pas encore créé les tables
→ Relancez : `python scripts/create_maison_tables.py`

### Erreur: "psycopg2.errors.OperationalError: could not connect to server"
→ Vérifiez que l'URL est correcte
→ Vérifiez la connexion Internet
→ Testez l'URL avec : `psql "your_url_here"`

### Erreur: "Configuration DB manquante"
→ DATABASE_URL est vide dans `.env.local`
→ Remplissez-la avec votre URL Supabase
→ Sauvegardez le fichier

---

## ✅ Vérification finale

Après le script, vérifiez dans Supabase :

1. **Supabase Dashboard** → Votre projet
2. **Table Editor** (colonne de gauche)
3. Vous devez voir 24 tables listées:
   - recettes
   - ingredients
   - projects
   - garden_items
   - routines
   - calendar_events
   - ... etc

**Si vous voyez toutes les tables = ✅ SUCCÈS !**

---

## 💡 Tips

- **URL Supabase change jamais** : Gardez-la sûre, c'est votre secret !
- **Ne committez JAMAIS .env.local** : C'est déjà dans `.gitignore`
- **PASSWORD sûr** : Supabase génère un password complexe, c'est normal

Vous êtes prêt ! 🎉
