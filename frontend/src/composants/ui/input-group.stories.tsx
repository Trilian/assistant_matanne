import type { Meta, StoryObj } from '@storybook/react'
import { InputGroup, InputGroupAddon } from './input-group'
import { Input } from './input'
import { Search, Euro } from 'lucide-react'

const meta: Meta<typeof InputGroup> = {
  title: 'UI/InputGroup',
  component: InputGroup,
}

export default meta
type Story = StoryObj<typeof InputGroup>

export const WithIcon: Story = {
  render: () => (
    <InputGroup className="w-[300px]">
      <InputGroupAddon>
        <Search className="h-4 w-4" />
      </InputGroupAddon>
      <Input placeholder="Rechercher une recette..." />
    </InputGroup>
  ),
}

export const WithSuffix: Story = {
  render: () => (
    <InputGroup className="w-[200px]">
      <Input placeholder="0.00" />
      <InputGroupAddon align="inline-end">
        <Euro className="h-4 w-4" />
      </InputGroupAddon>
    </InputGroup>
  ),
}

export const WithText: Story = {
  render: () => (
    <InputGroup className="w-[300px]">
      <InputGroupAddon>https://</InputGroupAddon>
      <Input placeholder="example.com" />
    </InputGroup>
  ),
}
