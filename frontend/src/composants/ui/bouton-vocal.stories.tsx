import type { Meta, StoryObj } from '@storybook/react'
import { BoutonVocal } from './bouton-vocal'
import { fn } from '@storybook/test'

const meta: Meta<typeof BoutonVocal> = {
  title: 'UI/BoutonVocal',
  component: BoutonVocal,
}

export default meta
type Story = StoryObj<typeof BoutonVocal>

export const Default: Story = {
  args: {
    onResultat: fn(),
    placeholder: 'Dictez une recette...',
  },
}

export const SmallOutline: Story = {
  args: {
    onResultat: fn(),
    variante: 'outline',
    taille: 'sm',
  },
}
