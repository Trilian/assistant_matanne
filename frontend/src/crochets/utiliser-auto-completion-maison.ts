// ═══════════════════════════════════════════════════════════
// Hook auto-complétion maison — suggestions IA onBlur
// Auto-complétion maison
// ═══════════════════════════════════════════════════════════

import { useState } from "react";
import { autoCompleterChamp } from "@/bibliotheque/api/maison";

/**
 * Hook de complétion automatique des champs de formulaires maison.
 * Appelle l'IA pour suggérer une valeur si le champ cible est vide.
 */
export function utiliserAutoCompletionMaison(contexte: string) {
  const [enChargement, setEnChargement] = useState(false);

  const autoCompleter = async (
    champ: string,
    valeur: string,
    setter: (val: string) => void
  ) => {
    if (valeur.length < 3) return;
    setEnChargement(true);
    try {
      const resultat = await autoCompleterChamp(champ, valeur, contexte);
      const suggestion = resultat.suggestions;
      // On ne remplace jamais une saisie utilisateur — uniquement si le champ cible est vide
      if (suggestion.categorie) {
        setter(suggestion.categorie);
      } else if (suggestion.description) {
        setter(suggestion.description);
      }
    } catch {
      // Échec silencieux — l'auto-complétion est facultative
    } finally {
      setEnChargement(false);
    }
  };

  return { autoCompleter, isLoading: enChargement };
}
