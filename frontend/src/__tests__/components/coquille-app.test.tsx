import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { CoquilleApp } from "@/composants/disposition/coquille-app";

const mockNotificationsJeux = vi.fn();

vi.mock("@/crochets/utiliser-notifications-jeux", () => ({
  useNotificationsJeux: () => mockNotificationsJeux(),
}));

vi.mock("@/composants/disposition/barre-laterale", () => ({
  BarreLaterale: () => <div>BarreLateraleMock</div>,
}));
vi.mock("@/composants/disposition/nav-mobile", () => ({
  NavMobile: () => <div>NavMobileMock</div>,
}));
vi.mock("@/composants/disposition/en-tete", () => ({
  EnTete: () => <div>EnTeteMock</div>,
}));
vi.mock("@/composants/disposition/fil-ariane", () => ({
  FilAriane: () => <div>FilArianeMock</div>,
}));
vi.mock("@/composants/disposition/menu-commandes", () => ({
  MenuCommandes: () => <div>MenuCommandesMock</div>,
}));
vi.mock("@/composants/disposition/tour-onboarding", () => ({
  TourOnboarding: () => <div>TourOnboardingMock</div>,
}));
vi.mock("@/composants/disposition/fab-chat-ia", () => ({
  FabChatIA: () => <div>FabChatIAMock</div>,
}));
vi.mock("@/composants/disposition/fab-assistant-vocal", () => ({
  FabAssistantVocal: () => <div>FabAssistantVocalMock</div>,
}));
vi.mock("@/composants/disposition/fab-actions-rapides", () => ({
  FabActionsRapides: () => <div>FabActionsRapidesMock</div>,
}));
vi.mock("@/composants/disposition/minuteur-flottant", () => ({
  MinuteurFlottant: () => <div>MinuteurFlottantMock</div>,
}));
vi.mock("@/composants/disposition/barre-progression", () => ({
  BarreProgression: () => <div>BarreProgressionMock</div>,
}));
vi.mock("@/composants/disposition/contenu-principal", () => ({
  ContenuPrincipal: ({ children }: { children: React.ReactNode }) => <main>{children}</main>,
}));
vi.mock("@/composants/disposition/bandeau-suggestion-proactive", () => ({
  BandeauSuggestionProactive: () => <div>BandeauSuggestionProactiveMock</div>,
}));
vi.mock("@/composants/disposition/bandeau-hors-ligne", () => ({
  BandeauHorsLigne: () => <div>BandeauHorsLigneMock</div>,
}));
vi.mock("@/composants/disposition/panneau-admin-flottant", () => ({
  PanneauAdminFlottant: () => <div>PanneauAdminFlottantMock</div>,
}));
vi.mock("@/composants/pwa/install-prompt", () => ({
  InstallPrompt: () => <div>InstallPromptMock</div>,
}));

describe("CoquilleApp", () => {
  it("assemble les blocs de disposition et rend le contenu enfant", () => {
    render(
      <CoquilleApp>
        <div>Contenu principal test</div>
      </CoquilleApp>
    );

    expect(mockNotificationsJeux).toHaveBeenCalledTimes(1);
    expect(screen.getByText("BarreProgressionMock")).toBeInTheDocument();
    expect(screen.getByText("BarreLateraleMock")).toBeInTheDocument();
    expect(screen.getByText("EnTeteMock")).toBeInTheDocument();
    expect(screen.getByText("FilArianeMock")).toBeInTheDocument();
    expect(screen.getByText("BandeauSuggestionProactiveMock")).toBeInTheDocument();
    expect(screen.getByText("BandeauHorsLigneMock")).toBeInTheDocument();
    expect(screen.getByText("Contenu principal test")).toBeInTheDocument();
    expect(screen.getByText("NavMobileMock")).toBeInTheDocument();
    expect(screen.getByText("MenuCommandesMock")).toBeInTheDocument();
    expect(screen.getByText("FabChatIAMock")).toBeInTheDocument();
    expect(screen.getByText("FabAssistantVocalMock")).toBeInTheDocument();
    expect(screen.getByText("FabActionsRapidesMock")).toBeInTheDocument();
    expect(screen.getByText("MinuteurFlottantMock")).toBeInTheDocument();
    expect(screen.getByText("TourOnboardingMock")).toBeInTheDocument();
    expect(screen.getByText("PanneauAdminFlottantMock")).toBeInTheDocument();
    expect(screen.getByText("InstallPromptMock")).toBeInTheDocument();
  });
});
