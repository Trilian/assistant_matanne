# 🔧 Configuration Mistral API - Guide Complet

## ⚠️ Problème détecté

L'erreur que vous recevez signifie que **aucune clé API Mistral n'est configurée**.

## ✅ Solutions (dans cet ordre de priorité)

### **Méthode 1: Variables d'environnement (RECOMMANDÉE)**

La plus simple et la plus sûre pour développement local.

```bash
# Dans un terminal:
export MISTRAL_API_KEY="votre_clé_api_ici"

# Ou ajoutez dans le fichier .env.local
MISTRAL_API_KEY="votre_clé_api_ici"
```

### **Méthode 2: Streamlit Secrets (pour Streamlit Cloud)**

1. **Localement** - créez `.streamlit/secrets.toml`:
```toml
[mistral]
api_key = "sk-xxxxxxxxxxxxx"
model = "mistral-small-latest"

[db]
host = "localhost"
port = 5432
name = "matanne"
user = "postgres"
password = "postgres"
```

2. **Sur Streamlit Cloud**:
   - Allez sur https://share.streamlit.io/
   - Cliquez sur votre app → Settings
   - Dans "Secrets", collez:
   ```toml
   [mistral]
   api_key = "sk-xxxxxxxxxxxxx"
   
   [db]
   host = "votre_db_host"
   port = 5432
   name = "votre_db"
   user = "votre_user"
   password = "votre_password"
   ```

## 🔑 Obtenir une clé API Mistral

1. Allez sur https://console.mistral.ai/
2. Créez un compte (gratuit)
3. Cliquez sur "API Keys"
4. Générez une nouvelle clé
   - Peut commencer par `sk-`, `msk-`, ou autre préfixe (c'est normal)
5. Copiez-la intégralement - **ne la partagez jamais**

## 🧪 Vérifier la configuration

Exécutez ce script de debug:

```bash
# Option 1: Avec Streamlit (interface web)
streamlit run debug_config.py

# Option 2: Via Python
python -c "
from src.core.config import obtenir_parametres
try:
    config = obtenir_parametres()
    print('✅ Configuration OK')
    print(f'Modèle: {config.MISTRAL_MODEL}')
except Exception as e:
    print(f'❌ Erreur: {e}')
"
```

## 🚨 Checklist de dépannage

- [ ] Clé API obtenue depuis https://console.mistral.ai/
- [ ] Clé API configurée dans `.env.local` OU `.streamlit/secrets.toml`
- [ ] Fichier `.env.local` n'est PAS dans `.gitignore` (vérifiez!)
- [ ] Relancez l'application après modification du `.env`
- [ ] Pour Streamlit: Re-déployez après changement de secrets
- [ ] Clé API n'est pas la clé de test "test_key_local"

## 🔍 Ordre de priorité de la configuration

La code cherche la clé API dans cet ordre:

1. **Streamlit Secrets** (`st.secrets['mistral']['api_key']`) - Production Cloud
2. **Variable d'environnement** (`MISTRAL_API_KEY`) - Développement local
3. **❌ Erreur** si aucun n'est trouvé

### Comment appliquer chaque méthode:

**Développement local** → Utilisez `.env.local`:
```bash
cp .env.example .env.local
# Éditez le fichier et ajoutez votre clé:
# MISTRAL_API_KEY=sk-xxxxxxxxxxxxx
```

**Streamlit Cloud** → Utilisez les secrets web:
```
Allez dans Settings de votre app → Secrets
```

## 📝 Fichiers modifiés

- ✅ `.streamlit/secrets.toml` - Structure corrigée
- ✅ `.env.example` - Ajout de MISTRAL_API_KEY
- ✅ `.env.local` - Créé avec template

## 💡 Tips

- 🚫 Ne commitez **jamais** votre clé API dans Git
- 🔐 Utilisez `.env.local` pour dev local (ignoré par Git)
- 🌍 Utilisez Streamlit Secrets pour Cloud (sécurisé par Streamlit)
- ⚡ Testez avec `debug_config.py` avant de déployer
