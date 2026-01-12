# 🚀 Configuration Streamlit Cloud - Guide Complet

## ✅ Corrections appliquées pour Streamlit Cloud

### Nouvelle fonction robuste: `_get_mistral_api_key_from_secrets()`

La fonction cherche la clé API Mistral dans **3 chemins différents**:

1. `st.secrets['mistral']['api_key']` ← Méthode officielle
2. `st.secrets['mistral_api_key']` ← Alternative
3. Itération sur tous les secrets si le nom contient "mistral" et "key"

Cela rend le code **beaucoup plus robuste** sur Streamlit Cloud!

---

## 📋 Étapes pour configurer sur Streamlit Cloud

### 1️⃣ Allez dans Settings de votre app

1. Connectez-vous à https://share.streamlit.io/
2. Cliquez sur votre app
3. Cliquez sur **⚙️ Settings** (en haut à droite)

### 2️⃣ Allez à la section "Secrets"

Vous verrez un formulaire avec du texte:
```
Secrets are securely stored on Streamlit Cloud and 
synced to your app with every deploy.
```

### 3️⃣ Copiez-collez EXACTEMENT ceci:

```toml
[mistral]
api_key = "votre_clé_api_mistral_complète"
```

Note: La clé peut commencer par `sk-`, `msk-`, ou autre format - c'est normal!

### 4️⃣ Valeurs importantes:

- **N'utilisez PAS** `[mistral_api_key]` (ancien format)
- **N'utilisez PAS** `mistral = "votre_clé"` (mauvais format)
- **REMPLACEZ** `votre_clé_api_mistral_complète` par votre **VRAIE clé API** (du copy-paste depuis console.mistral.ai)
- **La clé peut commencer par n'importe quel préfixe** (sk-, msk-, ou autre - c'est normal)
- **N'ajoutez PAS** de guillemets supplémentaires: `api_key = 'votre_clé'` ❌

### 5️⃣ Cliquez sur "Save"

Streamlit va redéployer l'app automatiquement.

### 6️⃣ Attendez 30-60 secondes

Le redéploiement peut prendre du temps. Vous verrez:
- 🟡 "Deploying..." (gris)
- ✅ "App is live" (vert)

### 7️⃣ Testez la configuration

Accédez à votre page de debug:
```
https://votre-app.streamlit.app/debug_config
```

Vous devriez voir:
```
✅ Configuration app chargée!
✅ API Key: sk-xxx...
```

---

## 🔍 Déboguer sur Streamlit Cloud

### Page de debug intégrée

Lancez cette page pour voir EXACTEMENT ce qui se passe:

```bash
streamlit run debug_config.py
```

Ou directement via l'URL:
```
https://votre-app.streamlit.app/debug_config
```

Elle affiche:
1. État de `st.secrets`
2. Tous les secrets présents
3. Statut de la clé API Mistral
4. Charge la configuration complète

### Logs en direct

Sur Streamlit Cloud, cliquez sur **Logs** (en bas) pour voir:
```
[32mDEBUG[0m | src.core.config | ✅ Clé API Mistral chargée depuis st.secrets
```

---

## ⚠️ Problèmes courants et solutions

### ❌ "Clé API Mistral manquante"

**Solutions à essayer dans cet ordre:**

1. **Vérifiez le format du secret**
   ```toml
   [mistral]
   api_key = "sk-xxx"
   ```
   Pas de guillemets supplémentaires!

2. **Re-déployez l'app**
   - Allez dans Settings
   - Changez un espace dans les secrets et resave
   - Cela force le redéploiement

3. **Attendez 60 secondes**
   - Parfois Streamlit a besoin de temps
   - Rafraîchissez la page (F5)

4. **Vérifiez votre clé API est valide**
   - Allez sur https://console.mistral.ai/
   - Vérifiez que votre clé n'est pas expirée
   - Générée une nouvelle si besoin

### ❌ "Configuration IA manquante" mais d'autres erreurs

Utilisez `debug_config.py` pour voir exactement ce qui se passe:
```bash
streamlit run debug_config.py
```

### ❌ Les logs ne montrent rien

1. Cliquez sur **Logs** en bas de la page
2. Cherchez les lignes avec `mistral`
3. Si vide, la config n'a pas été chargée

---

## 🔐 Sécurité - Points importants

- ✅ Les secrets sont **chiffrés** par Streamlit
- ✅ **Jamais visibles** dans le code
- ✅ **Jamais cachés** dans les logs (sauf si vous les affichezexplicitement)
- 🚫 **Ne commitez JAMAIS** votre clé API

---

## 📝 Résumé des changements de code

### Fichier: `src/core/config.py`

**Avant:**
```python
def _read_st_secret(section: str):
    try:
        if hasattr(st, "secrets"):
            return st.secrets.get(section)
    except Exception:
        return None
```

**Après:**
```python
def _get_mistral_api_key_from_secrets():
    """Essaie 3 chemins différents pour trouver la clé"""
    # Chemin 1: st.secrets['mistral']['api_key']
    # Chemin 2: st.secrets['mistral_api_key']
    # Chemin 3: Itération sur tous les secrets
```

**Avantages:**
- ✅ Beaucoup plus robuste
- ✅ Compatible avec plusieurs formats
- ✅ Gestion d'erreurs améliorée
- ✅ Debug plus facile

---

## 💡 Tips avancés

### Tester localement avant de déployer

```bash
# Créez .streamlit/secrets.toml
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
[mistral]
api_key = "sk-test_local"
EOF

# Testez
streamlit run debug_config.py
```

### Ajouter aussi la DB

```toml
[mistral]
api_key = "sk-xxx"

[db]
host = "xxx.supabase.co"
port = 5432
name = "postgres"
user = "postgres"
password = "xxx"
```

### Alternative: Variables d'environnement

Si les secrets ne fonctionnent pas, utilisez **Advanced settings** dans Streamlit Cloud:

```
MISTRAL_API_KEY=sk-xxx
```

---

## ✅ Checklist avant de déployer

- [ ] Clé API obtenue depuis https://console.mistral.ai/
- [ ] Secret ajouté dans Settings → Secrets (format TOML correct)
- [ ] App redéployée après modification
- [ ] Attendu 60 secondes
- [ ] Page de debug testée: `debug_config.py`
- [ ] Logs affichent "✅ Clé API Mistral chargée depuis st.secrets"
- [ ] `.env.local` n'est pas commitée (dans `.gitignore`)

---

## 🆘 Besoin d'aide?

1. Consultez `debug_config.py` - page de diagnostic complète
2. Lisez les logs Streamlit Cloud (onglet Logs)
3. Vérifiez le format TOML: https://toml.io/
4. Testez localement d'abord

**Créé:** 2026-01-12
**Version:** 1.0
