# Premiers pas avec Assistant Matanne

Ce guide vous accompagne dans la découverte d'Assistant Matanne, de l'inscription à la maîtrise des fonctionnalités essentielles.

---

## 📋 Table des matières

1. [Inscription](#inscription)
2. [Connexion](#connexion)
3. [Tour du dashboard](#dashboard)
4. [Module Cuisine](#module-cuisine)
5. [Module Famille](#module-famille)
6. [Module Maison](#module-maison)
7. [Cas d'usage typiques](#cas-dusage)

---

## 1. Inscription {#inscription}

### Créer votre compte

1. Rendez-vous sur **https://assistant-matanne.vercel.app**
2. Cliquez sur **"S'inscrire"**
3. Remplissez le formulaire :
   - **Email** : Votre adresse email (sera utilisée pour la connexion)
   - **Nom complet** : Prénom et nom
   - **Mot de passe** : Minimum 8 caractères
4. Cliquez sur **"Créer mon compte"**
5. Vous êtes automatiquement connecté et redirigé vers le dashboard

> 💡 **Astuce** : Votre mot de passe est chiffré et stocké de manière sécurisée. Nous ne pouvons pas le récupérer si vous l'oubliez.

---

## 2. Connexion {#connexion}

Si vous avez déjà un compte :

1. Cliquez sur **"Se connecter"** depuis la page d'accueil
2. Entrez vos identifiants (email + mot de passe)
3. Cliquez sur **"Connexion"**

Votre session reste active pendant 7 jours (sauf si vous vous déconnectez manuellement).

---

## 3. Tour du Dashboard {#dashboard}

Le **dashboard** est votre page d'accueil. Il affiche :

### Statistiques globales
- **Recettes** : Nombre total de recettes dans votre bibliothèque
- **Courses** : Items dans vos listes actives
- **Budget** : Dépenses du mois en cours
- **Projets** : Projets maison en cours

### Widgets principaux
- **📅 Prochaines activités** : Activités familiales à venir
- **🍽️ Planning de la semaine** : Aperçu des repas planifiés
- **⚠️ Alertes** : Rappels importants (dates de péremption, contrats à renouveler, etc.)
- **📊 Budget du mois** : Graphique des dépenses

### Navigation
- **Sidebar (desktop)** : Menu latéral gauche avec tous les modules
- **Bottom bar (mobile)** : Barre de navigation en bas d'écran
- **Header** : Recherche globale + paramètres + déconnexion

---

## 4. Module Cuisine {#module-cuisine}

### Ajouter votre première recette

1. Cliquez sur **Cuisine → Recettes** dans la sidebar
2. Cliquez sur **"+ Nouvelle recette"**
3. Remplissez les informations :
   - **Nom** : Titre de la recette
   - **Temps de préparation** / **Temps de cuisson**
   - **Portions** : Nombre de personnes
   - **Catégorie** : Entrée, plat, dessert...
   - **Saison** : Printemps, été, automne, hiver, toutes saisons
   - **Tags** : Étiquettes pour la recherche (ex: rapide, végétarien, sans gluten)
4. Ajoutez les **ingrédients** :
   - Quantité, unité, nom
   - Cliquez sur **"+ Ajouter ingrédient"** pour chaque ligne
5. Rédigez les **étapes** :
   - Numérotées automatiquement
   - Soyez précis et clair
6. (Optionnel) Ajoutez des **notes** ou une **URL source**
7. Cliquez sur **"Enregistrer"**

> 💡 **Import depuis URL** : Collez l'URL d'une recette en ligne, l'IA analysera la page et pré-remplira les champs automatiquement.

### Générer un planning de repas avec l'IA {#planning-ia}

1. Allez dans **Cuisine → Planning**
2. Cliquez sur **"Générer avec IA"**
3. Choisissez :
   - **Début de semaine** : Date de démarrage
   - **Nombre de jours** : 3, 5 ou 7 jours
   - **Préférences** : Recettes favorites, contraintes alimentaires, équilibre nutritionnel
4. Cliquez sur **"Générer le planning"**
5. L'IA propose un planning équilibré basé sur :
   - Votre bibliothèque de recettes
   - L'équilibre nutritionnel (protéines, légumes, féculents)
   - La variété (pas la même recette deux fois)
   - La saison actuelle
6. Vous pouvez **modifier** chaque repas manuellement après génération
7. Cliquez sur **"Valider le planning"**

### Générer la liste de courses

1. Depuis le planning validé, cliquez sur **"Générer liste de courses"**
2. L'application agrège automatiquement tous les ingrédients
3. Vérifiez les **quantités** (déjà optimisées)
4. Cochez **"Vérifier l'inventaire"** pour exclure ce que vous avez déjà
5. Cliquez sur **"Créer la liste"**
6. Partagez la liste en temps réel avec votre famille (collaboration live)
7. Cochez les articles au fur et à mesure de vos achats

### Gérer l'inventaire

1. Allez dans **Cuisine → Inventaire**
2. Ajoutez vos produits :
   - **Nom** : Nom du produit
   - **Quantité** : Nombre ou poids
   - **Emplacement** : Frigo, congélateur, placard...
   - **Date de péremption** : Pour suivre la fraîcheur
3. Activez les **alertes péremption** : vous serez notifié 3 jours avant
4. Utilisez **Anti-Gaspillage** pour voir les suggestions de recettes avec produits proches de la péremption

---

## 5. Module Famille {#module-famille}

### Suivre le développement de Jules

1. Allez dans **Famille → Jules**
2. Ajoutez les **jalons** :
   - Premier sourire, premiers pas, premières dents...
   - Date + description + photo optionnelle
3. Consultez la **courbe de croissance** :
   - Poids, taille, périmètre crânien
   - Comparaison avec les percentiles OMS
4. Suivez le **calendrier vaccinal** :
   - Vaccins recommandés par âge
   - Statut (à faire / fait)
   - Rappels automatiques

### Planifier les activités

1. Allez dans **Famille → Activités**
2. Créez une activité :
   - **Nom** : Ex: "Piscine"
   - **Fréquence** : Hebdomadaire, mensuelle, ponctuelle
   - **Jour/Heure** : Exemple: Mercredi 15h-16h
   - **Lieu** : Adresse ou nom du lieu
   - **Coût** : Montant mensuel ou par séance
3. Visualisez le calendrier de toutes les activités
4. Exportez au format iCal pour synchronisation avec Google Calendar / Outlook

### Suggestions weekend IA

1. Allez dans **Famille → Weekend**
2. Cliquez sur **"Suggestions IA"**
3. L'IA propose des activités adaptées :
   - **Âge de Jules** (développement moteur et cognitif)
   - **Météo** du weekend
   - **Saison** (activités intérieures/extérieures)
   - **Historique** (évite les répétitions)
4. Validez une suggestion ou demandez-en d'autres

---

## 6. Module Maison {#module-maison}

### Gérer vos projets

1. Allez dans **Maison → Projets**
2. Créez un projet :
   - **Titre** : Ex: "Refaire la salle de bain"
   - **Description** : Détails du projet
   - **Budget prévu** : Estimation
   - **Priorité** : Urgente, haute, moyenne, basse
   - **Statut** : Idée, planifié, en cours, terminé
3. Ajoutez des **tâches** à chaque projet
4. Suivez l'avancement avec la barre de progression
5. Ajoutez des **photos avant/après**

### Suivi de l'énergie

1. Allez dans **Maison → Énergie**
2. Entrez vos **relevés de compteur** (électricité, gaz, eau)
3. Consultez les **graphiques de consommation** mensuels
4. Recevez des **conseils d'économie** via Éco-Tips

---

## 7. Cas d'usage typiques {#cas-dusage}

### **Lundi matin : Planifier la semaine**
1. Générer le planning de repas avec IA (5 jours)
2. Générer la liste de courses automatiquement
3. Partager la liste avec votre conjoint
4. Vérifier les activités de Jules pour la semaine

### **Mercredi : Courses en magasin**
1. Ouvrir la liste partagée sur mobile
2. Cocher les articles au fur et à mesure
3. Ajouter des articles oubliés en temps réel
4. Voir les modifications en direct de votre conjoint

### **Samedi : Batch cooking**
1. Aller dans **Cuisine → Batch Cooking**
2. Créer une session avec les recettes de la semaine
3. Générer le planning de préparation optimisé
4. Suivre l'ordre suggéré pour gagner du temps

### **Dimanche soir : Bilan de la semaine**
1. Noter les recettes réussies (⭐ favoris)
2. Marquer les repas préparés dans le planning
3. Mettre à jour l'inventaire (produits consommés)
4. Préparer le planning de la semaine suivante

---

## ❓ Questions fréquentes

**Q : Puis-je utiliser l'app hors ligne ?**  
R : Actuellement non, une connexion internet est requise. Le mode hors ligne est prévu pour une version future.

**Q : Mes données sont-elles sécurisées ?**  
R : Oui. Authentification JWT, chiffrement des mots de passe, Row Level Security sur la base de données. Vos données ne sont visibles que par vous.

**Q : Puis-je partager mon compte avec ma famille ?**  
R : Vous pouvez partager vos identifiants, mais nous recommandons de créer un compte par utilisateur pour des raisons de sécurité. Le partage en temps réel (courses) fonctionne entre comptes.

**Q : Comment supprimer mon compte ?**  
R : Contactez-nous à support@assistant-matanne.fr. La suppression sera effective sous 48h avec effacement de toutes vos données.

Pour plus de questions, consultez la **[FAQ complète](./FAQ.md)**.

---

**Prêt à explorer ?** Retournez au [dashboard](/) et commencez votre organisation familiale ! 🚀
