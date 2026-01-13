import { useRef, useEffect, useCallback } from 'react'
import CytoscapeComponent from 'react-cytoscapejs'
import type { Core, EventObject } from 'cytoscape'
import { graphStylesheet, layoutConfigs } from './cytoscapeConfig'
import type { CytoscapeElement } from '@/api/graphTypes'

interface GraphCanvasProps {
  elements: CytoscapeElement[]
  layout?: 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent'
  centerNodeId?: string
  onNodeClick?: (nodeId: string) => void
  onNodeDoubleClick?: (nodeId: string) => void
  onNodeHover?: (nodeId: string | null, event?: MouseEvent) => void
  onCyReady?: (cy: Core) => void
  className?: string
}

export function GraphCanvas({
  elements,
  layout = 'dagre',
  centerNodeId,
  onNodeClick,
  onNodeDoubleClick,
  onNodeHover,
  onCyReady,
  className = '',
}: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null)

  const handleCy = useCallback(
    (cy: Core) => {
      cyRef.current = cy
      onCyReady?.(cy)

      cy.on('tap', 'node', (event: EventObject) => {
        const nodeId = event.target.id()
        onNodeClick?.(nodeId)
      })

      cy.on('dbltap', 'node', (event: EventObject) => {
        const nodeId = event.target.id()
        onNodeDoubleClick?.(nodeId)
      })

      cy.on('mouseover', 'node', (event: EventObject) => {
        const nodeId = event.target.id()
        onNodeHover?.(nodeId, event.originalEvent as MouseEvent)
      })

      cy.on('mouseout', 'node', () => {
        onNodeHover?.(null)
      })

      if (centerNodeId) {
        cy.getElementById(centerNodeId).addClass('center')
      }
    },
    [centerNodeId, onNodeClick, onNodeDoubleClick, onNodeHover, onCyReady]
  )

  useEffect(() => {
    if (cyRef.current && elements.length > 0) {
      const layoutConfig = layoutConfigs[layout] || layoutConfigs.dagre
      cyRef.current.layout(layoutConfig).run()
    }
  }, [layout, elements])

  useEffect(() => {
    if (cyRef.current && centerNodeId) {
      cyRef.current.nodes().removeClass('center')
      cyRef.current.getElementById(centerNodeId).addClass('center')
    }
  }, [centerNodeId])

  return (
    <CytoscapeComponent
      elements={elements as never[]}
      stylesheet={graphStylesheet as never[]}
      layout={layoutConfigs[layout] || layoutConfigs.dagre}
      cy={handleCy}
      className={`w-full h-full ${className}`}
      wheelSensitivity={1}
      minZoom={0.1}
      maxZoom={4}
      boxSelectionEnabled={false}
      autounselectify={false}
    />
  )
}
