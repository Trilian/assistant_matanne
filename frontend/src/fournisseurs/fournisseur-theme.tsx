// ═══════════════════════════════════════════════════════════
// Fournisseur Thème — Dark/Light mode via next-themes
// ═══════════════════════════════════════════════════════════

"use client";

import { ThemeProvider } from "next-themes";
import type { ReactNode } from "react";
import { useEffect } from "react";
import { useTheme } from "next-themes";

function ThemeAutoHoraire() {
  const { setTheme } = useTheme();

  useEffect(() => {
    const appliquerThemeHoraire = () => {
      const heure = new Date().getHours();
      const modeSombre = heure >= 21 || heure < 7;
      setTheme(modeSombre ? "dark" : "light");
    };

    appliquerThemeHoraire();
    const intervalle = window.setInterval(appliquerThemeHoraire, 60 * 60 * 1000);

    return () => window.clearInterval(intervalle);
  }, [setTheme]);

  return null;
}

export function FournisseurTheme({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <ThemeAutoHoraire />
      {children}
    </ThemeProvider>
  );
}
