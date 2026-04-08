/**
 * Client API pour les bridges inter-modules
 */

import { clientApi } from './client'

// ── Veille immobilière ──

export interface AnnonceImmoResume {
  id: number
  titre: string
  prix: number
  surface: number | null
  ville: string
  date_publication: string
  score_match: number
}

export interface WidgetVeilleImmoResponse {
  annonces_recentes: AnnonceImmoResume[]
  total_actives: number
  prix_moyen: number | null
  derniere_maj: string | null
}

export async function obtenirWidgetVeilleImmo(): Promise<WidgetVeilleImmoResponse> {
  const { data } = await clientApi.get('/bridges/widget-veille-immo')
  return data
}

// ── Saison jardin ──

export interface ActiviteJardinSaison {
  type: string
  description: string
  priorite: string
  plantes_concernees: string[]
}

export interface WidgetSaisonJardinResponse {
  saison: string
  mois: string
  activites: ActiviteJardinSaison[]
  conseil_ia: string | null
}

export async function obtenirWidgetSaisonJardin(): Promise<WidgetSaisonJardinResponse> {
  const { data } = await clientApi.get('/bridges/widget-saison-jardin')
  return data
}
