/**
 * Couche de données offline — IndexedDB wrapper léger.
 * Permet de cacher recettes, planning et courses pour consultation hors ligne.
 */

const DB_NAME = "matanne-offline";
const DB_VERSION = 1;

type NomStore = "recettes" | "planning" | "courses";

function ouvrirDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains("recettes")) {
        db.createObjectStore("recettes", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("planning")) {
        db.createObjectStore("planning", { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains("courses")) {
        db.createObjectStore("courses", { keyPath: "id" });
      }
    };

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

function executer<T>(
  store: NomStore,
  mode: IDBTransactionMode,
  fn: (objectStore: IDBObjectStore) => IDBRequest<T>
): Promise<T> {
  return ouvrirDB().then(
    (db) =>
      new Promise<T>((resolve, reject) => {
        const tx = db.transaction(store, mode);
        const os = tx.objectStore(store);
        const req = fn(os);
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
        tx.oncomplete = () => db.close();
      })
  );
}

/** Sauvegarder un item dans un store */
export async function sauvegarderItem<T extends { id: unknown }>(
  store: NomStore,
  item: T
): Promise<void> {
  await executer(store, "readwrite", (os) => os.put(item));
}

/** Sauvegarder plusieurs items (remplace le contenu existant) */
export async function sauvegarderListe<T extends { id: unknown }>(
  store: NomStore,
  items: T[]
): Promise<void> {
  const db = await ouvrirDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(store, "readwrite");
    const os = tx.objectStore(store);
    os.clear();
    for (const item of items) {
      os.put(item);
    }
    tx.oncomplete = () => {
      db.close();
      resolve();
    };
    tx.onerror = () => {
      db.close();
      reject(tx.error);
    };
  });
}

/** Récupérer un item par son id */
export async function obtenirItem<T>(
  store: NomStore,
  id: string | number
): Promise<T | undefined> {
  return executer<T>(store, "readonly", (os) => os.get(id));
}

/** Récupérer tous les items d'un store */
export async function obtenirTout<T>(store: NomStore): Promise<T[]> {
  return executer<T[]>(store, "readonly", (os) => os.getAll());
}

/** Supprimer un item */
export async function supprimerItem(
  store: NomStore,
  id: string | number
): Promise<void> {
  await executer(store, "readwrite", (os) => os.delete(id));
}

/** Vider un store entier */
export async function viderStore(store: NomStore): Promise<void> {
  await executer(store, "readwrite", (os) => os.clear());
}

/**
 * Hook de synchronisation — sauvegarde les données API dans IndexedDB
 * pour les rendre disponibles hors ligne.
 * À appeler après un fetch réussi côté TanStack Query.
 */
export function cacherPourOffline<T extends { id: unknown }>(
  store: NomStore,
  donnees: T | T[] | undefined | null
): void {
  if (!donnees || typeof indexedDB === "undefined") return;

  if (Array.isArray(donnees)) {
    sauvegarderListe(store, donnees).catch(() => {});
  } else {
    sauvegarderItem(store, donnees).catch(() => {});
  }
}
