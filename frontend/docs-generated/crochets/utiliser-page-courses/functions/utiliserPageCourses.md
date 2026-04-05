[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [crochets/utiliser-page-courses](../README.md) / utiliserPageCourses

# Function: utiliserPageCourses()

> **utiliserPageCourses**(): `object`

Defined in: [crochets/utiliser-page-courses.ts:49](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/crochets/utiliser-page-courses.ts#L49)

Hook principal de la page courses — orchestre formulaire, listes, prédictions, mode invités et Telegram.

## Returns

`object`

État complet de la page courses (formulaire, listes, articles, actions CRUD)

### ajouter

> **ajouter**: `UseMutateFunction`\<[`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md), `Error`, \{ `categorie?`: `string`; `magasin_cible?`: `string`; `nom`: `string`; `prix_estime?`: `number`; `quantite?`: `number`; `unite?`: `string`; \}, `ContexteArticle`\>

### arreterEcoute

> **arreterEcoute**: () => `void`

#### Returns

`void`

### articles

> **articles**: [`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md)[]

### articlesCoches

> **articlesCoches**: [`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md)[]

### articlesNonCoches

> **articlesNonCoches**: [`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md)[]

### articlesSelectionnes

> **articlesSelectionnes**: `Set`\<`number`\>

### basculerSelectionArticle

> **basculerSelectionArticle**: (`articleId`) => `void`

#### Parameters

##### articleId

`number`

#### Returns

`void`

### bioLocal

> **bioLocal**: \{ `liste_id`: `number`; `mois`: `string`; `nb_en_saison`: `number`; `suggestions`: [`SuggestionBioLocal`](../../../bibliotheque/api/courses/interfaces/SuggestionBioLocal.md)[]; \} \| `undefined`

### categoriesTriees

> **categoriesTriees**: `string`[]

### chargementDetail

> **chargementDetail**: `boolean`

### chargementListes

> **chargementListes**: `boolean`

### chargementQr

> **chargementQr**: `boolean`

### cocher

> **cocher**: `UseMutateFunction`\<[`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md), `Error`, \{ `articleId`: `number`; `coche`: `boolean`; \}, \{ `precedentDetail?`: `undefined`; `precedentListes?`: `undefined`; \} \| \{ `precedentDetail`: `unknown`; `precedentListes`: `unknown`; \}\>

### cocherCategorie

> **cocherCategorie**: `UseMutateFunction`\<\{ `categorie`: `string`; `total`: `number`; \}, `Error`, `string`, `unknown`\>

### cocherSelection

> **cocherSelection**: `UseMutateFunction`\<\{ `total`: `number`; \}, `Error`, `void`, `unknown`\>

### cocherTout

> **cocherTout**: `UseMutateFunction`\<\{ `total`: `number`; \}, `Error`, `void`, `unknown`\>

### confirmer

> **confirmer**: `UseMutateFunction`\<\{ `id`: `number`; `message`: `string`; \}, `Error`, `void`, `unknown`\>

### creerListe

> **creerListe**: `UseMutateFunction`\<[`ListeCourses`](../../../types/courses/interfaces/ListeCourses.md), `Error`, `string`, `unknown`\>

### demarrerEcoute

> **demarrerEcoute**: () => `void`

#### Returns

`void`

### detailListe

> **detailListe**: [`ListeCourses`](../../../types/courses/interfaces/ListeCourses.md) \| `undefined`

### dialogueArticle

> **dialogueArticle**: `boolean`

### dialogueQr

> **dialogueQr**: `boolean`

### enAjout

> **enAjout**: `boolean`

### enCochageCategorie

> **enCochageCategorie**: `boolean`

### enCochageGlobal

> **enCochageGlobal**: `boolean`

### enCochageSelection

> **enCochageSelection**: `boolean`

### enConfirmation

> **enConfirmation**: `boolean`

### enCreationListe

> **enCreationListe**: `boolean`

### enEcoute

> **enEcoute**: `boolean`

### enFinalisationCourses

> **enFinalisationCourses**: `boolean`

### enSuppressionSelection

> **enSuppressionSelection**: `boolean`

### enValidation

> **enValidation**: `boolean`

### erreursArticle

> **erreursArticle**: `FieldErrors`\<\{ `categorie?`: `string`; `magasin_cible?`: `string`; `nom`: `string`; `prix_estime?`: `number`; `quantite?`: `number`; `unite?`: `string`; \}\>

### estSupporte

> **estSupporte**: `boolean`

### evenementsModeInvites

> **evenementsModeInvites**: `string`[]

### finaliserCourses

> **finaliserCourses**: `UseMutateFunction`\<\{ `listeReportId`: `number` \| `null`; `reportes`: `number`; \}, `Error`, `void`, `unknown`\>

### groupesNonCoches

> **groupesNonCoches**: `Record`\<`string`, [`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md)[]\>

### importerDepuisScanner

> **importerDepuisScanner**: (`trouves`, `inconnus`) => `Promise`\<`void`\>

#### Parameters

##### trouves

[`ArticleBarcode`](../../../bibliotheque/api/inventaire/interfaces/ArticleBarcode.md)[]

##### inconnus

`string`[]

#### Returns

`Promise`\<`void`\>

### inputAjoutRef

> **inputAjoutRef**: `RefObject`\<`HTMLInputElement` \| `null`\>

### listes

> **listes**: [`ListeCourses`](../../../types/courses/interfaces/ListeCourses.md)[] \| `undefined`

### listeSelectionnee

> **listeSelectionnee**: `number` \| `null`

### mettreAJourModeInvites

> **mettreAJourModeInvites**: (`miseAJour`) => `void`

#### Parameters

##### miseAJour

`Partial`\<[`ContexteModeInvites`](../../utiliser-mode-invites/interfaces/ContexteModeInvites.md)\> \| ((`precedent`) => `Partial`\<[`ContexteModeInvites`](../../utiliser-mode-invites/interfaces/ContexteModeInvites.md)\>)

#### Returns

`void`

### modeInvites

> **modeInvites**: [`ContexteModeInvites`](../../utiliser-mode-invites/interfaces/ContexteModeInvites.md)

### modeSelection

> **modeSelection**: `boolean`

### nomNouvelleListe

> **nomNouvelleListe**: `string`

### ouvrirQrPartage

> **ouvrirQrPartage**: () => `Promise`\<`void`\>

#### Returns

`Promise`\<`void`\>

### panneauBio

> **panneauBio**: `boolean`

### predictionsInvites

> **predictionsInvites**: [`PredictionsCoursesResponse`](../../../bibliotheque/api/courses/interfaces/PredictionsCoursesResponse.md) \| `undefined`

### qrUrl

> **qrUrl**: `string` \| `null`

### recurrents

> **recurrents**: \{ `suggestions`: [`ArticleRecurrent`](../../../bibliotheque/api/courses/interfaces/ArticleRecurrent.md)[]; `total`: `number`; \} \| `undefined`

### regArticle

> **regArticle**: `UseFormRegister`\<\{ `categorie?`: `string`; `magasin_cible?`: `string`; `nom`: `string`; `prix_estime?`: `number`; `quantite?`: `number`; `unite?`: `string`; \}\>

### reinitialiserModeInvites

> **reinitialiserModeInvites**: () => `void`

#### Returns

`void`

### scanneurOuvert

> **scanneurOuvert**: `boolean`

### setArticlesSelectionnes

> **setArticlesSelectionnes**: `Dispatch`\<`SetStateAction`\<`Set`\<`number`\>\>\>

### setDialogueArticle

> **setDialogueArticle**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

### setDialogueQr

> **setDialogueQr**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

### setListeSelectionnee

> **setListeSelectionnee**: `Dispatch`\<`SetStateAction`\<`number` \| `null`\>\>

### setModeSelection

> **setModeSelection**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

### setNomNouvelleListe

> **setNomNouvelleListe**: `Dispatch`\<`SetStateAction`\<`string`\>\>

### setPanneauBio

> **setPanneauBio**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

### setQrUrl

> **setQrUrl**: `Dispatch`\<`SetStateAction`\<`string` \| `null`\>\>

### setScanneurOuvert

> **setScanneurOuvert**: `Dispatch`\<`SetStateAction`\<`boolean`\>\>

### submitArticle

> **submitArticle**: `UseFormHandleSubmit`\<\{ `categorie?`: `string`; `magasin_cible?`: `string`; `nom`: `string`; `prix_estime?`: `number`; `quantite?`: `number`; `unite?`: `string`; \}, \{ `categorie?`: `string`; `magasin_cible?`: `string`; `nom`: `string`; `prix_estime?`: `number`; `quantite?`: `number`; `unite?`: `string`; \}\>

### suggestionsInvites

> **suggestionsInvites**: `string`[]

### supprimerAvecUndo

> **supprimerAvecUndo**: (`article`) => `void`

#### Parameters

##### article

[`ArticleCourses`](../../../types/courses/interfaces/ArticleCourses.md)

#### Returns

`void`

### supprimerSelection

> **supprimerSelection**: `UseMutateFunction`\<\{ `total`: `number`; \}, `Error`, `void`, `unknown`\>

### telechargerQr

> **telechargerQr**: () => `void`

#### Returns

`void`

### valider

> **valider**: `UseMutateFunction`\<\{ `id`: `number`; `message`: `string`; \}, `Error`, `void`, `unknown`\>
