from pydantic import BaseModel
from typing import Optional, Dict, List


class LexiconInfo(BaseModel):
    id: str
    version: str
    label: str
    language: str
    license: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None
    citation: Optional[str] = None
    
    class Config:
        from_attributes = True


class LexiconDetail(LexiconInfo):
    word_count: Dict[str, int] = {}
    synset_count: Dict[str, int] = {}
    modified: bool = False


class LexiconListResponse(BaseModel):
    lexicons: List[LexiconInfo]
    count: int


class ProjectInfo(BaseModel):
    id: str
    label: str
    language: str
    versions: List[str] = []
    license: Optional[str] = None


class DownloadRequest(BaseModel):
    project_id: str
