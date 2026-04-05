[**Assistant Matanne — Frontend**](../../../../README.md)

***

[Assistant Matanne — Frontend](../../../../README.md) / [bibliotheque/api/inventaire](../README.md) / enrichirParCodeBarres

# Function: enrichirParCodeBarres()

> **enrichirParCodeBarres**(`code`): `Promise`\<\{ `code_barres`: `string`; `donnees?`: \{ `calories?`: `number`; `ecoscore?`: `string`; `nom_produit?`: `string`; `nova_group?`: `number`; `nutriscore?`: `string`; \}; `enrichi`: `boolean`; \}\>

Defined in: [bibliotheque/api/inventaire.ts:161](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/api/inventaire.ts#L161)

Enrichir un article via OpenFoodFacts (nutriscore, ecoscore, etc.)

## Parameters

### code

`string`

## Returns

`Promise`\<\{ `code_barres`: `string`; `donnees?`: \{ `calories?`: `number`; `ecoscore?`: `string`; `nom_produit?`: `string`; `nova_group?`: `number`; `nutriscore?`: `string`; \}; `enrichi`: `boolean`; \}\>
