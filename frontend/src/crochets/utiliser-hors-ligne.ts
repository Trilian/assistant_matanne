'use client'

import { useEffect, useState, useCallback } from 'react'

/**
 * Hook pour détecter le statut hors-ligne et gérer la synchronisation.
 * Utilisé principalement pour le mode courses en magasin.
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

  const forcerSync = useCallback(async () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      const reg = await navigator.serviceWorker.ready
      if ('sync' in reg) {
        await (reg as unknown as { sync: { register: (tag: string) => Promise<void> } }).sync.register('matanne-sync-queue')
      }
    }
  }, [])

  return { estHorsLigne, nbEnAttente, forcerSync }
}
