# 🏠 Guide de Test - Module Famille Refondé

## ✅ Checklist de Démarrage

### 1. **Démarrer l'app**
```bash
cd /workspaces/assistant_matanne
streamlit run src/app.py
```

### 2. **Aller au Module Famille**
- Menu latéral: `👨‍👩‍👧‍👦 Famille`
- Cliquer: `🏠 Hub Famille` (nouvelle option)
- Devrait afficher la page d'accueil avec 4 boutons

---

## 🧪 Tests par Section

### **A. Hub Famille (Accueil)**
✅ **À tester:**
- [ ] Page charge sans erreur
- [ ] Voir 4 boutons: Jules / Santé / Activités / Shopping
- [ ] Stats affichées: Jules (19m), Activités (0 semaine), Séances (0), Budget (0€)
- [ ] Cliquer chaque bouton navigue vers la section

**Attendu:**
- Page d'accueil avec navigation claire
- Métriques à jour

---

### **B. Jules (19 mois)**

#### **Onglet 1: Jalons**
✅ **À tester:**
1. Cliquer `➕ Ajouter un jalon`
2. Remplir:
   - Titre: "Premier mot 'maman'"
   - Catégorie: "Langage"
   - Date: Aujourd'hui
   - Description: "A dit clairement 'maman' ce matin!"
3. Cliquer `💾 Sauvegarder`

**Attendu:**
- ✅ Success message "Jalon 'Premier mot 'maman'' enregistré!"
- 🎉 Balloons animation
- Jalon apparaît dans la section "Langage" en-dessous

#### **Onglet 2: Activités**
✅ **À tester:**
1. Voir 8 activités recommandées (Blocs, Ballon, Peinture, etc.)
2. Cliquer `📅 Planifier` sur une activité
3. Voir "✅ Planifier une activité" en haut
4. Remplir formulaire et cliquer `📅 Ajouter`

**Attendu:**
- Success message
- Activité listé dans "Activités planifiées"

#### **Onglet 3: À Acheter**
✅ **À tester:**
1. Voir catégories: Jouets, Vêtements, Repas
2. Voir articles pré-remplis
3. Cliquer `➕ Courses` sur un article

**Attendu:**
- Article "ajouté aux courses"
- (Intégration future avec module Courses)

---

### **C. Santé & Sport**

#### **Haut de page**
✅ **À tester:**
- [ ] Voir 4 métriques: Séances (0), Minutes (0), Calories (0), Moral (—)

#### **Onglet 1: Routines Sport**
✅ **À tester:**
1. Cliquer `➕ Nouvelle routine`
2. Remplir:
   - Nom: "Yoga le matin"
   - Type: "Yoga"
   - Fréquence: "3x/semaine"
   - Durée: 30 minutes
   - Intensité: "Modérée"
   - Jours: Lundi, Mercredi, Vendredi
3. Cliquer `💾 Créer`

**Attendu:**
- Success + Balloons
- Routine affichée avec bouton `✅ Fait` et `🗑️`

#### **Onglet 2: Objectifs**
✅ **À tester:**
1. Cliquer `➕ Nouvel objectif`
2. Remplir:
   - Titre: "Courir 5km"
   - Catégorie: "Endurance"
   - Valeur cible: 5
   - Unité: "km"
   - Date cible: Dans 3 mois
3. Cliquer `💾 Créer`

**Attendu:**
- Objectif affiché avec barre de progression (0%)

#### **Onglet 3: Suivi**
✅ **À tester:**
- [ ] Onglet se charge (vide jusqu'à avoir séances)
- [ ] Message "Aucune séance enregistrée"

#### **Onglet 4: Alimentation**
✅ **À tester:**
- [ ] Voir principes à manger/modérer
- [ ] Lien vers "Voir recettes saines"
- [ ] Lien vers "Planifier une semaine saine"

---

### **D. Activités Familiales**

#### **Planning Semaine**
✅ **À tester:**
1. Cliquer `➕ Planifier une activité`
2. Remplir:
   - Titre: "Parc dimanche"
   - Type: "Parc"
   - Date: Dimanche prochain
   - Durée: 1.5h
   - Lieu: "Parc de la ville"
   - Qui: Jules, Maman, Papa
   - Coût estimé: 0€
3. Cliquer `📅 Ajouter`

**Attendu:**
- Success message
- Activité listée "📅 Dimanche XX/XX"

#### **Idées d'Activités**
✅ **À tester:**
1. Expander "Parc"
2. Voir "Jeux au parc", "Pique-nique"
3. Cliquer `📅 Planifier` sur une
4. Devrait pré-remplir et ajouter

**Attendu:**
- Nouvelle activité dans Planning

#### **Budget**
✅ **À tester:**
- [ ] Sélectionner mois courant
- [ ] Voir tableau et graphique
- [ ] Si activités ajoutées, voir dans tableau

---

### **E. Shopping Famille**

#### **Liste de Shopping**
✅ **À tester:**
1. Cliquer `➕ Ajouter un article`
2. Remplir:
   - Article: "Blocs Duplo"
   - Catégorie: "Jules - Jouets"
   - Quantité: 1
   - Prix: 30€
3. Cliquer `➕ Ajouter à la liste`

**Attendu:**
- Article ajouté
- Voir dans liste "Jules - Jouets"

#### **Idées Suggérées**
✅ **À tester:**
1. Expander "Jules - Jouets"
2. Voir Duplo, Balles, Livres, etc.
3. Cliquer `➕ Ajouter`

**Attendu:**
- Ajouté à liste avec prix pré-rempli

#### **Suivi Budget**
✅ **À tester:**
- [ ] Voir graphique dépenses par catégorie
- [ ] Voir tableau résumé
- [ ] Budget total = somme prix articles

---

## 🐛 Checks Techniques

### **Base de Données**
```bash
# Vérifier tables créées
sqlite3 app.db ".tables" | grep -E "milestone|health|family_activity|family_budget"

# Vérifier migrations OK
python -c "from src.core.database import get_db_context; print('✅ DB OK')"
```

### **Imports**
```bash
# Tester imports modules
python -c "from src.modules.famille import jules, sante, activites, shopping; print('✅ All imports OK')"
```

### **Navigation**
- [ ] Menu latéral affiche tous les sous-modules
- [ ] Cliquer chaque bouton navigue sans erreur
- [ ] Bouton actif est grisé (disabled)
- [ ] Appuyer sur "retour" revient au hub

---

## 💡 Cas d'Usage Complets

### **Scenario 1: Ajouter un jalon et planifier activité**
1. Jules → Jalons → Ajouter "Premiers pas" 
2. Jules → Activités → Planifier "Jeux parc"
3. Activités → Voir l'activité planifiée
4. Voir Jules et activité sur Hub

**Attendu:** Tout interconnecté ✅

### **Scenario 2: Créer routine et tracker**
1. Santé → Routines → Créer "Gym 3x/semaine"
2. Cliquer `✅ Fait` sur routine
3. Remplir effort (durée, intensité, calories)
4. Suivi → Voir entrée enregistrée
5. Hub → Voir stat "1 séance cette semaine" 

**Attendu:** Tracking complet ✅

### **Scenario 3: Planifier budget**
1. Shopping → Ajouter 5 articles (30€ total)
2. Activités → Planifier sortie (20€)
3. Shopping → Budget → Voir 50€ total
4. Activités → Budget → Voir 20€ activités

**Attendu:** Budget suivi par catégorie ✅

---

## 📊 Performance

- [ ] App charge en < 5 secondes
- [ ] Navigation < 1 sec
- [ ] Formulaires soumis rapidement
- [ ] Pas d'erreurs console (Ctrl+Shift+I)

---

## 🎨 Cosmétique

- [ ] Emojis affichés correctement
- [ ] Layout responsive
- [ ] Couleurs coher entes
- [ ] Textes lisibles

---

## 📝 Feedback

Pour chaque section, noter:
- ✅ Fonctionne?
- 🐛 Bugs?
- 💡 Améliorations?
- 🎯 Manque quoi?

**Exemple:**
```
## Jules - Jalons
✅ Ajouter jalon: OK
🐛 Photos upload: Pas testé
💡 Aimer avoir date automatique
🎯 Besoin: Supprimer jalon
```

---

**Bon test! 🚀**
