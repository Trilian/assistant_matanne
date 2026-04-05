import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Switch } from './switch'
import { Label } from './label'

const meta: Meta<typeof Switch> = {
  title: 'UI/Switch',
  component: Switch,
}

export default meta
type Story = StoryObj<typeof Switch>

export const Default: Story = {
  render: () => {
    const [checked, setChecked] = useState(false)
    return <Switch checked={checked} onCheckedChange={setChecked} />
  },
}

export const Checked: Story = {
  render: () => {
    const [checked, setChecked] = useState(true)
    return <Switch checked={checked} onCheckedChange={setChecked} />
  },
}

export const WithLabel: Story = {
  render: () => {
    const [checked, setChecked] = useState(false)
    return (
      <div className="flex items-center space-x-2">
        <Switch id="notifications" checked={checked} onCheckedChange={setChecked} />
        <Label htmlFor="notifications">Notifications activées</Label>
      </div>
    )
  },
}

export const Disabled: Story = {
  render: () => <Switch checked={false} disabled />,
}
