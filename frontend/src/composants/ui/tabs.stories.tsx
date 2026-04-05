import type { Meta, StoryObj } from '@storybook/react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from './tabs'

const meta: Meta<typeof Tabs> = {
  title: 'UI/Tabs',
  component: Tabs,
}

export default meta
type Story = StoryObj<typeof Tabs>

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="recettes" className="w-[400px]">
      <TabsList>
        <TabsTrigger value="recettes">Recettes</TabsTrigger>
        <TabsTrigger value="planning">Planning</TabsTrigger>
        <TabsTrigger value="courses">Courses</TabsTrigger>
      </TabsList>
      <TabsContent value="recettes">Liste des recettes ici.</TabsContent>
      <TabsContent value="planning">Planning de la semaine ici.</TabsContent>
      <TabsContent value="courses">Liste de courses ici.</TabsContent>
    </Tabs>
  ),
}

export const Line: Story = {
  render: () => (
    <Tabs defaultValue="jour" className="w-[400px]">
      <TabsList variant="line">
        <TabsTrigger value="jour">Jour</TabsTrigger>
        <TabsTrigger value="semaine">Semaine</TabsTrigger>
        <TabsTrigger value="mois">Mois</TabsTrigger>
      </TabsList>
      <TabsContent value="jour">Vue journalière.</TabsContent>
      <TabsContent value="semaine">Vue hebdomadaire.</TabsContent>
      <TabsContent value="mois">Vue mensuelle.</TabsContent>
    </Tabs>
  ),
}
