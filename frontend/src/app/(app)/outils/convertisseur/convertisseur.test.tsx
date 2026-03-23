import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ConvertisseurPage from "@/app/(app)/outils/convertisseur/page";

// Mock Next.js modules
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils/convertisseur",
}));

describe("ConvertisseurPage", () => {
  it("affiche le titre", () => {
    render(<ConvertisseurPage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Convertisseur/i);
  });

  it("affiche les 4 onglets", () => {
    render(<ConvertisseurPage />);
    expect(screen.getByText("Masse")).toBeInTheDocument();
    expect(screen.getByText("Volume")).toBeInTheDocument();
    expect(screen.getByText("Longueur")).toBeInTheDocument();
    expect(screen.getByText("Temp.")).toBeInTheDocument();
  });

  it("affiche un champ Valeur et un champ Résultat", () => {
    render(<ConvertisseurPage />);
    expect(screen.getByText("Valeur")).toBeInTheDocument();
    expect(screen.getByText("Résultat")).toBeInTheDocument();
  });

  it("change d'onglet vers Volume", () => {
    render(<ConvertisseurPage />);
    fireEvent.click(screen.getByText("Volume"));
    // Should still render value/result fields
    expect(screen.getByText("Valeur")).toBeInTheDocument();
  });
});
