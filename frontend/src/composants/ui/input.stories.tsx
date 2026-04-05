import type { Meta, StoryObj } from '@storybook/react'
import { Input } from './input'

const meta: Meta<typeof Input> = {
  title: 'UI/Input',
  component: Input,
  argTypes: {
    type: { control: 'select', options: ['text', 'email', 'password', 'number', 'search'] },
    placeholder: { control: 'text' },
    disabled: { control: 'boolean' },
  },
}

export default meta
type Story = StoryObj<typeof Input>

export const Default: Story = {
  args: { placeholder: 'Saisissez du texte...' },
}

export const Email: Story = {
  args: { type: 'email', placeholder: 'email@exemple.fr' },
}

export const Password: Story = {
  args: { type: 'password', placeholder: 'Mot de passe' },
}

export const Disabled: Story = {
  args: { placeholder: 'Désactivé', disabled: true },
}

export const WithValue: Story = {
  args: { defaultValue: 'Valeur pré-remplie' },
}
