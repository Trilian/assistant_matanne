# FAQ — Questions Fréquentes

Réponses aux questions les plus courantes sur Assistant Matanne.

---

## 📚 Table des matières

- [Général](#général)
- [Navigation](#navigation)
- [Compte et sécurité](#compte-et-sécurité)
- [Module Cuisine](#module-cuisine)
- [Module Famille](#module-famille)
- [Module Maison](#module-maison)
- [Fonctionnalités IA](#fonctionnalités-ia)
- [Technique](#technique)

---

## Général

### Qu'est-ce qu'Assistant Matanne ?

Assistant Matanne est une application web de gestion familiale qui centralise :
- La cuisine (recettes, planning, courses, inventaire)
- La famille (suivi enfant, activités, budget, journal)
- La maison (projets, entretien, énergie, stocks)
- Les jeux (paris sportifs virtuels, loto)
- Des outils pratiques (IA, convertisseur, météo)

### L'application est-elle gratuite ?

Oui, Assistant Matanne est actuellement gratuit dans sa version de base. Des fonctionnalités premium pourraient être ajoutées à l'avenir.

### Sur quels appareils puis-je utiliser l'application ?

L'application fonctionne sur :
- **Desktop** : Chrome, Firefox, Safari, Edge (dernières versions)
- **Mobile** : iOS 14+, Android 10+ (via navigateur)
- **Tablette** : iPad, Android tablets

Une application mobile native est prévue pour 2027.

### L'application fonctionne-t-elle hors ligne ?

Non, une connexion internet est requise actuellement. Le mode hors ligne (PWA) est en développement.

---

## Navigation

### Comment naviguer vite sans chercher dans les menus ?

Appuie sur **`Ctrl+K`** (ou `Cmd+K` sur Mac) depuis n'importe quelle page.
Une palette de recherche s'ouvre avec toutes les pages de l'application.
Tape les premiers mots du module ou de la page (« rec », « planning », « jul »…) et appuie sur `Entrée`.
Les 5 dernières pages visitées s'affichent en haut pour un accès encore plus rapide.

### À quoi sert “Ma Semaine” ?

C'est une vue calendaire transversale accessible depuis la sidebar ou via `Ctrl+K` → «Ma Semaine».
Elle regroupe sur 7 jours :
- 🍽️ Les **repas planifiés** (liés au planning cuisine)
- 👶 Les **activités famille** (Jules, sorties…)
- 🏆 Les **matchs** du calendrier jeux
- 🧹 Les **tâches ménage** du jour

Navigue entre les semaines avec les flèches `‹` / `›`.

### Comment utiliser le chat IA sans quitter la page ?

Clique sur le bouton **🤖** (en bas à droite de l'écran) pour ouvrir un mini-chat flottant.
Tu peux poser une question à l'assistant sans changer de page.
Appuie sur `Entrée` pour envoyer, `Maj+Entrée` pour un saut de ligne.
Pour une conversation plus longue, clique sur « Ouvrir le chat IA » en bas du popout.

### Comment lancer un minuteur et continuer à naviguer ?

1. Outils → Minuteur → Lance le compte à rebours
2. Une petite **barre de minuteur** apparaît en haut de l'écran dans toute l'application
3. Clique sur **« Ouvrir »** dans cette barre pour revenir au minuteur à tout moment
Le minuteur reste actif même si tu navigues vers d'autres pages.

### Comment épingler une page dans les favoris ?

Ouvre la page que tu veux épingler, puis clique sur l'étoile **★** qui apparaît dans le fil d'ariane (en haut).
La page s'ajoute en haut de la sidebar dans la section **Favoris** (accessible dès l'ouverture de l'app).
Clique à nouveau sur l'étoile pour désépingler. Maximum 10 favoris recommandés.

### Je ne vois pas le bouton étoile ★, pourquoi ?

Le bouton ★ n'apparaît que sur les pages statiques principales (hubs, listes…).
Il ne s'affiche pas sur les pages dynamiques comme une fiche recette ou un détail de projet.

---

## Compte et sécurité

### Comment créer un compte ?

1. Cliquez sur **"S'inscrire"**
2. Remplissez : email, nom complet, mot de passe (8+ caractères)
3. Cliquez sur **"Créer mon compte"**
4. Vous êtes automatiquement connecté

### J'ai oublié mon mot de passe, que faire ?

La fonctionnalité "Mot de passe oublié" arrive bientôt. En attendant, contactez support@assistant-matanne.fr avec votre email pour réinitialisation manuelle.

### Mes données sont-elles sécurisées ?

Oui, nous utilisons :
- **Authentification JWT** sécurisée
- **Chiffrement bcrypt** pour les mots de passe
- **Row Level Security (RLS)** sur la base de données
- **Rate limiting** pour protéger contre les attaques
- **HTTPS** systématique en production

Vos données ne sont visibles que par vous (sauf partage explicite comme les listes de courses).

### Puis-je partager mon compte avec ma famille ?

Vous pouvez partager vos identifiants, mais nous recommandons :
1. Un compte par utilisateur pour la sécurité
2. Utiliser les fonctionnalités de **partage** (listes de courses collaboratives, calendrier partagé)

Le compte familial multi-utilisateurs est prévu pour une future version.

### Comment supprimer mon compte ?

Envoyez un email à **support@assistant-matanne.fr** avec objet "Suppression de compte". Toutes vos données seront effacées sous 48h conformément au RGPD.

### Puis-je exporter mes données ?

Oui, plusieurs options :
- **Export PDF** : Planning, courses, recettes, budget (bouton "Exporter" disponible)
- **Export JSON** : API endpoint `/api/v1/export/all` (nécessite authentification)
- **Export RGPD** : Contactez support@assistant-matanne.fr pour export complet

---

## Module Cuisine

### Comment ajouter une recette ?

**Méthode 1 : Manuelle**
1. Cuisine → Recettes → **"+ Nouvelle recette"**
2. Remplissez les champs (nom, temps, portions, catégorie)
3. Ajoutez ingrédients et étapes
4. Enregistrez

**Méthode 2 : Import URL**
1. Cuisine → Recettes → **"Importer"**
2. Collez l'URL d'une recette en ligne (Marmiton, 750g, etc.)
3. L'IA analyse la page et pré-remplit les champs
4. Vérifiez et ajustez si nécessaire
5. Enregistrez

**Méthode 3 : Import PDF**
1. Téléchargez un PDF de recette
2. L'OCR extrait le texte automatiquement
3. Vérifiez les champs détectés

### Comment importer des recettes depuis Marmiton / 750g ?

1. Copiez l'URL complète de la recette (ex: https://www.marmiton.org/recettes/...)
2. Cuisine → Recettes → **"Importer depuis URL"**
3. Collez l'URL
4. Cliquez sur **"Analyser"**
5. L'IA extrait : nom, ingrédients, étapes, temps, portions
6. Vérifiez la précision et corrigez si besoin
7. Enregistrez

> ⚠️ **Note** : L'import fonctionne avec la plupart des sites de recettes français. Si un site ne fonctionne pas, signalez-le.

### Comment générer un planning de repas avec l'IA ?

1. Cuisine → Planning → **"Générer avec IA"**
2. Configurez :
   - Date de début
   - Nombre de jours (3, 5 ou 7)
   - Contraintes (végétarien, sans gluten, budget, temps de préparation max)
3. Cliquez sur **"Générer"**
4. L'IA propose un planning équilibré basé sur vos recettes
5. Modifiez les repas si besoin (drag & drop)
6. Validez le planning

### La génération IA ne me propose rien, pourquoi ?

Vérifiez :
- Vous avez au moins **10 recettes** dans votre bibliothèque
- Les recettes ont des **catégories** définies (plat, entrée, dessert)
- Votre clé API Mistral est configurée (si auto-hébergé)
- Vous n'avez pas atteint la limite d'appels IA (10/heure)

### Comment partager une liste de courses avec mon conjoint ?

1. Créez une liste de courses (Cuisine → Courses)
2. Cliquez sur **"Partager"**
3. Envoyez le **lien de partage** par email/SMS/WhatsApp
4. Votre conjoint ouvre le lien (connexion requise)
5. La liste est synchronisée en temps réel (WebSocket)
6. Chacun peut cocher/ajouter/retirer des articles instantanément

### Comment gérer les dates de péremption ?

1. Cuisine → Inventaire
2. Ajoutez vos produits avec **date de péremption**
3. Activez **"Alertes péremption"** dans Paramètres
4. Vous recevrez une notification **3 jours avant** la péremption
5. Utilisez **Anti-Gaspillage** pour voir les suggestions de recettes

### Puis-je importer mon inventaire en masse ?

Oui, via CSV :
1. Téléchargez le template : `data/reference/template_import_inventaire.csv`
2. Remplissez : nom, quantité, unité, emplacement, date_peremption
3. Cuisine → Inventaire → **"Importer CSV"**
4. Sélectionnez votre fichier
5. Vérifiez l'aperçu
6. Confirmez l'import

---

## Module Famille

### Comment suivre le développement de mon enfant ?

1. Famille → Jules
2. Onglet **"Jalons"** :
   - Ajoutez les étapes importantes (premier sourire, premiers pas...)
   - Date + description + photo optionnelle
3. Onglet **"Croissance"** :
   - Entrez poids, taille, périmètre crânien
   - Visualisez la courbe comparée aux percentiles OMS
4. Onglet **"Santé"** :
   - Suivez les vaccins (statut + rappels)
   - Notez les consultations médicales

### Comment obtenir des suggestions d'activités weekend ?

1. Famille → Weekend → **"Suggestions IA"**
2. L'IA analyse :
   - **Âge de Jules** (développement moteur/cognitif)
   - **Météo** du weekend (API intégrée)
   - **Saison** (activités intérieures/extérieures)
   - **Historique** (évite les répétitions)
3. Vous recevez 5 suggestions personnalisées
4. Validez une suggestion ou demandez-en d'autres

### Puis-je exporter le calendrier familial vers Google Calendar ?

Oui :
1. Famille → Activités → **"Exporter iCal"**
2. Téléchargez le fichier `.ics`
3. Importez-le dans Google Calendar / Outlook / Apple Calendar
4. Le synchronisation est **unidirectionnelle** (Assistant Matanne → Calendrier externe)

La synchronisation bidirectionnelle est prévue pour une future version.

### Comment suivre le budget familial ?

1. Famille → Budget
2. Ajoutez vos dépenses :
   - Montant, catégorie (alimentation, loisirs, santé), date
3. Consultez :
   - **Graphique mensuel** : Dépenses par catégorie
   - **Tendances** : Comparaison mois par mois
   - **Budget prévisionnel** vs réel
4. Activez les **alertes budget** (ex: "Plus de 500€ en alimentation ce mois")

---

## Module Maison

### Comment créer un projet maison ?

1. Maison → Projets → **"+ Nouveau projet"**
2. Remplissez :
   - **Titre** : Ex: "Refaire la cuisine"
   - **Description** : Détails du projet
   - **Budget prévu** : Estimation
   - **Priorité** : Urgente / Haute / Moyenne / Basse
   - **Statut** : Idée / Planifié / En cours / Terminé
3. Ajoutez des **tâches** (checklist)
4. Suivez l'avancement avec la barre de progression
5. Ajoutez des **photos avant/après**

### Comment suivre ma consommation énergétique ?

1. Maison → Énergie
2. Entrez vos **relevés de compteur** :
   - Électricité (kWh)
   - Gaz (m³ ou kWh)
   - Eau (m³)
   - Date du relevé
3. Consultez les graphiques :
   - **Consommation mensuelle** : Historique sur 12 mois
   - **Coût estimé** : Basé sur les tarifs moyens
   - **Évolution** : Comparaison année N vs année N-1
4. Recevez des **Éco-Tips** personnalisés pour réduire votre consommation

### Comment gérer les contrats de la maison ?

1. Maison → Contrats
2. Ajoutez vos contrats :
   - **Type** : Assurance, abonnement, maintenance
   - **Nom** : Ex: "Assurance habitation Allianz"
   - **Fournisseur** : Nom de l'entreprise
   - **Date début** / **Date fin**
   - **Montant** : Montant mensuel ou annuel
   - **Renouvellement automatique** : Oui/Non
3. Activez les **rappels** :
   - 30 jours avant échéance : Notification "Contrat à renouveler"
4. Stockez les **documents** (PDF du contrat)

### Comment suivre les coordonnées des artisans ?

1. Maison → Artisans
2. Ajoutez un artisan :
   - Nom, spécialité (plombier, électricien, etc.)
   - Coordonnées (téléphone, email, adresse)
   - **Notes** : Qualité du travail, tarifs, recommandations
   - **Interventions passées** : Historique des travaux
3. Évaluez avec des **étoiles** (1-5)
4. Recherchez par spécialité ou note

---

## Fonctionnalités IA

### Quelle IA utilisez-vous ?

Nous utilisons **Mistral AI** (modèle `mistral-large-latest`), une IA de pointe développée en France, pour :
- Suggestions de recettes
- Génération de planning repas
- Analyse nutritionnelle
- Import de recettes depuis URL/PDF
- Suggestions d'activités weekend
- Conseils budgétaires

### Combien de requêtes IA puis-je faire ?

Limites actuelles (protection anti-abus) :
- **10 requêtes IA par heure**
- **50 requêtes IA par jour**

Si vous dépassez, vous recevrez un message : "Limite atteinte, réessayez dans X minutes".

### L'IA se trompe parfois, est-ce normal ?

Oui, l'IA n'est pas parfaite à 100%. Cas possibles :
- Import de recette : Ingrédients mal parsés (vérifiez toujours)
- Planning : Suggestion non équilibrée (ajustez manuellement)
- Activités weekend : Proposition inadaptée (rafraîchissez)

**Bonne pratique** : Toujours vérifier et corriger les résultats de l'IA avant validation.

### Mes données sont-elles utilisées pour entraîner l'IA ?

**Non.** Vos données restent privées :
- Les requêtes vers Mistral AI sont **anonymisées**
- Aucune donnée personnelle n'est envoyée (seulement le contexte nécessaire)
- Nous n'entraînons pas de modèle sur vos données
- Mistral AI ne stocke pas vos requêtes au-delà de 30 jours (politique RGPD)

### Puis-je désactiver l'IA ?

Oui :
1. Paramètres → **"Fonctionnalités IA"**
2. Décochez **"Activer suggestions IA"**
3. Les boutons "Générer avec IA" disparaîtront
4. L'application reste pleinement fonctionnelle sans IA

---

## Technique

### L'application est lente, que faire ?

Vérifiez :
1. **Connexion internet** : Minimum 2 Mbps recommandé
2. **Navigateur** : Utilisez la dernière version de Chrome/Firefox/Safari
3. **Cache** : Videz le cache navigateur (Ctrl+Shift+Del)
4. **Taille données** : Si vous avez 500+ recettes, les filtres peuvent ralentir

Si le problème persiste, contactez support@assistant-matanne.fr avec :
- Navigateur + version
- Type d'appareil
- Page concernée

### Puis-je utiliser l'application sur plusieurs appareils ?

Oui, vos données sont synchronisées automatiquement :
1. Connectez-vous avec le même compte sur tous vos appareils
2. Les modifications se synchronisent en temps réel
3. Déconnectez-vous d'un appareil sans affecter les autres

### L'application est-elle open source ?

Actuellement **non**. Nous envisageons de publier le code source sous licence MIT à l'avenir.

### Puis-je auto-héberger l'application ?

Pas encore. L'auto-hébergement est prévu pour Q3 2026 avec :
- Docker Compose pour déploiement facile
- Documentation d'installation complète
- Support communautaire

### Quelle base de données utilisez-vous ?

**Supabase** (PostgreSQL 15+) avec :
- Row Level Security (RLS) pour l'isolation des données
- Migrations SQL versionnées
- Backup automatique quotidien

### Comment signaler un bug ?

1. **GitHub Issues** : https://github.com/votreorg/assistant-matanne/issues (à venir)
2. **Email** : support@assistant-matanne.fr avec :
   - Description du bug
   - Étapes pour reproduire
   - Screenshots si possible
   - Navigateur + appareil

### Comment proposer une fonctionnalité ?

1. Consultez la [roadmap](../../ROADMAP.md) pour voir si c'est déjà prévu
2. Ouvrez une **feature request** sur GitHub (à venir)
3. Ou envoyez un email à **features@assistant-matanne.fr**

---

## ❓ Question non listée ?

**Support utilisateur** : support@assistant-matanne.fr  
**Délai de réponse** : 24-48h ouvrées

Consultez aussi le **[Guide de démarrage](./getting-started.md)** pour des tutoriels détaillés.
