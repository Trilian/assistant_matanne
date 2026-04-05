[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/famille](../README.md) / obtenirResumeBudgetMois

# Function: obtenirResumeBudgetMois()

> **obtenirResumeBudgetMois**(): `Promise`\<\{ `achats_par_categorie`: `Record`\<`string`, `number`\>; `mois_courant`: `string`; `total_courant`: `number`; `total_precedent`: `number` \| `null`; `variation_pct`: `number` \| `null`; \}\>

Defined in: [bibliotheque/api/famille.ts:730](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/famille.ts#L730)

Résumé budget du mois courant vs précédent

## Returns

`Promise`\<\{ `achats_par_categorie`: `Record`\<`string`, `number`\>; `mois_courant`: `string`; `total_courant`: `number`; `total_precedent`: `number` \| `null`; `variation_pct`: `number` \| `null`; \}\>
