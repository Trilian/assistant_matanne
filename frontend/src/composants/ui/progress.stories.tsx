import type { Meta, StoryObj } from '@storybook/react'
import { Progress } from './progress'

const meta: Meta<typeof Progress> = {
  title: 'UI/Progress',
  component: Progress,
}

export default meta
type Story = StoryObj<typeof Progress>

export const Default: Story = {
  args: {
    value: 60,
    className: 'w-[300px]',
  },
}

export const Empty: Story = {
  args: {
    value: 0,
    className: 'w-[300px]',
  },
}

export const Full: Story = {
  args: {
    value: 100,
    className: 'w-[300px]',
  },
}

export const HalfWay: Story = {
  args: {
    value: 50,
    className: 'w-[300px]',
  },
}
