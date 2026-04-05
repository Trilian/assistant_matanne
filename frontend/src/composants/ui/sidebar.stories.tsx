import type { Meta, StoryObj } from '@storybook/react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  SidebarInset,
} from './sidebar'
import { Home, UtensilsCrossed, Users, Wrench } from 'lucide-react'

const meta: Meta<typeof Sidebar> = {
  title: 'UI/Sidebar',
  component: Sidebar,
  decorators: [
    (Story) => (
      <SidebarProvider>
        <Story />
      </SidebarProvider>
    ),
  ],
}

export default meta
type Story = StoryObj<typeof Sidebar>

const menuItems = [
  { titre: 'Accueil', icone: Home, href: '/' },
  { titre: 'Cuisine', icone: UtensilsCrossed, href: '/cuisine' },
  { titre: 'Famille', icone: Users, href: '/famille' },
  { titre: 'Maison', icone: Wrench, href: '/maison' },
]

export const Default: Story = {
  render: () => (
    <div className="flex min-h-[400px]">
      <Sidebar>
        <SidebarHeader className="p-4">
          <h2 className="text-lg font-bold">Matanne</h2>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Navigation</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {menuItems.map((item) => (
                  <SidebarMenuItem key={item.titre}>
                    <SidebarMenuButton>
                      <item.icone className="h-4 w-4" />
                      <span>{item.titre}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter className="p-4">
          <p className="text-xs text-muted-foreground">v1.0</p>
        </SidebarFooter>
      </Sidebar>
      <SidebarInset>
        <header className="flex items-center gap-2 border-b p-4">
          <SidebarTrigger />
          <h1 className="text-sm font-medium">Contenu principal</h1>
        </header>
        <div className="p-4">
          <p className="text-muted-foreground">Zone de contenu de la page.</p>
        </div>
      </SidebarInset>
    </div>
  ),
}
