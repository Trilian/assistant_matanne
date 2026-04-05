// Tests API famille — Jules, activités, routines, budget, anniversaires, achats

import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("@/bibliotheque/api/client", () => ({
  clientApi: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import { clientApi } from "@/bibliotheque/api/client";
import {
  obtenirProfilJules,
  listerJalons,
  ajouterJalon,
  supprimerJalon,
  listerActivites,
  creerActivite,
  modifierActivite,
  supprimerActivite,
  listerRoutines,
  creerRoutine,
  supprimerRoutine,
  listerDepenses,
  obtenirStatsBudget,
  ajouterDepense,
  supprimerDepense,
  listerAnniversaires,
  creerAnniversaire,
  supprimerAnniversaire,
  listerAchats,
  creerAchat,
  supprimerAchat,
  completerRoutine,
  lireConfigGarde,
  joursSansCReche,
} from "@/bibliotheque/api/famille";

const api = vi.mocked(clientApi);

beforeEach(() => vi.clearAllMocks());

// ─── Jules ────────────────────────────────────────────────

describe("obtenirProfilJules", () => {
  it("appelle GET /famille/enfants et retourne le premier", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, prenom: "Jules" }] } });
    const result = await obtenirProfilJules();
    expect(api.get).toHaveBeenCalledWith("/famille/enfants");
    expect(result.prenom).toBe("Jules");
  });
});

describe("listerJalons", () => {
  it("appelle GET /famille/enfants/1/jalons", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, titre: "Premier pas" }] } });
    const result = await listerJalons();
    expect(api.get).toHaveBeenCalledWith("/famille/enfants/1/jalons", { params: {} });
    expect(result).toHaveLength(1);
  });

  it("filtre par catégorie", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [] } });
    await listerJalons("motricite");
    expect(api.get).toHaveBeenCalledWith("/famille/enfants/1/jalons", { params: { categorie: "motricite" } });
  });
});

describe("ajouterJalon", () => {
  it("appelle POST /famille/jules/jalons", async () => {
    const jalon = { titre: "Marche", date_jalon: "2024-06-01" };
    api.post.mockResolvedValueOnce({ data: { id: 5, ...jalon } });
    const result = await ajouterJalon(jalon as never);
    expect(api.post).toHaveBeenCalledWith("/famille/enfants/1/jalons", jalon);
    expect(result.id).toBe(5);
  });
});

describe("supprimerJalon", () => {
  it("appelle DELETE", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerJalon(3);
    expect(api.delete).toHaveBeenCalledWith("/famille/enfants/1/jalons/3");
  });
});

// ─── Activités ────────────────────────────────────────────

describe("listerActivites", () => {
  it("appelle GET /famille/activites", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, nom: "Parc" }] } });
    const result = await listerActivites();
    expect(api.get).toHaveBeenCalledWith("/famille/activites", { params: {} });
    expect(result).toHaveLength(1);
  });
});

describe("creerActivite", () => {
  it("appelle POST /famille/activites", async () => {
    const act = { nom: "Piscine", type: "sport" };
    api.post.mockResolvedValueOnce({ data: { id: 2, ...act } });
    const result = await creerActivite(act as never);
    expect(api.post).toHaveBeenCalledWith("/famille/activites", act);
    expect(result.id).toBe(2);
  });
});

describe("modifierActivite", () => {
  it("appelle PATCH /famille/activites/:id", async () => {
    api.patch.mockResolvedValueOnce({ data: { id: 2, nom: "Piscine couverte" } });
    await modifierActivite(2, { nom: "Piscine couverte" } as never);
    expect(api.patch).toHaveBeenCalledWith("/famille/activites/2", { nom: "Piscine couverte" });
  });
});

describe("supprimerActivite", () => {
  it("appelle DELETE /famille/activites/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerActivite(4);
    expect(api.delete).toHaveBeenCalledWith("/famille/activites/4");
  });
});

// ─── Routines ─────────────────────────────────────────────

describe("listerRoutines", () => {
  it("appelle GET /famille/routines", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, nom: "Matin" }] } });
    const result = await listerRoutines();
    expect(api.get).toHaveBeenCalledWith("/famille/routines");
    expect(result).toHaveLength(1);
  });
});

describe("creerRoutine", () => {
  it("appelle POST /famille/routines", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 3, nom: "Soir" } });
    const result = await creerRoutine({ nom: "Soir" } as never);
    expect(api.post).toHaveBeenCalledWith("/famille/routines", { nom: "Soir" });
    expect(result.id).toBe(3);
  });
});

describe("supprimerRoutine", () => {
  it("appelle DELETE /famille/routines/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerRoutine(3);
    expect(api.delete).toHaveBeenCalledWith("/famille/routines/3");
  });
});

describe("completerRoutine", () => {
  it("appelle PATCH /famille/routines/:id/completer", async () => {
    api.patch.mockResolvedValueOnce({ data: { id: 1, nom: "Matin", derniere_completion: "2024-06-10" } });
    const result = await completerRoutine(1);
    expect(api.patch).toHaveBeenCalledWith("/famille/routines/1/completer");
    expect(result.id).toBe(1);
  });
});

// ─── Budget ───────────────────────────────────────────────

describe("listerDepenses", () => {
  it("appelle GET /famille/budget", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, montant: 50 }] } });
    const result = await listerDepenses();
    expect(result).toHaveLength(1);
  });
});

describe("obtenirStatsBudget", () => {
  it("appelle GET /famille/budget/stats", async () => {
    api.get.mockResolvedValueOnce({ data: { total: 500, par_categorie: {} } });
    const result = await obtenirStatsBudget();
    expect(result.total).toBe(500);
  });
});

describe("ajouterDepense", () => {
  it("appelle POST /famille/budget", async () => {
    const dep = { montant: 42, categorie: "courses" };
    api.post.mockResolvedValueOnce({ data: { id: 10, ...dep } });
    const result = await ajouterDepense(dep as never);
    expect(api.post).toHaveBeenCalledWith("/famille/budget", dep);
    expect(result.id).toBe(10);
  });
});

describe("supprimerDepense", () => {
  it("appelle DELETE", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerDepense(10);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Anniversaires ────────────────────────────────────────

describe("listerAnniversaires", () => {
  it("appelle GET /famille/anniversaires", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, nom_personne: "Maman" }] } });
    const result = await listerAnniversaires();
    expect(result).toHaveLength(1);
  });
});

describe("creerAnniversaire", () => {
  it("appelle POST /famille/anniversaires", async () => {
    const anniv = { nom_personne: "Papa", date_naissance: "1990-01-01", relation: "pere", rappel_jours_avant: [7] };
    api.post.mockResolvedValueOnce({ data: { id: 2, ...anniv } });
    const result = await creerAnniversaire(anniv as never);
    expect(result.id).toBe(2);
  });
});

describe("supprimerAnniversaire", () => {
  it("appelle DELETE /famille/anniversaires/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerAnniversaire(2);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Achats ───────────────────────────────────────────────

describe("listerAchats", () => {
  it("appelle GET /famille/achats", async () => {
    api.get.mockResolvedValueOnce({ data: { items: [{ id: 1, nom: "Jouet" }] } });
    const result = await listerAchats();
    expect(result).toHaveLength(1);
  });
});

describe("creerAchat", () => {
  it("appelle POST /famille/achats", async () => {
    api.post.mockResolvedValueOnce({ data: { id: 5, nom: "Livre" } });
    const result = await creerAchat({ nom: "Livre" } as never);
    expect(result.id).toBe(5);
  });
});

describe("supprimerAchat", () => {
  it("appelle DELETE /famille/achats/:id", async () => {
    api.delete.mockResolvedValueOnce({ data: null });
    await supprimerAchat(5);
    expect(api.delete).toHaveBeenCalled();
  });
});

// ─── Config Garde / Jours sans crèche ─────────────────────

describe("lireConfigGarde", () => {
  it("appelle GET /famille/config/garde", async () => {
    const config = { semaines_fermeture: [], nom_creche: "Rainbow", zone_academique: "C", annee_courante: 2024 };
    api.get.mockResolvedValueOnce({ data: config });
    const result = await lireConfigGarde();
    expect(result.nom_creche).toBe("Rainbow");
  });
});

describe("joursSansCReche", () => {
  it("appelle GET /famille/planning/jours-sans-creche", async () => {
    api.get.mockResolvedValueOnce({ data: { mois: "2024-06", jours: [], total: 5 } });
    const result = await joursSansCReche("2024-06");
    expect(result.total).toBe(5);
  });
});
