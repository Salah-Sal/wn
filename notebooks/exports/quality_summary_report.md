
# Arabic WordNet Quality Evaluation Report

**Generated:** 2026-01-12 02:17:10

## Lexicon Information
- **ID:** omw-arb
- **Version:** 1.4
- **Label:** Arabic WordNet (AWN v2)
- **Language:** arb

## Summary Statistics
| Metric | Value |
|--------|-------|
| Total Words | 18,003 |
| Total Senses | 37,342 |
| Total Synsets | 9,916 |
| Nouns | 10,344 words, 6,884 synsets |
| Verbs | 6,728 words, 2,484 synsets |
| Adjectives | 693 words, 443 synsets |
| Adverbs | 238 words, 105 synsets |

## Quality Indicators
| Indicator | Value |
|-----------|-------|
| ILI Coverage | 100.0% |
| Definition Coverage | 0.0% |
| Core Vocabulary Coverage | 87.3% |
| Singleton Synsets | 37.2% |

## Issues Found
- Structural issues: 2
- Encoding issues: 14
- ILI mapping issues: 0
- Alignment issues: 680

## Recommendations

1. **[High]** Only 0.0% have Arabic definitions
   - Add Arabic definitions to improve usability for Arabic speakers

2. **[Medium]** 37.2% synsets have only one word
   - Enrich synsets with additional synonyms

3. **[Medium]** 782 synsets have 10+ words (potential over-lumping)
   - Review large synsets for potential splitting

4. **[Medium]** 512 words have 10+ senses (potential over-splitting)
   - Review highly polysemous words for sense merging opportunities

5. **[Low]** 14 encoding/formatting issues detected
   - Clean up encoding issues for data consistency

## Exported Files
- `alignment_issues.csv` (85,388 bytes)
- `annotation_guidelines.md` (1,341 bytes)
- `completeness_audit.csv` (98,206 bytes)
- `coverage_comparison.png` (34,966 bytes)
- `coverage_summary.csv` (438 bytes)
- `definition_samples.csv` (4 bytes)
- `domain_coverage.csv` (689 bytes)
- `encoding_issues.csv` (857 bytes)
- `executive_summary.png` (91,605 bytes)
- `highly_polysemous_words.csv` (1,035 bytes)
- `morphological_analysis.csv` (73,870 bytes)
- `polysemy_distribution.png` (44,363 bytes)
- `quality_radar.png` (226,390 bytes)
- `recommendations.csv` (598 bytes)
- `relation_statistics.csv` (368 bytes)
- `review_sample_adjectives.csv` (6,850 bytes)
- `review_sample_adverbs.csv` (7,322 bytes)
- `review_sample_full.json` (100,270 bytes)
- `review_sample_nouns.csv` (8,468 bytes)
- `review_sample_verbs.csv` (9,469 bytes)
- `structural_issues.csv` (14,329 bytes)
- `synset_samples_for_review.csv` (4,936 bytes)
- `taxonomy_depth.png` (61,967 bytes)
- `translation_samples_for_review.csv` (14,190 bytes)
- `vocabulary_gaps.csv` (1,339 bytes)
