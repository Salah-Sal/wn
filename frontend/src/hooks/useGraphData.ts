import { useQuery, useMutation } from '@tanstack/react-query'
import { graphApi } from '@/api/client'
import { useGraphStore } from '@/stores/graphStore'
import { useEffect } from 'react'
import type { GraphData } from '@/api/graphTypes'

export function useGraphNeighborhood(synsetId: string | null) {
  const setElements = useGraphStore((state) => state.setElements)

  const query = useQuery({
    queryKey: ['graph', 'neighborhood', synsetId],
    queryFn: async () => {
      if (!synsetId) return null
      const response = await graphApi.getNeighborhood(synsetId, { depth: 1 })
      return response.data
    },
    enabled: !!synsetId,
  })

  useEffect(() => {
    if (query.data) {
      setElements(query.data.nodes, query.data.edges, query.data.center_node)
    }
  }, [query.data, setElements])

  return query
}

export function useExpandNode() {
  const addElements = useGraphStore((state) => state.addElements)
  const markNodeExpanded = useGraphStore((state) => state.markNodeExpanded)
  const expandedNodes = useGraphStore((state) => state.expandedNodes)

  return useMutation({
    mutationFn: async (synsetId: string) => {
      if (expandedNodes.has(synsetId)) {
        return null
      }
      const response = await graphApi.getNeighborhood(synsetId, { depth: 1 })
      return { data: response.data, synsetId }
    },
    onSuccess: (result) => {
      if (result?.data) {
        addElements(result.data.nodes, result.data.edges)
        markNodeExpanded(result.synsetId)
      }
    },
  })
}

export function useGraphPath(sourceId: string | null, targetId: string | null) {
  return useQuery({
    queryKey: ['graph', 'path', sourceId, targetId],
    queryFn: async () => {
      if (!sourceId || !targetId) return null
      const response = await graphApi.getPath(sourceId, targetId)
      return response.data
    },
    enabled: !!sourceId && !!targetId,
  })
}

export function useHypernymTree(synsetId: string | null, enabled = true) {
  const setElements = useGraphStore((state) => state.setElements)

  const query = useQuery({
    queryKey: ['graph', 'hypernym-tree', synsetId],
    queryFn: async () => {
      if (!synsetId) return null
      const response = await graphApi.getHypernymTree(synsetId, 5)
      return response.data
    },
    enabled: !!synsetId && enabled,
  })

  useEffect(() => {
    if (query.data && enabled) {
      setElements(query.data.nodes, query.data.edges, query.data.center_node)
    }
  }, [query.data, setElements, enabled])

  return query
}

export function useHyponymTree(synsetId: string | null, enabled = true) {
  const setElements = useGraphStore((state) => state.setElements)

  const query = useQuery({
    queryKey: ['graph', 'hyponym-tree', synsetId],
    queryFn: async () => {
      if (!synsetId) return null
      const response = await graphApi.getHyponymTree(synsetId, { maxDepth: 2, limit: 100 })
      return response.data
    },
    enabled: !!synsetId && enabled,
  })

  useEffect(() => {
    if (query.data && enabled) {
      setElements(query.data.nodes, query.data.edges, query.data.center_node)
    }
  }, [query.data, setElements, enabled])

  return query
}

export function useFetchGraphData() {
  const setElements = useGraphStore((state) => state.setElements)

  return useMutation({
    mutationFn: async ({
      type,
      synsetId,
    }: {
      type: 'neighborhood' | 'hypernym-tree' | 'hyponym-tree'
      synsetId: string
    }): Promise<GraphData | null> => {
      let response
      switch (type) {
        case 'neighborhood':
          response = await graphApi.getNeighborhood(synsetId, { depth: 1 })
          break
        case 'hypernym-tree':
          response = await graphApi.getHypernymTree(synsetId, 5)
          break
        case 'hyponym-tree':
          response = await graphApi.getHyponymTree(synsetId, { maxDepth: 2, limit: 100 })
          break
      }
      return response.data
    },
    onSuccess: (data) => {
      if (data) {
        setElements(data.nodes, data.edges, data.center_node)
      }
    },
  })
}
