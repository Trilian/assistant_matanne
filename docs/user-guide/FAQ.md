# FAQ � Questions Fr�quentes

R�ponses aux questions les plus courantes sur Assistant Matanne.

---

## ?? Table des mati�res

- [G�n�ral](#g�n�ral)
- [Navigation](#navigation)
- [Compte et s�curit�](#compte-et-s�curit�)
- [Module Cuisine](#module-cuisine)
- [Module Famille](#module-famille)
- [Module Maison](#module-maison)
- [Fonctionnalit�s IA](#fonctionnalit�s-ia)
- [Technique](#technique)

---

## G�n�ral

### Qu'est-ce qu'Assistant Matanne ?

Assistant Matanne est une application web de gestion familiale qui centralise :
- La cuisine (recettes, planning, courses, inventaire)
- La famille (suivi enfant, activit�s, budget, journal)
- La maison (projets, entretien, �nergie, stocks)
- Les jeux (paris sportifs virtuels, loto)
- Des outils pratiques (IA, convertisseur, m�t�o)

### L'application est-elle gratuite ?

Oui, Assistant Matanne est actuellement gratuit dans sa version de base. Des fonctionnalit�s premium pourraient �tre ajout�es � l'avenir.

### Sur quels appareils puis-je utiliser l'application ?

L'application fonctionne sur :
- **Desktop** : Chrome, Firefox, Safari, Edge (derni�res versions)
- **Mobile** : iOS 14+, Android 10+ (via navigateur)
- **Tablette** : iPad, Android tablets

Une application mobile native est pr�vue pour 2027.

### L'application fonctionne-t-elle hors ligne ?

Non, une connexion internet est requise actuellement. Le mode hors ligne (PWA) est en d�veloppement.

---

## Navigation

### Comment naviguer vite sans chercher dans les menus ?

Appuie sur **`Ctrl+K`** (ou `Cmd+K` sur Mac) depuis n'importe quelle page.
Une palette de recherche s'ouvre avec toutes les pages de l'application.
Tape les premiers mots du module ou de la page (� rec �, � planning �, � jul ��) et appuie sur `Entr�e`.
Les 5 derni�res pages visit�es s'affichent en haut pour un acc�s encore plus rapide.

### � quoi sert �Ma Semaine� ?

C'est une vue calendaire transversale accessible depuis la sidebar ou via `Ctrl+K` ? �Ma Semaine�.
Elle regroupe sur 7 jours :
- ??? Les **repas planifi�s** (li�s au planning cuisine)
- ?? Les **activit�s famille** (Jules, sorties�)
- ?? Les **matchs** du calendrier jeux
- ?? Les **t�ches m�nage** du jour

Navigue entre les semaines avec les fl�ches `�` / `�`.

### Comment utiliser le chat IA sans quitter la page ?

Clique sur le bouton **??** (en bas � droite de l'�cran) pour ouvrir un mini-chat flottant.
Tu peux poser une question � l'assistant sans changer de page.
Appuie sur `Entr�e` pour envoyer, `Maj+Entr�e` pour un saut de ligne.
Pour une conversation plus longue, clique sur � Ouvrir le chat IA � en bas du popout.

### Comment lancer un minuteur et continuer � naviguer ?

1. Outils ? Minuteur ? Lance le compte � rebours
2. Une petite **barre de minuteur** appara�t en haut de l'�cran dans toute l'application
3. Clique sur **� Ouvrir �** dans cette barre pour revenir au minuteur � tout moment
Le minuteur reste actif m�me si tu navigues vers d'autres pages.

### Comment �pingler une page dans les favoris ?

Ouvre la page que tu veux �pingler, puis clique sur l'�toile **?** qui appara�t dans le fil d'ariane (en haut).
La page s'ajoute en haut de la sidebar dans la section **Favoris** (accessible d�s l'ouverture de l'app).
Clique � nouveau sur l'�toile pour d�s�pingler. Maximum 10 favoris recommand�s.

### Je ne vois pas le bouton �toile ?, pourquoi ?

Le bouton ? n'appara�t que sur les pages statiques principales (hubs, listes�).
Il ne s'affiche pas sur les pages dynamiques comme une fiche recette ou un d�tail de projet.

---

## Compte et s�curit�

### Comment cr�er un compte ?

1. Cliquez sur **"S'inscrire"**
2. Remplissez : email, nom complet, mot de passe (8+ caract�res)
3. Cliquez sur **"Cr�er mon compte"**
4. Vous �tes automatiquement connect�

### J'ai oubli� mon mot de passe, que faire ?

La fonctionnalit� "Mot de passe oubli�" arrive bient�t. En attendant, contactez support@assistant-matanne.fr avec votre email pour r�initialisation manuelle.

### Mes donn�es sont-elles s�curis�es ?

Oui, nous utilisons :
- **Authentification JWT** s�curis�e
- **Chiffrement bcrypt** pour les mots de passe
- **Row Level Security (RLS)** sur la base de donn�es
- **Rate limiting** pour prot�ger contre les attaques
- **HTTPS** syst�matique en production

Vos donn�es ne sont visibles que par vous (sauf partage explicite comme les listes de courses).

### Puis-je partager mon compte avec ma famille ?

Vous pouvez partager vos identifiants, mais nous recommandons :
1. Un compte par utilisateur pour la s�curit�
2. Utiliser les fonctionnalit�s de **partage** (listes de courses collaboratives, calendrier partag�)

Le compte familial multi-utilisateurs est pr�vu pour une future version.

### Comment supprimer mon compte ?

Envoyez un email � **support@assistant-matanne.fr** avec objet "Suppression de compte". Toutes vos donn�es seront effac�es sous 48h conform�ment au RGPD.

### Puis-je exporter mes donn�es ?

Oui, plusieurs options :
- **Export PDF** : Planning, courses, recettes, budget (bouton "Exporter" disponible)
- **Export JSON** : API endpoint `/api/v1/export/all` (n�cessite authentification)
- **Export RGPD** : Contactez support@assistant-matanne.fr pour export complet

---

## Module Cuisine

### Comment ajouter une recette ?

**M�thode 1 : Manuelle**
1. Cuisine ? Recettes ? **"+ Nouvelle recette"**
2. Remplissez les champs (nom, temps, portions, cat�gorie)
3. Ajoutez ingr�dients et �tapes
4. Enregistrez

**M�thode 2 : Import URL**
1. Cuisine ? Recettes ? **"Importer"**
2. Collez l'URL d'une recette en ligne (Marmiton, 750g, etc.)
3. L'IA analyse la page et pr�-remplit les champs
4. V�rifiez et ajustez si n�cessaire
5. Enregistrez

**M�thode 3 : Import PDF**
1. T�l�chargez un PDF de recette
2. L'OCR extrait le texte automatiquement
3. V�rifiez les champs d�tect�s

### Comment importer des recettes depuis Marmiton / 750g ?

1. Copiez l'URL compl�te de la recette (ex: https://www.marmiton.org/recettes/...)
2. Cuisine ? Recettes ? **"Importer depuis URL"**
3. Collez l'URL
4. Cliquez sur **"Analyser"**
5. L'IA extrait : nom, ingr�dients, �tapes, temps, portions
6. V�rifiez la pr�cision et corrigez si besoin
7. Enregistrez

> ?? **Note** : L'import fonctionne avec la plupart des sites de recettes fran�ais. Si un site ne fonctionne pas, signalez-le.

### Comment g�n�rer un planning de repas avec l'IA ?

1. Cuisine ? Planning ? **"G�n�rer avec IA"**
2. Configurez :
   - Date de d�but
   - Nombre de jours (3, 5 ou 7)
   - Contraintes (v�g�tarien, sans gluten, budget, temps de pr�paration max)
3. Cliquez sur **"G�n�rer"**
4. L'IA propose un planning �quilibr� bas� sur vos recettes
5. Modifiez les repas si besoin (drag & drop)
6. Validez le planning

### La g�n�ration IA ne me propose rien, pourquoi ?

V�rifiez :
- Vous avez au moins **10 recettes** dans votre biblioth�que
- Les recettes ont des **cat�gories** d�finies (plat, entr�e, dessert)
- Votre cl� API Mistral est configur�e (si auto-h�berg�)
- Vous n'avez pas atteint la limite d'appels IA (10/heure)

### Comment partager une liste de courses avec mon conjoint ?

1. Cr�ez une liste de courses (Cuisine ? Courses)
2. Cliquez sur **"Partager"**
3. Envoyez le **lien de partage** par email/SMS/WhatsApp
4. Votre conjoint ouvre le lien (connexion requise)
5. La liste est synchronis�e en temps r�el (WebSocket)
6. Chacun peut cocher/ajouter/retirer des articles instantan�ment

### Comment g�rer les dates de p�remption ?

1. Cuisine ? Inventaire
2. Ajoutez vos produits avec **date de p�remption**
3. Activez **"Alertes p�remption"** dans Param�tres
4. Vous recevrez une notification **3 jours avant** la p�remption
5. Utilisez **Anti-Gaspillage** pour voir les suggestions de recettes

### Puis-je importer mon inventaire en masse ?

Oui, via CSV :
1. T�l�chargez le template : `data/reference/template_import_inventaire.csv`
2. Remplissez : nom, quantit�, unit�, emplacement, date_peremption
3. Cuisine ? Inventaire ? **"Importer CSV"**
4. S�lectionnez votre fichier
5. V�rifiez l'aper�u
6. Confirmez l'import

---

## Module Famille

### Comment suivre le d�veloppement de mon enfant ?

1. Famille ? Jules
2. Onglet **"Jalons"** :
   - Ajoutez les �tapes importantes (premier sourire, premiers pas...)
   - Date + description + photo optionnelle
3. Onglet **"Croissance"** :
   - Entrez poids, taille, p�rim�tre cr�nien
   - Visualisez la courbe compar�e aux percentiles OMS
4. Onglet **"Sant�"** :
   - Suivez les vaccins (statut + rappels)
   - Notez les consultations m�dicales

### Comment obtenir des suggestions d'activit�s weekend ?

1. Famille ? Weekend ? **"Suggestions IA"**
2. L'IA analyse :
   - **�ge de Jules** (d�veloppement moteur/cognitif)
   - **M�t�o** du weekend (API int�gr�e)
   - **Saison** (activit�s int�rieures/ext�rieures)
   - **Historique** (�vite les r�p�titions)
3. Vous recevez 5 suggestions personnalis�es
4. Validez une suggestion ou demandez-en d'autres

### Puis-je exporter le calendrier familial vers Google Calendar ?

Oui :
1. Famille ? Activit�s ? **"Exporter iCal"**
2. T�l�chargez le fichier `.ics`
3. Importez-le dans Google Calendar / Outlook / Apple Calendar
4. Le synchronisation est **unidirectionnelle** (Assistant Matanne ? Calendrier externe)

La synchronisation bidirectionnelle est pr�vue pour une future version.

### Comment suivre le budget familial ?

1. Famille ? Budget
2. Ajoutez vos d�penses :
   - Montant, cat�gorie (alimentation, loisirs, sant�), date
3. Consultez :
   - **Graphique mensuel** : D�penses par cat�gorie
   - **Tendances** : Comparaison mois par mois
   - **Budget pr�visionnel** vs r�el
4. Activez les **alertes budget** (ex: "Plus de 500� en alimentation ce mois")

---

## Module Maison

### Comment cr�er un projet maison ?

1. Maison ? Projets ? **"+ Nouveau projet"**
2. Remplissez :
   - **Titre** : Ex: "Refaire la cuisine"
   - **Description** : D�tails du projet
   - **Budget pr�vu** : Estimation
   - **Priorit�** : Urgente / Haute / Moyenne / Basse
   - **Statut** : Id�e / Planifi� / En cours / Termin�
3. Ajoutez des **t�ches** (checklist)
4. Suivez l'avancement avec la barre de progression
5. Ajoutez des **photos avant/apr�s**

### Comment suivre ma consommation �nerg�tique ?

1. Maison ? �nergie
2. Entrez vos **relev�s de compteur** :
   - �lectricit� (kWh)
   - Gaz (m� ou kWh)
   - Eau (m�)
   - Date du relev�
3. Consultez les graphiques :
   - **Consommation mensuelle** : Historique sur 12 mois
   - **Co�t estim�** : Bas� sur les tarifs moyens
   - **�volution** : Comparaison ann�e N vs ann�e N-1
4. Recevez des **�co-Tips** personnalis�s pour r�duire votre consommation

### Comment g�rer les contrats de la maison ?

1. Maison ? Contrats
2. Ajoutez vos contrats :
   - **Type** : Assurance, abonnement, maintenance
   - **Nom** : Ex: "Assurance habitation Allianz"
   - **Fournisseur** : Nom de l'entreprise
   - **Date d�but** / **Date fin**
   - **Montant** : Montant mensuel ou annuel
   - **Renouvellement automatique** : Oui/Non
3. Activez les **rappels** :
   - 30 jours avant �ch�ance : Notification "Contrat � renouveler"
4. Stockez les **documents** (PDF du contrat)

### Comment suivre les coordonn�es des artisans ?

1. Maison ? Artisans
2. Ajoutez un artisan :
   - Nom, sp�cialit� (plombier, �lectricien, etc.)
   - Coordonn�es (t�l�phone, email, adresse)
   - **Notes** : Qualit� du travail, tarifs, recommandations
   - **Interventions pass�es** : Historique des travaux
3. �valuez avec des **�toiles** (1-5)
4. Recherchez par sp�cialit� ou note

---

## Fonctionnalit�s IA

### Quelle IA utilisez-vous ?

Nous utilisons **Mistral AI** (mod�le `mistral-large-latest`), une IA de pointe d�velopp�e en France, pour :
- Suggestions de recettes
- G�n�ration de planning repas
- Analyse nutritionnelle
- Import de recettes depuis URL/PDF
- Suggestions d'activit�s weekend
- Conseils budg�taires

### Combien de requ�tes IA puis-je faire ?

Limites actuelles (protection anti-abus) :
- **10 requ�tes IA par heure**
- **50 requ�tes IA par jour**

Si vous d�passez, vous recevrez un message : "Limite atteinte, r�essayez dans X minutes".

### L'IA se trompe parfois, est-ce normal ?

Oui, l'IA n'est pas parfaite � 100%. Cas possibles :
- Import de recette : Ingr�dients mal pars�s (v�rifiez toujours)
- Planning : Suggestion non �quilibr�e (ajustez manuellement)
- Activit�s weekend : Proposition inadapt�e (rafra�chissez)

**Bonne pratique** : Toujours v�rifier et corriger les r�sultats de l'IA avant validation.

### Mes donn�es sont-elles utilis�es pour entra�ner l'IA ?

**Non.** Vos donn�es restent priv�es :
- Les requ�tes vers Mistral AI sont **anonymis�es**
- Aucune donn�e personnelle n'est envoy�e (seulement le contexte n�cessaire)
- Nous n'entra�nons pas de mod�le sur vos donn�es
- Mistral AI ne stocke pas vos requ�tes au-del� de 30 jours (politique RGPD)

### Puis-je d�sactiver l'IA ?

Oui :
1. Param�tres ? **"Fonctionnalit�s IA"**
2. D�cochez **"Activer suggestions IA"**
3. Les boutons "G�n�rer avec IA" dispara�tront
4. L'application reste pleinement fonctionnelle sans IA

---

## Technique

### L'application est lente, que faire ?

V�rifiez :
1. **Connexion internet** : Minimum 2 Mbps recommand�
2. **Navigateur** : Utilisez la derni�re version de Chrome/Firefox/Safari
3. **Cache** : Videz le cache navigateur (Ctrl+Shift+Del)
4. **Taille donn�es** : Si vous avez 500+ recettes, les filtres peuvent ralentir

Si le probl�me persiste, contactez support@assistant-matanne.fr avec :
- Navigateur + version
- Type d'appareil
- Page concern�e

### Puis-je utiliser l'application sur plusieurs appareils ?

Oui, vos donn�es sont synchronis�es automatiquement :
1. Connectez-vous avec le m�me compte sur tous vos appareils
2. Les modifications se synchronisent en temps r�el
3. D�connectez-vous d'un appareil sans affecter les autres

### L'application est-elle open source ?

Actuellement **non**. Nous envisageons de publier le code source sous licence MIT � l'avenir.

### Puis-je auto-h�berger l'application ?

Pas encore. L'auto-h�bergement est pr�vu pour Q3 2026 avec :
- Docker Compose pour d�ploiement facile
- Documentation d'installation compl�te
- Support communautaire

### Quelle base de donn�es utilisez-vous ?

**Supabase** (PostgreSQL 15+) avec :
- Row Level Security (RLS) pour l'isolation des donn�es
- Migrations SQL versionn�es
- Backup automatique quotidien

### Comment signaler un bug ?

1. **GitHub Issues** : https://github.com/votreorg/assistant-matanne/issues (� venir)
2. **Email** : support@assistant-matanne.fr avec :
   - Description du bug
   - �tapes pour reproduire
   - Screenshots si possible
   - Navigateur + appareil

### Comment proposer une fonctionnalit� ?

1. Consultez la [roadmap](../../ROADMAP.md) pour voir si c'est d�j� pr�vu
2. Ouvrez une **feature request** sur GitHub (� venir)
3. Ou envoyez un email � **features@assistant-matanne.fr**

---

## ? Question non list�e ?

**Support utilisateur** : support@assistant-matanne.fr  
**D�lai de r�ponse** : 24-48h ouvr�es

Consultez aussi le **[Guide de d�marrage](./getting-started.md)** pour des tutoriels d�taill�s.
