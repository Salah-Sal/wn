"""
Graph-specific API endpoints for visualization.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

import wn

router = APIRouter(prefix="/graph", tags=["graph"])


class GraphNode(BaseModel):
    """A node in the graph visualization."""
    id: str
    type: str
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


def synset_to_node(synset) -> GraphNode:
    """Convert a wn.Synset to a GraphNode."""
    lemmas = synset.lemmas()[:5]
    definition = synset.definition()
    ili_obj = synset.ili
    ili_str = str(ili_obj) if ili_obj else None

    return GraphNode(
        id=synset.id,
        type="synset",
        label=", ".join(lemmas[:3]) if lemmas else synset.id,
        pos=synset.pos,
        definition=definition[:200] if definition else None,
        lemmas=lemmas,
        ili=ili_str
    )


def is_valid_synset(synset) -> bool:
    """Filter out invalid/placeholder synsets."""
    if not synset or not hasattr(synset, 'id'):
        return False
    synset_id = synset.id
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
    """
    nodes = []
    edges = []
    edge_counter = 0

    directed_relations = {
        'hypernym', 'hyponym', 'instance_hypernym', 'instance_hyponym',
        'mero_part', 'holo_part', 'mero_member', 'holo_member',
        'mero_substance', 'holo_substance', 'causes', 'is_caused_by',
        'entails', 'is_entailed_by', 'domain_topic', 'has_domain_topic'
    }

    source_id = synset.id

    for rel_type in relation_types:
        try:
            related = synset.get_related(rel_type)
        except Exception:
            continue

        for target in related:
            if not is_valid_synset(target):
                continue

            target_id = target.id

            if target_id not in visited:
                nodes.append(synset_to_node(target))
                visited.add(target_id)

            edge_counter += 1
            edges.append(GraphEdge(
                id=f"e-{source_id}-{rel_type}-{edge_counter}",
                source=source_id,
                target=target_id,
                relation=rel_type,
                directed=rel_type in directed_relations
            ))

    return nodes, edges


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

    if relations:
        relation_types = [r.strip() for r in relations.split(',')]
    else:
        relation_types = [
            'hypernym', 'hyponym',
            'instance_hypernym', 'instance_hyponym',
            'mero_part', 'holo_part',
            'mero_member', 'holo_member',
            'similar', 'also',
            'antonym', 'attribute'
        ]

    center_node = synset_to_node(synset)
    all_nodes = [center_node]
    all_edges = []
    visited = {synset_id}

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

            remaining = limit - len(all_nodes)
            nodes = nodes[:remaining]

            all_nodes.extend(nodes)
            all_edges.extend(edges)

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

    nodes = [synset_to_node(s) for s in path_synsets if is_valid_synset(s)]

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

    try:
        paths = synset.hypernym_paths(simulate_root=False)
    except Exception:
        paths = []

    if not paths:
        return GraphData(
            nodes=[synset_to_node(synset)],
            edges=[],
            center_node=synset_id
        )

    visited = set()
    all_nodes = []
    all_edges = []
    edge_set = set()

    for path in paths:
        path = path[:max_depth]

        for i, path_synset in enumerate(path):
            if not is_valid_synset(path_synset):
                continue

            sid = path_synset.id

            if sid not in visited:
                all_nodes.append(synset_to_node(path_synset))
                visited.add(sid)

            if i < len(path) - 1:
                next_synset = path[i + 1]
                if is_valid_synset(next_synset):
                    edge_key = (sid, next_synset.id)
                    if edge_key not in edge_set:
                        all_edges.append(GraphEdge(
                            id=f"hyper-{sid}-{next_synset.id}",
                            source=sid,
                            target=next_synset.id,
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

                hypo_id = hypo.id

                if hypo_id not in visited and len(all_nodes) < limit:
                    all_nodes.append(synset_to_node(hypo))
                    visited.add(hypo_id)
                    next_level.append(hypo)

                    all_edges.append(GraphEdge(
                        id=f"hypo-{current.id}-{hypo_id}",
                        source=current.id,
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

    try:
        results["path"] = similarity.path(s1, s2, simulate_root=True)
    except Exception:
        results["path"] = None

    try:
        results["wup"] = similarity.wup(s1, s2, simulate_root=True)
    except Exception:
        results["wup"] = None

    if s1.pos == s2.pos:
        try:
            from wn.taxonomy import taxonomy_depth
            wordnet = wn.Wordnet()
            max_depth = taxonomy_depth(wordnet, s1.pos)
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
