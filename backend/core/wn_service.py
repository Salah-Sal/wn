import wn
from functools import lru_cache
from typing import Optional, List


class WnService:
    
    @staticmethod
    def get_lexicons():
        return list(wn.lexicons())
    
    @staticmethod
    def get_lexicon(spec: str):
        lexicons = list(wn.lexicons(lang=spec))
        if not lexicons:
            lexicons = [lex for lex in wn.lexicons() if lex.id == spec or f"{lex.id}:{lex.version}" == spec]
        return lexicons[0] if lexicons else None
    
    @staticmethod
    def get_projects():
        return wn.projects()
    
    @staticmethod
    def download_lexicon(project_id: str):
        wn.download(project_id)
    
    @staticmethod
    def search_words(
        form: Optional[str] = None,
        pos: Optional[str] = None,
        lang: Optional[str] = None,
        lexicon: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ):
        kwargs = {}
        if lang:
            kwargs['lang'] = lang
        if lexicon:
            kwargs['lexicon'] = lexicon
        
        if form:
            words = list(wn.words(form, pos=pos, **kwargs))
        elif pos:
            words = list(wn.words(pos=pos, **kwargs))[:limit + offset]
        else:
            return []
        
        return words[offset:offset + limit]
    
    @staticmethod
    def search_synsets(
        form: Optional[str] = None,
        pos: Optional[str] = None,
        lang: Optional[str] = None,
        lexicon: Optional[str] = None,
        ili: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ):
        kwargs = {}
        if lang:
            kwargs['lang'] = lang
        if ili:
            kwargs['ili'] = ili
        if lexicon:
            kwargs['lexicon'] = lexicon
        
        if form:
            synsets = list(wn.synsets(form, pos=pos, **kwargs))
        elif ili:
            synsets = list(wn.synsets(ili=ili, **kwargs))
        elif pos:
            synsets = list(wn.synsets(pos=pos, **kwargs))[:limit + offset]
        else:
            return []
        
        return synsets[offset:offset + limit]
    
    @staticmethod
    def get_word_by_id(word_id: str):
        try:
            return wn.word(word_id)
        except wn.Error:
            return None
    
    @staticmethod
    def get_synset_by_id(synset_id: str):
        try:
            return wn.synset(synset_id)
        except wn.Error:
            return None
    
    @staticmethod
    def get_sense_by_id(sense_id: str):
        try:
            return wn.sense(sense_id)
        except wn.Error:
            return None
    
    @staticmethod
    def autocomplete(query: str, limit: int = 10, lang: Optional[str] = None):
        if not query or len(query) < 2:
            return []
        
        kwargs = {}
        if lang:
            kwargs['lang'] = lang
        
        words = list(wn.words(query + '*', **kwargs))[:limit * 3]
        
        seen = set()
        matches = []
        
        for word in words:
            form = word.lemma()
            key = (form, word.pos)
            if key not in seen:
                seen.add(key)
                matches.append({
                    'form': form,
                    'pos': word.pos,
                    'id': word.id,
                    'sense_count': len(word.senses())
                })
                if len(matches) >= limit:
                    break
        
        return matches


@lru_cache
def get_wn_service() -> WnService:
    return WnService()
