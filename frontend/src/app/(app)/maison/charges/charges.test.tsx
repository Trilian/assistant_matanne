import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import PageCharges from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/maison/charges",
}));

const mockCharges = [
  { id: 1, type: "Électricité", montant: 120, mois: "2025-01" },
  { id: 2, type: "Internet", montant: 35, mois: "2025-01" },
  { id: 3, type: "Électricité", montant: 130, mois: "2025-02" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockCharges, isLoading: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  listerCharges: vi.fn(),
}));

describe("PageCharges", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Charges", () => {
    render(<PageCharges />);
    expect(screen.getByText(/Charges/)).toBeInTheDocument();
  });

  it("affiche la description", () => {
    render(<PageCharges />);
    expect(screen.getByText(/Factures, abonnements/)).toBeInTheDocument();
  });
});
