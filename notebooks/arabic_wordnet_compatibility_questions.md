# Questions to Answer for Building a wn-Compatible Arabic WordNet

This document outlines all questions that must be answered to convert AWN V3 data into a format compatible with the Python `wn` library (WordNet-LMF format).

---

## Part 1: Lexicon Metadata (REQUIRED)

### 1.1 Basic Identification

| Question | Field | Constraint |
|----------|-------|------------|
| What is the unique identifier for this lexicon? | `id` | Must be unique in database, e.g., `awn` or `omw-arb` |
| What is the human-readable label? | `label` | Free text, e.g., "Arabic WordNet V3" |
| What is the BCP-47 language tag? | `language` | Must be valid BCP-47, e.g., `ar` or `arb` (Modern Standard Arabic) |
| What is the maintainer's email? | `email` | Valid email address |
| What is the license URL? | `license` | Full URL, e.g., `https://creativecommons.org/licenses/by-nc/4.0/` |
| What is the version string? | `version` | e.g., "3.0" |

### 1.2 Optional Metadata

| Question | Field |
|----------|-------|
| What is the project URL? | `url` |
| What is the citation text? | `citation` |
| Is there a logo file? | `logo` |
| Any additional description? | `dc:description` |

---

## Part 2: Synset Design Decisions

### 2.1 Synset Identification

| # | Question | Options/Constraints |
|---|----------|---------------------|
| 1 | What ID format for synsets? | e.g., `awn-00001-n`, `awn-{pwn_id}-{pos}` |
| 2 | Should synset IDs include PWN synset offset for traceability? | Yes/No |
| 3 | How to handle AWN V3 synsets that don't have PWN IDs? | Generate new IDs vs. skip |

### 2.2 ILI (Interlingual Index) Mapping

| # | Question | Options |
|---|----------|---------|
| 4 | Does AWN V3 have ILI mappings? | Need to verify from PWN synset IDs |
| 5 | How to convert PWN synset offset to ILI? | Use existing ILI database or leave empty |
| 6 | What to do with lexical gaps (236 marked)? | `ili=""` (empty) vs `ili="in"` (proposed new) |
| 7 | For new concepts, should we propose new ILIs? | Yes (use `ili="in"` + `<ILIDefinition>`) vs No |

### 2.3 Synset Content

| # | Question | Current AWN V3 Status |
|---|----------|----------------------|
| 8 | How many synsets have Arabic definitions? | 9,322 (96.5%) |
| 9 | How many synsets have Arabic examples? | 9,261 (95.8%) |
| 10 | What language tag for Arabic definitions? | `ar`, `arb`, or omit (inherit from lexicon)? |
| 11 | Should English definitions also be included? | Yes (bilingual) vs No (Arabic only) |
| 12 | How to handle synsets with multiple definitions? | Concatenate vs. multiple `<Definition>` elements |

### 2.4 Part of Speech

| # | Question | Mapping Needed |
|---|----------|----------------|
| 13 | How to map AWN V3 POS to wn POS codes? | Nouns→`n`, Verbs→`v`, Adjectives→`a`, Adverbs→`r` |
| 14 | Are there any POS values outside the standard set? | Check for `s` (adj satellite), `t` (phrase), `c` (conj), `p` (adposition), `x` (other), `u` (unknown) |

**wn POS codes:**
```
n = noun
v = verb
a = adjective
r = adverb
s = adjective satellite
t = phrase
c = conjunction
p = adposition
x = other
u = unknown
```

---

## Part 3: Lexical Entry Design

### 3.1 Entry Identification

| # | Question | Options |
|---|----------|---------|
| 15 | What ID format for lexical entries? | e.g., `awn-{lemma}-{pos}`, `awn-entry-{number}` |
| 16 | How to handle Arabic text in IDs? | Transliterate vs. use numeric IDs |
| 17 | How to handle multi-word expressions? | Use underscores: `random_sample` |

### 3.2 Lemma (Word Form)

| # | Question | Constraint |
|---|----------|------------|
| 18 | What is the `writtenForm` for each entry? | Arabic text with or without diacritics |
| 19 | Should lemmas include full diacritization (tashkeel)? | AWN V3 has diacritics, preserve them? |
| 20 | What `script` tag to use? | `Arab` (ISO 15924 for Arabic script) |
| 21 | How to handle phrasets (701 in AWN V3)? | Include as multi-word lemmas vs. separate |

### 3.3 Form Variants

| # | Question | Options |
|---|----------|---------|
| 22 | Should we include variant forms (without diacritics)? | Yes (add `<Form>` elements) vs. No |
| 23 | Should we include broken plurals? | Yes (as `<Form>` with rank > 0) vs. No |
| 24 | Should we include verb conjugations? | Yes vs. No (not in AWN V3) |

### 3.4 Pronunciations (Optional)

| # | Question | Options |
|---|----------|---------|
| 25 | Should we include IPA pronunciations? | Yes vs. No (not in AWN V3) |
| 26 | Should we include audio files? | Yes vs. No |

### 3.5 Tags (Optional)

| # | Question | Options |
|---|----------|---------|
| 27 | Should we include grammatical tags? | e.g., gender, number, definiteness |
| 28 | What tag categories to use? | e.g., `gender`, `number`, `root`, `pattern` |

---

## Part 4: Sense Design

### 4.1 Sense Identification

| # | Question | Options |
|---|----------|---------|
| 29 | What ID format for senses? | e.g., `awn-{entry-id}-{synset-id}`, `awn-sense-{number}` |
| 30 | How to order senses within an entry? | By frequency? By AWN V3 order? |
| 31 | How to order senses within a synset? | Preferred term first? |

### 4.2 Sense Content

| # | Question | AWN V3 Status |
|---|----------|---------------|
| 32 | Are there sense-level examples (vs synset-level)? | Need to check |
| 33 | Are there sense frequency counts? | No in AWN V3 |
| 34 | Should lexical gaps have `lexicalized="false"`? | Yes for 236 gaps |

### 4.3 Adjective Positions (for adjectives only)

| # | Question | Options |
|---|----------|---------|
| 35 | Should Arabic adjectives have position markers? | `a` (attributive), `p` (predicative), `ip` (postnominal) |

---

## Part 5: Semantic Relations

### 5.1 Synset Relations

| # | Question | AWN V3 Status |
|---|----------|---------------|
| 36 | Does AWN V3 have hypernym/hyponym relations? | Need to check (inherited from PWN?) |
| 37 | Does AWN V3 have meronym/holonym relations? | Need to check |
| 38 | Does AWN V3 have domain relations? | Need to check |
| 39 | What relation types are present? | List all |

**Available synset relation types in wn:**
```
hypernym, hyponym, instance_hypernym, instance_hyponym
holonym, meronym (+ holo_part, mero_part, holo_member, etc.)
similar, also, attribute
causes, is_caused_by, entails, is_entailed_by
domain_topic, has_domain_topic, domain_region, has_domain_region
+ 50 more (see constants.py)
```

### 5.2 Sense Relations

| # | Question | AWN V3 Status |
|---|----------|---------------|
| 40 | Does AWN V3 have antonym relations? | Need to check |
| 41 | Does AWN V3 have derivation relations? | Need to check |
| 42 | Does AWN V3 have pertainym relations? | Need to check |

**Available sense relation types in wn:**
```
antonym, also, participle, pertainym, derivation
domain_topic, has_domain_topic, domain_region, has_domain_region
similar, other, feminine, masculine, diminutive, augmentative
```

### 5.3 Cross-Lexicon Relations

| # | Question | Options |
|---|----------|---------|
| 43 | Should we link to English WordNet synsets? | Via ILI (preferred) or direct relation |
| 44 | What English WordNet to reference? | OEWN, PWN 3.0, OMW-EN31 |

---

## Part 6: Data Transformation Questions

### 6.1 AWN V3 CSV to LMF XML Mapping

| AWN V3 Column | LMF Element | Question |
|---------------|-------------|----------|
| `PWN Synset ID` | `Synset@id` | How to format? |
| `English lemmas` | - | Include in Arabic lexicon? |
| `English Gloss` | `Definition` | Include with `language="en"`? |
| `English Examples` | `Example` | Include with `language="en"`? |
| `Arabic lemmas or Gap` | `Lemma@writtenForm` | How to parse multiple lemmas? |
| `Arabic gloss` | `Definition` | Language tag? |
| `Arabic examples` | `Example` | Language tag? |
| `Phrase` (phraset) | ? | How to represent? |

### 6.2 Lemma Parsing

| # | Question | Example |
|---|----------|---------|
| 45 | How are multiple lemmas separated in AWN V3? | Comma? Space? |
| 46 | How to split multi-word expressions? | `وَصْف شَفَهِيّ, وَصْف لَفْظِيّ` |
| 47 | How to handle "GAP" markers? | Create synset with `lexicalized="false"` |

### 6.3 ID Generation

| # | Question | Recommendation |
|---|----------|----------------|
| 48 | How to generate unique entry IDs from Arabic text? | Use numeric sequence + PWN ID |
| 49 | How to ensure ID uniqueness across the lexicon? | Validate with E101 check |
| 50 | Should IDs be human-readable or opaque? | Opaque recommended for Arabic |

---

## Part 7: Validation Requirements

### 7.1 Required Validations (Errors)

| Code | Check | Question |
|------|-------|----------|
| E101 | ID uniqueness | Are all IDs unique? |
| E204 | Synset existence | Does every sense reference a valid synset? |
| E401 | Relation targets | Are all relation targets valid? |

### 7.2 Quality Warnings

| Code | Check | Question |
|------|-------|----------|
| W201 | Entry without senses | Are there orphan entries? |
| W301 | Empty synsets | Are there synsets without any words? |
| W305 | Blank definitions | Any empty definition text? |
| W306 | Blank examples | Any empty example text? |
| W501 | POS mismatch with hypernym | Do hypernyms have matching POS? |

---

## Part 8: Technical Implementation Questions

### 8.1 Output Format

| # | Question | Options |
|---|----------|---------|
| 51 | Which LMF version to target? | 1.0, 1.1, 1.2, 1.3, or 1.4 |
| 52 | What XML encoding? | UTF-8 (required for Arabic) |
| 53 | What DOCTYPE declaration? | `<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.X.dtd">` |

### 8.2 File Structure

| # | Question | Options |
|---|----------|---------|
| 54 | Single file or split by POS? | Single recommended for wn compatibility |
| 55 | Include both English and Arabic in same file? | Single lexicon (Arabic) vs. two lexicons |

### 8.3 Dependencies & Extensions

| # | Question | Options |
|---|----------|---------|
| 56 | Should this lexicon depend on English WordNet? | Use `<Requires>` element? |
| 57 | Is this an extension of OMW-ARB? | Use `<LexiconExtension>` and `<Extends>`? |

---

## Part 9: Data Quality Questions

### 9.1 From AWN V3 Evaluation

| # | Question | AWN V3 Value |
|---|----------|--------------|
| 58 | Total synsets | 9,662 |
| 59 | With Arabic definitions | 9,322 (96.5%) |
| 60 | With Arabic examples | 9,261 (95.8%) |
| 61 | Lexical gaps | 236 |
| 62 | How to handle the ~340 synsets without definitions? | Skip? Add placeholder? |

### 9.2 Content Decisions

| # | Question | Decision Needed |
|---|----------|-----------------|
| 63 | Include synsets marked as GAP? | Yes (with `lexicalized="false"`) vs. No |
| 64 | Include phrasets as synonyms? | Yes vs. No |
| 65 | Keep English gloss alongside Arabic? | Yes (bilingual) vs. No |

---

## Part 10: Specific AWN V3 Questions

### 10.1 Data Structure Analysis Needed

| # | Question | Action Required |
|---|----------|-----------------|
| 66 | What is the exact delimiter between Arabic lemmas? | Analyze CSV |
| 67 | Are there duplicate lemmas across entries? | Check for W203 |
| 68 | Are synset IDs actually PWN offsets? | Verify format |
| 69 | How are relations encoded? | Check if present in data |
| 70 | Is there a separate relations file? | Check AWN V3 repo |

### 10.2 Cross-Reference to OMW

| # | Question | Action Required |
|---|----------|-----------------|
| 71 | How does AWN V3 relate to existing OMW-ARB? | Compare coverage |
| 72 | Should we deprecate OMW-ARB in favor of this? | Community decision |
| 73 | Can we provide ILI mappings from PWN offsets? | Use PWN-ILI mapping file |

---

## Summary: Critical Questions to Answer First

1. **Lexicon ID**: What unique identifier? (`awn`, `awn3`, `omw-arb3`?)
2. **Language Code**: `ar` or `arb`?
3. **Synset ID Format**: How to construct from PWN IDs?
4. **ILI Mapping**: How to get ILI from PWN synset offset?
5. **Lemma Delimiter**: How to parse multiple Arabic lemmas?
6. **Gap Handling**: Include or exclude lexical gaps?
7. **Relations**: Are hypernym/hyponym relations available?
8. **Output Format**: LMF version 1.0 or 1.3/1.4?

---

## Next Steps

1. **Analyze AWN V3 Data Structure**
   - Parse CSV files to understand exact format
   - Count entries, senses, synsets
   - Identify relation data

2. **Create PWN-to-ILI Mapping**
   - Download ILI database
   - Map PWN offsets to ILI identifiers

3. **Design ID Scheme**
   - Define entry ID format
   - Define sense ID format
   - Define synset ID format

4. **Build Converter Script**
   - Read AWN V3 CSV
   - Generate LMF XML
   - Validate output

5. **Test with wn Library**
   - Load generated LMF
   - Run validation checks
   - Query data

---

## Reference: Minimal LMF Example for Arabic

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">
<LexicalResource xmlns:dc="http://purl.org/dc/elements/1.1/">

  <Lexicon id="awn3"
           label="Arabic WordNet V3"
           language="arb"
           email="contact@example.com"
           license="https://creativecommons.org/licenses/by-nc/4.0/"
           version="3.0"
           url="https://github.com/HadiPTUK/AWN3.0">

    <LexicalEntry id="awn3-entry-1">
      <Lemma partOfSpeech="n" writtenForm="كيان" script="Arab" />
      <Sense id="awn3-sense-1" synset="awn3-00001740-n" />
    </LexicalEntry>

    <Synset id="awn3-00001740-n" ili="i1" partOfSpeech="n">
      <Definition language="ar">بنية ذات وجود خاص بحد ذاته</Definition>
      <Definition language="en">that which is perceived to have its own existence</Definition>
      <Example language="ar">الكيان التعليمي في بلادنا متطور</Example>
    </Synset>

  </Lexicon>

</LexicalResource>
```

---

## Files to Reference

| File | Purpose |
|------|---------|
| `/wn/wn/schema.sql` | Database schema - all tables and fields |
| `/wn/wn/constants.py` | Valid POS codes, relation types |
| `/wn/wn/lmf.py` | LMF parsing logic |
| `/wn/wn/validate.py` | Validation checks |
| `/wn/tests/data/mini-lmf-1.0.xml` | Example LMF file |
| `/wn/AWN3.0/*.csv` | Source AWN V3 data |
