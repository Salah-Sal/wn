# AWN3 (Arabic WordNet V3) Quality Assessment Report

**Assessment Date:** 2026-01-12
**Source:** AWN V3 (Freihat et al. 2024) + OEWN relation inheritance

---

## Executive Summary

| Metric | Score | Grade |
|--------|-------|-------|
| Arabic Definition Coverage | 97.4% | ★★★★★ |
| Arabic Example Coverage | 96.7% | ★★★★★ |
| ILI Alignment | 99.7% | ★★★★★ |
| Taxonomy Coverage | 90.9% | ★★★★☆ |
| Synset Size (avg 1.29) | Good | ★★★★☆ |
| OEWN Coverage (by synset) | 7.9% | ★★☆☆☆ |

---

## Basic Statistics

| Metric | Value |
|--------|-------|
| Synsets | 9,567 |
| Words | 12,310 |
| Senses | 12,310 |
| ILI-linked | 9,539 (99.7%) |

### By Part of Speech

| POS | Count | Percentage |
|-----|-------|------------|
| Nouns | 6,511 | 68.1% |
| Verbs | 2,503 | 26.2% |
| Adjectives | 446 | 4.7% |
| Adverbs | 107 | 1.1% |

---

## Relation Statistics

| Metric | Value |
|--------|-------|
| Hypernym relations | 8,904 |
| Hyponym relations | 8,904 |
| Synsets with hypernym | 8,696 (90.9%) |
| Synsets with hyponym | 3,468 (36.2%) |
| Leaf synsets | 5,347 (55.9%) |
| Root synsets | 119 |
| Orphan synsets (no relations) | 752 (7.9%) |
| Average taxonomy depth | 6.43 |
| Maximum taxonomy depth | 14 |

---

## Content Quality

### Definitions

| Metric | Value |
|--------|-------|
| Synsets with Arabic definition | 9,315 (97.4%) |
| Synsets without definition | 252 (2.6%) |
| Average definition length | 53.2 chars |
| Definitions with diacritics | 2,227 (23.9%) |

### Examples

| Metric | Value |
|--------|-------|
| Synsets with Arabic examples | 9,254 (96.7%) |
| Synsets without examples | 313 (3.3%) |
| Average example length | 52.2 chars |

### Lexical Gaps

| Metric | Value |
|--------|-------|
| Empty synsets (lexical gaps) | 236 (2.5%) |

---

## Coverage Analysis

### vs OEWN (Open English WordNet 2024)

| Metric | AWN3 | OEWN | Coverage |
|--------|------|------|----------|
| Synsets | 9,567 | 120,630 | 7.9% |
| Nouns | 6,511 | 84,956 | 7.7% |
| Verbs | 2,503 | 13,830 | 18.1% |
| Adjectives | 446 | 7,502 | 5.9% |
| Adverbs | 107 | 3,622 | 3.0% |

### Synset Size Distribution

| Words per Synset | Count | Percentage |
|------------------|-------|------------|
| 0 (lexical gaps) | 236 | 2.5% |
| 1 | 6,984 | 73.0% |
| 2 | 1,886 | 19.7% |
| 3 | 348 | 3.6% |
| 4+ | 113 | 1.2% |

---

## ILI Alignment Quality

| Metric | Value |
|--------|-------|
| Synsets with ILI | 9,539 (99.7%) |
| Synsets without ILI | 28 (0.3%) |

### ILI Coverage by POS

| POS | With ILI | Total | Coverage |
|-----|----------|-------|----------|
| Noun | 6,503 | 6,511 | 99.9% |
| Verb | 2,483 | 2,503 | 99.2% |
| Adjective | 446 | 446 | 100.0% |
| Adverb | 107 | 107 | 100.0% |

### Cross-Lingual Alignment Samples

| Arabic | English (via ILI) |
|--------|-------------------|
| كلب | dog, domestic dog, Canis familiaris |
| سيارة | car, auto, automobile |
| كتاب | book |
| طعام | food, nutrient |
| شمس | sun, Sun |
| قمر | moon |

---

## Comparison with OMW-ARB v1.4

| Metric | AWN3 | OMW-ARB | Winner |
|--------|------|---------|--------|
| Synsets | 9,567 | 9,916 | OMW-ARB |
| Arabic Definitions | 97.4% | 0.0% | **AWN3** |
| Arabic Examples | 96.7% | 0.0% | **AWN3** |
| Hypernym Relations | 8,904 | 9,272 | OMW-ARB |
| Hyponym Relations | 8,904 | 57,352 | OMW-ARB |
| Words | 12,310 | 18,003 | OMW-ARB |
| ILI Coverage | 99.7% | 100.0% | Tie |

### ILI-based Overlap

| Category | Count |
|----------|-------|
| Concepts in both AWN3 and OMW-ARB | 9,296 |
| Concepts only in AWN3 | 243 |
| Concepts only in OMW-ARB | 620 |

---

## Issues Identified

### High Priority

1. **Orphan synsets (752)** - No relations, isolated in taxonomy
2. **Missing relations** - Only hypernym/hyponym inherited (no meronym, holonym, domain, similar, etc.)
3. **Empty synsets (236)** - Lexical gaps with no Arabic words

### Medium Priority

4. **Low polysemy (0%)** - Each word appears in only 1 synset (may indicate over-splitting or data limitation)
5. **28 synsets without ILI** - Cannot cross-reference to English
6. **252 synsets without definitions**

### Low Priority

7. Mixed Arabic/Latin text in 9 definitions
8. Only 23.9% of definitions have diacritics

---

## Recommendations

### Immediate

1. **Inherit additional relation types from OEWN:**
   - Meronym/holonym relations
   - Domain relations
   - Similar/also relations

2. **Review and connect orphan synsets (752)**

3. **Fill lexical gaps where possible (236 empty synsets)**

### Future

4. **Consider merging with OMW-ARB** to get:
   - Additional Arabic lemmas (5,693 more words)
   - More hyponym relations (48,448 more)

5. **Add polysemy** - link same Arabic words to multiple synsets where appropriate

6. **Expand coverage** toward OEWN's 120,630 synsets

---

## Conclusion

AWN3 represents a **significant improvement** over OMW-ARB for Arabic lexical content quality, with 97%+ coverage of native Arabic definitions and examples. However, it has fewer synsets, words, and relations than OMW-ARB.

The ideal future Arabic WordNet would combine:
- AWN3's Arabic definitions and examples (97%+ coverage)
- OMW-ARB's extensive relation network (57K+ hyponyms)
- Expanded coverage toward OEWN's 120K+ concepts

---

## Technical Details

### Files

- **LMF XML:** `/wn/AWN3.0/awn3.xml` (5.3 MB)
- **Generator Script:** `/wn/scripts/generate_awn3_lmf.py`
- **Relation Inheritance Script:** `/wn/scripts/inherit_relations.py`

### Usage

```python
import wn

# Load AWN3
awn3 = wn.Wordnet('awn3')

# Query Arabic words
for ss in awn3.synsets('كلب'):
    print(ss.definition())
    print('Hypernyms:', ss.hypernyms())

# Cross-lingual lookup via ILI
oewn = wn.Wordnet('oewn:2024')
for ss in awn3.synsets('كيان'):
    for en_ss in oewn.synsets(ili=ss.ili):
        print(f'{ss.words()[0].lemma()} → {en_ss.words()[0].lemma()}')
```
