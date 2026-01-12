import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, X } from 'lucide-react'
import { searchApi, type AutocompleteItem } from '@/api/client'
import { useAppStore } from '@/stores/appStore'
import { cn } from '@/lib/utils'

const POS_OPTIONS = [
  { value: '', label: 'All POS' },
  { value: 'n', label: 'Noun' },
  { value: 'v', label: 'Verb' },
  { value: 'a', label: 'Adjective' },
  { value: 'r', label: 'Adverb' },
]

const POS_COLORS: Record<string, string> = {
  n: 'bg-blue-500',
  v: 'bg-green-500',
  a: 'bg-orange-500',
  r: 'bg-purple-500',
  s: 'bg-orange-400',
}

export function SearchBar() {
  const navigate = useNavigate()
  const { searchQuery, setSearchQuery, posFilter, setPosFilter, addRecentSearch } = useAppStore()
  const [query, setQuery] = useState(searchQuery)
  const [suggestions, setSuggestions] = useState<AutocompleteItem[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (query.length < 1) {
      setSuggestions([])
      return
    }

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    debounceRef.current = setTimeout(async () => {
      try {
        const { data } = await searchApi.autocomplete(query, undefined, 10)
        setSuggestions(data)
      } catch {
        setSuggestions([])
      }
    }, 150)

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [query])

  const handleSearch = (searchTerm?: string) => {
    const term = searchTerm || query
    if (!term.trim()) return
    
    setSearchQuery(term)
    addRecentSearch(term)
    setShowSuggestions(false)
    navigate(`/search?q=${encodeURIComponent(term)}${posFilter ? `&pos=${posFilter}` : ''}`)
  }

  const handleSuggestionClick = (item: AutocompleteItem) => {
    setQuery(item.form)
    setShowSuggestions(false)
    navigate(`/word/${encodeURIComponent(item.id)}`)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.min(prev + 1, suggestions.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.max(prev - 1, -1))
    } else if (e.key === 'Enter') {
      if (selectedIndex >= 0 && suggestions[selectedIndex]) {
        handleSuggestionClick(suggestions[selectedIndex])
      } else {
        handleSearch()
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
  }

  return (
    <div className="relative w-full max-w-2xl">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setShowSuggestions(true)
              setSelectedIndex(-1)
            }}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleKeyDown}
            placeholder="Search words, synsets..."
            className="w-full pl-10 pr-10 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          />
          {query && (
            <button
              onClick={() => {
                setQuery('')
                setSuggestions([])
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-[hsl(var(--secondary))]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <select
          value={posFilter || ''}
          onChange={(e) => setPosFilter(e.target.value || null)}
          className="px-3 py-2 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
        >
          {POS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        <button
          onClick={() => handleSearch()}
          className="px-4 py-2 rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
        >
          Search
        </button>
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-lg shadow-lg max-h-80 overflow-auto">
          {suggestions.map((item, index) => (
            <button
              key={item.id}
              onClick={() => handleSuggestionClick(item)}
              className={cn(
                'w-full px-4 py-2 text-left flex items-center gap-3 hover:bg-[hsl(var(--secondary))]',
                index === selectedIndex && 'bg-[hsl(var(--secondary))]'
              )}
            >
              <span
                className={cn(
                  'px-2 py-0.5 text-xs font-medium rounded text-white',
                  POS_COLORS[item.pos] || 'bg-gray-500'
                )}
              >
                {item.pos}
              </span>
              <span className="flex-1 text-[hsl(var(--foreground))]">{item.form}</span>
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                {item.sense_count} sense{item.sense_count !== 1 ? 's' : ''}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
