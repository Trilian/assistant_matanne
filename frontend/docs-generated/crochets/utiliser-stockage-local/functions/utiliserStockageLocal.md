[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-stockage-local](../README.md) / utiliserStockageLocal

# Function: utiliserStockageLocal()

> **utiliserStockageLocal**\<`T`\>(`cle`, `valeurDefaut`): readonly \[`T`, `Dispatch`\<`SetStateAction`\<`T`\>\>, () => `void`\]

Defined in: [crochets/utiliser-stockage-local.ts:13](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-stockage-local.ts#L13)

useState synchronisé avec localStorage.
Usage: `const [theme, setTheme] = utiliserStockageLocal("theme", "light")`

## Type Parameters

### T

`T`

## Parameters

### cle

`string`

### valeurDefaut

`T`

## Returns

readonly \[`T`, `Dispatch`\<`SetStateAction`\<`T`\>\>, () => `void`\]
