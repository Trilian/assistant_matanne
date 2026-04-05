[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-api](../README.md) / utiliserMutationAvecInvalidation

# Function: utiliserMutationAvecInvalidation()

> **utiliserMutationAvecInvalidation**\<`TData`, `TVariables`\>(`fn`, `clesAInvalider`, `options?`): `UseMutationResult`\<`TData`, `Error`, `TVariables`, `unknown`\>

Defined in: [crochets/utiliser-api.ts:69](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-api.ts#L69)

Mutation avec invalidation automatique après succès.
Usage: `utiliserMutationAvecInvalidation(creerRecette, ["recettes"])`

## Type Parameters

### TData

`TData`

### TVariables

`TVariables`

## Parameters

### fn

(`variables`) => `Promise`\<`TData`\>

### clesAInvalider

`string`[][]

### options?

`Partial`\<`UseMutationOptions`\<`TData`, `Error`, `TVariables`, `unknown`\>\>

## Returns

`UseMutationResult`\<`TData`, `Error`, `TVariables`, `unknown`\>
