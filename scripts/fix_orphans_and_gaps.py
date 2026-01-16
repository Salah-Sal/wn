#!/usr/bin/env python3
"""
Fix orphan synsets and lexical gaps in AWN3.

This script:
1. Connects orphan synsets by finding hypernyms from OEWN
2. Fills lexical gaps by copying words from OMW-ARB where ILI matches
"""

import wn
from wn_editor import LexiconEditor, SynsetEditor, RelationType, _set_relation_to_synset

def build_ili_mapping(wordnet):
    """Build ILI ID -> synset mapping for a wordnet."""
    ili_to_synset = {}
    for ss in wordnet.synsets():
        ili = ss.ili
        if ili:
            ili_to_synset[ili.id] = ss
    return ili_to_synset


def connect_orphan_synsets():
    """Find and connect orphan synsets using OEWN hypernym information."""
    print("=" * 70)
    print("CONNECTING ORPHAN SYNSETS")
    print("=" * 70)

    awn3 = wn.Wordnet('awn3')
    oewn = wn.Wordnet('oewn:2024')

    # Build ILI mappings
    awn3_ili_map = build_ili_mapping(awn3)
    oewn_ili_map = build_ili_mapping(oewn)

    # Find orphan synsets (no hypernym AND no hyponym)
    orphans = []
    for ss in awn3.synsets():
        if not ss.hypernyms() and not ss.hyponyms():
            orphans.append(ss)

    print(f"\nOrphan synsets found: {len(orphans)}")

    # Try to connect orphans via OEWN hypernyms
    connected = 0
    no_ili = 0
    no_oewn_match = 0
    no_hypernym_in_oewn = 0
    no_target_in_awn3 = 0

    for ss in orphans:
        if not ss.ili:
            no_ili += 1
            continue

        ili_id = ss.ili.id

        # Find corresponding OEWN synset
        if ili_id not in oewn_ili_map:
            no_oewn_match += 1
            continue

        oewn_ss = oewn_ili_map[ili_id]

        # Get OEWN hypernyms
        oewn_hypernyms = oewn_ss.hypernyms()
        if not oewn_hypernyms:
            no_hypernym_in_oewn += 1
            continue

        # Try to find a hypernym that exists in AWN3
        found_hypernym = False
        for oewn_hyper in oewn_hypernyms:
            if oewn_hyper.ili and oewn_hyper.ili.id in awn3_ili_map:
                awn3_target = awn3_ili_map[oewn_hyper.ili.id]
                try:
                    _set_relation_to_synset(ss, awn3_target, RelationType.hypernym)
                    connected += 1
                    found_hypernym = True
                    break
                except Exception as e:
                    pass

        if not found_hypernym:
            no_target_in_awn3 += 1

    print(f"\nResults:")
    print(f"  Connected: {connected}")
    print(f"  No ILI: {no_ili}")
    print(f"  No OEWN match: {no_oewn_match}")
    print(f"  No hypernym in OEWN: {no_hypernym_in_oewn}")
    print(f"  No target in AWN3: {no_target_in_awn3}")

    return connected


def fill_lexical_gaps():
    """Fill lexical gaps by copying words from OMW-ARB where ILI matches."""
    print("\n" + "=" * 70)
    print("FILLING LEXICAL GAPS")
    print("=" * 70)

    awn3 = wn.Wordnet('awn3')

    try:
        omw_arb = wn.Wordnet('omw-arb:1.4')
    except:
        print("ERROR: OMW-ARB not available")
        return 0

    # Build ILI mappings
    awn3_ili_map = build_ili_mapping(awn3)
    omw_ili_map = build_ili_mapping(omw_arb)

    # Find lexical gaps (synsets with no words)
    gaps = []
    for ss in awn3.synsets():
        if len(ss.words()) == 0:
            gaps.append(ss)

    print(f"\nLexical gaps found: {len(gaps)}")

    # Get LexiconEditor
    lex_editor = LexiconEditor('awn3')

    filled = 0
    no_ili = 0
    no_omw_match = 0
    no_words_in_omw = 0
    errors = 0

    for ss in gaps:
        if not ss.ili:
            no_ili += 1
            continue

        ili_id = ss.ili.id

        # Find corresponding OMW-ARB synset
        if ili_id not in omw_ili_map:
            no_omw_match += 1
            continue

        omw_ss = omw_ili_map[ili_id]

        # Get OMW-ARB words
        omw_words = omw_ss.words()
        if not omw_words:
            no_words_in_omw += 1
            continue

        # Add words from OMW-ARB to AWN3 synset
        try:
            ss_editor = SynsetEditor(ss)
            for word in omw_words:
                lemma = word.lemma()
                try:
                    ss_editor.add_word(lemma)
                except Exception as e:
                    pass  # Word might already exist or other issue
            filled += 1
        except Exception as e:
            errors += 1

    print(f"\nResults:")
    print(f"  Filled: {filled}")
    print(f"  No ILI: {no_ili}")
    print(f"  No OMW-ARB match: {no_omw_match}")
    print(f"  No words in OMW-ARB: {no_words_in_omw}")
    print(f"  Errors: {errors}")

    return filled


def verify_results():
    """Verify the results of the fixes."""
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)

    awn3 = wn.Wordnet('awn3')
    synsets = list(awn3.synsets())

    # Count orphans
    orphans = sum(1 for ss in synsets if not ss.hypernyms() and not ss.hyponyms())

    # Count lexical gaps
    gaps = sum(1 for ss in synsets if len(ss.words()) == 0)

    # Count total relations
    hyper_count = sum(len(ss.hypernyms()) for ss in synsets)
    hypo_count = sum(len(ss.hyponyms()) for ss in synsets)
    mero_count = sum(len(ss.meronyms()) for ss in synsets)
    holo_count = sum(len(ss.holonyms()) for ss in synsets)

    print(f"\nFinal Statistics:")
    print(f"  Total synsets: {len(synsets):,}")
    print(f"  Orphan synsets: {orphans:,}")
    print(f"  Lexical gaps: {gaps:,}")
    print(f"  Hypernym relations: {hyper_count:,}")
    print(f"  Hyponym relations: {hypo_count:,}")
    print(f"  Meronym relations: {mero_count:,}")
    print(f"  Holonym relations: {holo_count:,}")

    # Show remaining orphans sample
    if orphans > 0:
        print(f"\nSample remaining orphans:")
        count = 0
        for ss in synsets:
            if not ss.hypernyms() and not ss.hyponyms():
                words = [w.lemma() for w in ss.words()[:3]]
                defn = ss.definition()
                defn_preview = defn[:50] + "..." if defn and len(defn) > 50 else defn
                print(f"  {ss.id}: {words} - {defn_preview}")
                count += 1
                if count >= 5:
                    break

    # Show remaining gaps sample
    if gaps > 0:
        print(f"\nSample remaining gaps:")
        count = 0
        for ss in synsets:
            if len(ss.words()) == 0:
                defn = ss.definition()
                defn_preview = defn[:50] + "..." if defn and len(defn) > 50 else defn
                print(f"  {ss.id}: {defn_preview}")
                count += 1
                if count >= 5:
                    break


def main():
    # Connect orphan synsets
    connected = connect_orphan_synsets()

    # Fill lexical gaps
    filled = fill_lexical_gaps()

    # Verify results
    verify_results()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Orphan synsets connected: {connected}")
    print(f"  Lexical gaps filled: {filled}")


if __name__ == '__main__':
    main()
