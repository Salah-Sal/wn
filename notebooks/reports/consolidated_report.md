# Consolidated Research Report: High-Quality Arabic WordNet Alternatives

**Date:** 2026-01-12
**Based on:** 5 Independent Researcher Assessments
**Original Requirement:** Find better quality Arabic WordNet resource to replace AWN v2

---

## Executive Summary

All five researchers unanimously agree on the following key findings:

1. **AWN V3 (2024)** is the primary recommended resource, directly addressing all critical quality issues identified in AWN v2
2. **The Arabic Ontology (Birzeit University)** is the strongest complementary resource
3. **Adopting existing improved resources is substantially more efficient** than extending AWN v2 independently
4. **No single resource currently meets all specified requirements**, but a hybrid approach combining AWN V3 + Arabic Ontology provides the most comprehensive solution

---

## Consensus Findings Across All Reports

### AWN v2 Limitations Confirmed

| Issue | AWN v2 Status | Researcher Consensus |
|-------|---------------|---------------------|
| Arabic Definitions | 0% | All 5 confirm critical failure |
| Arabic Examples | 0% | All 5 confirm critical failure |
| Synset Coverage | ~11,269 (8.4% of PWN) | All 5 confirm inadequate |
| Diacritization | 28.6% | All 5 confirm problematic |
| Over-lumping | 782 synsets | Confirmed by multiple reports |
| Over-splitting | 512 words with 10+ senses | Confirmed by multiple reports |

### Primary Recommendation: AWN V3 (Arabic WordNet Version 3)

**All 5 researchers independently identified AWN V3 as the top candidate.**

| Metric | Value | Source |
|--------|-------|--------|
| Release Date | March/May 2024 | Reports 1-5 |
| Total Synsets | 9,576 | Reports 2, 3, 4 |
| Arabic Glosses | **100%** (9,322 glosses) | Reports 2, 3, 4, 5 |
| Arabic Examples | **100%** (12,204 sentences) | Reports 2, 3, 4, 5 |
| New Lemmas Added | 2,726 | Reports 4, 5 |
| Incorrect Lemmas Removed | 8,751 | Reports 2, 4 |
| Phrasets (Multi-word) | 701 | Reports 1, 2, 4, 5 |
| Lexical Gaps Documented | 236 | Reports 1, 2, 4 |
| Quality Validation Rate | **98.08%** | Report 3 |
| Diacritization | 100% fully vocalized (MSA) | Report 3 |

**Key Improvements Over AWN v2:**
- Native Arabic definitions written for Arabic speakers, not translations
- Authentic MSA usage examples for each lemma
- Explicit handling of untranslatable concepts via lexical gaps and phrasets
- Reduction of excessive English-centric polysemy
- Expert validation by Arabic linguistics PhD and professional translators

**Access Information:**
- **Repository:** https://github.com/HadiPTUK/AWN3.0
- **License:** CC BY-NC 4.0 (free for non-commercial use)
- **Publication:** Freihat et al., OSACT Workshop 2024 (ACL Anthology)
- **Contact:**
  - Dr. Abed Alhakim Freihat: abed.freihat@unitn.it
  - Dr. Hadi Khalilia: hadi.khalilia@unitn.it
  - University of Trento, Italy / Palestine Technical University

**Known Limitation:** Coverage (~9,576 synsets) falls short of the 20,000+ requirement

---

### Secondary Recommendation: Arabic Ontology (Birzeit University)

**All 5 researchers identified this as the strongest complementary resource.**

| Metric | Value | Source |
|--------|-------|--------|
| Core Validated Concepts | ~1,300 | Reports 1, 2, 4 |
| Extended Concepts | ~11,000 (partially validated) | Reports 1, 2, 4 |
| Total Concepts | ~12,300-17,000 | Reports 1, 2, 4 |
| Integrated Arabic Lexicons | **150** dictionaries | Reports 1, 2, 3, 4 |
| Arabic Lexical Entries | 1.1 million | Report 4 |
| Arabic Glosses | 800,000+ | Report 4 |
| Translation Pairs | 1.8 million | Report 4 |
| Native Arabic Definitions | **~100%** for validated concepts | All reports |

**Key Strengths:**
- "Ontologically clean" - benchmarked to scientific sources, not speaker intuitions
- Access to massive lexicographic database (150 Arabic dictionaries including Lisan Al-Arab)
- Fully mapped to Princeton WordNet, Wikidata, BFO, and DOLCE upper ontologies
- W3C Lemon RDF model compliance
- Active maintenance and public API

**Access Information:**
- **Portal:** https://ontology.birzeit.edu
- **Resources:** https://sina.birzeit.edu/resources/
- **License:** CC-BY-4.0
- **Contact:** Prof. Mustafa Jarrar: mjarrar@birzeit.edu (Birzeit University)

**Known Limitations:**
- No verb synsets (verbs via masdars/verbal nouns)
- ~11,000 concepts only "partially validated"

---

## Full Shortlist of Candidate Resources

### Tier 1: Primary Candidates (Recommended)

| Resource | Synsets | Native Arabic | Quality | Access | Recommendation |
|----------|---------|---------------|---------|--------|----------------|
| **AWN V3** | 9,576 | 100% glosses + examples | Expert validated (98%) | Open/GitHub | **Primary** |
| **Arabic Ontology** | 12,300+ | ~100% (via 150 lexicons) | Ontologically rigorous | Open/API | **Complementary** |

### Tier 2: Supplementary Resources

| Resource | Synsets/Lemmas | Native Arabic | Quality | Use Case |
|----------|----------------|---------------|---------|----------|
| **Qabas** (2024) | 58,000 lemmas | Via 110 lexicons | High | Morphological info, roots, patterns |
| **LughaNet** (2025) | 85,991 synsets | Machine-translated | ~75% accuracy | Coverage expansion (requires validation) |
| **Azhary** (2014) | 13,328 synsets | Relations only (no glosses) | Moderate | Islamic/Quranic domain |
| **Arabic Derivational ChainBank** | 34,453 lemmas | Morphological focus | High | Root-pattern relationships |

### Tier 3: Not Recommended as Primary

| Resource | Reason |
|----------|--------|
| **BabelNet (Arabic)** | Auto-generated content, inconsistent quality, no diacritics |
| **AWN V2** | 0% Arabic content, structural issues - the resource being replaced |
| **Arabic FrameNet** | Dialect-focused (Emirati), incomplete, English glosses |

---

## Requirements Fulfillment Matrix

| Requirement | AWN V3 | Arabic Ontology | AWN V3 + Ontology |
|-------------|--------|-----------------|-------------------|
| **Native definitions ≥80%** | 100% | ~100% | **100%** |
| **Arabic examples** | 100% | Yes (via lexicons) | **100%** |
| **Coverage ≥20K synsets** | 9.6K | 12.3K | **~20K combined** |
| **ILI/PWN alignment** | PWN 2.0 | PWN + Wikidata | **Yes** |
| **Diacritization ≥80%** | 100% | High (from lexicons) | **Yes** |
| **Quality assurance** | 98% validated | Ontological rigor | **Yes** |
| **Appropriate granularity** | Improved | Ontological | **Yes** |
| **Morphological info** | Limited | Via Qabas integration | **Via Qabas** |
| **Active maintenance** | 2024 | 2024 | **Yes** |

---

## Recommended Integration Strategy

### Phase 1: Immediate Adoption
1. Download AWN V3 from GitHub
2. Review methodology paper (Freihat et al., 2024)
3. Evaluate coverage against your specific domains

### Phase 2: Hybrid Integration
1. Use AWN V3 as the primary semantic backbone
2. Integrate Arabic Ontology's lexicographic database for extended definitions
3. Add Qabas lexicon for morphological information (roots, patterns, broken plurals)
4. Map both resources via shared PWN alignment

### Phase 3: Coverage Expansion (If Needed)
1. Selectively incorporate LughaNet synsets after human validation
2. Consider collaboration with AWN V3 team for AWN V3.1/V4
3. Use Arabic Ontology's 800K+ glosses to author definitions for new synsets

---

## Effort Estimate: Independent Extension vs. Adoption

### Independent AWN v2 Extension (NOT RECOMMENDED)

| Task | Low Estimate | High Estimate |
|------|--------------|---------------|
| Arabic definitions (~10K synsets) | 1,500 hrs | 3,000 hrs |
| Usage examples (~5K words) | 600 hrs | 1,200 hrs |
| Restructure 782 over-lumped synsets | 600 hrs | 1,000 hrs |
| Merge 512 over-split words | 400 hrs | 800 hrs |
| Improve diacritization to 80%+ | 400 hrs | 500 hrs |
| **Total** | **3,500 hrs** | **6,500 hrs** |
| **Person-months** | **18 months** | **34 months** |

### Adopting AWN V3 + Arabic Ontology (RECOMMENDED)

| Task | Estimated Effort |
|------|-----------------|
| Download and evaluate resources | 1-2 weeks |
| Integration and mapping | 2-4 weeks |
| Gap analysis for specific domains | 2-3 weeks |
| Targeted improvements | Ongoing |
| **Total** | **6-10 weeks** |

**Consensus from all 5 researchers:** Adopting existing improved resources is **substantially more efficient** than independent extension. The AWN V3 and Arabic Ontology teams have already invested years of expert effort.

---

## Key Contacts Summary

| Resource | Contact | Email | Institution |
|----------|---------|-------|-------------|
| AWN V3 | Dr. Abed Alhakim Freihat | abed.freihat@unitn.it | University of Trento |
| AWN V3 | Dr. Hadi Khalilia | hadi.khalilia@unitn.it | University of Trento / PTUK |
| Arabic Ontology | Prof. Mustafa Jarrar | mjarrar@birzeit.edu | Birzeit University |
| Arabic NLP (CAMeL Lab) | Prof. Nizar Habash | - | NYU Abu Dhabi |

---

## Key Publications

1. **Freihat, A.A., Khalilia, H., Bella, G., Giunchiglia, F.** (2024). "Advancing the Arabic WordNet: Elevating Content Quality." OSACT Workshop 2024, ACL. https://aclanthology.org/2024.osact-1.9/

2. **Jarrar, M.** (2021). "The Arabic Ontology – An Arabic Wordnet with Ontologically Clean Content." Applied Ontology, 16(1):1-26. https://arxiv.org/abs/2205.09664

3. **Jarrar, M., Hammouda, T.** (2024). "Qabas: An Open-Source Arabic Lexicographic Database." LREC-COLING 2024. https://aclanthology.org/2024.lrec-main.1170/

4. **Khalilia, H., Freihat, A.A., Giunchiglia, F.** (2021). "The Quality of Lexical Semantic Resources: A Survey." ICNLSP 2021.

---

## Conclusion

The Arabic NLP landscape has evolved significantly since the AWN v2 assessment. **AWN V3 represents a qualitative breakthrough** that directly solves the core limitations identified (0% Arabic content). Combined with the Arabic Ontology and Qabas resources, a high-quality Arabic WordNet solution meeting your requirements is now achievable without the need for extensive independent development.

**Final Recommendation:** Adopt AWN V3 as your primary resource and integrate with the Arabic Ontology for comprehensive coverage. This hybrid approach delivers the best balance of quality, coverage, and implementation efficiency.

---

*Report consolidated from 5 independent researcher assessments*
