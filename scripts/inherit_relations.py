#!/usr/bin/env python3
"""
Inherit semantic relations from OEWN to AWN3 via ILI mapping.

This script:
1. Builds ILI → synset mappings for both AWN3 and OEWN
2. For each AWN3 synset, finds corresponding OEWN synset via ILI
3. Copies hypernym/hyponym relations where both source and target exist in AWN3
"""

import wn
from wn_editor import LexiconEditor, SynsetEditor, RelationType, _set_relation_to_synset
from collections import defaultdict

def build_ili_mapping(wordnet):
    """Build ILI ID -> synset mapping for a wordnet."""
    ili_to_synset = {}
    for ss in wordnet.synsets():
        ili = ss.ili
        if ili:
            ili_to_synset[ili.id] = ss
    return ili_to_synset


def inherit_relations():
    """Inherit relations from OEWN to AWN3."""

    print("=== Loading Wordnets ===")
    awn3 = wn.Wordnet('awn3')
    oewn = wn.Wordnet('oewn:2024')

    print(f"AWN3 synsets: {len(list(awn3.synsets()))}")
    print(f"OEWN synsets: {len(list(oewn.synsets()))}")

    # Build ILI mappings
    print("\n=== Building ILI Mappings ===")
    awn3_ili_to_synset = build_ili_mapping(awn3)
    oewn_ili_to_synset = build_ili_mapping(oewn)

    print(f"AWN3 synsets with ILI: {len(awn3_ili_to_synset)}")
    print(f"OEWN synsets with ILI: {len(oewn_ili_to_synset)}")

    # Find common ILIs
    common_ilis = set(awn3_ili_to_synset.keys()) & set(oewn_ili_to_synset.keys())
    print(f"Common ILIs: {len(common_ilis)}")

    # Track statistics
    stats = {
        'hypernym_added': 0,
        'hyponym_added': 0,
        'hypernym_skipped_no_target': 0,
        'hyponym_skipped_no_target': 0,
        'synsets_with_relations': 0,
        'errors': 0
    }

    # Get LexiconEditor for AWN3
    lex_editor = LexiconEditor('awn3')

    print("\n=== Inheriting Relations ===")
    processed = 0

    for ili_id in common_ilis:
        awn3_synset = awn3_ili_to_synset[ili_id]
        oewn_synset = oewn_ili_to_synset[ili_id]

        has_relation = False

        # Get OEWN hypernyms
        for oewn_hyper in oewn_synset.hypernyms():
            hyper_ili = oewn_hyper.ili
            if hyper_ili and hyper_ili.id in awn3_ili_to_synset:
                # Found a hypernym that exists in AWN3
                awn3_target = awn3_ili_to_synset[hyper_ili.id]
                try:
                    _set_relation_to_synset(awn3_synset, awn3_target, RelationType.hypernym)
                    stats['hypernym_added'] += 1
                    has_relation = True
                except Exception as e:
                    stats['errors'] += 1
            else:
                stats['hypernym_skipped_no_target'] += 1

        # Get OEWN hyponyms
        for oewn_hypo in oewn_synset.hyponyms():
            hypo_ili = oewn_hypo.ili
            if hypo_ili and hypo_ili.id in awn3_ili_to_synset:
                # Found a hyponym that exists in AWN3
                awn3_target = awn3_ili_to_synset[hypo_ili.id]
                try:
                    _set_relation_to_synset(awn3_synset, awn3_target, RelationType.hyponym)
                    stats['hyponym_added'] += 1
                    has_relation = True
                except Exception as e:
                    stats['errors'] += 1
            else:
                stats['hyponym_skipped_no_target'] += 1

        if has_relation:
            stats['synsets_with_relations'] += 1

        processed += 1
        if processed % 1000 == 0:
            print(f"Processed {processed}/{len(common_ilis)} synsets...")

    print(f"\n=== Relation Inheritance Complete ===")
    print(f"Synsets processed: {processed}")
    print(f"Synsets with relations added: {stats['synsets_with_relations']}")
    print(f"Hypernym relations added: {stats['hypernym_added']}")
    print(f"Hyponym relations added: {stats['hyponym_added']}")
    print(f"Hypernyms skipped (target not in AWN3): {stats['hypernym_skipped_no_target']}")
    print(f"Hyponyms skipped (target not in AWN3): {stats['hyponym_skipped_no_target']}")
    print(f"Errors: {stats['errors']}")

    # Verify
    print("\n=== Verification ===")
    awn3_refreshed = wn.Wordnet('awn3')
    with_relations = sum(1 for ss in awn3_refreshed.synsets() if ss.hypernyms() or ss.hyponyms())
    print(f"AWN3 synsets with relations: {with_relations}")


if __name__ == '__main__':
    inherit_relations()
