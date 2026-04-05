import type { Meta, StoryObj } from '@storybook/react'
import { useState } from 'react'
import { Slider } from './slider'

function SliderWithLabelStory() {
  const [value, setValue] = useState([4])

  return (
    <div className="w-[300px] space-y-2">
      <div className="flex justify-between text-sm">
        <span>Portions</span>
        <span className="font-medium">{value[0]}</span>
      </div>
      <Slider value={value} onValueChange={setValue} min={1} max={12} step={1} />
    </div>
  )
}

const meta: Meta<typeof Slider> = {
  title: 'UI/Slider',
  component: Slider,
}

export default meta
type Story = StoryObj<typeof Slider>

export const Default: Story = {
  args: {
    defaultValue: [50],
    max: 100,
    step: 1,
    className: 'w-[300px]',
  },
}

export const Range: Story = {
  args: {
    defaultValue: [25],
    min: 0,
    max: 120,
    step: 5,
    className: 'w-[300px]',
  },
}

export const WithLabel: Story = {
  render: () => <SliderWithLabelStory />,
}
