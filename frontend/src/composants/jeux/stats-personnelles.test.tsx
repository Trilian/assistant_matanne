/**
 * Tests unitaires pour StatsPersonnelles component.
 * 
 * Vérifie:
 * - Rendu des 4 cartes métriques
 * - Sélecteur période
 * - Tabs (Évolution, Patterns, Détails)
 * - Calculs avec données mockées
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StatsPersonnelles } from './stats-personnelles'

type FetchMock = ReturnType<typeof vi.fn>

vi.mock('recharts', async () => {
  const actual = await vi.importActual<typeof import('recharts')>('recharts')
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div style={{ width: 800, height: 320 }} data-testid="mock-responsive-container">
        {children}
      </div>
    ),
  }
})

// Mock data
const mockStatsData = {
  roi: {
    roi: 15.5,
    gains_totaux: 1550.0,
    mises_totales: 1340.0,
    benefice_net: 210.0,
    nb_paris: 25,
    nb_grilles: 10,
    periode_jours: 30
  },
  win_rate: {
    win_rate_global: 42.5,
    win_rate_paris: 48.0,
    win_rate_loto: 5.0,
    win_rate_euromillions: 10.0,
    nb_gagnants: 15,
    nb_total: 35,
    periode_jours: 30
  },
  patterns: {
    meilleur_type_pari: "1",
    meilleure_strategie_loto: "frequences",
    meilleure_strategie_euro: "equilibree",
    roi_par_type: {
      "1": { roi: 25.5, nb: 12 },
      "X": { roi: -15.0, nb: 8 },
      "2": { roi: 10.2, nb: 5 }
    },
    recommandations: [
      "Prioriser les paris '1' (ROI 25.5%)",
      "Stratégie Loto la plus rentable: frequences",
      "Stratégie Euromillions la plus rentable: equilibree"
    ],
    periode_jours: 90
  },
  evolution: [
    { mois: "2024-01", roi: 5.0, benefice: 50.0, gains: 500.0, mises: 450.0 },
    { mois: "2024-02", roi: 10.0, benefice: 100.0, gains: 1100.0, mises: 1000.0 },
    { mois: "2024-03", roi: 15.5, benefice: 210.0, gains: 1550.0, mises: 1340.0 }
  ]
}

// Mock fetch
global.fetch = vi.fn()

describe('StatsPersonnelles', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })

    vi.clearAllMocks()
    
    // Mock successful fetch
    ;(global.fetch as FetchMock).mockResolvedValue({
      ok: true,
      json: async () => mockStatsData
    })
  })

  const renderComponent = (userId = 1) => {
    return render(
      <QueryClientProvider client={queryClient}>
        <StatsPersonnelles userId={userId} />
      </QueryClientProvider>
    )
  }

  it('affiche le loader pendant le chargement', () => {
    ;(global.fetch as FetchMock).mockImplementation(() => new Promise(() => {})) // Never resolves
    
    renderComponent()
    
    expect(screen.getByText(/chargement statistiques/i)).toBeInTheDocument()
  })

  it('affiche les 4 cartes métriques', async () => {
    renderComponent()

    await waitFor(() => {
      // ROI Global
      expect(screen.getByText(/ROI Global/i)).toBeInTheDocument()
      expect(screen.getByText(/15\.5%/)).toBeInTheDocument()

      // Win Rate
      expect(screen.getByText(/Win Rate/i)).toBeInTheDocument()
      expect(screen.getByText(/42\.5%/)).toBeInTheDocument()

      // Bénéfice Net
      expect(screen.getByText(/Bénéfice Net/i)).toBeInTheDocument()
      expect(screen.getByText(/210\.00€/)).toBeInTheDocument()

      // Activité
      expect(screen.getByText(/Activité/i)).toBeInTheDocument()
      expect(screen.getAllByText(/35/).length).toBeGreaterThan(0) // nb_paris + nb_grilles
    })
  })

  it('affiche le sélecteur de période', async () => {
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })
  })

  it('charge la période par défaut via le sélecteur', async () => {
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    // Vérifier que le fetch initial inclut la période 30 jours
    await waitFor(() => {
      const appels = (global.fetch as FetchMock).mock.calls
      expect(appels.some(([url]) => String(url).includes('periode=30'))).toBe(true)
    })
  })

  it('affiche les 3 tabs', async () => {
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /évolution/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /patterns/i })).toBeInTheDocument()
      expect(screen.getByRole('tab', { name: /détails/i })).toBeInTheDocument()
    })
  })

  it('affiche le graphique dans tab Évolution', async () => {
    renderComponent()

    await waitFor(() => {
      const tabEvolution = screen.getByRole('tab', { name: /évolution/i })
      expect(tabEvolution).toHaveAttribute('data-state', 'active')
      expect(screen.getByText(/Bénéfice et ROI mensuels/i)).toBeInTheDocument()
    })
  })

  it('affiche les recommandations dans tab Patterns', async () => {
    const user = userEvent.setup()
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /patterns/i })).toBeInTheDocument()
    })

    const tabPatterns = screen.getByRole('tab', { name: /patterns/i })
    await user.click(tabPatterns)

    await waitFor(() => {
      expect(screen.getByText(/Recommandations/i)).toBeInTheDocument()
      expect(screen.getByText(/Prioriser les paris '1'/)).toBeInTheDocument()
      expect(screen.getByText(/Stratégie Loto la plus rentable/)).toBeInTheDocument()
    })
  })

  it('affiche le ROI par type de pari dans tab Patterns', async () => {
    const user = userEvent.setup()
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /patterns/i })).toBeInTheDocument()
    })

    const tabPatterns = screen.getByRole('tab', { name: /patterns/i })
    await user.click(tabPatterns)

    await waitFor(() => {
      expect(screen.getByText(/ROI par type de pari/i)).toBeInTheDocument()
      expect(screen.getAllByText('1').length).toBeGreaterThan(0)
      expect(screen.getAllByText('X').length).toBeGreaterThan(0)
    })
  })

  it('affiche les détails financiers dans tab Détails', async () => {
    const user = userEvent.setup()
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /détails/i })).toBeInTheDocument()
    })

    const tabDetails = screen.getByRole('tab', { name: /détails/i })
    await user.click(tabDetails)

    await waitFor(() => {
      expect(screen.getByText(/Résumé Financier/i)).toBeInTheDocument()
      expect(screen.getAllByText(/1550\.00€/).length).toBeGreaterThan(0) // Gains
      expect(screen.getByText(/-1340\.00€/)).toBeInTheDocument() // Mises
      expect(screen.getByText(/\+210\.00€/)).toBeInTheDocument() // Bénéfice
    })
  })

  it('affiche le win rate par jeu dans tab Détails', async () => {
    const user = userEvent.setup()
    renderComponent()

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /détails/i })).toBeInTheDocument()
    })

    const tabDetails = screen.getByRole('tab', { name: /détails/i })
    await user.click(tabDetails)

    await waitFor(() => {
      expect(screen.getByText(/Win Rate par jeu/i)).toBeInTheDocument()
      expect(screen.getByText(/48\.0%/)).toBeInTheDocument() // Paris
      expect(screen.getByText(/5\.0%/)).toBeInTheDocument() // Loto
      expect(screen.getByText(/10\.0%/)).toBeInTheDocument() // Euromillions
    })
  })

  it('affiche erreur si fetch échoue', async () => {
    ;(global.fetch as FetchMock).mockRejectedValue(new Error('API Error'))
    
    renderComponent()

    await waitFor(() => {
      expect(screen.getByText(/erreur chargement statistiques/i)).toBeInTheDocument()
    })
  })

  it('calcule correctement le total activité (paris + grilles)', async () => {
    renderComponent()

    await waitFor(() => {
      // nb_paris (25) + nb_grilles (10) = 35
      expect(screen.getByText('35')).toBeInTheDocument()
    })
  })

  it('utilise les couleurs correctes pour ROI positif/négatif', async () => {
    renderComponent()

    await waitFor(() => {
      const roiElement = screen.getByText(/15\.5%/)
      expect(roiElement).toHaveClass('text-green-600') // ROI positif
    })
  })
})
