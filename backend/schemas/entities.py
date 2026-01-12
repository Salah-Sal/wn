from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FormInfo(BaseModel):
    value: str
    script: Optional[str] = None


class SenseInfo(BaseModel):
    id: str
    synset_id: str
    lexicon: str


class WordInfo(BaseModel):
    id: str
    pos: str
    lemma: str
    lexicon: str
    forms: List[str] = []
    sense_count: int = 0


class WordDetail(WordInfo):
    senses: List[SenseInfo] = []
    derived_words: List[str] = []


class SynsetInfo(BaseModel):
    id: str
    pos: str
    lexicon: str
    ili: Optional[str] = None
    definition: Optional[str] = None


class SynsetDetail(SynsetInfo):
    definitions: List[str] = []
    examples: List[str] = []
    lemmas: List[str] = []
    lexicalized: bool = True


class SenseDetail(BaseModel):
    id: str
    word_id: str
    word_form: str
    synset_id: str
    lexicon: str
    definition: Optional[str] = None
    examples: List[str] = []
    frames: List[str] = []


class SearchParams(BaseModel):
    q: Optional[str] = None
    pos: Optional[str] = None
    lang: Optional[str] = None
    lexicon: Optional[str] = None
    normalized: bool = False
    lemmatized: bool = False
    limit: int = 50
    offset: int = 0


class SearchResult(BaseModel):
    type: str
    id: str
    label: str
    pos: Optional[str] = None
    definition: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


class AutocompleteItem(BaseModel):
    form: str
    pos: str
    id: str
    sense_count: int
