// ═══════════════════════════════════════════════════════════
// Coquille App — Conteneur principal responsive
// ═══════════════════════════════════════════════════════════

import { BarreLaterale } from "./barre-laterale";
import { NavMobile } from "./nav-mobile";
import { EnTete } from "./en-tete";
import { FilAriane } from "./fil-ariane";
import { RechercheGlobale } from "./recherche-globale";
import { TourOnboarding } from "./tour-onboarding";

/**
 * Conteneur principal de l'application — assemble la sidebar desktop, l'en-tête,
 * le fil d'ariane, la zone de contenu scrollable et la navigation mobile.
 */
export function CoquilleApp({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar desktop */}
      <BarreLaterale />

      {/* Zone principale */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <EnTete />
        <FilAriane />

        {/* Contenu scrollable */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
          {children}
        </main>

        {/* Bottom nav mobile */}
        <NavMobile />
      </div>

      {/* Recherche globale (Ctrl+K) */}
      <RechercheGlobale />

      {/* Tour d'onboarding pour nouveaux utilisateurs */}
      <TourOnboarding />
    </div>
  );
}
