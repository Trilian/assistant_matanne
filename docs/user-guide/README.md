# Guide Utilisateur � Assistant Matanne

Bienvenue dans la documentation utilisateur d'**Assistant Matanne**, votre hub familial tout-en-un pour g�rer le quotidien avec simplicit� et intelligence.

## ?? Table des mati�res

- [Premiers pas](./getting-started.md) � Installation, inscription et tour rapide
- [FAQ � Questions fr�quentes](./FAQ.md) � R�ponses aux questions courantes
- [Modules](#modules) � Vue d'ensemble des fonctionnalit�s
### Guides par module

- [🍽️ Cuisine](./Cuisine.md) — Recettes, planning repas, courses, inventaire, batch cooking
- [👨‍👩‍👧 Famille](./Famille.md) — Jules, activités, routines, budget, voyages, contacts
- [🏠 Maison](./Maison.md) — Projets, entretien, jardin, énergie, équipements, finances
- [🎮 Jeux](./Jeux.md) — Paris sportifs, Loto, EuroMillions, bankroll
- [🔧 Outils](./Outils.md) — Chat IA, convertisseur, météo, minuteur, notes
---

## ?? Qu'est-ce qu'Assistant Matanne ?

Assistant Matanne est une application web moderne qui centralise la gestion familiale :

### ??? **Cuisine**
- **Recettes** : Biblioth�que de recettes avec recherche avanc�e, tags et notes
- **Planning repas** : Planification hebdomadaire avec suggestions IA
- **Courses** : Listes de courses intelligentes g�n�r�es depuis les recettes
- **Inventaire** : Suivi des stocks avec dates de p�remption
- **Batch Cooking** : Organisation des sessions de pr�paration
- **Anti-Gaspillage** : Suggestions pour utiliser les restes

### ???????? **Famille**
- **Jules** : Suivi du développement de l'enfant (jalons, alimentation, vaccins, activités)
- **Activit�s** : Gestion des activit�s familiales et emploi du temps
- **Routines** : Routines quotidiennes et habitudes
- **Budget** : Suivi des d�penses familiales
- **Weekend** : Suggestions d'activit�s pour le weekend
- **Anniversaires** : Rappels et organisation
- **Contacts** : Carnet d'adresses familial
- **Journal** : Journal familial avec suivi d'humeur
- **Documents** : Stockage et organisation des documents importants

### ?? **Maison**
- **Projets** : Gestion des travaux et projets maison
- **Jardin** : Planification et suivi du jardin
- **Entretien** : Calendrier d'entretien avec rappels
- **Charges** : Suivi des charges fixes
- **D�penses** : Historique des d�penses maison
- **�nergie** : Relev�s et suivi de consommation
- **Stocks** : Inventaire g�n�ral (produits m�nagers, etc.)
- **Cellier** : Gestion de la cave � vin
- **Artisans** : Coordonn�es et historique des interventions
- **Abonnements** : Comparateur d'abonnements (eau, électricité, gaz, assurances, téléphone, internet)
- **Diagnostics** : Stockage des diagnostics immobiliers
- **Visualisation** : Plan de la maison et visualisation des espaces
- **�co-Tips** : Conseils �cologiques et �conomies d'�nergie

### ?? **Planning**
- Vue calendrier unifi�e
- Timeline interactive
- Synchronisation avec les �v�nements famille

### ?? **Jeux**
- **Paris sportifs** : Suivi et statistiques (mode virtuel ou r�el)
- **Loto** : Gestion des grilles et tirages
- **EuroMillions** : Gestion des grilles

### ??? **Outils**
- **Chat IA** : Assistant conversationnel pour suggestions cuisine
- **Convertisseur** : Conversion d'unit�s (masse, volume, temp�rature)
- **M�t�o** : Pr�visions m�t�o int�gr�es
- **Minuteur** : Minuteurs de cuisine multiples
- **Notes** : Prise de notes rapide

---

## ? Fonctionnalit�s cl�s

### Intelligence Artificielle
- **Suggestions de recettes** bas�es sur inventaire et pr�f�rences
- **G�n�ration de planning** hebdomadaire �quilibr�
- **Suggestions d'activit�s weekend** adapt�es � l'�ge de l'enfant
- **Analyse nutritionnelle** automatique
- **Optimisation anti-gaspillage**

### Navigation rapide
- **`Ctrl+K` (ou `Cmd+K`)** : Palette de commandes � recherchez et acc�dez instantan�ment � n'importe quelle page sans cliquer dans les menus. Affiche aussi les 5 derni�res pages visit�es.
- **? Favoris** : �pingle tes pages les plus utilis�es via le bouton ? dans le fil d'ariane. Elles appara�ssent en haut de la sidebar.
- **Ma Semaine** (`/ma-semaine`) : Vue trans-modules de la semaine en cours � repas planifi�s, activit�s famille, matchs du jour et t�ches m�nage sur un seul �cran.
- **Chat IA flottant** (bouton ?? en bas � droite) : Mini-chat accessible depuis n'importe quelle page sans quitter son contexte. Sur mobile, redirige vers la page Chat IA compl�te.
- **Minuteur flottant** : Lance un minuteur depuis la page Outils ? Minuteur � une barre discr�te reste visible dans toute l'application tant que le minuteur tourne.

### Collaboration
- **Partage en temps r�el** des listes de courses (WebSocket)
- **Export PDF** (planning, courses, recettes, budget)
- **Export iCal** pour synchronisation avec calendriers externes

### Mobile-First
- Interface responsive optimis�e mobile
- Navigation bottom bar sur petits �crans (Accueil, Cuisine, Famille, Maison, Ma Semaine)
- Gestes tactiles intuitifs

### S�curit�
- Authentification JWT s�curis�e
- Row Level Security (RLS) Supabase
- Chiffrement des donn�es sensibles (mots de passe)
- Rate limiting API (protection DDoS)

---

## ?? D�marrage rapide

1. **[Cr�er un compte](./getting-started.md#inscription)** � Inscription rapide en 2 minutes
2. **[Explorer le dashboard](./getting-started.md#dashboard)** � Vue d'ensemble de vos donn�es
3. **[Ouvrir �Ma Semaine�](./FAQ.md#navigation)** � Vue unifi�e de toute la semaine
4. **[Ajouter votre premi�re recette](./getting-started.md#recettes)** � Commencez � construire votre biblioth�que
5. **[G�n�rer un planning IA](./getting-started.md#planning-ia)** � Laissez l'IA planifier vos repas

---

## ?? Screenshots

Voir le dossier [`screenshots/`](./screenshots/) pour des captures d'�cran de tous les modules.

---

## ?? Besoin d'aide ?

- **[FAQ](./FAQ.md)** � Questions fr�quentes et solutions
- **Support** � Contactez-nous via [contact@assistant-matanne.fr](mailto:contact@assistant-matanne.fr)
- **GitHub Issues** � Signalez un bug ou proposez une fonctionnalit�

---

## ?? Acc�s

- **URL Production** : https://assistant-matanne.vercel.app
- **Compatibilit�** : Chrome, Firefox, Safari, Edge (derni�res versions)
- **Mobile** : iOS 14+, Android 10+

---

**Version** : 1.0.0  
**Derni�re mise � jour** : Mars 2026
