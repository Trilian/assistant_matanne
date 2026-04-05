import type { Meta, StoryObj } from '@storybook/react'
import { SkeletonPage } from './skeleton-page'

const meta: Meta<typeof SkeletonPage> = {
  title: 'UI/SkeletonPage',
  component: SkeletonPage,
}

export default meta
type Story = StoryObj<typeof SkeletonPage>

export const Default: Story = {
  args: {},
}

export const CustomLines: Story = {
  args: {
    lignes: ['h-8 w-48', 'h-4 w-72', 'h-4 w-64', 'h-32 w-full', 'h-4 w-56'],
    ariaLabel: 'Chargement des recettes',
  },
}

export const Compact: Story = {
  args: {
    lignes: ['h-6 w-32', 'h-20 w-full'],
    ariaLabel: 'Chargement',
  },
}
