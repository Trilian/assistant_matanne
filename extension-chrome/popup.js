const elements = {
  apiBaseUrl: document.getElementById("apiBaseUrl"),
  apiToken: document.getElementById("apiToken"),
  listeId: document.getElementById("listeId"),
  chargerBtn: document.getElementById("chargerBtn"),
  ouvrirDriveBtn: document.getElementById("ouvrirDriveBtn"),
  syncMappedBtn: document.getElementById("syncMappedBtn"),
  ouvrirRecherchesBtn: document.getElementById("ouvrirRecherchesBtn"),
  status: document.getElementById("status"),
  articlesList: document.getElementById("articlesList"),
};

function setStatus(message) {
  elements.status.textContent = message;
}

function normaliserApiBase(url) {
  const base = (url || "http://localhost:8000/api/v1").trim().replace(/\/$/, "");
  return base.endsWith("/api/v1") ? base : `${base}/api/v1`;
}

async function chargerConfiguration() {
  const config = await chrome.storage.local.get(["apiBaseUrl", "apiToken", "listeId", "lastArticlesDrive"]);
  elements.apiBaseUrl.value = config.apiBaseUrl || "http://localhost:8000/api/v1";
  elements.apiToken.value = config.apiToken || "";
  elements.listeId.value = config.listeId || "";
  renderArticles(config.lastArticlesDrive || []);
}

async function enregistrerConfiguration() {
  await chrome.storage.local.set({
    apiBaseUrl: elements.apiBaseUrl.value.trim(),
    apiToken: elements.apiToken.value.trim(),
    listeId: elements.listeId.value.trim(),
  });
}

function renderArticles(articles) {
  elements.articlesList.innerHTML = "";
  if (!articles.length) {
    elements.articlesList.innerHTML = '<li>Aucun article Drive chargé.</li>';
    return;
  }

  for (const article of articles) {
    const li = document.createElement("li");
    const estMappe = Boolean(article.correspondance?.produit_drive_url);
    li.innerHTML = `
      <div class="article-top">
        <strong>${article.nom}</strong>
        <span class="badge ${estMappe ? "ok" : "warn"}">${estMappe ? "mappé" : "à chercher"}</span>
      </div>
      <div class="small">Qté: ${article.quantite} ${article.categorie ? `· ${article.categorie}` : ""}</div>
      <div class="small">${article.correspondance?.produit_drive_nom || "Aucune correspondance Carrefour"}</div>
    `;
    elements.articlesList.appendChild(li);
  }
}

async function chargerArticlesDrive() {
  await enregistrerConfiguration();
  const apiBaseUrl = normaliserApiBase(elements.apiBaseUrl.value);
  const token = elements.apiToken.value.trim();
  const listeId = elements.listeId.value.trim();

  if (!listeId) {
    setStatus("Renseigne un ID de liste.");
    return;
  }

  setStatus("Chargement des articles Drive...");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const response = await fetch(`${apiBaseUrl}/courses/${listeId}/articles-drive`, { headers });
  if (!response.ok) {
    const message = `Erreur API (${response.status})`;
    setStatus(message);
    throw new Error(message);
  }

  const articles = await response.json();
  await chrome.storage.local.set({ lastArticlesDrive: articles, listeId });
  renderArticles(articles);
  setStatus(`${articles.length} article(s) Drive chargé(s).`);
}

async function ouvrirDrive() {
  await chrome.tabs.create({ url: "https://www.carrefour.fr/courses-en-ligne" });
  setStatus("Carrefour Drive ouvert.");
}

async function syncMapped() {
  const { lastArticlesDrive = [] } = await chrome.storage.local.get("lastArticlesDrive");
  const articlesMappes = lastArticlesDrive.filter((item) => item.correspondance?.produit_drive_url);

  if (!articlesMappes.length) {
    setStatus("Aucun article mappé à ajouter automatiquement.");
    return;
  }

  await chrome.runtime.sendMessage({
    type: "START_DRIVE_SYNC",
    articles: articlesMappes,
  });
  setStatus(`${articlesMappes.length} produit(s) mappé(s) envoyés vers Carrefour.`);
}

async function ouvrirRecherches() {
  const { lastArticlesDrive = [] } = await chrome.storage.local.get("lastArticlesDrive");
  const articlesSansMapping = lastArticlesDrive.filter((item) => !item.correspondance?.produit_drive_url);

  if (!articlesSansMapping.length) {
    setStatus("Aucune recherche manquante.");
    return;
  }

  await chrome.runtime.sendMessage({
    type: "OPEN_MISSING_SEARCHES",
    articles: articlesSansMapping,
  });
  setStatus(`${articlesSansMapping.length} recherche(s) ouverte(s) pour les produits non mappés.`);
}

elements.chargerBtn.addEventListener("click", () => chargerArticlesDrive().catch((error) => setStatus(error.message)));
elements.ouvrirDriveBtn.addEventListener("click", () => ouvrirDrive().catch((error) => setStatus(error.message)));
elements.syncMappedBtn.addEventListener("click", () => syncMapped().catch((error) => setStatus(error.message)));
elements.ouvrirRecherchesBtn.addEventListener("click", () => ouvrirRecherches().catch((error) => setStatus(error.message)));

for (const input of [elements.apiBaseUrl, elements.apiToken, elements.listeId]) {
  input.addEventListener("change", () => enregistrerConfiguration().catch(() => undefined));
}

chargerConfiguration().catch(() => setStatus("Impossible de charger la configuration."));
