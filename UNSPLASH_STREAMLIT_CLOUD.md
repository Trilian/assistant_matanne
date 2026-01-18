# 🖼️ Configuration Unsplash sur Streamlit Cloud

## 🔴 Problème: Images ne se génèrent pas

La clé Unsplash n'est pas chargée depuis `st.secrets` sur Streamlit Cloud.

## ✅ Solution

### Étape 1: Vérifier votre clé Unsplash

1. Allez sur https://unsplash.com/oauth/applications
2. Sélectionnez votre application
3. Copiez l'**Access Key** (elle commence par `uc...`)
   - ⚠️ Ce n'est PAS "Secret Key"
   - C'est bien **"Access Key"**

### Étape 2: Configurer Streamlit Cloud

1. Allez sur votre app: https://share.streamlit.io/
2. Trouvez votre app → Cliquez **Settings** (⚙️)
3. Allez dans l'onglet **Secrets** 
4. Ajoutez exactement ceci:

```toml
[unsplash]
api_key = "uc_VOTRE_VRAIE_CLÉ_UNSPLASH"

[mistral]
api_key = "sk-..."

[database]
url = "postgresql://..."
```

**Important:** L'indentation avec `[unsplash]` doit être respectée!

5. Cliquez **Save**
6. Attendez que l'app redémarre (~30 secondes)

### Étape 3: Tester

1. Allez dans votre app
2. Générez une recette
3. Cliquez sur "🎨 Générer l'image"
4. Regardez les **Logs** (en bas à droite)

#### 🟢 Si ça marche:
```
✅ Clé Unsplash chargée (premiers caractères: uc_...)...
Recherche Unsplash pour: Fromage blanc food
Réponse Unsplash: 5 résultats trouvés
✅ Image trouvée via Unsplash
```

#### 🔴 Si ça ne marche pas:
```
⚠️ Clé Unsplash non trouvée - vérifiez st.secrets['unsplash']['api_key']
Clé Unsplash non configurée
```

→ Retournez à l'étape 2, assurez-vous que le format TOML est correct

## 📋 Format TOML correct

```toml
[unsplash]
api_key = "uc_YOUR_KEY_HERE"
```

❌ **INCORRECT:**
```toml
unsplash_api_key = "uc_YOUR_KEY_HERE"
```

## 🧪 Tester localement

```bash
# Terminal
export UNSPLASH_API_KEY="uc_YOUR_KEY"
streamlit run src/app.py
```

## 📊 Structure des secrets Streamlit Cloud

Votre `Secrets` doit ressembler à:
```toml
[mistral]
api_key = "sk-..."
model = "mistral-small-latest"

[database]
url = "postgresql://..."

[unsplash]
api_key = "uc_..."

[pexels]
api_key = "votre_clé_pexels"

[pixabay]
api_key = "votre_clé_pixabay"
```

## 🆘 Ça marche toujours pas?

1. ✅ Vérifiez que la clé commence par `uc_` (pas `sk-` ou autre)
2. ✅ Attendez 5 minutes après avoir sauvegardé les secrets
3. ✅ Rafraîchissez votre navigateur (Ctrl+F5)
4. ✅ Vérifiez les Logs dans Streamlit Cloud (Settings → Logs)
5. ✅ Redéployer: modifiez une ligne dans le code et poussez sur GitHub
   ```bash
   git add .
   git commit -m "Redeploy after secret config"
   git push
   ```

## 📞 Support

Les trois clés de banque d'images sont optionnelles:
- **Unsplash** (recommandé): https://unsplash.com/oauth/applications
- **Pexels**: https://www.pexels.com/api/
- **Pixabay**: https://pixabay.com/api/

Si aucune clé n'est configurée, l'app utilise **Pollinations.ai** (génération IA, pas de clé requise).
