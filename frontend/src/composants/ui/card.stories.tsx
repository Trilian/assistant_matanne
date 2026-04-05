import type { Meta, StoryObj } from '@storybook/react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, CardAction } from './card'
import { Button } from './button'

const meta: Meta<typeof Card> = {
  title: 'UI/Card',
  component: Card,
}

export default meta
type Story = StoryObj<typeof Card>

export const Default: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Titre de la carte</CardTitle>
        <CardDescription>Description de la carte avec du contexte supplémentaire.</CardDescription>
      </CardHeader>
      <CardContent>
        <p>Contenu principal de la carte.</p>
      </CardContent>
      <CardFooter>
        <Button>Action</Button>
      </CardFooter>
    </Card>
  ),
}

export const WithAction: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Recette du jour</CardTitle>
        <CardDescription>Tarte aux légumes de saison</CardDescription>
        <CardAction>
          <Button variant="outline" size="sm">Modifier</Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        <p>Temps de préparation : 30 min</p>
        <p>Cuisson : 45 min</p>
      </CardContent>
    </Card>
  ),
}

export const Simple: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardContent className="pt-6">
        <p>Carte avec contenu uniquement, sans header ni footer.</p>
      </CardContent>
    </Card>
  ),
}
