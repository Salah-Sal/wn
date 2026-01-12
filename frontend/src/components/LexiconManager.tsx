import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { lexiconApi } from '@/api/client'
import { useAppStore } from '@/stores/appStore'
import { cn } from '@/lib/utils'
import { BookOpen, Download, ChevronDown, ChevronRight, Loader2, Check, Upload, AlertCircle, Trash2 } from 'lucide-react'

export function LexiconManager() {
  const queryClient = useQueryClient()
  const { selectedLexicon, setSelectedLexicon } = useAppStore()
  const [showProjects, setShowProjects] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

  const uploadMutation = useMutation({
    mutationFn: (file: File) => lexiconApi.upload(file),
    onSuccess: (response) => {
      if (response.data.success) {
        setUploadSuccess(response.data.message || 'Upload successful')
        setUploadError(null)
        queryClient.invalidateQueries({ queryKey: ['lexicons'] })
        setTimeout(() => setUploadSuccess(null), 5000)
      } else {
        setUploadError(response.data.error || 'Upload failed')
        setUploadSuccess(null)
      }
    },
    onError: (error: Error) => {
      setUploadError(error.message || 'Upload failed')
      setUploadSuccess(null)
    },
  })

  const removeMutation = useMutation({
    mutationFn: (lexiconId: string) => lexiconApi.remove(lexiconId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lexicons'] })
      if (selectedLexicon) {
        setSelectedLexicon(null)
      }
    },
  })

  const handleRemove = (e: React.MouseEvent, lexiconId: string) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to remove this lexicon?')) {
      removeMutation.mutate(lexiconId)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadError(null)
      setUploadSuccess(null)
      uploadMutation.mutate(file)
    }
    // Reset input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

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
              <li key={`${lex.id}:${lex.version}`} className="group">
                <div
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[hsl(var(--secondary))]',
                    selectedLexicon === lex.id && 'bg-[hsl(var(--secondary))]'
                  )}
                >
                  <button
                    onClick={() => setSelectedLexicon(lex.id)}
                    className="flex items-center gap-2 flex-1 min-w-0 text-left"
                  >
                    <BookOpen className="w-4 h-4 text-[hsl(var(--primary))] flex-shrink-0" />
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
                  <button
                    onClick={(e) => handleRemove(e, lex.id)}
                    disabled={removeMutation.isPending}
                    className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 transition-opacity disabled:opacity-50"
                    title="Remove lexicon"
                  >
                    {removeMutation.isPending ? (
                      <Loader2 className="w-4 h-4 animate-spin text-[hsl(var(--muted-foreground))]" />
                    ) : (
                      <Trash2 className="w-4 h-4 text-red-500" />
                    )}
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Upload Local WordNet */}
      <div>
        <h2 className="text-sm font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider mb-2">
          Upload Local File
        </h2>
        <input
          ref={fileInputRef}
          type="file"
          accept=".xml,.xml.gz,.gz,application/xml,text/xml,application/gzip"
          onChange={handleFileSelect}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploadMutation.isPending}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg border border-dashed border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:bg-[hsl(var(--secondary))] text-sm transition-colors disabled:opacity-50"
        >
          {uploadMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload WN-LMF File
            </>
          )}
        </button>
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
          Supports .xml and .xml.gz files
        </p>

        {uploadError && (
          <div className="mt-2 p-2 rounded-lg bg-red-50 dark:bg-red-900/20 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-red-600 dark:text-red-400">{uploadError}</p>
          </div>
        )}

        {uploadSuccess && (
          <div className="mt-2 p-2 rounded-lg bg-green-50 dark:bg-green-900/20 flex items-start gap-2">
            <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-green-600 dark:text-green-400">{uploadSuccess}</p>
          </div>
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
