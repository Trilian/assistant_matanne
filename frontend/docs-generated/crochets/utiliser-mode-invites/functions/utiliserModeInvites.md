[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-mode-invites](../README.md) / utiliserModeInvites

# Function: utiliserModeInvites()

> **utiliserModeInvites**(): `object`

Defined in: [crochets/utiliser-mode-invites.ts:46](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-mode-invites.ts#L46)

Hook de gestion du mode invités pour les courses — persiste dans localStorage.

## Returns

`object`

### contexte

> **contexte**: [`ContexteModeInvites`](../interfaces/ContexteModeInvites.md)

### mettreAJour

> **mettreAJour**: (`miseAJour`) => `void`

#### Parameters

##### miseAJour

`Partial`\<[`ContexteModeInvites`](../interfaces/ContexteModeInvites.md)\> \| ((`precedent`) => `Partial`\<[`ContexteModeInvites`](../interfaces/ContexteModeInvites.md)\>)

#### Returns

`void`

### reinitialiser

> **reinitialiser**: () => `void`

#### Returns

`void`
