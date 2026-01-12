declare module 'cytoscape-dagre' {
  const ext: cytoscape.Ext
  export default ext
}

declare module 'cytoscape-fcose' {
  const ext: cytoscape.Ext
  export default ext
}

declare module 'cytoscape-cose-bilkent' {
  const ext: cytoscape.Ext
  export default ext
}

declare module 'react-cytoscapejs' {
  import { Component, CSSProperties } from 'react'
  import { Core, Stylesheet, LayoutOptions, ElementDefinition } from 'cytoscape'

  interface CytoscapeComponentProps {
    elements: ElementDefinition[]
    stylesheet?: Stylesheet[]
    layout?: LayoutOptions
    cy?: (cy: Core) => void
    className?: string
    style?: CSSProperties
    wheelSensitivity?: number
    minZoom?: number
    maxZoom?: number
    boxSelectionEnabled?: boolean
    autounselectify?: boolean
    autoungrabify?: boolean
    userZoomingEnabled?: boolean
    userPanningEnabled?: boolean
    pan?: { x: number; y: number }
    zoom?: number
  }

  export default class CytoscapeComponent extends Component<CytoscapeComponentProps> {}
}
