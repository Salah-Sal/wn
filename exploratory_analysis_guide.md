# Exploratory Analysis Guide for WordNets using `wn`

This guide walks you through performing exploratory analysis on a wordnet using the `wn` Python library.

## Table of Contents

1. [Setup](#setup)
2. [Loading and Inspecting Lexicons](#loading-and-inspecting-lexicons)
3. [Exploring Words](#exploring-words)
4. [Exploring Synsets](#exploring-synsets)
5. [Navigating the Taxonomy](#navigating-the-taxonomy)
6. [Semantic Relations](#semantic-relations)
7. [Similarity Measures](#similarity-measures)
8. [Cross-Linguistic Analysis](#cross-linguistic-analysis)
9. [Statistical Overview](#statistical-overview)
10. [Advanced Queries](#advanced-queries)

---

## Setup

### Installation

```bash
pip install wn
```

### Download a WordNet

```python
import wn

# Download the Open English WordNet
wn.download('oewn:2024')

# Or download the OMW English WordNet 3.1
wn.download('omw-en31:1.4')

# List all available projects
for project in wn.projects():
    print(f"{project.id}: {project.label}")
```

---

## Loading and Inspecting Lexicons

### List Installed Lexicons

```python
# See what's in your database
for lex in wn.lexicons():
    print(f"{lex.id()} v{lex.version()} - {lex.label()} ({lex.language()})")
```

### Create a Wordnet Instance

```python
# Default: use all installed lexicons
en = wn.Wordnet('oewn:2024')

# Or filter by language
en = wn.Wordnet(lang='en')

# Combine multiple lexicons
combined = wn.Wordnet(lang='en', lexicon='oewn:2024 omw-en31:1.4')
```

### Lexicon Metadata

```python
lex = wn.lexicons()[0]

print(f"ID: {lex.id()}")
print(f"Label: {lex.label()}")
print(f"Language: {lex.language()}")
print(f"Version: {lex.version()}")
print(f"License: {lex.license()}")
print(f"URL: {lex.url()}")
print(f"Citation: {lex.citation()}")
print(f"Metadata: {lex.metadata()}")
```

---

## Exploring Words

### Look Up a Word

```python
# Find all words matching a lemma
words = wn.words('dog')

for word in words:
    print(f"Word: {word.lemma()}")
    print(f"POS: {word.pos()}")
    print(f"Forms: {[f.form() for f in word.forms()]}")
    print(f"Number of senses: {len(word.senses())}")
    print()
```

### Explore Word Senses

```python
# Get all senses of a word
for word in wn.words('bank'):
    print(f"\n=== {word.lemma()} ({word.pos()}) ===")
    for sense in word.senses():
        synset = sense.synset()
        print(f"  - {synset.id()}: {synset.definition()}")
```

### Filter by Part of Speech

```python
# Only nouns
nouns = wn.words('run', pos='n')

# Only verbs
verbs = wn.words('run', pos='v')

# POS codes: 'n' (noun), 'v' (verb), 'a' (adjective),
#            'r' (adverb), 's' (adjective satellite)
```

### Word Forms (Inflections)

```python
for word in wn.words('go', pos='v'):
    print(f"Lemma: {word.lemma()}")
    for form in word.forms():
        print(f"  Form: {form.form()}")
```

---

## Exploring Synsets

### Look Up Synsets

```python
# Find synsets by lemma
synsets = wn.synsets('happy')

for ss in synsets:
    print(f"ID: {ss.id()}")
    print(f"POS: {ss.pos()}")
    print(f"Definition: {ss.definition()}")
    print(f"Examples: {ss.examples()}")
    print(f"Lemmas: {[w.lemma() for w in ss.words()]}")
    print()
```

### Get a Specific Synset

```python
# By ID
dog_synset = wn.synset('oewn-02086723-n')

# Or find by definition
for ss in wn.synsets('dog', pos='n'):
    if 'canine' in ss.definition().lower():
        print(ss.id(), ss.definition())
```

### Synset Members (Words/Senses)

```python
ss = wn.synsets('car', pos='n')[0]

# Get all words in this synset
print("Words in synset:")
for word in ss.words():
    print(f"  - {word.lemma()}")

# Get all senses
print("\nSenses in synset:")
for sense in ss.senses():
    print(f"  - {sense.word().lemma()}: {sense.id()}")
```

---

## Navigating the Taxonomy

### Hypernyms (More General)

```python
from wn import taxonomy

dog = wn.synsets('dog', pos='n')[0]

# Direct hypernyms
print("Direct hypernyms:")
for h in dog.hypernyms():
    print(f"  {h.id()}: {h.definition()}")

# All hypernym paths to root
print("\nHypernym paths:")
for path in dog.hypernym_paths():
    print(" -> ".join([s.words()[0].lemma() for s in path]))
```

### Hyponyms (More Specific)

```python
animal = wn.synsets('animal', pos='n')[0]

# Direct hyponyms
print("Direct hyponyms (first 10):")
for h in animal.hyponyms()[:10]:
    print(f"  {h.words()[0].lemma()}: {h.definition()[:50]}...")

# Count all descendants
def count_descendants(synset, visited=None):
    if visited is None:
        visited = set()
    count = 0
    for hypo in synset.hyponyms():
        if hypo.id() not in visited:
            visited.add(hypo.id())
            count += 1 + count_descendants(hypo, visited)
    return count

print(f"\nTotal descendants: {count_descendants(animal)}")
```

### Taxonomy Utilities

```python
from wn import taxonomy

# Find root synsets (no hypernyms)
print("Root synsets:")
for root in taxonomy.roots(wn.Wordnet('oewn:2024'), pos='n'):
    print(f"  {root.words()[0].lemma()}: {root.definition()[:50]}...")

# Find leaf synsets (no hyponyms)
dog = wn.synsets('dog', pos='n')[0]
print(f"\nLeaf descendants of 'dog': {len(list(taxonomy.leaves(dog)))}")

# Depth in taxonomy
print(f"Min depth of 'dog': {taxonomy.min_depth(dog)}")
print(f"Max depth of 'dog': {taxonomy.max_depth(dog)}")

# Shortest path between synsets
cat = wn.synsets('cat', pos='n')[0]
path = dog.shortest_path(cat)
if path:
    print(f"\nPath from dog to cat ({len(path)} steps):")
    for s in path:
        print(f"  {s.words()[0].lemma()}")
```

---

## Semantic Relations

### Explore All Relations

```python
ss = wn.synsets('dog', pos='n')[0]

# Get all relations as a map
relations = ss.relation_map()
for rel_type, related_synsets in relations.items():
    print(f"\n{rel_type}:")
    for r in related_synsets:
        print(f"  - {r.words()[0].lemma()}: {r.definition()[:40]}...")
```

### Common Relation Types

```python
# Synset relations
ss = wn.synsets('car', pos='n')[0]

# Meronyms (parts)
print("Parts (meronyms):")
for m in ss.meronyms():  # or part_meronyms(), substance_meronyms(), member_meronyms()
    print(f"  - {m.words()[0].lemma()}")

# Holonyms (wholes)
print("\nWholes (holonyms):")
for h in ss.holonyms():
    print(f"  - {h.words()[0].lemma()}")

# For verbs: entailment, causes
verb = wn.synsets('sleep', pos='v')[0]
print("\nEntails:")
for e in verb.entails():
    print(f"  - {e.words()[0].lemma()}")
```

### Sense Relations

```python
sense = wn.senses('good', pos='a')[0]

# Antonyms are sense-level relations
print("Antonyms:")
for ant in sense.relations('antonym'):
    print(f"  - {ant.word().lemma()}")

# Also-see, similar, etc.
print("\nAll sense relations:")
for rel_type, senses in sense.relation_map().items():
    print(f"  {rel_type}: {[s.word().lemma() for s in senses]}")
```

---

## Similarity Measures

```python
from wn import similarity

# Get two synsets to compare
dog = wn.synsets('dog', pos='n')[0]
cat = wn.synsets('cat', pos='n')[0]
car = wn.synsets('car', pos='n')[0]

# Path-based similarity (0-1, higher = more similar)
print(f"dog-cat path similarity: {similarity.path(dog, cat):.3f}")
print(f"dog-car path similarity: {similarity.path(dog, car):.3f}")

# Wu-Palmer similarity (considers depth)
print(f"\ndog-cat Wu-Palmer: {similarity.wup(dog, cat):.3f}")
print(f"dog-car Wu-Palmer: {similarity.wup(dog, car):.3f}")

# Leacock-Chodorow (uses max depth)
print(f"\ndog-cat Leacock-Chodorow: {similarity.lch(dog, cat):.3f}")
print(f"dog-car Leacock-Chodorow: {similarity.lch(dog, car):.3f}")
```

### Information Content-Based Similarity

```python
from wn import similarity, ic

# First, compute IC from a corpus or use intrinsic IC
# Intrinsic IC (based on taxonomy structure)
ic_data = ic.intrinsic_ic(wn.Wordnet('oewn:2024'))

# IC-based metrics
print(f"dog-cat Resnik: {similarity.res(dog, cat, ic_data):.3f}")
print(f"dog-cat Lin: {similarity.lin(dog, cat, ic_data):.3f}")
print(f"dog-cat Jiang-Conrath: {similarity.jcn(dog, cat, ic_data):.3f}")
```

---

## Cross-Linguistic Analysis

### Using the Interlingual Index (ILI)

```python
# Download wordnets for multiple languages
wn.download('omw-ja:1.4')  # Japanese
wn.download('omw-es:1.4')  # Spanish

# Find translations via ILI
en_dog = wn.synsets('dog', pos='n', lang='en')[0]
ili = en_dog.ili()

if ili:
    print(f"ILI: {ili.id()}")
    print(f"Status: {ili.status()}")

    # Find equivalent synsets in other languages
    for ss in wn.synsets(ili=ili.id()):
        lex = ss.lexicon()
        words = [w.lemma() for w in ss.words()]
        print(f"  {lex.language()}: {words}")
```

### Compare Lexicon Coverage

```python
# Compare what concepts exist across languages
def compare_coverage(concept, languages):
    results = {}
    for lang in languages:
        synsets = wn.synsets(concept, lang=lang)
        results[lang] = len(synsets)
    return results

concepts = ['dog', 'love', 'computer', 'democracy']
for concept in concepts:
    coverage = compare_coverage(concept, ['en', 'ja', 'es'])
    print(f"{concept}: {coverage}")
```

---

## Statistical Overview

### Database Statistics

```python
def wordnet_stats(wordnet):
    """Generate statistics for a wordnet."""
    stats = {
        'lexicons': len(list(wordnet.lexicons())),
        'words': len(list(wordnet.words())),
        'senses': len(list(wordnet.senses())),
        'synsets': len(list(wordnet.synsets())),
    }

    # By POS
    for pos in ['n', 'v', 'a', 'r']:
        stats[f'synsets_{pos}'] = len(list(wordnet.synsets(pos=pos)))

    return stats

en = wn.Wordnet('oewn:2024')
stats = wordnet_stats(en)

print("WordNet Statistics:")
print("-" * 30)
for key, value in stats.items():
    print(f"{key:20}: {value:,}")
```

### Polysemy Analysis

```python
def analyze_polysemy(wordnet, pos=None):
    """Analyze word polysemy (multiple senses per word)."""
    sense_counts = []

    for word in wordnet.words(pos=pos):
        sense_counts.append(len(word.senses()))

    if not sense_counts:
        return {}

    return {
        'total_words': len(sense_counts),
        'monosemous': sum(1 for c in sense_counts if c == 1),
        'polysemous': sum(1 for c in sense_counts if c > 1),
        'avg_senses': sum(sense_counts) / len(sense_counts),
        'max_senses': max(sense_counts),
    }

en = wn.Wordnet('oewn:2024')
print("\nPolysemy Analysis (Nouns):")
for k, v in analyze_polysemy(en, pos='n').items():
    print(f"  {k}: {v}")
```

### Taxonomy Depth Analysis

```python
from wn import taxonomy

def analyze_taxonomy_depth(wordnet, pos='n'):
    """Analyze the depth distribution of the taxonomy."""
    depths = []

    for ss in wordnet.synsets(pos=pos):
        depths.append(taxonomy.min_depth(ss))

    if not depths:
        return {}

    from collections import Counter
    depth_dist = Counter(depths)

    return {
        'max_depth': max(depths),
        'avg_depth': sum(depths) / len(depths),
        'depth_distribution': dict(sorted(depth_dist.items())),
    }

en = wn.Wordnet('oewn:2024')
depth_stats = analyze_taxonomy_depth(en, pos='n')
print(f"\nTaxonomy Depth (Nouns):")
print(f"  Max depth: {depth_stats['max_depth']}")
print(f"  Avg depth: {depth_stats['avg_depth']:.2f}")
```

---

## Advanced Queries

### Custom Normalization

```python
# Case-insensitive matching with custom normalizer
def my_normalizer(form):
    return form.lower().strip()

en = wn.Wordnet('oewn:2024', normalizer=my_normalizer)
words = en.words('DOG')  # Will match 'dog'
```

### Using Lemmatization

```python
from wn import morphy

# Enable lemmatization for English
en = wn.Wordnet('oewn:2024', lemmatizer=morphy.morphy)

# Now inflected forms are resolved
synsets = en.synsets('running')  # Finds 'run' synsets
synsets = en.synsets('dogs')     # Finds 'dog' synsets
synsets = en.synsets('better')   # Finds 'good' synsets
```

### Finding Specific Patterns

```python
# Find all synsets with a specific word in definition
def search_definitions(wordnet, keyword, pos=None):
    results = []
    for ss in wordnet.synsets(pos=pos):
        defn = ss.definition()
        if defn and keyword.lower() in defn.lower():
            results.append(ss)
    return results

en = wn.Wordnet('oewn:2024')
tech_synsets = search_definitions(en, 'computer', pos='n')
print(f"Found {len(tech_synsets)} synsets mentioning 'computer'")
```

### Export for External Analysis

```python
import json

def export_synsets_to_json(wordnet, output_file, pos=None):
    """Export synset data to JSON for external analysis."""
    data = []

    for ss in wordnet.synsets(pos=pos):
        entry = {
            'id': ss.id(),
            'pos': ss.pos(),
            'definition': ss.definition(),
            'examples': [str(e) for e in ss.examples()],
            'lemmas': [w.lemma() for w in ss.words()],
            'hypernyms': [h.id() for h in ss.hypernyms()],
            'hyponyms': [h.id() for h in ss.hyponyms()],
        }
        data.append(entry)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    return len(data)

# Export all noun synsets
# count = export_synsets_to_json(en, 'noun_synsets.json', pos='n')
```

---

## Quick Reference

| Task | Code |
|------|------|
| Download wordnet | `wn.download('oewn:2024')` |
| List lexicons | `wn.lexicons()` |
| Look up word | `wn.words('dog')` |
| Look up synsets | `wn.synsets('dog', pos='n')` |
| Get definition | `synset.definition()` |
| Get hypernyms | `synset.hypernyms()` |
| Get hyponyms | `synset.hyponyms()` |
| Path similarity | `similarity.path(ss1, ss2)` |
| Find translations | `wn.synsets(ili=ili_id)` |

---

## Further Resources

- [Official Documentation](https://wn.readthedocs.io/)
- [GitHub Repository](https://github.com/goodmami/wn)
- [Available WordNets Index](https://en-word.net/static/english-wordnet-2020.xml.gz)
- [WN-LMF Specification](https://globalwordnet.github.io/schemas/)
