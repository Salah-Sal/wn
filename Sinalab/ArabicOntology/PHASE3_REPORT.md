# Phase 3: Arabic-Specific Concepts Report

**Date:** 2026-01-12
**Source:** Arabic Ontology (SinaLab) → AWN3 (Arabic WordNet V3)

---

## Summary

Phase 3 added Arabic-specific concepts from Arabic Ontology that have no English translations and cannot be aligned to OEWN via ILI.

| Metric | Before Phase 3 | After Phase 3 | Change |
|--------|----------------|---------------|--------|
| Synsets | 10,201 | 14,829 | **+4,628** |
| Words | 16,252 | 24,011 | **+7,759** |
| Hypernym Relations | 9,363 | 10,618 | **+1,255** |
| ILI Coverage | 99.7% | 68.6% | -31.1% |

---

## Methodology

### Concept Selection Criteria
- No English translation (cannot align to OEWN)
- No word overlap with existing AWN3 (truly new concepts)
- Has Arabic definition (quality content)
- From Arabic Ontology's rich classical sources

### Process
1. Identified 4,628 Arabic-specific concepts
2. Created synsets without ILI links
3. Added Arabic words, definitions
4. Linked 1,255 synsets to AWN3 hierarchy via parent mapping

---

## Data Sources

| Source ID | Concepts | Description |
|-----------|----------|-------------|
| 43 | 2,456 | Modern Arabic terminology (with examples) |
| 38 | 1,217 | Classical Arabic terminology |
| 303 | 754 | Linguistic/grammatical terms |
| 200 | 201 | General vocabulary |

---

## Sample New Concepts

### Classical Arabic Terms (Source 38)
| Arabic | Gloss |
|--------|-------|
| الابتداء العُرفي | يطلق على الشيء الذي يقع قبل المقصود |
| إِبْدَالٌ | هو أن يُجْعَل حرف موضع حرف آخر لدفع الثِقل |
| إبَاضِيَّةٌ | هم المنسوبون الى عبد الله بن إبّاض |
| الأجوف | ما اعتلّ عينه كقال وباعَ |

### Modern Arabic Terms (Source 43)
| Arabic | Gloss |
|--------|-------|
| بَادِيَةٌ | أرض يسكنها البَدُو الرحالة |
| مُتَنَزَّهٌ | ملتقى يجتمع في الناس لتقضية الوقت |
| صَحْراء حارّة | صحراء رملية تتميز بأنها الأكثر جفافاً |

---

## Quality Metrics

- **Definition Coverage**: 97.2% (all new concepts have Arabic definitions)
- **Hypernym Coverage**: 1,255 synsets linked to AWN3 hierarchy (27.1%)
- **Orphan synsets**: 3,373 (no hypernym, Arabic-specific concepts)

---

## Files Generated

- `add_arabic_concepts_phase3.py` - Main script
- `phase3_candidates.csv` - All candidates analyzed
- `phase3_parent_mapping.csv` - Parent concept mappings
- `phase3_results.csv` - Successfully added synsets

---

## Notes

### ILI Coverage Trade-off
- Original AWN3: 99.7% ILI coverage
- After Phase 3: 68.6% ILI coverage
- The decrease is expected: Arabic-specific concepts cannot be cross-lingually aligned

### Orphan Synsets
- Many Arabic-specific concepts (especially classical terms) don't have direct hypernyms in AWN3
- These remain as isolated concepts but have rich Arabic definitions
- Future work could manually link these to appropriate hypernyms

---

## Combined Results (All Phases)

| Phase | Synsets | Words | Description |
|-------|---------|-------|-------------|
| Original | 9,567 | 13,496 | AWN3 base |
| Phase 1 | - | +1,786 | Vocabulary enrichment |
| Phase 2 | +634 | +970 | ILI-aligned concepts |
| Phase 3 | +4,628 | +7,759 | Arabic-specific concepts |
| **Total** | **14,829** | **24,011** | **+55% synsets, +78% words** |
