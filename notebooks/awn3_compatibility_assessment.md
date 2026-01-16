# AWN V3 Compatibility Assessment for wn Library

**Date:** 2026-01-12
**Purpose:** Assess if AWN V3 data is sufficient to create a wn-compatible Arabic WordNet

---

## Executive Summary

| Category | Status | Details |
|----------|--------|---------|
| **Synsets** | ✅ Available | 9,662 synsets |
| **Arabic Lemmas** | ✅ Available | ~11,835 lemmas (94.5% coverage) |
| **Arabic Definitions** | ✅ Available | 96.5% coverage |
| **Arabic Examples** | ✅ Available | 95.8% coverage |
| **PWN IDs (for ILI)** | ⚠️ Partial | 67.4% have PWN offset |
| **Relations** | ❌ **NOT AVAILABLE** | Must derive from OMW-ARB or OEWN |
| **Lexicon Metadata** | ⚠️ Must Define | ID, email, license, etc. |

### Bottom Line

**AWN V3 contains sufficient CONTENT data (lemmas, definitions, examples) but LACKS RELATION DATA (hypernyms, hyponyms, etc.).** Relations must be inherited from OMW-ARB or derived from the English WordNet via ILI mapping.

---

## Detailed Assessment

### 1. Synset Data ✅ AVAILABLE

| Metric | Value |
|--------|-------|
| Total Synsets | 9,662 |
| Nouns | 6,520 (67.5%) |
| Verbs | 2,507 (25.9%) |
| Adjectives | 526 (5.4%) |
| Adverbs | 109 (1.1%) |

**Format:** CSV files with columns for PWN ID, English content, Arabic content

### 2. Arabic Lemmas ✅ AVAILABLE

| Metric | Value |
|--------|-------|
| Synsets with lemmas | 9,426 (97.6%) |
| Total lemmas | ~11,835 |
| Lexical gaps (GAP) | 236 (2.4%) |
| Multi-lemma entries | 2,203 |
| Average lemmas/synset | 1.22 |

**Format:** Comma-separated Arabic text with full diacritization (tashkeel)

**Example:**
```
صِفَة, مِيزَة, خَاصِّيَّة
شَخْص, أَحَد, فَرْد, مَخْلُوق, إِنْسَان, نَفْس
```

**Parsing Notes:**
- Delimiter: comma (`,`)
- Some entries have brackets `[]` or `<>` that need cleaning
- Leading/trailing whitespace present

### 3. Arabic Definitions (Glosses) ✅ AVAILABLE

| Metric | Value |
|--------|-------|
| Synsets with Arabic gloss | 9,322 (96.5%) |
| Missing glosses | ~340 |

**Quality:** Native Arabic definitions, not translations. Written by expert linguists.

**Example:**
```
بنية ذات وجود خاص بحد ذاته ( سواء كان حياً أم غير حي )
وحدة لغوية نطلقها على شخص أو شيء ليعرف به
```

### 4. Arabic Examples ✅ AVAILABLE

| Metric | Value |
|--------|-------|
| Synsets with Arabic examples | 9,261 (95.8%) |

**Quality:** Authentic MSA usage sentences, not translations.

**Example:**
```
الكيان التعليمي في بلادنا متطور
سامر هو الاسم الذي يطلق على ذلك الشخص. ما اسمك؟
```

### 5. PWN IDs (for ILI Mapping) ⚠️ PARTIAL

| Metric | Value |
|--------|-------|
| Synsets with PWN ID | ~67% (varies by POS) |
| PWN ID format | Numeric offset (e.g., 1740, 6344646) |
| ILI derivable | Yes, via PWN-ILI mapping |

**Mapping Strategy:**
1. AWN V3 PWN ID → PWN 2.0 synset offset
2. PWN 2.0 offset → ILI (via existing mappings)

**Cross-reference with OMW-ARB:**
- ~60% of AWN V3 IDs found in OMW-ARB
- Some IDs are new (not in OMW-ARB)

### 6. Phrasets ✅ AVAILABLE (Nouns only)

| Metric | Value |
|--------|-------|
| Phrasets | 364 (in Nouns file) |
| Purpose | Multi-word expressions for untranslatable concepts |

**Example:**
```
Lemma: تَجْرِيد
Phraset: كيان تجريدي
```

### 7. Lexical Gaps ✅ AVAILABLE

| Metric | Value |
|--------|-------|
| Total gaps | 236 |
| Nouns | 28 |
| Verbs | 187 |
| Adjectives | 0 |
| Adverbs | 21 |

**Handling:** Mark with `lexicalized="false"` in LMF output

---

## MISSING DATA

### 8. Semantic Relations ❌ NOT AVAILABLE

**AWN V3 CSV files contain NO relation data:**
- ❌ No hypernym/hyponym relations
- ❌ No meronym/holonym relations
- ❌ No antonym relations
- ❌ No domain relations
- ❌ No similarity relations

**This is the CRITICAL GAP.**

**Solution Options:**

| Option | Pros | Cons |
|--------|------|------|
| **A. Inherit from OMW-ARB** | Direct mapping via PWN offset | Only covers ~60% of synsets |
| **B. Derive from OEWN via ILI** | Complete relation set | Requires ILI mapping |
| **C. No relations** | Simplest | Limited WordNet functionality |
| **D. Hybrid** | Best coverage | More complex |

**OMW-ARB Relation Statistics (for reference):**
- Hypernym relations: 9,272
- Hyponym relations: 57,352
- Meronym relations: 5,406
- Holonym relations: 1,901
- **Total: 73,931 relations**

### 9. Lexicon Metadata ⚠️ MUST DEFINE

| Field | Required | Suggested Value |
|-------|----------|-----------------|
| `id` | Yes | `awn3` or `omw-arb3` |
| `label` | Yes | `Arabic WordNet V3` |
| `language` | Yes | `arb` (BCP-47 for MSA) |
| `email` | Yes | Maintainer email |
| `license` | Yes | `https://creativecommons.org/licenses/by-nc/4.0/` |
| `version` | Yes | `3.0` |
| `url` | No | `https://github.com/HadiPTUK/AWN3.0` |
| `citation` | No | Freihat et al. 2024 |

### 10. Additional Fields Not in AWN V3

| Field | Status | Impact |
|-------|--------|--------|
| ILI definitions | ❌ Not available | Cannot propose new ILIs |
| Sense examples | ❌ Not available | Only synset-level examples |
| Sense frequency | ❌ Not available | No usage counts |
| Pronunciation | ❌ Not available | No IPA/audio |
| Morphological forms | ❌ Not available | No broken plurals, conjugations |
| Syntactic behaviours | ❌ Not available | No subcategorization frames |

---

## Data Quality Issues to Address

### Issue 1: Lemma Parsing
```python
# Some lemmas have inconsistent formatting:
"[غَرْسَة,] نَبَات, حَيَاة نَبَاتِيَّة"  # Brackets need removal
"جِزْء, قِسْم ,مكوِّن"                  # Inconsistent spacing around comma
```

### Issue 2: PWN ID Gaps
- Not all synsets have PWN IDs
- Some PWN IDs don't match OMW-ARB

### Issue 3: Missing Data
- ~340 synsets without Arabic definitions
- ~400 synsets without Arabic examples
- 236 lexical gaps (expected, not an issue)

---

## Recommended Conversion Strategy

### Phase 1: Core Data Conversion
1. Parse AWN V3 CSV files
2. Generate LMF XML with:
   - Lexical entries (from Arabic lemmas)
   - Synsets (from PWN IDs)
   - Definitions (Arabic glosses)
   - Examples (Arabic examples)
3. Map PWN IDs to ILI

### Phase 2: Relation Inheritance
1. Load OMW-ARB into database
2. For each AWN V3 synset with matching PWN offset:
   - Copy hypernym/hyponym relations
   - Copy meronym/holonym relations
   - Copy other relations as available

### Phase 3: Gap Handling
1. Mark 236 lexical gaps with `lexicalized="false"`
2. Include phrasets as sense examples or metadata
3. Handle missing definitions/examples appropriately

### Phase 4: Validation
1. Run wn validation checks
2. Fix E101 (non-unique ID) issues
3. Fix E204 (missing synset) issues
4. Fix E401 (missing relation target) issues

---

## Summary: Data Availability Matrix

| LMF Element | AWN V3 Source | Available | Notes |
|-------------|---------------|-----------|-------|
| `Lexicon/@id` | Define | ⚠️ | Must define |
| `Lexicon/@label` | Define | ⚠️ | Must define |
| `Lexicon/@language` | "arb" | ✅ | |
| `Lexicon/@email` | Define | ⚠️ | Must define |
| `Lexicon/@license` | CC BY-NC 4.0 | ✅ | From paper |
| `Lexicon/@version` | "3.0" | ✅ | |
| `LexicalEntry/@id` | Generate | ⚠️ | Must generate |
| `Lemma/@writtenForm` | "Arabic lemmas" column | ✅ | |
| `Lemma/@partOfSpeech` | File-based (n/v/a/r) | ✅ | |
| `Lemma/@script` | "Arab" | ✅ | Constant |
| `Sense/@id` | Generate | ⚠️ | Must generate |
| `Sense/@synset` | Reference synset ID | ✅ | |
| `Synset/@id` | PWN ID + POS | ✅ | |
| `Synset/@ili` | PWN ID → ILI mapping | ⚠️ | Requires mapping |
| `Synset/@partOfSpeech` | File-based | ✅ | |
| `Definition` | "Arabic gloss" column | ✅ | 96.5% |
| `Example` | "Arabic examples" column | ✅ | 95.8% |
| `SynsetRelation` | **NOT IN AWN V3** | ❌ | **CRITICAL GAP** |
| `SenseRelation` | **NOT IN AWN V3** | ❌ | **CRITICAL GAP** |

---

## Conclusion

**AWN V3 provides high-quality Arabic lexical content but requires supplementation with relation data from OMW-ARB or OEWN to create a fully functional wn-compatible WordNet.**

### Required Actions:
1. ✅ Use AWN V3 for lemmas, definitions, examples
2. ⚠️ Generate unique IDs for entries and senses
3. ⚠️ Map PWN offsets to ILI identifiers
4. ❌ **Inherit relations from OMW-ARB or derive from OEWN**
5. ⚠️ Define lexicon metadata

### Estimated Effort:
- Data parsing and conversion: ~2-3 days
- Relation inheritance: ~1-2 days
- Testing and validation: ~1 day
- **Total: ~1 week**
