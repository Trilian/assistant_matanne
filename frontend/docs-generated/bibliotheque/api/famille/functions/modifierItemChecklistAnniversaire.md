[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/famille](../README.md) / modifierItemChecklistAnniversaire

# Function: modifierItemChecklistAnniversaire()

> **modifierItemChecklistAnniversaire**(`anniversaireId`, `checklistId`, `itemId`, `patch`): `Promise`\<[`ItemChecklistAnniversaire`](../interfaces/ItemChecklistAnniversaire.md)\>

Defined in: [bibliotheque/api/famille.ts:453](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/famille.ts#L453)

Met à jour un item checklist anniversaire

## Parameters

### anniversaireId

`number`

### checklistId

`number`

### itemId

`number`

### patch

`Partial`\<`Pick`\<[`ItemChecklistAnniversaire`](../interfaces/ItemChecklistAnniversaire.md), `"fait"` \| `"budget_reel"` \| `"budget_estime"` \| `"priorite"` \| `"responsable"` \| `"quand"` \| `"notes"` \| `"libelle"` \| `"categorie"`\>\>

## Returns

`Promise`\<[`ItemChecklistAnniversaire`](../interfaces/ItemChecklistAnniversaire.md)\>
