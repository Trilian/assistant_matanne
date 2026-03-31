// ═══════════════════════════════════════════════════════════
// Fournisseur Thème — Dark/Light mode via next-themes
// ═══════════════════════════════════════════════════════════

"use client";

import { ThemeProvider } from "next-themes";
import type { ReactNode } from "react";
import { useEffect } from "react";
import { useTheme } from "next-themes";

type Saison = "printemps" | "ete" | "automne" | "hiver";

function obtenirSaison(date: Date): Saison {
  const mois = date.getMonth() + 1;
  if (mois >= 3 && mois <= 5) {
    return "printemps";
  }
  if (mois >= 6 && mois <= 8) {
    return "ete";
  }
  if (mois >= 9 && mois <= 11) {
    return "automne";
  }
  return "hiver";
}

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

function ThemeSaisonnier() {
  useEffect(() => {
    const appliquerSaison = () => {
      const saison = obtenirSaison(new Date());
      document.documentElement.setAttribute("data-saison", saison);
    };

    appliquerSaison();
    const intervalle = window.setInterval(appliquerSaison, 6 * 60 * 60 * 1000);

    return () => window.clearInterval(intervalle);
  }, []);

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
      <ThemeSaisonnier />
      {children}
    </ThemeProvider>
  );
}
