import { type ReactNode, useState } from 'react'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight, Menu } from 'lucide-react'
import { Breadcrumbs } from '@/components/Breadcrumbs'

interface ThreePanelLayoutProps {
  navigation: ReactNode
  main: ReactNode
  details?: ReactNode
}

export function ThreePanelLayout({ navigation, main, details }: ThreePanelLayoutProps) {
  const [navCollapsed, setNavCollapsed] = useState(false)
  const [detailsCollapsed, setDetailsCollapsed] = useState(false)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-[hsl(var(--background))]">
      <button
        className="fixed top-4 left-4 z-50 p-2 rounded-lg bg-[hsl(var(--secondary))] lg:hidden"
        onClick={() => setMobileNavOpen(!mobileNavOpen)}
      >
        <Menu className="w-5 h-5" />
      </button>

      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 bg-[hsl(var(--card))] border-r border-[hsl(var(--border))] transition-all duration-300 lg:relative lg:translate-x-0',
          navCollapsed ? 'w-16' : 'w-64',
          mobileNavOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-[hsl(var(--border))]">
            {!navCollapsed && (
              <h1 className="text-lg font-semibold text-[hsl(var(--foreground))]">WordNet Explorer</h1>
            )}
            <button
              onClick={() => setNavCollapsed(!navCollapsed)}
              className="p-1 rounded hover:bg-[hsl(var(--secondary))] hidden lg:block"
            >
              {navCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>
          <div className="flex-1 overflow-auto p-4">{navigation}</div>
        </div>
      </aside>

      {mobileNavOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setMobileNavOpen(false)}
        />
      )}

      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="px-6 pt-4 lg:pl-6 pl-16">
          <Breadcrumbs />
        </div>
        <div className="flex-1 overflow-auto p-6 pt-0 lg:pl-6 pl-16">{main}</div>
      </main>

      {details && (
        <aside
          className={cn(
            'hidden lg:block bg-[hsl(var(--card))] border-l border-[hsl(var(--border))] transition-all duration-300',
            detailsCollapsed ? 'w-12' : 'w-80'
          )}
        >
          <div className="flex flex-col h-full">
            <div className="flex items-center p-4 border-b border-[hsl(var(--border))]">
              <button
                onClick={() => setDetailsCollapsed(!detailsCollapsed)}
                className="p-1 rounded hover:bg-[hsl(var(--secondary))]"
              >
                {detailsCollapsed ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
              </button>
              {!detailsCollapsed && (
                <span className="ml-2 text-sm font-medium text-[hsl(var(--foreground))]">Details</span>
              )}
            </div>
            {!detailsCollapsed && <div className="flex-1 overflow-auto p-4">{details}</div>}
          </div>
        </aside>
      )}
    </div>
  )
}
