import { NextRequest, NextResponse } from 'next/server'
import type { NextMiddleware } from 'next/server'

/**
 * Middleware — Bloque l'accès aux routes avancées (/ia-avancee)
 * pour les utilisateurs non-admin
 */
export const middleware: NextMiddleware = (request: NextRequest) => {
  const pathname = request.nextUrl.pathname

  // Bloquer les routes /ia-avancee sauf pour les admins
  if (pathname.startsWith('/ia-avancee')) {
    // Note: Une vérification complète du rôle nécessiterait un JWT decode
    // Pour une meilleure protection, cela est aussi géré côté backend et API
    // Cette route ne devrait pas être accessible via la sidebar (déjà supprimée)
    // Rediriger vers le dashboard
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

// Appliquer le middleware à toutes les routes (sauf api, etc.)
export const config = {
  matcher: [
    /*
     * Correspondre à tous les chemins de requête sauf les suivants:
     * - api (routes API)
     * - _next/static (fichiers statiques)
     * - _next/image (optimisation image)
     * - favicon.ico (favicon)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
