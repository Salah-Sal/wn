#!/usr/bin/env python3
"""
Export the enriched AWN3 (Arabic WordNet V3) for preservation and distribution.

This script exports:
1. LMF XML format (standard interchange format)
2. Database backup (SQLite)
3. Statistics summary
"""

import wn
from wn import lmf
import shutil
from pathlib import Path
from datetime import datetime
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

OUTPUT_DIR = Path('awn3_enriched_export')
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

# =============================================================================
# MAIN EXPORT
# =============================================================================

def main():
    print("=" * 80)
    print("EXPORTING ENRICHED AWN3 (Arabic WordNet V3)")
    print("=" * 80)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")

    # Load AWN3
    print("\n[1/4] Loading AWN3...")
    awn3 = wn.Wordnet('awn3')

    # Collect statistics
    synsets = list(awn3.synsets())
    words = list(awn3.words())

    stats = {
        'export_date': TIMESTAMP,
        'wordnet_id': 'awn3',
        'synsets': len(synsets),
        'words': len(words),
        'ili_coverage': sum(1 for ss in synsets if ss.ili) / len(synsets) * 100,
        'pos_distribution': {},
        'with_definitions': sum(1 for ss in synsets if ss.definitions()),
        'with_examples': sum(1 for ss in synsets if ss.examples()),
    }

    # POS distribution
    for ss in synsets:
        pos = ss.pos if ss.pos else 'unknown'
        stats['pos_distribution'][pos] = stats['pos_distribution'].get(pos, 0) + 1

    print(f"  Synsets: {stats['synsets']:,}")
    print(f"  Words: {stats['words']:,}")
    print(f"  ILI coverage: {stats['ili_coverage']:.1f}%")

    # Export to LMF XML
    print("\n[2/4] Exporting to LMF XML...")
    xml_path = OUTPUT_DIR / f'awn3_enriched_{TIMESTAMP}.xml'
    # Use wn.export with lexicons (not lmf.dump)
    wn.export(awn3.lexicons(), str(xml_path))
    print(f"  Saved: {xml_path}")
    print(f"  Size: {xml_path.stat().st_size / 1024 / 1024:.2f} MB")

    # Also create a version without timestamp for easy reference
    xml_latest = OUTPUT_DIR / 'awn3_enriched_latest.xml'
    shutil.copy(xml_path, xml_latest)
    print(f"  Also saved as: {xml_latest}")

    # Backup database
    print("\n[3/4] Backing up database...")
    db_source = Path(wn.config.database_path)
    db_backup = OUTPUT_DIR / f'wn_database_{TIMESTAMP}.db'
    shutil.copy(db_source, db_backup)
    print(f"  Saved: {db_backup}")
    print(f"  Size: {db_backup.stat().st_size / 1024 / 1024:.2f} MB")

    # Save statistics
    print("\n[4/4] Saving statistics...")
    stats_path = OUTPUT_DIR / 'awn3_enriched_stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {stats_path}")

    # Create README
    readme_content = f"""# AWN3 Enriched Export

**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics

| Metric | Value |
|--------|-------|
| Synsets | {stats['synsets']:,} |
| Words | {stats['words']:,} |
| ILI Coverage | {stats['ili_coverage']:.1f}% |
| With Definitions | {stats['with_definitions']:,} |
| With Examples | {stats['with_examples']:,} |

## POS Distribution

| POS | Count |
|-----|-------|
| Noun (n) | {stats['pos_distribution'].get('n', 0):,} |
| Verb (v) | {stats['pos_distribution'].get('v', 0):,} |
| Adjective (a) | {stats['pos_distribution'].get('a', 0):,} |
| Adverb (r) | {stats['pos_distribution'].get('r', 0):,} |
| Unknown | {stats['pos_distribution'].get('unknown', 0):,} |

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
"""

    readme_path = OUTPUT_DIR / 'README.md'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"  Saved: {readme_path}")

    # Summary
    print("\n" + "=" * 80)
    print("EXPORT COMPLETE")
    print("=" * 80)
    print(f"\nAll files saved to: {OUTPUT_DIR.absolute()}")
    print("\nFiles generated:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        size = f.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / 1024 / 1024:.2f} MB"
        else:
            size_str = f"{size / 1024:.1f} KB"
        print(f"  - {f.name} ({size_str})")

    print("\n--- How to use the export ---")
    print("1. To share: Use awn3_enriched_latest.xml (LMF format)")
    print("2. To restore: Copy wn_database_*.db to ~/.wn_data/wn.db")
    print("3. To import in fresh environment:")
    print("   wn.download('file:/path/to/awn3_enriched_latest.xml')")

    return stats


if __name__ == '__main__':
    main()
