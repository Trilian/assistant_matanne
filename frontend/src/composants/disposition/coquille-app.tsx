// ═══════════════════════════════════════════════════════════
// Coquille App — Conteneur principal responsive
// ═══════════════════════════════════════════════════════════

import { BarreLaterale } from "./barre-laterale";
import { NavMobile } from "./nav-mobile";
import { EnTete } from "./en-tete";
import { FilAriane } from "./fil-ariane";

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
    </div>
  );
}
