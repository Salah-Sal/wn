import { useSearchParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { searchApi, type SearchResult } from '@/api/client'
import { SearchBar } from '@/components/SearchBar'
import { cn } from '@/lib/utils'
import { Loader2, FileText, Layers } from 'lucide-react'

const POS_COLORS: Record<string, string> = {
  n: 'bg-blue-500',
  v: 'bg-green-500',
  a: 'bg-orange-500',
  r: 'bg-purple-500',
  s: 'bg-orange-400',
}

const POS_LABELS: Record<string, string> = {
  n: 'noun',
  v: 'verb',
  a: 'adj',
  r: 'adv',
  s: 'adj',
}

export function SearchPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''
  const pos = searchParams.get('pos') || undefined

  const { data, isLoading, error } = useQuery({
    queryKey: ['search', query, pos],
    queryFn: () => searchApi.search({ q: query, pos, limit: 50 }).then((r) => r.data),
    enabled: !!query,
  })

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <SearchBar />
      </div>

      {query && (
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-[hsl(var(--foreground))]">
            Search results for "{query}"
          </h2>
          {data && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              {data.total} result{data.total !== 1 ? 's' : ''} found
            </p>
          )}
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
        </div>
      )}

      {error && (
        <div className="p-4 rounded-lg bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400">
          Error loading search results. Please try again.
        </div>
      )}

      {data && data.results.length === 0 && (
        <div className="text-center py-12">
          <p className="text-[hsl(var(--muted-foreground))]">
            No results found for "{query}"
          </p>
        </div>
      )}

      {data && data.results.length > 0 && (
        <div className="space-y-2">
          {data.results.map((result) => (
            <SearchResultCard key={result.id} result={result} />
          ))}
        </div>
      )}
    </div>
  )
}

function SearchResultCard({ result }: { result: SearchResult }) {
  const linkPath = result.type === 'word' 
    ? `/word/${encodeURIComponent(result.id)}`
    : `/synset/${encodeURIComponent(result.id)}`

  return (
    <Link
      to={linkPath}
      className="block p-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] hover:border-[hsl(var(--primary))] transition-colors"
    >
      <div className="flex items-start gap-3">
        <div className="mt-1">
          {result.type === 'word' ? (
            <FileText className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
          ) : (
            <Layers className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg font-medium text-[hsl(var(--foreground))]">
              {result.label}
            </span>
            {result.pos && (
              <span
                className={cn(
                  'px-2 py-0.5 text-xs font-medium rounded text-white',
                  POS_COLORS[result.pos] || 'bg-gray-500'
                )}
              >
                {POS_LABELS[result.pos] || result.pos}
              </span>
            )}
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              {result.type}
            </span>
          </div>
          {result.definition && (
            <p className="text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
              {result.definition}
            </p>
          )}
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1 font-mono">
            {result.id}
          </p>
        </div>
      </div>
    </Link>
  )
}
