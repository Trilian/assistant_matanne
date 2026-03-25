'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

// ═══════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════

interface UtilisateurConnecte {
  user_id: string
  username: string
  connected_at: string
}

interface MessageWS {
  type: string
  [cle: string]: unknown
}

interface OptionsWebSocket {
  /** URL WebSocket complète (ex: ws://localhost:8000/api/v1/ws/planning/1?user=xxx) */
  url: string | null
  /** Callbacks par type de message */
  gestionnaires?: Record<string, (data: MessageWS) => void>
  /** Intervalle de reconnexion en ms (défaut: 3000) */
  delaiReconnexion?: number
  /** Nombre max de tentatives de reconnexion (défaut: 5) */
  maxTentatives?: number
  /** Intervalle heartbeat en ms (défaut: 30000) */
  intervalleHeartbeat?: number
}

interface RetourWebSocket {
  /** État de la connexion */
  connecte: boolean
  /** Liste des utilisateurs connectés */
  utilisateurs: UtilisateurConnecte[]
  /** Envoyer un message JSON */
  envoyer: (message: Record<string, unknown>) => void
  /** Dernier message reçu */
  dernierMessage: MessageWS | null
  /** Erreur de connexion */
  erreur: string | null
}

// ═══════════════════════════════════════════════════════════
// HOOK
// ═══════════════════════════════════════════════════════════

export function utiliserWebSocket({
  url,
  gestionnaires = {},
  delaiReconnexion = 3000,
  maxTentatives = 5,
  intervalleHeartbeat = 30000,
}: OptionsWebSocket): RetourWebSocket {
  const [connecte, setConnecte] = useState(false)
  const [utilisateurs, setUtilisateurs] = useState<UtilisateurConnecte[]>([])
  const [dernierMessage, setDernierMessage] = useState<MessageWS | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const tentativesRef = useRef(0)
  const reconnexionRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const gestionnairesRef = useRef(gestionnaires)

  // Garder les gestionnaires à jour sans recréer la connexion
  useEffect(() => {
    gestionnairesRef.current = gestionnaires
  }, [gestionnaires])

  const arreterHeartbeat = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current)
      heartbeatRef.current = null
    }
  }, [])

  const demarrerHeartbeat = useCallback(() => {
    arreterHeartbeat()
    heartbeatRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: 'ping' }))
      }
    }, intervalleHeartbeat)
  }, [intervalleHeartbeat, arreterHeartbeat])

  const connecter = useCallback(() => {
    if (!url) return

    // Fermer l'ancienne connexion
    if (wsRef.current) {
      wsRef.current.close()
    }

    const ws = new WebSocket(url)

    ws.onopen = () => {
      setConnecte(true)
      setErreur(null)
      tentativesRef.current = 0
      demarrerHeartbeat()
    }

    ws.onmessage = (event) => {
      try {
        const data: MessageWS = JSON.parse(event.data)
        setDernierMessage(data)

        // Gestion des types de base
        switch (data.type) {
          case 'users_list':
            setUtilisateurs((data.users as UtilisateurConnecte[]) ?? [])
            break
          case 'user_joined':
            setUtilisateurs((prev) => [
              ...prev.filter((u) => u.user_id !== data.user_id),
              {
                user_id: data.user_id as string,
                username: data.username as string,
                connected_at: data.timestamp as string,
              },
            ])
            break
          case 'user_left':
            setUtilisateurs((prev) =>
              prev.filter((u) => u.user_id !== data.user_id)
            )
            break
          case 'pong':
            // Heartbeat OK
            break
          default:
            break
        }

        // Appeler le gestionnaire spécifique si défini
        const handler = gestionnairesRef.current[data.type]
        if (handler) {
          handler(data)
        }
      } catch {
        // Message non-JSON ignoré
      }
    }

    ws.onclose = () => {
      setConnecte(false)
      arreterHeartbeat()

      // Reconnexion auto
      if (tentativesRef.current < maxTentatives) {
        tentativesRef.current += 1
        reconnexionRef.current = setTimeout(connecter, delaiReconnexion)
      } else {
        setErreur('Connexion perdue. Veuillez rafraîchir la page.')
      }
    }

    ws.onerror = () => {
      setErreur('Erreur de connexion WebSocket')
    }

    wsRef.current = ws
  }, [url, delaiReconnexion, maxTentatives, demarrerHeartbeat, arreterHeartbeat])

  // Connexion / déconnexion
  useEffect(() => {
    if (url) {
      connecter()
    }

    return () => {
      arreterHeartbeat()
      if (reconnexionRef.current) {
        clearTimeout(reconnexionRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [url, connecter, arreterHeartbeat])

  const envoyer = useCallback((message: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [])

  return {
    connecte,
    utilisateurs,
    envoyer,
    dernierMessage,
    erreur,
  }
}
