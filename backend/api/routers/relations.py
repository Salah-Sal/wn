from fastapi import APIRouter, HTTPException
from typing import List
from backend.core.wn_service import get_wn_service
from backend.schemas.relations import (
    SynsetRelations, SenseRelations, RelatedSynset, RelatedSense, HypernymPath
)

router = APIRouter()
wn_service = get_wn_service()


def is_valid_synset(synset) -> bool:
    """Filter out placeholder synsets like *INFERRED*"""
    if not synset or not hasattr(synset, 'id'):
        return False
    synset_id = synset.id
    if not synset_id or synset_id.startswith('*') or synset_id == '*INFERRED*':
        return False
    return True


def synset_to_related(synset) -> RelatedSynset:
    return RelatedSynset(
        id=synset.id,
        pos=synset.pos,
        definition=synset.definition(),
        lemmas=synset.lemmas()[:5]
    )


def sense_to_related(sense) -> RelatedSense:
    return RelatedSense(
        id=sense.id,
        word_form=sense.word().lemma(),
        synset_id=sense.synset().id
    )


@router.get("/synsets/{synset_id}/relations", response_model=SynsetRelations)
async def get_synset_relations(synset_id: str):
    synset = wn_service.get_synset_by_id(synset_id)
    if not synset:
        raise HTTPException(status_code=404, detail=f"Synset '{synset_id}' not found")
    
    relations = synset.relations()
    
    return SynsetRelations(
        synset_id=synset_id,
        hypernyms=[synset_to_related(s) for s in relations.get('hypernym', []) if is_valid_synset(s)],
        hyponyms=[synset_to_related(s) for s in relations.get('hyponym', []) if is_valid_synset(s)],
        holonyms=[synset_to_related(s) for s in (
            relations.get('holo_member', []) +
            relations.get('holo_part', []) +
            relations.get('holo_substance', [])
        ) if is_valid_synset(s)],
        meronyms=[synset_to_related(s) for s in (
            relations.get('mero_member', []) +
            relations.get('mero_part', []) +
            relations.get('mero_substance', [])
        ) if is_valid_synset(s)],
        similar=[synset_to_related(s) for s in relations.get('similar', []) if is_valid_synset(s)],
        also=[synset_to_related(s) for s in relations.get('also', []) if is_valid_synset(s)],
        attributes=[synset_to_related(s) for s in relations.get('attribute', []) if is_valid_synset(s)],
        domain_topics=[synset_to_related(s) for s in relations.get('domain_topic', []) if is_valid_synset(s)],
        domain_regions=[synset_to_related(s) for s in relations.get('domain_region', []) if is_valid_synset(s)]
    )


@router.get("/synsets/{synset_id}/hypernyms", response_model=List[RelatedSynset])
async def get_hypernyms(synset_id: str, depth: int = 1):
    synset = wn_service.get_synset_by_id(synset_id)
    if not synset:
        raise HTTPException(status_code=404, detail=f"Synset '{synset_id}' not found")
    
    result = []
    current = [synset]
    visited = set()
    
    for _ in range(depth):
        next_level = []
        for s in current:
            for hyper in s.hypernyms():
                if hyper.id not in visited:
                    visited.add(hyper.id)
                    result.append(synset_to_related(hyper))
                    next_level.append(hyper)
        current = next_level
        if not current:
            break
    
    return result


@router.get("/synsets/{synset_id}/hyponyms", response_model=List[RelatedSynset])
async def get_hyponyms(synset_id: str, depth: int = 1):
    synset = wn_service.get_synset_by_id(synset_id)
    if not synset:
        raise HTTPException(status_code=404, detail=f"Synset '{synset_id}' not found")
    
    result = []
    current = [synset]
    visited = set()
    
    for _ in range(depth):
        next_level = []
        for s in current:
            for hypo in s.hyponyms():
                if hypo.id not in visited:
                    visited.add(hypo.id)
                    result.append(synset_to_related(hypo))
                    next_level.append(hypo)
        current = next_level
        if not current:
            break
    
    return result


@router.get("/synsets/{synset_id}/hypernym-paths", response_model=List[HypernymPath])
async def get_hypernym_paths(synset_id: str):
    synset = wn_service.get_synset_by_id(synset_id)
    if not synset:
        raise HTTPException(status_code=404, detail=f"Synset '{synset_id}' not found")
    
    paths = []
    
    def find_paths(current, path):
        hypernyms = current.hypernyms()
        if not hypernyms:
            if path:
                paths.append(HypernymPath(
                    path=[synset_to_related(s) for s in path],
                    depth=len(path)
                ))
        else:
            for hyper in hypernyms:
                find_paths(hyper, path + [hyper])
    
    find_paths(synset, [])
    return paths


@router.get("/senses/{sense_id}/relations", response_model=SenseRelations)
async def get_sense_relations(sense_id: str):
    sense = wn_service.get_sense_by_id(sense_id)
    if not sense:
        raise HTTPException(status_code=404, detail=f"Sense '{sense_id}' not found")
    
    relations = sense.relations()
    
    return SenseRelations(
        sense_id=sense_id,
        antonyms=[sense_to_related(s) for s in relations.get('antonym', [])],
        derivations=[sense_to_related(s) for s in relations.get('derivation', [])],
        pertainyms=[sense_to_related(s) for s in relations.get('pertainym', [])],
        similar=[sense_to_related(s) for s in relations.get('similar', [])]
    )
