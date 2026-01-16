#!/usr/bin/env python3
"""
Enhance AWN3 with additional relations from OEWN.

This script:
1. Inherits meronym/holonym relations (part, member, substance)
2. Inherits domain relations (topic, region)
3. Inherits similar/also relations
4. Connects orphan synsets where possible
"""

import wn
from wn_editor import RelationType, _set_relation_to_synset
from collections import defaultdict

# Relation type mappings: wn relation name -> (RelationType, inverse RelationType)
RELATION_MAPPINGS = {
    # Meronym/Holonym - Part
    'mero_part': (RelationType.mero_part, RelationType.holo_part),
    'holo_part': (RelationType.holo_part, RelationType.mero_part),
    # Meronym/Holonym - Member
    'mero_member': (RelationType.mero_member, RelationType.holo_member),
    'holo_member': (RelationType.holo_member, RelationType.mero_member),
    # Meronym/Holonym - Substance
    'mero_substance': (RelationType.mero_substance, RelationType.holo_substance),
    'holo_substance': (RelationType.holo_substance, RelationType.mero_substance),
    # Domain
    'domain_topic': (RelationType.domain_topic, RelationType.has_domain_topic),
    'has_domain_topic': (RelationType.has_domain_topic, RelationType.domain_topic),
    'domain_region': (RelationType.domain_region, RelationType.has_domain_region),
    'has_domain_region': (RelationType.has_domain_region, RelationType.domain_region),
    # Similar/Also
    'similar': (RelationType.similar, RelationType.similar),  # Symmetric
    'also': (RelationType.also, RelationType.also),  # Symmetric
    # Exemplifies
    'exemplifies': (RelationType.exemplifies, RelationType.is_exemplified_by),
    'is_exemplified_by': (RelationType.is_exemplified_by, RelationType.exemplifies),
}


def build_ili_mapping(wordnet):
    """Build ILI ID -> synset mapping for a wordnet."""
    ili_to_synset = {}
    for ss in wordnet.synsets():
        ili = ss.ili
        if ili:
            ili_to_synset[ili.id] = ss
    return ili_to_synset


def inherit_relations(awn3, oewn, relation_name, awn3_ili_map, oewn_ili_map, common_ilis):
    """Inherit a specific relation type from OEWN to AWN3."""
    rel_type, inverse_rel_type = RELATION_MAPPINGS[relation_name]

    stats = {
        'added': 0,
        'skipped_no_target': 0,
        'errors': 0
    }

    for ili_id in common_ilis:
        awn3_synset = awn3_ili_map[ili_id]
        oewn_synset = oewn_ili_map[ili_id]

        try:
            # relations() returns a dict: {relation_name: [Synset, ...]}
            related_dict = oewn_synset.relations(relation_name)
            if not related_dict or relation_name not in related_dict:
                continue
            related_synsets = related_dict[relation_name]
        except:
            continue

        for oewn_related in related_synsets:
            related_ili = oewn_related.ili
            if related_ili and related_ili.id in awn3_ili_map:
                awn3_target = awn3_ili_map[related_ili.id]
                try:
                    _set_relation_to_synset(awn3_synset, awn3_target, rel_type)
                    stats['added'] += 1
                except Exception as e:
                    stats['errors'] += 1
            else:
                stats['skipped_no_target'] += 1

    return stats


def main():
    print("=" * 70)
    print("AWN3 RELATION ENHANCEMENT")
    print("=" * 70)

    # Load wordnets
    print("\n=== Loading Wordnets ===")
    awn3 = wn.Wordnet('awn3')
    oewn = wn.Wordnet('oewn:2024')

    awn3_synsets = list(awn3.synsets())
    oewn_synsets = list(oewn.synsets())

    print(f"AWN3 synsets: {len(awn3_synsets):,}")
    print(f"OEWN synsets: {len(oewn_synsets):,}")

    # Build ILI mappings
    print("\n=== Building ILI Mappings ===")
    awn3_ili_map = build_ili_mapping(awn3)
    oewn_ili_map = build_ili_mapping(oewn)

    common_ilis = set(awn3_ili_map.keys()) & set(oewn_ili_map.keys())
    print(f"AWN3 synsets with ILI: {len(awn3_ili_map):,}")
    print(f"OEWN synsets with ILI: {len(oewn_ili_map):,}")
    print(f"Common ILIs: {len(common_ilis):,}")

    # Track all stats
    all_stats = {}

    # === MERONYM/HOLONYM RELATIONS ===
    print("\n=== Inheriting Meronym/Holonym Relations ===")

    mero_holo_relations = [
        'mero_part', 'holo_part',
        'mero_member', 'holo_member',
        'mero_substance', 'holo_substance'
    ]

    for rel_name in mero_holo_relations:
        print(f"\nProcessing {rel_name}...")
        stats = inherit_relations(awn3, oewn, rel_name, awn3_ili_map, oewn_ili_map, common_ilis)
        all_stats[rel_name] = stats
        print(f"  Added: {stats['added']}, Skipped: {stats['skipped_no_target']}, Errors: {stats['errors']}")

    # === DOMAIN RELATIONS ===
    print("\n=== Inheriting Domain Relations ===")

    domain_relations = [
        'domain_topic', 'has_domain_topic',
        'domain_region', 'has_domain_region'
    ]

    for rel_name in domain_relations:
        print(f"\nProcessing {rel_name}...")
        stats = inherit_relations(awn3, oewn, rel_name, awn3_ili_map, oewn_ili_map, common_ilis)
        all_stats[rel_name] = stats
        print(f"  Added: {stats['added']}, Skipped: {stats['skipped_no_target']}, Errors: {stats['errors']}")

    # === SIMILAR/ALSO RELATIONS ===
    print("\n=== Inheriting Similar/Also Relations ===")

    similar_relations = ['similar', 'also']

    for rel_name in similar_relations:
        print(f"\nProcessing {rel_name}...")
        stats = inherit_relations(awn3, oewn, rel_name, awn3_ili_map, oewn_ili_map, common_ilis)
        all_stats[rel_name] = stats
        print(f"  Added: {stats['added']}, Skipped: {stats['skipped_no_target']}, Errors: {stats['errors']}")

    # === EXEMPLIFIES RELATIONS ===
    print("\n=== Inheriting Exemplifies Relations ===")

    exemplifies_relations = ['exemplifies', 'is_exemplified_by']

    for rel_name in exemplifies_relations:
        print(f"\nProcessing {rel_name}...")
        stats = inherit_relations(awn3, oewn, rel_name, awn3_ili_map, oewn_ili_map, common_ilis)
        all_stats[rel_name] = stats
        print(f"  Added: {stats['added']}, Skipped: {stats['skipped_no_target']}, Errors: {stats['errors']}")

    # === SUMMARY ===
    print("\n" + "=" * 70)
    print("ENHANCEMENT SUMMARY")
    print("=" * 70)

    total_added = 0
    print(f"\n{'Relation Type':<25} {'Added':>10} {'Skipped':>10} {'Errors':>10}")
    print("-" * 55)

    for rel_name, stats in all_stats.items():
        print(f"{rel_name:<25} {stats['added']:>10,} {stats['skipped_no_target']:>10,} {stats['errors']:>10,}")
        total_added += stats['added']

    print("-" * 55)
    print(f"{'TOTAL':<25} {total_added:>10,}")

    # === VERIFICATION ===
    print("\n=== Verification ===")
    awn3_refreshed = wn.Wordnet('awn3')

    # Count all relations
    hyper_count = sum(len(ss.hypernyms()) for ss in awn3_refreshed.synsets())
    hypo_count = sum(len(ss.hyponyms()) for ss in awn3_refreshed.synsets())

    # Count new relation types
    mero_count = sum(len(ss.meronyms()) for ss in awn3_refreshed.synsets())
    holo_count = sum(len(ss.holonyms()) for ss in awn3_refreshed.synsets())

    print(f"Hypernym relations: {hyper_count:,}")
    print(f"Hyponym relations: {hypo_count:,}")
    print(f"Meronym relations: {mero_count:,}")
    print(f"Holonym relations: {holo_count:,}")

    # Count synsets with any relation
    with_relation = sum(1 for ss in awn3_refreshed.synsets()
                       if ss.hypernyms() or ss.hyponyms() or ss.meronyms() or ss.holonyms())
    orphan_count = len(list(awn3_refreshed.synsets())) - with_relation

    print(f"\nSynsets with relations: {with_relation:,}")
    print(f"Orphan synsets remaining: {orphan_count:,}")


if __name__ == '__main__':
    main()
