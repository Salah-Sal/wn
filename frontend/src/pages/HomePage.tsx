import { SearchBar } from '@/components/SearchBar'
import { useQuery } from '@tanstack/react-query'
import { lexiconApi } from '@/api/client'
import { BookOpen, Search, Share2 } from 'lucide-react'

export function HomePage() {
  const { data: lexiconsData } = useQuery({
    queryKey: ['lexicons'],
    queryFn: () => lexiconApi.list().then((r) => r.data),
  })

  const lexiconCount = lexiconsData?.count || 0

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-[hsl(var(--foreground))] mb-4">
          WordNet Explorer
        </h1>
        <p className="text-lg text-[hsl(var(--muted-foreground))] max-w-xl">
          Browse, search, and analyze lexical semantic databases. 
          Explore word meanings, relationships, and cross-lingual connections.
        </p>
      </div>

      <div className="w-full max-w-2xl mb-12">
        <SearchBar />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl">
        <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))]">
          <BookOpen className="w-8 h-8 text-[hsl(var(--primary))] mb-3" />
          <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">
            Lexicons
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            {lexiconCount} lexicon{lexiconCount !== 1 ? 's' : ''} installed. 
            Browse and manage your WordNet resources.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))]">
          <Search className="w-8 h-8 text-[hsl(var(--primary))] mb-3" />
          <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">
            Search
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Find words, synsets, and senses. Filter by part of speech and language.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))]">
          <Share2 className="w-8 h-8 text-[hsl(var(--primary))] mb-3" />
          <h3 className="text-lg font-semibold text-[hsl(var(--foreground))] mb-2">
            Relations
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Explore hypernyms, hyponyms, and other semantic relationships.
          </p>
        </div>
      </div>

      {lexiconCount === 0 && (
        <div className="mt-8 p-4 rounded-lg bg-[hsl(var(--secondary))] text-center">
          <p className="text-sm text-[hsl(var(--foreground))]">
            No lexicons installed yet. Use the Lexicon Manager in the sidebar to download WordNet data.
          </p>
        </div>
      )}
    </div>
  )
}
