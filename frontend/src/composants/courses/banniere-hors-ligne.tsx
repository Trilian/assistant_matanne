'use client'

import { WifiOff, RefreshCw, CloudOff } from 'lucide-react'
import { utiliserHorsLigne } from '@/crochets/utiliser-hors-ligne'

/**
 * Bannière indiquant le mode hors-ligne pour les courses en magasin.
 * Affiche le nombre de modifications en attente de synchronisation.
 */
export function BanniereHorsLigne() {
  const { estHorsLigne, nbEnAttente, forcerSync } = utiliserHorsLigne()

  if (!estHorsLigne) return null

  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-200">
      <div className="flex items-center gap-2">
        <WifiOff className="h-4 w-4 shrink-0" />
        <span className="font-medium">Mode hors-ligne</span>
        <span className="text-amber-600 dark:text-amber-400">
          — Tes courses sont accessibles, les modifications seront synchronisées au retour du réseau.
        </span>
      </div>
      <div className="flex items-center gap-3">
        {nbEnAttente > 0 && (
          <span className="flex items-center gap-1 text-xs">
            <CloudOff className="h-3 w-3" />
            {nbEnAttente} en attente
          </span>
        )}
        <button
          type="button"
          onClick={forcerSync}
          className="flex items-center gap-1 rounded-md bg-amber-200 px-2 py-1 text-xs font-medium text-amber-900 hover:bg-amber-300 dark:bg-amber-800 dark:text-amber-100 dark:hover:bg-amber-700"
        >
          <RefreshCw className="h-3 w-3" />
          Synchroniser
        </button>
      </div>
    </div>
  )
}
