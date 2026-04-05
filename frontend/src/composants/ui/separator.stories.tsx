import type { Meta, StoryObj } from '@storybook/react'
import { Separator } from './separator'

const meta: Meta<typeof Separator> = {
  title: 'UI/Separator',
  component: Separator,
}

export default meta
type Story = StoryObj<typeof Separator>

export const Horizontal: Story = {
  render: () => (
    <div className="w-[300px]">
      <div className="space-y-1">
        <h4 className="text-sm font-medium">Cuisine</h4>
        <p className="text-sm text-muted-foreground">Gestion des recettes et plannings.</p>
      </div>
      <Separator className="my-4" />
      <div className="space-y-1">
        <h4 className="text-sm font-medium">Famille</h4>
        <p className="text-sm text-muted-foreground">Suivi de Jules et activités.</p>
      </div>
    </div>
  ),
}

export const Vertical: Story = {
  render: () => (
    <div className="flex h-5 items-center space-x-4 text-sm">
      <span>Recettes</span>
      <Separator orientation="vertical" />
      <span>Planning</span>
      <Separator orientation="vertical" />
      <span>Courses</span>
    </div>
  ),
}
