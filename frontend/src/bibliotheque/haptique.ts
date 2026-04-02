// Utilitaires de feedback haptique pour mobile.

export type TypeHaptique = "light" | "medium" | "success" | "error";

const MOTIFS: Record<TypeHaptique, number | number[]> = {
  light: 20,
  medium: 35,
  success: [20, 30, 20],
  error: [40, 25, 40],
};

export function declencherHaptique(type: TypeHaptique = "light"): void {
  if (typeof window === "undefined") return;
  if (typeof navigator === "undefined" || typeof navigator.vibrate !== "function") return;

  navigator.vibrate(MOTIFS[type]);
}
