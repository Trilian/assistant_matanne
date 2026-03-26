// ============================================================
// Assistant Matanne — Tests de charge k6
// ============================================================
// Usage :
//   k6 run tests/load/k6_baseline.js
//   k6 run --vus 20 --duration 60s tests/load/k6_baseline.js
//
// Variables d'environnement :
//   BASE_URL  : URL du backend (défaut: http://localhost:8000)
//   JWT_TOKEN : Token JWT valide pour les endpoints authentifiés
//
// Seuils (thresholds) :
//   - Lectures (GET) : p95 < 500ms
//   - IA (POST /planning/generer) : p95 < 8000ms
//   - Erreurs : < 1%
// ============================================================

import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

// ── Configuration ────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const JWT_TOKEN = __ENV.JWT_TOKEN || "";

const headersJSON = {
  "Content-Type": "application/json",
  Authorization: JWT_TOKEN ? `Bearer ${JWT_TOKEN}` : "",
};

// ── Métriques personnalisées ─────────────────────────────────
const latenceLecture = new Trend("latence_lecture_ms", true);
const latenceIA = new Trend("latence_ia_ms", true);
const tauxErreur = new Rate("taux_erreur");

// ── Options de test ──────────────────────────────────────────
export const options = {
  scenarios: {
    // Scénario 1 : Lecture des recettes (endpoint le plus appelé)
    lecture_recettes: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "30s", target: 10 },
        { duration: "60s", target: 20 },
        { duration: "30s", target: 0 },
      ],
      exec: "scenarioLectureRecettes",
    },

    // Scénario 2 : Lecture des courses + inventaire
    lecture_courses: {
      executor: "constant-vus",
      vus: 5,
      duration: "90s",
      exec: "scenarioLectureCourses",
      startTime: "10s",
    },

    // Scénario 3 : Génération courses depuis planning (opération lourde)
    generation_courses: {
      executor: "constant-arrival-rate",
      rate: 2,           // 2 requêtes/seconde max
      timeUnit: "1s",
      duration: "60s",
      preAllocatedVUs: 5,
      exec: "scenarioGenerationCourses",
      startTime: "20s",
    },

    // Scénario 4 : Génération planning IA (endpoint IA lent)
    planning_ia: {
      executor: "constant-arrival-rate",
      rate: 1,           // 1 requête/seconde max (endpoint IA)
      timeUnit: "1s",
      duration: "30s",
      preAllocatedVUs: 3,
      exec: "scenarioPlanningIA",
      startTime: "30s",
    },
  },

  thresholds: {
    // Latences
    latence_lecture_ms: ["p(95)<500", "p(99)<1000"],
    latence_ia_ms: ["p(95)<8000"],

    // Taux d'erreur global
    taux_erreur: ["rate<0.01"],

    // Disponibilité HTTP
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<3000"],
  },
};

// ── Scénario 1 : GET /api/v1/recettes ───────────────────────
export function scenarioLectureRecettes() {
  const debut = Date.now();

  const res = http.get(`${BASE_URL}/api/v1/recettes?page=1&page_size=20`, {
    headers: headersJSON,
    tags: { name: "GET /recettes" },
  });

  const duree = Date.now() - debut;
  latenceLecture.add(duree);
  tauxErreur.add(res.status >= 400 ? 1 : 0);

  check(res, {
    "recettes: status 200": (r) => r.status === 200,
    "recettes: has items": (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.items) || Array.isArray(body);
      } catch {
        return false;
      }
    },
  });

  sleep(1 + Math.random() * 2);
}

// ── Scénario 2 : GET /api/v1/courses + /inventaire ──────────
export function scenarioLectureCourses() {
  const debut = Date.now();

  const resCourses = http.get(`${BASE_URL}/api/v1/courses`, {
    headers: headersJSON,
    tags: { name: "GET /courses" },
  });

  latenceLecture.add(Date.now() - debut);
  tauxErreur.add(resCourses.status >= 400 ? 1 : 0);

  check(resCourses, {
    "courses: status 200": (r) => r.status === 200,
  });

  sleep(0.5);

  const debutInv = Date.now();
  const resInv = http.get(`${BASE_URL}/api/v1/inventaire?page=1`, {
    headers: headersJSON,
    tags: { name: "GET /inventaire" },
  });

  latenceLecture.add(Date.now() - debutInv);
  tauxErreur.add(resInv.status >= 400 ? 1 : 0);

  check(resInv, {
    "inventaire: status 200": (r) => r.status === 200,
  });

  sleep(1 + Math.random());
}

// ── Scénario 3 : POST /api/v1/courses/generer-depuis-planning ─
export function scenarioGenerationCourses() {
  const payload = JSON.stringify({
    semaine_offset: 0,
    soustraire_inventaire: true,
  });

  const debut = Date.now();
  const res = http.post(
    `${BASE_URL}/api/v1/courses/generer-depuis-planning`,
    payload,
    {
      headers: headersJSON,
      tags: { name: "POST /courses/generer-depuis-planning" },
      timeout: "10s",
    }
  );

  latenceLecture.add(Date.now() - debut);
  tauxErreur.add(res.status >= 400 ? 1 : 0);

  check(res, {
    "gen-courses: status 200 ou 201": (r) => r.status === 200 || r.status === 201,
  });

  sleep(2);
}

// ── Scénario 4 : POST /api/v1/planning/generer (IA) ─────────
export function scenarioPlanningIA() {
  const payload = JSON.stringify({
    semaine_offset: 0,
    preferences: {},
  });

  const debut = Date.now();
  const res = http.post(`${BASE_URL}/api/v1/planning/generer`, payload, {
    headers: headersJSON,
    tags: { name: "POST /planning/generer (IA)" },
    timeout: "30s",
  });

  const duree = Date.now() - debut;
  latenceIA.add(duree);
  tauxErreur.add(res.status >= 400 ? 1 : 0);

  check(res, {
    "planning-ia: status 200 ou 201": (r) => r.status === 200 || r.status === 201,
    "planning-ia: réponse dans les 8s": () => duree < 8000,
  });

  sleep(3);
}

// ── Setup / Teardown ─────────────────────────────────────────
export function setup() {
  // Vérification santé avant de lancer les tests
  const res = http.get(`${BASE_URL}/health`);
  if (res.status !== 200) {
    throw new Error(`Backend non disponible (${res.status}): ${BASE_URL}/health`);
  }
  console.log(`✓ Backend disponible: ${BASE_URL}`);
  return { baseUrl: BASE_URL };
}
