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
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/outils", () => ({
  obtenirSuggestionsRecettes: vi.fn(),
}));

vi.mock("@/components/ui/scroll-area", () => ({
  ScrollArea: React.forwardRef(({ children, className }: { children: React.ReactNode; className?: string }, ref: React.Ref<HTMLDivElement>) => {
    const internalRef = React.useRef<HTMLDivElement>(null);
    React.useImperativeHandle(ref, () => {
      const el = internalRef.current!;
      if (el && !el.scrollTo) el.scrollTo = vi.fn();
      return el;
    });
    return <div ref={internalRef} className={className}>{children}</div>;
  }),
}));

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
    expect(screen.getByText(/suggestions de recettes/)).toBeInTheDocument();
  });

  it("affiche le champ de saisie", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByPlaceholderText(/poulet/)).toBeInTheDocument();
  });

  it("affiche le bouton Envoyer", () => {
    renderWithQuery(<ChatIAPage />);
    expect(screen.getByText("Envoyer")).toBeInTheDocument();
  });
});
