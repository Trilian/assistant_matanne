import type { Meta, StoryObj } from '@storybook/react'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './table'

const meta: Meta<typeof Table> = {
  title: 'UI/Table',
  component: Table,
}

export default meta
type Story = StoryObj<typeof Table>

const recettes = [
  { id: 1, nom: 'Poulet rôti', categorie: 'Plat', temps: '1h30' },
  { id: 2, nom: 'Tarte aux pommes', categorie: 'Dessert', temps: '45min' },
  { id: 3, nom: 'Salade niçoise', categorie: 'Entrée', temps: '15min' },
  { id: 4, nom: 'Gratin dauphinois', categorie: 'Plat', temps: '1h' },
]

export const Default: Story = {
  render: () => (
    <Table>
      <TableCaption>Liste des recettes favorites.</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">ID</TableHead>
          <TableHead>Nom</TableHead>
          <TableHead>Catégorie</TableHead>
          <TableHead className="text-right">Temps</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {recettes.map((r) => (
          <TableRow key={r.id}>
            <TableCell className="font-medium">{r.id}</TableCell>
            <TableCell>{r.nom}</TableCell>
            <TableCell>{r.categorie}</TableCell>
            <TableCell className="text-right">{r.temps}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  ),
}
