import { NextRequest, NextResponse } from 'next/server'

const ROUTES_PUBLIQUES = ["/connexion", "/inscription", "/auth-callback"];
const FICHIERS_PUBLICS = ["/_next", "/icons", "/manifest.json", "/sw.js", "/offline.html", "/favicon.ico"];

/** Décode le payload JWT et vérifie si le token est expiré (sans vérification de signature) */
function jwtExpire(token: string): boolean {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return true;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    if (!payload.exp) return false; // pas d'expiry = token permanent
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true; // malformé = considéré expiré
  }
}

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Laisser passer les fichiers statiques et routes API sans vérification
  if (FICHIERS_PUBLICS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  // Les routes API ne doivent jamais être redirigées vers /connexion
  if (pathname.startsWith('/api')) {
    return NextResponse.next();
  }

  // Routes publiques (connexion, inscription)
  if (ROUTES_PUBLIQUES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next();
  }

  // Vérifier le token JWT (cookie ou header Authorization)
  const token =
    request.cookies.get("access_token")?.value ??
    request.headers.get("authorization")?.replace("Bearer ", "");

  if (!token || jwtExpire(token)) {
    const url = request.nextUrl.clone();
    url.pathname = "/connexion";
    url.searchParams.set("redirect", pathname);
    const response = NextResponse.redirect(url);
    // Supprimer le cookie expiré s'il existe
    if (token) response.cookies.delete("access_token");
    return response;
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|icons|manifest.json|sw.js|offline.html).*)',
  ],
}
