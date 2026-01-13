#!/usr/bin/env python3
"""
Graph API Validation Script

Validates the graph visualization API endpoints against
ground truth data from Open English WordNet 2024.

Usage:
    python reports/validate_graph_api.py [--base-url URL]

Requirements:
    - Backend running on localhost:8000 (or specify --base-url)
    - OEWN 2024 installed
"""

import argparse
import json
import sys
from typing import Any
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

# =============================================================================
# Ground Truth Data (from OEWN 2024)
# =============================================================================

GROUND_TRUTH = {
    "synsets": {
        "dog": "oewn-02086723-n",
        "cat": "oewn-02124272-n",
        "car": "oewn-02961779-n",
        "canine": "oewn-02085998-n",
        "carnivore": "oewn-02077948-n",
        "feline": "oewn-02123649-n",
        "entity": "oewn-00001740-n",
        "puppy": "oewn-01325095-n",
    },
    "dog_hypernyms": ["oewn-02085998-n", "oewn-01320032-n"],
    "dog_hyponyms_count": 18,
    "car_meronyms_count": 30,
    "dog_to_cat_path_length": 3,
    "dog_to_cat_wup_similarity": 0.8571,
    "dog_hypernym_path_length": 8,
}


# =============================================================================
# Test Utilities
# =============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def fetch(url: str) -> dict[str, Any]:
    """Fetch JSON from URL."""
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except HTTPError as e:
        return {"error": e.code, "message": str(e)}
    except URLError as e:
        return {"error": "connection", "message": str(e)}


def test_result(name: str, passed: bool, details: str = "") -> bool:
    """Print test result."""
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    print(f"  [{status}] {name}")
    if details and not passed:
        print(f"         {Colors.YELLOW}{details}{Colors.END}")
    return passed


# =============================================================================
# Test Cases
# =============================================================================

def test_neighborhood(base_url: str) -> tuple[int, int]:
    """Test neighborhood endpoint."""
    print(f"\n{Colors.BLUE}Test Case 1: Neighborhood Expansion{Colors.END}")
    passed = 0
    total = 0

    synset_id = GROUND_TRUTH["synsets"]["dog"]
    url = f"{base_url}/graph/neighborhood/{synset_id}?depth=1"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 5

    # Test 1: Has nodes
    total += 1
    node_count = len(data.get("nodes", []))
    if test_result(f"Returns nodes (got {node_count})", node_count >= 3,
                   f"Expected at least 3 nodes"):
        passed += 1

    # Test 2: Center node is correct
    total += 1
    if test_result("Center node is dog synset",
                   data.get("center_node") == synset_id,
                   f"Got {data.get('center_node')}"):
        passed += 1

    # Test 3: Contains hypernyms
    total += 1
    node_ids = {n["id"] for n in data.get("nodes", [])}
    has_hypernym = GROUND_TRUTH["dog_hypernyms"][0] in node_ids
    if test_result("Contains canine hypernym", has_hypernym,
                   f"Missing {GROUND_TRUTH['dog_hypernyms'][0]}"):
        passed += 1

    # Test 4: Has edges
    total += 1
    edge_count = len(data.get("edges", []))
    if test_result(f"Has edges (got {edge_count})", edge_count >= 5,
                   "Expected at least 5 edges"):
        passed += 1

    # Test 5: Edge relations are valid
    total += 1
    relations = {e["relation"] for e in data.get("edges", [])}
    valid_relations = {"hypernym", "hyponym", "mero_part", "holo_part",
                       "similar", "also", "antonym"}
    has_valid = len(relations & valid_relations) > 0
    if test_result(f"Has valid relation types ({relations})", has_valid):
        passed += 1

    return passed, total


def test_hypernym_tree(base_url: str) -> tuple[int, int]:
    """Test hypernym tree endpoint."""
    print(f"\n{Colors.BLUE}Test Case 2: Hypernym Tree{Colors.END}")
    passed = 0
    total = 0

    synset_id = GROUND_TRUTH["synsets"]["dog"]
    url = f"{base_url}/graph/hypernym-tree/{synset_id}"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 4

    # Test 1: Has path to entity
    total += 1
    node_ids = {n["id"] for n in data.get("nodes", [])}
    entity_id = GROUND_TRUTH["synsets"]["entity"]
    if test_result("Path reaches entity root", entity_id in node_ids,
                   f"Missing {entity_id}"):
        passed += 1

    # Test 2: Correct path length
    total += 1
    node_count = len(data.get("nodes", []))
    expected = GROUND_TRUTH["dog_hypernym_path_length"]
    if test_result(f"Path length ~{expected} (got {node_count})",
                   expected - 2 <= node_count <= expected + 2,
                   f"Expected {expected}±2"):
        passed += 1

    # Test 3: All edges are hypernym type
    total += 1
    all_hypernym = all(e["relation"] == "hypernym"
                       for e in data.get("edges", []))
    if test_result("All edges are hypernym type", all_hypernym):
        passed += 1

    # Test 4: Center node correct
    total += 1
    if test_result("Center node is dog",
                   data.get("center_node") == synset_id):
        passed += 1

    return passed, total


def test_hyponym_tree(base_url: str) -> tuple[int, int]:
    """Test hyponym tree endpoint."""
    print(f"\n{Colors.BLUE}Test Case 3: Hyponym Tree{Colors.END}")
    passed = 0
    total = 0

    synset_id = GROUND_TRUTH["synsets"]["dog"]
    url = f"{base_url}/graph/hyponym-tree/{synset_id}?max_depth=1"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 3

    # Test 1: Has correct number of hyponyms
    total += 1
    node_count = len(data.get("nodes", []))
    expected = GROUND_TRUTH["dog_hyponyms_count"] + 1  # +1 for center
    if test_result(f"Node count ~{expected} (got {node_count})",
                   node_count >= expected - 5,
                   f"Expected at least {expected - 5}"):
        passed += 1

    # Test 2: Contains puppy
    total += 1
    node_ids = {n["id"] for n in data.get("nodes", [])}
    puppy_id = GROUND_TRUTH["synsets"]["puppy"]
    if test_result("Contains puppy hyponym", puppy_id in node_ids,
                   f"Missing {puppy_id}"):
        passed += 1

    # Test 3: All edges are hyponym type
    total += 1
    all_hyponym = all(e["relation"] == "hyponym"
                      for e in data.get("edges", []))
    if test_result("All edges are hyponym type", all_hyponym):
        passed += 1

    return passed, total


def test_shortest_path(base_url: str) -> tuple[int, int]:
    """Test shortest path endpoint."""
    print(f"\n{Colors.BLUE}Test Case 4: Shortest Path (dog → cat){Colors.END}")
    passed = 0
    total = 0

    dog_id = GROUND_TRUTH["synsets"]["dog"]
    cat_id = GROUND_TRUTH["synsets"]["cat"]
    url = f"{base_url}/graph/path/{dog_id}/{cat_id}"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 4

    # Test 1: Correct path length
    total += 1
    expected_length = GROUND_TRUTH["dog_to_cat_path_length"]
    actual_length = data.get("length", -1)
    if test_result(f"Path length is {expected_length} (got {actual_length})",
                   actual_length == expected_length):
        passed += 1

    # Test 2: Source correct
    total += 1
    if test_result("Source is dog", data.get("source") == dog_id):
        passed += 1

    # Test 3: Target correct
    total += 1
    if test_result("Target is cat", data.get("target") == cat_id):
        passed += 1

    # Test 4: Path goes through carnivore
    total += 1
    path_ids = [n["id"] for n in data.get("path", [])]
    carnivore_id = GROUND_TRUTH["synsets"]["carnivore"]
    if test_result("Path includes carnivore", carnivore_id in path_ids,
                   f"Path: {path_ids}"):
        passed += 1

    return passed, total


def test_similarity(base_url: str) -> tuple[int, int]:
    """Test similarity endpoint."""
    print(f"\n{Colors.BLUE}Test Case 5: Similarity Scores{Colors.END}")
    passed = 0
    total = 0

    dog_id = GROUND_TRUTH["synsets"]["dog"]
    cat_id = GROUND_TRUTH["synsets"]["cat"]
    url = f"{base_url}/graph/similarity/{dog_id}/{cat_id}"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 3

    sim = data.get("similarity", {})

    # Test 1: Path similarity in range
    total += 1
    path_sim = sim.get("path")
    if test_result(f"Path similarity 0.15-0.25 (got {path_sim})",
                   path_sim and 0.15 <= path_sim <= 0.25):
        passed += 1

    # Test 2: Wu-Palmer similarity
    total += 1
    wup_sim = sim.get("wup")
    expected_wup = GROUND_TRUTH["dog_to_cat_wup_similarity"]
    if test_result(f"Wu-Palmer ~{expected_wup:.2f} (got {wup_sim})",
                   wup_sim and abs(wup_sim - expected_wup) < 0.05):
        passed += 1

    # Test 3: LCH exists (same POS)
    total += 1
    lch_sim = sim.get("lch")
    if test_result(f"LCH similarity exists (got {lch_sim})",
                   lch_sim is not None):
        passed += 1

    return passed, total


def test_car_meronyms(base_url: str) -> tuple[int, int]:
    """Test car meronyms via neighborhood."""
    print(f"\n{Colors.BLUE}Test Case 6: Car Meronyms{Colors.END}")
    passed = 0
    total = 0

    car_id = GROUND_TRUTH["synsets"]["car"]
    url = f"{base_url}/graph/neighborhood/{car_id}?depth=1"
    data = fetch(url)

    if "error" in data:
        print(f"  {Colors.RED}ERROR: {data['message']}{Colors.END}")
        return 0, 2

    # Test 1: Has meronym edges
    total += 1
    edges = data.get("edges", [])
    mero_edges = [e for e in edges if "mero" in e.get("relation", "")]
    expected = GROUND_TRUTH["car_meronyms_count"]
    if test_result(f"Has meronym edges ~{expected} (got {len(mero_edges)})",
                   len(mero_edges) >= expected - 10,
                   f"Expected at least {expected - 10}"):
        passed += 1

    # Test 2: Total nodes reasonable
    total += 1
    node_count = len(data.get("nodes", []))
    if test_result(f"Has many nodes (got {node_count})",
                   node_count >= 20):
        passed += 1

    return passed, total


def test_error_cases(base_url: str) -> tuple[int, int]:
    """Test error handling."""
    print(f"\n{Colors.BLUE}Test Case 7: Error Handling{Colors.END}")
    passed = 0
    total = 0

    # Test 1: Invalid synset returns 404
    total += 1
    url = f"{base_url}/graph/neighborhood/invalid-synset-id"
    data = fetch(url)
    if test_result("Invalid synset returns error", "error" in data,
                   f"Got: {data}"):
        passed += 1

    # Test 2: Valid but non-existent synset
    total += 1
    url = f"{base_url}/graph/neighborhood/oewn-99999999-n"
    data = fetch(url)
    if test_result("Non-existent synset returns error", "error" in data):
        passed += 1

    return passed, total


def test_depth_expansion(base_url: str) -> tuple[int, int]:
    """Test depth parameter affects results."""
    print(f"\n{Colors.BLUE}Test Case 8: Depth Expansion{Colors.END}")
    passed = 0
    total = 0

    synset_id = GROUND_TRUTH["synsets"]["dog"]

    # Fetch depth=1
    url1 = f"{base_url}/graph/neighborhood/{synset_id}?depth=1"
    data1 = fetch(url1)

    # Fetch depth=2
    url2 = f"{base_url}/graph/neighborhood/{synset_id}?depth=2"
    data2 = fetch(url2)

    if "error" in data1 or "error" in data2:
        print(f"  {Colors.RED}ERROR fetching data{Colors.END}")
        return 0, 2

    # Test 1: depth=2 has more nodes
    total += 1
    nodes1 = len(data1.get("nodes", []))
    nodes2 = len(data2.get("nodes", []))
    if test_result(f"depth=2 ({nodes2}) > depth=1 ({nodes1})",
                   nodes2 > nodes1):
        passed += 1

    # Test 2: depth=2 has more edges
    total += 1
    edges1 = len(data1.get("edges", []))
    edges2 = len(data2.get("edges", []))
    if test_result(f"depth=2 edges ({edges2}) > depth=1 ({edges1})",
                   edges2 > edges1):
        passed += 1

    return passed, total


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validate Graph API")
    parser.add_argument("--base-url", default="http://localhost:8000/api",
                        help="API base URL")
    args = parser.parse_args()

    print("=" * 60)
    print("GRAPH API VALIDATION")
    print(f"Base URL: {args.base_url}")
    print("=" * 60)

    # Check connectivity
    health_url = args.base_url.replace("/api", "/health")
    health = fetch(health_url)
    if "error" in health:
        print(f"\n{Colors.RED}ERROR: Cannot connect to API at {args.base_url}")
        print(f"Make sure the backend is running.{Colors.END}")
        sys.exit(1)
    print(f"\n{Colors.GREEN}Connected to API{Colors.END}")

    # Run all tests
    total_passed = 0
    total_tests = 0

    tests = [
        test_neighborhood,
        test_hypernym_tree,
        test_hyponym_tree,
        test_shortest_path,
        test_similarity,
        test_car_meronyms,
        test_error_cases,
        test_depth_expansion,
    ]

    for test_fn in tests:
        p, t = test_fn(args.base_url)
        total_passed += p
        total_tests += t

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    color = Colors.GREEN if pct >= 80 else Colors.YELLOW if pct >= 60 else Colors.RED

    print(f"\nTotal: {color}{total_passed}/{total_tests} tests passed ({pct:.1f}%){Colors.END}")

    if pct == 100:
        print(f"\n{Colors.GREEN}All tests passed! The implementation is valid.{Colors.END}")
    elif pct >= 80:
        print(f"\n{Colors.YELLOW}Most tests passed. Review failures above.{Colors.END}")
    else:
        print(f"\n{Colors.RED}Many tests failed. Check implementation.{Colors.END}")

    sys.exit(0 if pct >= 80 else 1)


if __name__ == "__main__":
    main()
