# 🚀 Configuration Mistral pour Streamlit Cloud - Guide Complet

## ⚠️ URGENT: Tu as un problème de configuration des secrets!

Les messages d'erreur montrent que la clé API Mistral n'est **pas trouvée en Streamlit Cloud**, même si tu dis qu'elle est configurée.

## 🔍 Diagnostic

Première chose: **Lance le script de diagnostic** pour voir exactement ce qui manque:

```bash
streamlit run debug_streamlit_cloud.py
```

Cela te montrera si les secrets sont visibles ou pas.

## ✅ Solutions (essaie dans cet ordre)

### Solution 1: Via Streamlit Secrets (Recommandé) 

**Si ça ne fonctionne pas, c'est probablement un problème de FORMAT TOML**

1. Va à https://share.streamlit.io/ → Sélectionne ton app
2. Clique sur **⚙️ Settings** en haut à droite
3. Va dans **"Secrets"** (onglet gauche)
4. Saisis **EXACTEMENT** ceci (ATTENTION AU FORMAT!):

```toml
[mistral]
api_key = "sk-xxxxxxxxxxxxx"
```

**ATTENTION:**
- ❌ Pas de guillemets supplémentaires: `api_key = "'sk-xxx'"`  ← MAUVAIS
- ✅ Bon format: `api_key = "sk-xxx"`  ← BON
- ❌ Pas d'espaces bizarres avant/après `=`
- Utilise des guillemets droits `"` pas courbes `""`

5. Clique **Save** 
6. **Re-déploie** l'app complètement (pas juste refresh)
7. Attends 1-2 minutes pour que les changements se propagent

### Solution 2: Via Variable d'Environnement (Alternative)

Si Solution 1 ne marche pas:

1. Va à https://share.streamlit.io/ → Sélectionne ton app
2. Clique sur **⚙️ Settings** 
3. Va dans **"Advanced Settings"** (tout en bas du menu gauche)
4. **Add secret** (ou cherche un input pour variables d'env)
5. Ajoute:
   ```
   MISTRAL_API_KEY = sk-xxxxxxxxxxxxx
   ```
6. Sauvegarde et redéploie

### Solution 3: Vérifier le fichier secrets.toml local

Si tu testes en local avec `streamlit run`, assure-toi qu'il y a un fichier `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
[mistral]
api_key = "sk-xxxxxxxxxxxxx"
EOF
```

Puis redémarre Streamlit:
```bash
streamlit run src/app.py
```

## 🔧 Dépannage

### "Clé API Mistral manquante (Streamlit Cloud)" → Rien ne change?

Fais ceci:

1. **Vérifie qu'il n'y a pas de cache**:
   - Vide le cache Streamlit: `streamlit cache clear`
   - Vide le cache navigateur (Ctrl+Shift+Delete)

2. **Redéploie complètement**:
   - Ne fais pas que refresh la page
   - Redéploie toute l'app via GitHub

3. **Vérifie le format TOML**:
   - Utilise https://www.toml-lint.com/ pour valider
   - Copie-colle ton contenu secrets.toml là dedans

4. **Vérifie que c'est la bonne clé API**:
   - Clé test: commence par `sk-test-` → ❌ NE FONCTIONNE PAS
   - Vraie clé: commence par `sk-` sans `test` → ✅ OK
   - Vérifies sur https://console.mistral.ai/api-keys/

### Le script debug_streamlit_cloud.py montre quoi?

Lance-le et partage le résultat exact pour qu'on puisse diagnostiquer:

```bash
streamlit run debug_streamlit_cloud.py
```

Regarde particulièrement:
- ✅ ou ❌ à côté de "STREAMLIT CLOUD DETECTED"
- La section "4️⃣ Streamlit Secrets" - toutes les chemins
- Si les clés sont listées dans "Chemin 3: Recherche toutes les clés"

## 📝 Prochaines étapes

Une fois que tu auras configuré correctement:

1. Lance le diagnostic: `streamlit run debug_streamlit_cloud.py`
2. Redéploie ton app
3. Attends 2-3 minutes
4. Teste en cliquant sur "Générer version bébé"

**Partage-moi la sortie du script debug si ça ne marche toujours pas!**
