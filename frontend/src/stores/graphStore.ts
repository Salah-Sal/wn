import { create } from 'zustand'
import type { CytoscapeElement, GraphNode, GraphEdge } from '@/api/graphTypes'
import { ALL_RELATIONS } from '@/api/graphTypes'

interface GraphStore {
  elements: CytoscapeElement[]
  nodeMap: Map<string, GraphNode>
  centerNodeId: string | null
  selectedNodeId: string | null
  hoveredNode: GraphNode | null
  hoverPosition: { x: number; y: number } | null
  layout: 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent'
  visibleRelations: Set<string>
  expandedNodes: Set<string>

  setElements: (nodes: GraphNode[], edges: GraphEdge[], centerNodeId: string) => void
  addElements: (nodes: GraphNode[], edges: GraphEdge[]) => void
  clearGraph: () => void
  setSelectedNode: (nodeId: string | null) => void
  setHoveredNode: (node: GraphNode | null, position?: { x: number; y: number }) => void
  markNodeExpanded: (nodeId: string) => void
  setLayout: (layout: GraphStore['layout']) => void
  toggleRelation: (relation: string) => void
  setVisibleRelations: (relations: string[]) => void
}

export const useGraphStore = create<GraphStore>((set, get) => ({
  elements: [],
  nodeMap: new Map(),
  centerNodeId: null,
  selectedNodeId: null,
  hoveredNode: null,
  hoverPosition: null,
  layout: 'dagre',
  visibleRelations: new Set(ALL_RELATIONS),
  expandedNodes: new Set(),

  setElements: (nodes, edges, centerNodeId) => {
    const nodeMap = new Map<string, GraphNode>()

    const cytoscapeNodes: CytoscapeElement[] = nodes.map((node) => {
      nodeMap.set(node.id, node)
      return {
        data: {
          id: node.id,
          label: node.label,
          pos: node.pos,
          definition: node.definition,
          lemmas: node.lemmas,
          type: node.type,
        },
        classes: node.id === centerNodeId ? 'center' : '',
      }
    })

    const visibleRelations = get().visibleRelations
    const cytoscapeEdges: CytoscapeElement[] = edges
      .filter((edge) => visibleRelations.has(edge.relation))
      .map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
        },
      }))

    set({
      elements: [...cytoscapeNodes, ...cytoscapeEdges],
      nodeMap,
      centerNodeId,
      expandedNodes: new Set([centerNodeId]),
    })
  },

  addElements: (nodes, edges) => {
    const { elements, nodeMap, visibleRelations } = get()
    const existingIds = new Set(elements.map((el) => el.data.id))

    const newNodes: CytoscapeElement[] = nodes
      .filter((node) => !existingIds.has(node.id))
      .map((node) => {
        nodeMap.set(node.id, node)
        return {
          data: {
            id: node.id,
            label: node.label,
            pos: node.pos,
            definition: node.definition,
            lemmas: node.lemmas,
            type: node.type,
          },
        }
      })

    const newEdges: CytoscapeElement[] = edges
      .filter((edge) => !existingIds.has(edge.id) && visibleRelations.has(edge.relation))
      .map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
        },
      }))

    set({
      elements: [...elements, ...newNodes, ...newEdges],
      nodeMap,
    })
  },

  clearGraph: () => {
    set({
      elements: [],
      nodeMap: new Map(),
      centerNodeId: null,
      selectedNodeId: null,
      expandedNodes: new Set(),
    })
  },

  setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),

  setHoveredNode: (node, position) =>
    set({
      hoveredNode: node,
      hoverPosition: position || null,
    }),

  markNodeExpanded: (nodeId) => {
    const { expandedNodes } = get()
    set({ expandedNodes: new Set([...expandedNodes, nodeId]) })
  },

  setLayout: (layout) => set({ layout }),

  toggleRelation: (relation) => {
    const { visibleRelations } = get()
    const newSet = new Set(visibleRelations)
    if (newSet.has(relation)) {
      newSet.delete(relation)
    } else {
      newSet.add(relation)
    }
    set({ visibleRelations: newSet })
  },

  setVisibleRelations: (relations) => {
    set({ visibleRelations: new Set(relations) })
  },
}))
