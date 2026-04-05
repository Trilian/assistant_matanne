import type { Meta, StoryObj } from '@storybook/react'
import { Textarea } from './textarea'
import { Label } from './label'

const meta: Meta<typeof Textarea> = {
  title: 'UI/Textarea',
  component: Textarea,
}

export default meta
type Story = StoryObj<typeof Textarea>

export const Default: Story = {
  args: {
    placeholder: 'Décrivez les étapes de la recette...',
  },
}

export const WithLabel: Story = {
  render: () => (
    <div className="grid w-full gap-1.5">
      <Label htmlFor="instructions">Instructions</Label>
      <Textarea id="instructions" placeholder="Étape 1 : Préchauffer le four à 180°C..." />
    </div>
  ),
}

export const Disabled: Story = {
  args: {
    placeholder: 'Non modifiable',
    disabled: true,
    defaultValue: 'Ce champ est en lecture seule.',
  },
}
