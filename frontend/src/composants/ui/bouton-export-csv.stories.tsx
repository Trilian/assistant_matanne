import type { Meta, StoryObj } from '@storybook/react'
import { BoutonExportCsv } from './bouton-export-csv'

const meta: Meta<typeof BoutonExportCsv> = {
  title: 'UI/BoutonExportCsv',
  component: BoutonExportCsv,
}

export default meta
type Story = StoryObj<typeof BoutonExportCsv>

const sampleData = [
  { nom: 'Poulet', quantite: 1, unite: 'kg' },
  { nom: 'Tomates', quantite: 6, unite: 'pièces' },
  { nom: 'Oignons', quantite: 3, unite: 'pièces' },
]

export const Default: Story = {
  args: {
    data: sampleData,
    filename: 'courses.csv',
  },
}

export const CustomLabel: Story = {
  args: {
    data: sampleData,
    filename: 'recettes.csv',
    label: 'Télécharger les recettes',
  },
}

export const Disabled: Story = {
  args: {
    data: [],
    filename: 'vide.csv',
    disabled: true,
  },
}
