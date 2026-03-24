import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import PageAlbum from "./page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/famille/album",
}));

const mockPhotos = [
  { id: 1, url: "/photos/1.jpg", nom: "Plage été", taille: 2048000, date_upload: "2025-01-01" },
  { id: 2, url: "/photos/2.jpg", nom: "Noël", taille: 1024000, date_upload: "2024-12-25" },
];

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: () => ({ data: mockPhotos, isLoading: false }),
  utiliserMutation: () => ({ mutate: vi.fn(), isPending: false }),
}));

vi.mock("@/bibliotheque/api/album", () => ({
  listerPhotos: vi.fn(),
  uploaderPhoto: vi.fn(),
  supprimerPhoto: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageAlbum", () => {
  beforeEach(() => vi.clearAllMocks());

  it("affiche le titre Album", () => {
    renderWithQuery(<PageAlbum />);
    expect(screen.getByText(/Album/)).toBeInTheDocument();
  });

  it("affiche le nombre de photos", () => {
    renderWithQuery(<PageAlbum />);
    expect(screen.getByText(/2 photos/)).toBeInTheDocument();
  });
});
