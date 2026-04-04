const CLE_ARTICLE_EN_ATTENTE = "assistantMatannePendingArticle";

function normaliserTexte(texte) {
  return (texte || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

function texteBouton(bouton) {
  return (bouton?.textContent || bouton?.getAttribute?.("aria-label") || "")
    .trim()
    .toLowerCase();
}

function estBoutonAjout(bouton) {
  if (!(bouton instanceof HTMLButtonElement) || bouton.disabled) {
    return false;
  }
  const texte = texteBouton(bouton);
  return texte.includes("ajouter") || texte.includes("panier") || texte.includes("drive");
}

function trouverBoutonAjout() {
  const selecteurs = [
    '[data-testid*="add-to-cart"]',
    'button[aria-label*="Ajouter"]',
    'button[title*="Ajouter"]',
    'button[class*="add"]',
    'button[class*="cart"]'
  ];

  for (const selecteur of selecteurs) {
    const bouton = document.querySelector(selecteur);
    if (estBoutonAjout(bouton)) {
      return bouton;
    }
  }

  const boutons = Array.from(document.querySelectorAll("button"));
  return boutons.find((bouton) => estBoutonAjout(bouton)) || null;
}

function extraireIdProduitDepuisUrl(url) {
  if (!url) return null;
  const match = url.match(/\/p\/[^/]*-(\d{8,14})/i) || url.match(/[-_/](\d{8,14})(?:\?.*)?$/i);
  return match?.[1] || null;
}

function extraireProduitDepuisJsonLd() {
  const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
  for (const script of scripts) {
    try {
      const brut = JSON.parse(script.textContent || "null");
      const candidats = Array.isArray(brut) ? brut : [brut, ...(Array.isArray(brut?.['@graph']) ? brut['@graph'] : [])];
      for (const item of candidats) {
        if (!item || item['@type'] !== 'Product') continue;
        const url = item.url || window.location.href;
        return {
          produit_drive_id: item.productID || item.sku || item.gtin13 || extraireIdProduitDepuisUrl(url),
          produit_drive_nom: item.name || document.title,
          produit_drive_ean: item.gtin13 || item.gtin || null,
          produit_drive_url: url,
        };
      }
    } catch {
      // ignore json-ld parse errors
    }
  }
  return null;
}

function extraireProduitDepuisElement(element) {
  const bloc = element?.closest?.('article, li, div');
  const lien = bloc?.querySelector?.('a[href*="/p/"]') || document.querySelector('a[href*="/p/"]');
  const titre = bloc?.querySelector?.('h1, h2, h3, [data-testid*="title"], a[href*="/p/"]');
  const url = lien?.href || window.location.href;
  const nom = titre?.textContent?.trim() || document.querySelector('h1')?.textContent?.trim() || document.title;
  return {
    produit_drive_id: extraireIdProduitDepuisUrl(url),
    produit_drive_nom: nom,
    produit_drive_ean: extraireIdProduitDepuisUrl(url),
    produit_drive_url: url,
  };
}

function extraireProduitDepuisPage() {
  return extraireProduitDepuisJsonLd() || extraireProduitDepuisElement(document.body);
}

function memoriserArticle(article) {
  if (!article) return;
  sessionStorage.setItem(CLE_ARTICLE_EN_ATTENTE, JSON.stringify(article));
}

function lireArticleMemorise() {
  try {
    const brut = sessionStorage.getItem(CLE_ARTICLE_EN_ATTENTE);
    return brut ? JSON.parse(brut) : null;
  } catch {
    return null;
  }
}

async function obtenirArticleContexte() {
  const stockage = await chrome.storage.local.get(["driveSyncQueue", "drivePendingSearchArticles"]);
  const queue = stockage.driveSyncQueue || [];
  const articleMappe = queue.find((item) => {
    const url = item.correspondance?.produit_drive_url;
    return typeof url === "string" && window.location.href.startsWith(url);
  });
  if (articleMappe) {
    memoriserArticle(articleMappe);
    return articleMappe;
  }

  const memorise = lireArticleMemorise();
  if (memorise) {
    return memorise;
  }

  const pending = stockage.drivePendingSearchArticles || [];
  const q = new URL(window.location.href).searchParams.get("q");
  const hashNom = decodeURIComponent((window.location.hash || "").replace("#assistant-matanne=", ""));
  const reference = normaliserTexte(hashNom || q || document.title);
  const articleRecherche = pending.find((item) => {
    const nom = normaliserTexte(item.nom);
    return reference && (nom.includes(reference) || reference.includes(nom));
  });

  if (articleRecherche) {
    memoriserArticle(articleRecherche);
    return articleRecherche;
  }

  return null;
}

async function marquerResultat(article, statut, extras = {}) {
  if (!article?.id) return;
  const stockage = await chrome.storage.local.get("driveSyncResults");
  const resultats = stockage.driveSyncResults || {};
  resultats[article.id] = {
    nom: article.nom,
    statut,
    url: window.location.href,
    horodatage: new Date().toISOString(),
    ...extras,
  };
  await chrome.storage.local.set({ driveSyncResults: resultats });
}

async function sauvegarderCorrespondance(article, produit) {
  if (!article || !produit?.produit_drive_id) {
    return false;
  }

  const stockage = await chrome.storage.local.get(["apiBaseUrl", "apiToken"]);
  const base = (stockage.apiBaseUrl || "http://localhost:8000/api/v1").replace(/\/$/, "");
  const token = (stockage.apiToken || "").trim();

  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
  }

  const response = await fetch(`${base}/courses/correspondances-drive`, {
    method: "POST",
    headers,
    credentials: "include",
    body: JSON.stringify({
      nom_article: article.nom,
      ingredient_id: article.ingredient_id ?? null,
      produit_drive_id: produit.produit_drive_id,
      produit_drive_nom: produit.produit_drive_nom || article.nom,
      produit_drive_ean: produit.produit_drive_ean || null,
      produit_drive_url: produit.produit_drive_url || window.location.href,
      quantite_par_defaut: article.quantite || 1,
    }),
  });

  return response.ok;
}

function installerCaptureManuelle() {
  document.addEventListener(
    "click",
    (event) => {
      const bouton = event.target?.closest?.("button");
      if (!estBoutonAjout(bouton)) {
        return;
      }

      window.setTimeout(async () => {
        const article = await obtenirArticleContexte();
        if (!article) {
          return;
        }

        const produit = extraireProduitDepuisElement(bouton) || extraireProduitDepuisPage();
        if (!produit?.produit_drive_id) {
          await marquerResultat(article, "produit_non_identifie");
          return;
        }

        const ok = await sauvegarderCorrespondance(article, produit);
        await marquerResultat(article, ok ? "correspondance_enregistree" : "correspondance_echec", {
          produit: produit.produit_drive_nom,
        });
      }, 800);
    },
    true,
  );
}

async function traiterArticleCourant() {
  const article = await obtenirArticleContexte();
  if (!article) return;

  memoriserArticle(article);

  const estArticleMappe = Boolean(article.correspondance?.produit_drive_url) &&
    window.location.href.startsWith(article.correspondance.produit_drive_url);

  if (!estArticleMappe) {
    return;
  }

  await new Promise((resolve) => setTimeout(resolve, 1500));
  const bouton = trouverBoutonAjout();
  if (!bouton) {
    await marquerResultat(article, "bouton_introuvable");
    return;
  }

  bouton.click();
  await marquerResultat(article, "ajout_tente");
}

installerCaptureManuelle();

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    traiterArticleCourant().catch(() => undefined);
  });
} else {
  traiterArticleCourant().catch(() => undefined);
}
