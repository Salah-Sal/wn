from fastapi import APIRouter, Query
from typing import Optional, List
from backend.core.wn_service import get_wn_service
from backend.schemas.entities import (
    SearchResponse, SearchResult, AutocompleteItem
)

router = APIRouter()
wn_service = get_wn_service()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    pos: Optional[str] = Query(None, description="Part of speech filter (n, v, a, r, s)"),
    lang: Optional[str] = Query(None, description="Language filter"),
    lexicon: Optional[str] = Query(None, description="Lexicon filter"),
    mode: str = Query("word", description="Search mode: word, synset, definition"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    results = []
    
    if mode == "synset" and q.startswith(("oewn-", "omw-", "own-")):
        synset = wn_service.get_synset_by_id(q)
        if synset:
            results.append(SearchResult(
                type="synset",
                id=synset.id,
                label=", ".join(synset.lemmas()[:3]) if synset.lemmas() else synset.id,
                pos=synset.pos,
                definition=synset.definition()
            ))
    else:
        words = wn_service.search_words(
            form=q, pos=pos, lang=lang, lexicon=lexicon,
            limit=limit, offset=offset
        )
        
        for word in words:
            results.append(SearchResult(
                type="word",
                id=word.id,
                label=word.lemma(),
                pos=word.pos,
                definition=None
            ))
        
        if len(results) < limit:
            synsets = wn_service.search_synsets(
                form=q, pos=pos, lang=lang, lexicon=lexicon,
                limit=limit - len(results), offset=0
            )
            
            for synset in synsets:
                if not any(r.id == synset.id for r in results):
                    results.append(SearchResult(
                        type="synset",
                        id=synset.id,
                        label=", ".join(synset.lemmas()[:3]) if synset.lemmas() else synset.id,
                        pos=synset.pos,
                        definition=synset.definition()
                    ))
    
    return SearchResponse(
        results=results[:limit],
        total=len(results),
        query=q
    )


@router.get("/autocomplete", response_model=List[AutocompleteItem])
async def autocomplete(
    q: str = Query(..., min_length=1, description="Query prefix"),
    lang: Optional[str] = Query(None, description="Language filter"),
    limit: int = Query(10, ge=1, le=50)
):
    matches = wn_service.autocomplete(q, limit=limit, lang=lang)
    return [AutocompleteItem(**match) for match in matches]
