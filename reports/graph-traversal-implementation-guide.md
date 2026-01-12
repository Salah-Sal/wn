# WordNet Graph Traversal UI - Implementation Guide

**Date:** January 2026
**Project:** WordNet Explorer
**Document Type:** Technical Implementation Guide

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Project Setup](#2-project-setup)
3. [Backend Implementation](#3-backend-implementation)
4. [Frontend Implementation](#4-frontend-implementation)
5. [Graph Components](#5-graph-components)
6. [State Management](#6-state-management)
7. [Styling and Theming](#7-styling-and-theming)
8. [Testing](#8-testing)
9. [Performance Optimization](#9-performance-optimization)
10. [Deployment Checklist](#10-deployment-checklist)

---

## 1. Prerequisites

### 1.1 Required Knowledge

- React 18+ with hooks
- TypeScript
- FastAPI (Python)
- Graph theory basics (nodes, edges, traversal)
- CSS/Tailwind CSS

### 1.2 Development Environment

```bash
# Verify installations
node --version    # v18+ required
npm --version     # v9+ required
python --version  # 3.9+ required
```

### 1.3 Existing Project Structure

```
wn/
├── backend/
│   ├── main.py
│   ├── api/
│   │   └── routers/
│   │       ├── lexicons.py
│   │       ├── entities.py
│   │       ├── relations.py
│   │       └── search.py
│   └── core/
│       └── wn_service.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── lib/
│   └── package.json
└── wn/  # Python wn library
```

---

## 2. Project Setup

### 2.1 Install Frontend Dependencies

```bash
cd frontend

# Core graph library
npm install cytoscape@^3.28.0
npm install react-cytoscapejs@^2.0.0

# Layout extensions
npm install cytoscape-dagre@^2.5.0
npm install cytoscape-fcose@^2.2.0
npm install cytoscape-cose-bilkent@^4.1.0

# Tooltip support
npm install cytoscape-popper@^2.0.0
npm install @popperjs/core@^2.11.8

# TypeScript types
npm install -D @types/cytoscape
```

### 2.2 Install Backend Dependencies

```bash
# No additional dependencies needed
# wn package already provides all traversal capabilities
```

### 2.3 Create Directory Structure

```bash
# Frontend directories
mkdir -p frontend/src/components/graph
mkdir -p frontend/src/pages
mkdir -p frontend/src/hooks

# Backend directories
mkdir -p backend/api/routers
```

---

## 3. Backend Implementation

### 3.1 Create Graph Router

Create `backend/api/routers/graph.py`:

```python
"""
Graph-specific API endpoints for visualization.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

import wn

router = APIRouter(prefix="/graph", tags=["graph"])


# =============================================================================
# Pydantic Models
# =============================================================================

class GraphNode(BaseModel):
    """A node in the graph visualization."""
    id: str
    type: str  # 'synset' | 'word' | 'sense'
    label: str
    pos: str
    definition: Optional[str] = None
    lemmas: list[str] = []
    ili: Optional[str] = None


class GraphEdge(BaseModel):
    """An edge in the graph visualization."""
    id: str
    source: str
    target: str
    relation: str
    directed: bool = True


class GraphData(BaseModel):
    """Complete graph data for rendering."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    center_node: str


class PathResult(BaseModel):
    """Result of a path query."""
    source: str
    target: str
    path: list[GraphNode]
    edges: list[GraphEdge]
    length: int


# =============================================================================
# Helper Functions
# =============================================================================

def synset_to_node(synset) -> GraphNode:
    """Convert a wn.Synset to a GraphNode."""
    lemmas = synset.lemmas()[:5]  # Limit to 5 lemmas
    definition = synset.definition()

    return GraphNode(
        id=synset.id(),
        type="synset",
        label=", ".join(lemmas[:3]) if lemmas else synset.id(),
        pos=synset.pos(),
        definition=definition[:200] if definition else None,
        lemmas=lemmas,
        ili=synset.ili().id() if synset.ili() else None
    )


def is_valid_synset(synset) -> bool:
    """Filter out invalid/placeholder synsets."""
    if not synset or not hasattr(synset, 'id'):
        return False
    synset_id = synset.id()
    if not synset_id or synset_id.startswith('*') or '*INFERRED*' in synset_id:
        return False
    return True


def get_synset_relations_as_edges(
    synset,
    relation_types: list[str],
    visited: set[str]
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """
    Get related synsets as graph nodes and edges.

    Args:
        synset: Source synset
        relation_types: List of relation types to include
        visited: Set of already-visited synset IDs

    Returns:
        Tuple of (nodes, edges)
    """
    nodes = []
    edges = []
    edge_counter = 0

    # Define which relations are directed
    directed_relations = {
        'hypernym', 'hyponym', 'instance_hypernym', 'instance_hyponym',
        'mero_part', 'holo_part', 'mero_member', 'holo_member',
        'mero_substance', 'holo_substance', 'causes', 'is_caused_by',
        'entails', 'is_entailed_by', 'domain_topic', 'has_domain_topic'
    }

    source_id = synset.id()

    for rel_type in relation_types:
        try:
            related = synset.get_related(rel_type)
        except Exception:
            continue

        for target in related:
            if not is_valid_synset(target):
                continue

            target_id = target.id()

            # Add node if not visited
            if target_id not in visited:
                nodes.append(synset_to_node(target))
                visited.add(target_id)

            # Add edge
            edge_counter += 1
            edges.append(GraphEdge(
                id=f"e-{source_id}-{rel_type}-{edge_counter}",
                source=source_id,
                target=target_id,
                relation=rel_type,
                directed=rel_type in directed_relations
            ))

    return nodes, edges


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/neighborhood/{synset_id}", response_model=GraphData)
async def get_neighborhood(
    synset_id: str,
    depth: int = Query(default=1, ge=1, le=3),
    relations: Optional[str] = Query(
        default=None,
        description="Comma-separated relation types. Default: all"
    ),
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Get a synset and its neighbors up to N levels deep.

    Returns graph data suitable for visualization.
    """
    # Find the synset
    try:
        synset = wn.synset(synset_id)
    except Exception:
        synset = None

    if not synset:
        raise HTTPException(
            status_code=404,
            detail=f"Synset '{synset_id}' not found"
        )

    # Parse relation types
    if relations:
        relation_types = [r.strip() for r in relations.split(',')]
    else:
        # Default relation types for visualization
        relation_types = [
            'hypernym', 'hyponym',
            'instance_hypernym', 'instance_hyponym',
            'mero_part', 'holo_part',
            'mero_member', 'holo_member',
            'similar', 'also',
            'antonym', 'attribute'
        ]

    # Initialize with center node
    center_node = synset_to_node(synset)
    all_nodes = [center_node]
    all_edges = []
    visited = {synset_id}

    # BFS expansion
    current_level = [synset]

    for level in range(depth):
        next_level = []

        for current_synset in current_level:
            if len(all_nodes) >= limit:
                break

            nodes, edges = get_synset_relations_as_edges(
                current_synset,
                relation_types,
                visited
            )

            # Limit nodes per level
            remaining = limit - len(all_nodes)
            nodes = nodes[:remaining]

            all_nodes.extend(nodes)
            all_edges.extend(edges)

            # Prepare next level
            for node in nodes:
                try:
                    next_synset = wn.synset(node.id)
                    if next_synset:
                        next_level.append(next_synset)
                except Exception:
                    continue

        current_level = next_level

        if len(all_nodes) >= limit:
            break

    return GraphData(
        nodes=all_nodes,
        edges=all_edges,
        center_node=synset_id
    )


@router.get("/path/{source_id}/{target_id}", response_model=PathResult)
async def get_shortest_path(source_id: str, target_id: str):
    """
    Find the shortest path between two synsets.

    Uses hypernym/hyponym relations for path finding.
    """
    try:
        source = wn.synset(source_id)
        target = wn.synset(target_id)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="One or both synsets not found"
        )

    if not source or not target:
        raise HTTPException(
            status_code=404,
            detail="One or both synsets not found"
        )

    # Use wn's shortest_path method
    try:
        path_synsets = source.shortest_path(target, simulate_root=True)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"No path found between synsets: {str(e)}"
        )

    if not path_synsets:
        raise HTTPException(
            status_code=404,
            detail="No path found between the synsets"
        )

    # Convert to graph format
    nodes = [synset_to_node(s) for s in path_synsets if is_valid_synset(s)]

    # Create edges along the path
    edges = []
    for i in range(len(nodes) - 1):
        edges.append(GraphEdge(
            id=f"path-edge-{i}",
            source=nodes[i].id,
            target=nodes[i + 1].id,
            relation="path",
            directed=True
        ))

    return PathResult(
        source=source_id,
        target=target_id,
        path=nodes,
        edges=edges,
        length=len(nodes) - 1
    )


@router.get("/hypernym-tree/{synset_id}", response_model=GraphData)
async def get_hypernym_tree(
    synset_id: str,
    max_depth: int = Query(default=5, ge=1, le=10)
):
    """
    Get all hypernym paths from a synset to root concepts.

    Returns a tree structure for hierarchical visualization.
    """
    try:
        synset = wn.synset(synset_id)
    except Exception:
        synset = None

    if not synset:
        raise HTTPException(
            status_code=404,
            detail=f"Synset '{synset_id}' not found"
        )

    # Get all hypernym paths
    try:
        paths = synset.hypernym_paths(simulate_root=False)
    except Exception:
        paths = []

    if not paths:
        # Return just the synset if no hypernyms
        return GraphData(
            nodes=[synset_to_node(synset)],
            edges=[],
            center_node=synset_id
        )

    # Collect unique nodes and edges
    visited = set()
    all_nodes = []
    all_edges = []
    edge_set = set()  # Avoid duplicate edges

    for path in paths:
        # Limit path depth
        path = path[:max_depth]

        for i, path_synset in enumerate(path):
            if not is_valid_synset(path_synset):
                continue

            sid = path_synset.id()

            # Add node
            if sid not in visited:
                all_nodes.append(synset_to_node(path_synset))
                visited.add(sid)

            # Add edge to next synset
            if i < len(path) - 1:
                next_synset = path[i + 1]
                if is_valid_synset(next_synset):
                    edge_key = (sid, next_synset.id())
                    if edge_key not in edge_set:
                        all_edges.append(GraphEdge(
                            id=f"hyper-{sid}-{next_synset.id()}",
                            source=sid,
                            target=next_synset.id(),
                            relation="hypernym",
                            directed=True
                        ))
                        edge_set.add(edge_key)

    return GraphData(
        nodes=all_nodes,
        edges=all_edges,
        center_node=synset_id
    )


@router.get("/hyponym-tree/{synset_id}", response_model=GraphData)
async def get_hyponym_tree(
    synset_id: str,
    max_depth: int = Query(default=2, ge=1, le=4),
    limit: int = Query(default=100, ge=1, le=500)
):
    """
    Get hyponym subtree from a synset.

    Returns descendants for hierarchical visualization.
    """
    try:
        synset = wn.synset(synset_id)
    except Exception:
        synset = None

    if not synset:
        raise HTTPException(
            status_code=404,
            detail=f"Synset '{synset_id}' not found"
        )

    # BFS to collect hyponyms
    all_nodes = [synset_to_node(synset)]
    all_edges = []
    visited = {synset_id}

    current_level = [synset]

    for depth in range(max_depth):
        if len(all_nodes) >= limit:
            break

        next_level = []

        for current in current_level:
            try:
                hyponyms = current.hyponyms()
            except Exception:
                continue

            for hypo in hyponyms:
                if not is_valid_synset(hypo):
                    continue

                hypo_id = hypo.id()

                if hypo_id not in visited and len(all_nodes) < limit:
                    all_nodes.append(synset_to_node(hypo))
                    visited.add(hypo_id)
                    next_level.append(hypo)

                    all_edges.append(GraphEdge(
                        id=f"hypo-{current.id()}-{hypo_id}",
                        source=current.id(),
                        target=hypo_id,
                        relation="hyponym",
                        directed=True
                    ))

        current_level = next_level

    return GraphData(
        nodes=all_nodes,
        edges=all_edges,
        center_node=synset_id
    )


@router.get("/similarity/{synset_id1}/{synset_id2}")
async def get_similarity(synset_id1: str, synset_id2: str):
    """
    Calculate similarity scores between two synsets.
    """
    from wn import similarity

    try:
        s1 = wn.synset(synset_id1)
        s2 = wn.synset(synset_id2)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="One or both synsets not found"
        )

    if not s1 or not s2:
        raise HTTPException(
            status_code=404,
            detail="One or both synsets not found"
        )

    results = {}

    # Path-based similarity
    try:
        results["path"] = similarity.path(s1, s2, simulate_root=True)
    except Exception:
        results["path"] = None

    # Wu-Palmer similarity
    try:
        results["wup"] = similarity.wup(s1, s2, simulate_root=True)
    except Exception:
        results["wup"] = None

    # Leacock-Chodorow (requires same POS)
    if s1.pos() == s2.pos():
        try:
            # Need to calculate max_depth for the POS
            wordnet = wn.Wordnet()
            from wn.taxonomy import taxonomy_depth
            max_depth = taxonomy_depth(wordnet, s1.pos())
            results["lch"] = similarity.lch(s1, s2, max_depth, simulate_root=True)
        except Exception:
            results["lch"] = None
    else:
        results["lch"] = None

    return {
        "synset1": synset_id1,
        "synset2": synset_id2,
        "similarity": results
    }
```

### 3.2 Register the Router

Update `backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import lexicons, search, entities, relations, graph

app = FastAPI(
    title="WordNet Explorer API",
    description="API for exploring WordNet lexical databases",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(lexicons.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(entities.router, prefix="/api")
app.include_router(relations.router, prefix="/api")
app.include_router(graph.router, prefix="/api")  # Add this line


@app.get("/")
async def root():
    return {"message": "WordNet Explorer API", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 3.3 Test Backend Endpoints

```bash
# Start the backend
python -m uvicorn backend.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/graph/neighborhood/oewn-02084071-n?depth=1
curl http://localhost:8000/api/graph/hypernym-tree/oewn-02084071-n
curl http://localhost:8000/api/graph/path/oewn-02084071-n/oewn-00001740-n
```

---

## 4. Frontend Implementation

### 4.1 TypeScript Types

Create `frontend/src/api/graphTypes.ts`:

```typescript
/**
 * Graph visualization types
 */

export interface GraphNode {
  id: string;
  type: 'synset' | 'word' | 'sense';
  label: string;
  pos: string;
  definition?: string;
  lemmas?: string[];
  ili?: string;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation: string;
  directed: boolean;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  center_node: string;
}

export interface PathResult {
  source: string;
  target: string;
  path: GraphNode[];
  edges: GraphEdge[];
  length: number;
}

export interface SimilarityResult {
  synset1: string;
  synset2: string;
  similarity: {
    path: number | null;
    wup: number | null;
    lch: number | null;
  };
}

// Cytoscape element types
export interface CytoscapeNode {
  data: {
    id: string;
    label: string;
    pos: string;
    definition?: string;
    lemmas?: string[];
    type: string;
  };
  classes?: string;
}

export interface CytoscapeEdge {
  data: {
    id: string;
    source: string;
    target: string;
    relation: string;
  };
  classes?: string;
}

export type CytoscapeElement = CytoscapeNode | CytoscapeEdge;

// Graph state
export interface GraphState {
  elements: CytoscapeElement[];
  centerNodeId: string | null;
  selectedNodeId: string | null;
  expandedNodes: Set<string>;
  layout: 'dagre' | 'fcose' | 'circle' | 'breadthfirst';
  visibleRelations: Set<string>;
}

// Relation categories for filtering
export const RELATION_CATEGORIES = {
  hierarchical: ['hypernym', 'hyponym', 'instance_hypernym', 'instance_hyponym'],
  meronymic: ['mero_part', 'holo_part', 'mero_member', 'holo_member', 'mero_substance', 'holo_substance'],
  semantic: ['similar', 'also', 'antonym', 'attribute'],
  domain: ['domain_topic', 'has_domain_topic', 'domain_region', 'has_domain_region'],
} as const;

export const ALL_RELATIONS = Object.values(RELATION_CATEGORIES).flat();
```

### 4.2 API Client Extensions

Update `frontend/src/api/client.ts`:

```typescript
import axios from 'axios';
import type { GraphData, PathResult, SimilarityResult } from './graphTypes';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ... existing API methods ...

// Graph API
export const graphApi = {
  /**
   * Get neighborhood graph for a synset
   */
  getNeighborhood: (
    synsetId: string,
    options?: {
      depth?: number;
      relations?: string[];
      limit?: number;
    }
  ) => {
    const params = new URLSearchParams();
    if (options?.depth) params.append('depth', options.depth.toString());
    if (options?.relations) params.append('relations', options.relations.join(','));
    if (options?.limit) params.append('limit', options.limit.toString());

    return api.get<GraphData>(
      `/graph/neighborhood/${encodeURIComponent(synsetId)}?${params}`
    );
  },

  /**
   * Get shortest path between two synsets
   */
  getPath: (sourceId: string, targetId: string) =>
    api.get<PathResult>(
      `/graph/path/${encodeURIComponent(sourceId)}/${encodeURIComponent(targetId)}`
    ),

  /**
   * Get hypernym tree (ancestors)
   */
  getHypernymTree: (synsetId: string, maxDepth?: number) => {
    const params = maxDepth ? `?max_depth=${maxDepth}` : '';
    return api.get<GraphData>(
      `/graph/hypernym-tree/${encodeURIComponent(synsetId)}${params}`
    );
  },

  /**
   * Get hyponym tree (descendants)
   */
  getHyponymTree: (synsetId: string, options?: { maxDepth?: number; limit?: number }) => {
    const params = new URLSearchParams();
    if (options?.maxDepth) params.append('max_depth', options.maxDepth.toString());
    if (options?.limit) params.append('limit', options.limit.toString());

    return api.get<GraphData>(
      `/graph/hyponym-tree/${encodeURIComponent(synsetId)}?${params}`
    );
  },

  /**
   * Get similarity scores between two synsets
   */
  getSimilarity: (synsetId1: string, synsetId2: string) =>
    api.get<SimilarityResult>(
      `/graph/similarity/${encodeURIComponent(synsetId1)}/${encodeURIComponent(synsetId2)}`
    ),
};

export default api;
```

---

## 5. Graph Components

### 5.1 Cytoscape Configuration

Create `frontend/src/components/graph/cytoscapeConfig.ts`:

```typescript
import cytoscape, { Stylesheet, LayoutOptions } from 'cytoscape';
import dagre from 'cytoscape-dagre';
import fcose from 'cytoscape-fcose';
import coseBilkent from 'cytoscape-cose-bilkent';

// Register layout extensions
cytoscape.use(dagre);
cytoscape.use(fcose);
cytoscape.use(coseBilkent);

// POS colors matching the app theme
export const POS_COLORS: Record<string, string> = {
  n: '#3b82f6', // blue - noun
  v: '#22c55e', // green - verb
  a: '#f97316', // orange - adjective
  r: '#a855f7', // purple - adverb
  s: '#fb923c', // light orange - adjective satellite
  default: '#6b7280', // gray
};

// Relation colors
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
};

// Cytoscape stylesheet
export const graphStylesheet: Stylesheet[] = [
  // Base node style
  {
    selector: 'node',
    style: {
      'background-color': '#6b7280',
      'label': 'data(label)',
      'text-valign': 'bottom',
      'text-halign': 'center',
      'font-size': '10px',
      'text-margin-y': 5,
      'width': 30,
      'height': 30,
      'border-width': 2,
      'border-color': '#374151',
      'text-max-width': '100px',
      'text-wrap': 'ellipsis',
    },
  },
  // POS-based node colors
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
  // Selected node
  {
    selector: 'node:selected',
    style: {
      'border-width': 4,
      'border-color': '#fbbf24',
      'width': 40,
      'height': 40,
    },
  },
  // Center node (starting point)
  {
    selector: 'node.center',
    style: {
      'width': 45,
      'height': 45,
      'border-width': 4,
      'border-color': '#f59e0b',
      'font-weight': 'bold',
    },
  },
  // Highlighted node (in path)
  {
    selector: 'node.highlighted',
    style: {
      'background-color': '#fbbf24',
      'border-color': '#f59e0b',
    },
  },
  // Base edge style
  {
    selector: 'edge',
    style: {
      'width': 2,
      'line-color': '#9ca3af',
      'target-arrow-color': '#9ca3af',
      'target-arrow-shape': 'triangle',
      'curve-style': 'bezier',
      'label': 'data(relation)',
      'font-size': '8px',
      'text-rotation': 'autorotate',
      'text-margin-y': -10,
      'color': '#6b7280',
    },
  },
  // Relation-specific edge colors
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
      'width': 4,
    },
  },
  // Highlighted edge (in path)
  {
    selector: 'edge.highlighted',
    style: {
      'line-color': '#f59e0b',
      'target-arrow-color': '#f59e0b',
      'width': 4,
    },
  },
];

// Layout configurations
export const layoutConfigs: Record<string, LayoutOptions> = {
  dagre: {
    name: 'dagre',
    rankDir: 'TB', // Top to bottom
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
};
```

### 5.2 Graph Canvas Component

Create `frontend/src/components/graph/GraphCanvas.tsx`:

```tsx
import React, { useRef, useEffect, useCallback } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape, { Core, EventObject } from 'cytoscape';
import { graphStylesheet, layoutConfigs } from './cytoscapeConfig';
import type { CytoscapeElement } from '@/api/graphTypes';

interface GraphCanvasProps {
  elements: CytoscapeElement[];
  layout?: 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent';
  centerNodeId?: string;
  onNodeClick?: (nodeId: string) => void;
  onNodeDoubleClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null, event?: MouseEvent) => void;
  className?: string;
}

export function GraphCanvas({
  elements,
  layout = 'dagre',
  centerNodeId,
  onNodeClick,
  onNodeDoubleClick,
  onNodeHover,
  className = '',
}: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null);

  // Handle Cytoscape instance
  const handleCy = useCallback((cy: Core) => {
    cyRef.current = cy;

    // Node click handler
    cy.on('tap', 'node', (event: EventObject) => {
      const nodeId = event.target.id();
      onNodeClick?.(nodeId);
    });

    // Node double-click handler
    cy.on('dbltap', 'node', (event: EventObject) => {
      const nodeId = event.target.id();
      onNodeDoubleClick?.(nodeId);
    });

    // Node hover handlers
    cy.on('mouseover', 'node', (event: EventObject) => {
      const nodeId = event.target.id();
      onNodeHover?.(nodeId, event.originalEvent as MouseEvent);
    });

    cy.on('mouseout', 'node', () => {
      onNodeHover?.(null);
    });

    // Mark center node
    if (centerNodeId) {
      cy.getElementById(centerNodeId).addClass('center');
    }
  }, [centerNodeId, onNodeClick, onNodeDoubleClick, onNodeHover]);

  // Update layout when it changes
  useEffect(() => {
    if (cyRef.current && elements.length > 0) {
      const layoutConfig = layoutConfigs[layout] || layoutConfigs.dagre;
      cyRef.current.layout(layoutConfig).run();
    }
  }, [layout, elements]);

  // Update center node class
  useEffect(() => {
    if (cyRef.current && centerNodeId) {
      cyRef.current.nodes().removeClass('center');
      cyRef.current.getElementById(centerNodeId).addClass('center');
    }
  }, [centerNodeId]);

  return (
    <CytoscapeComponent
      elements={elements}
      stylesheet={graphStylesheet}
      layout={layoutConfigs[layout] || layoutConfigs.dagre}
      cy={handleCy}
      className={`w-full h-full ${className}`}
      wheelSensitivity={0.3}
      minZoom={0.1}
      maxZoom={3}
      boxSelectionEnabled={false}
      autounselectify={false}
    />
  );
}
```

### 5.3 Graph Controls Component

Create `frontend/src/components/graph/GraphControls.tsx`:

```tsx
import React from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  LayoutGrid,
  GitBranch,
  Circle,
  Layers,
  RotateCcw,
} from 'lucide-react';

type LayoutType = 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent';

interface GraphControlsProps {
  layout: LayoutType;
  onLayoutChange: (layout: LayoutType) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFitView: () => void;
  onReset: () => void;
}

const layouts: { value: LayoutType; label: string; icon: React.ReactNode }[] = [
  { value: 'dagre', label: 'Hierarchical', icon: <GitBranch size={16} /> },
  { value: 'fcose', label: 'Force', icon: <Layers size={16} /> },
  { value: 'circle', label: 'Circle', icon: <Circle size={16} /> },
  { value: 'breadthfirst', label: 'Tree', icon: <LayoutGrid size={16} /> },
];

export function GraphControls({
  layout,
  onLayoutChange,
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
}: GraphControlsProps) {
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2 bg-white/90 dark:bg-gray-800/90 rounded-lg shadow-lg p-2 backdrop-blur-sm">
      {/* Zoom controls */}
      <div className="flex gap-1">
        <button
          onClick={onZoomIn}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Zoom In"
        >
          <ZoomIn size={18} />
        </button>
        <button
          onClick={onZoomOut}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Zoom Out"
        >
          <ZoomOut size={18} />
        </button>
        <button
          onClick={onFitView}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          title="Fit View"
        >
          <Maximize2 size={18} />
        </button>
      </div>

      <hr className="border-gray-200 dark:border-gray-600" />

      {/* Layout selector */}
      <div className="flex flex-col gap-1">
        {layouts.map((l) => (
          <button
            key={l.value}
            onClick={() => onLayoutChange(l.value)}
            className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm ${
              layout === l.value
                ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                : 'hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
            title={l.label}
          >
            {l.icon}
            <span className="hidden sm:inline">{l.label}</span>
          </button>
        ))}
      </div>

      <hr className="border-gray-200 dark:border-gray-600" />

      {/* Reset */}
      <button
        onClick={onReset}
        className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-sm"
        title="Reset Graph"
      >
        <RotateCcw size={16} />
        <span className="hidden sm:inline">Reset</span>
      </button>
    </div>
  );
}
```

### 5.4 Graph Tooltip Component

Create `frontend/src/components/graph/GraphTooltip.tsx`:

```tsx
import React from 'react';
import type { GraphNode } from '@/api/graphTypes';
import { POS_COLORS } from './cytoscapeConfig';

interface GraphTooltipProps {
  node: GraphNode | null;
  position: { x: number; y: number } | null;
}

const POS_LABELS: Record<string, string> = {
  n: 'Noun',
  v: 'Verb',
  a: 'Adjective',
  r: 'Adverb',
  s: 'Adj. Satellite',
};

export function GraphTooltip({ node, position }: GraphTooltipProps) {
  if (!node || !position) return null;

  return (
    <div
      className="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-3 max-w-xs pointer-events-none"
      style={{
        left: position.x + 15,
        top: position.y + 15,
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span
          className="px-2 py-0.5 rounded text-white text-xs font-medium"
          style={{ backgroundColor: POS_COLORS[node.pos] || POS_COLORS.default }}
        >
          {POS_LABELS[node.pos] || node.pos.toUpperCase()}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
          {node.id}
        </span>
      </div>

      {/* Lemmas */}
      {node.lemmas && node.lemmas.length > 0 && (
        <div className="font-medium text-sm mb-1">
          {node.lemmas.slice(0, 5).join(', ')}
          {node.lemmas.length > 5 && (
            <span className="text-gray-400"> +{node.lemmas.length - 5} more</span>
          )}
        </div>
      )}

      {/* Definition */}
      {node.definition && (
        <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
          {node.definition}
        </p>
      )}

      {/* Hint */}
      <p className="text-xs text-gray-400 mt-2 italic">
        Click to expand • Double-click to view details
      </p>
    </div>
  );
}
```

### 5.5 Graph Legend Component

Create `frontend/src/components/graph/GraphLegend.tsx`:

```tsx
import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { POS_COLORS, RELATION_COLORS } from './cytoscapeConfig';

const POS_LABELS: Record<string, string> = {
  n: 'Noun',
  v: 'Verb',
  a: 'Adjective',
  r: 'Adverb',
  s: 'Adj. Satellite',
};

const RELATION_LABELS: Record<string, string> = {
  hypernym: 'Hypernym (IS-A parent)',
  hyponym: 'Hyponym (IS-A child)',
  mero_part: 'Part of',
  holo_part: 'Has part',
  similar: 'Similar',
  antonym: 'Antonym',
  attribute: 'Attribute',
  path: 'Path',
};

export function GraphLegend() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-gray-800/90 rounded-lg shadow-lg backdrop-blur-sm">
      {/* Toggle header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 px-3 py-2 w-full text-sm font-medium"
      >
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        Legend
      </button>

      {/* Legend content */}
      {expanded && (
        <div className="px-3 pb-3 space-y-3">
          {/* Node colors */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
              Node Types (POS)
            </h4>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(POS_LABELS).map(([pos, label]) => (
                <div key={pos} className="flex items-center gap-2 text-xs">
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: POS_COLORS[pos] }}
                  />
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Edge colors */}
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
              Edge Types
            </h4>
            <div className="space-y-1">
              {Object.entries(RELATION_LABELS).map(([rel, label]) => (
                <div key={rel} className="flex items-center gap-2 text-xs">
                  <span
                    className="w-4 h-0.5"
                    style={{ backgroundColor: RELATION_COLORS[rel] || RELATION_COLORS.default }}
                  />
                  <span>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 5.6 Relation Filter Component

Create `frontend/src/components/graph/RelationFilter.tsx`:

```tsx
import React from 'react';
import { Filter } from 'lucide-react';
import { RELATION_CATEGORIES, ALL_RELATIONS } from '@/api/graphTypes';

interface RelationFilterProps {
  visibleRelations: Set<string>;
  onToggleRelation: (relation: string) => void;
  onToggleCategory: (category: keyof typeof RELATION_CATEGORIES) => void;
  onSelectAll: () => void;
  onSelectNone: () => void;
}

const CATEGORY_LABELS: Record<keyof typeof RELATION_CATEGORIES, string> = {
  hierarchical: 'Hierarchical (IS-A)',
  meronymic: 'Part-Whole',
  semantic: 'Semantic',
  domain: 'Domain',
};

export function RelationFilter({
  visibleRelations,
  onToggleRelation,
  onToggleCategory,
  onSelectAll,
  onSelectNone,
}: RelationFilterProps) {
  return (
    <div className="absolute top-4 left-4 bg-white/90 dark:bg-gray-800/90 rounded-lg shadow-lg p-3 backdrop-blur-sm max-w-xs">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 font-medium text-sm">
          <Filter size={16} />
          Relations
        </div>
        <div className="flex gap-2 text-xs">
          <button
            onClick={onSelectAll}
            className="text-blue-600 hover:underline"
          >
            All
          </button>
          <button
            onClick={onSelectNone}
            className="text-blue-600 hover:underline"
          >
            None
          </button>
        </div>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {(Object.entries(RELATION_CATEGORIES) as [keyof typeof RELATION_CATEGORIES, string[]][]).map(
          ([category, relations]) => {
            const allSelected = relations.every((r) => visibleRelations.has(r));
            const someSelected = relations.some((r) => visibleRelations.has(r));

            return (
              <div key={category}>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={allSelected}
                    ref={(el) => {
                      if (el) el.indeterminate = someSelected && !allSelected;
                    }}
                    onChange={() => onToggleCategory(category)}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium">
                    {CATEGORY_LABELS[category]}
                  </span>
                </label>

                <div className="ml-6 mt-1 space-y-1">
                  {relations.map((rel) => (
                    <label
                      key={rel}
                      className="flex items-center gap-2 cursor-pointer text-xs text-gray-600 dark:text-gray-400"
                    >
                      <input
                        type="checkbox"
                        checked={visibleRelations.has(rel)}
                        onChange={() => onToggleRelation(rel)}
                        className="rounded border-gray-300"
                      />
                      {rel.replace(/_/g, ' ')}
                    </label>
                  ))}
                </div>
              </div>
            );
          }
        )}
      </div>
    </div>
  );
}
```

---

## 6. State Management

### 6.1 Graph Store with Zustand

Create `frontend/src/stores/graphStore.ts`:

```typescript
import { create } from 'zustand';
import type { CytoscapeElement, GraphNode, GraphEdge } from '@/api/graphTypes';
import { ALL_RELATIONS } from '@/api/graphTypes';

interface GraphStore {
  // Graph data
  elements: CytoscapeElement[];
  nodeMap: Map<string, GraphNode>;

  // UI state
  centerNodeId: string | null;
  selectedNodeId: string | null;
  hoveredNodeId: string | null;
  hoverPosition: { x: number; y: number } | null;

  // Settings
  layout: 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent';
  visibleRelations: Set<string>;
  expandedNodes: Set<string>;

  // Actions
  setElements: (nodes: GraphNode[], edges: GraphEdge[], centerNodeId: string) => void;
  addElements: (nodes: GraphNode[], edges: GraphEdge[]) => void;
  clearGraph: () => void;

  setSelectedNode: (nodeId: string | null) => void;
  setHoveredNode: (nodeId: string | null, position?: { x: number; y: number }) => void;
  markNodeExpanded: (nodeId: string) => void;

  setLayout: (layout: GraphStore['layout']) => void;
  toggleRelation: (relation: string) => void;
  setVisibleRelations: (relations: string[]) => void;
}

export const useGraphStore = create<GraphStore>((set, get) => ({
  // Initial state
  elements: [],
  nodeMap: new Map(),
  centerNodeId: null,
  selectedNodeId: null,
  hoveredNodeId: null,
  hoverPosition: null,
  layout: 'dagre',
  visibleRelations: new Set(ALL_RELATIONS),
  expandedNodes: new Set(),

  // Set graph elements (replace all)
  setElements: (nodes, edges, centerNodeId) => {
    const nodeMap = new Map<string, GraphNode>();

    const cytoscapeNodes: CytoscapeElement[] = nodes.map((node) => {
      nodeMap.set(node.id, node);
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
      };
    });

    const visibleRelations = get().visibleRelations;
    const cytoscapeEdges: CytoscapeElement[] = edges
      .filter((edge) => visibleRelations.has(edge.relation))
      .map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
        },
      }));

    set({
      elements: [...cytoscapeNodes, ...cytoscapeEdges],
      nodeMap,
      centerNodeId,
      expandedNodes: new Set([centerNodeId]),
    });
  },

  // Add elements (expand)
  addElements: (nodes, edges) => {
    const { elements, nodeMap, visibleRelations } = get();
    const existingIds = new Set(elements.map((el) => el.data.id));

    const newNodes: CytoscapeElement[] = nodes
      .filter((node) => !existingIds.has(node.id))
      .map((node) => {
        nodeMap.set(node.id, node);
        return {
          data: {
            id: node.id,
            label: node.label,
            pos: node.pos,
            definition: node.definition,
            lemmas: node.lemmas,
            type: node.type,
          },
        };
      });

    const newEdges: CytoscapeElement[] = edges
      .filter((edge) => !existingIds.has(edge.id) && visibleRelations.has(edge.relation))
      .map((edge) => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          relation: edge.relation,
        },
      }));

    set({
      elements: [...elements, ...newNodes, ...newEdges],
      nodeMap,
    });
  },

  // Clear graph
  clearGraph: () => {
    set({
      elements: [],
      nodeMap: new Map(),
      centerNodeId: null,
      selectedNodeId: null,
      expandedNodes: new Set(),
    });
  },

  // Selection
  setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),

  // Hover
  setHoveredNode: (nodeId, position) =>
    set({
      hoveredNodeId: nodeId,
      hoverPosition: position || null,
    }),

  // Mark node as expanded
  markNodeExpanded: (nodeId) => {
    const { expandedNodes } = get();
    set({ expandedNodes: new Set([...expandedNodes, nodeId]) });
  },

  // Layout
  setLayout: (layout) => set({ layout }),

  // Relation visibility
  toggleRelation: (relation) => {
    const { visibleRelations } = get();
    const newSet = new Set(visibleRelations);
    if (newSet.has(relation)) {
      newSet.delete(relation);
    } else {
      newSet.add(relation);
    }
    set({ visibleRelations: newSet });
  },

  setVisibleRelations: (relations) => {
    set({ visibleRelations: new Set(relations) });
  },
}));
```

### 6.2 Custom Hook for Graph Data

Create `frontend/src/hooks/useGraphData.ts`:

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { graphApi } from '@/api/client';
import { useGraphStore } from '@/stores/graphStore';
import type { GraphData } from '@/api/graphTypes';

export function useGraphNeighborhood(synsetId: string | null) {
  const setElements = useGraphStore((state) => state.setElements);

  return useQuery({
    queryKey: ['graph', 'neighborhood', synsetId],
    queryFn: async () => {
      if (!synsetId) return null;
      const response = await graphApi.getNeighborhood(synsetId, { depth: 1 });
      return response.data;
    },
    enabled: !!synsetId,
    onSuccess: (data: GraphData | null) => {
      if (data) {
        setElements(data.nodes, data.edges, data.center_node);
      }
    },
  });
}

export function useExpandNode() {
  const addElements = useGraphStore((state) => state.addElements);
  const markNodeExpanded = useGraphStore((state) => state.markNodeExpanded);
  const expandedNodes = useGraphStore((state) => state.expandedNodes);

  return useMutation({
    mutationFn: async (synsetId: string) => {
      if (expandedNodes.has(synsetId)) {
        return null; // Already expanded
      }
      const response = await graphApi.getNeighborhood(synsetId, { depth: 1 });
      return response.data;
    },
    onSuccess: (data: GraphData | null, synsetId: string) => {
      if (data) {
        addElements(data.nodes, data.edges);
        markNodeExpanded(synsetId);
      }
    },
  });
}

export function useGraphPath(sourceId: string | null, targetId: string | null) {
  return useQuery({
    queryKey: ['graph', 'path', sourceId, targetId],
    queryFn: async () => {
      if (!sourceId || !targetId) return null;
      const response = await graphApi.getPath(sourceId, targetId);
      return response.data;
    },
    enabled: !!sourceId && !!targetId,
  });
}

export function useHypernymTree(synsetId: string | null) {
  const setElements = useGraphStore((state) => state.setElements);

  return useQuery({
    queryKey: ['graph', 'hypernym-tree', synsetId],
    queryFn: async () => {
      if (!synsetId) return null;
      const response = await graphApi.getHypernymTree(synsetId, 5);
      return response.data;
    },
    enabled: !!synsetId,
    onSuccess: (data: GraphData | null) => {
      if (data) {
        setElements(data.nodes, data.edges, data.center_node);
      }
    },
  });
}

export function useHyponymTree(synsetId: string | null) {
  const setElements = useGraphStore((state) => state.setElements);

  return useQuery({
    queryKey: ['graph', 'hyponym-tree', synsetId],
    queryFn: async () => {
      if (!synsetId) return null;
      const response = await graphApi.getHyponymTree(synsetId, { maxDepth: 2, limit: 100 });
      return response.data;
    },
    enabled: !!synsetId,
    onSuccess: (data: GraphData | null) => {
      if (data) {
        setElements(data.nodes, data.edges, data.center_node);
      }
    },
  });
}
```

---

## 7. Styling and Theming

### 7.1 Graph Container Styles

Add to `frontend/src/index.css`:

```css
/* Graph container */
.graph-container {
  @apply relative w-full h-full min-h-[500px] bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden;
}

/* Cytoscape canvas overrides */
.graph-canvas {
  @apply w-full h-full;
}

/* Ensure cytoscape fills container */
.graph-canvas > div {
  width: 100% !important;
  height: 100% !important;
}

/* Node selection glow */
.cy-node-selected {
  box-shadow: 0 0 0 4px rgba(251, 191, 36, 0.5);
}

/* Loading overlay */
.graph-loading {
  @apply absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm;
}

/* Empty state */
.graph-empty {
  @apply absolute inset-0 flex flex-col items-center justify-center text-gray-500 dark:text-gray-400;
}
```

### 7.2 Dark Mode Support

The Cytoscape stylesheet in `cytoscapeConfig.ts` uses color variables. For dark mode support, create alternate colors:

```typescript
// Add to cytoscapeConfig.ts

export const darkModeStyles: Stylesheet[] = [
  {
    selector: 'node',
    style: {
      'color': '#e5e7eb', // Light text for dark mode
    },
  },
  {
    selector: 'edge',
    style: {
      'color': '#9ca3af',
    },
  },
];

export function getStylesheet(darkMode: boolean): Stylesheet[] {
  return darkMode
    ? [...graphStylesheet, ...darkModeStyles]
    : graphStylesheet;
}
```

---

## 8. Testing

### 8.1 Backend Tests

Create `backend/tests/test_graph.py`:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_neighborhood_endpoint():
    """Test neighborhood endpoint returns valid graph data."""
    # Assuming oewn is installed
    response = client.get("/api/graph/neighborhood/oewn-02084071-n")

    if response.status_code == 404:
        pytest.skip("Test lexicon not installed")

    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert "center_node" in data
    assert len(data["nodes"]) > 0


def test_neighborhood_depth():
    """Test depth parameter affects result size."""
    response1 = client.get("/api/graph/neighborhood/oewn-02084071-n?depth=1")
    response2 = client.get("/api/graph/neighborhood/oewn-02084071-n?depth=2")

    if response1.status_code == 404:
        pytest.skip("Test lexicon not installed")

    data1 = response1.json()
    data2 = response2.json()

    # Depth 2 should have more or equal nodes
    assert len(data2["nodes"]) >= len(data1["nodes"])


def test_invalid_synset():
    """Test 404 for non-existent synset."""
    response = client.get("/api/graph/neighborhood/nonexistent-synset")
    assert response.status_code == 404


def test_hypernym_tree():
    """Test hypernym tree endpoint."""
    response = client.get("/api/graph/hypernym-tree/oewn-02084071-n")

    if response.status_code == 404:
        pytest.skip("Test lexicon not installed")

    assert response.status_code == 200
    data = response.json()

    # Should have edges only with hypernym relation
    for edge in data["edges"]:
        assert edge["relation"] == "hypernym"
```

### 8.2 Frontend Tests

Create `frontend/src/components/graph/__tests__/GraphCanvas.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { GraphCanvas } from '../GraphCanvas';

const mockElements = [
  {
    data: {
      id: 'node1',
      label: 'Test Node',
      pos: 'n',
      type: 'synset',
    },
  },
  {
    data: {
      id: 'node2',
      label: 'Related Node',
      pos: 'n',
      type: 'synset',
    },
  },
  {
    data: {
      id: 'edge1',
      source: 'node1',
      target: 'node2',
      relation: 'hypernym',
    },
  },
];

describe('GraphCanvas', () => {
  it('renders without crashing', () => {
    render(<GraphCanvas elements={mockElements} />);
  });

  it('renders with center node', () => {
    render(<GraphCanvas elements={mockElements} centerNodeId="node1" />);
  });

  it('calls onNodeClick when node is clicked', () => {
    const handleClick = jest.fn();
    render(<GraphCanvas elements={mockElements} onNodeClick={handleClick} />);
    // Note: Cytoscape events require special handling in tests
  });
});
```

---

## 9. Performance Optimization

### 9.1 Lazy Loading Strategy

```typescript
// In useGraphData.ts

export function useLazyExpand() {
  const expandedNodes = useGraphStore((state) => state.expandedNodes);
  const addElements = useGraphStore((state) => state.addElements);

  const expand = async (nodeId: string) => {
    // Don't re-expand
    if (expandedNodes.has(nodeId)) return;

    // Fetch only if not in cache
    const response = await graphApi.getNeighborhood(nodeId, {
      depth: 1,
      limit: 30, // Limit per expansion
    });

    addElements(response.data.nodes, response.data.edges);
  };

  return { expand };
}
```

### 9.2 Element Limiting

```typescript
// In graphStore.ts

const MAX_NODES = 500;
const MAX_EDGES = 1000;

addElements: (nodes, edges) => {
  const { elements } = get();

  // Count current elements
  const currentNodes = elements.filter(el => !el.data.source).length;
  const currentEdges = elements.filter(el => el.data.source).length;

  // Limit new additions
  const allowedNodes = Math.max(0, MAX_NODES - currentNodes);
  const allowedEdges = Math.max(0, MAX_EDGES - currentEdges);

  const limitedNodes = nodes.slice(0, allowedNodes);
  const limitedEdges = edges.slice(0, allowedEdges);

  // ... rest of addElements
}
```

### 9.3 Virtualization for Large Graphs

For graphs exceeding 500 nodes, consider switching to WebGL rendering:

```typescript
// Install: npm install cytoscape-canvas

import cytoscapeCanvas from 'cytoscape-canvas';
cytoscape.use(cytoscapeCanvas);

// In GraphCanvas.tsx
const handleCy = (cy: Core) => {
  if (elements.length > 500) {
    // Enable WebGL rendering
    const layer = cy.cyCanvas();
    const canvas = layer.getCanvas();
    const ctx = canvas.getContext('2d');
    // Custom WebGL rendering...
  }
};
```

---

## 10. Deployment Checklist

### 10.1 Pre-deployment

- [ ] All tests pass (`pytest` and `npm test`)
- [ ] No TypeScript errors (`npm run build`)
- [ ] Performance tested with 500+ nodes
- [ ] Mobile responsiveness verified
- [ ] Accessibility checked (keyboard navigation)

### 10.2 Backend Deployment

```bash
# Ensure dependencies
pip install -r requirements.txt

# Run with production server
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 10.3 Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Output in dist/ directory
# Serve with nginx/apache or static hosting
```

### 10.4 Environment Variables

```bash
# Backend
WN_DATABASE_PATH=/path/to/wn.db
API_HOST=0.0.0.0
API_PORT=8000

# Frontend (build-time)
VITE_API_URL=https://api.example.com
```

---

## Appendix A: Complete File List

```
backend/
├── api/
│   └── routers/
│       └── graph.py          # NEW: Graph API endpoints
├── main.py                    # UPDATED: Register graph router

frontend/
├── src/
│   ├── api/
│   │   ├── client.ts          # UPDATED: Add graphApi
│   │   └── graphTypes.ts      # NEW: Graph TypeScript types
│   ├── components/
│   │   └── graph/
│   │       ├── GraphCanvas.tsx       # NEW: Main canvas
│   │       ├── GraphControls.tsx     # NEW: Zoom/layout controls
│   │       ├── GraphTooltip.tsx      # NEW: Hover tooltips
│   │       ├── GraphLegend.tsx       # NEW: Color legend
│   │       ├── RelationFilter.tsx    # NEW: Relation filtering
│   │       └── cytoscapeConfig.ts    # NEW: Styles/layouts
│   ├── hooks/
│   │   └── useGraphData.ts    # NEW: Graph data hooks
│   ├── stores/
│   │   └── graphStore.ts      # NEW: Graph state
│   ├── pages/
│   │   └── GraphExplorerPage.tsx  # NEW: Main graph page
│   └── index.css              # UPDATED: Graph styles
├── package.json               # UPDATED: New dependencies
```

---

## Appendix B: Quick Reference

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/graph/neighborhood/{id}` | GET | Get node + neighbors |
| `/api/graph/path/{src}/{tgt}` | GET | Shortest path |
| `/api/graph/hypernym-tree/{id}` | GET | Ancestors tree |
| `/api/graph/hyponym-tree/{id}` | GET | Descendants tree |
| `/api/graph/similarity/{id1}/{id2}` | GET | Similarity scores |

### Key Components

| Component | Purpose |
|-----------|---------|
| `GraphCanvas` | Cytoscape rendering |
| `GraphControls` | Zoom, layout buttons |
| `GraphTooltip` | Hover information |
| `GraphLegend` | Color/symbol key |
| `RelationFilter` | Show/hide relations |

### Store Actions

| Action | Description |
|--------|-------------|
| `setElements` | Replace all graph data |
| `addElements` | Expand with new data |
| `clearGraph` | Reset to empty |
| `setLayout` | Change layout algorithm |
| `toggleRelation` | Show/hide relation type |

---

**End of Implementation Guide**
