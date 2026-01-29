# Tests - Fixes Module Courses

## Problèmes Fixés

### 1. ✅ Ajouter ingrédients manquants pour recettes
**Problème:** La fonctionnalité "Ajouter ingrédients manquants" dans l'onglet "🍽️ Par recettes" n'était pas implémentée.

**Fix:**
- Implémentation complète du bouton "🔍 Ajouter ingrédients manquants"
- Récupère les ingrédients de la recette sélectionnée
- Crée les ingrédients s'ils n'existent pas dans la BD
- Ajoute chaque ingrédient à la liste de courses avec:
  - Quantité depuis la recette
  - Priorité: "moyenne"
  - Rayon: "Autre"
  - Notes: "Pour [nom recette]"

**Code modifié:** `src/domains/cuisine/ui/courses.py` lignes 471-530

---

### 2. ✅ Sélectionner une recette (depuis module courses)
**Problème:** Le selectbox pour choisir une recette causait une erreur car il était défini sans clé unique.

**Fix:**
- Ajout de `key="select_recette_courses"` au selectbox
- Ajout de `key="btn_add_missing_ingredients"` au bouton
- Évite les conflits de clé avec d'autres modules

**Code modifié:** `src/domains/cuisine/ui/courses.py` ligne 491

---

### 3. ✅ Impossible d'ajouter des courses manuellement
**Problème:** Le formulaire "➕ Ajouter un article" utilisait `next(obtenir_contexte_db())` qui pouvait échouer.

**Fix:**
- Changement de `next(obtenir_contexte_db())` à `with obtenir_contexte_db() as db:`
- Ajout de `db.flush()` et `db.refresh(ingredient)` pour garantir l'ID
- Passage correct de `ingredient_id` au service
- Meilleure gestion des erreurs avec traceback

**Code modifié:** `src/domains/cuisine/ui/courses.py` lignes 328-366

---

## Tests Manuels à Faire

### Test 1: Ajouter un article manuellement
1. Ouvrir module 🛍 Courses
2. Onglet "📋 Liste Active"
3. Bouton "➕ Ajouter article"
4. Remplir: Nom="Tomates", Unité="kg", Quantité=2, Priorité="haute", Rayon="Fruits/Légumes"
5. ✅ Devrait afficher "✅ Tomates ajouté à la liste!"
6. Article devrait apparaître dans la liste

### Test 2: Ajouter ingrédients d'une recette
1. Onglet "✨ Suggestions IA"
2. Tab "🍽️ Par recettes"
3. Sélectionner une recette
4. Cliquer "🔍 Ajouter ingrédients manquants"
5. ✅ Devrait afficher "✅ X ingrédient(s) ajouté(s) à la liste!"
6. Articles devraient apparaître avec notes "Pour [recette]"

### Test 3: Gestion des erreurs
1. Essayer d'ajouter un article sans nom
2. ✅ Devrait afficher "⚠️ Entrez un nom d'article"
3. Essayer d'ajouter des ingrédients depuis une recette vide
4. ✅ Devrait afficher "Aucun ingrédient dans cette recette"

---

## Vérification des Logs

Quand DEBUG=True dans .env.local, vous devriez voir:
```
✅ Tomates ajouté à la liste!
✅ 3 ingrédient(s) ajouté(s) à la liste!
```

Si erreur, vérifier:
- `st.session_state.courses_refresh` doit incrémenter
- `st.rerun()` déclenche le rafraîchissement
- Les IDs d'ingrédients sont bien assignés

---

## Changements de Code Résumé

| Fichier | Lignes | Changement |
|---------|--------|-----------|
| courses.py | 328-366 | Fix `next(obtenir_contexte_db())` → `with obtenir_contexte_db()` |
| courses.py | 471-530 | Implémentation complète "Ajouter ingrédients manquants" |
| courses.py | 491 | Ajout key="select_recette_courses" |

**Total:** 3 fixes critiques - tous les problèmes résoluent
