[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/famille](../README.md) / obtenirSuggestionsAchatsAuto

# Function: obtenirSuggestionsAchatsAuto()

> **obtenirSuggestionsAchatsAuto**(`params?`): `Promise`\<\{ `groupes`: \{ `anniversaire`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `jalon`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `saison`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; \}; `suggestions`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md) & `object`[]; `total`: `number`; \}\>

Defined in: [bibliotheque/api/famille.ts:834](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/famille.ts#L834)

Suggestions IA proactives (anniversaires, jalons, saison)

## Parameters

### params?

#### budget_max?

`number`

#### relation_defaut?

`string`

## Returns

`Promise`\<\{ `groupes`: \{ `anniversaire`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `jalon`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; `saison`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md)[]; \}; `suggestions`: [`SuggestionAchat`](../interfaces/SuggestionAchat.md) & `object`[]; `total`: `number`; \}\>
