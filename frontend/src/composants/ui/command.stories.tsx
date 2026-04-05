import type { Meta, StoryObj } from '@storybook/react'
import {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
} from './command'
import { Smile, Calculator, Calendar } from 'lucide-react'

const meta: Meta<typeof Command> = {
  title: 'UI/Command',
  component: Command,
}

export default meta
type Story = StoryObj<typeof Command>

export const Default: Story = {
  render: () => (
    <Command className="w-[350px] rounded-lg border shadow-md">
      <CommandInput placeholder="Rechercher..." />
      <CommandList>
        <CommandEmpty>Aucun résultat.</CommandEmpty>
        <CommandGroup heading="Suggestions">
          <CommandItem>
            <Calendar className="mr-2 h-4 w-4" />
            <span>Planning</span>
          </CommandItem>
          <CommandItem>
            <Smile className="mr-2 h-4 w-4" />
            <span>Recettes</span>
          </CommandItem>
          <CommandItem>
            <Calculator className="mr-2 h-4 w-4" />
            <span>Budget</span>
          </CommandItem>
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Paramètres">
          <CommandItem>Profil</CommandItem>
          <CommandItem>Préférences</CommandItem>
        </CommandGroup>
      </CommandList>
    </Command>
  ),
}
