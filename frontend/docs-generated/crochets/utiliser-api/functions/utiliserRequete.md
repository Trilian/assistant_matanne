[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-api](../README.md) / utiliserRequete

# Function: utiliserRequete()

> **utiliserRequete**\<`T`\>(`cle`, `fn`, `options?`): \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \}

Defined in: [crochets/utiliser-api.ts:21](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-api.ts#L21)

Query wrapper avec cache par défaut de 5 minutes.
Usage: `utiliserRequete(["recettes"], listerRecettes)`

## Type Parameters

### T

`T`

## Parameters

### cle

`string`[]

### fn

() => `Promise`\<`T`\>

### options?

`Partial`\<`UseQueryOptions`\<`T`, `Error`, `T`, readonly `unknown`[]\>\>

## Returns

\{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \} \| \{ `chargement`: `boolean`; `donnees`: `NoInfer_2`\<`T`\> \| `undefined`; `erreur`: `Error` \| `null`; \}
