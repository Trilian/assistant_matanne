import type { Meta, StoryObj } from '@storybook/react'
import { ItemAnime, variantesFadeIn, variantesPop } from './motion-utils'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge } from './badge'

const meta: Meta<typeof ItemAnime> = {
  title: 'UI/MotionUtils',
  component: ItemAnime,
}

export default meta
type Story = StoryObj<typeof ItemAnime>

const items = ['Poulet', 'Tomates', 'Oignons', 'Ail', 'Huile d\'olive']

export const ListeAnimee: Story = {
  render: () => (
    <AnimatePresence>
      <div className="space-y-2">
        {items.map((item, index) => (
          <ItemAnime key={item} index={index}>
            <div className="rounded-md border p-3 text-sm">{item}</div>
          </ItemAnime>
        ))}
      </div>
    </AnimatePresence>
  ),
}

export const FadeIn: Story = {
  render: () => (
    <motion.div
      variants={variantesFadeIn}
      initial="hidden"
      animate="visible"
      className="rounded-lg border p-4"
    >
      Contenu avec fade-in
    </motion.div>
  ),
}

export const Pop: Story = {
  render: () => (
    <motion.div
      variants={variantesPop}
      initial="hidden"
      animate="visible"
      className="inline-block"
    >
      <Badge>Nouveau !</Badge>
    </motion.div>
  ),
}
