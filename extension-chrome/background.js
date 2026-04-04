chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "START_DRIVE_SYNC") {
    lancerSync(message.articles || [])
      .then((resultat) => sendResponse({ ok: true, ...resultat }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  if (message?.type === "OPEN_MISSING_SEARCHES") {
    ouvrirRecherches(message.articles || [])
      .then((resultat) => sendResponse({ ok: true, ...resultat }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  if (message?.type === "SYNC_FROM_APP") {
    synchroniserDepuisListe(message.payload || {})
      .then((resultat) => sendResponse(resultat))
      .catch((error) => sendResponse({ ok: false, error: error.message }));
    return true;
  }

  return false;
});

function normaliserApiBase(url) {
  const valeur = (url || "").trim().replace(/\/$/, "");
  if (!valeur) {
    return "http://localhost:8000/api/v1";
  }
  return valeur.endsWith("/api/v1") ? valeur : `${valeur}/api/v1`;
}

async function chargerArticlesDepuisApi({ listeId, apiBaseUrl, apiToken }) {
  const stockage = await chrome.storage.local.get(["apiBaseUrl", "apiToken"]);
  const base = normaliserApiBase(apiBaseUrl || stockage.apiBaseUrl);
  const token = (apiToken || stockage.apiToken || "").trim();

  if (!listeId) {
    throw new Error("ID de liste manquant pour la synchronisation Drive.");
  }

  const headers = {};
  if (token) {
    headers.Authorization = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  }

  const response = await fetch(`${base}/courses/${listeId}/articles-drive`, {
    headers,
    credentials: "include",
  });
  if (!response.ok) {
    throw new Error(`Erreur API Carrefour Drive (${response.status}).`);
  }

  const articles = await response.json();
  await chrome.storage.local.set({
    apiBaseUrl: base,
    apiToken: token,
    listeId: String(listeId),
    lastArticlesDrive: articles,
  });
  return articles;
}

async function synchroniserDepuisListe(payload) {
  const articles = await chargerArticlesDepuisApi(payload);
  const articlesActifs = articles.filter((article) => !article.coche);
  const articlesMappes = articlesActifs.filter((article) => article.correspondance?.produit_drive_url);
  const articlesSansMapping = articlesActifs.filter((article) => !article.correspondance?.produit_drive_url);

  const resultatSync = await lancerSync(articlesMappes);
  const resultatRecherche = await ouvrirRecherches(articlesSansMapping);

  return {
    ok: true,
    total: articlesActifs.length,
    mappes: resultatSync.ouverts,
    recherches: resultatRecherche.ouverts,
  };
}

async function lancerSync(articles) {
  await chrome.storage.local.set({ driveSyncQueue: articles, driveSyncResults: {} });

  if (!articles.length) {
    return { ouverts: 0 };
  }

  for (const article of articles) {
    const url = article.correspondance?.produit_drive_url;
    if (!url) continue;
    await chrome.tabs.create({ url, active: false });
  }

  return { ouverts: articles.length };
}

async function ouvrirRecherches(articles) {
  if (!articles.length) {
    await chrome.storage.local.set({ drivePendingSearchArticles: [] });
    return { ouverts: 0 };
  }

  await chrome.storage.local.set({ drivePendingSearchArticles: articles });

  for (const article of articles) {
    const query = encodeURIComponent(article.nom);
    const ancre = `#assistant-matanne=${encodeURIComponent(article.nom)}`;
    const url = `https://www.carrefour.fr/s?q=${query}${ancre}`;
    await chrome.tabs.create({ url, active: false });
  }

  return { ouverts: articles.length };
}
