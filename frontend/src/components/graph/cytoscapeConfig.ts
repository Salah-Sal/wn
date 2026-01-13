import cytoscape from 'cytoscape'
import type { LayoutOptions } from 'cytoscape'
import dagre from 'cytoscape-dagre'
import fcose from 'cytoscape-fcose'
import coseBilkent from 'cytoscape-cose-bilkent'

cytoscape.use(dagre)
cytoscape.use(fcose)
cytoscape.use(coseBilkent)

export const POS_COLORS: Record<string, string> = {
  n: '#2563eb',
  v: '#16a34a',
  a: '#ea580c',
  r: '#9333ea',
  s: '#d97706',
  default: '#64748b',
}

export const RELATION_COLORS: Record<string, string> = {
  hypernym: '#0ea5e9',
  hyponym: '#0ea5e9',
  instance_hypernym: '#6366f1',
  instance_hyponym: '#6366f1',
  mero_part: '#14b8a6',
  holo_part: '#14b8a6',
  mero_member: '#10b981',
  holo_member: '#10b981',
  similar: '#8b5cf6',
  also: '#a1a1aa',
  antonym: '#ef4444',
  attribute: '#eab308',
  path: '#f97316',
  default: '#71717a',
}

interface StylesheetEntry {
  selector: string
  style: Record<string, unknown>
}

export const graphStylesheet: StylesheetEntry[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#64748b',
      label: 'data(label)',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '11px',
      'font-weight': 500,
      'text-margin-y': 6,
      width: 36,
      height: 36,
      'border-width': 3,
      'border-color': '#ffffff',
      'text-max-width': '120px',
      'text-wrap': 'ellipsis',
      'text-outline-color': '#ffffff',
      'text-outline-width': 2,
      color: '#1e293b',
    },
  },
  {
    selector: 'node[pos="n"]',
    style: { 'background-color': POS_COLORS.n },
  },
  {
    selector: 'node[pos="v"]',
    style: { 'background-color': POS_COLORS.v },
  },
  {
    selector: 'node[pos="a"]',
    style: { 'background-color': POS_COLORS.a },
  },
  {
    selector: 'node[pos="r"]',
    style: { 'background-color': POS_COLORS.r },
  },
  {
    selector: 'node[pos="s"]',
    style: { 'background-color': POS_COLORS.s },
  },
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#fbbf24',
      width: 44,
      height: 44,
    },
  },
  {
    selector: 'node.center',
    style: {
      width: 50,
      height: 50,
      'border-width': 4,
      'border-color': '#f59e0b',
      'font-weight': 700,
    },
  },
  {
    selector: 'node.highlighted',
    style: {
      'background-color': '#fbbf24',
      'border-color': '#f59e0b',
    },
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#94a3b8',
      'target-arrow-color': '#94a3b8',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      label: 'data(relation)',
      'font-size': '9px',
      'text-rotation': 'autorotate',
      'text-margin-y': -10,
      color: '#475569',
      'text-outline-color': '#ffffff',
      'text-outline-width': 1.5,
    },
  },
  {
    selector: 'edge[relation="hypernym"], edge[relation="hyponym"]',
    style: {
      'line-color': RELATION_COLORS.hypernym,
      'target-arrow-color': RELATION_COLORS.hypernym,
    },
  },
  {
    selector: 'edge[relation="antonym"]',
    style: {
      'line-color': RELATION_COLORS.antonym,
      'target-arrow-color': RELATION_COLORS.antonym,
      'line-style': 'dashed',
    },
  },
  {
    selector: 'edge[relation="similar"], edge[relation="also"]',
    style: {
      'line-color': RELATION_COLORS.similar,
      'target-arrow-shape': 'none',
      'line-style': 'dotted',
    },
  },
  {
    selector: 'edge[relation="path"]',
    style: {
      'line-color': RELATION_COLORS.path,
      'target-arrow-color': RELATION_COLORS.path,
      width: 4,
    },
  },
  {
    selector: 'edge.highlighted',
    style: {
      'line-color': '#f59e0b',
      'target-arrow-color': '#f59e0b',
      width: 4,
    },
  },
]

export const layoutConfigs: Record<string, LayoutOptions> = {
  dagre: {
    name: 'dagre',
    rankDir: 'TB',
    nodeSep: 50,
    rankSep: 80,
    edgeSep: 10,
    animate: true,
    animationDuration: 300,
  } as LayoutOptions,

  fcose: {
    name: 'fcose',
    quality: 'proof',
    randomize: false,
    animate: true,
    animationDuration: 300,
    nodeDimensionsIncludeLabels: true,
    idealEdgeLength: 100,
    nodeRepulsion: 4500,
    edgeElasticity: 0.45,
  } as LayoutOptions,

  circle: {
    name: 'circle',
    animate: true,
    animationDuration: 300,
    avoidOverlap: true,
    spacingFactor: 1.5,
  } as LayoutOptions,

  breadthfirst: {
    name: 'breadthfirst',
    directed: true,
    animate: true,
    animationDuration: 300,
    spacingFactor: 1.2,
    avoidOverlap: true,
  } as LayoutOptions,

  'cose-bilkent': {
    name: 'cose-bilkent',
    animate: true,
    animationDuration: 300,
    nodeRepulsion: 4500,
    idealEdgeLength: 100,
    edgeElasticity: 0.45,
    nestingFactor: 0.1,
    gravity: 0.25,
    numIter: 2500,
    tile: true,
  } as LayoutOptions,
}
