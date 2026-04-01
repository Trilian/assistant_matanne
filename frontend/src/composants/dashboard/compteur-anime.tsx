// ═══════════════════════════════════════════════════════════
// CompteurAnime — Incrémentation animée des valeurs numériques
// ═══════════════════════════════════════════════════════════

"use client";

import { useEffect, useRef, useState } from "react";

interface CompteurAnimeProps {
  valeur: number;
  duree?: number;
  prefixe?: string;
  suffixe?: string;
  decimales?: number;
  className?: string;
}

export function CompteurAnime({
  valeur,
  duree = 800,
  prefixe = "",
  suffixe = "",
  decimales = 0,
  className,
}: CompteurAnimeProps) {
  const [affichage, setAffichage] = useState(0);
  const precedent = useRef(0);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const debut = precedent.current;
    const diff = valeur - debut;
    if (diff === 0) return;

    const start = performance.now();

    function animer(now: number) {
      const elapsed = now - start;
      const progression = Math.min(elapsed / duree, 1);
      // Easing: easeOutCubic
      const ease = 1 - Math.pow(1 - progression, 3);
      const courant = debut + diff * ease;
      setAffichage(courant);

      if (progression < 1) {
        rafRef.current = requestAnimationFrame(animer);
      } else {
        precedent.current = valeur;
      }
    }

    rafRef.current = requestAnimationFrame(animer);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [valeur, duree]);

  const texte = `${prefixe}${affichage.toFixed(decimales)}${suffixe}`;

  return <span className={className}>{texte}</span>;
}
