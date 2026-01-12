import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { entityApi, relationsApi } from '@/api/client'
import { Loader2, Copy, Check, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import { BackButton } from '@/components/BackButton'

export function SensePage() {
  const { id } = useParams<{ id: string }>()
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    word: true,
    synset: true,
    examples: true,
    frames: true,
    relations: true,
  })

  const { data: sense, isLoading, error } = useQuery({
    queryKey: ['sense', id],
    queryFn: () => entityApi.getSense(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: relations } = useQuery({
    queryKey: ['sense-relations', id],
    queryFn: () => relationsApi.getSenseRelations(id!).then((r) => r.data),
    enabled: !!id,
  })

  const copyId = async () => {
    if (sense) {
      await navigator.clipboard.writeText(sense.id)
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

  if (error || !sense) {
    return (
      <div className="p-4 rounded-lg bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400">
        Error loading sense. The sense may not exist.
      </div>
    )
  }

  const hasRelations = relations && (
    relations.antonyms.length > 0 ||
    relations.derivations.length > 0 ||
    relations.pertainyms.length > 0 ||
    relations.similar.length > 0
  )

  return (
    <div className="max-w-3xl mx-auto">
      <BackButton />
      <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))] mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {sense.word_form}
              </h1>
              <span className="text-sm text-[hsl(var(--muted-foreground))]">Sense</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
              <span>Lexicon: {sense.lexicon}</span>
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
        <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">{sense.id}</p>
      </div>

      <CollapsibleSection
        title="Word"
        expanded={expandedSections.word}
        onToggle={() => toggleSection('word')}
      >
        <Link
          to={`/word/${encodeURIComponent(sense.word_id)}`}
          className="flex items-center gap-2 text-[hsl(var(--primary))] hover:underline"
        >
          {sense.word_form}
          <ExternalLink className="w-4 h-4" />
        </Link>
      </CollapsibleSection>

      <CollapsibleSection
        title="Synset"
        expanded={expandedSections.synset}
        onToggle={() => toggleSection('synset')}
      >
        <Link
          to={`/synset/${encodeURIComponent(sense.synset_id)}`}
          className="block p-4 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] bg-[hsl(var(--background))]"
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-[hsl(var(--foreground))]">{sense.synset_id}</span>
            <ExternalLink className="w-4 h-4 text-[hsl(var(--primary))]" />
          </div>
          {sense.definition && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">{sense.definition}</p>
          )}
        </Link>
      </CollapsibleSection>

      {sense.examples.length > 0 && (
        <CollapsibleSection
          title="Examples"
          count={sense.examples.length}
          expanded={expandedSections.examples}
          onToggle={() => toggleSection('examples')}
        >
          <ul className="space-y-2">
            {sense.examples.map((example, i) => (
              <li key={i} className="text-[hsl(var(--foreground))] italic">
                "{example}"
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}

      {sense.frames.length > 0 && (
        <CollapsibleSection
          title="Subcategorization Frames"
          count={sense.frames.length}
          expanded={expandedSections.frames}
          onToggle={() => toggleSection('frames')}
        >
          <ul className="space-y-2">
            {sense.frames.map((frame, i) => (
              <li key={i} className="text-[hsl(var(--foreground))] font-mono text-sm">
                {frame}
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}

      {hasRelations && (
        <CollapsibleSection
          title="Sense Relations"
          expanded={expandedSections.relations}
          onToggle={() => toggleSection('relations')}
        >
          <div className="space-y-4">
            {relations!.antonyms.length > 0 && (
              <SenseRelationGroup title="Antonyms" items={relations!.antonyms} />
            )}
            {relations!.derivations.length > 0 && (
              <SenseRelationGroup title="Derivations" items={relations!.derivations} />
            )}
            {relations!.pertainyms.length > 0 && (
              <SenseRelationGroup title="Pertainyms" items={relations!.pertainyms} />
            )}
            {relations!.similar.length > 0 && (
              <SenseRelationGroup title="Similar" items={relations!.similar} />
            )}
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

function SenseRelationGroup({
  title,
  items,
}: {
  title: string
  items: Array<{ id: string; word_form: string; synset_id: string }>
}) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-[hsl(var(--muted-foreground))] mb-2">
        {title} ({items.length})
      </h4>
      <div className="space-y-2">
        {items.map((item) => (
          <Link
            key={item.id}
            to={`/sense/${encodeURIComponent(item.id)}`}
            className="block p-3 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] bg-[hsl(var(--background))]"
          >
            <span className="font-medium text-[hsl(var(--foreground))]">{item.word_form}</span>
            <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">{item.id}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
