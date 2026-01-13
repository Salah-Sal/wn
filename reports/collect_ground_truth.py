#!/usr/bin/env python3
"""
Ground Truth Data Collection Script

Collects comprehensive ground truth data from OEWN 2024 using the wn library
directly. This data will be used to validate the graph API implementation.

Usage:
    python reports/collect_ground_truth.py

Output:
    reports/ground_truth_data.json
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for local wn module
sys.path.insert(0, str(Path(__file__).parent.parent))

import wn
from wn import similarity

# Ensure we're using OEWN 2024
LEXICON = "oewn:2024"


def get_synset_info(synset_id: str) -> dict:
    """Get basic info about a synset."""
    try:
        s = wn.synset(synset_id)
        if not s:
            return None
        return {
            "id": s.id,
            "lemmas": s.lemmas()[:10],
            "pos": s.pos,
            "definition": s.definition()[:200] if s.definition() else None,
        }
    except Exception as e:
        print(f"  Error getting synset {synset_id}: {e}")
        return None


def find_synset_by_lemma(lemma: str, pos: str = "n") -> str:
    """Find synset ID by lemma and POS."""
    try:
        synsets = wn.synsets(lemma, pos=pos)
        if synsets:
            return synsets[0].id
    except Exception:
        pass
    return None


def collect_hypernym_data(synset_id: str) -> dict:
    """Collect hypernym tree ground truth."""
    try:
        s = wn.synset(synset_id)
        if not s:
            return {"error": "synset not found"}

        # Get direct hypernyms
        direct_hypernyms = [h.id for h in s.hypernyms()]

        # Get all hypernym paths
        paths = s.hypernym_paths(simulate_root=False)
        all_path_ids = []
        for path in paths:
            path_ids = [syn.id for syn in path]
            all_path_ids.append(path_ids)

        # Get root (entity or top concept)
        roots = set()
        for path in paths:
            if path:
                roots.add(path[-1].id)

        return {
            "synset_id": synset_id,
            "direct_hypernyms": direct_hypernyms,
            "hypernym_path_count": len(paths),
            "paths": all_path_ids,
            "roots": list(roots),
            "max_path_length": max(len(p) for p in paths) if paths else 0,
        }
    except Exception as e:
        return {"error": str(e)}


def collect_hyponym_data(synset_id: str, max_depth: int = 1) -> dict:
    """Collect hyponym tree ground truth."""
    try:
        s = wn.synset(synset_id)
        if not s:
            return {"error": "synset not found"}

        # Get direct hyponyms
        direct_hyponyms = [h.id for h in s.hyponyms()]

        # Collect hyponyms up to max_depth
        all_hyponyms = set()
        current_level = [s]

        for depth in range(max_depth):
            next_level = []
            for current in current_level:
                for hypo in current.hyponyms():
                    if hypo.id not in all_hyponyms:
                        all_hyponyms.add(hypo.id)
                        next_level.append(hypo)
            current_level = next_level

        return {
            "synset_id": synset_id,
            "direct_hyponym_count": len(direct_hyponyms),
            "direct_hyponyms": direct_hyponyms[:20],  # Limit for readability
            "total_hyponyms_depth_1": len(all_hyponyms) if max_depth == 1 else None,
        }
    except Exception as e:
        return {"error": str(e)}


def collect_neighborhood_data(synset_id: str) -> dict:
    """Collect neighborhood ground truth (all relation types)."""
    try:
        s = wn.synset(synset_id)
        if not s:
            return {"error": "synset not found"}

        relations = {}

        # Hypernyms/Hyponyms
        relations["hypernym"] = [h.id for h in s.hypernyms()]
        relations["hyponym"] = [h.id for h in s.hyponyms()]

        # Instance relations
        relations["instance_hypernym"] = [h.id for h in s.get_related("instance_hypernym")]
        relations["instance_hyponym"] = [h.id for h in s.get_related("instance_hyponym")]

        # Meronyms (part-of)
        relations["mero_part"] = [h.id for h in s.get_related("mero_part")]
        relations["mero_member"] = [h.id for h in s.get_related("mero_member")]
        relations["mero_substance"] = [h.id for h in s.get_related("mero_substance")]

        # Holonyms (has-part)
        relations["holo_part"] = [h.id for h in s.get_related("holo_part")]
        relations["holo_member"] = [h.id for h in s.get_related("holo_member")]
        relations["holo_substance"] = [h.id for h in s.get_related("holo_substance")]

        # Other relations
        relations["similar"] = [h.id for h in s.get_related("similar")]
        relations["also"] = [h.id for h in s.get_related("also")]
        relations["antonym"] = [h.id for h in s.get_related("antonym")]
        relations["attribute"] = [h.id for h in s.get_related("attribute")]

        # Count totals
        total_relations = sum(len(v) for v in relations.values())
        non_empty = {k: v for k, v in relations.items() if v}

        return {
            "synset_id": synset_id,
            "total_neighbors": total_relations,
            "relations": non_empty,
            "relation_counts": {k: len(v) for k, v in non_empty.items()},
        }
    except Exception as e:
        return {"error": str(e)}


def collect_path_data(source_id: str, target_id: str) -> dict:
    """Collect shortest path ground truth."""
    try:
        s1 = wn.synset(source_id)
        s2 = wn.synset(target_id)

        if not s1 or not s2:
            return {"error": "synset not found"}

        path = s1.shortest_path(s2, simulate_root=True)

        if not path:
            return {
                "source": source_id,
                "target": target_id,
                "path_exists": False,
            }

        return {
            "source": source_id,
            "target": target_id,
            "path_exists": True,
            "path_length": len(path) - 1,  # edges, not nodes
            "path_nodes": [syn.id for syn in path],
            "path_lemmas": [syn.lemmas()[0] if syn.lemmas() else syn.id for syn in path],
        }
    except Exception as e:
        return {"error": str(e)}


def collect_similarity_data(synset_id1: str, synset_id2: str) -> dict:
    """Collect similarity scores ground truth."""
    try:
        s1 = wn.synset(synset_id1)
        s2 = wn.synset(synset_id2)

        if not s1 or not s2:
            return {"error": "synset not found"}

        result = {
            "synset1": synset_id1,
            "synset2": synset_id2,
            "same_pos": s1.pos == s2.pos,
        }

        # Path similarity
        try:
            result["path_similarity"] = similarity.path(s1, s2, simulate_root=True)
        except Exception:
            result["path_similarity"] = None

        # Wu-Palmer similarity
        try:
            result["wup_similarity"] = similarity.wup(s1, s2, simulate_root=True)
        except Exception:
            result["wup_similarity"] = None

        # LCH similarity - SKIP for now as taxonomy_depth is very slow
        # If needed, this can be computed separately
        result["lch_similarity"] = None
        result["lch_note"] = "Skipped - taxonomy_depth calculation is slow"

        return result
    except Exception as e:
        return {"error": str(e)}


def main():
    # Force unbuffered output
    import functools
    print = functools.partial(__builtins__.print, flush=True)

    print("=" * 60)
    print("GROUND TRUTH DATA COLLECTION")
    print("=" * 60)

    # Check for OEWN
    lexicons = wn.lexicons()
    print(f"\nInstalled lexicons: {[l.id for l in lexicons]}")

    oewn = None
    for lex in lexicons:
        if "oewn" in lex.id.lower():
            oewn = lex
            break

    if not oewn:
        print("ERROR: OEWN 2024 not installed!")
        sys.exit(1)

    print(f"Using lexicon: {oewn.id}")

    # =========================================================================
    # Define test synsets
    # =========================================================================
    print("\n" + "-" * 40)
    print("Finding test synsets...")
    print("-" * 40)

    test_synsets = {}

    # Nouns with rich hierarchies
    noun_targets = [
        ("dog", "n"),
        ("cat", "n"),
        ("car", "n"),
        ("tree", "n"),
        ("person", "n"),
        ("food", "n"),
        ("computer", "n"),
        ("music", "n"),
        ("water", "n"),
        ("house", "n"),
    ]

    # Verbs
    verb_targets = [
        ("run", "v"),
        ("eat", "v"),
        ("think", "v"),
        ("see", "v"),
    ]

    # Adjectives
    adj_targets = [
        ("big", "a"),
        ("happy", "a"),
        ("fast", "a"),
    ]

    for lemma, pos in noun_targets + verb_targets + adj_targets:
        synsets = wn.synsets(lemma, pos=pos)
        if synsets:
            # Take the first (most common) sense
            s = synsets[0]
            test_synsets[lemma] = {
                "id": s.id,
                "pos": s.pos,
                "lemmas": s.lemmas()[:5],
                "definition": s.definition()[:100] if s.definition() else None,
            }
            print(f"  {lemma}: {s.id} - {s.lemmas()[:3]}")
        else:
            print(f"  {lemma}: NOT FOUND")

    # Override ambiguous lemmas with specific synsets
    # (first sense isn't always the intended one)
    override_synsets = {
        "cat": "oewn-02124272-n",      # feline mammal, not CT scan
        "tree": "oewn-13124818-n",     # woody plant, not person name
    }

    for name, sid in override_synsets.items():
        info = get_synset_info(sid)
        if info:
            test_synsets[name] = info
            print(f"  {name} (override): {sid} - {info['lemmas'][:3]}")

    # Add specific known synsets
    known_synsets = {
        "entity": "oewn-00001740-n",
        "physical_entity": "oewn-00001930-n",
        "canine": "oewn-02085998-n",
        "feline": "oewn-02123649-n",
        "carnivore": "oewn-02077948-n",
        "mammal": "oewn-01864419-n",
        "animal": "oewn-00015568-n",
        "organism": "oewn-00004475-n",
        "puppy": "oewn-01325095-n",
        "domestic_animal": "oewn-01320032-n",
    }

    for name, sid in known_synsets.items():
        info = get_synset_info(sid)
        if info:
            test_synsets[name] = info
            print(f"  {name}: {sid} - {info['lemmas'][:3]}")

    # =========================================================================
    # Collect ground truth data
    # =========================================================================
    ground_truth = {
        "metadata": {
            "lexicon": oewn.id,
            "collection_date": "2026-01-12",
            "description": "Ground truth data for graph API validation",
        },
        "synsets": test_synsets,
        "tests": {
            "hypernym_trees": [],
            "hyponym_trees": [],
            "neighborhoods": [],
            "shortest_paths": [],
            "similarities": [],
        },
    }

    # -------------------------------------------------------------------------
    # Hypernym Trees
    # -------------------------------------------------------------------------
    print("\n" + "-" * 40)
    print("Collecting hypernym tree data...")
    print("-" * 40)

    hypernym_targets = ["dog", "cat", "car", "tree", "person", "run", "big"]
    for name in hypernym_targets:
        if name in test_synsets:
            sid = test_synsets[name]["id"]
            print(f"  {name} ({sid})...")
            data = collect_hypernym_data(sid)
            data["name"] = name
            ground_truth["tests"]["hypernym_trees"].append(data)
            print(f"    Paths: {data.get('hypernym_path_count', 0)}, "
                  f"Max depth: {data.get('max_path_length', 0)}")

    # -------------------------------------------------------------------------
    # Hyponym Trees
    # -------------------------------------------------------------------------
    print("\n" + "-" * 40)
    print("Collecting hyponym tree data...")
    print("-" * 40)

    hyponym_targets = ["dog", "cat", "car", "animal", "tree", "run"]
    for name in hyponym_targets:
        if name in test_synsets:
            sid = test_synsets[name]["id"]
            print(f"  {name} ({sid})...")
            data = collect_hyponym_data(sid, max_depth=1)
            data["name"] = name
            ground_truth["tests"]["hyponym_trees"].append(data)
            print(f"    Direct hyponyms: {data.get('direct_hyponym_count', 0)}")

    # -------------------------------------------------------------------------
    # Neighborhoods
    # -------------------------------------------------------------------------
    print("\n" + "-" * 40)
    print("Collecting neighborhood data...")
    print("-" * 40)

    neighborhood_targets = ["dog", "cat", "car", "tree", "water", "run"]
    for name in neighborhood_targets:
        if name in test_synsets:
            sid = test_synsets[name]["id"]
            print(f"  {name} ({sid})...")
            data = collect_neighborhood_data(sid)
            data["name"] = name
            ground_truth["tests"]["neighborhoods"].append(data)
            print(f"    Total neighbors: {data.get('total_neighbors', 0)}")
            if data.get("relation_counts"):
                for rel, count in data["relation_counts"].items():
                    print(f"      {rel}: {count}")

    # -------------------------------------------------------------------------
    # Shortest Paths
    # -------------------------------------------------------------------------
    print("\n" + "-" * 40)
    print("Collecting shortest path data...")
    print("-" * 40)

    path_pairs = [
        ("dog", "cat"),
        ("dog", "car"),
        ("dog", "person"),
        ("cat", "tree"),
        ("car", "house"),
        ("dog", "entity"),
        ("dog", "animal"),
        ("dog", "puppy"),
    ]

    for name1, name2 in path_pairs:
        if name1 in test_synsets and name2 in test_synsets:
            sid1 = test_synsets[name1]["id"]
            sid2 = test_synsets[name2]["id"]
            print(f"  {name1} -> {name2}...")
            data = collect_path_data(sid1, sid2)
            data["source_name"] = name1
            data["target_name"] = name2
            ground_truth["tests"]["shortest_paths"].append(data)
            if data.get("path_exists"):
                print(f"    Length: {data['path_length']}, "
                      f"Path: {' -> '.join(data['path_lemmas'][:5])}")
            else:
                print(f"    No path found")

    # -------------------------------------------------------------------------
    # Similarity Scores
    # -------------------------------------------------------------------------
    print("\n" + "-" * 40)
    print("Collecting similarity data...")
    print("-" * 40)

    similarity_pairs = [
        ("dog", "cat"),
        ("dog", "car"),
        ("dog", "puppy"),
        ("cat", "feline"),
        ("car", "tree"),
    ]

    for name1, name2 in similarity_pairs:
        if name1 in test_synsets and name2 in test_synsets:
            sid1 = test_synsets[name1]["id"]
            sid2 = test_synsets[name2]["id"]
            print(f"  {name1} vs {name2}...")
            data = collect_similarity_data(sid1, sid2)
            data["name1"] = name1
            data["name2"] = name2
            ground_truth["tests"]["similarities"].append(data)
            print(f"    Path: {data.get('path_similarity')}, "
                  f"WuP: {data.get('wup_similarity')}")

    # =========================================================================
    # Save results
    # =========================================================================
    output_path = Path("reports/ground_truth_data.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"Ground truth data saved to: {output_path}")
    print("=" * 60)

    # Summary
    print("\nSummary:")
    print(f"  Synsets collected: {len(test_synsets)}")
    print(f"  Hypernym tests: {len(ground_truth['tests']['hypernym_trees'])}")
    print(f"  Hyponym tests: {len(ground_truth['tests']['hyponym_trees'])}")
    print(f"  Neighborhood tests: {len(ground_truth['tests']['neighborhoods'])}")
    print(f"  Path tests: {len(ground_truth['tests']['shortest_paths'])}")
    print(f"  Similarity tests: {len(ground_truth['tests']['similarities'])}")


if __name__ == "__main__":
    main()
