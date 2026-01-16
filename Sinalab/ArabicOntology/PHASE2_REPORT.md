# Phase 2: New ILI-Aligned Concepts Report

**Date:** 2026-01-12
**Source:** Arabic Ontology (SinaLab) → AWN3 (Arabic WordNet V3)

---

## Summary

Phase 2 added new concepts from Arabic Ontology that have English translations, aligning them to OEWN via ILI.

| Metric | Before Phase 2 | After Phase 2 | Change |
|--------|----------------|---------------|--------|
| Synsets | 9,568 | 10,201 | **+633** |
| Words | 15,282 | 16,252 | **+970** |
| Hypernym Relations | 8,904 | 9,363 | **+459** |
| ILI Coverage | 99.7% | 99.7% | - |

---

## Methodology

### Alignment Strategy
1. Found Arabic Ontology concepts with English translations (1,894 concepts)
2. Matched English words to OEWN synsets
3. Extracted ILI identifiers from OEWN
4. Filtered out ILIs already present in AWN3
5. Created new synsets with proper ILI links

### Process
1. **Candidate Identification**: 633 unique new ILIs found
2. **Synset Creation**: Created new synsets with:
   - Arabic words from Arabic Ontology
   - Arabic definitions (75.5% coverage)
   - Arabic examples (50.3% coverage)
   - ILI links for cross-lingual alignment
3. **Relation Inheritance**: Added 459 hypernym relations from OEWN

---

## Results by POS

| POS | New Synsets |
|-----|-------------|
| Noun | 446 |
| Verb | 91 |
| Adjective (satellite) | 55 |
| Adjective | 16 |
| Adverb | 4 |

---

## Sample New Concepts

| ILI | Arabic | English Equivalent |
|-----|--------|-------------------|
| i64973 | الغدة الكظرية | adrenal gland |
| i65764 | غدة نُخَامِيّة | pituitary gland |
| i56039 | مَسْجِدٌ, جَامِعٌ | mosque |
| i52081 | منجم فحم | coal mine |
| i52995 | مصنع التقطير | distillery |
| i52784 | عَرينٌ | den (animal lair) |
| i45121 | زَرِيبَةٌ, حَظِيرَةٌ | pen (animal enclosure) |

---

## Quality Metrics

- **ILI Coverage**: 99.7% (all new synsets have ILI)
- **Definition Coverage**: 96.0%
- **Example Coverage**: 93.9%
- **Hypernym Coverage**: 89.7%

---

## Files Generated

- `add_new_synsets_phase2.py` - Main script for adding synsets
- `phase2_candidates.csv` - All alignment candidates
- `phase2_results.csv` - Successfully added synsets

---

## Combined Results (Phase 1 + Phase 2)

| Metric | Original AWN3 | After Both Phases | Total Change |
|--------|---------------|-------------------|--------------|
| **Synsets** | 9,567 | 10,201 | **+634 (+6.6%)** |
| **Words** | 13,496 | 16,252 | **+2,756 (+20.4%)** |
| **Relations** | 8,904 | 9,363 | **+459 (+5.2%)** |

---

## Next Steps (Optional)

### Phase 3: Arabic-Specific Concepts
- ~6,000 concepts from Arabic Ontology without English translations
- These would not have ILI links
- Useful for Arabic-specific terminology
- Requires careful curation

---

## Technical Notes

- New synsets have IDs starting with `awn3-15318835-u`
- POS code 's' (satellite adjective) mapped to 'a' for compatibility
- Hypernym relations inherited from OEWN where target exists in AWN3
