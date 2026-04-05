[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-api](../README.md) / utiliserMutation

# Function: utiliserMutation()

> **utiliserMutation**\<`TData`, `TVariables`, `TContext`\>(`fn`, `options?`): `UseMutationResult`\<`TData`, `Error`, `TVariables`, `TContext`\>

Defined in: [crochets/utiliser-api.ts:45](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-api.ts#L45)

Mutation wrapper avec invalidation automatique.
Usage: `utiliserMutation(mutationFn, { onSuccess: () => ... })`

## Type Parameters

### TData

`TData`

### TVariables

`TVariables` = `void`

### TContext

`TContext` = `unknown`

## Parameters

### fn

(`variables`) => `Promise`\<`TData`\>

### options?

`Partial`\<`UseMutationOptions`\<`TData`, `Error`, `TVariables`, `TContext`\>\>

## Returns

`UseMutationResult`\<`TData`, `Error`, `TVariables`, `TContext`\>
