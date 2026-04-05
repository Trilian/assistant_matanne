'use client'

import { useEffect, useState, useCallback } from 'react'

const CACHE_PREFIX = 'matanne-offline-'
const CLES_CACHE = ['recette-du-jour', 'courses-actives', 'taches-jour'] as const
type CleCacheHorsLigne = (typeof CLES_CACHE)[number]

/**
 * Hook pour détecter le statut hors-ligne et gérer la synchronisation.
 * Cache les données essentielles (recette du jour, courses, tâches) dans localStorage
 * pour consultation hors-ligne en magasin.
 */
export function utiliserHorsLigne() {
  const [estHorsLigne, setEstHorsLigne] = useState(false)
  const [nbEnAttente, setNbEnAttente] = useState(0)

  useEffect(() => {
    setEstHorsLigne(!navigator.onLine)

    const handleOnline = () => setEstHorsLigne(false)
    const handleOffline = () => setEstHorsLigne(true)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Compter les requêtes en attente dans IndexedDB
  useEffect(() => {
    if (!estHorsLigne) {
      setNbEnAttente(0)
      return
    }

    const compterEnAttente = async () => {
      try {
        const req = indexedDB.open('matanne-sync', 1)
        req.onsuccess = (e) => {
          const db = (e.target as IDBOpenDBRequest).result
          if (!db.objectStoreNames.contains('queue')) {
            setNbEnAttente(0)
            return
          }
          const tx = db.transaction('queue', 'readonly')
          const countReq = tx.objectStore('queue').count()
          countReq.onsuccess = () => setNbEnAttente(countReq.result)
        }
      } catch {
        setNbEnAttente(0)
      }
    }

    compterEnAttente()
    const interval = setInterval(compterEnAttente, 5000)
    return () => clearInterval(interval)
  }, [estHorsLigne])

  useEffect(() => {
    if (!("serviceWorker" in navigator)) return

    const handleMessage = (event: MessageEvent) => {
      const data = event.data as { type?: string; pending?: number } | undefined
      if (!data?.type) return
      if (data.type === "SYNC_QUEUE_UPDATED") {
        setNbEnAttente(typeof data.pending === "number" ? data.pending : 0)
      }
      if (data.type === "SYNC_QUEUE_FLUSHED") {
        setNbEnAttente(0)
      }
    }

    navigator.serviceWorker.addEventListener("message", handleMessage)
    return () => navigator.serviceWorker.removeEventListener("message", handleMessage)
  }, [])

  const forcerSync = useCallback(async () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      const reg = await navigator.serviceWorker.ready
      if ('sync' in reg) {
        await (reg as unknown as { sync: { register: (tag: string) => Promise<void> } }).sync.register('matanne-sync-queue')
      }
    }
  }, [])

  /**
   * Sauvegarde des données en cache localStorage pour consultation hors-ligne.
   */
  const cacherDonnees = useCallback(<T,>(cle: CleCacheHorsLigne, donnees: T) => {
    try {
      localStorage.setItem(
        `${CACHE_PREFIX}${cle}`,
        JSON.stringify({ donnees, timestamp: Date.now() })
      )
    } catch {
      // localStorage plein — on ignore silencieusement
    }
  }, [])

  /**
   * Récupère les données depuis le cache localStorage.
   * Retourne null si absent ou expiré (TTL = 24h par défaut).
   */
  const lireCacheDonnees = useCallback(<T,>(cle: CleCacheHorsLigne, ttlMs = 24 * 60 * 60 * 1000): T | null => {
    try {
      const brut = localStorage.getItem(`${CACHE_PREFIX}${cle}`)
      if (!brut) return null
      const { donnees, timestamp } = JSON.parse(brut) as { donnees: T; timestamp: number }
      if (Date.now() - timestamp > ttlMs) return null
      return donnees
    } catch {
      return null
    }
  }, [])

  /**
   * Supprime les entrées expirées du cache hors-ligne.
   */
  const nettoyerCache = useCallback(() => {
    for (const cle of CLES_CACHE) {
      lireCacheDonnees(cle) // side-effect: retourne null si expiré mais ne supprime pas
      try {
        const brut = localStorage.getItem(`${CACHE_PREFIX}${cle}`)
        if (!brut) continue
        const { timestamp } = JSON.parse(brut) as { timestamp: number }
        if (Date.now() - timestamp > 24 * 60 * 60 * 1000) {
          localStorage.removeItem(`${CACHE_PREFIX}${cle}`)
        }
      } catch {
        localStorage.removeItem(`${CACHE_PREFIX}${cle}`)
      }
    }
  }, [lireCacheDonnees])

  return { estHorsLigne, nbEnAttente, forcerSync, cacherDonnees, lireCacheDonnees, nettoyerCache }
}
