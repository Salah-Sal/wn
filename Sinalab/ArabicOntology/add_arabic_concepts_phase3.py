#!/usr/bin/env python3
"""
Phase 3: Add Arabic-specific concepts from Arabic Ontology to AWN3.

These concepts:
- Have no English translations (cannot be aligned to OEWN via ILI)
- Have no word overlap with AWN3 (truly new concepts)
- Have Arabic definitions (quality content)
- Will NOT have ILI links (Arabic-specific)
- Will be linked to AWN3 hierarchy where parent mapping exists
"""

import pandas as pd
import wn
import re
from collections import defaultdict
from wn_editor import LexiconEditor, SynsetEditor, RelationType, _set_relation_to_synset

# =============================================================================
# CONFIGURATION
# =============================================================================

# Maximum words per new synset
MAX_WORDS_PER_SYNSET = 5

# Dry run mode
DRY_RUN = False

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_arabic(text):
    """Normalize Arabic text."""
    if pd.isna(text) or text is None:
        return None
    text = str(text)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text.strip()


def build_parent_mapping():
    """Build mapping from AO parent concepts to AWN3 synsets."""

    concepts = pd.read_csv('Concepts.csv')
    awn3 = wn.Wordnet('awn3')

    # Build AWN3 word -> synset index
    awn3_word_to_synsets = defaultdict(list)
    for ss in awn3.synsets():
        for w in ss.words():
            norm = normalize_arabic(w.lemma())
            if norm:
                awn3_word_to_synsets[norm].append(ss)

    # Build AO concept words
    ao_concept_words = {}
    for idx, row in concepts.iterrows():
        cid = row['conceptId']
        if pd.notna(row['arabicSynset']):
            words = [w.strip() for w in str(row['arabicSynset']).split('|')]
            ao_concept_words[cid] = [normalize_arabic(w) for w in words if normalize_arabic(w)]

    # Load parent mapping from Phase 3 analysis
    parent_mapping = pd.read_csv('phase3_parent_mapping.csv')

    parent_to_awn3 = {}
    for _, row in parent_mapping.iterrows():
        ao_parent_id = int(row['ao_parent_id'])
        awn3_synset_id = row['awn3_synset_id']

        # Find the actual synset object
        for ss in awn3.synsets():
            if ss.id == awn3_synset_id:
                parent_to_awn3[ao_parent_id] = ss
                break

    return parent_to_awn3


def create_arabic_synset(lex_editor, arabic_words, gloss, example, pos='n'):
    """Create a new Arabic-specific synset (no ILI)."""

    # Create the synset
    ss_editor = lex_editor.create_synset()

    # Set POS (default to noun for Arabic terms)
    ss_editor.set_pos(pos)

    # Add Arabic definition
    if gloss:
        ss_editor.add_definition(gloss, language='ar')

    # Add Arabic example
    if example:
        ss_editor.add_example(example, language='ar')

    # Add Arabic words
    for word in arabic_words[:MAX_WORDS_PER_SYNSET]:
        if word and word.strip():
            try:
                ss_editor.add_word(word.strip())
            except Exception as e:
                pass  # Skip problematic words

    return ss_editor


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 80)
    print("PHASE 3: ADD ARABIC-SPECIFIC CONCEPTS")
    print("=" * 80)

    if DRY_RUN:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Load candidates
    print("\n[1/5] Loading Phase 3 candidates...")
    candidates = pd.read_csv('phase3_candidates.csv')
    print(f"  Candidates: {len(candidates):,}")

    # Build parent mapping
    print("\n[2/5] Building parent mapping...")
    parent_to_awn3 = build_parent_mapping()
    print(f"  Parent mappings loaded: {len(parent_to_awn3)}")

    # Current stats
    print("\n[3/5] Current AWN3 statistics...")
    awn3 = wn.Wordnet('awn3')
    initial_synsets = len(list(awn3.synsets()))
    initial_words = len(list(awn3.words()))
    print(f"  Synsets: {initial_synsets:,}")
    print(f"  Words: {initial_words:,}")

    # Create synsets
    print("\n[4/5] Creating Arabic-specific synsets...")

    if DRY_RUN:
        print("  Skipping (dry run)")
        return

    lex_editor = LexiconEditor('awn3')

    results = {
        'success': [],
        'with_hypernym': [],
        'errors': []
    }

    # Keep track of created synsets for linking
    created_synsets = {}  # ao_concept_id -> SynsetEditor

    for i, row in candidates.iterrows():
        if (i + 1) % 500 == 0:
            print(f"  Processing {i + 1}/{len(candidates)}...")

        try:
            # Parse data
            arabic_words = row['arabic_words'].split('|') if pd.notna(row['arabic_words']) else []
            gloss = row['gloss'] if pd.notna(row['gloss']) else ''
            example = ''  # Example is in has_example column but actual text not stored
            parent_id = int(row['parent_id']) if pd.notna(row['parent_id']) else None
            concept_id = row['concept_id']

            # Create synset
            ss_editor = create_arabic_synset(
                lex_editor,
                arabic_words,
                gloss,
                example,
                pos='n'  # Default to noun
            )

            synset = ss_editor.as_synset()
            created_synsets[concept_id] = synset

            # Try to link to parent
            hypernym_added = False
            if parent_id and parent_id in parent_to_awn3:
                try:
                    parent_synset = parent_to_awn3[parent_id]
                    _set_relation_to_synset(synset, parent_synset, RelationType.hypernym)
                    hypernym_added = True
                    results['with_hypernym'].append(concept_id)
                except Exception as e:
                    pass

            results['success'].append({
                'ao_concept_id': concept_id,
                'synset_id': synset.id,
                'arabic_words': arabic_words[:3],
                'has_hypernym': hypernym_added
            })

        except Exception as e:
            results['errors'].append({
                'ao_concept_id': row['concept_id'],
                'error': str(e)
            })

    # Report results
    print(f"\n[5/5] Results...")
    print(f"\n  Synsets created: {len(results['success'])}")
    print(f"  With hypernym: {len(results['with_hypernym'])}")
    print(f"  Errors: {len(results['errors'])}")

    # Verify
    print("\n--- Verification ---")
    awn3_new = wn.Wordnet('awn3')
    final_synsets = len(list(awn3_new.synsets()))
    final_words = len(list(awn3_new.words()))

    print(f"  Initial synsets: {initial_synsets:,}")
    print(f"  Final synsets: {final_synsets:,}")
    print(f"  Net increase: {final_synsets - initial_synsets:,}")
    print(f"\n  Initial words: {initial_words:,}")
    print(f"  Final words: {final_words:,}")
    print(f"  Net increase: {final_words - initial_words:,}")

    # ILI coverage
    with_ili = sum(1 for ss in awn3_new.synsets() if ss.ili)
    print(f"\n  Synsets with ILI: {with_ili:,} ({with_ili/final_synsets*100:.1f}%)")

    # Export results
    df = pd.DataFrame([{
        'ao_concept_id': r['ao_concept_id'],
        'synset_id': r['synset_id'],
        'arabic_words': '|'.join(r['arabic_words']),
        'has_hypernym': r['has_hypernym']
    } for r in results['success']])

    df.to_csv('phase3_results.csv', index=False)
    print(f"\n  Results saved to: phase3_results.csv")

    # Sample results
    print("\n--- Sample New Arabic-Specific Synsets ---")
    for r in results['success'][:10]:
        words = ', '.join(r['arabic_words'])
        hyper = "✓" if r['has_hypernym'] else "✗"
        print(f"  {r['synset_id']}: {words} [hypernym: {hyper}]")

    return results


if __name__ == '__main__':
    main()
