# TODO - Améliorations Inventaire & Recettes & Courses

## 📋 Courses

### Phase 2: Persistance & Modèles
- [ ] **Modèles persistants en BD** ✅ FAIT - Sauvegarde en BD au lieu de session state
  - ✅ Tables modeles_courses + articles_modeles créées
  - ✅ Service: get_modeles(), create_modele(), delete_modele(), appliquer_modele()
  - ✅ UI refactorisée avec BD persistant
  - [ ] Tester après création tables Supabase

### Phase 2: Code-barres & UX
- [ ] **Scanning code-barres** - Saisie rapide article par scan
  - Structure: Tab "Code-barres" prête dans render_outils()
  - Nécessite: Composant scanning + base données codes-barres
  
- [ ] **Actions de masse** - Marquer tout acheté, appliquer modèle
  - ✅ Structure prête (boutons dans render_liste_active)
  - Nécessite: Implémentation complète

- [ ] **Filtres avancés** - Tri par priorité/rayon/quantité
  - ✅ Filterss basiques existants
  - [ ] Tri multi-critères + sauvegarde préférences

### Phase 2: Partage & Multi-user
- [ ] **Partage multi-utilisateurs** - Lister avec famille/colocataires
  - Structure: Tab "Partage" prête dans render_outils()
  - Nécessite: user_id depuis auth Supabase
  - Nécessite: Permissions (lecteur/éditeur)
  - Nécessite: Notifications temps réel (qui achète quoi)

### Phase 3: Intégrations
- [ ] **Intégration Recettes** - Suggestions articles par recettes planifiées
  - Structure prête dans render_suggestions_ia() (onglet recettes)
  - Nécessite: Linking recette → ingrédients → courses

- [ ] **Budget tracking** - Estimation coût total
  - Structure: Stats tab avec "Budget tracking (Phase 2)"
  - Nécessite: Prix par article en BD
  - Nécessite: Historique achats + prix

- [ ] **Intégrations magasins** - Comparaison prix, promo
  - Nécessite: API partenaires (Carrefour, etc.)
  - Nécessite: Base données prix par magasin

---

## 🍽️ Recettes

### Intégration & Synchronisation
- [ ] **Intégration Inventaire** - Décroissance automatique des ingrédients après cuisson
- [ ] **Suggestions par inventaire** - Proposer recettes basées sur articles en stock
- [ ] **Planification hebdomadaire** - Menus auto-générés

### Contenu & Métadonnées
- [ ] **Allergènes/régimes** - Tags pour allergies, végétariens, végan, sans gluten
- [ ] **Commentaires/notes** - Feedback utilisateur sur recettes
- [ ] **Évaluations** - Notes/avis utilisateurs

### UX & Features
- [ ] Favoris (marquer recettes favorites)
- [ ] Impressions optimisées
- [ ] Partage recettes (URL, PDF)
- [ ] Notation recettes par difficulté réelle (vs estimée)

---

## 📦 Inventaire

### Capture & Saisie
- [ ] **Code-barres** 🔲 - Scanner code-barres pour ajouter articles rapidement
- [ ] **Reconnaissance image** - Photo → détection automatique article
- [ ] **Recherche auto-complétion** - Suggestions lors de la saisie

### Notifications & Alertes
- [ ] **Notifications en temps réel** - Alertes push stock critique
- [ ] **Email/SMS** pour alertes importantes
- [ ] **Calendrier d'alertes** - Vue calendrier des péremptions

### Intégration Recettes
- [ ] **Recettes utilisables** - Afficher recettes faisables avec articles actuels
- [ ] **Décroissance auto** - Réduction auto des quantités après cuisson
- [ ] **Suggestion préparation** - Proposer recettes avant péremption

### Collaboratif
- [ ] **Partage multi-appareils** - Sync liste courses avec famille/colocataires
- [ ] **Historique collaboratif** - Qui a acheté quoi et quand
- [ ] **Permissions** - Lecture/écriture granulaire

### Export & Intégrations
- [ ] **Codes-barres en PDF** - Générer étiquettes stock
- [ ] **Intégration recettes** - Lister ingrédients manquants par recette
- [ ] **Rappel shoppinglist** - Export pour appli shopping externe

---

## 🔗 Intégrations Transversales (Recettes ↔ Inventaire ↔ Courses)

- [ ] **Workflow complet** : Recette → Courses → Inventaire → Cuisson
- [ ] **Analytics croisées** - Plats préférés vs ingrédients les plus utilisés
- [ ] **Budgeting** - Coût recettes basé sur prix inventaire + courses
- [ ] **Durabilité** - Stats gaspillage vs utilisation

---

**Priorité : Intégration Recettes ↔ Inventaire ↔ Courses pour créer boucle fermée**


### Intégration & Synchronisation
- [ ] **Intégration Inventaire** - Décroissance automatique des ingrédients après cuisson
- [ ] **Suggestions par inventaire** - Proposer recettes basées sur articles en stock
- [ ] **Planification hebdomadaire** - Menus auto-générés

### Contenu & Métadonnées
- [ ] **Allergènes/régimes** - Tags pour allergies, végétariens, végan, sans gluten
- [ ] **Commentaires/notes** - Feedback utilisateur sur recettes
- [ ] **Évaluations** - Notes/avis utilisateurs

### UX & Features
- [ ] Favoris (marquer recettes favorites)
- [ ] Impressions optimisées
- [ ] Partage recettes (URL, PDF)
- [ ] Notation recettes par difficulté réelle (vs estimée)

---

## 📦 Inventaire

### Capture & Saisie
- [ ] **Code-barres** 🔲 - Scanner code-barres pour ajouter articles rapidement
- [ ] **Reconnaissance image** - Photo → détection automatique article
- [ ] **Recherche auto-complétion** - Suggestions lors de la saisie

### Notifications & Alertes
- [ ] **Notifications en temps réel** - Alertes push stock critique
- [ ] **Email/SMS** pour alertes importantes
- [ ] **Calendrier d'alertes** - Vue calendrier des péremptions

### Intégration Recettes
- [ ] **Recettes utilisables** - Afficher recettes faisables avec articles actuels
- [ ] **Décroissance auto** - Réduction auto des quantités après cuisson
- [ ] **Suggestion préparation** - Proposer recettes avant péremption

### Collaboratif
- [ ] **Partage multi-appareils** - Sync liste courses avec famille/colocataires
- [ ] **Historique collaboratif** - Qui a acheté quoi et quand
- [ ] **Permissions** - Lecture/écriture granulaire

### Export & Intégrations
- [ ] **Codes-barres en PDF** - Générer étiquettes stock
- [ ] **Intégration recettes** - Lister ingrédients manquants par recette
- [ ] **Rappel shoppinglist** - Export pour appli shopping externe

---

## 🔗 Intégrations Transversales (Recettes ↔ Inventaire)

- [ ] **Workflow complet** : Recette → Courses → Inventaire → Cuisson
- [ ] **Analytics croisées** - Plats préférés vs ingrédients les plus utilisés
- [ ] **Budgeting** - Coût recettes basé sur prix inventaire
- [ ] **Durabilité** - Stats gaspillage vs utilisation

---

**Priorité : Intégration Inventaire ↔ Recettes pour créer boucle fermée**
