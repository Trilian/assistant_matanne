/**
 * Helpers partagés entre les pages Loto et Euromillions.
 */

/** Formate une date ISO en format français court (ex: "15 avr. 2025") */
export function formaterDate(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** Parse une liste de numéros depuis un string URL (ex: "1,5,12,33,49") */
export function parseListeNumeros(
  raw: string | null,
  min: number,
  max: number,
  attendu: number
): number[] {
  if (!raw) return [];
  const nums = raw
    .split(",")
    .map((v) => Number(v.trim()))
    .filter((n) => Number.isInteger(n) && n >= min && n <= max);
  const uniq = Array.from(new Set(nums)).sort((a, b) => a - b);
  return uniq.length === attendu ? uniq : [];
}
