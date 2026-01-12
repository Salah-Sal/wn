# Wn - Python Wordnet Library

## Overview
Wn is a Python library for exploring information in wordnets. It provides a multilingual interface to wordnet databases with support for various wordnets around the world.

## Project Structure
- `wn/` - Main library source code
- `tests/` - Test suite
- `docs/` - Sphinx documentation
- `bench/` - Benchmarking tests

## Getting Started

### Installation
The package is installed in development mode with all dependencies.

### Download WordNet Data
Before using, download wordnet data:
```bash
python -m wn download oewn:2024  # Open English WordNet 2024
```

### Basic Usage
```python
import wn

# List available projects
wn.projects()

# Download a wordnet
wn.download('oewn:2024')

# Query the wordnet
en = wn.Wordnet('oewn:2024')
synsets = en.synsets('dog')
```

## CLI Commands
- `python -m wn download <project>` - Download wordnet data
- `python -m wn lexicons` - List installed lexicons
- `python -m wn projects` - List known projects
- `python -m wn validate <file>` - Validate a lexicon file

## Dependencies
- httpx - HTTP client
- tomli - TOML parser
- starlette - Web framework (optional, for web features)

## Recent Changes
- Initial Replit environment setup (January 2026)
