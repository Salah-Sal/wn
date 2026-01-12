import cytoscape from 'cytoscape'
import type { LayoutOptions } from 'cytoscape'
import dagre from 'cytoscape-dagre'
import fcose from 'cytoscape-fcose'
import coseBilkent from 'cytoscape-cose-bilkent'

cytoscape.use(dagre)
cytoscape.use(fcose)
cytoscape.use(coseBilkent)

export const POS_COLORS: Record<string, string> = {
  n: '#3b82f6',
  v: '#22c55e',
  a: '#f97316',
  r: '#a855f7',
  s: '#fb923c',
  default: '#6b7280',
}

export const RELATION_COLORS: Record<string, string> = {
  hypernym: '#1e40af',
  hyponym: '#1e40af',
  instance_hypernym: '#3730a3',
  instance_hyponym: '#3730a3',
  mero_part: '#065f46',
  holo_part: '#065f46',
  mero_member: '#047857',
  holo_member: '#047857',
  similar: '#7c3aed',
  also: '#9ca3af',
  antonym: '#dc2626',
  attribute: '#ca8a04',
  path: '#f59e0b',
  default: '#6b7280',
}

interface StylesheetEntry {
  selector: string
  style: Record<string, unknown>
}

export const graphStylesheet: StylesheetEntry[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#6b7280',
      label: 'data(label)',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '10px',
      'text-margin-y': 5,
      width: 30,
      height: 30,
      'border-width': 2,
      'border-color': '#374151',
      'text-max-width': '100px',
      'text-wrap': 'ellipsis',
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
      width: 40,
      height: 40,
    },
  },
  {
    selector: 'node.center',
    style: {
      width: 45,
      height: 45,
      'border-width': 4,
      'border-color': '#f59e0b',
      'font-weight': 'bold',
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
      'line-color': '#9ca3af',
      'target-arrow-color': '#9ca3af',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      label: 'data(relation)',
      'font-size': '8px',
      'text-rotation': 'autorotate',
      'text-margin-y': -10,
      color: '#6b7280',
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
