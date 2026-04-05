[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-crud](../README.md) / utiliserDialogCrud

# Function: utiliserDialogCrud()

> **utiliserDialogCrud**\<`T`\>(`options?`): `object`

Defined in: [crochets/utiliser-crud.ts:29](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-crud.ts#L29)

Hook générique pour gérer l'état dialog + mode édition d'un CRUD.

Remplace le boilerplate répété dans chaque page :
- `const [dialogOuvert, setDialogOuvert] = useState(false)`
- `const [enEdition, setEnEdition] = useState<T | null>(null)`
- Fonctions `ouvrirCreation`, `ouvrirEdition`, `fermerDialog`

## Type Parameters

### T

`T`

## Parameters

### options?

#### onFermer?

() => `void`

Appelé à la fermeture — nettoyage supplémentaire si besoin

#### onOuvrirCreation?

() => `void`

Appelé lors de l'ouverture en mode création — typiquement pour réinitialiser le form

#### onOuvrirEdition?

(`item`) => `void`

Appelé lors de l'ouverture en mode édition — typiquement pour pré-remplir le form

## Returns

### dialogOuvert

> **dialogOuvert**: `boolean`

### elementEnCours

> **elementEnCours**: `T` \| `null` = `enEdition`

### elementEnEdition

> **elementEnEdition**: `T` \| `null` = `enEdition`

### enEdition

> **enEdition**: `T` \| `null`

### estEnEdition

> **estEnEdition**: `boolean`

Vrai si on est en mode édition (enEdition !== null)

### fermer

> **fermer**: () => `void` = `fermerDialog`

#### Returns

`void`

### fermerDialog

> **fermerDialog**: () => `void`

#### Returns

`void`

### mode

> **mode**: `string`

### ouvert

> **ouvert**: `boolean` = `dialogOuvert`

### ouvrir

> **ouvrir**: (`modeOuItem?`, `itemEdition?`) => `void`

#### Parameters

##### modeOuItem?

`T` \| `"edition"` \| `"creation"`

##### itemEdition?

`T`

#### Returns

`void`

### ouvrirCreation

> **ouvrirCreation**: () => `void`

#### Returns

`void`

### ouvrirEdition

> **ouvrirEdition**: (`item`) => `void`

#### Parameters

##### item

`T`

#### Returns

`void`

### setDialogOuvert

> **setDialogOuvert**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

## Example

```tsx
const formVide = { nom: "", description: "" };
const [form, setForm] = useState(formVide);

const { dialogOuvert, setDialogOuvert, enEdition, ouvrirCreation, ouvrirEdition, fermerDialog } =
  utiliserDialogCrud<MonType>({
    onOuvrirCreation: () => setForm(formVide),
    onOuvrirEdition: (item) => setForm({ nom: item.nom, description: item.description ?? "" }),
  });
```
