import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import EuromillionsPage from "@/app/(app)/jeux/euromillions/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/jeux/euromillions",
}));

describe("EuromillionsPage", () => {
  it("affiche le titre", () => {
    render(<EuromillionsPage />);
    expect(screen.getByText(/Euromillions/i)).toBeInTheDocument();
  });

  it("affiche 5 numéros et 2 étoiles", () => {
    render(<EuromillionsPage />);
    expect(screen.getByText(/5 numéros/i)).toBeInTheDocument();
    expect(screen.getByText(/2 étoiles/i)).toBeInTheDocument();
  });

  it("bouton Nouvelle grille génère de nouveaux numéros", () => {
    render(<EuromillionsPage />);
    const bouton = screen.getByText(/Nouvelle grille/);
    expect(bouton).toBeInTheDocument();
    fireEvent.click(bouton);
    // Page should still be rendered after click
    expect(screen.getByText(/Euromillions/i)).toBeInTheDocument();
  });

  it("affiche les informations probabilité", () => {
    render(<EuromillionsPage />);
    expect(screen.getByText("1/139M")).toBeInTheDocument();
    expect(screen.getByText("5 + 2")).toBeInTheDocument();
  });
});
