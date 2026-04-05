import type { Meta, StoryObj } from '@storybook/react'
import { LienTransition } from './lien-transition'

const meta: Meta<typeof LienTransition> = {
  title: 'UI/LienTransition',
  component: LienTransition,
}

export default meta
type Story = StoryObj<typeof LienTransition>

export const Default: Story = {
  args: {
    href: '/cuisine',
    children: 'Aller à Cuisine',
    className: 'text-primary underline',
  },
}

export const Navigation: Story = {
  render: () => (
    <nav className="flex gap-4">
      <LienTransition href="/cuisine" className="text-sm hover:underline">Cuisine</LienTransition>
      <LienTransition href="/famille" className="text-sm hover:underline">Famille</LienTransition>
      <LienTransition href="/maison" className="text-sm hover:underline">Maison</LienTransition>
    </nav>
  ),
}
