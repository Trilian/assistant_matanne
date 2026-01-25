# 🔧 Configuration Base de Données requise

**Erreur** : `Configuration DB manquante!`

**Cause** : Le fichier `.env.local` (ou variables d'environnement) contenant les identifiants Supabase n'existe pas.

## Solution : Configurer la BD

### Étape 1 : Créer `.env.local`

À la racine du projet (`d:\Projet_streamlit\assistant_matanne`), créer un fichier `.env.local` :

```bash
# .env.local (option 1)
DATABASE_URL=postgresql://user:password@host:5432/database
```

Ou avec les paramètres séparés :

```bash
# Option 2 : Variables d'environnement séparées
DB_HOST=your-project.supabase.co
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=postgres
```

Ou avec Streamlit Secrets :

```bash
# Option 3 : .streamlit/secrets.toml
[db]
host = "your-project.supabase.co"
port = "5432"
name = "postgres"
user = "postgres"
password = "your-password"
```

### Étape 2 : Obtenir les credentials Supabase

1. Aller sur [supabase.com](https://supabase.com)
2. Ouvrir votre projet
3. Cliquer sur "Settings" → "Database"
4. Copier la connexion PostgreSQL :
   ```
   postgresql://postgres.[project-id]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

### Étape 3 : Tester la connexion

```bash
python -c "
from src.core.database import obtenir_moteur
try:
    moteur = obtenir_moteur()
    print('✅ Connexion BD OK')
except Exception as e:
    print(f'❌ Erreur: {e}')
"
```

### Étape 4 : Créer les tables

Une fois connecté, créer les tables :

```bash
python -c "
from src.core.database import obtenir_moteur
from src.core.models import Base

moteur = obtenir_moteur()
Base.metadata.create_all(bind=moteur)
print('✅ Tables créées')
"
```

### Étape 5 : Relancer l'app

```bash
streamlit run src/app.py
```

## Format DATABASE_URL

Pour PostgreSQL Supabase :
```
postgresql://[user]:[password]@[host]:[port]/[database]
```

**Exemple réel :**
```
postgresql://postgres.abc123:mypassword123@aws-0-eu-west-1.pooler.supabase.com:6543/postgres
```

## Fichiers clés

- ✅ [.env.local](../.env.local) - À créer si n'existe pas
- ✅ [src/core/config.py](../src/core/config.py) - Charge configuration
- ✅ [src/core/database.py](../src/core/database.py) - Connexion BD

## Vérifier la configuration

```bash
# Afficher la configuration chargée
python -c "from src.core.config import obtenir_parametres; config = obtenir_parametres(); print(f'DB: {config.DATABASE_URL[:50]}...')"
```

## Dépannage

### "psycopg2.errors.UndefinedTable"
- ✅ BD connectée mais tables manquantes
- Solution : Lancer `Base.metadata.create_all()`

### "password authentication failed"
- ❌ Mauvais mot de passe
- Vérifier credentials Supabase

### "connection refused"
- ❌ Host/port incorrect
- Vérifier URL de connexion Supabase

### ".env.local not found"
- ✅ Normal (fallback sur variables env)
- Créer fichier `.env.local` pour plus de clarté

## Prochaines étapes

1. ✅ Créer `.env.local`
2. ✅ Ajouter `DATABASE_URL` ou variables
3. ✅ Tester connexion
4. ✅ Créer tables : `Base.metadata.create_all()`
5. ✅ Relancer app

---

**Status** : 📋 Configuration requise  
**Temps** : ~5 minutes
