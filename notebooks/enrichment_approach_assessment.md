# Assessment: Enriching OMW-ARB with AWN V3 Using WN-Agent

**Date:** 2026-01-12
**Purpose:** Evaluate the approach of enriching existing OMW-ARB v1.4 with AWN V3 content using wn-editor-extended, compared to creating a standalone AWN V3 wordnet.

---

## Executive Summary

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **A: Create Standalone AWN V3** | Clean slate, full control over structure | Must inherit relations from OMW-ARB/OEWN | Medium |
| **B: Enrich OMW-ARB with AWN V3** | Preserves all existing relations (~66K) | Complex PWN version mapping required | High |
| **C: Hybrid via ILI** | Best of both worlds | Requires ILI mapping infrastructure | Medium-High |

### Recommendation

**Approach A (Standalone AWN V3)** is recommended due to:
1. Critical PWN version mismatch (PWN 2.0 vs PWN 3.0) makes direct enrichment impractical
2. Only ~0.3% synset overlap via direct offset matching
3. ILI-based bridging requires external PWN 2.0→ILI mapping tables not readily available
4. AWN V3 data is self-contained and can inherit relations from OMW-ARB via ILI

---

## Detailed Analysis

### 1. Current State of Resources

#### OMW-ARB v1.4 (Open Multilingual Wordnet Arabic)

| Metric | Value |
|--------|-------|
| Synsets | 9,916 |
| Words | 18,003 |
| Senses | 37,342 |
| Arabic Definitions | **0%** (none) |
| Arabic Examples | **0%** (none) |
| Hypernym Relations | 9,272 |
| Hyponym Relations | 57,352 |
| Total Relations | ~66,624+ |
| PWN Version | **3.0** |
| ILI Coverage | 100% |

#### AWN V3 (Arabic WordNet Version 3, 2024)

| Metric | Value |
|--------|-------|
| Synsets | 9,662 |
| Arabic Lemmas | ~11,835 (97.6% coverage) |
| Arabic Definitions | 9,322 (96.5% coverage) |
| Arabic Examples | 9,261 (95.8% coverage) |
| Relations | **0** (not included) |
| PWN Version | **2.0** |
| ILI Coverage | Derivable via PWN 2.0→ILI mapping |

### 2. Critical Finding: PWN Version Mismatch

```
OMW-ARB synset ID format: omw-arb-{PWN3_offset}-{pos}
Example: omw-arb-03012209-a (PWN 3.0 offset)

AWN V3 PWN ID format: {PWN2_offset}
Example: 1740 (PWN 2.0 offset)
```

**Direct matching results:**
- OMW-ARB synsets: 9,916
- AWN V3 synsets with PWN ID: 7,064
- **Direct offset overlap: 19 synsets (0.3%)**

This extremely low overlap is because **synset offsets changed significantly between PWN 2.0 and PWN 3.0**. The same concept has different numeric identifiers in each version.

### 3. WN-Editor-Extended Capabilities

Based on the `wn-editor-extended` v0.6.1 source code:

| Operation | Supported | Method |
|-----------|-----------|--------|
| Add Arabic definitions | ✅ Yes | `SynsetEditor.add_definition(text, language="ar")` |
| Add Arabic examples | ✅ Yes | `SynsetEditor.add_example(text, language="ar")` |
| Add Arabic lemmas | ✅ Yes | `SynsetEditor.add_word(word)` |
| Modify definitions | ✅ Yes | `SynsetEditor.mod_definition(text)` |
| Set relations | ✅ Yes | `SynsetEditor.set_hypernym_of(synset)` |
| Create new synsets | ✅ Yes | `LexiconEditor.create_synset()` |
| Set ILI | ✅ Yes | `SynsetEditor.set_ili(ili_rowid)` |

**WN-Editor-Extended CAN technically enrich OMW-ARB, but the challenge is MATCHING synsets, not the editing operations.**

---

## Approach Analysis

### Approach A: Create Standalone AWN V3 Wordnet

**Process:**
1. Parse AWN V3 CSV files
2. Generate LMF XML with:
   - Synset IDs based on PWN 2.0 offsets
   - Arabic lemmas, definitions, examples
   - ILI mappings via PWN 2.0→ILI lookup
3. Inherit relations from OMW-ARB or OEWN via ILI matching
4. Validate with `wn.validate()`

**Pros:**
- Clean, self-contained lexicon
- Full control over ID scheme and structure
- AWN V3 data remains intact
- Can later merge with OEWN relations via ILI

**Cons:**
- Must build relation inheritance mechanism
- New lexicon ID (won't replace OMW-ARB)
- Requires PWN 2.0→ILI mapping

**Estimated Effort:** 1-2 weeks

### Approach B: Enrich OMW-ARB with AWN V3 Data

**Process:**
1. For each AWN V3 synset:
   - Convert PWN 2.0 offset → ILI
   - Find matching OMW-ARB synset via ILI
   - Use `SynsetEditor.add_definition()` to add Arabic gloss
   - Use `SynsetEditor.add_example()` to add Arabic example
   - Use `SynsetEditor.add_word()` to add Arabic lemmas

**Pros:**
- Preserves all OMW-ARB relations (~66K relations)
- Single unified Arabic WordNet
- Direct database modification

**Cons:**
- Requires PWN 2.0→ILI mapping table (external dependency)
- Only enriches matching synsets (~60-70% at best with ILI)
- ~30% of AWN V3 synsets may have no OMW-ARB match
- Modifies OMW-ARB in-place (risky)
- Complex error handling needed

**Estimated Effort:** 2-3 weeks

### Approach C: Hybrid via ILI (Recommended Alternative)

**Process:**
1. Create new lexicon `arb-unified`
2. Import AWN V3 content as primary data
3. Link to OMW-ARB synsets via ILI where possible
4. For synsets with ILI match:
   - Reference OMW-ARB relations (via `<Requires>` element)
5. For synsets without match:
   - Leave without relations OR
   - Derive from OEWN via ILI

**Pros:**
- Best coverage of both content and relations
- Doesn't modify existing lexicons
- Can evolve independently

**Cons:**
- More complex architecture
- Requires ILI infrastructure

**Estimated Effort:** 2 weeks

---

## ILI Mapping Requirement

To bridge AWN V3 (PWN 2.0) with OMW-ARB (PWN 3.0), you need:

### Option 1: Download PWN 2.0→ILI Mapping

The ILI project provides mapping files:
- **Source:** https://github.com/globalwordnet/ili
- **File:** `ili-map-pwn20.tab` (PWN 2.0 offset → ILI)

### Option 2: Use OEWN as Bridge

OEWN 2024 contains synsets with ILI mappings:
```python
import wn
oewn = wn.Wordnet('oewn:2024')
# OEWN synsets have ILI links
for ss in oewn.synsets():
    ili = ss.ili
    if ili:
        print(f"{ss.id} -> {ili.id}")
```

However, OEWN is based on PWN 3.1+, so still need PWN 2.0 mapping.

### Option 3: Use PyWSD or NLTK

```python
from nltk.corpus import wordnet as wn20
# NLTK can access PWN 2.0 data
```

---

## WN-Agent Applicability

Based on the WN-Agent README, it is designed for:
1. **Adding new terms** to WordNet
2. **Finding hypernyms** automatically via LLM
3. **Creating synsets** with proper relations

**WN-Agent is NOT designed for:**
- Bulk enrichment of existing synsets with definitions/examples
- Cross-version PWN mapping
- Large-scale data migration

**WN-Agent could potentially be used to:**
- Add missing AWN V3 synsets that don't exist in OMW-ARB
- Automatically find hypernyms for new Arabic concepts
- Validate translations via LLM reasoning

**Verdict:** WN-Agent is a **supplementary tool**, not the primary mechanism for AWN V3 integration.

---

## Implementation Recommendation

### Recommended Approach: Standalone AWN V3 with Relation Inheritance

```
Phase 1: Build AWN V3 LMF (1 week)
├── Parse AWN V3 CSV files
├── Generate synset IDs: awn3-{pwn2_offset}-{pos}
├── Include Arabic lemmas, definitions, examples
├── Map PWN 2.0 → ILI (download ili-map-pwn20.tab)
└── Output: awn3.xml

Phase 2: Relation Inheritance (1 week)
├── Load AWN V3 into wn database
├── For each AWN V3 synset with ILI:
│   ├── Find matching OMW-ARB synset via ILI
│   └── Copy hypernym/hyponym relations
└── Validate with wn.validate()

Phase 3: Gap Filling (Optional)
├── Use WN-Agent for synsets without ILI match
├── LLM finds appropriate hypernyms
└── Manual review of suggestions
```

### Required Files

1. **AWN V3 CSV files:** `/Users/salahmac/Desktop/MLProjects/wn-project/wn/AWN3.0/`
2. **ILI mapping:** Download from https://github.com/globalwordnet/ili
3. **wn-editor-extended:** For Phase 2 relation copying

### Sample Code for Relation Inheritance

```python
from wn_editor import LexiconEditor, SynsetEditor, RelationType
import wn

# Load both wordnets
arb = wn.Wordnet('omw-arb')
awn3 = wn.Wordnet('awn3')

# Build ILI to OMW-ARB synset mapping
ili_to_omw = {ss.ili.id: ss for ss in arb.synsets() if ss.ili}

# For each AWN3 synset, inherit relations
for awn_ss in awn3.synsets():
    if awn_ss.ili and awn_ss.ili.id in ili_to_omw:
        omw_ss = ili_to_omw[awn_ss.ili.id]

        # Copy hypernyms
        for hyper in omw_ss.hypernyms():
            if hyper.ili and hyper.ili.id in ili_to_awn3:
                awn_editor = SynsetEditor(awn_ss)
                awn_editor.set_hypernym_of(ili_to_awn3[hyper.ili.id])
```

---

## Conclusion

| Factor | Approach A (Standalone) | Approach B (Enrich OMW-ARB) |
|--------|------------------------|---------------------------|
| PWN Version Handling | Inherent (uses PWN 2.0) | Requires mapping |
| Relation Preservation | Via ILI inheritance | Already in OMW-ARB |
| Risk Level | Low | High (modifies existing) |
| Complexity | Medium | High |
| Recommended | **Yes** | No |

**Final Recommendation:** Create a standalone AWN V3 wordnet and use ILI-based relation inheritance from OMW-ARB. This approach is cleaner, safer, and more maintainable than attempting to enrich OMW-ARB directly.

---

## References

- [wn-editor-extended](https://github.com/Salah-Sal/wn-editor-extended) - Database editing
- [WN-Agent](https://github.com/Salah-Sal/wn-agent) - LLM-based term integration
- [ILI Project](https://github.com/globalwordnet/ili) - Interlingual Index mappings
- [AWN V3 Paper](https://aclanthology.org/2024.osact-1.9/) - Freihat et al. 2024
