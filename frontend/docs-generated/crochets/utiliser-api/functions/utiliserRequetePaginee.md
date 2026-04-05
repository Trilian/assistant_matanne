[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-api](../README.md) / utiliserRequetePaginee

# Function: utiliserRequetePaginee()

> **utiliserRequetePaginee**\<`T`\>(`cleBase`, `fn`, `page`, `options?`): `UseQueryResult`\<`NoInfer_2`\<`T`\>, `Error`\>

Defined in: [crochets/utiliser-api.ts:92](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-api.ts#L92)

Query paginée avec paramètres de page.
Usage: `utiliserRequetePaginee(["recettes"], (p) => listerRecettes(p), page)`

## Type Parameters

### T

`T`

## Parameters

### cleBase

`string`[]

### fn

(`page`) => `Promise`\<`T`\>

### page

`number`

### options?

`Partial`\<`UseQueryOptions`\<`T`, `Error`, `T`, readonly `unknown`[]\>\>

## Returns

`UseQueryResult`\<`NoInfer_2`\<`T`\>, `Error`\>
