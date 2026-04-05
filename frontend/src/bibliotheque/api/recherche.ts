/**
 * Client API pour la recherche globale
 */

import { clientApi } from './client'

/**
 * Type de résultat de recherche unifié
 */
export type TypeResultatRecherche =
  | 'recette'
  | 'projet'
  | 'activite'
  | 'note'
  | 'contact'
  | 'plante'
  | 'document'
  | 'abonnement'
  | 'entretien'
  | 'annonce'
  | 'scenario'
  | 'pari'
  | 'loto'
  | 'routine'

export interface ResultatRecherche {
  /** Type d'entité (recette, projet, activite, note, contact, plante, document, abonnement, entretien) */
  type: TypeResultatRecherche
  /** ID de l'entité */
  id: number
  /** Titre principal */
  titre: string
  /** Description ou sous-titre */
  description: string
  /** URL pour naviguer vers l'entité */
  url: string
  /** Nom d'icône Lucide pour l'affichage */
  icone: string
}

/**
 * Effectue une recherche globale multi-entités
 * 
 * @param query Terme de recherche (min 2 caractères)
 * @param limit Nombre maximum de résultats (défaut: 20, max: 100)
 * @returns Liste de résultats unifiés
 * @throws Error si le terme est trop court ou si l'API retourne une erreur
 */
export async function rechercheGlobale(
  query: string,
  limit: number = 20,
  types?: TypeResultatRecherche[]
): Promise<ResultatRecherche[]> {
  if (query.length < 2) {
    throw new Error('Le terme de recherche doit contenir au moins 2 caractères')
  }

  const { data } = await clientApi.get<ResultatRecherche[]>('/api/v1/recherche/global', {
    params: { q: query, limit, types: types?.length ? types.join(',') : undefined }
  })

  return data
}
