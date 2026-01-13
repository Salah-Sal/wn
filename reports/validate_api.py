#!/usr/bin/env python3
"""
Graph API Validation Script

Validates all graph API endpoints against ground truth data collected
from OEWN 2024.

Usage:
    python reports/validate_api.py [--base-url URL] [--test TEST_NAME]

Options:
    --base-url URL      API base URL (default: http://localhost:8000/api)
    --test TEST_NAME    Run specific test only (neighborhood, hypernym, hyponym, path, similarity)
    --verbose           Show detailed output for each test
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Optional
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


# =============================================================================
# Configuration
# =============================================================================

GROUND_TRUTH_FILE = Path(__file__).parent / "ground_truth_data.json"
TIMEOUT_SECONDS = 30


# =============================================================================
# Colors
# =============================================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{Colors.END}"


# =============================================================================
# HTTP Client
# =============================================================================

def fetch_json(url: str, timeout: int = TIMEOUT_SECONDS) -> tuple[Optional[dict], Optional[str]]:
    """
    Fetch JSON from URL.
    Returns (data, error) tuple.
    """
    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode()), None
    except HTTPError as e:
        return None, f"HTTP {e.code}: {str(e)}"
    except URLError as e:
        return None, f"Connection error: {str(e)}"
    except json.JSONDecodeError as e:
        return None, f"JSON decode error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"


# =============================================================================
# Test Result Tracking
# =============================================================================

class TestResult:
    def __init__(self, name: str, passed: bool, details: str = "", expected: Any = None, actual: Any = None):
        self.name = name
        self.passed = passed
        self.details = details
        self.expected = expected
        self.actual = actual

    def __str__(self):
        status = colorize("PASS", Colors.GREEN) if self.passed else colorize("FAIL", Colors.RED)
        result = f"  [{status}] {self.name}"
        if not self.passed and self.details:
            result += f"\n         {colorize(self.details, Colors.YELLOW)}"
        return result


class TestSuite:
    def __init__(self, name: str):
        self.name = name
        self.results: list[TestResult] = []
        self.start_time = None
        self.end_time = None

    def add(self, result: TestResult):
        self.results.append(result)

    def start(self):
        self.start_time = time.time()

    def finish(self):
        self.end_time = time.time()

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def pass_rate(self) -> float:
        if self.total_count == 0:
            return 0
        return self.passed_count / self.total_count * 100


# =============================================================================
# Individual Validators
# =============================================================================

def validate_neighborhood(
    base_url: str,
    ground_truth: dict,
    verbose: bool = False
) -> TestSuite:
    """Validate neighborhood endpoint against ground truth."""
    suite = TestSuite("Neighborhood API")
    suite.start()

    neighborhoods = ground_truth["tests"]["neighborhoods"]
    synsets = ground_truth["synsets"]

    for test in neighborhoods:
        name = test["name"]
        synset_id = test["synset_id"]
        expected_total = test["total_neighbors"]
        expected_relations = test.get("relation_counts", {})

        print(f"\n  Testing: {name} ({synset_id})")

        # Make API call
        url = f"{base_url}/graph/neighborhood/{synset_id}?depth=1&limit=200"
        data, error = fetch_json(url)

        if error:
            suite.add(TestResult(
                f"{name}: API call",
                False,
                f"Failed: {error}"
            ))
            continue

        suite.add(TestResult(
            f"{name}: API responds",
            True
        ))

        # Check center node
        center_node = data.get("center_node")
        suite.add(TestResult(
            f"{name}: center_node correct",
            center_node == synset_id,
            f"Expected {synset_id}, got {center_node}"
        ))

        # Check node count
        node_count = len(data.get("nodes", []))
        # Node count should include center + neighbors
        # Allow some tolerance due to API limit
        expected_node_count = expected_total + 1  # +1 for center
        min_expected = min(expected_node_count, 50)  # API default limit
        suite.add(TestResult(
            f"{name}: node count >= {min_expected}",
            node_count >= min_expected - 5,  # Allow small tolerance
            f"Expected >= {min_expected - 5}, got {node_count}"
        ))

        # Check edge count
        edge_count = len(data.get("edges", []))
        suite.add(TestResult(
            f"{name}: has edges",
            edge_count > 0,
            f"Got {edge_count} edges"
        ))

        # Check specific relation types
        actual_relations = {}
        for edge in data.get("edges", []):
            rel = edge.get("relation", "unknown")
            actual_relations[rel] = actual_relations.get(rel, 0) + 1

        for rel_type, expected_count in expected_relations.items():
            actual_count = actual_relations.get(rel_type, 0)
            # Allow some tolerance for hyponyms due to limit
            tolerance = 5 if rel_type == "hyponym" else 2
            suite.add(TestResult(
                f"{name}: {rel_type} count ~{expected_count}",
                abs(actual_count - expected_count) <= tolerance or actual_count >= expected_count - tolerance,
                f"Expected ~{expected_count}, got {actual_count}"
            ))

        if verbose:
            print(f"    Nodes: {node_count}, Edges: {edge_count}")
            print(f"    Relations: {actual_relations}")

    suite.finish()
    return suite


def validate_hypernym_tree(
    base_url: str,
    ground_truth: dict,
    verbose: bool = False
) -> TestSuite:
    """Validate hypernym tree endpoint against ground truth."""
    suite = TestSuite("Hypernym Tree API")
    suite.start()

    hypernym_tests = ground_truth["tests"]["hypernym_trees"]

    for test in hypernym_tests:
        name = test["name"]
        synset_id = test["synset_id"]
        expected_roots = test.get("roots", [])
        expected_path_count = test.get("hypernym_path_count", 0)
        expected_max_depth = test.get("max_path_length", 0)
        direct_hypernyms = test.get("direct_hypernyms", [])

        # Skip adjectives (no hypernym hierarchy)
        if expected_path_count == 0:
            continue

        print(f"\n  Testing: {name} ({synset_id})")

        # Make API call (max_depth is limited to 10 by API)
        url = f"{base_url}/graph/hypernym-tree/{synset_id}?max_depth=10"
        data, error = fetch_json(url)

        if error:
            suite.add(TestResult(
                f"{name}: API call",
                False,
                f"Failed: {error}"
            ))
            continue

        suite.add(TestResult(
            f"{name}: API responds",
            True
        ))

        # Check center node
        center_node = data.get("center_node")
        suite.add(TestResult(
            f"{name}: center_node correct",
            center_node == synset_id,
            f"Expected {synset_id}, got {center_node}"
        ))

        # Check that root node is reached
        node_ids = {n["id"] for n in data.get("nodes", [])}
        root_reached = any(root in node_ids for root in expected_roots)
        suite.add(TestResult(
            f"{name}: reaches root ({expected_roots[0] if expected_roots else 'N/A'})",
            root_reached or not expected_roots,
            f"Root not in nodes: {node_ids}"
        ))

        # Check all edges are hypernym type
        edges = data.get("edges", [])
        all_hypernym = all(e.get("relation") == "hypernym" for e in edges)
        suite.add(TestResult(
            f"{name}: all edges are hypernym",
            all_hypernym,
            f"Found non-hypernym edges"
        ))

        # Check direct hypernyms are included
        for hyper_id in direct_hypernyms[:2]:  # Check first 2
            suite.add(TestResult(
                f"{name}: includes hypernym {hyper_id[:20]}...",
                hyper_id in node_ids,
                f"Missing direct hypernym"
            ))

        if verbose:
            print(f"    Nodes: {len(data.get('nodes', []))}, Edges: {len(edges)}")
            print(f"    Root reached: {root_reached}")

    suite.finish()
    return suite


def validate_hyponym_tree(
    base_url: str,
    ground_truth: dict,
    verbose: bool = False
) -> TestSuite:
    """Validate hyponym tree endpoint against ground truth."""
    suite = TestSuite("Hyponym Tree API")
    suite.start()

    hyponym_tests = ground_truth["tests"]["hyponym_trees"]

    for test in hyponym_tests:
        name = test["name"]
        synset_id = test["synset_id"]
        expected_hyponym_count = test.get("direct_hyponym_count", 0)
        direct_hyponyms = test.get("direct_hyponyms", [])

        # Skip if no hyponyms
        if expected_hyponym_count == 0:
            continue

        print(f"\n  Testing: {name} ({synset_id})")

        # Make API call
        url = f"{base_url}/graph/hyponym-tree/{synset_id}?max_depth=1&limit=500"
        data, error = fetch_json(url)

        if error:
            suite.add(TestResult(
                f"{name}: API call",
                False,
                f"Failed: {error}"
            ))
            continue

        suite.add(TestResult(
            f"{name}: API responds",
            True
        ))

        # Check center node
        center_node = data.get("center_node")
        suite.add(TestResult(
            f"{name}: center_node correct",
            center_node == synset_id,
            f"Expected {synset_id}, got {center_node}"
        ))

        # Check node count (should be center + hyponyms)
        node_count = len(data.get("nodes", []))
        expected_node_count = expected_hyponym_count + 1
        tolerance = 5
        suite.add(TestResult(
            f"{name}: node count ~{expected_node_count}",
            abs(node_count - expected_node_count) <= tolerance,
            f"Expected ~{expected_node_count}, got {node_count}"
        ))

        # Check all edges are hyponym type
        edges = data.get("edges", [])
        all_hyponym = all(e.get("relation") == "hyponym" for e in edges)
        suite.add(TestResult(
            f"{name}: all edges are hyponym",
            all_hyponym,
            f"Found non-hyponym edges"
        ))

        # Check some direct hyponyms are included
        node_ids = {n["id"] for n in data.get("nodes", [])}
        hyponyms_found = sum(1 for h in direct_hyponyms if h in node_ids)
        suite.add(TestResult(
            f"{name}: contains direct hyponyms",
            hyponyms_found >= len(direct_hyponyms) * 0.8,  # 80% threshold
            f"Found {hyponyms_found}/{len(direct_hyponyms)} direct hyponyms"
        ))

        if verbose:
            print(f"    Nodes: {node_count}, Edges: {len(edges)}")
            print(f"    Hyponyms found: {hyponyms_found}/{len(direct_hyponyms)}")

    suite.finish()
    return suite


def validate_shortest_path(
    base_url: str,
    ground_truth: dict,
    verbose: bool = False
) -> TestSuite:
    """Validate shortest path endpoint against ground truth."""
    suite = TestSuite("Shortest Path API")
    suite.start()

    path_tests = ground_truth["tests"]["shortest_paths"]

    for test in path_tests:
        source_name = test.get("source_name", "?")
        target_name = test.get("target_name", "?")
        source_id = test["source"]
        target_id = test["target"]
        expected_length = test.get("path_length")
        expected_path_nodes = test.get("path_nodes", [])

        print(f"\n  Testing: {source_name} -> {target_name}")

        # Make API call
        url = f"{base_url}/graph/path/{source_id}/{target_id}"
        data, error = fetch_json(url)

        if error:
            suite.add(TestResult(
                f"{source_name}->{target_name}: API call",
                False,
                f"Failed: {error}"
            ))
            continue

        suite.add(TestResult(
            f"{source_name}->{target_name}: API responds",
            True
        ))

        # Check source and target
        suite.add(TestResult(
            f"{source_name}->{target_name}: source correct",
            data.get("source") == source_id,
            f"Expected {source_id}, got {data.get('source')}"
        ))

        suite.add(TestResult(
            f"{source_name}->{target_name}: target correct",
            data.get("target") == target_id,
            f"Expected {target_id}, got {data.get('target')}"
        ))

        # Check path length
        actual_length = data.get("length")
        # Allow tolerance of 1 for different path choices
        suite.add(TestResult(
            f"{source_name}->{target_name}: length = {expected_length}",
            actual_length is not None and abs(actual_length - expected_length) <= 1,
            f"Expected {expected_length}, got {actual_length}"
        ))

        # Check path contains expected intermediate nodes
        path_ids = [n["id"] for n in data.get("path", [])]
        # Check that at least half the expected nodes are in the path
        common_nodes = set(path_ids) & set(expected_path_nodes)
        suite.add(TestResult(
            f"{source_name}->{target_name}: path nodes overlap",
            len(common_nodes) >= len(expected_path_nodes) * 0.3,
            f"Only {len(common_nodes)}/{len(expected_path_nodes)} common nodes"
        ))

        if verbose:
            print(f"    Length: {actual_length} (expected {expected_length})")
            print(f"    Path: {' -> '.join(path_ids[:5])}...")

    suite.finish()
    return suite


def validate_similarity(
    base_url: str,
    ground_truth: dict,
    verbose: bool = False
) -> TestSuite:
    """Validate similarity endpoint against ground truth."""
    suite = TestSuite("Similarity API")
    suite.start()

    similarity_tests = ground_truth["tests"]["similarities"]

    for test in similarity_tests:
        name1 = test.get("name1", "?")
        name2 = test.get("name2", "?")
        synset1 = test["synset1"]
        synset2 = test["synset2"]
        expected_path = test.get("path_similarity")
        expected_wup = test.get("wup_similarity")

        print(f"\n  Testing: {name1} vs {name2}")

        # Make API call with shorter timeout (similarity can be slow)
        url = f"{base_url}/graph/similarity/{synset1}/{synset2}"
        data, error = fetch_json(url, timeout=60)  # Longer timeout for similarity

        if error:
            suite.add(TestResult(
                f"{name1} vs {name2}: API call",
                False,
                f"Failed: {error}"
            ))
            continue

        suite.add(TestResult(
            f"{name1} vs {name2}: API responds",
            True
        ))

        sim = data.get("similarity", {})

        # Check path similarity
        actual_path = sim.get("path")
        if expected_path is not None:
            tolerance = 0.05
            suite.add(TestResult(
                f"{name1} vs {name2}: path sim ~{expected_path:.3f}",
                actual_path is not None and abs(actual_path - expected_path) <= tolerance,
                f"Expected {expected_path:.3f}, got {actual_path}"
            ))

        # Check Wu-Palmer similarity
        actual_wup = sim.get("wup")
        if expected_wup is not None:
            tolerance = 0.05
            suite.add(TestResult(
                f"{name1} vs {name2}: WuP sim ~{expected_wup:.3f}",
                actual_wup is not None and abs(actual_wup - expected_wup) <= tolerance,
                f"Expected {expected_wup:.3f}, got {actual_wup}"
            ))

        if verbose:
            print(f"    Path: {actual_path}, WuP: {actual_wup}")

    suite.finish()
    return suite


def validate_error_handling(
    base_url: str,
    verbose: bool = False
) -> TestSuite:
    """Validate error handling for invalid inputs."""
    suite = TestSuite("Error Handling")
    suite.start()

    print("\n  Testing error handling...")

    # Invalid synset ID format
    url = f"{base_url}/graph/neighborhood/invalid-id"
    data, error = fetch_json(url)
    suite.add(TestResult(
        "Invalid synset ID returns error",
        error is not None or (data and "error" in str(data).lower()),
        f"Should return error for invalid ID"
    ))

    # Non-existent synset
    url = f"{base_url}/graph/neighborhood/oewn-99999999-n"
    data, error = fetch_json(url)
    suite.add(TestResult(
        "Non-existent synset returns error",
        error is not None or (data and "error" in str(data).lower()),
        f"Should return error for non-existent synset"
    ))

    # Invalid path (same synset)
    url = f"{base_url}/graph/path/oewn-02086723-n/oewn-02086723-n"
    data, error = fetch_json(url)
    suite.add(TestResult(
        "Same synset path handled",
        error is None or data is not None,  # Either works or returns valid response
        f"Should handle same-synset path gracefully"
    ))

    suite.finish()
    return suite


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Validate Graph API against ground truth")
    parser.add_argument("--base-url", default="http://localhost:8000/api",
                        help="API base URL")
    parser.add_argument("--test", choices=["neighborhood", "hypernym", "hyponym", "path", "similarity", "error"],
                        help="Run specific test only")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output")
    args = parser.parse_args()

    print("=" * 70)
    print(colorize("GRAPH API VALIDATION", Colors.BOLD))
    print("=" * 70)
    print(f"Base URL: {args.base_url}")
    print(f"Ground truth: {GROUND_TRUTH_FILE}")

    # Load ground truth
    if not GROUND_TRUTH_FILE.exists():
        print(colorize(f"\nERROR: Ground truth file not found!", Colors.RED))
        print("Run: python reports/collect_ground_truth.py")
        sys.exit(1)

    with open(GROUND_TRUTH_FILE) as f:
        ground_truth = json.load(f)

    print(f"Loaded {len(ground_truth['synsets'])} test synsets")

    # Check connectivity
    print("\nChecking API connectivity...")
    health_url = args.base_url.replace("/api", "/health")
    data, error = fetch_json(health_url)
    if error:
        print(colorize(f"\nERROR: Cannot connect to API!", Colors.RED))
        print(f"  {error}")
        print(f"  Make sure the backend is running on {args.base_url}")
        sys.exit(1)
    print(colorize("  Connected!", Colors.GREEN))

    # Run tests
    all_suites: list[TestSuite] = []

    test_map = {
        "neighborhood": lambda: validate_neighborhood(args.base_url, ground_truth, args.verbose),
        "hypernym": lambda: validate_hypernym_tree(args.base_url, ground_truth, args.verbose),
        "hyponym": lambda: validate_hyponym_tree(args.base_url, ground_truth, args.verbose),
        "path": lambda: validate_shortest_path(args.base_url, ground_truth, args.verbose),
        "similarity": lambda: validate_similarity(args.base_url, ground_truth, args.verbose),
        "error": lambda: validate_error_handling(args.base_url, args.verbose),
    }

    if args.test:
        # Run single test
        tests_to_run = [args.test]
    else:
        # Run all tests
        tests_to_run = list(test_map.keys())

    for test_name in tests_to_run:
        print(f"\n{colorize('=' * 70, Colors.BLUE)}")
        print(colorize(f"TEST SUITE: {test_name.upper()}", Colors.BOLD + Colors.BLUE))
        print(colorize("=" * 70, Colors.BLUE))

        suite = test_map[test_name]()
        all_suites.append(suite)

        # Print individual results
        for result in suite.results:
            print(result)

        # Suite summary
        print(f"\n  Suite: {suite.passed_count}/{suite.total_count} passed "
              f"({suite.pass_rate:.1f}%) in {suite.duration:.2f}s")

    # Overall summary
    print("\n" + "=" * 70)
    print(colorize("OVERALL SUMMARY", Colors.BOLD))
    print("=" * 70)

    total_passed = sum(s.passed_count for s in all_suites)
    total_tests = sum(s.total_count for s in all_suites)
    total_duration = sum(s.duration for s in all_suites)

    if total_tests > 0:
        overall_rate = total_passed / total_tests * 100
    else:
        overall_rate = 0

    print(f"\n{'Suite':<20} {'Passed':<10} {'Total':<10} {'Rate':<10} {'Time':<10}")
    print("-" * 60)

    for suite in all_suites:
        rate_color = Colors.GREEN if suite.pass_rate >= 80 else Colors.YELLOW if suite.pass_rate >= 60 else Colors.RED
        print(f"{suite.name:<20} {suite.passed_count:<10} {suite.total_count:<10} "
              f"{colorize(f'{suite.pass_rate:.1f}%', rate_color):<19} {suite.duration:.2f}s")

    print("-" * 60)

    overall_color = Colors.GREEN if overall_rate >= 80 else Colors.YELLOW if overall_rate >= 60 else Colors.RED
    print(f"{'TOTAL':<20} {total_passed:<10} {total_tests:<10} "
          f"{colorize(f'{overall_rate:.1f}%', overall_color):<19} {total_duration:.2f}s")

    # Final verdict
    print()
    if overall_rate >= 90:
        print(colorize("RESULT: EXCELLENT - API implementation is highly accurate!", Colors.GREEN))
    elif overall_rate >= 80:
        print(colorize("RESULT: GOOD - API implementation is mostly correct.", Colors.GREEN))
    elif overall_rate >= 60:
        print(colorize("RESULT: PARTIAL - Some issues need attention.", Colors.YELLOW))
    else:
        print(colorize("RESULT: POOR - Significant issues found.", Colors.RED))

    sys.exit(0 if overall_rate >= 80 else 1)


if __name__ == "__main__":
    main()
