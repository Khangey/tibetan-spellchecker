"""
Tibetan Syllable Spellchecker
Uses dictionary resources from tibetan-spellchecker project
"""
import json
from pathlib import Path

# Tibetan tsheg (syllable separator) U+0F0B
TSHEG = "\u0f0b"
# Tibetan shad (period) U+0F0D - often appears at end of syllable
SHAD = "\u0f0d"


def load_dictionary(base_dir: Path) -> set:
    """Load all valid syllables from dictionary files."""
    valid = set()
    syllables_dir = base_dir / "syllables"

    # Load suffixes
    with open(syllables_dir / "suffixes.json", "r", encoding="utf-8") as f:
        suffixes = json.load(f)

    # Add NB (no suffix) type - only empty suffix
    suffixes["NB"] = [""]

    # Load root.txt: format is "root/TYPE" (e.g., "ཀ/A", "དཀ/NB")
    with open(syllables_dir / "root.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "/" in line:
                root, suffix_type = line.split("/", 1)
                root = root.strip()
                suffix_type = suffix_type.strip()
                if suffix_type in suffixes:
                    for suf in suffixes[suffix_type]:
                        valid.add(root + suf)

    # Load wasurs.txt: format "syllable" or "syllable/TYPE" (full form or root+type)
    with open(syllables_dir / "wasurs.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "/" in line:
                root, suffix_type = line.split("/", 1)
                if suffix_type.strip() in suffixes:
                    for suf in suffixes[suffix_type.strip()]:
                        valid.add(root.strip() + suf)
            else:
                valid.add(line)

    # Load rare.txt: full syllable forms, some with /C
    with open(syllables_dir / "rare.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "/" in line:
                root, suffix_type = line.split("/", 1)
                if suffix_type.strip() in suffixes:
                    for suf in suffixes[suffix_type.strip()]:
                        valid.add(root.strip() + suf)
            else:
                valid.add(line)

    # Load exceptions.txt: full forms
    with open(syllables_dir / "exceptions.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                valid.add(line)

    # Load proper-names.txt
    with open(syllables_dir / "proper-names.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "/" in line:
                root, suffix_type = line.split("/", 1)
                if suffix_type.strip() in suffixes:
                    for suf in suffixes[suffix_type.strip()]:
                        valid.add(root.strip() + suf)
            else:
                valid.add(line)

    # Load supplement.txt - 补充词典（常用但未生成的音节，用户可编辑添加）
    supplement_file = syllables_dir / "supplement.txt"
    if supplement_file.exists():
        with open(supplement_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    valid.add(line)

    return valid


def split_syllables(text: str) -> list[tuple[str, int, int]]:
    """
    Split Tibetan text into syllables by tsheg.
    Returns list of (syllable, start_idx, end_idx) for each syllable.
    """
    result = []
    start = 0
    for i, char in enumerate(text):
        if char == TSHEG:
            if i > start:
                result.append((text[start:i], start, i))
            start = i + 1
    if start < len(text):
        result.append((text[start:], start, len(text)))
    return result


def spellcheck_text(text: str, valid_syllables: set) -> list[dict]:
    """
    Check Tibetan text for spelling errors.
    Returns list of {syllable, start, end, valid} for each syllable.
    """
    syllables = split_syllables(text)
    results = []
    for syl, start, end in syllables:
        # Skip empty, spaces, punctuation
        if not syl or syl.isspace():
            continue
        # Skip non-Tibetan (numbers, etc.)
        if not any(ord(c) >= 0x0F00 and ord(c) <= 0x0FFF for c in syl):
            continue
        # Strip trailing shad for dictionary lookup (ལེགས། -> ལེགས)
        lookup = syl.rstrip(SHAD)
        results.append({
            "syllable": syl,
            "start": start,
            "end": end,
            "valid": lookup in valid_syllables,
        })
    return results
