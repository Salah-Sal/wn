import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { POS_COLORS, RELATION_COLORS } from './cytoscapeConfig'

const POS_LABELS: Record<string, string> = {
  n: 'Noun',
  v: 'Verb',
  a: 'Adjective',
  r: 'Adverb',
  s: 'Adj. Satellite',
}

const RELATION_LABELS: Record<string, string> = {
  hypernym: 'Hypernym (IS-A parent)',
  hyponym: 'Hyponym (IS-A child)',
  mero_part: 'Part of',
  holo_part: 'Has part',
  similar: 'Similar',
  antonym: 'Antonym',
  attribute: 'Attribute',
  path: 'Path',
}

export function GraphLegend() {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-gray-800/90 rounded-lg shadow-lg backdrop-blur-sm z-10">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 px-3 py-2 w-full text-sm font-medium"
      >
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        Legend
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-3">
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Node Types (POS)</h4>
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

          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">Edge Types</h4>
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
  )
}
