[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/telegram](../README.md) / envoyerPlanningTelegram

# Function: envoyerPlanningTelegram()

> **envoyerPlanningTelegram**(`planningId`, `planningTexte?`): `Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>

Defined in: [bibliotheque/api/telegram.ts:16](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/telegram.ts#L16)

Envoyer le planning de la semaine via Telegram avec boutons interactifs
Appelé après genererPlanningSemaine() pour notifier les utilisateurs via Telegram

Le callback_data sera formaté comme:
- planning_valider:ID (valide le planning)
- planning_modifier:ID (lien web pour modifier)
- planning_regenerer:ID (régénère un nouveau planning)

## Parameters

### planningId

`number`

### planningTexte?

`string`

## Returns

`Promise`\<\{ `id?`: `number` \| `null`; `message`: `string`; \}\>
