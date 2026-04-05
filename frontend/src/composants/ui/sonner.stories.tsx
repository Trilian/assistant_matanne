import type { Meta, StoryObj } from '@storybook/react'
import { Toaster } from './sonner'
import { Button } from './button'
import { toast } from 'sonner'

const meta: Meta<typeof Toaster> = {
  title: 'UI/Sonner',
  component: Toaster,
}

export default meta
type Story = StoryObj<typeof Toaster>

export const AllVariants: Story = {
  render: () => (
    <div className="space-y-2">
      <Toaster />
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" onClick={() => toast('Notification simple')}>
          Default
        </Button>
        <Button variant="outline" onClick={() => toast.success('Recette ajoutée !')}>
          Succès
        </Button>
        <Button variant="outline" onClick={() => toast.error('Erreur de sauvegarde')}>
          Erreur
        </Button>
        <Button variant="outline" onClick={() => toast.warning('Stock faible')}>
          Warning
        </Button>
        <Button variant="outline" onClick={() => toast.info('Planning mis à jour')}>
          Info
        </Button>
        <Button
          variant="outline"
          onClick={() =>
            toast.promise(new Promise((r) => setTimeout(r, 2000)), {
              loading: 'Génération IA...',
              success: 'Suggestions prêtes !',
              error: 'Échec de la génération',
            })
          }
        >
          Promise
        </Button>
      </div>
    </div>
  ),
}
