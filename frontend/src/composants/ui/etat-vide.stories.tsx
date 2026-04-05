import type { Meta, StoryObj } from '@storybook/react'
import { EtatVide } from './etat-vide'
import { Button } from './button'
import { UtensilsCrossed, ShoppingCart } from 'lucide-react'

const meta: Meta<typeof EtatVide> = {
  title: 'UI/EtatVide',
  component: EtatVide,
}

export default meta
type Story = StoryObj<typeof EtatVide>

export const Default: Story = {
  args: {
    Icone: UtensilsCrossed,
    titre: 'Aucune recette',
    description: 'Ajoutez votre première recette pour commencer.',
  },
}

export const WithAction: Story = {
  args: {
    Icone: ShoppingCart,
    titre: 'Liste de courses vide',
    description: 'Planifiez vos repas pour remplir la liste automatiquement.',
    action: <Button size="sm">Créer un planning</Button>,
  },
}

export const Minimal: Story = {
  args: {
    Icone: UtensilsCrossed,
    titre: 'Rien ici',
  },
}
