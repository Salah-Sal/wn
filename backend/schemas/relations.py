from pydantic import BaseModel
from typing import List, Optional, Dict


class RelatedSynset(BaseModel):
    id: str
    pos: str
    definition: Optional[str] = None
    lemmas: List[str] = []


class RelatedSense(BaseModel):
    id: str
    word_form: str
    synset_id: str


class SynsetRelations(BaseModel):
    synset_id: str
    hypernyms: List[RelatedSynset] = []
    hyponyms: List[RelatedSynset] = []
    holonyms: List[RelatedSynset] = []
    meronyms: List[RelatedSynset] = []
    similar: List[RelatedSynset] = []
    also: List[RelatedSynset] = []
    attributes: List[RelatedSynset] = []
    domain_topics: List[RelatedSynset] = []
    domain_regions: List[RelatedSynset] = []


class SenseRelations(BaseModel):
    sense_id: str
    antonyms: List[RelatedSense] = []
    derivations: List[RelatedSense] = []
    pertainyms: List[RelatedSense] = []
    similar: List[RelatedSense] = []


class HypernymPath(BaseModel):
    path: List[RelatedSynset]
    depth: int
