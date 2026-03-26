import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import OCRTicketJeuxPage from "@/app/(app)/jeux/ocr-ticket/page";

const mockAnalyserTicketJeuxOCR = vi.fn();

vi.mock("@/bibliotheque/api/jeux", () => ({
  analyserTicketJeuxOCR: (file: File) => mockAnalyserTicketJeuxOCR(file),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("OCRTicketJeuxPage", () => {
  it("affiche des CTA de pré-remplissage après OCR", async () => {
    mockAnalyserTicketJeuxOCR.mockResolvedValueOnce({
      success: true,
      message: "ok",
      donnees: {
        point_vente: "FDJ Kiosk",
        date_achat: "2026-03-26",
        total: 10,
        mode_paiement: "CB",
        lignes: [
          { description: "Euromillions 1 2 3 4 5 etoiles 1 2", quantite: 1, prix_unitaire: null, prix_total: 5 },
          { description: "PARI 1N2 PSG @ 1.85", quantite: 1, prix_unitaire: null, prix_total: 5 },
          { description: "GRILLE 7 11 22 33 44", quantite: 1, prix_unitaire: null, prix_total: 2 },
        ],
      },
    });

    render(<OCRTicketJeuxPage />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["dummy"], "ticket.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Résultat OCR/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Grilles détectées et pré-remplissage/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Pré-remplir Euromillions/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Créer un pari pré-rempli/i })).toBeInTheDocument();
  });

  it("filtre les grilles par confiance OCR", async () => {
    mockAnalyserTicketJeuxOCR.mockResolvedValueOnce({
      success: true,
      message: "ok",
      donnees: {
        point_vente: "FDJ",
        date_achat: "2026-03-26",
        total: 7,
        mode_paiement: "CB",
        lignes: [
          { description: "Euromillions 1 2 3 4 5 etoiles 1 2", quantite: 1, prix_unitaire: null, prix_total: 5 },
          { description: "7 11 22 33 44", quantite: 1, prix_unitaire: null, prix_total: 2 },
        ],
      },
    });

    render(<OCRTicketJeuxPage />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["dummy"], "ticket2.png", { type: "image/png" });
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/Filtre confiance OCR/i)).toBeInTheDocument();
    });

    const slider = document.querySelector('input[type="range"]') as HTMLInputElement;
    fireEvent.change(slider, { target: { value: "95" } });

    await waitFor(() => {
      expect(screen.getByText(/1 \/ 2 grilles proposées/i)).toBeInTheDocument();
    });
  });
});
