# ?? Analyse Compl�te � Assistant Matanne

> **Date**: 1er Avril 2026
> **Scope**: Backend (FastAPI/Python) + Frontend (Next.js 16) + SQL + Tests + Docs + Int�grations
> **Objectif**: Audit exhaustif, plan d'action, axes d'am�lioration

---

## Table des mati�res

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Inventaire des modules](#2-inventaire-des-modules)
3. [Bugs et probl�mes d�tect�s](#3-bugs-et-probl�mes-d�tect�s)
4. [Gaps et fonctionnalit�s manquantes](#4-gaps-et-fonctionnalit�s-manquantes)
5. [Consolidation SQL](#5-consolidation-sql)
6. [Interactions intra-modules](#6-interactions-intra-modules)
7. [Interactions inter-modules](#7-interactions-inter-modules)
8. [Opportunit�s IA](#8-opportunit�s-ia)
9. [Jobs automatiques (CRON)](#9-jobs-automatiques-cron)
10. [Notifications � WhatsApp, Email, Push](#10-notifications--whatsapp-email-push)
11. [Mode Admin manuel](#11-mode-admin-manuel)
12. [Couverture de tests](#12-couverture-de-tests)
13. [Documentation](#13-documentation)
14. [Organisation et architecture](#14-organisation-et-architecture)
15. [Am�liorations UI/UX](#15-am�liorations-uiux)
16. [Visualisations 2D et 3D](#16-visualisations-2d-et-3d)
17. [Simplification du flux utilisateur](#17-simplification-du-flux-utilisateur)
18. [Axes d'innovation](#18-axes-dinnovation)
19. [Plan d'action prioris�](#19-plan-daction-prioris�)

---

## 1. Vue d'ensemble du projet

### Chiffres cl�s

| M�trique | Valeur |
| ---------- | -------- |
| Routes API (endpoints) | ~250+ |
| Routeurs FastAPI | 38 |
| Mod�les SQLAlchemy (ORM) | 100+ (32 fichiers) |
| Sch�mas Pydantic | ~150+ (25 fichiers) |
| Tables SQL | 80+ |
| Pages frontend | ~60+ |
| Composants React | 208+ |
| Clients API frontend | 34 |
| Hooks React custom | 15 |
| Stores Zustand | 4 |
| Sch�mas Zod | 22 |
| Fichiers de tests (backend) | 74+ |
| Fichiers de tests (frontend) | 71 |
| CRON jobs | 68+ |
| Bridges inter-modules | 21 |
| Middlewares | 7 couches |
| WebSockets | 5 impl�mentations |
| Canaux de notification | 4 (push, ntfy, WhatsApp, email) |

### Stack technique

| Couche | Technologie |
| -------- | ------------- |
| Backend | Python 3.13+, FastAPI 0.109, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Next.js 16.2.1, React 19, TypeScript 5, Tailwind CSS v4 |
| Base de donn�es | Supabase PostgreSQL, migrations SQL-file |
| IA | Mistral AI (client custom + cache s�mantique + circuit breaker) |
| �tat frontend | TanStack Query v5, Zustand 5 |
| Charts | Recharts 3.8, Chart.js 4.5 |
| 3D | Three.js 0.183, @react-three/fiber 9.5 |
| Cartes | Leaflet 1.9, react-leaflet 5.0 |
| Tests backend | pytest, SQLite in-memory |
| Tests frontend | Vitest 4.1, Testing Library, Playwright |
| Monitoring | Prometheus metrics, Sentry |
| Notifications | ntfy.sh, Web Push VAPID, Meta WhatsApp Cloud, Resend |

---

## 2. Inventaire des modules

### Backend � Modules par domaine

| Module | Routes | Services | Bridges | CRON | Tests | Statut |
| -------- | -------- | ---------- | --------- | ------ | ------- | -------- |
| ??? **Cuisine/Recettes** | 20 endpoints | RecetteService, ImportService | 7 | 5 | ? Complet | ? Mature |
| ?? **Courses** | 20 endpoints | CoursesService | 3 | 3 | ? Complet | ? Mature |
| ?? **Inventaire** | 14 endpoints | InventaireService | 4 | 3 | ? Complet | ? Mature |
| ?? **Planning** | 15 endpoints | PlanningService (5 sous-modules) | 5 | 4 | ? Complet | ? Mature |
| ????? **Batch Cooking** | 8 endpoints | BatchCookingService | 1 | 1 | ? OK | ? Stable |
| ?? **Anti-Gaspillage** | 6 endpoints | AntiGaspillageService | 2 | 2 | ? OK | ? Stable |
| ?? **Suggestions IA** | 4 endpoints | BaseAIService | 0 | 0 | ? OK | ? Stable |
| ?? **Famille/Jules** | 20 endpoints | JulesAIService | 7 | 5 | ? Complet | ? Mature |
| ?? **Maison** | 15+ endpoints | MaisonService | 4 | 6 | ? OK | ? Stable |
| ?? **Habitat** | 10 endpoints | HabitatService | 0 | 2 | ?? Partiel | ?? En cours |
| ?? **Jeux** | 12 endpoints | JeuxService | 1 | 3 | ? OK | ? Stable |
| ??? **Calendriers** | 6 endpoints | CalendrierService | 2 | 2 | ?? Partiel | ?? En cours |
| ?? **Dashboard** | 3 endpoints | DashboardService | 0 | 0 | ? OK | ? Stable |
| ?? **Documents** | 6 endpoints | DocumentService | 1 | 1 | ?? Partiel | ?? En cours |
| ?? **Utilitaires** | 10+ endpoints | Notes, Journal, Contacts | 1 | 0 | ?? Partiel | ?? En cours |
| ?? **IA Avanc�e** | 14 endpoints | Multi-service | 0 | 0 | ?? Partiel | ?? En cours |
| ?? **Voyages** | 8 endpoints | VoyageService | 2 | 1 | ?? Partiel | ?? En cours |
| ? **Garmin** | 5 endpoints | GarminService | 1 | 1 | ?? Minimal | ?? En cours |
| ?? **Auth / Admin** | 15+ endpoints | AuthService | 0 | 0 | ? OK | ? Stable |
| ?? **Export PDF** | 3 endpoints | RapportService | 0 | 0 | ?? Partiel | ?? En cours |
| ?? **Push / Webhooks** | 8 endpoints | NotificationService | 0 | 5 | ?? Partiel | ?? En cours |
| ?? **Automations** | 6 endpoints | AutomationsEngine | 0 | 1 | ?? Partiel | ?? En cours |

### Frontend � Pages par module

| Module | Pages | Composants sp�cifiques | Tests | Statut |
| -------- | ------- | ------------------------ | ------- | -------- |
| ??? **Cuisine** | 12 pages (recettes, planning, courses, inventaire, batch, anti-gasp, frigo, nutrition) | ~20 | ? 8 fichiers | ? Mature |
| ?? **Famille** | 10 pages (jules, activit�s, routines, budget, anniversaires, weekend, contacts, docs) | ~8 | ?? 3 fichiers | ?? Gaps |
| ?? **Maison** | 8 pages (projets, charges, entretien, jardin, stocks, �nergie, artisans, visualisation) | ~15 | ?? 2 fichiers | ?? Gaps |
| ?? **Habitat** | 3 pages (hub, veille-immo, sc�narios) | ~6 | ?? 1 fichier | ?? Gaps |
| ?? **Jeux** | 7 pages (paris, loto, euromillions, performance, bankroll, OCR) | ~12 | ? 5 fichiers | ? OK |
| ?? **Planning** | 2 pages (hub, timeline) | ~3 | ? 2 fichiers | ? OK |
| ?? **Outils** | 6 pages (chat-ia, notes, minuteur, m�t�o, nutritionniste, assistant-vocal) | ~5 | ? 6 fichiers | ? OK |
| ?? **Param�tres** | 3 pages + 7 onglets | ~7 | ?? 1 fichier | ?? Gaps |
| ?? **Admin** | 10 pages (jobs, users, services, events, cache, IA, SQL, flags, WhatsApp, notif) | ~5 | ?? 2 fichiers | ?? Gaps |

---

## 3. Bugs et probl�mes d�tect�s

### ?? Critiques

| # | Bug / Probl�me | Module | Impact | Fichier |
| --- | ---------------- | -------- | -------- | --------- |
| B1 | **API_SECRET_KEY random par process** � En multi-process (production), chaque worker g�n�re un secret diff�rent ? les tokens d'un worker sont invalides sur un autre | Auth | Tokens invalides en production multi-worker | `src/api/auth.py` |
| B2 | **WebSocket courses sans fallback HTTP** � Si le WebSocket est indisponible (proxy restrictif, mobile 3G), pas de polling HTTP alternatif ? la collaboration temps r�el casse silencieusement | Courses | Perte de sync en temps r�el | `utiliser-websocket-courses.ts` |
| B3 | **Promesse non g�r�e dans l'intercepteur auth** � Le refresh token peut timeout et laisser l'utilisateur bloqu� (ni connect� ni d�connect�) | Frontend Auth | UX d�grad�e sur token expir� | `api/client.ts` |
| B4 | **Event bus en m�moire uniquement** � L'historique des �v�nements est perdu au red�marrage du serveur, impossible de rejouer des �v�nements apr�s un crash | Core Events | Perte d'audit trail | `src/services/core/events/` |

### ?? Importants

| # | Bug / Probl�me | Module | Impact | Fichier |
| --- | ---------------- | -------- | -------- | --------- |
| B5 | **Rate limiting en m�moire non born�** � Le stockage en m�moire cro�t avec chaque IP/user unique sans �viction ? fuite m�moire lente | Rate Limiting | Memory leak en production long | `rate_limiting/storage.py` |
| B6 | **Maintenance mode avec cache 5s** � La mise en maintenance peut prendre jusqu'� 5 secondes pour �tre effective ? requ�tes accept�es pendant la transition | Admin | Requ�tes pendant maintenance | `src/api/main.py` |
| B7 | **X-Forwarded-For spoofable** � L'IP client est extraite du header sans v�rifier la confiance du proxy ? bypass possible du rate limiting | S�curit� | Rate limiting contournable | `rate_limiting/limiter.py` |
| B8 | **Metrics capped � 500 endpoints / 1000 samples** � Les percentiles (p95, p99) deviennent impr�cis apr�s beaucoup de requ�tes | Monitoring | M�triques d�grad�es | `src/api/utils/metrics.py` |
| B9 | **Multi-turn WhatsApp sans persistence d'�tat** � La state machine de planning WhatsApp perd son �tat entre les messages ? flux interrompu si l'utilisateur tarde | WhatsApp | Conversation WhatsApp cass�e | `webhooks_whatsapp.py` |
| B10 | **CORS vide en production** � Si CORS_ORIGINS n'est pas configur�, toutes les origines sont bloqu�es mais aucune erreur explicite | Config | Frontend bloqu� en prod sans config | `src/api/main.py` |

### ?? Mineurs

| # | Bug / Probl�me | Module | Impact |
| --- | ---------------- | -------- | -------- |
| B11 | **ResponseValidationError** logg� en 500 sans contexte debug ? difficile � diagnostiquer | API | DX d�grad�e |
| B12 | **Pagination cursor** � Les suppressions concurrentes peuvent sauter des enregistrements | Pagination | Donn�es manqu�es rarement |
| B13 | **ServiceMeta auto-sync wrappers** � La g�n�ration automatique de wrappers sync pour les m�thodes async n'est pas test�e exhaustivement | Core Services | Bugs potentiels subtils |
| B14 | **Sentry int�gration � 50%** � Configur� mais ne capture pas tous les erreurs frontend | Frontend | Erreurs non trac�es |

---

## 4. Gaps et fonctionnalit�s manquantes

### Par module

#### ??? Cuisine

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G1 | **Drag-drop recettes dans planning** | Moyenne | 2j | Le planning repas n'a pas de drag-drop pour r�organiser les repas ? UX fastidieuse |
| G2 | **Import recettes par photo** | Moyenne | 3j | L'import URL/PDF existe mais pas l'import par photo d'un livre de cuisine (Pixtral disponible c�t� IA) |
| G3 | **Partage recette via WhatsApp** | Basse | 1j | Le partage existe par lien mais pas d'envoi direct WhatsApp avec preview |
| G4 | **Veille prix articles d�sir�s** | Moyenne | 3j | Scraper une API de suivi de prix (type Dealabs/Idealo) pour des articles ajout�s � une wishlist + alertes soldes automatiques via `calendrier_soldes.json` d�j� pr�sent. Pas de saisie manuelle de prix � chaque achat (trop fastidieux) |
| G5 | **Mode hors-ligne courses** | Haute | 3j | PWA install�e mais pas de cache offline pour consulter la liste en magasin sans r�seau |

#### ?? Famille

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G6 | **Pr�vision budget IA** | Haute | 3j | Le budget famille n'a que le r�sum� mensuel, pas de pr�diction "fin de mois" avec IA |
| G7 | **Timeline Jules visuelle** | Moyenne | 2j | Les jalons de d�veloppement existent mais pas de frise chronologique visuelle interactive |
| G8 | **Export calendrier anniversaires** | Basse | 1j | Les anniversaires ne s'exportent pas vers Google Calendar |
| G9 | **Photos souvenirs li�es aux activit�s** | Moyenne | 2j | Les activit�s familiales n'ont pas d'upload photo pour le journal |

#### ?? Maison

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G10 | **Plan 3D interactif limit�** | Haute | 5j | Le composant Three.js existe mais n'est pas connect� aux donn�es r�elles (t�ches par pi�ce, consommation �nergie) |
| G11 | **Historique �nergie avec graphes** | Moyenne | 2j | Les relev�s existent mais pas de visualisation tendancielle (courbes mois/ann�e) |
| G12 | **Catalogue artisans enrichi** | Basse | 2j | Pas d'avis/notes sur les artisans, pas de recherche par m�tier |
| G13 | **Devis comparatif** | Moyenne | 3j | Pas de visualisation comparative des devis pour un m�me projet |

#### ?? Jeux

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G14 | **Graphique ROI temporel** | Haute | 2j | Le ROI global existe mais pas la courbe d'�volution mensuelle du ROI paris sportifs |
| G15 | **Alertes cotes temps r�el** | Moyenne | 3j | Pas d'alerte quand une cote atteint un seuil d�fini par l'utilisateur |
| G16 | **Comparaison strat�gies loto** | Basse | 2j | Le backtest existe mais pas la comparaison c�te � c�te de 2+ strat�gies |

#### ?? Planning

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G17 | **Sync Google Calendar bidirectionnelle** | Haute | 4j | L'export iCal existe, la sync Google est � ~60% ? pas de push automatique des repas/activit�s vers Google Calendar |
| G18 | **Planning familial consolid� visuel** | Moyenne | 3j | Pas de vue Gantt compl�te m�lant repas + activit�s + entretien + anniversaires |
| G19 | **R�currence d'�v�nements** | Moyenne | 2j | Pas de gestion native "tous les mardis" pour les routines dans le calendrier |

#### ?? G�n�ral

| # | Gap | Priorit� | Effort | Description |
| --- | ----- | ---------- | -------- | ------------- |
| G20 | **Recherche globale incompl�te** | Haute | 3j | La recherche globale (Ctrl+K) ne couvre pas tous les modules (manque: notes, jardin, contrats) |
| G21 | **Mode hors-ligne (PWA)** | Haute | 5j | Service Worker enregistr� mais pas de strat�gie de cache offline structur�e |
| G22 | **Onboarding interactif** | Moyenne | 3j | Le composant tour-onboarding existe mais n'est pas activ�/configur� avec les �tapes du parcours utilisateur |
| G23 | **Export donn�es backup incomplet** | Moyenne | 2j | L'export JSON fonctionne mais l'import/restauration UI est incomplet |

---

## 5. Consolidation SQL

### �tat actuel

```
sql/
+-- INIT_COMPLET.sql          # Auto-g�n�r� (4922 lignes, 18 fichiers schema)
+-- schema/                   # 18 fichiers organis�s (01_extensions ? 99_footer)
�   +-- 01_extensions.sql
�   +-- 02_types_enums.sql
�   +-- 03_system_tables.sql
�   +-- 04_cuisine.sql
�   +-- 05_famille.sql
�   +-- 06_maison.sql
�   +-- 07_jeux.sql
�   +-- 08_habitat.sql
�   +-- 09_voyages.sql
�   +-- 10_notifications.sql
�   +-- 11_gamification.sql
�   +-- 12_automations.sql
�   +-- 13_utilitaires.sql
�   +-- 14_indexes.sql
�   +-- 15_rls_policies.sql
�   +-- 16_triggers.sql
�   +-- 17_views.sql
�   +-- 99_footer.sql
+-- migrations/               # 7 fichiers (V003-V008) + README
    +-- V003_*.sql
    +-- V004_*.sql
    +-- V005_phase2_sql_consolidation.sql
    +-- V006_*.sql
    +-- V007_*.sql
    +-- V008_phase4.sql
```

### Actions recommand�es (mode dev, pas de versioning)

| # | Action | Priorit� | D�tail |
| --- | -------- | ---------- | -------- |
| S1 | **Reg�n�rer INIT_COMPLET.sql** | Haute | Ex�cuter `python scripts/db/regenerate_init.py` pour s'assurer que le fichier monolithique est synchronis� avec les 18 fichiers schema |
| S2 | **Audit ORM ? SQL** | Haute | Ex�cuter `python scripts/audit_orm_sql.py` pour d�tecter les divergences entre les mod�les SQLAlchemy et les tables SQL |
| S3 | **Consolider les migrations en un seul schema** | Haute | En mode dev, fusionner les 7 migrations dans les fichiers schema correspondants et r�g�n�rer INIT_COMPLET.sql. Une seule source de v�rit� |
| S4 | **V�rifier les index manquants** | Moyenne | Certaines colonnes fr�quemment requ�t�es (user_id, date, statut) peuvent manquer d'index dans `14_indexes.sql` |
| S5 | **Nettoyer les tables inutilis�es** | Basse | V�rifier si toutes les 80+ tables ont un mod�le ORM et une route API correspondante |
| S6 | **Vues SQL non utilis�es** | Basse | V�rifier que les vues dans `17_views.sql` sont r�ellement utilis�es par le backend |

### Proposition de workflow simplifi�

```
1. Modifier le fichier schema appropri� (ex: sql/schema/04_cuisine.sql)
2. Ex�cuter: python scripts/db/regenerate_init.py
3. Appliquer: ex�cuter INIT_COMPLET.sql sur Supabase (SQL Editor)
4. V�rifier: python scripts/audit_orm_sql.py
```

> Pas de migrations ni de versioning en phase dev. Un seul INIT_COMPLET.sql fait foi.

---

## 6. Interactions intra-modules

### Cuisine (interne)

```
Recettes ---- planifi�es ---? Planning
    �                            �
    �                            +-- g�n�re --? Courses
    �                            �
    +-- version Jules --? portions adapt�es
                                 �
Inventaire ?------ checkout ----+
    �
    +-- p�remption --? Anti-Gaspillage --? Recettes rescue
    �
    +-- stock bas --? Automation --? Courses auto
    
Batch Cooking ?-- planning semaine -- pr�pare --? bloque planning
```

**? Bien connect�** � Le module cuisine a le plus d'interactions internes, toutes fonctionnelles.

**?? � am�liorer:**
- Le checkout courses ? inventaire pourrait mettre � jour les prix moyens automatiquement
- Le batch cooking manque un "mode robot" intelligent qui optimise l'ordre des �tapes par appareil

### Famille (interne)

```
Jules profil --? jalons developpement
    �               �
    �               +-- notifications anniversaire jalon
    �
Budget ?---- d�penses cat�goris�es
    �
Routines --? check quotidien --? gamification (limit�e)
    �
Anniversaires --? checklist --? budget cadeau
    �
Documents --? expiration --? rappels calendrier
```

**?? � am�liorer:**
- Jules jalons ? suggestions d'activit�s adapt�es � l'�ge (IA contextuelle)
- Budget anomalies ? pas de notification proactive ("tu d�penses +30% en restaurants ce mois")
- Routines ? pas de tracking de compl�tion visuel (streak)

### Maison (interne)

```
Projets --? t�ches --? devis --? d�penses
    �
Entretien --? calendrier --? produits n�cessaires
    �
Jardin --? arrosage/r�colte --? saison
    �
�nergie --? relev�s compteurs --? historique
    �
Stocks (cellier) --? consolid� avec inventaire cuisine
```

**?? � am�liorer:**
- Projets ? pas de timeline visuelle Gantt des travaux
- �nergie ? pas de graphe d'�volution ni de comparaison N vs N-1
- Entretien ? pas de suggestions IA proactives ("votre chaudi�re a 8 ans, pr�voir r�vision")

---

## 7. Interactions inter-modules

### Bridges existants (21 actifs) ?

```
+----------+     +-----------+     +----------+
� CUISINE  �?---?� PLANNING  �?---?� COURSES  �
�          �     �           �     �          �
� recettes �     � repas     �     � listes   �
� inventaire�    � semaine   �     � articles �
� nutrition �    � conflits  �     �          �
� batch     �    �           �     �          �
+----------+     +-----------+     +----------+
     �                 �                 �
     �    +------------�                 �
     �    �            �                 �
+----?----?--+   +----?-----+     +----?-----+
�  FAMILLE   �   �  MAISON  �     �  BUDGET  �
�            �   �          �     �          �
� jules      �   � entretien�     � famille  �
� routines   �   � jardin   �     � jeux (s�par�)
� annivers.  �   � �nergie  �     � maison   �
� documents  �   � projets  �     �          �
� weekend    �   � stocks   �     �          �
+------------+   +----------+     +----------+
     �                �
     �    +-----------�
     �    �           �
+----?----?--+   +---?------+
� CALENDRIER �   �  JEUX    �
�            �   �          �
� google cal �   � paris    �
� �v�nements �   � loto     �
�            �   � bankroll �
+------------+   +----------+
```

### Bridges inter-modules d�taill�s

| # | Bridge | De ? Vers | Fonctionnel | Description |
| --- | -------- | ----------- | ------------- | ------------- |
| 1 | `inter_module_inventaire_planning` | Stock ? Planning | ? | Priorise recettes par ingr�dients disponibles |
| 2 | `inter_module_jules_nutrition` | Jules ? Recettes | ? | Portions adapt�es �ge, filtrage allerg�nes |
| 3 | `inter_module_saison_menu` | Saison ? Planning | ? | Produits frais de saison dans les suggestions |
| 4 | `inter_module_courses_budget` | Courses ? Budget | ? | Suivi impact budget des courses |
| 5 | `inter_module_batch_inventaire` | Batch ? Inventaire | ? | Mise � jour stock apr�s batch cooking |
| 6 | `inter_module_planning_voyage` | Voyage ? Planning | ? | Exclusion planning pendant les voyages |
| 7 | `inter_module_peremption_recettes` | P�remption ? Recettes | ? | Recettes rescue des produits bient�t p�rim�s |
| 8 | `inter_module_documents_calendrier` | Documents ? Calendrier | ? | Rappels renouvellement docs expir�s |
| 9 | `inter_module_meteo_activites` | M�t�o ? Activit�s | ? | Suggestions activit�s selon m�t�o |
| 10 | `inter_module_weekend_courses` | Weekend ? Courses | ? | Liste courses pour activit�s weekend |
| 11 | `inter_module_voyages_budget` | Voyages ? Budget | ? | Sync co�ts voyage ? budget |
| 12 | `inter_module_anniversaires_budget` | Anniversaires ? Budget | ? | Tracking d�penses cadeaux/f�tes |
| 13 | `inter_module_budget_jeux` | Jeux ? Budget | ? (info) | Sync pour info uniquement (budgets s�par�s volontairement) |
| 14 | `inter_module_garmin_health` | Garmin ? Dashboard | ? | Score bien-�tre int�grant fitness |
| 15 | `inter_module_entretien_courses` | Entretien ? Courses | ? | Produits m�nagers pour t�ches � venir |
| 16 | `inter_module_jardin_entretien` | Jardin ? Entretien | ? | Coordination jardinage/entretien |
| 17 | `inter_module_charges_energie` | Charges ? �nergie | ? | Budget insights factures |
| 18 | `inter_module_energie_cuisine` | �nergie ? Cuisine | ? | Optimisation cuisson heures creuses |
| 19 | `inter_module_chat_contexte` | Tous ? Chat IA | ? | Contexte multi-module inject� dans le chat |
| 20 | `inter_module_voyages_calendrier` | Voyages ? Calendrier | ? | Sync dates voyage dans calendrier |
| 21 | `inter_module_garmin_planning` | Garmin ? Planning | ?? | Partiellement connect� |

### Interactions manquantes � impl�menter

| # | Interaction propos�e | De ? Vers | Valeur | Effort |
| --- | --------------------- | ----------- | -------- | -------- |
| I1 | **R�colte jardin ? Recettes semaine suivante** | Jardin ? Planning | ? Accept�e | 2j |
| I2 | **Entretien r�current ? Planning unifi�** | Entretien ? Planning global | Haute | 2j |
| I3 | **Budget anomalie ? Notification proactive** | Budget ? Notifications | Haute | 2j |
| I4 | **Voyages ? Inventaire** (d�stockage avant d�part) | Voyages ? Inventaire | Moyenne | 1j |
| I5 | **Documents expir�s ? Dashboard alerte** | Documents ? Dashboard | Haute | 1j |
| I6 | **Anniversaire proche ? Suggestions cadeaux IA** | Anniversaires ? IA | Moyenne | 2j |
| I7 | **Contrats/Garanties ? Dashboard widgets** | Maison ? Dashboard | Moyenne | 1j |
| I8 | **M�t�o ? Entretien maison** (ex: gel ? penser au jardin) | M�t�o ? Maison | Moyenne | 2j |
| I9 | **Planning sport Garmin ? Planning repas** (adapter alimentation) | Garmin ? Cuisine | Moyenne | 3j |
| I10 | **Courses historique ? Pr�diction prochaine liste** | Courses ? IA | Haute | 3j |

---

## 8. Opportunit�s IA

### IA actuellement en place ?

| Fonctionnalit� | Service | Module | Statut |
| ---------------- | --------- | -------- | -------- |
| Suggestions recettes | BaseAIService | Cuisine | ? Fonctionnel |
| G�n�ration planning IA | PlanningService | Planning | ? Fonctionnel |
| Recettes rescue anti-gaspi | AntiGaspillageService | Cuisine | ? Fonctionnel |
| Batch cooking optimis� | BatchCookingService | Cuisine | ? Fonctionnel |
| Suggestions weekend | WeekendAIService | Famille | ? Fonctionnel |
| Score bien-�tre | DashboardService | Dashboard | ? Fonctionnel |
| Chat IA contextualis� | AssistantService | Outils | ? Fonctionnel |
| Version Jules recettes | JulesAIService | Famille | ? Fonctionnel |
| 14 endpoints IA avanc�e | Multi-services | IA Avanc�e | ?? Partiel |

### Nouvelles opportunit�s IA � exploiter

| # | Opportunit� | Module(s) | Description | Priorit� | Effort |
| --- | ------------- | ----------- | ------------- | ---------- | -------- |
| IA1 | **Pr�diction courses intelligente** | Courses + Historique | Analyser l'historique des courses (fr�quence, quantit�s) pour pr�-remplir la prochaine liste. "Tu ach�tes du lait tous les 5 jours, il est temps d'en commander" | ?? Haute | 3j |
| IA2 | **Planificateur adaptatif m�t�o+stock+budget** | Planning + M�t�o + Inventaire + Budget | L'endpoint existe mais sous-utilis�. Exploiter : m�t�o chaude ? salades/grillades, stock important de tomates ? les utiliser, budget serr� ? recettes avec ce qu'on a | ?? Haute | 2j |
| IA3 | **Diagnostic pannes maison** | Maison | Photo d'un appareil en panne ? diagnostic IA (Pixtral) + suggestion d'action (appeler artisan X, pi�ce � commander) | ?? Moyenne | 3j |
| IA4 | **Assistant vocal contextuel** | Tous | Google Assistant connect� mais capacit�s limit�es � quelques intents. �tendre: "Hey Google, qu'est-ce qu'on mange ce soir ?" ? lecture du planning + suggestions si vide | ?? Moyenne | 4j |
| IA5 | **R�sum� hebdomadaire intelligent** | Dashboard | R�sum� IA de la semaine: repas cuisin�s, t�ches accomplies, budget, scores, prochaines �ch�ances. Format narratif agr�able � lire | ?? Haute | 2j |
| IA6 | **Optimisation �nergie pr�dictive** | Maison/�nergie | Analyser les relev�s compteurs + m�t�o ? pr�dire la facture du mois + sugg�rer des �conomies cibl�es | ?? Moyenne | 3j |
| IA7 | **Analyse nutritionnelle photo** | Cuisine/Nutrition | Prendre en photo un plat ? l'IA estime les calories/macros/micros (Pixtral) | ?? Moyenne | 3j |
| IA8 | **Suggestion d'organisation batch cooking** | Batch Cooking | Analyser le planning de la semaine + les appareils dispo (robot, four, etc.) ? proposer un plan de batch cooking optimal avec timeline parall�le | ?? Haute | 3j |
| IA9 | **Jules: conseil d�veloppement proactif** | Famille/Jules | "� l'�ge de Jules, les enfants commencent �..." � suggestions d'activit�s/jouets/apprentissages adapt�s en fonction des jalons franchis vs attendus | ?? Moyenne | 2j |
| IA10 | **Auto-cat�gorisation budget** | Budget | Cat�goriser automatiquement les d�penses � partir du nom du commer�ant/article (pas d'OCR ticket, juste texte) | ?? Moyenne | 2j |
| IA11 | **G�n�ration checklist voyage** | Voyages | � partir de la destination, dates, participants ? checklist compl�te IA (v�tements, documents, r�servations, vaccins si besoin) | ?? Moyenne | 2j |
| IA12 | **Score �cologique repas** | Cuisine | �valuer l'impact �cologique du planning repas (saisonnalit�, distance parcourue des aliments, prot�ines v�g�tales vs animales) | ?? Basse | 2j |

---

## 9. Jobs automatiques (CRON)

### Jobs existants (68+)

#### Quotidiens

| Job | Horaire | Action | Canaux | Modules impliqu�s |
| ----- | --------- | -------- | -------- | ------------------- |
| `digest_whatsapp_matinal` | 07h30 | Repas du jour, t�ches, p�remptions, boutons interactifs | WhatsApp | Cuisine, Maison, Inventaire |
| `rappels_famille` | 07h00 | Anniversaires, documents, jalons Jules | WhatsApp + Push + ntfy | Famille |
| `rappels_maison` | 08h00 | Garanties, contrats, entretien | Push + ntfy | Maison |
| `digest_ntfy` | 09h00 | Digest compact | ntfy | Multi-module |
| `rappel_courses` | 18h00 | Revue liste interactive | WhatsApp | Courses |
| `push_contextuel_soir` | 18h00 | Pr�paration lendemain | Push | Planning |
| `alerte_stock_bas` | 07h00 | Stock bas ? ajout auto courses | Automation | Inventaire ? Courses |
| `sync_google_calendar` | 23h00 | Push planning vers Google Cal | - | Planning ? Calendrier |
| `garmin_sync_matinal` | 06h00 | Sync donn�es Garmin | - | Garmin |
| `automations_runner` | Toutes les 5 min | Ex�cution r�gles automation | Variable | Automations |

#### Hebdomadaires

| Job | Jour/Horaire | Action | Canaux |
| ----- | ------------- | -------- | -------- |
| `resume_hebdo` | Lundi 07h30 | R�sum� semaine pass�e | ntfy, email, WhatsApp |
| `score_weekend` | Vendredi 17h00 | Contexte weekend (m�t�o, activit�s, suggestions) | WhatsApp |
| `score_bien_etre_hebdo` | Dimanche 20h00 | Score consolid� bien-�tre | Dashboard |
| `points_famille_hebdo` | Dimanche 20h00 | Points gamification | Dashboard |
| `sync_openfoodfacts` | Dimanche 03h00 | Rafra�chir cache produits | - |

#### Mensuels

| Job | Jour/Horaire | Action | Canaux |
| ----- | ------------- | -------- | -------- |
| `rapport_mensuel_budget` | 1er 08h15 | R�sum� budget + tendances | Email |
| `controle_contrats_garanties` | 1er 09h00 | Alertes renouvellement | Push + ntfy |
| `rapport_maison_mensuel` | 1er 09h30 | R�sum� entretien maison | Email |

### Nouveaux jobs propos�s

| # | Job propos� | Fr�quence | Modules | Description | Priorit� |
| --- | ------------- | ----------- | --------- | ------------- | ---------- |
| J1 | **`prediction_courses_hebdo`** | Vendredi 16h | Courses + IA | Pr�-g�n�rer une liste de courses pr�dictive pour la semaine suivante bas�e sur l'historique | ?? Haute |
| J2 | **`planning_auto_semaine`** | Dimanche 19h | Planning + IA | Si le planning de la semaine suivante est vide, proposer un planning IA via WhatsApp (valider/modifier/rejeter) | ?? Haute |
| J3 | **`nettoyage_cache_export`** | Quotidien 02h | Export | Supprimer les fichiers d'export > 7 jours dans data/exports/ | ?? Moyenne |
| J4 | **`rappel_jardin_saison`** | Hebdo (Lundi) | Jardin | "C'est la saison pour planter les tomates" � rappels saisonniers intelligents | ?? Moyenne |
| J5 | **`sync_budget_consolidation`** | Quotidien 22h | Budget | Consolider les d�penses de tous les modules (courses, maison, jeux info, voyages) en un seul suivi | ?? Moyenne |
| J6 | **`verification_sante_systeme`** | Toutes les heures | Admin | V�rifier DB, cache, IA, et envoyer alerte ntfy si un service est down | ?? Moyenne |
| J7 | **`backup_auto_json`** | Hebdo (Dimanche 04h) | Admin | Export automatique de toutes les donn�es en JSON (backup) | ?? Basse |
| J8 | **`tendances_nutrition_hebdo`** | Dimanche 18h | Cuisine/Nutrition | Analyser les repas de la semaine ? score nutritionnel + recommandations | ?? Moyenne |
| J9 | **`alertes_budget_seuil`** | Quotidien 20h | Budget | V�rifier si une cat�gorie d�passe 80% du budget mensuel ? alerte proactive | ?? Haute |
| J10 | **`rappel_activite_jules`** | Quotidien 09h | Famille | "Jules a 18 mois aujourd'hui ! Voici les activit�s recommand�es pour son �ge" | ?? Moyenne |

---

## 10. Notifications � WhatsApp, Email, Push

### Architecture actuelle

```
                    +-----------------+
                    �  �v�nement      �
                    �  (CRON / User)  �
                    +-----------------+
                             �
                    +--------?--------+
                    �  Router de      �
                    �  notifications  �
                    +-----------------+
                             �
            +----------------+----------------+
            �                �                �
    +-------?------+ +------?-------+ +-----?------+
    �  Web Push    � �   ntfy.sh    � � WhatsApp   �
    �  (VAPID)     � �  (open src)  � � (Meta API) �
    +--------------+ +--------------+ +------------+
                             �
                    +--------?--------+
                    �    Email        �
                    �   (Resend)      �
                    +-----------------+
    
    Failover: Push ? ntfy ? WhatsApp ? Email
    Throttle: 2h par type d'�v�nement par canal
```

### Am�liorations WhatsApp propos�es

| # | Am�lioration | Priorit� | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| W1 | **Persistence �tat conversation** | ?? Haute | 2j | Le state machine planning perd l'�tat entre les messages. Stocker dans Redis/DB pour permettre des conversations multi-tour |
| W2 | **Commandes texte enrichies** | ?? Haute | 3j | Supporter: "ajoute du lait � la liste", "qu'est-ce qu'on mange demain", "combien j'ai d�pens� ce mois" ? parsing NLP via Mistral |
| W3 | **Boutons interactifs �tendus** | ?? Moyenne | 2j | Ajouter des boutons quick-reply pour: valider courses, noter une d�pense, signaler un probl�me maison |
| W4 | **Photo ? action** | ?? Moyenne | 3j | Envoyer une photo de plante malade ? diagnostic IA. Photo d'un plat ? identification + ajout recette |
| W5 | **R�sum� quotidien personnalisable** | ?? Moyenne | 2j | Permettre � l'utilisateur de choisir quelles infos recevoir dans le digest matinal (via param�tres) |

### Am�liorations Email propos�es

| # | Am�lioration | Priorit� | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| E1 | **Templates HTML jolis** | ?? Moyenne | 2j | Les emails actuels sont basiques. Cr�er des templates HTML modernes (MJML) pour les rapports mensuels |
| E2 | **R�sum� hebdo email** | ?? Moyenne | 1j | Pas d'email hebdomadaire automatique (seulement ntfy/WhatsApp). Ajouter un email digest optionnel |
| E3 | **Alertes critiques par email** | ?? Haute | 1j | Les alertes critiques (document expir�, stock critique, budget d�pass�) devraient aussi aller par email en plus des autres canaux |

### Am�liorations Push propos�es

| # | Am�lioration | Priorit� | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| P1 | **Actions dans la notification** | ?? Moyenne | 2j | "Ajouter au courses" directement depuis la notification push (web push actions) |
| P2 | **Push conditionnel (heure calme)** | ?? Moyenne | 1j | Respecter les heures calmes configur�es dans les param�tres utilisateur |
| P3 | **Badge app PWA** | ?? Basse | 1j | Afficher le nombre de notifications non lues sur l'ic�ne PWA |

---

## 11. Mode Admin manuel

### Existant ? (tr�s complet)

L'application a d�j� un **panneau admin robuste** accessible via:
- **Frontend**: `/admin/*` (10 pages d�di�es)
- **Raccourci**: `Ctrl+Shift+A` (panneau flottant overlay)
- **Backend**: `POST /api/v1/admin/*` (20+ endpoints admin)

#### Fonctionnalit�s admin existantes

| Cat�gorie | Fonctionnalit� | Status |
| ----------- | --------------- | -------- |
| **Jobs CRON** | Lister tous les jobs + prochain run | ? |
| **Jobs CRON** | D�clencher manuellement n'importe quel job | ? |
| **Jobs CRON** | Voir l'historique d'ex�cution | ? |
| **Notifications** | Tester un canal sp�cifique (ntfy/push/email/WhatsApp) | ? |
| **Notifications** | Broadcast test sur tous les canaux | ? |
| **Event Bus** | Voir l'historique des �v�nements | ? |
| **Event Bus** | �mettre un �v�nement manuellement | ? |
| **Cache** | Voir les stats du cache | ? |
| **Cache** | Purger par pattern | ? |
| **Services** | �tat de tous les services (registre) | ? |
| **Feature Flags** | Activer/d�sactiver des features | ? |
| **Maintenance** | Mode maintenance ON/OFF | ? |
| **Simulation** | Dry-run workflows (p�remption, digest, rappels) | ? |
| **IA Console** | Tester des prompts avec contr�le temp�rature/tokens | ? |
| **Impersonation** | Switcher d'utilisateur | ? |
| **Audit Logs** | Tra�abilit� compl�te | ? |
| **Security Logs** | �v�nements s�curit� | ? |
| **SQL Views** | Browser de vues SQL | ? |
| **WhatsApp Test** | Envoyer un message WhatsApp test | ? |
| **Config** | Export/import configuration runtime | ? |

### Am�liorations propos�es

| # | Am�lioration | Priorit� | Effort | Description |
| --- | ------------- | ---------- | -------- | ------------- |
| A1 | **Console de commande rapide** | ?? Moyenne | 2j | Un champ texte dans le panneau admin pour lancer des commandes rapides: "run job rappels_famille", "clear cache recettes*", "test whatsapp" |
| A2 | **Dashboard admin temps r�el** | ?? Moyenne | 3j | WebSocket admin_logs d�j� en place � l'afficher en temps r�el sur la page admin avec filtres et auto-scroll |
| A3 | **Scheduler visuel** | ?? Moyenne | 3j | Vue timeline des 68 CRON jobs avec le prochain run, la derni�re ex�cution, et les d�pendances visuelles |
| A4 | **Replay d'�v�nements** | ?? Moyenne | 2j | Permettre de rejouer un �v�nement pass� du bus avec ses subscriber handlers |
| A5 | **Panneau admin invisible pour l'utilisateur** | ? D�j� fait | - | Le panneau est accessible uniquement via `role=admin` et `Ctrl+Shift+A`. Invisible pour l'utilisateur normal |
| A6 | **Logs en temps r�el** | ?? Moyenne | 2j | Stream les logs du serveur via WebSocket admin_logs (l'endpoint existe, le connecter � l'UI) |
| A7 | **Test E2E one-click** | ?? Basse | 3j | Bouton "Lancer test complet" qui ex�cute un sc�nario E2E (cr�er recette ? planifier ? g�n�rer courses ? checkout ? v�rifier inventaire) |

---

## 12. Couverture de tests

### Backend (Python/pytest)

| Zone | Fichiers test | Fonctions test | Couverture estim�e | Note |
| ------ | ------------- | ---------------- | --------------------- | ------ |
| Routes API (cuisine) | 8 | ~120 | ? ~85% | Bien couvert |
| Routes API (famille) | 6 | ~80 | ? ~75% | OK |
| Routes API (maison) | 5 | ~60 | ?? ~60% | Gaps sur jardin, �nergie |
| Routes API (jeux) | 2 | ~30 | ?? ~55% | Gaps sur loto, euromillions |
| Routes API (admin) | 2 | ~40 | ? ~70% | OK |
| Routes API (export/upload) | 2 | ~15 | ? ~30% | Tr�s faible |
| Routes API (webhooks) | 2 | ~10 | ? ~25% | Tr�s faible |
| Services | 20+ | ~300 | ?? ~60% | Variable |
| Core (config, db, cache) | 6 | ~200 | ?? ~55% | Cache orchestrateur faible |
| Event Bus | 1 | ~10 | ? ~20% | Tr�s faible |
| R�silience | 1 | ~15 | ?? ~40% | Manque sc�narios r�els |
| WebSocket | 1 | ~8 | ? ~25% | Edge cases manquants |
| Int�grations | 3 | ~20 | ? ~20% | Stubs mais pas end-to-end |
| **TOTAL** | **74+** | **~1000** | **?? ~55%** | **50-60% estim�** |

### Frontend (Vitest)

| Zone | Fichiers test | Couverture estim�e | Note |
| ------ | ------------- | --------------------- | ------ |
| Pages cuisine | 8 | ? ~70% | Bien couvert |
| Pages jeux | 5 | ? ~65% | OK |
| Pages outils | 6 | ? ~60% | OK |
| Pages famille | 3 | ?? ~35% | Gaps importants |
| Pages maison | 2 | ?? ~30% | Gaps importants |
| Pages admin | 2 | ?? ~30% | Gaps importants |
| Pages param�tres | 1 | ? ~15% | Tr�s faible |
| Hooks | 2 | ?? ~45% | WebSocket sous-test� |
| Stores | 4 | ? ~80% | Bien couvert |
| Composants | 12 | ?? ~40% | Variable |
| API clients | 1 | ? ~15% | Tr�s faible |
| E2E (Playwright) | Quelques | ? ~10% | Quasi inexistant |
| **TOTAL** | **71** | **?? ~40%** | **Min Vitest: 50%** |

### Tests manquants prioritaires

| # | Test � ajouter | Module | Priorit� | Description |
| --- | --------------- | -------- | ---------- | ------------- |
| T1 | **Tests export PDF** | Export | ?? Haute | V�rifier g�n�ration PDF pour courses, planning, recettes, budget |
| T2 | **Tests webhooks WhatsApp** | Notifications | ?? Haute | Tester state machine planning, parsing commandes |
| T3 | **Tests event bus scenarios** | Core | ?? Haute | Pub/sub avec wildcards, priorit�s, erreurs handlers |
| T4 | **Tests cache L1/L2/L3** | Core | ?? Moyenne | Sc�narios promotion/�viction entre niveaux |
| T5 | **Tests WebSocket edge cases** | Courses | ?? Moyenne | Reconnexion, timeout, messages malform�s |
| T6 | **Tests E2E parcours utilisateur** | Frontend | ?? Haute | Sc�nario complet: login ? cr�er recette ? planifier ? courses ? checkout |
| T7 | **Tests API clients frontend** | Frontend | ?? Moyenne | Erreurs r�seau, refresh token, pagination |
| T8 | **Tests pages param�tres** | Frontend | ?? Moyenne | Chaque onglet de param�tres |
| T9 | **Tests pages admin** | Frontend | ?? Moyenne | Jobs, services, cache, feature flags |
| T10 | **Tests Playwright accessibilit�** | Frontend | ?? Basse | axe-core sur les pages principales |

---

## 13. Documentation

### �tat actuel

| Document | Derni�re M�J | Statut | Action n�cessaire |
| ---------- | ------------- | -------- | ------------------- |
| `docs/INDEX.md` | 1 Avril 2026 | ? Courant | - |
| `docs/MODULES.md` | 1 Avril 2026 | ? Courant | - |
| `docs/API_REFERENCE.md` | 1 Avril 2026 | ? Courant | - |
| `docs/API_SCHEMAS.md` | 1 Avril 2026 | ? Courant | - |
| `docs/SERVICES_REFERENCE.md` | 1 Avril 2026 | ? Courant | - |
| `docs/SQLALCHEMY_SESSION_GUIDE.md` | 31 Mars 2026 | ? Courant | - |
| `docs/ERD_SCHEMA.md` | 31 Mars 2026 | ? Courant | - |
| `docs/ARCHITECTURE.md` | 1 Mars 2026 | ?? 1 mois | Rafra�chir avec les changements core r�cents |
| `docs/DATA_MODEL.md` | Inconnu | ?? V�rifier | Peut �tre obsol�te post-phases 8-10 |
| `docs/DEPLOYMENT.md` | Mars 2026 | ?? V�rifier | V�rifier config Railway/Vercel actuelle |
| `docs/ADMIN_RUNBOOK.md` | Inconnu | ?? V�rifier | Les 20+ endpoints admin ont-ils tous un doc ? |
| `docs/CRON_JOBS.md` | Inconnu | ?? Obsol�te | 68+ jobs, probablement plus � jour depuis phases 8-10 |
| `docs/NOTIFICATIONS.md` | Inconnu | ?? Obsol�te | Syst�me refait en phase 8 |
| `docs/AUTOMATIONS.md` | Inconnu | ?? Obsol�te | Expansion phases 8-10 |
| `docs/INTER_MODULES.md` | Inconnu | ?? V�rifier | 21 bridges � tous document�s ? |
| `docs/EVENT_BUS.md` | Inconnu | ?? V�rifier | Subscribers � jour ? |
| `docs/MONITORING.md` | Inconnu | ?? V�rifier | Prometheus metrics actuelles ? |
| `docs/SECURITY.md` | Inconnu | ?? V�rifier | Rate limiting, 2FA, CORS docs � jour ? |
| `PLANNING_IMPLEMENTATION.md` | Inconnu | ?? Obsol�te | Liste seulement sprints 1-9, projet � Phase 10+ |
| `ROADMAP.md` | Inconnu | ?? Obsol�te | Priorit�s peut-�tre obsol�tes |

### Documentation manquante

| # | Document � cr�er | Priorit� | Description |
| --- | ----------------- | ---------- | ------------- |
| D1 | **Guide complet des CRON jobs** | ?? Haute | Lister les 68+ jobs, horaires, d�pendances, comment ajouter un nouveau job |
| D2 | **Guide des notifications** (refonte) | ?? Haute | 4 canaux, failover, throttle, templates WhatsApp, configuration |
| D3 | **Guide admin** (mise � jour) | ?? Moyenne | Les 20+ endpoints admin, panneau flottant, simulations, feature flags |
| D4 | **Guide des bridges inter-modules** | ?? Moyenne | Les 21 bridges, comment en cr�er un nouveau, naming convention |
| D5 | **Guide de test** (unifi�) | ?? Moyenne | Backend pytest + Frontend Vitest + E2E Playwright, fixtures, mocks communs |
| D6 | **Changelog module par module** | ?? Basse | Historique des changements par module pour le suivi |

---

## 14. Organisation et architecture

### Points forts ?

- **Architecture modulaire** : S�paration claire routes/schemas/services/models
- **Service Registry** : Pattern singleton thread-safe avec `@service_factory`
- **Event Bus** : Pub/sub d�coupl� avec wildcards et priorit�s
- **Cache multi-niveaux** : L1 (m�moire) ? L2 (session) ? L3 (fichier) + Redis optionnel
- **R�silience** : Retry + Timeout + Circuit Breaker composables
- **S�curit�** : JWT + 2FA TOTP + rate limiting + security headers + sanitization
- **Frontend** : App Router Next.js 16 bien structur�, composants shadcn/ui consistants

### Points � am�liorer ??

| # | Probl�me | Fichier(s) | Action |
| --- | ---------- | ----------- | -------- |
| O1 | **jobs.py monolithique (3500+ lignes)** | `src/services/core/cron/jobs.py` | D�couper en fichiers par domaine: `jobs_cuisine.py`, `jobs_famille.py`, `jobs_maison.py`, etc. |
| O2 | **Routes famille �clat�es** | `src/api/routes/famille*.py` (multiples) | Consolider ou documenter le naming pattern des sous-routes famille |
| O3 | **Scripts legacy non archiv�s** | `scripts/` (split_init_sql, split_jeux, rename_factory) | D�placer dans `scripts/_archive/` ou supprimer |
| O4 | **Doubles biblioth�ques de charts** | `chart.js` + `recharts` | Standardiser sur Recharts (d�j� plus utilis�) et retirer chart.js |
| O5 | **RGPD route non pertinente** | `src/api/routes/rgpd.py` | App familiale priv�e � simplifier en "Export backup" uniquement (pr�f�rence utilisateur) |
| O6 | **R�f�rences crois�es types** | `frontend/src/types/` | Certains types sont dupliqu�s entre fichiers � centraliser via barrel exports |
| O7 | **Donn�es r�f�rence non versionn�es** | `data/reference/*.json` | Ajouter un num�ro de version dans chaque fichier JSON |
| O8 | **Dossier exports non nettoy�** | `data/exports/` | Pas de politique de r�tention automatique |

---

## 15. Am�liorations UI/UX

### Dashboard principal

| # | Am�lioration | Priorit� | Description |
| --- | ------------- | ---------- | ------------- |
| U1 | **Widgets configurables drag-drop** | ?? Haute | Le composant `grille-widgets.tsx` existe mais pas de drag-drop pour r�organiser. Impl�menter avec `@dnd-kit/core` |
| U2 | **Cartes avec micro-animations** | ?? Moyenne | Ajouter des animations subtiles sur les cartes dashboard (compteurs qui s'incr�mentent, barres de progression anim�es) avec Framer Motion |
| U3 | **Mode sombre raffin�** | ?? Moyenne | Le dark mode fonctionne mais certains composants (charts, calendrier) n'ont pas de palette d�di�e |
| U4 | **Squelettes de chargement coh�rents** | ?? Moyenne | Les skeleton loaders existent mais ne refl�tent pas fid�lement la forme du contenu final |

### Navigation

| # | Am�lioration | Priorit� | Description |
| --- | ------------- | ---------- | ------------- |
| U5 | **Sidebar avec favoris dynamiques** | ?? Moyenne | Le composant `favoris-rapides.tsx` existe � interconnecter avec le store pour pins persistants |
| U6 | **Breadcrumbs interactifs** | ?? Basse | Les breadcrumbs sont l� mais pas cliquables sur tous les niveaux de navigation |
| U7 | **Transitions de page fluides** | ?? Moyenne | Pas de transitions entre pages � ajouter un fade-in/slide avec `framer-motion` ou les View Transitions API |
| U8 | **Bottom bar mobile enrichie** | ?? Moyenne | 5 items fixes � ajouter un indicateur visuel de la page active + animation |

### Formulaires

| # | Am�lioration | Priorit� | Description |
| --- | ------------- | ---------- | ------------- |
| U9 | **Auto-compl�tion intelligente** | ?? Haute | Les formulaires d'ajout (recettes, inventaire, courses) devraient proposer auto-compl�tion bas�e sur l'historique |
| U10 | **Validation inline en temps r�el** | ?? Moyenne | Les erreurs Zod s'affichent au submit � ajouter validation pendant la saisie (onBlur) |
| U11 | **Assistant formulaire IA** | ?? Moyenne | "Aide-moi � remplir" � L'IA pr�-remplit les champs bas� sur le contexte (ex: recette ? pr�-remplit les ingr�dients courants) |

### Mobile

| # | Am�lioration | Priorit� | Description |
| --- | ------------- | ---------- | ------------- |
| U12 | **Swipe actions** | ?? Moyenne | Le composant `swipeable-item.tsx` existe � l'appliquer � toutes les listes (courses, t�ches, recettes) pour supprimer/archiver |
| U13 | **Pull-to-refresh** | ?? Moyenne | Pattern mobile natif absent � TanStack Query le supporte |
| U14 | **Haptic feedback** | ?? Basse | Vibrations sur les actions importantes (checkout, suppression, validation) via Vibration API |

### Micro-interactions

| # | Am�lioration | Priorit� | Description |
| --- | ------------- | ---------- | ------------- |
| U15 | **Confetti sur accomplissement** | ?? Basse | Animation confetti quand un planning complet est valid�, quand toutes les courses sont coch�es, etc. |
| U16 | **Compteurs anim�s dashboard** | ?? Moyenne | Les chiffres du dashboard s'incr�mentent de 0 � la valeur r�elle � l'affichage |
| U17 | **Toast notifications am�lior�es** | ?? Moyenne | Utiliser Sonner avec des styles custom: succ�s vert + check anim�, erreur rouge + shake |

---

## 16. Visualisations 2D et 3D

### Existant

| Composant | Technologie | Module | Statut |
| ----------- | ------------- | -------- | -------- |
| Plan 3D maison | Three.js / @react-three/fiber | Maison | ?? Squelette (non connect� aux donn�es) |
| Heatmap num�ros loto | Recharts | Jeux | ? Fonctionnel |
| Heatmap cotes paris | Recharts | Jeux | ? Fonctionnel |
| Camembert budget | Recharts | Famille | ? Fonctionnel |
| Graphique ROI | Recharts | Jeux | ? Fonctionnel |
| Graphique jalons Jules | Recharts | Famille | ? Fonctionnel |
| Timeline planning | Custom CSS | Planning | ?? Basique |
| Carte Leaflet (habitat) | react-leaflet | Habitat | ?? Partiel |

### Am�liorations visualisation propos�es

#### 3D

| # | Visualisation | Module | Technologie | Description |
| --- | --------------- | -------- | ------------- | ------------- |
| V1 | **Plan 3D maison interactif** | Maison | Three.js + @react-three/drei | Connecter le plan 3D aux donn�es r�elles: couleur des pi�ces par nombre de t�ches en attente, indicateurs �nergie par pi�ce, clic ? d�tail des t�ches de la pi�ce |
| V2 | **Vue jardin 3D/2D** | Maison/Jardin | Three.js ou Canvas 2D | Plan du jardin avec les zones de plantation, �tat des plantes (couleur), calendrier d'arrosage visuel |
| V3 | **Globe 3D voyages** | Voyages | Three.js (globe.gl) | Vue globe avec les destinations pass�es et � venir, trac� des itin�raires |

#### 2D � Graphiques avanc�s

| # | Visualisation | Module | Technologie | Description |
| --- | --------------- | -------- | ------------- | ------------- |
| V4 | **Calendrier nutritionnel heatmap** | Cuisine | D3.js ou Recharts | Grille type GitHub contributions: chaque jour color� selon le score nutritionnel (rouge ? vert) |
| V5 | **Treemap budget** | Famille/Budget | Recharts Treemap | Visualisation proportionnelle des cat�gories de d�penses, cliquable pour drill-down |
| V6 | **Sunburst recettes** | Cuisine | D3.js Sunburst | Cat�gories ? sous-cat�gories ? recettes, proportionnel au nombre de fois cuisin�es |
| V7 | **Radar skill Jules** | Famille/Jules | Recharts RadarChart | Diagramme araign�e des comp�tences de Jules (motricit�, langage, social, cognitif) vs normes OMS |
| V8 | **Sparklines dans les cartes** | Dashboard | Inline SVG / Recharts | Mini graphiques dans les cartes dashboard (tendance 7 jours) pour chaque m�trique |
| V9 | **Graphe r�seau modules** | Admin | D3.js Force Graph ou vis.js | Visualisation interactive des 21 bridges inter-modules: noeuds = modules, liens = bridges, �paisseur = fr�quence d'utilisation |
| V10 | **Timeline Gantt entretien** | Maison | Recharts ou dhtmlxGantt | Planification visuelle des t�ches d'entretien sur l'ann�e |
| V11 | **Courbe �nergie N vs N-1** | Maison/�nergie | Recharts AreaChart | Comparaison consommation �nergie mois par mois vs ann�e pr�c�dente |
| V12 | **Flux Sankey courses ? cat�gories** | Courses/Budget | D3.js Sankey | Visualiser le flux de d�penses: fournisseurs ? cat�gories ? sous-cat�gories |
| V13 | **Wheel fortune loto** | Jeux | Canvas / CSS animation | Animation roue pour la r�v�lation des num�ros g�n�r�s par l'IA |

---

## 17. Simplification du flux utilisateur

### Principes de design

> L'utilisateur doit pouvoir accomplir ses t�ches quotidiennes en **3 clics maximum**.
> Les actions fr�quentes sont en **premier plan**, les actions rares en **menus secondaires**.
> L'IA fait le travail lourd en **arri�re-plan**, l'utilisateur **valide**.

### Flux principaux simplifi�s

#### ??? Flux cuisine (central)

```
Semaine vide
    �
    +--? IA propose un planning --? Valider / Modifier / R�g�n�rer
    �                                    �
    �                                    ?
    �                            Planning valid�
    �                                    �
    �                              +-----------+
    �                              �            �
    �                    Auto-g�n�re         Notif WhatsApp
    �                    courses               recap
    �                        �
    �                        ?
    �                  Liste courses
    �                  (tri�e par rayon)
    �                        �
    �                        ?
    �              En magasin: cocher au fur et � mesure
    �                        �
    �                        ?
    �              Checkout ? transfert automatique inventaire
    �                        �
    �                        ?
    �              Score anti-gaspi mis � jour
    �
    +--?  Fin de semaine: "Qu'avez-vous vraiment mang� ?" ? feedback IA
```

**Actions utilisateur**: 3 (valider planning ? cocher courses ? checkout)
**Actions IA**: Planning, liste courses, organisation rayons, transfert inventaire

#### ?? Flux famille quotidien

```
Matin (auto WhatsApp 07h30)
    �
    +-- "Bonjour ! Aujourd'hui: repas X, t�che Y, Jules a Z mois"
    �   +-- Bouton: "OK" ou "Modifier"
    �
    +-- Routines Jules (checklist)
    �   +-- Cocher les �tapes faites
    �
    +-- Soir: r�cap auto
        +-- "Aujourd'hui: 3/5 t�ches, 2 repas ok, Jules: poids not�"
```

**Actions utilisateur**: Cocher les routines, r�pondre OK/Modifier
**Actions IA**: Digest, rappels, scores

#### ?? Flux maison

```
Notification push (automatique)
    �
    +-- "T�che entretien � faire: [t�che] � Voir d�tail"
    �   +-- Clic ? fiche t�che avec guide
    �       +-- Marquer "fait" ? auto-prochaine date
    �
    +-- "Stock produit [X] bas"
    �   +-- Bouton: "Ajouter aux courses"
    �
    +-- Rapport mensuel (1er du mois)
        +-- Email avec r�sum� t�ches + budget maison
```

**Actions utilisateur**: Marquer fait, ajouter aux courses
**Actions IA**: Rappels, planification, rapport

### Actions rapides (FAB mobile)

Le composant `fab-actions-rapides.tsx` existe � le configurer avec:

| Action rapide | Cible | Ic�ne |
| -------------- | ------- | ------- |
| + Recette rapide | Formulaire simplifi� (nom + photo) | ?? |
| + Article courses | Ajout vocal ou texte | ?? |
| + D�pense | Montant + cat�gorie | ?? |
| + Note | Texte libre | ?? |
| Scan barcode | Scanner ? inventaire ou courses | ?? |
| Timer cuisine | Minuteur rapide | ?? |

---

## 18. Axes d'innovation

### Innovations propos�es (au-del� du scope actuel)

| # | Innovation | Modules | Description | Effort | Impact |
| --- | ----------- | --------- | ------------- | -------- | -------- |
| IN1 | **Mode "Pilote automatique"** | Tous | L'IA g�re le planning, les courses, les rappels sans intervention. L'utilisateur re�oit un r�sum� quotidien et intervient uniquement pour corriger. Bouton ON/OFF dans les param�tres | 5j | ?? Tr�s �lev� |
| IN2 | **Widget tablette Google (�cran d'accueil)** | Dashboard | Widget Android/web widget affichant: repas du jour, prochaine t�che, m�t�o, timer actif. Compatible avec la tablette Google | 4j | ?? �lev� |
| IN3 | **Vue "Ma journ�e" unifi�e** | Planning + Cuisine + Famille + Maison | Une seule page "Aujourd'hui" avec tout: repas, t�ches, routines Jules, m�t�o, anniversaires, timer. Le concentr� de la journ�e | 3j | ?? Tr�s �lev� |
| IN4 | **Suggestions proactives contextuelles** | IA + Tous | Banni�re en haut de chaque module avec une suggestion IA contextuelle: "Il reste des tomates qui expirent demain ? [Voir recettes]", "Budget restaurants atteint 80% ? [Voir d�tail]" | 3j | ?? �lev� |
| IN5 | **Journal familial automatique** | Famille | L'app g�n�re automatiquement un journal de la semaine: repas cuisin�s, activit�s faites, jalons Jules, photos upload�es, m�t�o, d�penses. Exportable en PDF joli | 3j | ?? Moyen |
| IN6 | **Mode focus/zen** | UI | Le composant `focus/` existe en squelette. Impl�menter un mode "concentration" qui masque tout sauf la t�che en cours (recette en cuisine, liste de courses en magasin) | 2j | ?? Moyen |
| IN7 | **Comparateur de prix courses** | Courses + IA | � partir de la liste de courses, l'IA compare avec les prix r�f�rence (sans OCR tickets) et donne un budget estim� | 3j | ?? Moyen |
| IN8 | **Int�gration Google Home routines** | Assistant | Routines Google Home: "Bonsoir" ? lecture du repas du lendemain + t�ches demain. �tendre les intents Google Assistant existants | 4j | ?? Moyen |
| IN9 | **Seasonal meal prep planner** | Cuisine + IA | Chaque saison, l'IA propose un plan de batch cooking saisonnier avec les produits de saison et les cong�lations recommand�es | 2j | ?? Moyen |
| IN10 | **Score famille hebdomadaire** | Dashboard | Score composite: nutrition + d�penses ma�tris�es + activit�s + entretien � jour + bien-�tre. Graphe d'�volution semaine par semaine | 2j | ?? �lev� |
| IN11 | **Export rapport mensuel PDF** | Export + IA | Un beau rapport PDF mensuel avec graphiques: budget, nutrition, entretien, Jules, jeux. R�sum� narratif IA | 3j | ?? Moyen |
| IN12 | **Planning vocal** | Assistant + Planning | "Ok Google, planifie du poulet pour mardi soir" ? cr�� le repas + v�rifie le stock + ajoute les manquants aux courses | 3j | ?? Moyen |
| IN13 | **Tableau de bord �nergie** | Maison | Dashboard d�di� �nergie: consommation temps r�el (si compteur Linky connect�), historique, comparaison N-1, pr�vision facture, tips IA | 4j | ?? Moyen |
| IN14 | **Mode "invit�" pour le conjoint** | Auth | Vue simplifi�e pour un 2�me utilisateur: juste les courses, le planning, les routines. Sans admin ni config | 2j | ?? �lev� |

---

## 19. Plan d'action prioris�

### ?? Phase A � Stabilisation (Semaine 1-2)

> **Objectif**: Corriger les bugs, consolider SQL, couvrir les tests critiques

| # | T�che | Effort | Cat�gorie |
| --- | ------- | -------- | ----------- |
| A1 | Fixer B1 (API_SECRET_KEY multi-process) | 1h | Bug critique |
| A2 | Fixer B2 (WebSocket fallback HTTP polling) | 1j | Bug critique |
| A3 | Fixer B3 (Intercepteur auth promise non g�r�e) | 2h | Bug critique |
| A4 | Fixer B5 (Rate limiting m�moire non born� � ajouter LRU) | 2h | Bug important |
| A5 | Fixer B9 (WhatsApp state persistence � Redis/DB) | 1j | Bug important |
| A6 | Ex�cuter audit_orm_sql.py et corriger divergences (S2) | 1j | SQL |
| A7 | Consolider migrations dans les fichiers schema (S3) | 1j | SQL |
| A8 | R�g�n�rer INIT_COMPLET.sql propre (S1) | 30min | SQL |
| A9 | Ajouter tests export PDF (T1) | 1j | Tests |
| A10 | Ajouter tests webhooks WhatsApp (T2) | 1j | Tests |
| A11 | Ajouter tests event bus sc�narios (T3) | 1j | Tests |
| A12 | Mettre � jour CRON_JOBS.md (D1) | 2h | Doc |
| A13 | Mettre � jour NOTIFICATIONS.md (D2) | 2h | Doc |

### ?? Phase B � Fonctionnalit�s & IA (Semaine 3-4)

> **Objectif**: Combler les gaps fonctionnels, enrichir l'IA

| # | T�che | Effort | Cat�gorie |
| --- | ------- | -------- | ----------- |
| B1 | Impl�menter G5 (Mode offline courses) | 3j | Gap |
| B2 | Impl�menter IA1 (Pr�diction courses intelligente) | 3j | IA |
| B3 | Impl�menter J2 (Planning auto semaine CRON) | 2j | CRON |
| B4 | Impl�menter J9 (Alertes budget seuil CRON) | 1j | CRON |
| B5 | Impl�menter W2 (Commandes WhatsApp enrichies) | 3j | WhatsApp |
| B6 | Impl�menter I1 (R�colte jardin ? Recettes) | 2j | Inter-module |
| B7 | Impl�menter I3 (Budget anomalie ? notification) | 2j | Inter-module |
| B8 | Impl�menter I5 (Documents expir�s ? Dashboard) | 1j | Inter-module |
| B9 | Impl�menter IA5 (R�sum� hebdo intelligent) | 2j | IA |
| B10 | Impl�menter IA8 (Suggestion batch cooking intelligent) | 3j | IA |
| B11 | Ajouter tests pages famille frontend (T8 �tendu) | 2j | Tests |
| B12 | Ajouter tests E2E parcours utilisateur (T6) | 3j | Tests |

### ?? Phase C � UI/UX & Visualisations (Semaine 5-6)

> **Objectif**: Rendre l'interface belle, moderne, fluide

| # | T�che | Effort | Cat�gorie |
| --- | ------- | -------- | ----------- |
| C1 | Impl�menter U1 (Dashboard widgets drag-drop) | 2j | UI |
| C2 | Impl�menter IN3 (Page "Ma journ�e" unifi�e) | 3j | Innovation |
| C3 | Impl�menter V1 (Plan 3D maison interactif connect�) | 5j | 3D |
| C4 | Impl�menter V4 (Calendrier nutritionnel heatmap) | 2j | 2D |
| C5 | Impl�menter V5 (Treemap budget) | 2j | 2D |
| C6 | Impl�menter V7 (Radar skill Jules) | 1j | 2D |
| C7 | Impl�menter V8 (Sparklines dans cartes dashboard) | 1j | 2D |
| C8 | Impl�menter U7 (Transitions de page fluides) | 2j | UI |
| C9 | Impl�menter U12 (Swipe actions listes) | 1j | Mobile |
| C10 | Impl�menter U16 (Compteurs anim�s dashboard) | 1j | UI |
| C11 | Impl�menter U9 (Auto-compl�tion intelligent formulaires) | 2j | UX |
| C12 | Impl�menter IN4 (Suggestions proactives contextuelles) | 3j | Innovation |

### ?? Phase D � Admin & Automatisations (Semaine 7-8)

> **Objectif**: Enrichir le mode admin, nouvelles automatisations

| # | T�che | Effort | Cat�gorie |
| --- | ------- | -------- | ----------- |
| D1 | Impl�menter A1 (Console commande rapide admin) | 2j | Admin |
| D2 | Impl�menter A3 (Scheduler visuel CRON) | 3j | Admin |
| D3 | Impl�menter A6 (Logs temps r�el via WebSocket) | 2j | Admin |
| D4 | Impl�menter J1 (CRON pr�diction courses hebdo) | 1j | CRON |
| D5 | Impl�menter J4 (Rappels jardin saisonniers) | 1j | CRON |
| D6 | Impl�menter J6 (V�rif sant� syst�me horaire) | 1j | CRON |
| D7 | Impl�menter J7 (Backup auto hebdomadaire JSON) | 1j | CRON |
| D8 | Impl�menter W1 (WhatsApp state persistence) | 2j | Notifications |
| D9 | Impl�menter E1 (Templates email HTML/MJML) | 2j | Notifications |
| D10 | D�couper jobs.py en modules (O1) | 1j | Refactoring |
| D11 | Archiver scripts legacy (O3) | 30min | Nettoyage |
| D12 | Standardiser sur Recharts uniquement (O4) | 1j | Nettoyage |

### ?? Phase E � Innovations (Semaine 9+)

> **Objectif**: Features diff�renciantes

| # | T�che | Effort | Cat�gorie |
| --- | ------- | -------- | ----------- |
| E1 | Impl�menter IN1 (Mode Pilote automatique) | 5j | Innovation |
| E2 | Impl�menter IN2 (Widget tablette Google) | 4j | Innovation |
| E3 | Impl�menter IN10 (Score famille hebdomadaire) | 2j | Innovation |
| E4 | Impl�menter IN14 (Mode invit� conjoint) | 2j | Innovation |
| E5 | Impl�menter V9 (Graphe r�seau modules admin) | 2j | Visualisation |
| E6 | Impl�menter V10 (Timeline Gantt entretien) | 2j | Visualisation |
| E7 | Impl�menter V2 (Vue jardin 2D/3D) | 3j | Visualisation |
| E8 | Impl�menter IN5 (Journal familial automatique) | 3j | Innovation |
| E9 | Impl�menter IN11 (Rapport mensuel PDF export) | 3j | Innovation |
| E10 | Impl�menter IN8 (Google Home routines �tendues) | 4j | Innovation |
| E11 | Impl�menter G17 (Sync Google Calendar bidirectionnelle) | 4j | Gap |
| E12 | Impl�menter IA4 (Assistant vocal �tendu) | 4j | IA |

---

## Annexe A � R�sum� des fichiers cl�s

### Backend Python

```
src/
+-- api/
�   +-- main.py                    # FastAPI app + 7 middlewares + health
�   +-- auth.py                    # JWT + 2FA TOTP
�   +-- dependencies.py            # require_auth, require_role
�   +-- routes/                    # 41 fichiers routeurs (~250 endpoints)
�   +-- schemas/                   # 25 fichiers Pydantic (~150 mod�les)
�   +-- utils/                     # Exception handler, pagination, metrics, ETag, security
�   +-- rate_limiting/             # Multi-strategy (memory/Redis/file)
�   +-- websocket_courses.py       # WS collaboration courses
�   +-- websocket/                 # 4 autres WebSockets
+-- core/
�   +-- ai/                        # Mistral client, cache s�mantique, circuit breaker
�   +-- caching/                   # L1/L2/L3 + Redis
�   +-- config/                    # Pydantic BaseSettings
�   +-- db/                        # Engine, sessions, migrations
�   +-- decorators/                # @avec_session_db, @avec_cache, @avec_resilience
�   +-- models/                    # 32 fichiers ORM (100+ classes)
�   +-- resilience/                # Retry + Timeout + CircuitBreaker
�   +-- validation/                # Pydantic schemas + sanitizer
+-- services/
    +-- core/
    �   +-- base/                  # BaseAIService (4 mixins)
    �   +-- cron/                  # 68+ jobs (3500+ lignes)
    �   +-- events/                # Pub/Sub event bus
    �   +-- registry.py            # @service_factory singleton
    +-- cuisine/                   # RecetteService, ImportService
    +-- famille/                   # JulesAI, WeekendAI
    +-- maison/                    # MaisonService
    +-- jeux/                      # JeuxService
    +-- planning/                  # 5 sous-modules
    +-- inventaire/                # InventaireService
    +-- dashboard/                 # Agr�gation multi-module
    +-- integrations/              # Multimodal, webhooks
    +-- utilitaires/               # Automations, divers
```

### Frontend Next.js

```
frontend/src/
+-- app/
�   +-- (auth)/                    # Login / Inscription
�   +-- (app)/                     # App prot�g�e (~60 pages)
�   �   +-- page.tsx               # Dashboard
�   �   +-- cuisine/               # 12 pages
�   �   +-- famille/               # 10 pages
�   �   +-- maison/                # 8 pages
�   �   +-- jeux/                  # 7 pages
�   �   +-- planning/              # 2 pages
�   �   +-- outils/                # 6 pages
�   �   +-- parametres/            # 3 pages + 7 onglets
�   �   +-- admin/                 # 10 pages
�   �   +-- habitat/               # 3 pages
�   �   +-- ia-avancee/            # IA avanc�e
�   +-- share/                     # Partage public
+-- composants/
�   +-- ui/                        # 29 shadcn/ui
�   +-- disposition/               # 19 layout components
�   +-- cuisine/                   # Composants cuisine
�   +-- famille/                   # Composants famille
�   +-- jeux/                      # Composants jeux (heatmaps, grilles)
�   +-- maison/                    # Composants maison (plan 3D, drawers)
�   +-- habitat/                   # Composants habitat
�   +-- graphiques/                # Charts r�utilisables
�   +-- planning/                  # Timeline, calendrier
+-- bibliotheque/
�   +-- api/                       # 34 clients API
�   +-- validateurs.ts             # 22 sch�mas Zod
+-- crochets/                      # 15 hooks custom
+-- magasins/                      # 4 stores Zustand
+-- types/                         # 15 fichiers TypeScript
+-- fournisseurs/                  # 3 providers React
```

### SQL

```
sql/
+-- INIT_COMPLET.sql               # 4922 lignes, source unique (prod)
+-- schema/ (18 fichiers)          # Source de v�rit� par domaine
+-- migrations/ (7 fichiers)       # � consolider dans schema/
```

---

## Annexe B � M�triques de sant� projet

| Indicateur | Valeur | Cible | Statut |
| ----------- | -------- | ------- | -------- |
| Tests backend | ~55% couverture | =70% | ?? |
| Tests frontend | ~40% couverture | =50% | ?? |
| Tests E2E | ~10% | =30% | ?? |
| Docs � jour | ~60% (35/58 fichiers) | =90% | ?? |
| SQL ORM sync | Non v�rifi� | 100% | ?? |
| Endpoints document�s | ~80% | 100% | ?? |
| Bridges inter-modules | 21 actifs | 31 possibles | ?? |
| CRON jobs test�s | ~30% | =70% | ?? |
| Bugs critiques ouverts | 4 | 0 | ?? |
| S�curit� (OWASP) | Bon (JWT, sanitize, rate limit) | Complet | ?? |

---

> **Derni�re mise � jour**: 1er Avril 2026
> **Prochaine revue pr�vue**: Apr�s Phase A (stabilisation)
