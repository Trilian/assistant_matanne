// ═══════════════════════════════════════════════════════════
// Coquille App — Conteneur principal responsive
// ═══════════════════════════════════════════════════════════

import { BarreLaterale } from "./barre-laterale";
import { NavMobile } from "./nav-mobile";
import { EnTete } from "./en-tete";
import { FilAriane } from "./fil-ariane";
import { MenuCommandes } from "./menu-commandes";
import { TourOnboarding } from "./tour-onboarding";
import { FabChatIA } from "./fab-chat-ia";
import { MinuteurFlottant } from "./minuteur-flottant";
import { InstallPrompt } from "@/composants/pwa/install-prompt";

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

      {/* Menu commandes avec navigation rapide (Ctrl+K) */}
      <MenuCommandes />

      {/* FAB chat IA flottant (AC2) */}
      <FabChatIA />

      {/* Minuteur flottant (AC2) */}
      <MinuteurFlottant />

      {/* Tour d'onboarding pour nouveaux utilisateurs */}
      <TourOnboarding />

      {/* Bannière d'installation PWA */}
      <InstallPrompt />
    </div>
  );
}
