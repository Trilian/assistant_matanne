import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ChatIAPage from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils/chat-ia",
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: null, isLoading: false, error: null }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/outils", () => ({
  obtenirSuggestionsRecettes: vi.fn(),
}));

vi.mock("@/composants/ui/scroll-area", () => {
  const ScrollArea = React.forwardRef<HTMLDivElement, { children: React.ReactNode; className?: string }>(
    ({ children, className }, ref) => {
      const internalRef = React.useRef<HTMLDivElement>(null);
      React.useImperativeHandle(ref, () => {
        const el = internalRef.current!;
        if (el && !el.scrollTo) el.scrollTo = vi.fn();
        return el;
      });
      return <div ref={internalRef} className={className}>{children}</div>;
    }
  );
  ScrollArea.displayName = "ScrollArea";
  return { ScrollArea };
});

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("ChatIAPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByText(/Chat IA/)).toBeInTheDocument();
  });

  it("affiche le message d'accueil", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByText(/Assistant multi-contexte/)).toBeInTheDocument();
  });

  it("affiche le champ de saisie", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByPlaceholderText(/Posez votre question/)).toBeInTheDocument();
  });

  it("affiche le bouton Envoyer", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByRole("button", { name: /Envoyer le message/ })).toBeInTheDocument();
  });
});
