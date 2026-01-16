#!/usr/bin/env python3
"""
Phase 2: Add new ILI-aligned synsets from Arabic Ontology to AWN3.

This script:
1. Finds Arabic Ontology concepts with English translations
2. Maps them to OEWN synsets via English words
3. Creates new synsets in AWN3 with the same ILI
4. Adds Arabic words, definitions, and examples
"""

import pandas as pd
import wn
import re
from collections import defaultdict
from wn_editor import LexiconEditor, SynsetEditor

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


def get_ili_candidates():
    """Find Arabic Ontology concepts that can be aligned to new ILIs."""

    # Load Arabic Ontology
    concepts = pd.read_csv('Concepts.csv')

    ao_data = {}
    for idx, row in concepts.iterrows():
        cid = row['conceptId']

        if pd.notna(row['englishSynset']) and row['englishSynset'] != 'NULL':
            ao_data[cid] = {
                'english': [w.strip().lower() for w in str(row['englishSynset']).split('|')],
                'arabic': [w.strip() for w in str(row['arabicSynset']).split('|')] if pd.notna(row['arabicSynset']) else [],
                'gloss': str(row['gloss']) if pd.notna(row['gloss']) and row['gloss'] != 'NULL' else '',
                'example': str(row['example']) if pd.notna(row['example']) and row['example'] != 'NULL' else ''
            }

    # Get AWN3 existing ILIs
    awn3 = wn.Wordnet('awn3')
    awn3_ilis = set()
    for ss in awn3.synsets():
        if ss.ili:
            awn3_ilis.add(ss.ili.id)

    # Build OEWN word index
    oewn = wn.Wordnet('oewn:2024')
    oewn_word_to_synsets = defaultdict(list)
    for ss in oewn.synsets():
        for w in ss.words():
            oewn_word_to_synsets[w.lemma().lower()].append(ss)

    # Find candidates
    candidates = []
    seen_ilis = set()

    for ao_cid, ao_info in ao_data.items():
        for en_word in ao_info['english']:
            oewn_matches = oewn_word_to_synsets.get(en_word, [])

            for oewn_ss in oewn_matches:
                if oewn_ss.ili:
                    ili_id = oewn_ss.ili.id

                    # Skip if already in AWN3 or already processed
                    if ili_id in awn3_ilis or ili_id in seen_ilis:
                        continue

                    seen_ilis.add(ili_id)

                    candidates.append({
                        'ao_concept_id': ao_cid,
                        'ili_id': ili_id,
                        'pos': oewn_ss.pos,
                        'oewn_synset_id': oewn_ss.id,
                        'arabic_words': ao_info['arabic'][:MAX_WORDS_PER_SYNSET],
                        'arabic_gloss': ao_info['gloss'],
                        'arabic_example': ao_info['example'],
                        'oewn_definition': oewn_ss.definition()
                    })
                    break

            if ao_cid in [c['ao_concept_id'] for c in candidates]:
                break

    return candidates


def create_synset_with_ili(lex_editor, ili_id, pos, arabic_words, arabic_gloss, arabic_example):
    """Create a new synset with ILI link."""

    # Create the synset
    ss_editor = lex_editor.create_synset()

    # Set POS
    # Map 's' (satellite adjective) to 'a' for AWN3 compatibility
    if pos == 's':
        pos = 'a'
    ss_editor.set_pos(pos)

    # Set ILI
    try:
        ili_obj = wn.ili(ili_id)
        ss_editor.set_ili(ili_obj)
    except Exception as e:
        raise Exception(f"Failed to set ILI {ili_id}: {e}")

    # Add Arabic definition
    if arabic_gloss:
        ss_editor.add_definition(arabic_gloss, language='ar')

    # Add Arabic example
    if arabic_example:
        ss_editor.add_example(arabic_example, language='ar')

    # Add Arabic words
    for word in arabic_words:
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
    print("PHASE 2: ADD NEW ILI-ALIGNED SYNSETS")
    print("=" * 80)

    if DRY_RUN:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Get candidates
    print("\n[1/4] Finding ILI alignment candidates...")
    candidates = get_ili_candidates()
    print(f"  Found {len(candidates)} candidates")

    # Current stats
    print("\n[2/4] Current AWN3 statistics...")
    awn3 = wn.Wordnet('awn3')
    initial_synsets = len(list(awn3.synsets()))
    initial_words = len(list(awn3.words()))
    print(f"  Synsets: {initial_synsets:,}")
    print(f"  Words: {initial_words:,}")

    # Create synsets
    print("\n[3/4] Creating new synsets...")

    if DRY_RUN:
        print("  Skipping (dry run)")
        results = {'success': candidates, 'errors': []}
    else:
        lex_editor = LexiconEditor('awn3')

        results = {
            'success': [],
            'errors': []
        }

        for i, c in enumerate(candidates):
            if (i + 1) % 100 == 0:
                print(f"  Processing {i + 1}/{len(candidates)}...")

            try:
                ss_editor = create_synset_with_ili(
                    lex_editor,
                    c['ili_id'],
                    c['pos'],
                    c['arabic_words'],
                    c['arabic_gloss'],
                    c['arabic_example']
                )

                results['success'].append({
                    'ili_id': c['ili_id'],
                    'synset_id': ss_editor.as_synset().id if hasattr(ss_editor, 'as_synset') else 'unknown',
                    'pos': c['pos'],
                    'arabic_words': c['arabic_words'],
                    'ao_concept_id': c['ao_concept_id']
                })
            except Exception as e:
                results['errors'].append({
                    'ili_id': c['ili_id'],
                    'error': str(e)
                })

    # Report results
    print(f"\n[4/4] Results...")
    print(f"\n  Synsets created: {len(results['success'])}")
    print(f"  Errors: {len(results['errors'])}")

    # Verify
    if not DRY_RUN:
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

    # Export results
    if results['success']:
        df = pd.DataFrame([{
            'ili_id': r['ili_id'],
            'pos': r['pos'],
            'arabic_words': '|'.join(r['arabic_words']) if isinstance(r['arabic_words'], list) else r['arabic_words'],
            'ao_concept_id': r['ao_concept_id']
        } for r in results['success']])

        df.to_csv('phase2_results.csv', index=False)
        print(f"\n  Results saved to: phase2_results.csv")

    # Sample results
    print("\n--- Sample New Synsets ---")
    for r in results['success'][:10]:
        words = r['arabic_words'] if isinstance(r['arabic_words'], list) else r['arabic_words'].split('|')
        print(f"  {r['ili_id']} ({r['pos']}): {', '.join(words[:3])}")

    return results


if __name__ == '__main__':
    main()
