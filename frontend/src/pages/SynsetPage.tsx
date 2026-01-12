import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { entityApi, relationsApi } from '@/api/client'
import { cn } from '@/lib/utils'
import { Loader2, Copy, Check, ChevronDown, ChevronRight } from 'lucide-react'
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

export function SynsetPage() {
  const { id } = useParams<{ id: string }>()
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    definition: true,
    lemmas: true,
    relations: true,
    examples: true,
  })

  const { data: synset, isLoading, error } = useQuery({
    queryKey: ['synset', id],
    queryFn: () => entityApi.getSynset(id!).then((r) => r.data),
    enabled: !!id,
  })

  const { data: relations } = useQuery({
    queryKey: ['synset-relations', id],
    queryFn: () => relationsApi.getSynsetRelations(id!).then((r) => r.data),
    enabled: !!id,
  })

  const copyId = async () => {
    if (synset) {
      await navigator.clipboard.writeText(synset.id)
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

  if (error || !synset) {
    return (
      <div className="p-4 rounded-lg bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400">
        Error loading synset. The synset may not exist.
      </div>
    )
  }

  const hasRelations = relations && (
    relations.hypernyms.length > 0 ||
    relations.hyponyms.length > 0 ||
    relations.holonyms.length > 0 ||
    relations.meronyms.length > 0 ||
    relations.similar.length > 0
  )

  return (
    <div className="max-w-3xl mx-auto">
      <div className="p-6 rounded-xl bg-[hsl(var(--card))] border border-[hsl(var(--border))] mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
                {synset.lemmas.slice(0, 3).join(', ')}
              </h1>
              <span
                className={cn(
                  'px-3 py-1 text-sm font-medium rounded text-white',
                  POS_COLORS[synset.pos] || 'bg-gray-500'
                )}
              >
                {POS_LABELS[synset.pos] || synset.pos}
              </span>
            </div>
            <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
              <span>Lexicon: {synset.lexicon}</span>
              {synset.ili && <span>ILI: {synset.ili}</span>}
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
        <p className="text-xs font-mono text-[hsl(var(--muted-foreground))]">{synset.id}</p>
      </div>

      <CollapsibleSection
        title="Definition"
        expanded={expandedSections.definition}
        onToggle={() => toggleSection('definition')}
      >
        {synset.definition ? (
          <p className="text-[hsl(var(--foreground))]">{synset.definition}</p>
        ) : (
          <p className="text-[hsl(var(--muted-foreground))] italic">No definition available</p>
        )}
      </CollapsibleSection>

      {synset.examples.length > 0 && (
        <CollapsibleSection
          title="Examples"
          count={synset.examples.length}
          expanded={expandedSections.examples}
          onToggle={() => toggleSection('examples')}
        >
          <ul className="space-y-2">
            {synset.examples.map((example, i) => (
              <li key={i} className="text-[hsl(var(--foreground))] italic">
                "{example}"
              </li>
            ))}
          </ul>
        </CollapsibleSection>
      )}

      <CollapsibleSection
        title="Lemmas"
        count={synset.lemmas.length}
        expanded={expandedSections.lemmas}
        onToggle={() => toggleSection('lemmas')}
      >
        <div className="flex flex-wrap gap-2">
          {synset.lemmas.map((lemma, i) => (
            <span
              key={i}
              className="px-3 py-1 rounded-full bg-[hsl(var(--secondary))] text-sm"
            >
              {lemma}
            </span>
          ))}
        </div>
      </CollapsibleSection>

      {hasRelations && (
        <CollapsibleSection
          title="Relations"
          expanded={expandedSections.relations}
          onToggle={() => toggleSection('relations')}
        >
          <div className="space-y-4">
            {relations!.hypernyms.length > 0 && (
              <RelationGroup title="Hypernyms" items={relations!.hypernyms} />
            )}
            {relations!.hyponyms.length > 0 && (
              <RelationGroup title="Hyponyms" items={relations!.hyponyms} />
            )}
            {relations!.holonyms.length > 0 && (
              <RelationGroup title="Holonyms" items={relations!.holonyms} />
            )}
            {relations!.meronyms.length > 0 && (
              <RelationGroup title="Meronyms" items={relations!.meronyms} />
            )}
            {relations!.similar.length > 0 && (
              <RelationGroup title="Similar" items={relations!.similar} />
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

function RelationGroup({
  title,
  items,
}: {
  title: string
  items: Array<{ id: string; pos: string; definition?: string; lemmas: string[] }>
}) {
  return (
    <div>
      <h4 className="text-sm font-semibold text-[hsl(var(--muted-foreground))] mb-2">
        {title} ({items.length})
      </h4>
      <div className="space-y-2">
        {items.slice(0, 10).map((item) => (
          <Link
            key={item.id}
            to={`/synset/${encodeURIComponent(item.id)}`}
            className="block p-3 rounded-lg border border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] bg-[hsl(var(--background))]"
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-[hsl(var(--foreground))]">
                {item.lemmas.slice(0, 3).join(', ')}
              </span>
              <span
                className={cn(
                  'px-2 py-0.5 text-xs font-medium rounded text-white',
                  POS_COLORS[item.pos] || 'bg-gray-500'
                )}
              >
                {item.pos}
              </span>
            </div>
            {item.definition && (
              <p className="text-sm text-[hsl(var(--muted-foreground))] line-clamp-2">
                {item.definition}
              </p>
            )}
          </Link>
        ))}
        {items.length > 10 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            +{items.length - 10} more...
          </p>
        )}
      </div>
    </div>
  )
}
