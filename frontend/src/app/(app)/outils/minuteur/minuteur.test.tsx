import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import MinuteurPage from "@/app/(app)/outils/minuteur/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/outils/minuteur",
  useSearchParams: () => ({ get: vi.fn().mockReturnValue(null) }),
}));

describe("MinuteurPage", () => {
  it("affiche le titre", () => {
    render(<MinuteurPage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(/Minuteur/i);
  });

  it("affiche les onglets Minuteur et Chronomètre", () => {
    render(<MinuteurPage />);
    expect(screen.getByRole("tab", { name: /minuteur/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /chronomètre/i })).toBeInTheDocument();
  });

  it("affiche les presets de durée", () => {
    render(<MinuteurPage />);
    expect(screen.getByText("1 min")).toBeInTheDocument();
    expect(screen.getByText("5 min")).toBeInTheDocument();
    expect(screen.getByText("10 min")).toBeInTheDocument();
    expect(screen.getByText("30 min")).toBeInTheDocument();
  });

  it("affiche le bouton Démarrer", () => {
    render(<MinuteurPage />);
    expect(screen.getByText(/Démarrer/)).toBeInTheDocument();
  });

  it("changement vers onglet chronomètre", () => {
    render(<MinuteurPage />);
    fireEvent.click(screen.getByRole("tab", { name: /chronomètre/i }));
    // Chronometre also has a Démarrer button
    expect(screen.getByText(/Démarrer/)).toBeInTheDocument();
  });
});
