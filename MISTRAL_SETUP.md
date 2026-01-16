# Configuration Mistral API

## 🔑 Obtenir une clé API Mistral

1. Allez sur https://console.mistral.ai/
2. Créez un compte ou connectez-vous
3. Générez une clé API
4. Copiez la clé (elle commence par `sk-`)

## ⚙️ Configuration pour le développement

### Option 1: Fichier `.env.local` (Recommandé pour dev local)

Modifiez `/workspaces/assistant_matanne/.env.local`:

```dotenv
MISTRAL_API_KEY=sk-YOUR_ACTUAL_KEY_HERE
```

Remplacez `sk-YOUR_ACTUAL_KEY_HERE` par votre vraie clé API.

### Option 2: Variable d'environnement (Pour Linux/Mac)

```bash
export MISTRAL_API_KEY='sk-YOUR_ACTUAL_KEY_HERE'
```

### Option 3: Streamlit Secrets (Pour Streamlit Cloud)

Créez/modifiez `.streamlit/secrets.toml`:

```toml
[mistral]
api_key = "sk-YOUR_ACTUAL_KEY_HERE"
model = "mistral-small-latest"
```

## 🚀 Lancer l'application

```bash
cd /workspaces/assistant_matanne
streamlit run src/app.py --server.enableCORS false --server.enableXsrfProtection false
```

## ❌ Erreurs courantes

### "Clé API Mistral manquante"
- ✅ Vérifiez que `MISTRAL_API_KEY` est dans `.env.local`
- ✅ Redémarrez Streamlit après modification du `.env.local`
- ✅ Vérifiez que le chemin `.env.local` est correct

### "Request URL is missing protocol"
- ✅ Vous avez probablement une clé API factice (`sk-test-...`)
- ✅ Remplacez par une vraie clé API depuis https://console.mistral.ai/

### "Invalid API Key"
- ✅ Vérifiez que la clé est correcte (elle commence par `sk-`)
- ✅ Vérifiez qu'il n'y a pas d'espaces avant/après la clé

## 📝 Notes

- La clé API n'est jamais commitée dans git (`.env.local` est ignoré)
- En production (Streamlit Cloud), utilisez les secrets via l'interface web
- Les tests utilisent une clé de test, mais l'app réelle a besoin d'une clé valide
