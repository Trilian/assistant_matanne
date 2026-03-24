import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageContacts from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/contacts",
}));

const mockContacts = [
  { id: 1, nom: "Dr Martin", telephone: "0612345678", email: "martin@med.fr", categorie: "sante", adresse: "Paris", favori: true },
  { id: 2, nom: "Crèche Soleil", telephone: "0198765432", email: "contact@creche.fr", categorie: "garde", adresse: "Lyon", favori: false },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockContacts, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: () => vi.fn(),
}));

vi.mock("@/bibliotheque/api/utilitaires", () => ({
  listerContacts: vi.fn(),
  creerContact: vi.fn(),
  modifierContact: vi.fn(),
  supprimerContact: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageContacts", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre", () => {
    renderWithQuery(<PageContacts />);
    expect(screen.getByText(/Contacts/)).toBeInTheDocument();
  });

  it("affiche les contacts", () => {
    renderWithQuery(<PageContacts />);
    expect(screen.getByText("Dr Martin")).toBeInTheDocument();
    expect(screen.getByText("Crèche Soleil")).toBeInTheDocument();
  });

  it("affiche le bouton ajouter", () => {
    renderWithQuery(<PageContacts />);
    expect(screen.getByText("Ajouter")).toBeInTheDocument();
  });

  it("affiche les catégories de filtre", () => {
    renderWithQuery(<PageContacts />);
    expect(screen.getByText("Tous")).toBeInTheDocument();
  });
});
