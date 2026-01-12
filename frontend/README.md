# WordNet Frontend

A modern React-based web interface for exploring and managing WordNet lexical databases. This frontend provides an intuitive UI for searching words, browsing synsets, exploring semantic relations, and managing lexicon uploads.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite 7** - Build tool and dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **TanStack React Query** - Server state management
- **Zustand** - Client state management
- **React Router 7** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icons

## Prerequisites

### All Platforms
- **Node.js** >= 18.x (recommended: 20.x or later)
- **npm** >= 9.x (comes with Node.js)
- **Python** >= 3.9 (for the backend API)

### Windows

1. **Install Node.js**
   - Download from [nodejs.org](https://nodejs.org/) (LTS version recommended)
   - Or use winget: `winget install OpenJS.NodeJS.LTS`
   - Or use Chocolatey: `choco install nodejs-lts`

2. **Install Python**
   - Download from [python.org](https://www.python.org/downloads/)
   - Or use winget: `winget install Python.Python.3.12`
   - Ensure "Add Python to PATH" is checked during installation

3. **Verify installations**
   ```powershell
   node --version   # Should show v18.x or higher
   npm --version    # Should show 9.x or higher
   python --version # Should show 3.9 or higher
   ```

### macOS

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Node.js**
   ```bash
   brew install node
   ```
   Or use nvm for version management:
   ```bash
   brew install nvm
   nvm install 20
   nvm use 20
   ```

3. **Install Python**
   ```bash
   brew install python@3.12
   ```

4. **Verify installations**
   ```bash
   node --version   # Should show v18.x or higher
   npm --version    # Should show 9.x or higher
   python3 --version # Should show 3.9 or higher
   ```

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/goodmami/wn.git
cd wn
```

### 2. Set Up the Backend

The frontend requires the FastAPI backend to be running.

**Windows (PowerShell):**
```powershell
# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .

# Start the backend server
python -m uvicorn backend.main:app --reload --port 8000
```

**macOS / Linux:**
```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Start the backend server
python -m uvicorn backend.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### 3. Set Up the Frontend

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5000`.

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production (runs TypeScript check first) |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint for code quality checks |

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts       # API client with typed endpoints
│   ├── components/
│   │   ├── BackButton.tsx      # Navigation back button
│   │   ├── Breadcrumbs.tsx     # Breadcrumb navigation
│   │   ├── Header.tsx          # App header
│   │   ├── LexiconManager.tsx  # Lexicon list & upload UI
│   │   ├── RelationCard.tsx    # Synset relation display
│   │   ├── SearchBar.tsx       # Search with autocomplete
│   │   └── ThreePanelLayout.tsx # Main layout component
│   ├── lib/
│   │   └── utils.ts        # Utility functions (cn, etc.)
│   ├── pages/
│   │   ├── HomePage.tsx    # Landing/search page
│   │   ├── SearchPage.tsx  # Search results
│   │   ├── SensePage.tsx   # Sense detail view
│   │   ├── SynsetPage.tsx  # Synset detail view
│   │   └── WordPage.tsx    # Word detail view
│   ├── stores/
│   │   └── appStore.ts     # Zustand global state
│   ├── App.tsx             # Root component with routes
│   ├── index.css           # Global styles & Tailwind
│   └── main.tsx            # Entry point
├── index.html              # HTML template
├── package.json            # Dependencies & scripts
├── tailwind.config.ts      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite configuration
```

## API Proxy Configuration

The Vite dev server proxies `/api` requests to the backend:

```typescript
// vite.config.ts
server: {
  port: 5000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

This means API calls like `/api/lexicons` are automatically forwarded to `http://localhost:8000/api/lexicons`.

## Features

- **Search**: Full-text search across words with autocomplete
- **Word Details**: View lemmas, forms, and associated senses
- **Synset Browser**: Explore synsets with definitions, examples, and lemmas
- **Semantic Relations**: Navigate hypernyms, hyponyms, meronyms, holonyms, and more
- **Lexicon Management**: View installed lexicons and upload new WN-LMF files
- **Multi-language Support**: Works with any WordNet in WN-LMF format (English, Arabic, etc.)

## Supported File Formats for Upload

The lexicon upload feature supports:
- `.xml` - WN-LMF XML files
- `.xml.gz` - Gzip-compressed WN-LMF files

## Troubleshooting

### Port Already in Use

If port 5000 or 8000 is already in use:

**Windows:**
```powershell
# Find process using port
netstat -ano | findstr :5000
# Kill process by PID
taskkill /PID <PID> /F
```

**macOS:**
```bash
# Find and kill process using port
lsof -ti:5000 | xargs kill -9
```

### Node Modules Issues

If you encounter dependency issues:
```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

Run the TypeScript compiler to check for errors:
```bash
npx tsc --noEmit
```

### Backend Connection Issues

Ensure the backend is running on port 8000:
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## Building for Production

```bash
# Build the frontend
npm run build

# The output will be in the 'dist' directory
# This can be served by any static file server
```

For production deployment, you'll typically serve the built files through the FastAPI backend or a reverse proxy like nginx.
