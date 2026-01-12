export interface GraphNode {
  id: string
  type: 'synset' | 'word' | 'sense'
  label: string
  pos: string
  definition?: string
  lemmas?: string[]
  ili?: string
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  relation: string
  directed: boolean
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  center_node: string
}

export interface PathResult {
  source: string
  target: string
  path: GraphNode[]
  edges: GraphEdge[]
  length: number
}

export interface SimilarityResult {
  synset1: string
  synset2: string
  similarity: {
    path: number | null
    wup: number | null
    lch: number | null
  }
}

export interface CytoscapeNodeData {
  id: string
  label: string
  pos: string
  definition?: string
  lemmas?: string[]
  type: string
}

export interface CytoscapeEdgeData {
  id: string
  source: string
  target: string
  relation: string
}

export interface CytoscapeNode {
  data: CytoscapeNodeData
  classes?: string
}

export interface CytoscapeEdge {
  data: CytoscapeEdgeData
  classes?: string
}

export type CytoscapeElement = CytoscapeNode | CytoscapeEdge

export interface GraphState {
  elements: CytoscapeElement[]
  centerNodeId: string | null
  selectedNodeId: string | null
  expandedNodes: Set<string>
  layout: 'dagre' | 'fcose' | 'circle' | 'breadthfirst'
  visibleRelations: Set<string>
}

export const RELATION_CATEGORIES = {
  hierarchical: ['hypernym', 'hyponym', 'instance_hypernym', 'instance_hyponym'],
  meronymic: ['mero_part', 'holo_part', 'mero_member', 'holo_member', 'mero_substance', 'holo_substance'],
  semantic: ['similar', 'also', 'antonym', 'attribute'],
  domain: ['domain_topic', 'has_domain_topic', 'domain_region', 'has_domain_region'],
} as const

export const ALL_RELATIONS = Object.values(RELATION_CATEGORIES).flat()
