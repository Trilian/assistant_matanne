import type { Meta, StoryObj } from '@storybook/react'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from './select'

const meta: Meta<typeof Select> = {
  title: 'UI/Select',
  component: Select,
}

export default meta
type Story = StoryObj<typeof Select>

export const Default: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="Catégorie" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Repas</SelectLabel>
          <SelectItem value="entree">Entrée</SelectItem>
          <SelectItem value="plat">Plat</SelectItem>
          <SelectItem value="dessert">Dessert</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  ),
}

export const WithGroups: Story = {
  render: () => (
    <Select>
      <SelectTrigger className="w-[220px]">
        <SelectValue placeholder="Choisir un module" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Cuisine</SelectLabel>
          <SelectItem value="recettes">Recettes</SelectItem>
          <SelectItem value="planning">Planning</SelectItem>
          <SelectItem value="courses">Courses</SelectItem>
        </SelectGroup>
        <SelectGroup>
          <SelectLabel>Famille</SelectLabel>
          <SelectItem value="jules">Jules</SelectItem>
          <SelectItem value="activites">Activités</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  ),
}
