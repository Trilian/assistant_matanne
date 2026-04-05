import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Switch } from './switch'
import { Label } from './label'

function SwitchStory({ initialChecked = false, withLabel = false }: { initialChecked?: boolean; withLabel?: boolean }) {
  const [checked, setChecked] = useState(initialChecked)

  if (withLabel) {
    return (
      <div className="flex items-center space-x-2">
        <Switch id="notifications" checked={checked} onCheckedChange={setChecked} />
        <Label htmlFor="notifications">Notifications activées</Label>
      </div>
    )
  }

  return <Switch checked={checked} onCheckedChange={setChecked} />
}

const meta: Meta<typeof Switch> = {
  title: 'UI/Switch',
  component: Switch,
}

export default meta
type Story = StoryObj<typeof Switch>

export const Default: Story = {
  render: () => <SwitchStory />,
}

export const Checked: Story = {
  render: () => <SwitchStory initialChecked />,
}

export const WithLabel: Story = {
  render: () => <SwitchStory withLabel />,
}

export const Disabled: Story = {
  render: () => <Switch checked={false} disabled />,
}
