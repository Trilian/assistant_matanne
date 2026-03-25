// ═══════════════════════════════════════════════════════════
// Tests Zod — Validateurs Sprint 11
// ═══════════════════════════════════════════════════════════

import { describe, it, expect } from "vitest";
import {
  schemaAnniversaire,
  schemaEvenementFamilial,
  schemaActiviteFamille,
  schemaDepenseBudget,
  schemaProjetMaison,
  schemaTacheEntretien,
  schemaPariSportif,
  schemaNote,
  schemaJournal,
  schemaContact,
} from "@/bibliotheque/validateurs";

// ─── Famille ──────────────────────────────────────

describe("schemaAnniversaire", () => {
  it("accepte des données valides", () => {
    const result = schemaAnniversaire.safeParse({
      nom_personne: "Mamie Françoise",
      date_naissance: "1955-08-20",
      relation: "grand_parent",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un nom vide", () => {
    const result = schemaAnniversaire.safeParse({
      nom_personne: "",
      date_naissance: "1955-08-20",
      relation: "parent",
    });
    expect(result.success).toBe(false);
  });

  it("rejette une relation invalide", () => {
    const result = schemaAnniversaire.safeParse({
      nom_personne: "Test",
      date_naissance: "1990-01-01",
      relation: "voisin",
    });
    expect(result.success).toBe(false);
  });
});

describe("schemaEvenementFamilial", () => {
  it("accepte des données valides", () => {
    const result = schemaEvenementFamilial.safeParse({
      titre: "Noël en famille",
      date_evenement: "2026-12-25",
      type_evenement: "fete",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un titre vide", () => {
    const result = schemaEvenementFamilial.safeParse({
      titre: "",
      date_evenement: "2026-12-25",
      type_evenement: "fete",
    });
    expect(result.success).toBe(false);
  });

  it("applique la recurrence par défaut", () => {
    const result = schemaEvenementFamilial.safeParse({
      titre: "Test",
      date_evenement: "2026-01-01",
      type_evenement: "tradition",
    });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.recurrence).toBe("unique");
    }
  });
});

describe("schemaActiviteFamille", () => {
  it("accepte des données valides", () => {
    const result = schemaActiviteFamille.safeParse({
      titre: "Sortie au parc",
      date_prevue: "2026-05-15",
    });
    expect(result.success).toBe(true);
  });

  it("rejette sans titre", () => {
    const result = schemaActiviteFamille.safeParse({
      date_prevue: "2026-05-15",
    });
    expect(result.success).toBe(false);
  });
});

describe("schemaDepenseBudget", () => {
  it("accepte des données valides", () => {
    const result = schemaDepenseBudget.safeParse({
      categorie: "loisirs",
      montant: 35,
    });
    expect(result.success).toBe(true);
  });

  it("rejette un montant à zéro", () => {
    const result = schemaDepenseBudget.safeParse({
      categorie: "loisirs",
      montant: 0,
    });
    expect(result.success).toBe(false);
  });
});

// ─── Maison ──────────────────────────────────────

describe("schemaProjetMaison", () => {
  it("accepte des données valides", () => {
    const result = schemaProjetMaison.safeParse({
      nom: "Refaire la terrasse",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un nom vide", () => {
    const result = schemaProjetMaison.safeParse({
      nom: "",
    });
    expect(result.success).toBe(false);
  });
});

describe("schemaTacheEntretien", () => {
  it("accepte des données complètes", () => {
    const result = schemaTacheEntretien.safeParse({
      nom: "Nettoyer les gouttières",
      categorie: "exterieur",
      frequence_jours: 90,
    });
    expect(result.success).toBe(true);
  });
});

// ─── Jeux ──────────────────────────────────────

describe("schemaPariSportif", () => {
  it("accepte des données valides", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 1,
      prediction: "1",
      cote: 1.45,
    });
    expect(result.success).toBe(true);
  });

  it("rejette un match_id à 0", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 0,
      prediction: "1",
      cote: 1.45,
    });
    expect(result.success).toBe(false);
  });
});

// ─── Utilitaires ──────────────────────────────────────

describe("schemaNote", () => {
  it("accepte des données valides", () => {
    const result = schemaNote.safeParse({
      titre: "Liste à faire",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un titre vide", () => {
    const result = schemaNote.safeParse({
      titre: "",
    });
    expect(result.success).toBe(false);
  });

  it("applique les défauts", () => {
    const result = schemaNote.safeParse({ titre: "Test" });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.epingle).toBe(false);
      expect(result.data.categorie).toBe("general");
      expect(result.data.tags).toEqual([]);
    }
  });
});

describe("schemaJournal", () => {
  it("accepte des données valides", () => {
    const result = schemaJournal.safeParse({
      date_entree: "2026-06-01",
      contenu: "Belle journée au parc",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un contenu vide", () => {
    const result = schemaJournal.safeParse({
      date_entree: "2026-06-01",
      contenu: "",
    });
    expect(result.success).toBe(false);
  });

  it("rejette énergie hors bornes", () => {
    const result = schemaJournal.safeParse({
      date_entree: "2026-06-01",
      contenu: "Test",
      energie: 11,
    });
    expect(result.success).toBe(false);
  });
});

describe("schemaContact", () => {
  it("accepte des données valides", () => {
    const result = schemaContact.safeParse({
      nom: "Dr. Martin",
    });
    expect(result.success).toBe(true);
  });

  it("rejette un nom vide", () => {
    const result = schemaContact.safeParse({
      nom: "",
    });
    expect(result.success).toBe(false);
  });

  it("rejette un email invalide", () => {
    const result = schemaContact.safeParse({
      nom: "Test",
      email: "not-an-email",
    });
    expect(result.success).toBe(false);
  });
});
