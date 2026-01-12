import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface NavigationEntry {
  type: 'word' | 'synset' | 'sense' | 'search'
  id: string
  label: string
}

interface AppState {
  selectedLexicon: string | null
  searchQuery: string
  posFilter: string | null
  history: NavigationEntry[]
  historyIndex: number
  recentSearches: string[]
  
  setSelectedLexicon: (lexicon: string | null) => void
  setSearchQuery: (query: string) => void
  setPosFilter: (pos: string | null) => void
  addToHistory: (entry: NavigationEntry) => void
  goBack: () => NavigationEntry | null
  goForward: () => NavigationEntry | null
  addRecentSearch: (query: string) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      selectedLexicon: null,
      searchQuery: '',
      posFilter: null,
      history: [],
      historyIndex: -1,
      recentSearches: [],

      setSelectedLexicon: (lexicon) => set({ selectedLexicon: lexicon }),
      setSearchQuery: (query) => set({ searchQuery: query }),
      setPosFilter: (pos) => set({ posFilter: pos }),

      addToHistory: (entry) => {
        const { history, historyIndex } = get()
        const newHistory = history.slice(0, historyIndex + 1)
        newHistory.push(entry)
        set({ history: newHistory, historyIndex: newHistory.length - 1 })
      },

      goBack: () => {
        const { history, historyIndex } = get()
        if (historyIndex > 0) {
          set({ historyIndex: historyIndex - 1 })
          return history[historyIndex - 1]
        }
        return null
      },

      goForward: () => {
        const { history, historyIndex } = get()
        if (historyIndex < history.length - 1) {
          set({ historyIndex: historyIndex + 1 })
          return history[historyIndex + 1]
        }
        return null
      },

      addRecentSearch: (query) => {
        const { recentSearches } = get()
        const filtered = recentSearches.filter((s) => s !== query)
        set({ recentSearches: [query, ...filtered].slice(0, 10) })
      },
    }),
    {
      name: 'wordnet-explorer-store',
      partialize: (state) => ({
        selectedLexicon: state.selectedLexicon,
        recentSearches: state.recentSearches,
      }),
    }
  )
)
