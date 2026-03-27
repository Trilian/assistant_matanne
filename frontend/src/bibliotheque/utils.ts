import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function couleurBarreBudget(pct: number, inclureSeuilBloquant = false): string {
  if (inclureSeuilBloquant && pct >= 100) return "bg-red-600"
  if (pct >= 90) return "bg-red-500"
  if (pct >= 75) return "bg-orange-400"
  if (pct >= 50) return "bg-yellow-400"
  return "bg-green-500"
}
