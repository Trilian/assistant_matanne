import { describe, it, expect, vi, beforeEach } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PageEquipements from "./page";

vi.mock("next/navigation", () => ({
  useSearchParams: () => ({ get: () => "inventaire" }),
  useRouter: () => ({ replace: vi.fn() }),
}));

vi.mock("@/composants/maison/bandeau-ia", () => ({
  BandeauIA: () => <div data-testid="bandeau-ia" />,
}));

vi.mock("@/composants/bouton-achat", () => ({
  BoutonAchat: () => <button type="button">Acheter</button>,
}));

const mockInventaire = {
  pieces: [
    {
      piece: "Cuisine",
      objets: [
        {
          id: 1,
          nom: "Lave-vaisselle",
          categorie: "electromenager",
          statut: "fonctionne",
          sous_garantie: true,
          duree_garantie_mois: 24,
        },
      ],
    },
  ],
  total: 1,
};

let mockDocumentsGarantie = {
  ok: true,
  nb_documents: 1,
  documents: [
    {
      id: 7,
      titre: "Facture lave-vaisselle",
      categorie: "administratif",
      fichier_url: "/uploads/facture-lv.pdf",
      tags: ["garantie", "equipement:1"],
    },
  ],
};

const mockDocumentsDisponibles = {
  items: [
    {
      id: 9,
      titre: "Facture SAV Bosch",
      categorie: "administratif",
      tags: [],
      actif: true,
      est_expire: false,
    },
    {
      id: 10,
      titre: "Bon de livraison cuisine",
      categorie: "administratif",
      tags: [],
      actif: true,
      est_expire: false,
    },
  ],
  total: 2,
};

const mutateMock = vi.fn();

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn((cle: string[]) => {
    if (cle[0] === "maison" && cle[1] === "inventaire") {
      return { data: mockInventaire, isLoading: false };
    }
    if (cle[0] === "maison" && cle[1] === "renouvellement") {
      return { data: { suggestions: [], total: 0 }, isLoading: false };
    }
    if (cle[0] === "maison" && cle[1] === "routines") {
      return { data: [], isLoading: false };
    }
    if (cle[0] === "documents" && cle[1] === "garantie") {
      return { data: mockDocumentsGarantie, isLoading: false };
    }
    if (cle[0] === "documents" && cle[1] === "liste") {
      return { data: mockDocumentsDisponibles, isLoading: false };
    }
    return { data: undefined, isLoading: false };
  }),
  utiliserMutation: () => ({ mutate: mutateMock, isPending: false }),
}));

vi.mock("@/bibliotheque/api/maison", () => ({
  obtenirAstucesDomotique: vi.fn(),
  obtenirPiecesAvecObjets: vi.fn(),
  obtenirSuggestionsRenouvellement: vi.fn(),
  listerToutesLesTachesRoutines: vi.fn(),
  associerRoutineObjet: vi.fn(),
}));

vi.mock("@/bibliotheque/api/documents", () => ({
  obtenirDocumentsGarantieObjet: vi.fn((objetId: number) =>
    Promise.resolve({ ...mockDocumentsGarantie, objet: { id: objetId, nom: "Lave-vaisselle" } })
  ),
  listerDocuments: vi.fn(() => Promise.resolve(mockDocumentsDisponibles)),
  lierDocumentGarantie: vi.fn(),
}));

function renderWithQuery(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={qc}>{ui}</QueryClientProvider>);
}

describe("PageEquipements", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mutateMock.mockClear();
    mockDocumentsGarantie = {
      ok: true,
      nb_documents: 1,
      documents: [
        {
          id: 7,
          titre: "Facture lave-vaisselle",
          categorie: "administratif",
          fichier_url: "/uploads/facture-lv.pdf",
          tags: ["garantie", "equipement:1"],
        },
      ],
    };
  });

  it("affiche les documents de garantie liés à un équipement", () => {
    renderWithQuery(<PageEquipements />);

    expect(screen.getByText("Lave-vaisselle")).toBeInTheDocument();
    expect(screen.getByText(/Facture lave-vaisselle/i)).toBeInTheDocument();
  });

  it("propose de lier une facture quand aucun document n'est associé", () => {
    mockDocumentsGarantie = { ok: true, nb_documents: 0, documents: [] };
    renderWithQuery(<PageEquipements />);

    expect(screen.getByText(/Lier une facture/i)).toBeInTheDocument();
  });

  it("permet de choisir un document existant depuis la fiche équipement", () => {
    renderWithQuery(<PageEquipements />);

    fireEvent.click(screen.getByRole("button", { name: /lier un document existant/i }));
    fireEvent.click(screen.getByRole("button", { name: /Facture SAV Bosch/i }));

    expect(mutateMock).toHaveBeenCalledWith({ documentId: 9, objetId: 1 });
  });
});
