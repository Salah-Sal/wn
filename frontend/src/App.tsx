import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThreePanelLayout } from '@/layouts/ThreePanelLayout'
import { LexiconManager } from '@/components/LexiconManager'
import { HomePage } from '@/pages/HomePage'
import { SearchPage } from '@/pages/SearchPage'
import { WordPage } from '@/pages/WordPage'
import { SynsetPage } from '@/pages/SynsetPage'
import { SensePage } from '@/pages/SensePage'
import { GraphExplorerPage } from '@/pages/GraphExplorerPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
})

function AppRoutes() {
  return (
    <ThreePanelLayout
      navigation={<LexiconManager />}
      main={
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/word/:id" element={<WordPage />} />
          <Route path="/synset/:id" element={<SynsetPage />} />
          <Route path="/sense/:id" element={<SensePage />} />
          <Route path="/graph" element={<GraphExplorerPage />} />
        </Routes>
      }
    />
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
