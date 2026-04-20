import { describe, it, expect } from "vitest";
import {
  schemaPariSportif,
  schemaGrilleLoto,
  schemaGrilleEuromillions,
} from "./validateurs-jeux";

describe("schemaPariSportif", () => {
  it("valide un pari correct", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 1,
      prediction: "1",
      cote: 1.8,
    });
    expect(result.success).toBe(true);
  });

  it("rejette match_id invalide", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 0,
      prediction: "1",
      cote: 1.8,
    });
    expect(result.success).toBe(false);
  });

  it("rejette prédiction vide", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 1,
      prediction: "",
      cote: 1.8,
    });
    expect(result.success).toBe(false);
  });

  it("rejette cote < 1", () => {
    const result = schemaPariSportif.safeParse({
      match_id: 1,
      prediction: "1",
      cote: 0.5,
    });
    expect(result.success).toBe(false);
  });

  it("applique les défauts", () => {
    const result = schemaPariSportif.parse({
      match_id: 1,
      prediction: "1",
      cote: 2.0,
    });
    expect(result.type_pari).toBe("1N2");
    expect(result.mise).toBe(0);
    expect(result.est_virtuel).toBe(true);
  });
});

describe("schemaGrilleLoto", () => {
  it("valide une grille correcte", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [5, 12, 23, 34, 49],
      numero_chance: 7,
    });
    expect(result.success).toBe(true);
  });

  it("rejette moins de 5 numéros", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [5, 12, 23],
      numero_chance: 7,
    });
    expect(result.success).toBe(false);
  });

  it("rejette plus de 5 numéros", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [1, 2, 3, 4, 5, 6],
      numero_chance: 7,
    });
    expect(result.success).toBe(false);
  });

  it("rejette numéro hors range (> 49)", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [5, 12, 23, 34, 50],
      numero_chance: 7,
    });
    expect(result.success).toBe(false);
  });

  it("rejette numéro < 1", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [0, 12, 23, 34, 49],
      numero_chance: 7,
    });
    expect(result.success).toBe(false);
  });

  it("rejette chance hors range (> 10)", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [5, 12, 23, 34, 49],
      numero_chance: 11,
    });
    expect(result.success).toBe(false);
  });

  it("rejette chance < 1", () => {
    const result = schemaGrilleLoto.safeParse({
      numeros: [5, 12, 23, 34, 49],
      numero_chance: 0,
    });
    expect(result.success).toBe(false);
  });

  it("applique les défauts", () => {
    const result = schemaGrilleLoto.parse({
      numeros: [1, 2, 3, 4, 5],
      numero_chance: 1,
    });
    expect(result.est_fleche).toBe(false);
  });
});

describe("schemaGrilleEuromillions", () => {
  it("valide une grille correcte", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12, 23, 34, 50],
      etoiles: [3, 11],
    });
    expect(result.success).toBe(true);
  });

  it("rejette moins de 5 numéros", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12],
      etoiles: [3, 11],
    });
    expect(result.success).toBe(false);
  });

  it("rejette numéro hors range (> 50)", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12, 23, 34, 51],
      etoiles: [3, 11],
    });
    expect(result.success).toBe(false);
  });

  it("rejette 1 étoile au lieu de 2", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12, 23, 34, 50],
      etoiles: [3],
    });
    expect(result.success).toBe(false);
  });

  it("rejette étoile hors range (> 12)", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12, 23, 34, 50],
      etoiles: [3, 13],
    });
    expect(result.success).toBe(false);
  });

  it("rejette étoile < 1", () => {
    const result = schemaGrilleEuromillions.safeParse({
      numeros: [5, 12, 23, 34, 50],
      etoiles: [0, 11],
    });
    expect(result.success).toBe(false);
  });

  it("applique les défauts", () => {
    const result = schemaGrilleEuromillions.parse({
      numeros: [1, 2, 3, 4, 5],
      etoiles: [1, 2],
    });
    expect(result.est_etoile_plus).toBe(false);
  });
});
