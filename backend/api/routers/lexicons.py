from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from pathlib import Path
import tempfile
import os
from backend.core.wn_service import get_wn_service
from backend.schemas.lexicon import (
    LexiconInfo, LexiconDetail, LexiconListResponse,
    ProjectInfo, DownloadRequest, UploadResponse, UploadedLexiconInfo
)

router = APIRouter()
wn_service = get_wn_service()


def lexicon_to_info(lex) -> LexiconInfo:
    return LexiconInfo(
        id=lex.id,
        version=lex.version,
        label=lex.label or lex.id,
        language=lex.language,
        license=lex.license,
        url=lex.url,
        email=lex.email,
        citation=lex.citation
    )


def lexicon_to_detail(lex) -> LexiconDetail:
    stats = lex.describe()
    word_count = {}
    synset_count = {}
    
    for key, value in stats.items():
        if key.startswith('Words:'):
            pos = key.split(':')[1].strip() if ':' in key else 'all'
            word_count[pos] = value
        elif key.startswith('Synsets:'):
            pos = key.split(':')[1].strip() if ':' in key else 'all'
            synset_count[pos] = value
    
    return LexiconDetail(
        id=lex.id,
        version=lex.version,
        label=lex.label or lex.id,
        language=lex.language,
        license=lex.license,
        url=lex.url,
        email=lex.email,
        citation=lex.citation,
        word_count=word_count,
        synset_count=synset_count,
        modified=lex.modified
    )


@router.get("/lexicons", response_model=LexiconListResponse)
async def list_lexicons():
    lexicons = wn_service.get_lexicons()
    return LexiconListResponse(
        lexicons=[lexicon_to_info(lex) for lex in lexicons],
        count=len(lexicons)
    )


@router.get("/lexicons/{spec}", response_model=LexiconDetail)
async def get_lexicon(spec: str):
    lex = wn_service.get_lexicon(spec)
    if not lex:
        raise HTTPException(status_code=404, detail=f"Lexicon '{spec}' not found")
    return lexicon_to_detail(lex)


@router.get("/projects", response_model=List[ProjectInfo])
async def list_projects():
    projects = wn_service.get_projects()
    result = []
    for proj in projects:
        result.append(ProjectInfo(
            id=proj.get('id', ''),
            label=proj.get('label', proj.get('id', '')),
            language=proj.get('language') or 'unknown',
            versions=[proj.get('version', '')] if proj.get('version') else [],
            license=proj.get('license')
        ))
    return result


@router.post("/lexicons/download")
async def download_lexicon(request: DownloadRequest):
    try:
        wn_service.download_lexicon(request.project_id)
        return {"status": "success", "message": f"Downloaded {request.project_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lexicons/upload", response_model=UploadResponse)
async def upload_lexicon(file: UploadFile = File(...)):
    """Upload a WordNet LMF file from local disk."""
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    valid_extensions = ('.xml', '.xml.gz', '.gz')
    if not file.filename.lower().endswith(valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Supported formats: {', '.join(valid_extensions)}"
        )

    # Determine suffix for temp file
    suffix = '.xml.gz' if file.filename.lower().endswith('.gz') else '.xml'

    # Save to temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        # Add to wn database
        result = wn_service.add_from_file(tmp_path)

        if result["success"]:
            return UploadResponse(
                success=True,
                message=result["message"],
                lexicons=[UploadedLexiconInfo(**lex) for lex in result["lexicons"]],
                filename=file.filename
            )
        else:
            return UploadResponse(
                success=False,
                error=result["error"],
                filename=file.filename
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    finally:
        # Clean up temp file
        if 'tmp_path' in locals() and tmp_path.exists():
            os.unlink(tmp_path)
