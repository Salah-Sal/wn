from fastapi import APIRouter, HTTPException
from backend.core.wn_service import get_wn_service
from backend.schemas.entities import (
    WordInfo, WordDetail, SynsetInfo, SynsetDetail, SenseDetail, SenseInfo
)
from typing import List

router = APIRouter()
wn_service = get_wn_service()


def word_to_detail(word) -> WordDetail:
    senses = []
    for sense in word.senses():
        senses.append(SenseInfo(
            id=sense.id(),
            synset_id=sense.synset().id(),
            lexicon=sense.lexicon().id()
        ))
    
    derived = []
    for sense in word.senses():
        for rel_type, related_senses in sense.relations().items():
            if rel_type == 'derivation':
                for rel_sense in related_senses:
                    derived.append(rel_sense.word().lemma())
    
    return WordDetail(
        id=word.id(),
        pos=word.pos(),
        lemma=word.lemma(),
        lexicon=word.lexicon().id(),
        forms=[f.form() for f in word.forms()],
        sense_count=len(word.senses()),
        senses=senses,
        derived_words=list(set(derived))
    )


def synset_to_detail(synset) -> SynsetDetail:
    return SynsetDetail(
        id=synset.id(),
        pos=synset.pos(),
        lexicon=synset.lexicon().id(),
        ili=synset.ili() if synset.ili() else None,
        definition=synset.definition(),
        definitions=[synset.definition()] if synset.definition() else [],
        examples=synset.examples(),
        lemmas=synset.lemmas(),
        lexicalized=synset.lexicalized()
    )


def sense_to_detail(sense) -> SenseDetail:
    return SenseDetail(
        id=sense.id(),
        word_id=sense.word().id(),
        word_form=sense.word().lemma(),
        synset_id=sense.synset().id(),
        lexicon=sense.lexicon().id(),
        definition=sense.synset().definition(),
        examples=sense.examples() if hasattr(sense, 'examples') else [],
        frames=sense.frames() if hasattr(sense, 'frames') else []
    )


@router.get("/words/{word_id}", response_model=WordDetail)
async def get_word(word_id: str):
    word = wn_service.get_word_by_id(word_id)
    if not word:
        raise HTTPException(status_code=404, detail=f"Word '{word_id}' not found")
    return word_to_detail(word)


@router.get("/synsets/{synset_id}", response_model=SynsetDetail)
async def get_synset(synset_id: str):
    synset = wn_service.get_synset_by_id(synset_id)
    if not synset:
        raise HTTPException(status_code=404, detail=f"Synset '{synset_id}' not found")
    return synset_to_detail(synset)


@router.get("/senses/{sense_id}", response_model=SenseDetail)
async def get_sense(sense_id: str):
    sense = wn_service.get_sense_by_id(sense_id)
    if not sense:
        raise HTTPException(status_code=404, detail=f"Sense '{sense_id}' not found")
    return sense_to_detail(sense)
