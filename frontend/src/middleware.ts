// ═══════════════════════════════════════════════════════════
// Middleware Next.js — Protection des routes côté edge
// ═══════════════════════════════════════════════════════════

import { NextResponse, type NextRequest } from "next/server";

const ROUTES_PUBLIQUES = ["/connexion", "/inscription"];
const FICHIERS_PUBLICS = ["/_next", "/icons", "/manifest.json", "/sw.js", "/offline.html", "/favicon.ico"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Laisser passer les fichiers statiques et les routes API
  if (FICHIERS_PUBLICS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Laisser passer les routes publiques
  if (ROUTES_PUBLIQUES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next();
  }

  // Vérifier la présence du token (cookie ou header)
  const token =
    request.cookies.get("access_token")?.value ??
    request.headers.get("authorization")?.replace("Bearer ", "");

  if (!token) {
    const url = request.nextUrl.clone();
    url.pathname = "/connexion";
    url.searchParams.set("redirect", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    // Match all routes except static files
    "/((?!_next/static|_next/image|favicon.ico|icons|manifest.json|sw.js|offline.html).*)",
  ],
};
