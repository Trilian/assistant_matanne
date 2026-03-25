"use client";

const COULEURS: Record<string, string> = {
  a: "bg-green-600 text-white",
  b: "bg-lime-500 text-white",
  c: "bg-yellow-400 text-black",
  d: "bg-orange-500 text-white",
  e: "bg-red-600 text-white",
};

interface BadgeNutriscoreProps {
  grade: string | null | undefined;
  className?: string;
}

export function BadgeNutriscore({ grade, className = "" }: BadgeNutriscoreProps) {
  if (!grade) return null;
  const g = grade.toLowerCase();
  const couleur = COULEURS[g] ?? "bg-muted text-muted-foreground";

  return (
    <span
      className={`inline-flex items-center justify-center rounded px-1.5 py-0.5 text-[10px] font-bold uppercase leading-none ${couleur} ${className}`}
      title={`Nutri-Score ${g.toUpperCase()}`}
    >
      {g.toUpperCase()}
    </span>
  );
}
