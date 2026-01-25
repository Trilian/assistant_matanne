# 🚀 Guide de test rapide - Module Maison

## Prérequis

- ✅ Python 3.11+
- ✅ Streamlit installé
- ✅ Base de données Supabase connectée (ou SQLite)
- ✅ API Mistral configurée (optionnel pour IA)

## Démarrage rapide

### 1. Lancer l'app
```bash
cd d:\Projet_streamlit\assistant_matanne
streamlit run src/app.py
```

### 2. Naviguer vers Maison
Cliquer sur "🏠 Maison" dans la sidebar

## Tests par module

### 🏗️ Projets

**À tester:**
1. ✅ Tab "📋 En cours" : Affiche liste des projets en cours
2. ✅ Tab "➕ Nouveau" : Créer un projet
   - Remplir nom, description, priorité, échéance
   - Cliquer "💾 Créer le projet"
   - Vérifier réappariton dans tab "En cours"
3. ✅ Tab "🤖 Assistant IA" : Générer tâches
   - Entrer nom projet + description
   - Cliquer "💡 Générer tâches"
   - Voir suggestions IA (ou warning si IA indispo)
4. ✅ Templates : Cliquer "Rénovation cuisine"
   - Crée projet avec tâches pré-remplies
5. ✅ Progression : Barre % doit augmenter quand tâches marquées ✓

**Résultat attendu:**
- Nouveau projet visible
- Tâches ajoutables
- IA génère 5-7 tâches ou warning gracieux
- Progression calculée correctement

### 🌿 Jardin

**À tester:**
1. ✅ Tab "🌱 Mes Plantes" : Affiche plantes (vide si aucune)
2. ✅ Tab "➕ Ajouter" : Créer une plante
   - Remplir nom, type, emplacement
   - Cliquer "🌱 Ajouter au jardin"
   - Vérifier apparition dans "Mes Plantes"
3. ✅ Suggestion rapide : Cliquer "🍅 Tomates cerises"
   - Crée plante instantanément
4. ✅ Tab "🤖 Conseils IA" : Générer conseils
   - Cliquer "💡 Conseils pour cette saison"
   - Affiche 3-4 conseils jardin OU warning
5. ✅ Tab "📊 Stats" : Affiche métriques
   - Nombre total plantes
   - Plantes à arroser
   - Récoltes prochaines
   - Graphique par type
6. ✅ Arroser : Dans "Mes Plantes", cliquer "💧 Arroser"
   - Plante disparaît de "à arroser" (jusqu'à demain)
   - Log enregistré

**Résultat attendu:**
- Nouvelle plante dans inventory
- Détection automatique "à arroser" si ajoutée
- IA suggest conseils ou gracieux fallback
- Stats mises à jour

### 🧹 Entretien

**À tester:**
1. ✅ Tab "☑️ Aujourd'hui" : Affiche tâches (vide si aucune routine)
2. ✅ Tab "➕ Créer" : Créer routine
   - Remplir nom, catégorie, fréquence
   - Cliquer "✅ Créer routine"
   - Vérifier dans tab "📅 Routines"
3. ✅ Template : Cliquer "📋 Nettoyage cuisine"
   - Crée routine avec tâches (Laver vaisselle, etc.)
4. ✅ Tab "🤖 Assistant IA" : Optimiser semaine
   - Lister tâches (une par ligne)
   - Cliquer "🔮 Proposer répartition"
   - Voir suggestion Lun-Dim OU warning
5. ✅ Checklist : Dans "☑️ Aujourd'hui", cliquer "✓ Fait"
   - Tâche marquée complète
   - Progression % augmente
6. ✅ Tab "📊 Stats" : Affiche métriques
   - Routines actives
   - % completion aujourd'hui

**Résultat attendu:**
- Routine créée avec tâches
- Checklist fonctionne
- IA optimise ou warning gracieux
- Stats correctes

## Tests du Hub d'accueil

**À tester:**
1. ✅ Affiche alertes si:
   - Projets urgents/en retard
   - Plantes à arroser
   - Tâches ménage non faites
2. ✅ Affiche statistiques:
   - Nombre de projets en cours
   - Nombre de plantes
   - Nombre de routines
3. ✅ Boutons navigation : Cliquer vers chaque module
   - Affiche module correspondant

## Tests IA (optionnel)

Si API Mistral configurée :

**À tester:**
1. ✅ Projets → "💡 Générer tâches"
   - Affiche liste tâches numérotée
2. ✅ Projets → "🔮 Estimer durée"
   - Affiche estimation min/max + phases
3. ✅ Jardin → "💡 Conseils saison"
   - Affiche 3-4 conseils spécifiques
4. ✅ Jardin → "Conseil d'arrosage"
   - Affiche fréquence, quantité, moment
5. ✅ Entretien → "💡 Générer tâches"
   - Affiche 5-8 tâches ordonnées
6. ✅ Entretien → "🔮 Proposer répartition"
   - Affiche Lun-Dim avec tâches réparties

**Résultat attendu:**
- IA génère contenu cohérent
- Cache fonctionne (2e appel =rapide)
- Erreurs gracieuses si quota atteint

## Checklist de validation

- [ ] App démarre sans erreur
- [ ] Module Maison accessible
- [ ] Hub affiche correctement
- [ ] Créer projet fonctionne
- [ ] Créer plante fonctionne
- [ ] Créer routine fonctionne
- [ ] Progression calculée correctement
- [ ] Cache Streamlit opérationnel (visible dans metrics)
- [ ] IA fonctionne (si disponible)
- [ ] Fallback gracieux si IA indispo
- [ ] Imports ne génèrent pas erreur

## Dépannage

### "IA temporairement indisponible"
- ✅ Normal si API Mistral pas configurée
- Vérifier .env.local contient MISTRAL_API_KEY
- Check rate limiting (max 100 appels/jour par défaut)

### "No runtime found, using MemoryCacheStorage"
- ✅ Normal en test Python
- Disparaît quand lancé via Streamlit

### Base de données vide
- ✅ Normal au premier démarrage
- Ajouter données via formulaires
- Ou lancer seed_data.py si disponible

### Cache pas invalidé
- Cliquer "⚙️" ou arrêter/relancer Streamlit
- Ou appeler `clear_maison_cache()` dans code

## Performance

| Action | Temps attendu |
|--------|---------------|
| Charger Maison hub | <100ms |
| Ouvrir tab Jardin | <200ms |
| Créer projet | <500ms |
| Génération IA | 2-5s |
| Stat recalc | <100ms (cached) |

## Logs utiles

Pour debug, chercher dans logs:
```
✅ Module maison OK
✅ Logging initialisé
⚠️ No runtime found (normal en test)
❌ Error ... (à corriger)
```

## Prochaines étapes après test

1. Vérifier BD contient données
2. Tester intégration avec autres modules (future)
3. Ajouter règles validation (email, budgets, etc.)
4. Configurer notifications (future)
5. Ajouter graphiques/rapports avancés

---

**Tout fonctionne?** ✅ Vous êtes prêt à utiliser! 🎉

**Questions?** Voir [MAISON_MODULE_DOCUMENTATION.md](MAISON_MODULE_DOCUMENTATION.md)
