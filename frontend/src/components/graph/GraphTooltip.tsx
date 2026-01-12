import type { GraphNode } from '@/api/graphTypes'
import { POS_COLORS } from './cytoscapeConfig'

interface GraphTooltipProps {
  node: GraphNode | null
  position: { x: number; y: number } | null
}

const POS_LABELS: Record<string, string> = {
  n: 'Noun',
  v: 'Verb',
  a: 'Adjective',
  r: 'Adverb',
  s: 'Adj. Satellite',
}

export function GraphTooltip({ node, position }: GraphTooltipProps) {
  if (!node || !position) return null

  return (
    <div
      className="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-3 max-w-xs pointer-events-none"
      style={{
        left: position.x + 15,
        top: position.y + 15,
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span
          className="px-2 py-0.5 rounded text-white text-xs font-medium"
          style={{ backgroundColor: POS_COLORS[node.pos] || POS_COLORS.default }}
        >
          {POS_LABELS[node.pos] || node.pos.toUpperCase()}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400 truncate">{node.id}</span>
      </div>

      {node.lemmas && node.lemmas.length > 0 && (
        <div className="font-medium text-sm mb-1">
          {node.lemmas.slice(0, 5).join(', ')}
          {node.lemmas.length > 5 && (
            <span className="text-gray-400"> +{node.lemmas.length - 5} more</span>
          )}
        </div>
      )}

      {node.definition && (
        <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">{node.definition}</p>
      )}

      <p className="text-xs text-gray-400 mt-2 italic">Click to expand / Double-click to view</p>
    </div>
  )
}
