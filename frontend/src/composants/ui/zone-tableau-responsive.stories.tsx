import type { Meta, StoryObj } from '@storybook/react'
import { ZoneTableauResponsive } from './zone-tableau-responsive'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './table'

const meta: Meta<typeof ZoneTableauResponsive> = {
  title: 'UI/ZoneTableauResponsive',
  component: ZoneTableauResponsive,
}

export default meta
type Story = StoryObj<typeof ZoneTableauResponsive>

export const Default: Story = {
  render: () => (
    <ZoneTableauResponsive>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Jour</TableHead>
            <TableHead>Petit-déjeuner</TableHead>
            <TableHead>Déjeuner</TableHead>
            <TableHead>Goûter</TableHead>
            <TableHead>Dîner</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">Lundi</TableCell>
            <TableCell>Tartines</TableCell>
            <TableCell>Poulet rôti</TableCell>
            <TableCell>Fruits</TableCell>
            <TableCell>Soupe</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">Mardi</TableCell>
            <TableCell>Céréales</TableCell>
            <TableCell>Pâtes</TableCell>
            <TableCell>Yaourt</TableCell>
            <TableCell>Salade</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </ZoneTableauResponsive>
  ),
}
