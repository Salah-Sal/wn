# AWN3 Enriched Export

**Export Date:** 2026-01-12 05:30:40

## Statistics

| Metric | Value |
|--------|-------|
| Synsets | 14,829 |
| Words | 24,011 |
| ILI Coverage | 68.6% |
| With Definitions | 14,419 |
| With Examples | 9,574 |

## POS Distribution

| POS | Count |
|-----|-------|
| Noun (n) | 11,597 |
| Verb (v) | 2,602 |
| Adjective (a) | 518 |
| Adverb (r) | 111 |
| Unknown | 1 |

## Files

- `awn3_enriched_latest.xml` - LMF XML format (use for import)
- `wn_database_*.db` - SQLite database backup
- `awn3_enriched_stats.json` - Statistics in JSON format

## Enrichment Phases

This AWN3 was enriched from the original Arabic WordNet with data from Arabic Ontology (SinaLab):

1. **Phase 1**: Vocabulary enrichment (+1,786 words)
2. **Phase 2**: ILI-aligned new concepts (+634 synsets)
3. **Phase 3**: Arabic-specific concepts (+4,628 synsets)

## How to Import

```python
import wn

# Import the enriched AWN3
wn.download('file:awn3_enriched_latest.xml')
```

## License

Arabic WordNet is distributed under [original AWN license].
Arabic Ontology data from SinaLab (see Arabic Ontology license).
