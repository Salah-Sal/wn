from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.api.routers import lexicons, search, entities, relations, graph

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API for exploring WordNet data using the wn Python library",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lexicons.router, prefix=settings.api_prefix, tags=["Lexicons"])
app.include_router(search.router, prefix=settings.api_prefix, tags=["Search"])
app.include_router(entities.router, prefix=settings.api_prefix, tags=["Entities"])
app.include_router(relations.router, prefix=settings.api_prefix, tags=["Relations"])
app.include_router(graph.router, prefix=settings.api_prefix, tags=["Graph"])


@app.get("/")
async def root():
    return {"message": "WordNet Explorer API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
