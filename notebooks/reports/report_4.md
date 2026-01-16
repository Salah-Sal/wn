# Arabic WordNet alternatives: AWN V3 emerges as the leading candidate

A 2024 release from the University of Trento has fundamentally transformed the Arabic WordNet landscape. **AWN V3** directly addresses every critical quality issue identified with AWN v2—adding native Arabic definitions and examples to all synsets while correcting thousands of errors. Combined with the **Arabic Ontology** from Birzeit University, researchers now have viable high-quality options that were unavailable just two years ago.

The most significant finding is that **no single resource currently meets all specified requirements**, but AWN V3 comes closest for quality-focused applications, while a hybrid approach combining AWN V3 with the Arabic Ontology's rich lexicographic database offers the most comprehensive solution. The estimated effort to extend AWN v2 independently would require **3,500–6,500 person-hours**, making adoption of existing improved resources the more practical path forward.

## Shortlist of candidate resources

### 1. AWN V3 (Arabic WordNet Version 3) — RECOMMENDED

**Version:** V3, released March 2024  
**Developers:** Abed Alhakim Freihat, Hadi Khalilia, Gábor Bella, Fausto Giunchiglia (University of Trento, Palestine Technical University)

| Metric | Value |
|--------|-------|
| Total synsets | ~9,576 (quality-focused, not coverage-focused) |
| Synsets updated | 58%+ of AWN V1 corrected/extended |
| Arabic glosses | **100%** (9,322 glosses added) |
| Arabic examples | **100%** (12,204 example sentences) |
| New lemmas added | 2,726 |
| Incorrect lemmas removed | 8,751 |
| Phrasets | 701 (for untranslatable concepts) |
| Lexical gaps documented | 236 |

**Native Arabic content:** This is the first AWN version with native Arabic definitions and examples for all synsets. The development methodology used expert Arabic linguists with a quality-over-quantity philosophy, explicitly addressing Western-centric representation problems in previous versions.

**Cross-lingual alignment:** Based on PWN 2.0 alignment (inherited from AWN V1), maintains synset structure compatibility with Princeton WordNet and Global WordNet Association resources.

**Access:** Open source, freely available. Published at OSACT Workshop 2024 (ACL Anthology).

**Known limitations:**
- Coverage remains at approximately **8.1%** of PWN's 117,659 synsets (below the 20K minimum requirement)
- POS distribution likely mirrors AWN V1's noun-heavy structure; adjective/adverb coverage not explicitly improved
- Diacritization rate not specified in available documentation
- Aligned to older PWN 2.0 rather than PWN 3.0/3.1 or Open English WordNet

**Contact:**
- Dr. Abed Alhakim Freihat: abed.freihat@unitn.it
- Dr. Hadi Khalilia: hadi.khalilia@unitn.it
- University of Trento, Department of Information Engineering and Computer Science

---

### 2. Arabic Ontology (Birzeit University) — STRONG ALTERNATIVE

**Version:** Ongoing development since 2010, major publication 2021  
**Developer:** Prof. Mustafa Jarrar, Sina Institute for Knowledge Engineering and Arabic Technologies, Birzeit University

| Metric | Value |
|--------|-------|
| Well-investigated concepts | ~1,300 |
| Partially validated concepts | ~11,000 |
| Total concepts | ~12,300+ |
| Arabic lexical entries | 1.1 million |
| English lexical entries | 1.1 million |
| Arabic glosses | 800,000+ |
| Semantic relations | 489,000 (170K SubTypeOf, 29K PartOf, 260K Has-Domain, 30K other) |
| Integrated lexicons | **150** Arabic-multilingual dictionaries |
| Translation pairs | 1.8 million |

**Native Arabic content:** Achieves effectively **100%** native Arabic definitions for validated concepts. Glosses are formulated using strict ontological rules and benchmarked to scientific sources rather than mere translation. Includes Arabic usage examples and example instances. The resource explicitly distinguishes Classical vs. Modern Standard Arabic through era/area metadata.

**Cross-lingual alignment:** Fully mapped to Princeton WordNet and Wikidata, follows W3C Lemon RDF model. Linked to BFO and DOLCE upper ontologies for formal semantic applications.

**Access:** Open access via https://ontology.birzeit.edu (lexicographic search engine), API available, CC-BY-4.0 license.

**Known limitations:**
- Total validated concept count (~12,300) below 20K synset requirement
- No verb synsets—verbs captured through maṣdars (verbal nouns) following ontological principles, which may complicate integration with standard WordNet applications
- "Partially validated" concepts (11,000) vary in quality
- Academic project dependent on continued institutional support

**Contact:**
- Prof. Mustafa Jarrar: mjarrar@birzeit.edu
- Currently also Visiting Research Professor at Hamad Bin Khalifa University, Qatar (2025)
- Web: https://sina.birzeit.edu

---

### 3. LughaNet (2025) — HIGHEST COVERAGE

**Version:** Published January 2025  
**Developers:** Automated construction using machine learning methods

| Metric | Value |
|--------|-------|
| Total synsets | **85,991** (~73% of PWN coverage) |
| Unique Arabic words | 102,355 |
| Average words per synset | 3.16 (higher than PWN's 1.759) |
| Single-word synsets | 33.81% (vs. PWN's 54%) |
| Validation accuracy | ~75.4% (sample evaluation) |

**Native Arabic content:** Arabic definitions and examples exist but are **machine-translated** from English, not natively authored. Quality concerns are significant—this resource requires substantial human validation before production use.

**Cross-lingual alignment:** Aligned to Princeton WordNet 3.0 (117,659 synsets), achieving approximately 73% coverage.

**Access:** Research/academic use, published in Journal of Soft Computing and Data Mining Vol. 6 No. 1 (2025).

**Known limitations:**
- **Quality is the critical issue**: Automatically generated content with only ~75% validation accuracy
- Machine-translated glosses do not constitute native Arabic definitions
- Over-lumping likely persists (3.16 words/synset average is high)
- No evidence of linguistic expert review or inter-annotator agreement scores
- Not yet widely adopted or validated in downstream applications

**Recommendation:** Useful as a coverage expansion layer or for bootstrapping, but not suitable as primary resource without extensive human curation. Could provide candidate synsets for human validation to extend AWN V3.

---

### 4. AWN V2 + SAFAR Framework (Mohammed V University, Morocco)

**Version:** V2, 2016  
**Developers:** Prof. Karim Bouzoubaa's team at Mohammadia School of Engineers (EMI)

| Metric | Value |
|--------|-------|
| Total synsets | 11,269 |
| Arabic glosses | **0%** |
| Arabic examples | **0%** |
| Diacritization | 28.6% |
| PWN alignment | PWN 2.0 |

**Access:** Open source via Global WordNet Association, LMF/XML format, CC-BY-SA 3.0 license. Integrated into SAFAR (Software Architecture For ARabic) NLP platform.

**Assessment:** This is essentially the resource being replaced. Documented here for completeness and because the SAFAR framework and ongoing Moroccan research may produce future improvements.

**Contact:** Prof. Karim Bouzoubaa, EMI, Mohammed V University, Rabat, Morocco

---

### 5. Qabas Lexicon (Birzeit University, 2024) — COMPLEMENTARY RESOURCE

**Version:** June 2024  
**Developer:** Prof. Mustafa Jarrar, Birzeit University

| Metric | Value |
|--------|-------|
| Lemmas | 58,000 |
| Linked lexicons | 110 |
| Linked corpora | 12 morphologically annotated corpora |

**Native Arabic content:** Rich Arabic definitions, morphological information including roots and patterns, Quran morphology tagging. Provides comprehensive lexicographic data in graph format.

**Cross-lingual alignment:** Not a WordNet structure but links to Arabic Ontology infrastructure.

**Access:** Open source at https://sina.birzeit.edu/qabas

**Assessment:** Not a WordNet replacement but an excellent complementary resource for Arabic definitions, morphological patterns, and root information that could enhance any WordNet-based resource.

---

## Requirements assessment matrix

| Requirement | AWN V3 | Arabic Ontology | LughaNet | AWN V2 |
|-------------|--------|-----------------|----------|--------|
| **Native Arabic definitions (≥80%)** | ✅ 100% | ✅ ~100% | ❌ MT | ❌ 0% |
| **Arabic usage examples** | ✅ 100% | ✅ Yes | ⚠️ MT | ❌ 0% |
| **Coverage (≥20K synsets)** | ❌ ~9.6K | ❌ ~12.3K | ✅ ~86K | ❌ ~11K |
| **ILI/PWN alignment** | ✅ PWN 2.0 | ✅ PWN + Wikidata | ✅ PWN 3.0 | ✅ PWN 2.0 |
| **Balanced POS (adj ≥10%, adv ≥5%)** | ⚠️ Limited | ⚠️ No verbs | ❓ Unknown | ❌ 5.9%/2.9% |
| **Diacritization (≥80%)** | ❓ Unspecified | ⚠️ Partial | ⚠️ Partial | ❌ 28.6% |
| **Quality assurance/expert review** | ✅ Yes | ✅ Yes | ❌ Automated | ⚠️ Limited |
| **Appropriate granularity** | ✅ Improved | ✅ Ontological | ❌ Inherited | ❌ Over-split/lumped |
| **Active maintenance** | ✅ 2024 | ✅ 2024 | ⚠️ 2025 | ❌ 2016 |

## Primary recommendation

**AWN V3 is the recommended primary resource**, with the Arabic Ontology as essential complement.

AWN V3 directly addresses the critical quality requirements that motivated this search: native Arabic definitions (100%), Arabic usage examples (100%), and appropriate granularity through expert-driven synset correction. The development team explicitly prioritized "quality over quantity" and addressed Western-centric representation issues. The resource maintains standard WordNet structure and PWN alignment, ensuring compatibility with existing NLP pipelines.

The coverage limitation (~9,600 synsets vs. 20,000+ requirement) is real but manageable through a **hybrid approach**:

1. **Use AWN V3 as the primary semantic backbone** for its verified, high-quality content
2. **Integrate Arabic Ontology's lexicographic database** (150 lexicons, 800K+ Arabic glosses) to extend definitions and synonymy
3. **Use Qabas lexicon** for morphological information (roots, patterns, broken plurals)
4. **Selectively incorporate LughaNet synsets** after human validation to expand coverage for specific domains

The AWN V3 team (University of Trento) and Arabic Ontology team (Birzeit University) have overlapping researchers (Dr. Khalilia works with both groups), suggesting potential for formal collaboration to merge resources.

## Promising academic projects and future directions

Several active research initiatives warrant monitoring or collaboration outreach:

**CAMeL Lab (NYU Abu Dhabi)** maintains substantial Arabic NLP resources including the SAMER lexicon (26,000+ lemmas with readability annotations) and MADAR dialectal lexicon (1,045 concepts × 25 city dialects). Contact: Prof. Nizar Habash. While not WordNet-structured, these resources could inform dialect-aware extensions.

**QCRI (Qatar Computing Research Institute)** leads Arabic NLP tool development including Farasa (segmentation, diacritization, NER) but does not currently maintain lexical-semantic databases. Their tools could support resource construction workflows.

**Arabic VerbNet** provides verb semantic frames aligned with AWN structure, superior to Arabic PropBank for verb coverage. Available on GitHub (JaouadMousser/Arabic-Verbnet). Could address AWN's verb coverage limitations.

**SinaTools ecosystem** (Birzeit University) includes open-source Arabic NLP tools (lemmatization, POS tagging, NER) that integrate with the Arabic Ontology and could facilitate resource development workflows.

The **ArabicNLP conference** (formerly WANLP) and the **Arabic NLP School** (next session March 2026, Rabat) represent the primary venues for Arabic lexical-semantic research and potential collaboration partners.

## Effort estimate for independent AWN V2 extension

If pursuing independent extension rather than adopting existing resources, estimated effort totals **3,500–6,500 person-hours** (18–34 person-months at full-time):

| Task | Low estimate | High estimate |
|------|--------------|---------------|
| Arabic definitions (~10K synsets) | 1,500 hrs | 3,000 hrs |
| Usage examples (~5K words) | 600 hrs | 1,200 hrs |
| Restructure 782 over-lumped synsets | 600 hrs | 1,000 hrs |
| Merge 512 over-split words | 400 hrs | 800 hrs |
| Improve diacritization to 80%+ | 400 hrs | 500 hrs |
| **Total** | **3,500 hrs** | **6,500 hrs** |

**Recommended methodology** combines semi-automatic generation with human validation: use Arabic dictionaries (Arramooz Alwaseet, Arabic Ontology's 150 lexicons) as definition sources, apply LLM-assisted draft generation, then crowdsource validation with expert review for core vocabulary. State-of-the-art Arabic diacritization tools (SUKOUN, CAMeLBERT) achieve 98%+ accuracy, reducing manual diacritization burden.

However, **adopting AWN V3 is substantially more efficient** than independent extension. The AWN V3 team has already invested significant expert effort addressing quality dimensions—building on their work rather than duplicating it represents the pragmatic path forward. Collaboration with the Trento/Birzeit teams to extend AWN V3's coverage using the Arabic Ontology's lexicographic resources would likely achieve better results than independent development.

## Key publications

- Freihat, A.A., Khalilia, H., Bella, G., Giunchiglia, F. (2024). "Advancing the Arabic WordNet: Elevating Content Quality." OSACT Workshop 2024, ACL. arXiv:2403.20215
- Jarrar, M. (2021). "The Arabic Ontology – An Arabic Wordnet with Ontologically Clean Content." Applied Ontology, 16(1):1-26. IOS Press.
- Jarrar, M., Hammouda, T. (2024). "Qabas: An Open-Source Arabic Lexicographic Database." LREC-COLING 2024.
- Khalilia, H., Freihat, A.A., Giunchiglia, F. (2021). "The Quality of Lexical Semantic Resources: A Survey." ICNLSP 2021.
- Regragui et al. (2016). "Arabic WordNet: New Content and New Applications." Global WordNet Conference.