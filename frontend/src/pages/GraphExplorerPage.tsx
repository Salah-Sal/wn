import { useState, useCallback, useRef, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import type { Core } from 'cytoscape'
import { GraphCanvas, GraphControls, GraphTooltip, GraphLegend } from '@/components/graph'
import { useGraphStore } from '@/stores/graphStore'
import { useFetchGraphData, useExpandNode } from '@/hooks/useGraphData'
import { BackButton } from '@/components/BackButton'
import { Network, TreeDeciduous, TreePine, Loader2 } from 'lucide-react'

type ViewMode = 'neighborhood' | 'hypernym-tree' | 'hyponym-tree'

export function GraphExplorerPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const synsetId = searchParams.get('synset')
  const initialMode = (searchParams.get('mode') as ViewMode) || 'neighborhood'

  const [viewMode, setViewMode] = useState<ViewMode>(initialMode)
  const [zoomSensitivity, setZoomSensitivity] = useState(1)
  const cyRef = useRef<Core | null>(null)

  const elements = useGraphStore((state) => state.elements)
  const nodeMap = useGraphStore((state) => state.nodeMap)
  const centerNodeId = useGraphStore((state) => state.centerNodeId)
  const layout = useGraphStore((state) => state.layout)
  const setLayout = useGraphStore((state) => state.setLayout)
  const hoveredNode = useGraphStore((state) => state.hoveredNode)
  const hoverPosition = useGraphStore((state) => state.hoverPosition)
  const setHoveredNode = useGraphStore((state) => state.setHoveredNode)
  const clearGraph = useGraphStore((state) => state.clearGraph)

  const fetchGraph = useFetchGraphData()
  const expandNode = useExpandNode()

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      if (viewMode === 'neighborhood') {
        expandNode.mutate(nodeId)
      }
    },
    [viewMode, expandNode]
  )

  const handleNodeDoubleClick = useCallback(
    (nodeId: string) => {
      navigate(`/synset/${encodeURIComponent(nodeId)}`)
    },
    [navigate]
  )

  const handleNodeHover = useCallback(
    (nodeId: string | null, event?: MouseEvent) => {
      if (nodeId) {
        const node = nodeMap.get(nodeId)
        if (node && event) {
          setHoveredNode(node, { x: event.clientX, y: event.clientY })
        }
      } else {
        setHoveredNode(null)
      }
    },
    [nodeMap, setHoveredNode]
  )

  const handleZoomIn = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() * 1.2)
  }, [])

  const handleZoomOut = useCallback(() => {
    cyRef.current?.zoom(cyRef.current.zoom() / 1.2)
  }, [])

  const handleFitView = useCallback(() => {
    cyRef.current?.fit(undefined, 50)
  }, [])

  const handleReset = useCallback(() => {
    if (synsetId) {
      clearGraph()
      fetchGraph.mutate({ type: viewMode, synsetId })
    }
  }, [synsetId, viewMode, clearGraph, fetchGraph])

  const handleModeChange = useCallback(
    (mode: ViewMode) => {
      setViewMode(mode)
      if (synsetId) {
        clearGraph()
        fetchGraph.mutate({ type: mode, synsetId })
      }
    },
    [synsetId, clearGraph, fetchGraph]
  )

  const handleCyReady = useCallback((cy: Core) => {
    cyRef.current = cy
  }, [])

  useEffect(() => {
    if (synsetId && elements.length === 0) {
      fetchGraph.mutate({ type: viewMode, synsetId })
    }
  }, [synsetId])

  if (!synsetId) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <Network className="w-16 h-16 text-gray-400 mb-4" />
        <h2 className="text-xl font-semibold mb-2">No Synset Selected</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Open a synset and click "Explore Graph" to visualize its relationships.
        </p>
        <BackButton />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-4">
          <BackButton />
          <div>
            <h1 className="text-lg font-semibold">Graph Explorer</h1>
            <p className="text-sm text-gray-500">{synsetId}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => handleModeChange('neighborhood')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
              viewMode === 'neighborhood'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <Network size={16} />
            Neighborhood
          </button>
          <button
            onClick={() => handleModeChange('hypernym-tree')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
              viewMode === 'hypernym-tree'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <TreeDeciduous size={16} />
            Hypernyms
          </button>
          <button
            onClick={() => handleModeChange('hyponym-tree')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
              viewMode === 'hyponym-tree'
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <TreePine size={16} />
            Hyponyms
          </button>
        </div>
      </div>

      <div className="relative flex-1 bg-gray-50 dark:bg-gray-900">
        {fetchGraph.isPending && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        )}

        {elements.length === 0 && !fetchGraph.isPending && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-500">
            <Network className="w-12 h-12 mb-2" />
            <p>Loading graph...</p>
          </div>
        )}

        {elements.length > 0 && (
          <GraphCanvas
            elements={elements}
            layout={layout}
            centerNodeId={centerNodeId || undefined}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
            onNodeHover={handleNodeHover}
            onCyReady={handleCyReady}
            zoomSensitivity={zoomSensitivity}
          />
        )}

        <GraphControls
          layout={layout}
          onLayoutChange={setLayout}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onFitView={handleFitView}
          onReset={handleReset}
          zoomSensitivity={zoomSensitivity}
          onZoomSensitivityChange={setZoomSensitivity}
        />

        <GraphLegend />

        <GraphTooltip node={hoveredNode} position={hoverPosition} />
      </div>
    </div>
  )
}
