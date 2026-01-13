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
  zoomSensitivity?: number
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
  zoomSensitivity = 1,
}: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const zoomSensitivityRef = useRef(zoomSensitivity)

  // Keep ref in sync with prop for use in wheel handler
  useEffect(() => {
    zoomSensitivityRef.current = zoomSensitivity
  }, [zoomSensitivity])

  // Custom wheel zoom handler
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault()
      const cy = cyRef.current
      if (!cy) return

      const sensitivity = zoomSensitivityRef.current
      const zoomFactor = Math.pow(10, -e.deltaY * sensitivity / 500)

      // Zoom centered on cursor position
      const rect = container.getBoundingClientRect()
      cy.zoom({
        level: cy.zoom() * zoomFactor,
        renderedPosition: {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        },
      })
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    return () => container.removeEventListener('wheel', handleWheel)
  }, [])

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
    <div ref={containerRef} className={`w-full h-full ${className}`}>
      <CytoscapeComponent
        elements={elements as never[]}
        stylesheet={graphStylesheet as never[]}
        layout={layoutConfigs[layout] || layoutConfigs.dagre}
        cy={handleCy}
        className="w-full h-full"
        wheelSensitivity={0}
        minZoom={0.1}
        maxZoom={4}
        boxSelectionEnabled={false}
        autounselectify={false}
      />
    </div>
  )
}
