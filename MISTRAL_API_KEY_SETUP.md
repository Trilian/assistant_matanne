# ⚠️ URGENT: Configuration Mistral API

Vous avez actuellement une clé de **test** (`sk-test-dummy-key-replace-with-real-key`) 
qui ne fonctionne pas avec l'API Mistral réelle.

## 🔑 Comment obtenir votre vraie clé API

### Étape 1: Créer un compte Mistral
1. Allez sur https://console.mistral.ai/
2. Cliquez "Sign up" ou "Log in" si vous avez déjà un compte
3. Complétez l'enregistrement

### Étape 2: Générer une clé API
1. Dans le dashboard Mistral, allez dans **API Keys**
2. Cliquez "Create new API key"
3. **Copiez la clé** (elle commence par `sk-`)

### Étape 3: Configurer dans votre app

#### Option A: Local Development
Modifiez `/workspaces/assistant_matanne/.env.local`:

```dotenv
# Avant:
MISTRAL_API_KEY=sk-test-dummy-key-replace-with-real-key

# Après:
MISTRAL_API_KEY=sk-VOTRE_VRAIE_CLE_ICI
```

Remplacez `sk-VOTRE_VRAIE_CLE_ICI` par votre vraie clé de Mistral.

#### Option B: Streamlit Cloud
1. Allez sur https://share.streamlit.io/
2. Cliquez sur votre app
3. Settings (⚙️) > Secrets
4. Ajoutez ou modifiez:
```toml
[mistral]
api_key = "sk-VOTRE_VRAIE_CLE_ICI"
model = "mistral-small-latest"
```

### Étape 4: Redémarrer l'app
```bash
# Local: redémarrez Streamlit
# Cloud: secrets sauvegardés = redémarrage auto
```

## ✅ Vérification

Après avoir entré votre clé:
- L'app doit démarrer sans erreur API
- Les fonctionnalités IA (générer recette) doivent fonctionner
- Pas de message "Clé API Mistral manquante"

## ⚠️ Important

- **Ne commitez jamais** votre vraie clé en git!
- `.env.local` est dans `.gitignore` (safe pour local)
- Pour Streamlit Cloud, utilisez les secrets via l'interface web
- Les clés test (`sk-test-...`) ne fonctionnent **pas**

## 🆘 Besoin d'aide?

Si ça ne fonctionne toujours pas:
1. Vérifiez la clé commence par `sk-` (pas `sk-test-`)
2. Vérifiez qu'il n'y a pas d'espaces avant/après la clé
3. Redémarrez l'app après modification
4. Vérifiez que votre compte Mistral a des crédits
