# AI Services

> RÃ©fÃ©rence des services IA, de leurs usages actuels et des garde-fous communs.

---

## Fondations communes

La brique IA du projet repose sur:

- client IA: `src/core/ai/`
- base commune: `src/services/core/base/`
- limitation de dÃ©bit et cache sÃ©mantique intÃ©grÃ©s
- parsing structurÃ© des rÃ©ponses via Pydantic

CapacitÃ©s transverses fournies par `BaseAIService`:

- appels synchrones et structurÃ©s
- cache sÃ©mantique
- parsing JSON / liste / modÃ¨le Pydantic
- gestion d'erreur et fallback
- pilotage uniforme des prompts systÃ¨me

---

## Services IA identifiÃ©s

| Domaine | Service | RÃ´le principal |
| --------- | --------- | ---------------- |
| Cuisine | `ServiceSuggestions` | suggestions recettes et planning |
| Cuisine | `ServicePredictionCourses` | prÃ©diction d'achats |
| Cuisine | `ServicePredictionPeremption` | prÃ©diction / priorisation pÃ©remption |
| Famille | `JulesAIService` | dÃ©veloppement enfant |
| Famille | `WeekendAIService` | idÃ©es weekend |
| Famille | `SoireeAIService` | suggestions de soirÃ©e |
| Famille | `AchatsIAService` | suggestions d'achats famille |
| Dashboard | `ResumeFamilleIAService` | rÃ©sumÃ© hebdomadaire |
| Dashboard | `ServiceAnomaliesFinancieres` | anomalies budgÃ©taires |
| Jeux | `JeuxAIService` | analyses paris et opportunitÃ©s |
| Maison | services projets / jardin / conseiller | conseils et enrichissement ciblÃ© |
| Outils | `ChatAIService` | chat conversationnel multi-contexte |
| IntÃ©grations | `MultiModalAIService` | OCR, analyse image, multimodal |

---

## Chat IA multi-contexte

Le chat IA de `src/services/utilitaires/chat_ai.py` gÃ¨re actuellement les contextes:

- `cuisine`
- `famille`
- `maison`
- `budget`
- `general`
- `nutrition`

Objectif actuel du service:

- rÃ©ponses contextualisÃ©es par domaine
- mÃ©moire courte de conversation
- actions rapides et ton adaptÃ© au contexte

---

## Bonnes pratiques projet

- toujours utiliser les abstractions du package `src/core/ai`
- prÃ©fÃ©rer les sorties structurÃ©es Pydantic quand la rÃ©ponse nourrit une logique mÃ©tier
- limiter les appels coÃ»teux via cache et rate limiting
- Ã©viter les prompts non bornÃ©s cÃ´tÃ© route API
- journaliser les dÃ©gradations sans faire Ã©chouer tout le flux utilisateur si l'IA est un enrichissement non bloquant

---

## Limites et points Ã  surveiller

- certaines fonctionnalitÃ©s restent encore rule-based et non enrichies par IA
- le chat multi-module peut encore Ãªtre enrichi avec plus de contexte inter-modules
- certains services mÃ©tier utilisent l'IA comme enrichissement, pas comme source de vÃ©ritÃ©

---

## RÃ©fÃ©rences associÃ©es

- `docs/ARCHITECTURE.md`
- `docs/INTER_MODULES.md`
- `docs/TROUBLESHOOTING.md`
