#!/usr/bin/env python3
"""
Generate WN-LMF XML file from AWN V3 CSV data.

This script:
1. Parses AWN V3 CSV files (Nouns, Verbs, Adjectives, Adverbs)
2. Maps PWN 2.0 offsets to ILI identifiers
3. Generates a valid WN-LMF 1.3 XML file
"""

import pandas as pd
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict
from pathlib import Path
import unicodedata

# Configuration
AWN3_DIR = Path('/Users/salahmac/Desktop/MLProjects/wn-project/wn/AWN3.0')
OUTPUT_FILE = AWN3_DIR / 'awn3.xml'
ILI_MAP_FILE = AWN3_DIR / 'ili-map-pwn20.tab'

# Lexicon metadata
LEXICON_ID = 'awn3'
LEXICON_LABEL = 'Arabic WordNet V3'
LEXICON_LANGUAGE = 'arb'
LEXICON_EMAIL = 'abed.freihat@unitn.it'
LEXICON_LICENSE = 'https://creativecommons.org/licenses/by-nc/4.0/'
LEXICON_VERSION = '3.0'
LEXICON_URL = 'https://github.com/HadiPTUK/AWN3.0'
LEXICON_CITATION = 'Freihat et al. (2024). Advancing the Arabic WordNet: Elevating Content Quality. OSACT 2024.'

# POS mapping
POS_MAP = {'n': 'n', 'v': 'v', 'a': 'a', 'r': 'r'}

# File paths
CSV_FILES = {
    'n': AWN3_DIR / '2. Nouns - organized columns.csv',
    'v': AWN3_DIR / '4. Verbs - organized columns.csv',
    'a': AWN3_DIR / '6. Adjectives - organized columns.csv',
    'r': AWN3_DIR / '8. Adverbs - organized columns.csv'
}


def load_ili_mapping():
    """Load ILI mapping from OEWN (Open English WordNet 2024).

    AWN V3 uses PWN 3.0 offsets (same as OEWN), so we can map directly
    from OEWN synset IDs to ILI.
    """
    import wn

    ili_map = {}  # (offset, pos) -> ili_id

    print("Loading OEWN for ILI mapping...")
    oewn = wn.Wordnet('oewn:2024')

    for ss in oewn.synsets():
        # Extract offset from synset ID: oewn-00001740-n -> (1740, 'n')
        parts = ss.id.split('-')
        if len(parts) >= 3:
            offset = int(parts[1])
            pos = parts[2]
            ili = ss.ili
            if ili:
                ili_map[(offset, pos)] = ili.id

    return ili_map


def clean_lemmas(lemma_str):
    """Clean Arabic lemmas - remove brackets, split by comma."""
    if not lemma_str or pd.isna(lemma_str):
        return []

    s = str(lemma_str).strip()

    # Check for GAP marker
    if 'GAP' in s.upper():
        return []

    # Remove various bracket types
    s = re.sub(r'[\[\]<>(){}]', '', s)

    # Split by comma
    lemmas = [l.strip() for l in s.split(',') if l.strip()]

    # Remove empty entries
    lemmas = [l for l in lemmas if l and not l.isspace()]

    return lemmas


def normalize_for_id(text):
    """Create a safe ID from Arabic text."""
    # Remove diacritics for ID
    normalized = unicodedata.normalize('NFD', text)
    # Keep only base characters
    base = ''.join(c for c in normalized if not unicodedata.combining(c))
    # Replace spaces with underscores
    base = base.replace(' ', '_')
    # Remove any remaining non-alphanumeric (except underscore)
    base = re.sub(r'[^\w]', '', base, flags=re.UNICODE)
    return base[:50]  # Limit length


def escape_xml(text):
    """Escape special XML characters."""
    if not text:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


def parse_csv_files():
    """Parse all AWN V3 CSV files and extract data."""
    all_data = []

    for pos, filepath in CSV_FILES.items():
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            continue

        df = pd.read_csv(filepath)

        # Find PWN ID column
        pwn_col = None
        for col in df.columns:
            col_lower = col.lower().strip()
            if col_lower == 'id' or 'pwn' in col_lower:
                pwn_col = col
                break

        # Find Arabic lemmas column
        lemma_col = None
        for col in df.columns:
            if 'arabic lemmas' in col.lower():
                lemma_col = col
                break

        # Find cleaned/GAP column
        cleaned_col = None
        for col in df.columns:
            if 'cleaned' in col.lower() or 'gap' in col.lower():
                cleaned_col = col

        # Find Arabic gloss column
        gloss_col = None
        for col in df.columns:
            if 'arabic gloss' in col.lower():
                gloss_col = col
                break

        # Find Arabic examples column
        example_col = None
        for col in df.columns:
            if 'arabic exam' in col.lower():
                example_col = col
                break

        # Find phraset column
        phraset_col = None
        for col in df.columns:
            if 'phrase' in col.lower():
                phraset_col = col
                break

        for idx, row in df.iterrows():
            pwn_id = row.get(pwn_col) if pwn_col else None

            if pd.isna(pwn_id):
                continue

            try:
                pwn_id = int(float(pwn_id))
            except:
                continue

            # Get Arabic lemmas - prefer cleaned column
            arabic_lemmas_raw = None
            if cleaned_col and pd.notna(row.get(cleaned_col)):
                arabic_lemmas_raw = row[cleaned_col]
            elif lemma_col and pd.notna(row.get(lemma_col)):
                arabic_lemmas_raw = row[lemma_col]

            # Check for GAP
            is_gap = False
            if arabic_lemmas_raw and 'GAP' in str(arabic_lemmas_raw).upper():
                is_gap = True
                lemmas = []
            else:
                lemmas = clean_lemmas(arabic_lemmas_raw)

            # Get gloss and examples
            arabic_gloss = row.get(gloss_col) if gloss_col else None
            arabic_examples = row.get(example_col) if example_col else None
            phraset = row.get(phraset_col) if phraset_col else None

            all_data.append({
                'pos': pos,
                'pwn_id': pwn_id,
                'lemmas': lemmas,
                'arabic_gloss': str(arabic_gloss).strip() if pd.notna(arabic_gloss) else None,
                'arabic_examples': str(arabic_examples).strip() if pd.notna(arabic_examples) else None,
                'phraset': str(phraset).strip() if pd.notna(phraset) else None,
                'is_gap': is_gap
            })

    return all_data


def generate_lmf_xml(data, ili_map):
    """Generate WN-LMF XML from parsed data."""

    # XML declaration and DOCTYPE
    xml_header = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">
'''

    # Create root element
    root = ET.Element('LexicalResource')
    root.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')

    # Create Lexicon element
    lexicon = ET.SubElement(root, 'Lexicon')
    lexicon.set('id', LEXICON_ID)
    lexicon.set('label', LEXICON_LABEL)
    lexicon.set('language', LEXICON_LANGUAGE)
    lexicon.set('email', LEXICON_EMAIL)
    lexicon.set('license', LEXICON_LICENSE)
    lexicon.set('version', LEXICON_VERSION)
    lexicon.set('url', LEXICON_URL)
    lexicon.set('citation', LEXICON_CITATION)

    # Track unique entries and synsets
    entry_counter = 0
    sense_counter = 0
    synsets_created = set()
    ili_mapped = 0
    ili_missing = 0

    # Group by synset (PWN ID + POS)
    synset_data = defaultdict(lambda: {'lemmas': [], 'gloss': None, 'examples': None, 'is_gap': False, 'phraset': None})

    for item in data:
        key = (item['pwn_id'], item['pos'])
        synset_data[key]['lemmas'].extend(item['lemmas'])
        if item['arabic_gloss'] and not synset_data[key]['gloss']:
            synset_data[key]['gloss'] = item['arabic_gloss']
        if item['arabic_examples'] and not synset_data[key]['examples']:
            synset_data[key]['examples'] = item['arabic_examples']
        if item['is_gap']:
            synset_data[key]['is_gap'] = True
        if item['phraset'] and not synset_data[key]['phraset']:
            synset_data[key]['phraset'] = item['phraset']

    # Collect entries and synsets separately (entries must come before synsets in LMF)
    entries_to_add = []
    synsets_to_add = []

    # Generate entries and synsets
    for (pwn_id, pos), sdata in synset_data.items():
        # Create synset ID
        synset_id = f"{LEXICON_ID}-{pwn_id:08d}-{pos}"

        # Get ILI mapping
        ili_id = ili_map.get((pwn_id, pos))
        # Try adjective satellite for adjectives
        if not ili_id and pos == 'a':
            ili_id = ili_map.get((pwn_id, 's'))

        if ili_id:
            ili_mapped += 1
        else:
            ili_missing += 1

        # Remove duplicate lemmas while preserving order
        seen = set()
        unique_lemmas = []
        for lemma in sdata['lemmas']:
            if lemma not in seen:
                seen.add(lemma)
                unique_lemmas.append(lemma)

        # Create LexicalEntry for each unique lemma
        for lemma in unique_lemmas:
            entry_counter += 1
            entry_id = f"{LEXICON_ID}-e{entry_counter:06d}"

            entry_data = {
                'id': entry_id,
                'lemma': lemma,
                'pos': pos,
                'synset_id': synset_id,
                'sense_counter': sense_counter + 1,
                'is_gap': sdata['is_gap']
            }
            entries_to_add.append(entry_data)
            sense_counter += 1

        # Create Synset data (only once per PWN ID + POS)
        if synset_id not in synsets_created:
            synsets_created.add(synset_id)

            synset_data_item = {
                'id': synset_id,
                'pos': pos,
                'ili': ili_id,
                'gloss': sdata['gloss'],
                'examples': sdata['examples']
            }
            synsets_to_add.append(synset_data_item)

    # Add all entries first
    for entry_data in entries_to_add:
        entry = ET.SubElement(lexicon, 'LexicalEntry')
        entry.set('id', entry_data['id'])

        # Add Lemma
        lemma_elem = ET.SubElement(entry, 'Lemma')
        lemma_elem.set('writtenForm', entry_data['lemma'])
        lemma_elem.set('partOfSpeech', entry_data['pos'])
        lemma_elem.set('script', 'Arab')

        # Add Sense
        sense_id = f"{LEXICON_ID}-s{entry_data['sense_counter']:06d}"
        sense = ET.SubElement(entry, 'Sense')
        sense.set('id', sense_id)
        sense.set('synset', entry_data['synset_id'])

        # Mark lexical gaps
        if entry_data['is_gap']:
            sense.set('lexicalized', 'false')

    # Then add all synsets
    for synset_data_item in synsets_to_add:
        synset = ET.SubElement(lexicon, 'Synset')
        synset.set('id', synset_data_item['id'])
        synset.set('partOfSpeech', synset_data_item['pos'])

        # Add ILI if available
        if synset_data_item['ili']:
            synset.set('ili', synset_data_item['ili'])
        else:
            synset.set('ili', '')  # Empty ILI for unmapped synsets

        # Add Definition
        if synset_data_item['gloss']:
            definition = ET.SubElement(synset, 'Definition')
            definition.text = synset_data_item['gloss']

        # Add Example
        if synset_data_item['examples']:
            example = ET.SubElement(synset, 'Example')
            example.text = synset_data_item['examples']

    # Pretty print
    xml_str = ET.tostring(root, encoding='unicode')

    # Parse and prettify
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ')

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]

    # Replace XML declaration with our header
    lines[0] = ''
    final_xml = xml_header + '\n'.join(lines[1:])

    print(f"\n=== Generation Stats ===")
    print(f"Synsets created: {len(synsets_created)}")
    print(f"Lexical entries: {entry_counter}")
    print(f"Senses: {sense_counter}")
    print(f"ILI mapped: {ili_mapped}")
    print(f"ILI missing: {ili_missing}")

    return final_xml


def main():
    print("=== AWN V3 LMF Generator ===\n")

    # Load ILI mapping
    print("Loading PWN 2.0 → ILI mapping...")
    ili_map = load_ili_mapping()
    print(f"Loaded {len(ili_map)} ILI mappings")

    # Parse CSV files
    print("\nParsing AWN V3 CSV files...")
    data = parse_csv_files()
    print(f"Parsed {len(data)} entries")
    print(f"  Nouns: {sum(1 for d in data if d['pos']=='n')}")
    print(f"  Verbs: {sum(1 for d in data if d['pos']=='v')}")
    print(f"  Adjectives: {sum(1 for d in data if d['pos']=='a')}")
    print(f"  Adverbs: {sum(1 for d in data if d['pos']=='r')}")
    print(f"  With lemmas: {sum(1 for d in data if d['lemmas'])}")
    print(f"  Lexical gaps: {sum(1 for d in data if d['is_gap'])}")

    # Generate XML
    print("\nGenerating LMF XML...")
    xml_content = generate_lmf_xml(data, ili_map)

    # Write output
    print(f"\nWriting to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(xml_content)

    print(f"\nDone! Output: {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    main()
