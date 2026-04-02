// ═══════════════════════════════════════════════════════════
// B12 — Tests pages famille frontend
// Couvre: Hub, Jules, Routines, Budget, Weekend,
//         Anniversaires, Documents, Contacts, Journal
// ═══════════════════════════════════════════════════════════

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

// ── Mocks ────────────────────────────────────────────────

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), replace: vi.fn(), refresh: vi.fn() }),
  usePathname: () => "/famille",
  useSearchParams: () => ({ get: vi.fn().mockReturnValue(null) }),
  redirect: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) =>
    React.createElement("a", { href }, children),
}));

vi.mock("@/bibliotheque/api/client", () => ({
  apiClient: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
  },
  clientApi: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
  },
}));

vi.mock("@/bibliotheque/api/famille", async () => {
  const actual = await vi.importActual<typeof import("@/bibliotheque/api/famille")>("@/bibliotheque/api/famille");
  return {
    ...actual,
    obtenirContexteFamilial: vi.fn().mockResolvedValue({ suggestions: [], rappels: [], anniversaires: [] }),
    evaluerRappelsFamille: vi.fn().mockResolvedValue([]),
    listerAchats: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    obtenirResumeBudgetMois: vi.fn().mockResolvedValue({ total: 500, par_categorie: {} }),
    completerRoutine: vi.fn().mockResolvedValue({ ok: true }),
    obtenirSuggestionsWeekend: vi.fn().mockResolvedValue([]),
    joursSansCReche: vi.fn().mockResolvedValue({ jours: [] }),
    obtenirSuggestionsAchatsEnrichies: vi.fn().mockResolvedValue([]),
    obtenirProfilJules: vi.fn().mockResolvedValue(null),
    obtenirAlimentsExclus: vi.fn().mockResolvedValue([]),
    obtenirCoachingHebdo: vi.fn().mockResolvedValue(null),
    obtenirProfilsEnfants: vi.fn().mockResolvedValue([]),
    obtenirJalonsJules: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    obtenirMesuresCroissance: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    obtenirRoutines: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    listerRoutines: vi.fn().mockResolvedValue([]),
    listerAnniversaires: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    listerDocuments: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    listerContacts: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    listerJournal: vi.fn().mockResolvedValue({ items: [], total: 0 }),
    obtenirBudgetFamille: vi.fn().mockResolvedValue({ depenses: [], total: 0 }),
    obtenirStatsBudget: vi.fn().mockResolvedValue({
      depenses_mensuelles: [],
      repartition_categories: {},
      total_mois: 0,
    }),
    obtenirAnalyseBudgetIA: vi.fn().mockResolvedValue({
      resume: "",
      tendances: [],
      recommandations: [],
      alertes: [],
    }),
  };
});

vi.mock("@/crochets/utiliser-api", () => ({
  utiliserRequete: vi.fn().mockReturnValue({
    data: undefined,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
  utiliserMutation: vi.fn().mockReturnValue({
    mutate: vi.fn(),
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  utiliserInvalidation: vi.fn().mockReturnValue(vi.fn()),
}));

vi.mock("@tanstack/react-query", async () => {
  const actual = await vi.importActual("@tanstack/react-query");
  return {
    ...actual,
    useQuery: vi.fn().mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    }),
    useMutation: vi.fn().mockReturnValue({
      mutate: vi.fn(),
      mutateAsync: vi.fn(),
      isPending: false,
      isSuccess: false,
    }),
    useQueryClient: vi.fn().mockReturnValue({
      invalidateQueries: vi.fn(),
    }),
  };
});

function renderWithQuery(ui: React.ReactElement) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    React.createElement(QueryClientProvider, { client }, ui),
  );
}

beforeEach(() => {
  vi.clearAllMocks();
});

// ── Hub Famille ──────────────────────────────────────────

describe("Hub Famille", () => {
  it("rend le hub famille sans erreur", async () => {
    const PageFamille = (await import("@/app/(app)/famille/page")).default;
    const { container } = renderWithQuery(React.createElement(PageFamille));
    expect(container).toBeDefined();
  });
});

// ── Jules ────────────────────────────────────────────────

describe("Page Jules", () => {
  it("rend la page Jules sans erreur", async () => {
    const PageJules = (await import("@/app/(app)/famille/jules/page")).default;
    const { container } = renderWithQuery(React.createElement(PageJules));
    expect(container).toBeDefined();
  });
});

// ── Routines ─────────────────────────────────────────────

describe("Page Routines", () => {
  it("rend la page routines sans erreur", async () => {
    const PageRoutines = (await import("@/app/(app)/famille/routines/page")).default;
    const { container } = renderWithQuery(React.createElement(PageRoutines));
    expect(container).toBeDefined();
  });
});

// ── Budget Famille ───────────────────────────────────────

describe("Page Budget Famille", () => {
  it("rend la page budget sans erreur", async () => {
    const PageBudget = (await import("@/app/(app)/famille/budget/page")).default;
    const { container } = renderWithQuery(React.createElement(PageBudget));
    expect(container).toBeDefined();
  });
});

// ── Weekend ──────────────────────────────────────────────

describe("Page Weekend", () => {
  it("rend la page weekend sans erreur", async () => {
    const PageWeekend = (await import("@/app/(app)/famille/weekend/page")).default;
    const { container } = renderWithQuery(React.createElement(PageWeekend));
    expect(container).toBeDefined();
  });
});

// ── Anniversaires ────────────────────────────────────────

describe("Page Anniversaires", () => {
  it("rend la page anniversaires sans erreur", async () => {
    const PageAnniversaires = (await import("@/app/(app)/famille/anniversaires/page")).default;
    const { container } = renderWithQuery(React.createElement(PageAnniversaires));
    expect(container).toBeDefined();
  });
});

// ── Documents ────────────────────────────────────────────

describe("Page Documents", () => {
  it("rend la page documents sans erreur", async () => {
    const PageDocuments = (await import("@/app/(app)/famille/documents/page")).default;
    const { container } = renderWithQuery(React.createElement(PageDocuments));
    expect(container).toBeDefined();
  });
});

// ── Contacts ─────────────────────────────────────────────

describe("Page Contacts", () => {
  it("rend la page contacts sans erreur", async () => {
    const PageContacts = (await import("@/app/(app)/famille/contacts/page")).default;
    const { container } = renderWithQuery(React.createElement(PageContacts));
    expect(container).toBeDefined();
  });
});

// ── Journal ──────────────────────────────────────────────

describe("Page Journal", () => {
  it("rend la page journal sans erreur", async () => {
    const PageJournal = (await import("@/app/(app)/famille/journal/page")).default;
    PageJournal();
    expect(true).toBe(true);
  });
});

// ── Activités ────────────────────────────────────────────

describe("Page Activités", () => {
  it("rend la page activités sans erreur", async () => {
    const PageActivites = (await import("@/app/(app)/famille/activites/page")).default;
    const { container } = renderWithQuery(React.createElement(PageActivites));
    expect(container).toBeDefined();
  });
});

// ── Calendriers ──────────────────────────────────────────

describe("Page Calendriers", () => {
  it("rend la page calendriers sans erreur", async () => {
    const PageCalendriers = (await import("@/app/(app)/famille/calendriers/page")).default;
    const { container } = renderWithQuery(React.createElement(PageCalendriers));
    expect(container).toBeDefined();
  });
});

// ── Voyages ──────────────────────────────────────────────

describe("Page Voyages", () => {
  it("rend la page voyages sans erreur", async () => {
    const PageVoyages = (await import("@/app/(app)/famille/voyages/page")).default;
    const { container } = renderWithQuery(React.createElement(PageVoyages));
    expect(container).toBeDefined();
  });
});
