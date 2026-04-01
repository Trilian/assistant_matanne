'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

interface Noeud {
  id: string
  label: string
  categorie: string
}

interface Lien {
  source: string
  target: string
  type: string
}

interface GrapheReseauModulesProps {
  width?: number
  height?: number
}

/**
 * E5 — Graphe Réseau Modules avec D3.js Force Layout
 * Affiche les 21 modules et leurs inter-connections (bridges)
 */
export function GrapheReseauModules({ width = 1000, height = 800 }: GrapheReseauModulesProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current) return

    // Les 21 modules du projet et leurs connections
    const noeuds: Noeud[] = [
      // Cuisine
      { id: 'recettes', label: 'Recettes', categorie: 'cuisine' },
      { id: 'planning', label: 'Planning', categorie: 'cuisine' },
      { id: 'courses', label: 'Courses', categorie: 'cuisine' },
      { id: 'inventaire', label: 'Inventaire', categorie: 'cuisine' },
      { id: 'batch-cooking', label: 'Batch Cooking', categorie: 'cuisine' },
      { id: 'anti-gaspillage', label: 'Anti-gaspillage', categorie: 'cuisine' },

      // Maison
      { id: 'projets', label: 'Projets', categorie: 'maison' },
      { id: 'entretien', label: 'Entretien', categorie: 'maison' },
      { id: 'jardin', label: 'Jardin', categorie: 'maison' },
      { id: 'charges', label: 'Charges', categorie: 'maison' },
      { id: 'energie', label: 'Énergie', categorie: 'maison' },

      // Famille
      { id: 'jules', label: 'Jules', categorie: 'famille' },
      { id: 'activites', label: 'Activités', categorie: 'famille' },
      { id: 'routines', label: 'Routines', categorie: 'famille' },
      { id: 'budget', label: 'Budget', categorie: 'famille' },
      { id: 'weekend', label: 'Weekend', categorie: 'famille' },

      // Jeux
      { id: 'paris', label: 'Paris', categorie: 'jeux' },
      { id: 'loto', label: 'Loto', categorie: 'jeux' },

      // Other
      { id: 'dashboard', label: 'Dashboard', categorie: 'autres' },
      { id: 'notifications', label: 'Notifications', categorie: 'autres' },
      { id: 'ia', label: 'IA', categorie: 'autres' },
    ]

    const liens: Lien[] = [
      // Recettes <-> Planning, Courses, Inventaire
      { source: 'recettes', target: 'planning', type: 'data' },
      { source: 'recettes', target: 'courses', type: 'data' },
      { source: 'recettes', target: 'inventaire', type: 'data' },
      { source: 'recettes', target: 'anti-gaspillage', type: 'data' },

      // Planning <-> Courses, Charge, Weekend
      { source: 'planning', target: 'courses', type: 'data' },
      { source: 'planning', target: 'charges', type: 'data' },
      { source: 'planning', target: 'weekend', type: 'cron' },
      { source: 'planning', target: 'notifications', type: 'alert' },

      // Courses <-> Inventaire, Charges
      { source: 'courses', target: 'inventaire', type: 'data' },
      { source: 'courses', target: 'charges', type: 'cost' },

      // Inventaire <-> Anti-gaspillage
      { source: 'inventaire', target: 'anti-gaspillage', type: 'data' },
      { source: 'inventaire', target: 'batch-cooking', type: 'data' },

      // Maison
      { source: 'projets', target: 'charges', type: 'cost' },
      { source: 'entretien', target: 'charges', type: 'cost' },
      { source: 'jardin', target: 'ia', type: 'suggest' },

      // Famille
      { source: 'jules', target: 'activites', type: 'track' },
      { source: 'jules', target: 'routines', type: 'track' },
      { source: 'activites', target: 'weekend', type: 'plan' },
      { source: 'budget', target: 'charges', type: 'aggregate' },

      // Dashboard aggregates
      { source: 'dashboard', target: 'planning', type: 'display' },
      { source: 'dashboard', target: 'budget', type: 'display' },
      { source: 'dashboard', target: 'jules', type: 'display' },
    ]

    // Créer le SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('style', 'background: linear-gradient(135deg, var(--background), var(--muted) 10%));')

    // Effacer le contenu précédent
    svg.selectAll('*').remove()

    // Créer la simulation de force
    const simulation = d3.forceSimulation(noeuds as any[])
      .force('link', d3.forceLink(liens as any)
        .id((d: any) => d.id)
        .distance(80)
        .strength(0.5))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide(50))

    // Ajouter les liens (edges)
    const link = svg.append('g')
      .selectAll('line')
      .data(liens)
      .enter()
      .append('line')
      .attr('stroke', '#hsl(var(--muted-foreground))')
      .attr('stroke-opacity', 0.5)
      .attr('stroke-width', (d: any) => {
        const widths = { data: 3, cron: 2, alert: 2, cost: 2, suggest: 1.5, track: 2, plan: 1.5, display: 2, aggregate: 2 }
        return widths[d.type as keyof typeof widths] || 2
      })
      .attr('stroke-dasharray', (d: any) => {
        return d.type === 'cron' ? '5,5' : ''
      })

    // Ajouter les labels pour les liens (optionnel)
    const linkLabel = svg.append('g')
      .selectAll('text')
      .data(liens)
      .enter()
      .append('text')
      .text((d: any) => d.type)
      .attr('font-size', '10px')
      .attr('fill', 'hsl(var(--muted-foreground))')
      .attr('opacity', 0.6)

    // Ajouter les noeuds (nodes)
    const node = svg.append('g')
      .selectAll('circle')
      .data(noeuds)
      .enter()
      .append('circle')
      .attr('r', 30)
      .attr('fill', (d: any) => {
        const colors = {
          cuisine: '#f97316',
          maison: '#22c55e',
          famille: '#3b82f6',
          jeux: '#a855f7',
          autres: '#8b5cf6',
        }
        return colors[d.categorie as keyof typeof colors] || '#64748b'
      })
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .attr('opacity', 0.9)
      .call(d3.drag() as any
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('mouseover', function(d: any) {
        d3.select(this).transition().attr('r', 40).attr('stroke-width', 3)
      })
      .on('mouseout', function(d: any) {
        d3.select(this).transition().attr('r', 30).attr('stroke-width', 2)
      })

    // Ajouter les labels des noeuds
    const text = svg.append('g')
      .selectAll('text')
      .data(noeuds)
      .enter()
      .append('text')
      .text((d: any) => d.label)
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#ffffff')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.3em')
      .style('pointer-events', 'none')
      .style('user-select', 'none')

    // Mise à jour de la position des éléments
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      linkLabel
        .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
        .attr('y', (d: any) => (d.source.y + d.target.y) / 2)

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y)

      text
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y)
    })

    // Fonctions de drag
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    return () => {
      simulation.stop()
    }
  }, [width, height])

  return (
    <div className="w-full rounded-lg overflow-hidden border border-border shadow-lg">
      <svg ref={svgRef} className="w-full" style={{ minHeight: '400px' }} />
    </div>
  )
}

export default GrapheReseauModules
