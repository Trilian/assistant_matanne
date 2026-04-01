// ═══════════════════════════════════════════════════════════
// Proxy Next.js - Protection des routes cote edge
// ═══════════════════════════════════════════════════════════

import { NextResponse, type NextRequest } from "next/server";

const ROUTES_PUBLIQUES = ["/connexion", "/inscription"];
const FICHIERS_PUBLICS = ["/_next", "/icons", "/manifest.json", "/sw.js", "/offline.html", "/favicon.ico"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (FICHIERS_PUBLICS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  if (ROUTES_PUBLIQUES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next();
  }

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
    "/((?!_next/static|_next/image|favicon.ico|icons|manifest.json|sw.js|offline.html).*)",
  ],
};