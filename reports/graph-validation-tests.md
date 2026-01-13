# Graph Visualization Validation Tests

**Lexicon:** Open English WordNet 2024 (oewn:2024)
**Date:** January 2026

---

## Ground Truth Data

### Test Synsets

| Name | Synset ID | Lemmas | Definition |
|------|-----------|--------|------------|
| dog | `oewn-02086723-n` | dog, domestic dog, Canis familiaris | a member of the genus Canis... |
| cat | `oewn-02124272-n` | cat, true cat | feline mammal usually having thick soft fur... |
| car | `oewn-02961779-n` | car, auto, automobile | a motor vehicle with four wheels... |
| canine | `oewn-02085998-n` | canine, canid | any of various fissiped mammals... |
| puppy | `oewn-01325095-n` | puppy | a young dog |

---

## Test Case 1: Neighborhood Expansion

### Expected: Dog Synset Neighbors

**Endpoint:** `GET /api/graph/neighborhood/oewn-02086723-n?depth=1`

**Expected Nodes (minimum):**
- Center: `oewn-02086723-n` (dog)
- Hypernyms:
  - `oewn-02085998-n` (canine, canid)
  - `oewn-01320032-n` (domestic animal)
- Hyponyms (partial - 18 total):
  - `oewn-01325095-n` (puppy)
  - `oewn-02087384-n` (pooch, doggie)
  - `oewn-02087513-n` (cur, mongrel)
  - `oewn-02087924-n` (lapdog)
  - `oewn-02088026-n` (toy dog)

**Expected Edges:**
- hypernym: dog → canine
- hypernym: dog → domestic animal
- hyponym: dog → puppy
- hyponym: dog → pooch
- (etc.)

**Validation Criteria:**
- [ ] Returns at least 3 nodes (center + 2 hypernyms)
- [ ] Contains both hypernym edges
- [ ] Contains at least 5 hyponym edges
- [ ] All node IDs start with `oewn-`

---

## Test Case 2: Hypernym Tree

### Expected: Dog Ancestry Chain

**Endpoint:** `GET /api/graph/hypernym-tree/oewn-02086723-n`

**Expected Path (one of multiple):**
```
dog (oewn-02086723-n)
  ↓ hypernym
domestic animal (oewn-01320032-n)
  ↓ hypernym
animal (oewn-00015568-n)
  ↓ hypernym
organism (oewn-00004475-n)
  ↓ hypernym
living thing (oewn-00004258-n)
  ↓ hypernym
whole (oewn-00003553-n)
  ↓ hypernym
object (oewn-00002684-n)
  ↓ hypernym
physical entity (oewn-00001930-n)
  ↓ hypernym
entity (oewn-00001740-n)
```

**Validation Criteria:**
- [ ] Path contains `oewn-00001740-n` (entity) as root
- [ ] Path length is 8-9 nodes
- [ ] All edges are "hypernym" type
- [ ] Path is directed (child → parent)

---

## Test Case 3: Hyponym Tree

### Expected: Dog Descendants

**Endpoint:** `GET /api/graph/hyponym-tree/oewn-02086723-n?max_depth=2`

**Expected Direct Hyponyms (18 total):**
| ID | Lemmas |
|----|--------|
| oewn-01325095-n | puppy |
| oewn-02087384-n | pooch, doggie, doggy |
| oewn-02087513-n | cur, mongrel, mutt |
| oewn-02087924-n | lapdog |
| oewn-02088026-n | toy dog, toy |
| oewn-02088418-n | hunting dog |
| oewn-02093256-n | working dog |
| oewn-02104625-n | dalmatian, coach dog |
| oewn-02104951-n | basenji |
| oewn-02105056-n | pug, pug-dog |

**Validation Criteria:**
- [ ] Returns center node + at least 15 hyponyms
- [ ] All edges are "hyponym" type
- [ ] With depth=2, includes second-level descendants

---

## Test Case 4: Shortest Path

### Expected: Dog to Cat Path

**Endpoint:** `GET /api/graph/path/oewn-02086723-n/oewn-02124272-n`

**Expected Path (4 nodes, 3 edges):**
```
dog (oewn-02086723-n)
  ↓
canine (oewn-02085998-n)
  ↓
carnivore (oewn-02077948-n)
  ↓
feline (oewn-02123649-n)
  ↓
cat (oewn-02124272-n)
```

**Validation Criteria:**
- [ ] Path length = 3 edges (4 nodes)
- [ ] Source = `oewn-02086723-n`
- [ ] Target = `oewn-02124272-n`
- [ ] Intermediate nodes include carnivore
- [ ] Path goes through common ancestor

---

## Test Case 5: Similarity Scores

### Expected: Dog vs Cat Similarity

**Endpoint:** `GET /api/graph/similarity/oewn-02086723-n/oewn-02124272-n`

**Expected Scores:**
| Metric | Expected Value | Tolerance |
|--------|---------------|-----------|
| Path | 0.2000 | ±0.05 |
| Wu-Palmer | 0.8571 | ±0.05 |
| LCH | ~2.0-3.0 | ±0.5 |

**Validation Criteria:**
- [ ] Path similarity between 0.15-0.25
- [ ] Wu-Palmer similarity between 0.80-0.90
- [ ] Both synsets have same POS (noun)

---

## Test Case 6: Car Meronyms

### Expected: Car Parts

**Endpoint:** `GET /api/graph/neighborhood/oewn-02961779-n?depth=1`

**Expected Meronym Nodes (30 total):**
| ID | Lemmas |
|----|--------|
| oewn-02673313-n | accelerator, gas pedal |
| oewn-02688224-n | air bag |
| oewn-02764562-n | automobile engine |
| oewn-02764839-n | car horn |
| oewn-02914504-n | fender |
| oewn-02921979-n | bumper |
| oewn-02967273-n | car door |
| oewn-02969235-n | car mirror |
| oewn-02974144-n | car seat |

**Validation Criteria:**
- [ ] Contains mero_part relations
- [ ] At least 20 meronym nodes returned
- [ ] Includes common parts (door, seat, engine)

---

## Test Case 7: Edge Filtering

### Depth Expansion Test

**Test:** Compare depth=1 vs depth=2

**Endpoint 1:** `GET /api/graph/neighborhood/oewn-02086723-n?depth=1`
**Endpoint 2:** `GET /api/graph/neighborhood/oewn-02086723-n?depth=2`

**Validation Criteria:**
- [ ] depth=2 returns more nodes than depth=1
- [ ] depth=2 includes grandchildren of dog
- [ ] Both contain the center node

---

## API Test Script

Run these curl commands to validate:

```bash
# Base URL
API="http://localhost:8000/api"

# Test 1: Neighborhood
curl -s "$API/graph/neighborhood/oewn-02086723-n?depth=1" | jq '.nodes | length'
# Expected: 20+

# Test 2: Hypernym Tree
curl -s "$API/graph/hypernym-tree/oewn-02086723-n" | jq '.nodes[-1].id'
# Expected: "oewn-00001740-n" (entity)

# Test 3: Hyponym Tree
curl -s "$API/graph/hyponym-tree/oewn-02086723-n?max_depth=1" | jq '.nodes | length'
# Expected: 19 (1 center + 18 hyponyms)

# Test 4: Shortest Path
curl -s "$API/graph/path/oewn-02086723-n/oewn-02124272-n" | jq '.length'
# Expected: 3

# Test 5: Similarity
curl -s "$API/graph/similarity/oewn-02086723-n/oewn-02124272-n" | jq '.similarity.wup'
# Expected: ~0.857

# Test 6: Car Meronyms
curl -s "$API/graph/neighborhood/oewn-02961779-n?depth=1" | jq '[.edges[] | select(.relation | contains("mero"))] | length'
# Expected: 30
```

---

## Visual Validation Checklist

### Graph Canvas
- [ ] Nodes display with POS-based colors (blue=noun)
- [ ] Center node is highlighted (larger, gold border)
- [ ] Edges show relation type labels
- [ ] Clicking a node expands its neighbors
- [ ] Double-clicking navigates to synset detail page

### Graph Controls
- [ ] Zoom in/out works
- [ ] Fit view centers the graph
- [ ] Layout switching works (dagre, fcose, circle, etc.)
- [ ] Reset clears and reloads initial graph

### Tooltips
- [ ] Hovering shows synset info
- [ ] Tooltip displays lemmas and definition
- [ ] Tooltip follows cursor

### View Modes
- [ ] "Neighborhood" shows all relation types
- [ ] "Hypernyms" shows only ancestor tree
- [ ] "Hyponyms" shows only descendant tree

---

## Expected Node/Edge Counts

| Synset | Depth | Expected Nodes | Expected Edges |
|--------|-------|----------------|----------------|
| dog | 1 | ~20 | ~20 |
| dog | 2 | ~50-100 | ~50-100 |
| car | 1 | ~35 | ~35 |
| entity | 1 | ~10 | ~10 |

---

## Error Cases to Test

1. **Invalid synset ID:**
   - `GET /api/graph/neighborhood/invalid-id`
   - Expected: 404 Not Found

2. **Non-existent path:**
   - `GET /api/graph/path/oewn-02086723-n/oewn-00001740-n`
   - Expected: Valid path (dog to entity)

3. **Same synset path:**
   - `GET /api/graph/path/oewn-02086723-n/oewn-02086723-n`
   - Expected: Path of length 0 or error

4. **Cross-POS similarity:**
   - `GET /api/graph/similarity/oewn-02086723-n/oewn-00612841-v` (noun vs verb)
   - Expected: LCH should be null (different POS)
