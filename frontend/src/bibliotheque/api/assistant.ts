import { clientApi } from './client'
import type { ObjetDonnees } from '@/types/commun'

export type AssistantIntent = {
  intent: string
  description: string
  slots: string[]
  action_attendue: string
}

export type AssistantExecutionResponse = {
  intent: string
  langue: string
  commande: string
  resultat: {
    action: string
    message: string
    details?: ObjetDonnees
  }
}

export async function listerIntentsGoogleAssistant(): Promise<{ intents: AssistantIntent[] }> {
  const { data } = await clientApi.get<{ intents: AssistantIntent[] }>('/assistant/google-assistant/intents')
  return data
}

export async function executerIntentGoogleAssistant(payload: {
  intent: string
  slots: Record<string, string>
  langue?: string
}): Promise<AssistantExecutionResponse> {
  const { data } = await clientApi.post<AssistantExecutionResponse>(
    '/assistant/google-assistant/executer',
    payload
  )
  return data
}
