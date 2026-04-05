[**Assistant Matanne — Frontend**](../../../README.md)

***

[Assistant Matanne — Frontend](../../../README.md) / [bibliotheque/validateurs](../README.md) / schemaEvenementFamilial

# Variable: schemaEvenementFamilial

> `const` **schemaEvenementFamilial**: `ZodObject`\<\{ `date_evenement`: `ZodString`; `notes`: `ZodOptional`\<`ZodNullable`\<`ZodString`\>\>; `participants`: `ZodOptional`\<`ZodNullable`\<`ZodArray`\<`ZodString`\>\>\>; `rappel_jours_avant`: `ZodDefault`\<`ZodCoercedNumber`\<`unknown`\>\>; `recurrence`: `ZodDefault`\<`ZodEnum`\<\{ `annuelle`: `"annuelle"`; `mensuelle`: `"mensuelle"`; `unique`: `"unique"`; \}\>\>; `titre`: `ZodString`; `type_evenement`: `ZodEnum`\<\{ `anniversaire`: `"anniversaire"`; `fete`: `"fete"`; `rentree`: `"rentree"`; `tradition`: `"tradition"`; `vacances`: `"vacances"`; \}\>; \}, `$strip`\>

Defined in: [bibliotheque/validateurs-famille.ts:21](https://github.com/Trilian/assistant_matanne/blob/363b51de0e987de2bff6b0f6d8a68f1492dc8d71/frontend/src/bibliotheque/validateurs-famille.ts#L21)
