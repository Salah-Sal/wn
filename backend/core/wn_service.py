import wn
from wn import lmf
from functools import lru_cache
from typing import Optional, List
from pathlib import Path


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
    def remove_lexicon(lexicon_spec: str):
        """Remove a lexicon from the database."""
        wn.remove(lexicon_spec)
    
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

    @staticmethod
    def validate_lmf_file(file_path: Path) -> dict:
        """Validate an LMF file and return info about its lexicons."""
        try:
            infos = lmf.scan_lexicons(file_path)
            if not infos:
                return {"valid": False, "error": "No lexicons found in file"}

            lexicons = []
            for info in infos:
                lexicons.append({
                    "id": info.get("id"),
                    "version": info.get("version"),
                    "label": info.get("label"),
                    "language": info.get("language"),
                })
            return {"valid": True, "lexicons": lexicons}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def add_from_file(file_path: Path) -> dict:
        """Add a wordnet from a local file."""
        try:
            # First validate the file
            validation = WnService.validate_lmf_file(file_path)
            if not validation["valid"]:
                return {"success": False, "error": validation["error"]}

            # Add to database (progress_handler=None for API usage)
            wn.add(file_path, progress_handler=None)

            return {
                "success": True,
                "lexicons": validation["lexicons"],
                "message": f"Successfully added {len(validation['lexicons'])} lexicon(s)"
            }
        except wn.Error as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


@lru_cache
def get_wn_service() -> WnService:
    return WnService()
