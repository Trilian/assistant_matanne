"use client";

const COULEURS: Record<string, string> = {
  a: "bg-green-700 text-white",
  b: "bg-green-500 text-white",
  c: "bg-yellow-500 text-black",
  d: "bg-orange-500 text-white",
  e: "bg-red-700 text-white",
};

const EMOJIS: Record<string, string> = {
  a: "🌿",
  b: "🌱",
  c: "🍃",
  d: "⚠️",
  e: "🔴",
};

interface BadgeEcoscoreProps {
  grade: string | null | undefined;
  className?: string;
}

export function BadgeEcoscore({ grade, className = "" }: BadgeEcoscoreProps) {
  if (!grade) return null;
  const g = grade.toLowerCase();
  const couleur = COULEURS[g] ?? "bg-muted text-muted-foreground";
  const emoji = EMOJIS[g] ?? "";

  return (
    <span
      className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase leading-none ${couleur} ${className}`}
      title={`Eco-Score ${g.toUpperCase()}`}
    >
      {emoji} {g.toUpperCase()}
    </span>
  );
}
