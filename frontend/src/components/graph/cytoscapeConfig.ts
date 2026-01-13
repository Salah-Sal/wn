import cytoscape from 'cytoscape'
import type { LayoutOptions } from 'cytoscape'
import dagre from 'cytoscape-dagre'
import fcose from 'cytoscape-fcose'
import coseBilkent from 'cytoscape-cose-bilkent'

cytoscape.use(dagre)
cytoscape.use(fcose)
cytoscape.use(coseBilkent)

export const POS_COLORS: Record<string, string> = {
  n: '#4f8fba',
  v: '#5a9a6e',
  a: '#c9884b',
  r: '#9b7bb8',
  s: '#c9884b',
  default: '#7a8694',
}

export const RELATION_COLORS: Record<string, string> = {
  hypernym: '#5b92b8',
  hyponym: '#5b92b8',
  instance_hypernym: '#7b82b8',
  instance_hyponym: '#7b82b8',
  mero_part: '#5aa89a',
  holo_part: '#5aa89a',
  mero_member: '#6aab8a',
  holo_member: '#6aab8a',
  similar: '#9a85c4',
  also: '#8a949e',
  antonym: '#c86464',
  attribute: '#c4a854',
  path: '#d98b4a',
  default: '#8a949e',
}

interface StylesheetEntry {
  selector: string
  style: Record<string, unknown>
}

export const graphStylesheet: StylesheetEntry[] = [
  {
    selector: 'node',
    style: {
      'background-color': '#7a8694',
      label: 'data(label)',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '11px',
      'font-weight': 500,
      'text-margin-y': 6,
      width: 32,
      height: 32,
      'border-width': 2,
      'border-color': '#4a5568',
      'text-max-width': '100px',
      'text-wrap': 'ellipsis',
      color: '#2d3748',
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
      'border-width': 3,
      'border-color': '#d4a84a',
      width: 38,
      height: 38,
    },
  },
  {
    selector: 'node.center',
    style: {
      width: 42,
      height: 42,
      'border-width': 3,
      'border-color': '#d4a84a',
      'font-weight': 600,
    },
  },
  {
    selector: 'node.highlighted',
    style: {
      'background-color': '#d4a84a',
      'border-color': '#b8923a',
    },
  },
  {
    selector: 'edge',
    style: {
      width: 1.5,
      'line-color': '#a0aab4',
      'target-arrow-color': '#a0aab4',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      label: 'data(relation)',
      'font-size': '9px',
      'text-rotation': 'autorotate',
      'text-margin-y': -8,
      color: '#5a6672',
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
      width: 2.5,
    },
  },
  {
    selector: 'edge.highlighted',
    style: {
      'line-color': '#d4a84a',
      'target-arrow-color': '#d4a84a',
      width: 3,
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
