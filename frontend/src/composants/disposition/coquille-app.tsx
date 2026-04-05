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
import { BandeauHorsLigne } from "./bandeau-hors-ligne";
import { BandeauImpersonation } from "./bandeau-impersonation";
import { PanneauAdminFlottant } from "./panneau-admin-flottant";
import { InstallPrompt } from "@/composants/pwa/install-prompt";
import { useNotificationsJeux } from "@/crochets/utiliser-notifications-jeux";

/**
 * Conteneur principal de l'application — assemble la sidebar desktop, l'en-tête,
 * le fil d'ariane, la zone de contenu scrollable et la navigation mobile.
 */
export function CoquilleApp({ children }: { children: React.ReactNode }) {
  // Activer les notifications jeux
  useNotificationsJeux();

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Lien d'accessibilité : aller au contenu principal */}
      <a
        href="#contenu-principal"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:shadow-lg"
      >
        Aller au contenu principal
      </a>

      {/* Barre de progression de navigation (Idée B) */}
      <BarreProgression />

      {/* Sidebar desktop */}
      <BarreLaterale />

      {/* Zone principale */}
      <div className="flex flex-1 flex-col overflow-hidden">
        <EnTete />
        <BandeauImpersonation />
        <BandeauHorsLigne />
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

      {/* FAB actions rapides mobiles  */}
      <FabActionsRapides />

      {/* FAB assistant vocal global  */}
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
