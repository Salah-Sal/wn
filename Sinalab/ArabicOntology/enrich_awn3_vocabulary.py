#!/usr/bin/env python3
"""
Phase 1: Vocabulary Enrichment - Add Arabic words from Arabic Ontology to AWN3.

This script:
1. Identifies high-confidence alignments between AO concepts and AWN3 synsets
2. Adds new Arabic words from AO to the matched AWN3 synsets
3. Generates a detailed report of changes
"""

import pandas as pd
import wn
import re
from collections import defaultdict
from wn_editor import SynsetEditor

# =============================================================================
# CONFIGURATION
# =============================================================================

# Only add words from 1-to-1 matches (highest confidence)
HIGH_CONFIDENCE_ONLY = True

# Minimum gloss similarity threshold (0-1) for additional validation
# Set to 0 to skip similarity check
MIN_GLOSS_SIMILARITY = 0.0

# Dry run mode - if True, don't actually modify the database
DRY_RUN = False

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def normalize_arabic(text):
    """Normalize Arabic text for matching."""
    if pd.isna(text) or text is None:
        return None
    text = str(text)
    # Remove diacritics (tashkeel)
    text = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Normalize alef variants
    text = re.sub(r'[إأآا]', 'ا', text)
    # Normalize taa marbuta
    text = re.sub(r'ة', 'ه', text)
    # Normalize yaa
    text = re.sub(r'ى', 'ي', text)
    return text.strip()


def load_arabic_ontology(csv_path='Concepts.csv'):
    """Load Arabic Ontology data."""
    concepts = pd.read_csv(csv_path)

    ao_word_to_concepts = defaultdict(list)
    ao_concept_to_words = {}
    ao_concept_to_gloss = {}
    ao_concept_to_english = {}

    for idx, row in concepts.iterrows():
        cid = row['conceptId']
        ar_synset = row['arabicSynset']
        gloss = row['gloss']
        english = row['englishSynset']

        if pd.notna(ar_synset):
            words = [w.strip() for w in str(ar_synset).split('|')]
            ao_concept_to_words[cid] = words
            for word in words:
                norm = normalize_arabic(word)
                if norm:
                    ao_word_to_concepts[norm].append(cid)

        if pd.notna(gloss) and gloss != 'NULL':
            ao_concept_to_gloss[cid] = str(gloss)

        if pd.notna(english) and english != 'NULL':
            ao_concept_to_english[cid] = str(english)

    return {
        'word_to_concepts': ao_word_to_concepts,
        'concept_to_words': ao_concept_to_words,
        'concept_to_gloss': ao_concept_to_gloss,
        'concept_to_english': ao_concept_to_english
    }


def load_awn3_indexes():
    """Load AWN3 data indexes."""
    awn3 = wn.Wordnet('awn3')

    awn3_word_to_synsets = defaultdict(list)
    awn3_synset_to_words = {}
    awn3_synset_to_words_norm = {}
    awn3_synset_to_gloss = {}
    awn3_synset_objects = {}

    for ss in awn3.synsets():
        ss_id = ss.id
        words = [w.lemma() for w in ss.words()]
        words_norm = set(normalize_arabic(w) for w in words if normalize_arabic(w))

        awn3_synset_to_words[ss_id] = words
        awn3_synset_to_words_norm[ss_id] = words_norm
        awn3_synset_to_gloss[ss_id] = ss.definition()
        awn3_synset_objects[ss_id] = ss

        for word in words:
            norm = normalize_arabic(word)
            if norm:
                awn3_word_to_synsets[norm].append(ss)

    return {
        'word_to_synsets': awn3_word_to_synsets,
        'synset_to_words': awn3_synset_to_words,
        'synset_to_words_norm': awn3_synset_to_words_norm,
        'synset_to_gloss': awn3_synset_to_gloss,
        'synset_objects': awn3_synset_objects
    }


def find_high_confidence_alignments(ao_data, awn3_data):
    """Find 1-to-1 word alignments between AO and AWN3."""
    alignments = []

    ao_words = set(ao_data['word_to_concepts'].keys())
    awn3_words = set(awn3_data['word_to_synsets'].keys())
    common_words = ao_words & awn3_words

    for norm_word in common_words:
        ao_cids = ao_data['word_to_concepts'][norm_word]
        awn3_synsets = awn3_data['word_to_synsets'][norm_word]

        # Only 1-to-1 matches for high confidence
        if len(ao_cids) == 1 and len(awn3_synsets) == 1:
            ao_cid = ao_cids[0]
            awn3_ss = awn3_synsets[0]

            # Get words from AO that are not in AWN3
            ao_words_list = ao_data['concept_to_words'].get(ao_cid, [])
            awn3_words_norm = awn3_data['synset_to_words_norm'].get(awn3_ss.id, set())

            new_words = [w for w in ao_words_list if normalize_arabic(w) not in awn3_words_norm]

            if new_words:
                alignments.append({
                    'matched_word': norm_word,
                    'ao_concept_id': ao_cid,
                    'awn3_synset_id': awn3_ss.id,
                    'awn3_synset': awn3_ss,
                    'ao_words': ao_words_list,
                    'awn3_words': awn3_data['synset_to_words'].get(awn3_ss.id, []),
                    'ao_gloss': ao_data['concept_to_gloss'].get(ao_cid, ''),
                    'awn3_gloss': awn3_data['synset_to_gloss'].get(awn3_ss.id, ''),
                    'new_words': new_words
                })

    return alignments


def add_words_to_synset(synset, words, dry_run=False):
    """Add words to a synset using wn_editor."""
    added = []
    errors = []

    if dry_run:
        return words, []

    try:
        ss_editor = SynsetEditor(synset)

        for word in words:
            try:
                ss_editor.add_word(word)
                added.append(word)
            except Exception as e:
                errors.append({'word': word, 'error': str(e)})

    except Exception as e:
        errors.append({'word': 'ALL', 'error': str(e)})

    return added, errors


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 80)
    print("PHASE 1: VOCABULARY ENRICHMENT")
    print("Adding Arabic words from Arabic Ontology to AWN3")
    print("=" * 80)

    if DRY_RUN:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Load data
    print("\n[1/4] Loading data...")
    ao_data = load_arabic_ontology()
    awn3_data = load_awn3_indexes()

    print(f"  Arabic Ontology: {len(ao_data['concept_to_words']):,} concepts")
    print(f"  AWN3: {len(awn3_data['synset_objects']):,} synsets")

    # Find alignments
    print("\n[2/4] Finding high-confidence alignments...")
    alignments = find_high_confidence_alignments(ao_data, awn3_data)

    total_new_words = sum(len(a['new_words']) for a in alignments)
    print(f"  Alignments found: {len(alignments)}")
    print(f"  Total new words to add: {total_new_words}")

    # Process alignments
    print("\n[3/4] Adding words to synsets...")

    results = {
        'success': [],
        'errors': [],
        'skipped': []
    }

    for i, alignment in enumerate(alignments):
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(alignments)}...")

        added, errors = add_words_to_synset(
            alignment['awn3_synset'],
            alignment['new_words'],
            dry_run=DRY_RUN
        )

        if added:
            results['success'].append({
                'synset_id': alignment['awn3_synset_id'],
                'matched_word': alignment['matched_word'],
                'existing_words': alignment['awn3_words'],
                'added_words': added,
                'ao_concept_id': alignment['ao_concept_id']
            })

        if errors:
            results['errors'].append({
                'synset_id': alignment['awn3_synset_id'],
                'errors': errors
            })

    # Generate report
    print("\n[4/4] Generating report...")

    print("\n" + "=" * 80)
    print("ENRICHMENT RESULTS")
    print("=" * 80)

    total_added = sum(len(r['added_words']) for r in results['success'])

    print(f"\n  Synsets enriched: {len(results['success'])}")
    print(f"  Total words added: {total_added}")
    print(f"  Errors: {len(results['errors'])}")

    # Sample successful enrichments
    print("\n--- Sample Enrichments ---")
    for r in results['success'][:15]:
        existing = ', '.join(r['existing_words'][:2])
        added = ', '.join(r['added_words'][:3])
        print(f"  {r['synset_id']}: [{existing}] + [{added}]")

    # Export results to CSV
    if results['success']:
        df = pd.DataFrame([
            {
                'synset_id': r['synset_id'],
                'ao_concept_id': r['ao_concept_id'],
                'matched_word': r['matched_word'],
                'existing_words': '|'.join(r['existing_words']),
                'added_words': '|'.join(r['added_words'])
            }
            for r in results['success']
        ])
        df.to_csv('enrichment_report.csv', index=False)
        print(f"\n  Report saved to: enrichment_report.csv")

    # Verification
    if not DRY_RUN:
        print("\n--- Verification ---")
        awn3_new = wn.Wordnet('awn3')
        new_word_count = len(list(awn3_new.words()))
        print(f"  AWN3 total words after enrichment: {new_word_count:,}")

    return results


if __name__ == '__main__':
    main()
