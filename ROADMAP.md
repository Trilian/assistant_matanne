# ROADMAP - Assistant Matanne

> Derniere mise a jour : 1 avril 2026.

- Audit complet : [`ANALYSE_COMPLETE.md`](ANALYSE_COMPLETE.md) - etat reel, bugs, dette technique, plan long terme
- Plan d'implementation : [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md) - sprints 1 a 10, taches detaillees

---

## Sprints 1 a 7 termines

**Sprint 1 - Bugs critiques push** : P-01/P-02/P-03/B-05
**Sprint 4 - Features Jules + Cuisine** : CT-05/CT-06/CT-09/QW-02
**Sprint 5 - Notifications + Admin + 2FA** : CT-01/CT-02/WhatsApp webhook/RouteurIA/Redis L2
**Sprint 6 - Cron jobs** : CT-03/CT-04 (10 jobs APScheduler actifs)
**Sprint 7 - SQL consolidation + Bugs + Tests + Doc**

- P-04/P-05/P-06 : migrations SQL absorbees dans INIT_COMPLET (Sprint 1)
- P-07 : alembic archive (`alembic.ini.bak`)
- B-06/B-07/B-11/B-12 : bugs corriges
- CT-08 : index SQL manquants ajoutes
- CT-10 : audit orphelines ORM -> SQL + test de non regression
- CT-12/CT-13/CT-14/CT-07 : tests push, admin, famille crees
- CT-02-FE : page Admin Jobs (`/admin/jobs`) creee
- CT-11/CT-15/CT-16/CT-17 : documentation nettoyee

---

## Sprint 8 - Inter-modules + Dashboard avance

| # | Tache | Item | Effort |
| --- | --- | --- | --- |
| 1 | Cellier -> inventaire cuisine consolide | MT-01 | M |
| 2 | Score bien-etre global (IA-09) | MT-03 | M |
| 3 | Alertes meteo contextuelles cross-modules | MT-04 | M |
| 4 | Widgets dashboard configurables (drag and drop) | MT-06 | L |
| 5 | Timeline vie familiale | MT-08 | M |
| 6 | OCR photo-frigo -> auto-sync inventaire | MT-09 | S |
| 7 | Widget meteo sur dashboard | QW-01 | XS |
| 8 | "Aujourd'hui dans l'histoire de la famille" | QW-06 | S |

Detail dans [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md#sprint-8)

---

## Sprint 9 - WhatsApp sortant + IA avancee

- MT-02 : WhatsApp sortant proactif (messages preemptifs Meta Cloud API)
- MT-07 : assistant vocal (Web Speech API + commandes Mistral)
- J-03 a J-11 : cron jobs restants (peremptions, planning dimanche, budget mensuel)
- IA-04/IA-05/IA-07/IA-08 : planificateur vacances, anomalies financieres, optimisation budget, diagnostic photo maison

Note : plusieurs items de Sprint 9 sont desormais partiellement ou totalement implementes cote backend, notamment la refonte notifications, l'extension CRON (68 jobs) et le moteur d'automations enrichi. Le detail operationnel a jour se trouve dans `PLANNING_IMPLEMENTATION.md` et les guides de documentation specialises.

---

## Sprint 10 - Innovations et long terme

- LT-01 : integration Garmin sante/sport (sync matinale + recommandations diner)
- LT-02 : gamification sport + alimentation (points/badges persistants + page dediee)
- LT-03 : mode voyage avec checklists intelligentes (scaling participants + generation courses)
- LT-04 : automations "Si Alors" (table DB + moteur + cron + execution manuelle)

Etat reel du moteur LT-04 au 1er avril 2026 :

- 9 declencheurs supportes
- 10 actions supportees
- dry-run global et par regle
- generation IA de regle structuree

Detail dans [`PLANNING_IMPLEMENTATION.md`](PLANNING_IMPLEMENTATION.md#sprint-10)

---

## Principes

- **Pas de feature creep** : chaque ajout doit resoudre un besoin reel de la famille
- **Stabilite d'abord** : corriger les bugs et tests avant d'ajouter des fonctionnalites
- **Documentation a jour** : toute nouvelle feature = mise a jour du guide et de l'API reference
- **Securite** : RLS Supabase, JWT, rate limiting, sanitization non negociables
