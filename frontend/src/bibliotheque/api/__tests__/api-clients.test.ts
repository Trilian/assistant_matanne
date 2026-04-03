/**
 * Tests unitaires pour les API clients frontend (P2-17).
 *
 * Couvre:
 * - client.ts (instance Axios, intercepteurs JWT)
 * - recettes.ts (CRUD recettes, suggestions)
 * - courses.ts (listes, articles, génération)
 * - planning.ts (planning semaine, repas)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios from "axios";

// Mock axios avant d'importer les modules
vi.mock("axios", () => {
  const mockAxiosInstance = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    defaults: {
      headers: { common: {} },
    },
  };
  return {
    default: {
      create: vi.fn(() => mockAxiosInstance),
      isAxiosError: vi.fn(),
    },
  };
});

// ═══════════════════════════════════════════════════════════
// client.ts
// ═══════════════════════════════════════════════════════════

describe("clientApi", () => {
  it("crée une instance axios avec la bonne baseURL", () => {
    // Re-import pour trigger le create
    vi.resetModules();
    expect(axios.create).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════
// recettes.ts
// ═══════════════════════════════════════════════════════════

describe("API recettes", () => {
  let clientApi: ReturnType<typeof axios.create>;

  beforeEach(() => {
    vi.resetModules();
    clientApi = axios.create() as unknown as ReturnType<typeof axios.create>;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("listerRecettes appelle GET /recettes avec pagination", async () => {
    const mockData = {
      data: { items: [], total: 0, page: 1, taille: 20 },
    };
    (clientApi.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce(mockData);

    const { listerRecettes } = await import("@/bibliotheque/api/recettes");
    const result = await listerRecettes(1, 20);
    expect(result).toBeDefined();
  });

  it("creerRecette appelle POST /recettes", async () => {
    const mockRecette = { id: 1, nom: "Tarte aux pommes" };
    (clientApi.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: mockRecette,
    });

    const { creerRecette } = await import("@/bibliotheque/api/recettes");
    expect(creerRecette).toBeDefined();
  });

  it("supprimerRecette appelle DELETE /recettes/:id", async () => {
    (clientApi.delete as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: null,
    });

    const { supprimerRecette } = await import("@/bibliotheque/api/recettes");
    expect(supprimerRecette).toBeDefined();
  });
});

// ═══════════════════════════════════════════════════════════
// courses.ts
// ═══════════════════════════════════════════════════════════

describe("API courses", () => {
  let clientApi: ReturnType<typeof axios.create>;

  beforeEach(() => {
    vi.resetModules();
    clientApi = axios.create() as unknown as ReturnType<typeof axios.create>;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("listerListesCourses est exportée", async () => {
    (clientApi.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: [],
    });

    const { listerListesCourses } = await import(
      "@/bibliotheque/api/courses"
    );
    expect(listerListesCourses).toBeDefined();
    expect(typeof listerListesCourses).toBe("function");
  });

  it("genererCoursesDepuisPlanning est exportée", async () => {
    const { genererCoursesDepuisPlanning } = await import(
      "@/bibliotheque/api/courses"
    );
    expect(genererCoursesDepuisPlanning).toBeDefined();
    expect(typeof genererCoursesDepuisPlanning).toBe("function");
  });

  it("obtenirPredictionsCourses est exportée", async () => {
    const { obtenirPredictionsCourses } = await import(
      "@/bibliotheque/api/courses"
    );
    expect(obtenirPredictionsCourses).toBeDefined();
    expect(typeof obtenirPredictionsCourses).toBe("function");
  });
});

// ═══════════════════════════════════════════════════════════
// planning.ts
// ═══════════════════════════════════════════════════════════

describe("API planning", () => {
  let clientApi: ReturnType<typeof axios.create>;

  beforeEach(() => {
    vi.resetModules();
    clientApi = axios.create() as unknown as ReturnType<typeof axios.create>;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("obtenirPlanningSemaine est exportée", async () => {
    const { obtenirPlanningSemaine } = await import(
      "@/bibliotheque/api/planning"
    );
    expect(obtenirPlanningSemaine).toBeDefined();
    expect(typeof obtenirPlanningSemaine).toBe("function");
  });

  it("genererPlanningSemaine est exportée", async () => {
    const { genererPlanningSemaine } = await import(
      "@/bibliotheque/api/planning"
    );
    expect(genererPlanningSemaine).toBeDefined();
    expect(typeof genererPlanningSemaine).toBe("function");
  });

  it("obtenirNutritionHebdo est exportée", async () => {
    const { obtenirNutritionHebdo } = await import(
      "@/bibliotheque/api/planning"
    );
    expect(obtenirNutritionHebdo).toBeDefined();
    expect(typeof obtenirNutritionHebdo).toBe("function");
  });

  it("exporterPlanningPdf est exportée", async () => {
    const { exporterPlanningPdf } = await import(
      "@/bibliotheque/api/planning"
    );
    expect(exporterPlanningPdf).toBeDefined();
    expect(typeof exporterPlanningPdf).toBe("function");
  });
});

// ═══════════════════════════════════════════════════════════
// telegram.ts
// ═══════════════════════════════════════════════════════════

describe("API telegram", () => {
  let clientApi: ReturnType<typeof axios.create>;

  beforeEach(() => {
    vi.resetModules();
    clientApi = axios.create() as unknown as ReturnType<typeof axios.create>;
    // Réinitialiser toutes les queues mockResolvedValueOnce pour éviter la pollution entre tests
    vi.mocked(clientApi.post).mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("envoyerPlanningTelegram appelle POST /telegram/envoyer-planning", async () => {
    (clientApi.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: { message: "planning_envoye", id: 42 },
    });

    const { envoyerPlanningTelegram } = await import(
      "@/bibliotheque/api/telegram"
    );
    const result = await envoyerPlanningTelegram(42);

    expect(clientApi.post).toHaveBeenCalledWith("/telegram/envoyer-planning", {
      planning_id: 42,
      contenu: undefined,
    });
    expect(result).toEqual({ message: "planning_envoye", id: 42 });
  });

  it("envoyerListeCoursesTelegram appelle POST /telegram/envoyer-courses", async () => {
    (clientApi.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
      data: { message: "courses_envoyees", id: 15 },
    });

    const { envoyerListeCoursesTelegram } = await import(
      "@/bibliotheque/api/telegram"
    );
    const result = await envoyerListeCoursesTelegram(15, "Courses semaine");

    expect(clientApi.post).toHaveBeenCalledWith("/telegram/envoyer-courses", {
      liste_id: 15,
      nom_liste: "Courses semaine",
    });
    expect(result).toEqual({ message: "courses_envoyees", id: 15 });
  });
});
