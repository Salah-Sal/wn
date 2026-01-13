import { ZoomIn, ZoomOut, Maximize2, GitBranch, Circle, Layers, LayoutGrid, RotateCcw, MousePointer2 } from 'lucide-react'

type LayoutType = 'dagre' | 'fcose' | 'circle' | 'breadthfirst' | 'cose-bilkent'

interface GraphControlsProps {
  layout: LayoutType
  onLayoutChange: (layout: LayoutType) => void
  onZoomIn: () => void
  onZoomOut: () => void
  onFitView: () => void
  onReset: () => void
  zoomSensitivity: number
  onZoomSensitivityChange: (value: number) => void
}

const layouts: { value: LayoutType; label: string; icon: React.ReactNode }[] = [
  { value: 'dagre', label: 'Hierarchical', icon: <GitBranch size={16} /> },
  { value: 'fcose', label: 'Force', icon: <Layers size={16} /> },
  { value: 'circle', label: 'Circle', icon: <Circle size={16} /> },
  { value: 'breadthfirst', label: 'Tree', icon: <LayoutGrid size={16} /> },
]

export function GraphControls({
  layout,
  onLayoutChange,
  onZoomIn,
  onZoomOut,
  onFitView,
  onReset,
  zoomSensitivity,
  onZoomSensitivityChange,
}: GraphControlsProps) {
  return (
    <div className="absolute top-4 right-4 flex flex-col gap-2 bg-white/90 dark:bg-gray-800/90 rounded-lg shadow-lg p-2 backdrop-blur-sm z-10">
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

      <div className="px-1 py-1">
        <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 mb-1">
          <MousePointer2 size={14} />
          <span>Zoom Speed</span>
        </div>
        <input
          type="range"
          min="0.2"
          max="2"
          step="0.1"
          value={zoomSensitivity}
          onChange={(e) => onZoomSensitivityChange(parseFloat(e.target.value))}
          className="w-full h-1.5 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-blue-500"
          title={`Zoom sensitivity: ${(zoomSensitivity ?? 1).toFixed(1)}`}
        />
        <div className="flex justify-between text-[10px] text-gray-400 mt-0.5">
          <span>Slow</span>
          <span>Fast</span>
        </div>
      </div>

      <hr className="border-gray-200 dark:border-gray-600" />

      <button
        onClick={onReset}
        className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-sm"
        title="Reset Graph"
      >
        <RotateCcw size={16} />
        <span className="hidden sm:inline">Reset</span>
      </button>
    </div>
  )
}
