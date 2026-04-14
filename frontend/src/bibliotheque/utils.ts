import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Formate une durée en minutes en chaîne lisible.
 * - < 60 min → "X min"
 * - >= 60 min → "Xh" ou "Xh Ymin"
 */
export function formaterDuree(minutes: number): string {
  if (minutes < 60) return `${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}min`;
}

export function couleurBarreBudget(pct: number, inclureSeuilBloquant = false): string {
  if (inclureSeuilBloquant && pct >= 100) return "bg-red-600"
  if (pct >= 90) return "bg-red-500"
  if (pct >= 75) return "bg-orange-400"
  if (pct >= 50) return "bg-yellow-400"
  return "bg-green-500"
}
