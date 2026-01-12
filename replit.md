# WordNet Explorer

## Overview
WordNet Explorer is a web application for linguists and wordnet engineers to browse, search, and analyze lexical semantic databases. Built on top of the `wn` Python library, it provides an intuitive interface for exploring wordnet data.

## Project Structure
```
backend/
  main.py           - FastAPI application entry point
  api/
    routers/        - API route handlers (lexicons, search, entities, relations)
  core/
    wn_service.py   - WordNet service wrapper for wn library
frontend/
  src/
    api/            - API client and type definitions
    components/     - React components (SearchBar, LexiconManager, etc.)
    layouts/        - Layout components (ThreePanelLayout)
    pages/          - Page components (Home, Search, Word, Synset, Sense)
    lib/            - Utility functions
wn/                 - Original wn library source code
```

## Tech Stack
- **Backend**: FastAPI (Python 3.11), running on port 8000
- **Frontend**: React + TypeScript + Vite, running on port 5000
- **Styling**: Tailwind CSS with custom CSS variables
- **State**: Zustand (global), React Query (server state)
- **WordNet**: wn Python library with OEWN support

## Running the Application

### Development
Both workflows run automatically:
- Backend API: `python -m uvicorn backend.main:app --host localhost --port 8000 --reload`
- Frontend: `npm run dev` (in frontend directory)

### Getting Started
1. Open the app in the webview
2. Use the Lexicon Manager in the sidebar to download a WordNet (e.g., ewn:2020 or oewn:2024)
3. Search for words, synsets, or browse lexical relations

## API Endpoints
- `GET /api/lexicons` - List installed lexicons
- `GET /api/projects` - List available projects for download
- `POST /api/lexicons/download` - Download and install a project
- `GET /api/search` - Search words and synsets
- `GET /api/autocomplete` - Search autocomplete suggestions
- `GET /api/words/{id}` - Get word details
- `GET /api/synsets/{id}` - Get synset details
- `GET /api/senses/{id}` - Get sense details
- `GET /api/synsets/{id}/relations` - Get synset relations

## Key Features
- Three-panel layout (Navigation | Content | Details)
- Universal search with 150ms debounced autocomplete
- POS filter (noun, verb, adjective, adverb)
- Color-coded POS badges (noun=blue, verb=green, adj=orange, adv=purple)
- Collapsible sections in entity browsers
- Linked navigation between words, synsets, and senses
- Clipboard copy for IDs

## Recent Changes
- January 2026: Initial WordNet Explorer implementation
  - Backend API with FastAPI and wn integration
  - Frontend with React, TypeScript, Tailwind CSS
  - Three-panel responsive layout
  - Lexicon management with download capability
  - Universal search with autocomplete
  - Word, Synset, Sense detail pages
  - Breadcrumb navigation

## User Preferences
- Frontend must bind to 0.0.0.0:5000 with proxy to backend
- All hosts must be allowed for Replit iframe preview
- Using path alias `@/` for clean imports
