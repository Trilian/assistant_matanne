// ═══════════════════════════════════════════════════════════
// Coquille App — Conteneur principal responsive
// ═══════════════════════════════════════════════════════════

"use client";

import { BarreLaterale } from "./barre-laterale";
import { NavMobile } from "./nav-mobile";
import { EnTete } from "./en-tete";
import { FilAriane } from "./fil-ariane";
import { MenuCommandes } from "./menu-commandes";
import { TourOnboarding } from "./tour-onboarding";
import { FabChatIA } from "./fab-chat-ia";
import { FabAssistantVocal } from "./fab-assistant-vocal";
import { FabActionsRapides } from "./fab-actions-rapides";
import { MinuteurFlottant } from "./minuteur-flottant";
import { BarreProgression } from "./barre-progression";
import { ContenuPrincipal } from "./contenu-principal";
import { BandeauSuggestionProactive } from "./bandeau-suggestion-proactive";
import { PanneauAdminFlottant } from "./panneau-admin-flottant";
import { InstallPrompt } from "@/composants/pwa/install-prompt";
import { useNotificationsJeux } from "@/crochets/utiliser-notifications-jeux";

/**
 * Conteneur principal de l'application — assemble la sidebar desktop, l'en-tête,
 * le fil d'ariane, la zone de contenu scrollable et la navigation mobile.
 */
export function CoquilleApp({ children }: { children: React.ReactNode }) {
  // Activer les notifications jeux (Phase W)
  useNotificationsJeux();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Barre de progression de navigation (Idée B) */}
      <BarreProgression />

      {/* Sidebar desktop */}
      <BarreLaterale />

      {/* Zone principale */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <EnTete />
        <FilAriane />
        <BandeauSuggestionProactive />

        {/* Contenu scrollable avec fade-in (Idée E) */}
        <ContenuPrincipal>
          {children}
        </ContenuPrincipal>

        {/* Bottom nav mobile */}
        <NavMobile />
      </div>

      {/* Menu commandes avec navigation rapide (Ctrl+K) */}
      <MenuCommandes />

      {/* FAB chat IA flottant (AC2) */}
      <FabChatIA />

      {/* FAB actions rapides mobiles (Phase 4) */}
      <FabActionsRapides />

      {/* FAB assistant vocal global (Sprint 8) */}
      <FabAssistantVocal />

      {/* Minuteur flottant (AC2) */}
      <MinuteurFlottant />

      {/* Tour d'onboarding pour nouveaux utilisateurs */}
      <TourOnboarding />

      {/* Panneau admin flottant (Ctrl+Shift+A) */}
      <PanneauAdminFlottant />

      {/* Bannière d'installation PWA */}
      <InstallPrompt />
    </div>
  );
}
