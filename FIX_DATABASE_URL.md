# 🔧 Guide de configuration DATABASE_URL Supabase

## ❌ Problème actuel

Erreur: **"Tenant or user not found"**

Cela signifie que l'URL de connexion n'est pas au bon format pour Supabase.

---

## ✅ Solution: Obtenir la bonne URL depuis Supabase

### Étape 1: Se connecter à Supabase

1. Aller sur https://supabase.com/dashboard
2. Se connecter avec votre compte
3. Sélectionner votre projet **Assistant MaTanne**

### Étape 2: Obtenir la Database URL

1. Cliquer sur **⚙️ Settings** (en bas à gauche)
2. Cliquer sur **Database**
3. Scroller jusqu'à la section **Connection string**
4. Sélectionner l'onglet **URI**
5. Vous verrez une URL comme:

```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**⚠️ IMPORTANT:** Le `[YOUR-PASSWORD]` n'est PAS affiché. Vous devez le remplacer par votre mot de passe.

### Étape 3: Copier dans .env.local

```env
DATABASE_URL=postgresql://postgres.VOTRE_PROJECT_REF:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Exemple réel (avec vos données):**
```env
# Remplacer VOTRE_PROJECT_REF par la référence de votre projet
# Remplacer VOTRE_MOT_DE_PASSE par le mot de passe de votre base
DATABASE_URL=postgresql://postgres.haieczwixbkeuwcgdzvn:Famille2Geek@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## 🔍 Formats d'URL Supabase

### Option 1: Connection Pooler (recommandé pour l'app)
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```
✅ Utiliser pour: Application Streamlit en production  
✅ Port: **6543**

### Option 2: Connexion directe (pour migrations)
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
```
✅ Utiliser pour: Déploiement SQL, migrations Alembic  
✅ Port: **5432**

---

## 📋 Checklist de vérification

- [ ] L'URL commence par `postgresql://`
- [ ] L'utilisateur est `postgres.[PROJECT-REF]` (avec le point et la ref)
- [ ] L'hôte est `aws-0-eu-central-1.pooler.supabase.com` (PAS `db.xxx`)
- [ ] Le port est `6543` (pooler) ou `5432` (direct)
- [ ] Le mot de passe est correct
- [ ] Pas d'espaces dans l'URL

---

## 🧪 Tester la connexion

Après avoir mis à jour `.env.local`:

```bash
# Test rapide
python test_db_connection.py

# Si ça marche, tester le déploiement
python deploy_supabase.py --check
```

---

## 🆘 Toujours des erreurs?

### Erreur: "Tenant or user not found"
❌ Le format utilisateur est incorrect  
✅ Solution: Vérifier que l'utilisateur est `postgres.PROJECT_REF` (avec le point)

### Erreur: "could not translate host name"
❌ Le nom d'hôte est incorrect  
✅ Solution: Utiliser `aws-0-eu-central-1.pooler.supabase.com`

### Erreur: "password authentication failed"
❌ Le mot de passe est incorrect  
✅ Solution: Copier le mot de passe depuis Supabase Dashboard > Settings > Database

### Erreur: "timeout"
❌ Problème de réseau ou firewall  
✅ Solution: Vérifier votre connexion internet, tester depuis un autre réseau

---

## 📱 Obtenir le PROJECT-REF

Si vous ne connaissez pas votre PROJECT-REF:

1. Dashboard Supabase
2. URL de votre projet: `https://supabase.com/dashboard/project/haieczwixbkeuwcgdzvn`
3. Le PROJECT-REF est: `haieczwixbkeuwcgdzvn` (la dernière partie de l'URL)

**Donc votre utilisateur est:**
```
postgres.haieczwixbkeuwcgdzvn
```

---

## 🔐 Réinitialiser le mot de passe

Si vous avez oublié le mot de passe de la base:

1. Dashboard Supabase
2. Settings > Database
3. Section **Database Password**
4. Cliquer sur **Reset database password**
5. Copier le nouveau mot de passe
6. Mettre à jour `.env.local`

---

## ✅ URL correcte finale

Avec vos informations:
```env
DATABASE_URL=postgresql://postgres.haieczwixbkeuwcgdzvn:VOTRE_VRAI_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**Remplacer `VOTRE_VRAI_MOT_DE_PASSE` par votre mot de passe actuel.**

Si le mot de passe actuel (`Famille2Geek`) ne fonctionne pas, il faut le réinitialiser sur Supabase.
