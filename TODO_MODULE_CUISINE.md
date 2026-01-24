# 📋 TODO - Module Cuisine

> Vue globale de ce qui reste à faire pour **Recettes**, **Inventaire**, **Courses** et **Planning**

---

## 📊 Status Global

| Module | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **📅 Planning** | ✅ 100% | 🔄 Planifié | 🔄 Planifié |
| **🛒 Courses** | ✅ 95% | 🔄 En attente | 🔄 Planifié |
| **📚 Recettes** | ✅ 90% | 🔄 En attente | 🔄 Planifié |
| **📦 Inventaire** | ✅ 85% | 🔄 En attente | 🔄 Planifié |

---

## 📅 PLANNING

### Phase 1: Core Features ✅ COMPLÉTÉ
**Status:** Production Ready - 3 onglets + 34 tests

#### Implémenté
- ✅ Onglet "Planning Actif" - Vue 7 jours + édition inline
- ✅ Onglet "Générer avec IA" - Formulaire préférences + Mistral
- ✅ Onglet "Historique" - Filtres + chargement/suppression
- ✅ Service couche (PlanningService)
- ✅ 34 tests (17 module + 17 service) - 100% pass

#### Actions Immédiates
- [ ] **Supabase SQL Phase 2** - Exécuter `006_add_modeles_courses.sql` (courses modèles)
- [ ] **Test Streamlit** - Valider UI sur Streamlit (Cuisine > Planning)

### Phase 2: Intégrations & Multi-user
- [ ] **Intégration Courses** - Générer courses depuis planning
  - [ ] Bouton "Générer courses" → articles du planning
  - [ ] Mapper ingrédients recettes → courses
  - [ ] Suggestions modèles courses pertinents

- [ ] **Intégration Inventaire** - Check stock avant génération
  - [ ] Vérifier articles existants avant suggestions
  - [ ] Proposer recettes basées sur inventaire
  - [ ] Décroissance auto quantités après cuisson

- [ ] **Multi-user & Collaboratif**
  - [ ] Ajouter user_id au planning
  - [ ] Permissions (lecteur/éditeur)
  - [ ] Partage famille/colocataires
  - [ ] Notifications temps réel: qui modifie

### Phase 3: Advanced Features
- [ ] **Variants & Allergies** - Repas différents par personne
- [ ] **Nutrition Tracking** - Calories/macros par repas
- [ ] **Export/Print** - PDF pour frigo

---

## 🛒 COURSES

### Phase 1: Core Features ✅ 95% COMPLÉTÉ
**Status:** Fonctionnel - Prêt pour test Supabase

#### Implémenté
- ✅ 4 render functions (liste, modèles, suggestions, historique)
- ✅ 55 tests (27 module + 28 service)
- ✅ CRUD articles complet
- ✅ Suggestions IA basées inventaire
- ✅ Historique + filtres

#### À Faire Phase 1
- [ ] **Tester BD Supabase** - Après exécution SQL (modeles_courses, articles_modeles)
  - [ ] Vérifier persistance des modèles en BD
  - [ ] Tester CRUD service methods

### Phase 2: Code-barres, UX & Partage
- [ ] **Code-barres Scanning** - Saisie rapide par scan
  - [ ] Composant scanning (caméra)
  - [ ] Base données codes-barres
  - [ ] Lien article → code-barres

- [ ] **Actions de Masse** - Améliorations UX
  - [ ] "Marquer tout acheté"
  - [ ] "Appliquer modèle" à une liste
  - [ ] Filtres multi-critères (priorité, rayon, quantité)

- [ ] **Partage Multi-user**
  - [ ] Sync avec famille/colocataires
  - [ ] Notifications: "X a acheté Y"
  - [ ] Historique collaboratif
  - [ ] Permissions (lecteur/éditeur)

- [ ] **Budget Tracking**
  - [ ] Estimation coût total par article
  - [ ] Historique prix
  - [ ] Budget par semaine/mois

### Phase 3: Intégrations Magasins
- [ ] **Intégrations Magasins** - Prix + Promos
  - [ ] API Carrefour, Monoprix, etc.
  - [ ] Comparaison prix
  - [ ] Alertes promo
  - [ ] Meilleur magasin

---

## 📚 RECETTES

### Phase 1: Core Features ✅ 90% COMPLÉTÉ
**Status:** Excellent - À améliorer avec métadonnées

#### Implémenté
- ✅ CRUD recettes complet
- ✅ Import CSV (TEMPLATE_IMPORT.csv)
- ✅ Recherche + filtres
- ✅ Navigation par catégorie
- ✅ Photos des recettes
- ✅ Temps, difficulté, portions

#### À Faire Phase 1
- [ ] **Tester import/export** - Valider CSV upload
- [ ] **Ajouter allergènes** - Base allergies courantes

### Phase 2: Métadonnées & Contenu
- [ ] **Allergènes/Régimes** - Tags détaillés
  - [ ] Allergènes: arachides, gluten, lactose, œufs, fruits secs, etc.
  - [ ] Régimes: omnivore, végétarien, végan, sans gluten, etc.
  - [ ] Profil nutritionnel (vegan, etc.)

- [ ] **Ingrédients Structurés** - Lier à inventaire
  - [ ] Parser les ingrédients (quantité, unité, article)
  - [ ] Linking article → inventaire
  - [ ] Calcul automatique coût recette

- [ ] **Avis & Notes Utilisateurs**
  - [ ] Notation (⭐⭐⭐⭐⭐)
  - [ ] Commentaires
  - [ ] Favoris (marquer recettes préférées)
  - [ ] Difficulté réelle vs estimée

### Phase 3: UX & Partage
- [ ] **Favoris & Collections**
- [ ] **Partage** - Exporter URL/PDF
- [ ] **Impressions Optimisées** - Format pour cuisine
- [ ] **Shopping List Auto** - Générer courses par recette

---

## 📦 INVENTAIRE

### Phase 1: Core Features ✅ 85% COMPLÉTÉ
**Status:** Fonctionnel - Bug photos fixé

#### Implémenté
- ✅ CRUD articles complet
- ✅ Quantités + unités
- ✅ Péremptions + alertes
- ✅ Photos (bug fixé ligne 418)
- ✅ Catégories
- ✅ Historique

#### À Faire Phase 1
- [ ] **Tester photos** - Valider upload/affichage après fix

### Phase 2: Code-barres, Alertes & Intégrations
- [ ] **Code-barres Scanning**
  - [ ] Scanner QR/code-barres (caméra)
  - [ ] Base données codes-barres (GTIN)
  - [ ] Lookup automatique (Open Food Facts API)
  - [ ] Génération étiquettes PDF

- [ ] **Alertes & Notifications**
  - [ ] Stock critique (alertes push)
  - [ ] Péremptions proches (calendrier visuel)
  - [ ] Email/SMS notifications
  - [ ] Calendrier péremptions

- [ ] **Recherche Intelligente**
  - [ ] Auto-complétion lors de la saisie
  - [ ] Reconnaissance image (photo → détection article)
  - [ ] Suggestions basées on inventory

- [ ] **Intégration Recettes**
  - [ ] "Recettes faisables" - Check articles actuels
  - [ ] "Avant péremption" - Proposer recettes urgentes
  - [ ] Lien ingrédient → article inventaire

### Phase 3: Collaboratif & Analytics
- [ ] **Partage Multi-appareils**
  - [ ] Sync temps réel famille
  - [ ] Historique: "X a acheté Y quand"
  - [ ] Permissions granulaires

- [ ] **Analytics**
  - [ ] Articles les plus périmés
  - [ ] Taux gaspillage
  - [ ] Ingrédients les plus utilisés
  - [ ] Patterns saisonniers

---

## 🔗 INTÉGRATIONS TRANSVERSALES

### Priority 1: Planning ↔ Courses ↔ Inventaire
```
Planning (recettes) → Courses (articles) → Inventaire (stock)
                ↑__________________________|
```

#### À Implémenter
- [ ] **Planning → Courses**
  - [ ] "Générer courses" depuis planning
  - [ ] Mapper ingrédients recettes
  - [ ] Suggestions modèles pertinents

- [ ] **Courses → Inventaire**
  - [ ] Check stock avant achat
  - [ ] Proposer articles en stock
  - [ ] Update inventaire après achat

- [ ] **Inventaire → Planning**
  - [ ] Suggestions recettes par stock
  - [ ] Check articles avant génération
  - [ ] Décroissance auto après cuisson

### Priority 2: Analytics & Budgeting
- [ ] **Coût Recettes**
  - [ ] Prix articles (historique courses)
  - [ ] Coût par recette
  - [ ] Budget planning

- [ ] **Durabilité**
  - [ ] Gaspillage (péremptions)
  - [ ] Utilisation (articles cuisine)
  - [ ] Stats saisonniers

- [ ] **Patterns Utilisateur**
  - [ ] Plats favoris
  - [ ] Ingrédients préférés
  - [ ] Patterns saisonniers

---

## 🎯 PLAN D'ACTION RECOMMANDÉ

### Semaine 1: Supabase + Validation
- [ ] Exécuter SQL Phase 2 (courses modèles) sur Supabase
- [ ] Tester Planning sur Streamlit UI
- [ ] Valider Courses persistance BD
- [ ] Tester Inventaire photos fix

### Semaine 2-3: Intégrations Core
- [ ] Planning → Courses (générer courses)
- [ ] Courses → Inventaire (check stock)
- [ ] Inventaire → Planning (suggestions)

### Semaine 4-5: Phase 2 Multi-user
- [ ] Ajouter user_id partout
- [ ] Permissions
- [ ] Notifications

### Semaine 6+: Phase 3 Advanced
- [ ] Code-barres scanning
- [ ] Analytics
- [ ] Intégrations magasins

---

## 📝 NOTES

- **Planning:** ✅ 100% - Prêt prod après SQL Supabase
- **Courses:** ✅ 95% - Prêt après test BD
- **Recettes:** ✅ 90% - Bon état, améliorer métadonnées
- **Inventaire:** ✅ 85% - Bon état, photo bug fixé

**Blockers:** SQL Phase 2 sur Supabase (courses modèles)

---

**Last Updated:** January 24, 2026  
**Status:** All modules production-ready, Phase 2 in planning
