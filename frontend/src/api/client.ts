import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Lexicon {
  id: string
  version: string
  label: string
  language: string
  license?: string
  url?: string
  email?: string
  citation?: string
}

export interface LexiconDetail extends Lexicon {
  word_count: Record<string, number>
  synset_count: Record<string, number>
  modified: boolean
}

export interface Project {
  id: string
  label: string
  language: string
  versions: string[]
  license?: string
}

export interface SearchResult {
  type: 'word' | 'synset'
  id: string
  label: string
  pos?: string
  definition?: string
}

export interface WordDetail {
  id: string
  pos: string
  lemma: string
  lexicon: string
  forms: string[]
  sense_count: number
  senses: Array<{
    id: string
    synset_id: string
    lexicon: string
  }>
  derived_words: string[]
}

export interface SynsetDetail {
  id: string
  pos: string
  lexicon: string
  ili?: string
  definition?: string
  definitions: string[]
  examples: string[]
  lemmas: string[]
  lexicalized: boolean
}

export interface SenseDetail {
  id: string
  word_id: string
  word_form: string
  synset_id: string
  lexicon: string
  definition?: string
  examples: string[]
  frames: string[]
}

export interface RelatedSynset {
  id: string
  pos: string
  definition?: string
  lemmas: string[]
}

export interface SynsetRelations {
  synset_id: string
  hypernyms: RelatedSynset[]
  hyponyms: RelatedSynset[]
  holonyms: RelatedSynset[]
  meronyms: RelatedSynset[]
  similar: RelatedSynset[]
  also: RelatedSynset[]
  attributes: RelatedSynset[]
  domain_topics: RelatedSynset[]
  domain_regions: RelatedSynset[]
}

export interface RelatedSense {
  id: string
  word_form: string
  synset_id: string
}

export interface SenseRelations {
  sense_id: string
  antonyms: RelatedSense[]
  derivations: RelatedSense[]
  pertainyms: RelatedSense[]
  similar: RelatedSense[]
}

export interface AutocompleteItem {
  form: string
  pos: string
  id: string
  sense_count: number
}

export interface UploadedLexiconInfo {
  id: string
  version: string
  label?: string
  language?: string
}

export interface UploadResponse {
  success: boolean
  message?: string
  error?: string
  lexicons: UploadedLexiconInfo[]
  filename?: string
}

export const lexiconApi = {
  list: () => api.get<{ lexicons: Lexicon[]; count: number }>('/lexicons'),
  get: (spec: string) => api.get<LexiconDetail>(`/lexicons/${spec}`),
  download: (projectId: string) => api.post('/lexicons/download', { project_id: projectId }),
  listProjects: () => api.get<Project[]>('/projects'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<UploadResponse>('/lexicons/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const searchApi = {
  search: (params: {
    q: string
    pos?: string
    lang?: string
    lexicon?: string
    mode?: string
    limit?: number
    offset?: number
  }) => api.get<{ results: SearchResult[]; total: number; query: string }>('/search', { params }),
  autocomplete: (q: string, lang?: string, limit = 10) =>
    api.get<AutocompleteItem[]>('/autocomplete', { params: { q, lang, limit } }),
}

export const entityApi = {
  getWord: (id: string) => api.get<WordDetail>(`/words/${id}`),
  getSynset: (id: string) => api.get<SynsetDetail>(`/synsets/${id}`),
  getSense: (id: string) => api.get<SenseDetail>(`/senses/${id}`),
}

export const relationsApi = {
  getSynsetRelations: (id: string) => api.get<SynsetRelations>(`/synsets/${id}/relations`),
  getHypernyms: (id: string, depth = 1) =>
    api.get<RelatedSynset[]>(`/synsets/${id}/hypernyms`, { params: { depth } }),
  getHyponyms: (id: string, depth = 1) =>
    api.get<RelatedSynset[]>(`/synsets/${id}/hyponyms`, { params: { depth } }),
  getHypernymPaths: (id: string) =>
    api.get<Array<{ path: RelatedSynset[]; depth: number }>>(`/synsets/${id}/hypernym-paths`),
  getSenseRelations: (id: string) => api.get<SenseRelations>(`/senses/${id}/relations`),
}

export default api
