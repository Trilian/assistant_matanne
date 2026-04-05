[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-auto-completion-maison](../README.md) / utiliserAutoCompletionMaison

# Function: utiliserAutoCompletionMaison()

> **utiliserAutoCompletionMaison**(`contexte`): `object`

Defined in: [crochets/utiliser-auto-completion-maison.ts:13](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-auto-completion-maison.ts#L13)

Hook de complétion automatique des champs de formulaires maison.
Appelle l'IA pour suggérer une valeur si le champ cible est vide.

## Parameters

### contexte

`string`

## Returns

`object`

### autoCompleter

> **autoCompleter**: (`champ`, `valeur`, `setter`) => `Promise`\<`void`\>

#### Parameters

##### champ

`string`

##### valeur

`string`

##### setter

(`val`) => `void`

#### Returns

`Promise`\<`void`\>

### isLoading

> **isLoading**: `boolean` = `enChargement`
