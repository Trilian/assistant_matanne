# 🔍 Comment voir les LOGS sur Streamlit Cloud

## 📋 Problème
Vous ne voyez pas les logs de génération d'image sur Streamlit Cloud

## ✅ Solution pour voir les logs

### Étape 1: Aller aux logs Streamlit Cloud

1. Ouvrez votre app sur https://share.streamlit.io/
2. **Attendez que l'app se charge complètement** (l'app peut être en "sleeping" mode)
3. Cherchez **Settings** (⚙️) en haut à droite → cliquez
4. Cliquez sur l'onglet **Logs** (en bas)

### Étape 2: Générer une image

1. Fermez le menu Settings
2. Générez une recette IA
3. Cliquez sur "🎨 Générer l'image"
4. **Attendez 5-10 secondes**
5. Retournez aux **Logs** pour voir ce qui s'est passé

## 🔍 Que chercher dans les logs

### ✅ Si ça marche:
```
============================================================
🖼️  IMAGE GENERATOR INITIALIZED
============================================================
✅ Unsplash:  CONFIGURED uc_XXXXX...
✅ Pexels:    NOT SET ...
✅ Pixabay:   NOT SET ...
============================================================

🎨 APPEL generer_image_recette: Fromage blanc
  → Essai Unsplash...
  🔍 Recherche Unsplash: 'Fromage blanc recipe dish food'
  📊 Unsplash trouvé 5 résultats
  ✅ Image sélectionnée: White cheese...
  ✅ SUCCESS Unsplash!
```

### ❌ Si Unsplash échoue:
```
✅ Unsplash:  NOT SET ...
```
→ **Votre clé Unsplash n'est pas configurée dans Streamlit Cloud**

Solution: Settings → Secrets → Ajouter `[unsplash] api_key = "..."`

### ❌ Si Unsplash est configuré mais ne fonctionne pas:
```
✅ Unsplash:  CONFIGURED uc_XXXXX...

🎨 APPEL generer_image_recette: Fromage blanc
  → Essai Unsplash...
  ❌ Unsplash error: 401 Unauthorized
```
→ **Votre clé est invalide ou expirée**

Solution: Créer une nouvelle clé sur https://unsplash.com/oauth/applications

## 📊 Messages de debug visibles dans l'app

L'app affiche aussi directement:
- ✅ État des clés configurées
- 📋 Nombre d'ingrédients trouvés
- 🔍 Recherche en cours
- ✅ Image générée avec succès
- ❌ Les erreurs détaillées

## 🆘 Pas de logs du tout?

Si vous ne voyez **aucun** log même après avoir cliqué sur le bouton:

1. Attendez 30 secondes (l'app peut être en "sleeping")
2. Vérifiez que l'app redémarre bien après sauvegarder les secrets
3. Rafraîchissez la page (Ctrl+F5)
4. Essayez de redéployer:
   ```bash
   git add .
   git commit -m "Force redeploy"
   git push origin main
   ```

## 💡 Conseil

Le plus fiable pour déboguer: **Regardez les messages d'erreur/succès affichés directement dans l'app** avant d'aller dans les Logs!
