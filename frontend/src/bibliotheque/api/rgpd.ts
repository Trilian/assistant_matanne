import { apiClient } from './client'

export async function exporterDonnees(): Promise<Blob> {
  const { data } = await apiClient.get('/api/v1/rgpd/export', {
    responseType: 'blob',
  })
  return data
}

export interface ResumeDonnees {
  user_id: string
  categories: { categorie: string; nombre: number }[]
  total_elements: number
}

export async function obtenirResumeDonnees(): Promise<ResumeDonnees> {
  const { data } = await apiClient.get('/api/v1/rgpd/data-summary')
  return data
}

export interface SuppressionResponse {
  message: string
  deleted_at: string
  elements_supprimes: number
}

export async function supprimerCompte(
  confirmation: string,
  motif?: string
): Promise<SuppressionResponse> {
  const { data } = await apiClient.post('/api/v1/rgpd/delete-account', {
    confirmation,
    motif,
  })
  return data
}
