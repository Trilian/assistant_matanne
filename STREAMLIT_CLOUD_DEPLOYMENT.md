# 🚀 Guide Streamlit Cloud

## 📋 Prérequis

- Compte GitHub avec ce repo
- Compte Streamlit (connexion via GitHub)
- Clé API Mistral (https://console.mistral.ai/)
- URL Supabase PostgreSQL (https://supabase.com/)

## 🔧 Configuration Streamlit Cloud

### Étape 1: Connecter le repo GitHub

1. Allez sur https://share.streamlit.io/
2. Cliquez "New app"
3. Sélectionnez votre repo GitHub
4. Branche: `main`
5. Main file path: `src/app.py`

### Étape 2: Configurer les Secrets

1. Dans votre app Streamlit Cloud, cliquez **Settings** (⚙️) en haut à droite
2. Allez dans l'onglet **Secrets**
3. Copiez-collez ceci:

```toml
[mistral]
api_key = "sk-YOUR_ACTUAL_MISTRAL_KEY"
model = "mistral-small-latest"

[database]
url = "postgresql://user:password@host:port/postgres"
```

**Remplacez:**
- `sk-YOUR_ACTUAL_MISTRAL_KEY` par votre vraie clé API Mistral
- `postgresql://...` par votre URL Supabase

### Étape 3: Déployer

1. Cliquez **Save**
2. L'app redémarre automatiquement
3. Attendez 2-3 minutes pour que l'app soit prête

## 🔑 Récupérer vos clés

### Clé Mistral
1. Allez sur https://console.mistral.ai/
2. Connectez-vous
3. Allez dans "API Keys"
4. Créez ou copiez une clé (elle commence par `sk-`)

### URL Supabase
1. Allez sur https://supabase.com/
2. Ouvrez votre projet
3. Allez dans **Settings** > **Database**
4. Copiez l'URL PostgreSQL
5. Format: `postgresql://postgres.XXXX:PASSWORD@aws-X-eu.pooler.supabase.com:6543/postgres`

## ⚠️ Erreurs courantes

### "Clé API Mistral manquante"
- ✅ Vérifiez que vous avez configuré les secrets dans Streamlit Cloud
- ✅ Vérifiez que la clé commence par `sk-`
- ✅ Attendez quelques secondes et rafraîchissez la page

### "Connection refused" (Database)
- ✅ Vérifiez que votre URL Supabase est correcte
- ✅ Vérifiez que vous n'êtes pas bloqueés par un pare-feu
- ✅ Contactez le support Supabase

### "Invalid API Key"
- ✅ La clé API Mistral peut être invalide ou expirée
- ✅ Générez une nouvelle clé sur https://console.mistral.ai/

## 📊 Logs et Debugging

Pour voir les logs:
1. Cliquez sur votre app dans Streamlit Cloud
2. Regardez la section **Logs** en bas
3. Cherchez les messages d'erreur rouges

## 🔄 Redéployer après modifications

Juste pusher vos modifications sur `main`:
```bash
git add .
git commit -m "Mon changement"
git push origin main
```

Streamlit Cloud redéploiera automatiquement!

## ✅ Vérification

Une fois déployé, vérifiez:
- ✅ La page d'accueil se charge
- ✅ Pas de message d'erreur rouge
- ✅ Les boutons répondent
- ✅ Vous pouvez générer une recette IA

## 💡 Tips

- Les secrets Streamlit Cloud ne sont jamais loggés
- Utilisez des URLs courtes pour gagner de la bande passante
- Les apps gratuites se mettent en standby après 7 jours d'inactivité
- Vous pouvez redéployer gratuitement illimité
