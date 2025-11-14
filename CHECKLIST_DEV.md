# 📝 Checklist de développement – Assistant Familial

## 🧱 1. Fondations et base de données
- [ ] Vérifier les relations entre les tables (`repas`, `routines`, `projets`, `tâches`, `liens_intelligents`)
- [ ] Ajouter les champs d’**archivage doux** (`is_archived`, `archived_at`)
- [ ] Créer les vues ORM / requêtes pour :
    - [ ] Charge globale (routines + tâches + sommeil)
    - [ ] Suggestions croisées entre modules
- [ ] Tester la création/suppression d’un utilisateur et la cohérence de ses modules

---

## 🎨 2. Interface Streamlit
- [ ] Layout principal : sidebar + navigation multi-modules
- [ ] Page Accueil :
    - [ ] Dashboard résumé du jour
    - [ ] Indicateur de charge mentale visuel (fleur / thermomètre)
    - [ ] Widget météo
- [ ] Pages modules :
    - [ ] **Routines** : tableau, boutons ajout/pause/archive
    - [ ] **Repas & Batch Cooking** : calendrier, liste de courses, recettes
    - [ ] **Maison / Projets** : liste filtrable, vue détaillée
    - [ ] **Jules** : chronologie, suivi développement
    - [ ] **Bien-être** : suivi sommeil / repos
    - [ ] **Jardin** : fiches plantations, notes saisonnières
    - [ ] **Météo** : affichage météo et recommandations
    - [ ] **Paramètres / Profil** : gestion utilisateurs, préférences

---

## 🔗 3. Automatisations et liens intelligents
- [ ] Logique : relier tâches et modules automatiquement
    - Exemple : tâche ménage cuisine → visible dans batch cooking
- [ ] Moteur d’association : tags + contexte
- [ ] Rappels automatiques selon contexte (jour, météo, crèche)
- [ ] Suggestions intelligentes :
    - [ ] Repas selon stock
    - [ ] Activité détente selon charge globale
    - [ ] Entretien maison/jardin selon saison

---

## 🧠 4. IA et recommandations
- [ ] Module IA :
    - [ ] `planner.py` : générer menus et optimiser routines
    - [ ] `assistant.py` : chat contextuel
    - [ ] `predictor.py` : anticiper besoins
    - [ ] `summarizer.py` : résumé intelligent des activités
- [ ] `core/services/ai_bridge.py` : interface IA ↔ modules
- [ ] Intégration UI : boutons IA sur modules clés
    - Exemple : “Proposer menu semaine”, “Optimiser routine matin”
- [ ] Tester cohérence des suggestions IA avec données réelles

---

## 🌦️ 5. Connectivité et données externes
- [ ] API météo (`weather_service.py`) : récupérer prévisions et traduire en recommandations
- [ ] Synchronisation iCal (`ical_service.py`) : récupérer et mettre à jour événements
- [ ] Sauvegarde cloud (`cloud_service.py`) : backup et restauration
- [ ] Export PDF / CSV / JSON par module
- [ ] Mode invité : accès lecture seule à certaines parties

---

## ☁️ 6. Confort et extensions
- [ ] Thème clair / sombre + CSS personnalisée
- [ ] Animation / illustration indicateur de charge
- [ ] Notifications locales (Streamlit / email)
- [ ] Import automatique recettes PDF / web
- [ ] Préparer futur mode mobile / tablette
