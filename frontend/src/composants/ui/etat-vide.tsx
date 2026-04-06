"use client";

import type { LucideIcon } from "lucide-react";

/** Illustrations SVG intégrées pour les états vides courants */
const ILLUSTRATIONS = {
  recettes: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <rect x="30" y="30" width="60" height="48" rx="6" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <rect x="38" y="40" width="44" height="4" rx="2" fill="currentColor" className="text-muted-foreground/40" />
      <rect x="38" y="50" width="32" height="4" rx="2" fill="currentColor" className="text-muted-foreground/30" />
      <rect x="38" y="60" width="38" height="4" rx="2" fill="currentColor" className="text-muted-foreground/30" />
      <circle cx="60" cy="18" r="10" fill="currentColor" className="text-primary/30" stroke="currentColor" strokeWidth="1.5" />
      <path d="M60 12 L60 18 M57 15 L60 18 L63 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary/60" />
    </svg>
  ),
  courses: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <path d="M25 20 L35 70 H85 L95 20 H25Z" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="42" cy="78" r="6" fill="currentColor" className="text-muted-foreground/50" />
      <circle cx="78" cy="78" r="6" fill="currentColor" className="text-muted-foreground/50" />
      <path d="M20 20 H25" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-muted-foreground/40" />
      <rect x="44" y="35" width="32" height="3" rx="1.5" fill="currentColor" className="text-muted-foreground/40" />
      <rect x="44" y="44" width="24" height="3" rx="1.5" fill="currentColor" className="text-muted-foreground/30" />
      <rect x="44" y="53" width="28" height="3" rx="1.5" fill="currentColor" className="text-muted-foreground/30" />
    </svg>
  ),
  planning: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <rect x="20" y="20" width="80" height="62" rx="6" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <rect x="20" y="20" width="80" height="16" rx="6" fill="currentColor" className="text-primary/25" />
      <line x1="40" y1="20" x2="40" y2="82" stroke="currentColor" strokeWidth="1" className="text-muted-foreground/20" />
      <line x1="60" y1="20" x2="60" y2="82" stroke="currentColor" strokeWidth="1" className="text-muted-foreground/20" />
      <line x1="80" y1="20" x2="80" y2="82" stroke="currentColor" strokeWidth="1" className="text-muted-foreground/20" />
      <line x1="20" y1="52" x2="100" y2="52" stroke="currentColor" strokeWidth="1" className="text-muted-foreground/20" />
      <line x1="20" y1="67" x2="100" y2="67" stroke="currentColor" strokeWidth="1" className="text-muted-foreground/20" />
    </svg>
  ),
  jardin: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <rect x="20" y="60" width="80" height="22" rx="4" fill="currentColor" className="text-emerald-500/20" />
      <path d="M60 60 C60 60 45 45 50 30 C55 15 65 20 65 30 C65 20 75 10 80 25 C85 40 70 55 60 60Z" fill="currentColor" className="text-emerald-500/40" />
      <path d="M60 60 C60 60 40 50 35 35 C30 20 45 18 50 30" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" className="text-emerald-600/40" />
      <line x1="60" y1="60" x2="60" y2="82" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-emerald-700/40" />
    </svg>
  ),
  activites: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <circle cx="60" cy="42" r="26" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <path d="M60 26 L65 38 H78 L67 46 L72 58 L60 50 L48 58 L53 46 L42 38 H55Z" fill="currentColor" className="text-primary/30" />
    </svg>
  ),
  inventaire: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <rect x="28" y="28" width="28" height="30" rx="3" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <rect x="64" y="28" width="28" height="30" rx="3" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <rect x="28" y="64" width="28" height="18" rx="3" fill="currentColor" className="text-muted/40" stroke="currentColor" strokeWidth="1.5" />
      <rect x="64" y="64" width="28" height="18" rx="3" fill="currentColor" className="text-muted/40" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  ),
  defaut: (
    <svg viewBox="0 0 120 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-28 h-24 opacity-60">
      <ellipse cx="60" cy="88" rx="44" ry="8" fill="currentColor" className="text-muted-foreground/20" />
      <rect x="28" y="22" width="64" height="58" rx="8" fill="currentColor" className="text-muted/60" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="60" cy="48" r="14" fill="currentColor" className="text-muted-foreground/20" stroke="currentColor" strokeWidth="1.5" />
      <path d="M60 42 L60 48 M60 54 L60 54.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-muted-foreground/50" />
    </svg>
  ),
} as const;

export type IllustrationEtatVide = keyof typeof ILLUSTRATIONS;

export function EtatVide({
  Icone,
  illustration,
  titre,
  description,
  action,
  className,
}: {
  Icone?: LucideIcon;
  illustration?: IllustrationEtatVide;
  titre: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  const svgIllustration = illustration
    ? (ILLUSTRATIONS[illustration] ?? ILLUSTRATIONS.defaut)
    : null;

  return (
    <div
      className={`flex flex-col items-center gap-3 rounded-xl border border-dashed p-8 text-center ${className ?? ""}`}
    >
      {svgIllustration ? (
        <div className="mb-1">{svgIllustration}</div>
      ) : Icone ? (
        <div className="rounded-full bg-muted p-3">
          <Icone className="h-5 w-5 text-muted-foreground" />
        </div>
      ) : null}
      <div>
        <p className="text-sm font-medium">{titre}</p>
        {description && (
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      {action}
    </div>
  );
}
