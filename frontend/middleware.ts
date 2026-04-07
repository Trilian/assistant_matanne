import { NextRequest, NextResponse } from 'next/server'

const ROUTES_PUBLIQUES = ["/connexion", "/inscription"];
const FICHIERS_PUBLICS = ["/_next", "/icons", "/manifest.json", "/sw.js", "/offline.html", "/favicon.ico"];

export function middleware(request: NextRequest) {
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
    '/((?!_next/static|_next/image|favicon.ico|icons|manifest.json|sw.js|offline.html).*)',
  ],
}
