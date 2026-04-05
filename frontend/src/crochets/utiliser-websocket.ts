'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import type { ObjetDonnees, ValeurDonnee } from '@/types/commun'

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
  [cle: string]: ValeurDonnee
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
  /** URL de fallback pour le polling HTTP */
  urlPollingFallback?: string | null
  /** URL de fallback pour les actions HTTP */
  urlActionFallback?: string | null
  /** Intervalle polling en ms (défaut: 3000) */
  intervallePolling?: number
}

interface RetourWebSocket {
  /** État de la connexion */
  connecte: boolean
  /** Liste des utilisateurs connectés */
  utilisateurs: UtilisateurConnecte[]
  /** Envoyer un message JSON */
  envoyer: (message: ObjetDonnees) => void
  /** Dernier message reçu */
  dernierMessage: MessageWS | null
  /** Erreur de connexion */
  erreur: string | null
  /** Mode de connexion actuel */
  mode: 'websocket' | 'polling' | 'deconnecte'
}

// ═══════════════════════════════════════════════════════════
// HOOK
// ═══════════════════════════════════════════════════════════

/**
 * Hook WebSocket générique avec reconnexion automatique et heartbeat.
 * @param options - URL, gestionnaires par type, délai reconnexion, max tentatives
 * @returns {estConnecte, utilisateursConnectes, envoyer, fermer}
 */
export function utiliserWebSocket({
  url,
  gestionnaires = {},
  delaiReconnexion = 3000,
  maxTentatives = 5,
  intervalleHeartbeat = 30000,
  urlPollingFallback = null,
  urlActionFallback = null,
  intervallePolling = 3000,
}: OptionsWebSocket): RetourWebSocket {
  const [connecte, setConnecte] = useState(false)
  const [utilisateurs, setUtilisateurs] = useState<UtilisateurConnecte[]>([])
  const [dernierMessage, setDernierMessage] = useState<MessageWS | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)
  const [mode, setMode] = useState<'websocket' | 'polling' | 'deconnecte'>('deconnecte')

  const wsRef = useRef<WebSocket | null>(null)
  const tentativesRef = useRef(0)
  const reconnexionRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const gestionnairesRef = useRef(gestionnaires)
  const pendingActionsRef = useRef<ObjetDonnees[]>([])
  const lastSeqRef = useRef(0)

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

    if (typeof window === 'undefined' || typeof window.WebSocket !== 'function') {
      setConnecte(false)
      if (urlPollingFallback) {
        setMode('polling')
        setErreur(null)
        demarrerPolling()
      } else {
        setMode('deconnecte')
        setErreur(null)
      }
      return
    }

    // Fermer l'ancienne connexion
    if (wsRef.current) {
      wsRef.current.close()
    }

    const ws = new window.WebSocket(url)

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

      // Reconnexion auto avec backoff exponentiel
      if (tentativesRef.current < maxTentatives) {
        tentativesRef.current += 1
        const backoff = delaiReconnexion * Math.pow(2, tentativesRef.current - 1)
        reconnexionRef.current = setTimeout(connecter, Math.min(backoff, 30000))
      } else if (urlPollingFallback) {
        // Basculer en mode polling HTTP si la socket échoue.
        setMode('polling')
        setErreur(null)
        demarrerPolling()
      } else {
        setMode('deconnecte')
        setErreur('Connexion perdue. Veuillez rafraîchir la page.')
      }
    }

    ws.onerror = () => {
      setErreur('Erreur de connexion WebSocket')
    }

    wsRef.current = ws
    // La callback de connexion pilote volontairement la reconnexion et le basculement polling.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, delaiReconnexion, maxTentatives, demarrerHeartbeat, arreterHeartbeat])

  // Fallback en polling HTTP quand le WebSocket n'est pas disponible.
  const arreterPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const demarrerPolling = useCallback(() => {
    if (!urlPollingFallback) return
    arreterPolling()

    setConnecte(true)

    const poll = async () => {
      try {
        const res = await fetch(`${urlPollingFallback}?since_seq=${lastSeqRef.current}`)
        if (!res.ok) return
        const data = await res.json()
        if (data.current_seq) lastSeqRef.current = data.current_seq
        if (data.users) setUtilisateurs(data.users)
        for (const change of data.changes ?? []) {
          setDernierMessage(change)
          const handler = gestionnairesRef.current[change.type]
          if (handler) handler(change)
        }
      } catch {
        // Polling error silencieux
      }
    }

    // Premier poll immédiat
    void poll()
    pollingRef.current = setInterval(poll, intervallePolling)
  }, [urlPollingFallback, intervallePolling, arreterPolling])

  // Connexion / déconnexion
  useEffect(() => {
    if (url) {
      setMode('websocket')
      connecter()
    }

    return () => {
      arreterHeartbeat()
      arreterPolling()
      if (reconnexionRef.current) {
        clearTimeout(reconnexionRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [url, connecter, arreterHeartbeat, arreterPolling])

  const envoyer = useCallback((message: ObjetDonnees) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      // Mode WebSocket : envoi direct + flush de la queue
      wsRef.current.send(JSON.stringify(message))
      // Envoyer les actions en attente
      while (pendingActionsRef.current.length > 0) {
        const pending = pendingActionsRef.current.shift()!
        wsRef.current.send(JSON.stringify(pending))
      }
    } else if (mode === 'polling' && urlActionFallback) {
      // Envoyer l'action via HTTP quand le fallback est actif.
      void fetch(urlActionFallback, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message),
      }).catch(() => {
        // Mettre en queue si ça échoue aussi
        pendingActionsRef.current.push(message)
      })
    } else {
      // Mettre en queue pour envoi ultérieur
      pendingActionsRef.current.push(message)
    }
  }, [mode, urlActionFallback])

  return {
    connecte,
    utilisateurs,
    envoyer,
    dernierMessage,
    erreur,
    mode,
  }
}
