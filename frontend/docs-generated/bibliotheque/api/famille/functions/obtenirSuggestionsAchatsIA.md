[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/famille](../README.md) / obtenirSuggestionsAchatsIA

# Function: obtenirSuggestionsAchatsIA()

> **obtenirSuggestionsAchatsIA**(`params`): `Promise`\<\{ `suggestions`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `total`: `number`; `type`: `string`; \}\>

Defined in: [bibliotheque/api/famille.ts:818](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/famille.ts#L818)

## Parameters

### params

#### age?

`number`

#### budget_max?

`number`

#### historique_cadeaux?

`string`[]

#### nom?

`string`

#### prochains_jalons?

`string`[]

#### relation?

`string`

#### saison?

`string`

#### tailles?

`Record`\<`string`, `string`\>

#### type

`"anniversaire"` \| `"jalon"` \| `"saison"`

## Returns

`Promise`\<\{ `suggestions`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `total`: `number`; `type`: `string`; \}\>
