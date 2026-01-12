# WordNet Explorer

## Overview
WordNet Explorer is a web application for linguists and wordnet engineers to browse, search, and analyze lexical semantic databases. Built on top of the `wn` Python library, it provides an intuitive interface for exploring wordnet data.

## Project Structure
```
backend/
  main.py           - FastAPI application entry point
  api/
    routers/        - API route handlers (lexicons, search, entities, relations, graph)
  core/
    wn_service.py   - WordNet service wrapper for wn library
frontend/
  src/
    api/            - API client and type definitions (including graphTypes.ts)
    components/     - React components (SearchBar, LexiconManager, etc.)
      graph/        - Graph visualization components (GraphCanvas, GraphControls, etc.)
    hooks/          - Custom React hooks (useGraphData.ts)
    stores/         - Zustand stores (graphStore.ts)
    layouts/        - Layout components (ThreePanelLayout)
    pages/          - Page components (Home, Search, Word, Synset, Sense, GraphExplorer)
    lib/            - Utility functions
    types/          - TypeScript type declarations
wn/                 - Original wn library source code
```

## Tech Stack
- **Backend**: FastAPI (Python 3.11), running on port 8000
- **Frontend**: React + TypeScript + Vite, running on port 5000
- **Styling**: Tailwind CSS with custom CSS variables
- **State**: Zustand (global), React Query (server state)
- **Graph Visualization**: Cytoscape.js with dagre, fcose, cose-bilkent layouts
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
- `GET /api/graph/neighborhood/{synset_id}` - Get graph neighborhood for a synset
- `GET /api/graph/hypernym-tree/{synset_id}` - Get hypernym ancestry tree
- `GET /api/graph/hyponym-tree/{synset_id}` - Get hyponym descendants tree
- `GET /api/graph/path/{synset_id1}/{synset_id2}` - Find shortest path between synsets
- `GET /api/graph/similarity/{synset_id1}/{synset_id2}` - Calculate similarity metrics

## Key Features
- Three-panel layout (Navigation | Content | Details)
- Universal search with 150ms debounced autocomplete
- POS filter (noun, verb, adjective, adverb)
- Color-coded POS badges (noun=blue, verb=green, adj=orange, adv=purple)
- Collapsible sections in entity browsers
- Linked navigation between words, synsets, and senses
- Clipboard copy for IDs
- Interactive graph visualization with Cytoscape.js
  - Neighborhood expansion (click nodes to explore)
  - Hypernym tree view (ancestry)
  - Hyponym tree view (descendants)
  - Multiple layout algorithms (dagre, fcose, circle, breadthfirst, cose-bilkent)
  - POS-colored nodes, relation-styled edges
  - Zoom/pan controls and tooltip on hover

## Recent Changes
- January 2026: Graph visualization feature
  - Backend graph router with neighborhood, tree, path, and similarity endpoints
  - Cytoscape.js integration with react-cytoscapejs
  - GraphCanvas, GraphControls, GraphTooltip, GraphLegend components
  - GraphExplorerPage with three view modes (neighborhood, hypernym-tree, hyponym-tree)
  - Zustand store for graph state management
  - "Explore Graph" button on SynsetPage as entry point
- January 2026: Lexicon management improvements
  - Added ability to remove installed lexicons (DELETE endpoint + UI)
  - Added file upload for local WN-LMF files
  - Fixed *INFERRED* placeholder synset handling in Arabic WordNet
- January 2026: Navigation UX improvements
  - Added BackButton component to all detail pages for easy navigation
  - Made senses clickable with "View Sense" links in WordPage
  - Made derived words clickable (links to search)
  - Made lemmas clickable in SynsetPage (links to search)
  - Added Breadcrumbs component to ThreePanelLayout
  - Added expand/collapse for truncated relations in SynsetPage
- January 2026: Initial WordNet Explorer implementation
  - Backend API with FastAPI and wn integration
  - Frontend with React, TypeScript, Tailwind CSS
  - Three-panel responsive layout
  - Lexicon management with download capability
  - Universal search with autocomplete
  - Word, Synset, Sense detail pages

## User Preferences
- Frontend must bind to 0.0.0.0:5000 with proxy to backend
- All hosts must be allowed for Replit iframe preview
- Using path alias `@/` for clean imports
