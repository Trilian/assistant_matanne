import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// ─── Mocks ────────────────────────────────────────────────

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/cuisine/courses",
  redirect: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn(), info: vi.fn() },
}));

vi.mock("@/bibliotheque/api/courses", () => ({
  obtenirArticlesDrive: vi.fn().mockResolvedValue([]),
}));

vi.mock("@/bibliotheque/api/telegram", () => ({
  envoyerCoursesMagasinTelegram: vi.fn().mockResolvedValue({ ok: true }),
}));

const mockUtiliserPageCourses = {
  modeInvites: null,
  mettreAJourModeInvites: vi.fn(),
  reinitialiserModeInvites: vi.fn(),
  listeSelectionnee: 1,
  setListeSelectionnee: vi.fn(),
  nomNouvelleListe: "",
  setNomNouvelleListe: vi.fn(),
  dialogueArticle: false,
  setDialogueArticle: vi.fn(),
  scanneurOuvert: false,
  setScanneurOuvert: vi.fn(),
  panneauBio: false,
  setPanneauBio: vi.fn(),
  dialogueQr: false,
  setDialogueQr: vi.fn(),
  qrUrl: "",
  setQrUrl: vi.fn(),
  chargementQr: false,
  modeSelection: false,
  setModeSelection: vi.fn(),
  articlesSelectionnes: new Set<number>(),
  setArticlesSelectionnes: vi.fn(),
  inputAjoutRef: { current: null },
  listes: [{ id: 1, nom: "Ma liste", nb_articles: 3, statut: "en_cours" }],
  detailListe: { id: 1, nom: "Ma liste", articles: [] },
  bioLocal: [],
  recurrents: [],
  predictionsInvites: [],
  suggestionsInvites: [],
  chargementListes: false,
  chargementDetail: false,
  enCreationListe: false,
  enAjout: false,
  enEcoute: false,
  estSupporte: true,
  enCochageSelection: false,
  enSuppressionSelection: false,
  enValidation: false,
  enConfirmation: false,
  enCochageGlobal: false,
  enCochageCategorie: false,
  enFinalisationCourses: false,
  regArticle: vi.fn(),
  submitArticle: vi.fn(),
  erreursArticle: {},
  articles: [
    { id: 10, nom: "Tomates", quantite: 4, unite: "pièce", categorie: "Fruits et légumes", est_coche: false },
    { id: 11, nom: "Lait", quantite: 1, unite: "L", categorie: "Produits laitiers", est_coche: true },
  ],
  articlesNonCoches: [
    { id: 10, nom: "Tomates", quantite: 4, unite: "pièce", categorie: "Fruits et légumes", est_coche: false },
  ],
  ouvrirQrPartage: vi.fn(),
  telechargerQr: vi.fn(),
  creerListe: vi.fn(),
  ajouter: vi.fn(),
  cocher: vi.fn(),
  confirmer: vi.fn(),
  valider: vi.fn(),
  cocherTout: vi.fn(),
  cocherSelection: vi.fn(),
  supprimerSelection: vi.fn(),
  cocherCategorie: vi.fn(),
  finaliserCourses: vi.fn(),
  basculerSelectionArticle: vi.fn(),
  supprimerAvecUndo: vi.fn(),
  importerDepuisScanner: vi.fn(),
  demarrerEcoute: vi.fn(),
  arreterEcoute: vi.fn(),
};

vi.mock("@/crochets/utiliser-page-courses", () => ({
  utiliserPageCourses: () => mockUtiliserPageCourses,
}));

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockReturnValue({ data: [], isLoading: false }),
  utiliserMutation: vi.fn().mockReturnValue({ mutate: vi.fn(), isPending: false }),
  utiliserInvalidation: vi.fn().mockReturnValue(vi.fn()),
}));

// Mock des composants enfants complexes
vi.mock("@/composants/courses/dialogue-article-courses", () => ({
  DialogueArticleCourses: () => null,
}));
vi.mock("@/composants/courses/dialogue-qr-courses", () => ({
  DialogueQrCourses: () => null,
}));
vi.mock("@/composants/courses/filtre-magasins", () => ({
  FiltreMagasins: () => <div data-testid="filtre-magasins" />,
}));
vi.mock("@/composants/courses/panneau-bio-local", () => ({
  PanneauBioLocal: () => null,
}));
vi.mock("@/composants/courses/panneau-correspondances-drive", () => ({
  PanneauCorrespondancesDrive: () => null,
}));
vi.mock("@/composants/courses/panneau-detail-courses", () => ({
  PanneauDetailCourses: () => null,
}));
vi.mock("@/composants/courses/panneau-listes-courses", () => ({
  PanneauListesCourses: () => <div data-testid="panneau-listes" />,
}));
vi.mock("@/composants/cuisine/carte-mode-invites", () => ({
  CarteModeInvites: () => null,
}));
vi.mock("@/composants/scanneur-multi-codes", () => ({
  ScanneurMultiCodes: () => null,
}));

// ─── Helpers ──────────────────────────────────────────────

function renderCourses() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  // Lazy import pour que les mocks soient actifs
  const { default: PageCourses } = require("@/app/(app)/cuisine/courses/page");
  return render(
    <QueryClientProvider client={client}>
      <PageCourses />
    </QueryClientProvider>
  );
}

// ─── Tests ────────────────────────────────────────────────

describe("PageCourses", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("rend sans crash", () => {
    renderCourses();
    expect(document.body).toBeTruthy();
  });

  it("affiche les articles non cochés", async () => {
    renderCourses();
    await waitFor(() => {
      expect(screen.getByText("Tomates")).toBeInTheDocument();
    });
  });

  it("n'affiche pas d'erreur en état de chargement", () => {
    mockUtiliserPageCourses.chargementListes = true;
    mockUtiliserPageCourses.chargementDetail = true;
    renderCourses();
    // En chargement, pas de crash
    expect(document.body).toBeTruthy();
    // Reset
    mockUtiliserPageCourses.chargementListes = false;
    mockUtiliserPageCourses.chargementDetail = false;
  });

  it("gère l'état sans liste sélectionnée", () => {
    mockUtiliserPageCourses.listeSelectionnee = null;
    renderCourses();
    expect(document.body).toBeTruthy();
    mockUtiliserPageCourses.listeSelectionnee = 1;
  });
});
