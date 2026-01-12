import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { lexiconApi, type Lexicon, type Project } from '@/api/client'
import { useAppStore } from '@/stores/appStore'
import { cn } from '@/lib/utils'
import { BookOpen, Download, ChevronDown, ChevronRight, Loader2, Check } from 'lucide-react'

export function LexiconManager() {
  const queryClient = useQueryClient()
  const { selectedLexicon, setSelectedLexicon } = useAppStore()
  const [showProjects, setShowProjects] = useState(false)

  const { data: lexiconsData, isLoading: loadingLexicons } = useQuery({
    queryKey: ['lexicons'],
    queryFn: () => lexiconApi.list().then((r) => r.data),
  })

  const { data: projectsData, isLoading: loadingProjects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => lexiconApi.listProjects().then((r) => r.data),
    enabled: showProjects,
  })

  const downloadMutation = useMutation({
    mutationFn: (projectId: string) => lexiconApi.download(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lexicons'] })
    },
  })

  const lexicons = lexiconsData?.lexicons || []
  const projects = projectsData || []

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-sm font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-2">
          Installed Lexicons
        </h2>
        {loadingLexicons ? (
          <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading...
          </div>
        ) : lexicons.length === 0 ? (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">No lexicons installed</p>
        ) : (
          <ul className="space-y-1">
            {lexicons.map((lex) => (
              <li key={`${lex.id}:${lex.version}`}>
                <button
                  onClick={() => setSelectedLexicon(lex.id)}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left hover:bg-[hsl(var(--secondary))]',
                    selectedLexicon === lex.id && 'bg-[hsl(var(--secondary))]'
                  )}
                >
                  <BookOpen className="w-4 h-4 text-[hsl(var(--primary))]" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[hsl(var(--foreground))] truncate">
                      {lex.label}
                    </div>
                    <div className="text-xs text-[hsl(var(--muted-foreground))]">
                      {lex.language} · v{lex.version}
                    </div>
                  </div>
                  {selectedLexicon === lex.id && <Check className="w-4 h-4 text-[hsl(var(--primary))]" />}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div>
        <button
          onClick={() => setShowProjects(!showProjects)}
          className="flex items-center gap-2 text-sm font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-2 hover:text-[hsl(var(--foreground))]"
        >
          {showProjects ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          Available Projects
        </button>

        {showProjects && (
          <div className="space-y-1">
            {loadingProjects ? (
              <div className="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
                <Loader2 className="w-4 h-4 animate-spin" />
                Loading projects...
              </div>
            ) : projects.length === 0 ? (
              <p className="text-sm text-[hsl(var(--muted-foreground))]">No projects available</p>
            ) : (
              projects.slice(0, 15).map((proj, index) => (
                <div
                  key={`${proj.id}-${proj.versions[0] || index}`}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[hsl(var(--secondary))]"
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[hsl(var(--foreground))] truncate">
                      {proj.label}
                    </div>
                    <div className="text-xs text-[hsl(var(--muted-foreground))]">
                      {proj.language} · v{proj.versions[0] || '?'}
                    </div>
                  </div>
                  <button
                    onClick={() => downloadMutation.mutate(`${proj.id}:${proj.versions[0]}`)}
                    disabled={downloadMutation.isPending}
                    className="p-1.5 rounded hover:bg-[hsl(var(--background))] disabled:opacity-50"
                    title="Download"
                  >
                    {downloadMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}
