import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { entityApi } from '@/api/client'
import { cn } from '@/lib/utils'
import { Loader2, Copy, Check, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'
import { useState } from 'react'

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
  a: 'adjective',
  r: 'adverb',
  s: 'adjective satellite',
}

export function WordPage() {
  const { id } = useParams<{ id: string }>()
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    senses: true,
    forms: true,
    derived: true,
  })

  const { data: word, isLoading, error } = useQuery({
    queryKey: ['word', id],
    queryFn: () => entityApi.getWord(id!).then((r) => r.data),
    enabled: !!id,
  })

  const copyId = async () => {
    if (word) {
      await navigator.clipboard.writeText(word.id)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }))
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
      </div>
    )
  }

  if (error || !word) {
    return (
      <div className="p-4 rounded-lg bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400">
        Error loading word. The word may not exist.
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))] mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-[hsl(var(--foreground))]">
                {word.lemma}
              </h1>
              <span
                className={cn(
                  'px-3 py-1 text-sm font-medium rounded text-white',
                  POS_COLORS[word.pos] || 'bg-gray-500'
                )}
              >
                {POS_LABELS[word.pos] || word.pos}
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
              <span>Lexicon: {word.lexicon}</span>
              <span>{word.sense_count} sense{word.sense_count !== 1 ? 's' : ''}</span>
            </div>
          </div>
          <button
            onClick={copyId}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--secondary))] text-sm"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-500" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                Copy ID
              </>
            )}
          </button>
        </div>
        <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">{word.id}</p>
      </div>

      {word.forms.length > 0 && (
        <CollapsibleSection
          title="Forms"
          count={word.forms.length}
          expanded={expandedSections.forms}
          onToggle={() => toggleSection('forms')}
        >
          <div className="flex flex-wrap gap-2">
            {word.forms.map((form, i) => (
              <span
                key={i}
                className="px-3 py-1 rounded-full bg-[hsl(var(--secondary))] text-sm"
              >
                {form}
              </span>
            ))}
          </div>
        </CollapsibleSection>
      )}

      <CollapsibleSection
        title="Senses"
        count={word.senses.length}
        expanded={expandedSections.senses}
        onToggle={() => toggleSection('senses')}
      >
        <div className="space-y-3">
          {word.senses.map((sense, index) => (
            <div
              key={sense.id}
              className="p-4 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--background))]"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-[hsl(var(--foreground))]">
                  {index + 1}. Sense
                </span>
                <Link
                  to={`/synset/${encodeURIComponent(sense.synset_id)}`}
                  className="flex items-center gap-1 text-sm text-[hsl(var(--primary))] hover:underline"
                >
                  View Synset
                  <ExternalLink className="w-3 h-3" />
                </Link>
              </div>
              <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">
                {sense.id}
              </p>
              <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">
                Synset: {sense.synset_id}
              </p>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {word.derived_words.length > 0 && (
        <CollapsibleSection
          title="Derived Words"
          count={word.derived_words.length}
          expanded={expandedSections.derived}
          onToggle={() => toggleSection('derived')}
        >
          <div className="flex flex-wrap gap-2">
            {word.derived_words.map((derivedWord, i) => (
              <span
                key={i}
                className="px-3 py-1 rounded-full bg-[hsl(var(--secondary))] text-sm"
              >
                {derivedWord}
              </span>
            ))}
          </div>
        </CollapsibleSection>
      )}
    </div>
  )
}

function CollapsibleSection({
  title,
  count,
  expanded,
  onToggle,
  children,
}: {
  title: string
  count?: number
  expanded: boolean
  onToggle: () => void
  children: React.ReactNode
}) {
  return (
    <div className="mb-4 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))] overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-[hsl(var(--secondary))]"
      >
        <div className="flex items-center gap-2">
          {expanded ? (
            <ChevronDown className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
          ) : (
            <ChevronRight className="w-5 h-5 text-[hsl(var(--muted-foreground))]" />
          )}
          <span className="font-semibold text-[hsl(var(--foreground))]">{title}</span>
          {count !== undefined && (
            <span className="text-sm text-[hsl(var(--muted-foreground))]">({count})</span>
          )}
        </div>
      </button>
      {expanded && <div className="p-4 pt-0">{children}</div>}
    </div>
  )
}
