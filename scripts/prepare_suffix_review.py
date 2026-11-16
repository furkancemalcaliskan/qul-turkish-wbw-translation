"""Prepare noun-case alignment candidates without editing either translation."""
import json
import re
from collections import defaultdict
from pathlib import Path
from alignment_common import load_baseline

ROOT = Path(__file__).resolve().parents[1]
en, tr = load_baseline()

def lower(text):
    return text.replace("İ", "i").replace("I", "ı").lower()

def normalize_english(text):
    text = re.sub(r"[\[\]()]", "", text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"^(?:the|an|a) ", "", text)

lexicon = defaultdict(set)
for key, text in tr.items():
    if not any(c in text for c in "()[]"):
        lexicon[normalize_english(en[key])].add(lower(text.strip()))

endings = {
    "ablative": ["nden", "ndan", "den", "dan", "ten", "tan"],
    "locative": ["nde", "nda", "de", "da", "te", "ta"],
    "dative": ["ye", "ya", "ne", "na", "e", "a"],
    "genitive": ["nin", "nın", "nun", "nün", "in", "ın", "un", "ün"],
    "instrumental": ["yle", "yla", "le", "la"],
}
relations = {
    "from": ["ablative"], "than": ["ablative"],
    "of": ["ablative", "genitive"], "among": ["ablative", "locative"],
    "in": ["locative", "dative"], "at": ["locative", "dative"],
    "on": ["locative", "dative"], "upon": ["locative", "dative"],
    "over": ["locative", "dative"], "to": ["dative"],
    "into": ["dative"], "towards": ["dative"], "for": ["dative"],
    "about": ["ablative", "locative"], "against": ["dative"],
    "with": ["instrumental"], "by": ["instrumental"],
}
rows = []
for key in sorted(en, key=lambda k: tuple(map(int, k.split(":")))):
    if key in tr:
        continue
    s, a, w = key.split(":")
    previous = f"{s}:{a}:{int(w) - 1}"
    if previous not in tr:
        continue
    source_relation = re.sub(r"[\[\]()]", "", en[previous]).lower().strip()
    relation = re.sub(r"^and ", "", source_relation)
    has_copula = bool(re.match(r"^(?:is|are|was|were|will be|am) ", relation))
    relation = re.sub(r"^(?:is|are|was|were|will be|am) ", "", relation)
    relation = re.sub(r"^(?:surely|even|out) ", "", relation)
    relation = {"in to": "into", "into": "into"}.get(relation, relation)
    if relation not in relations:
        continue
    text = tr[previous]
    candidates = []
    if text == text.strip() and not any(c in text for c in "()[]"):
        for case in relations[relation]:
            copulas = [""]
            if has_copula:
                copulas += ["dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
                            "sın", "sin", "sun", "sün", "sınız", "siniz", "sunuz", "sünüz",
                            "ım", "im", "um", "üm", "ız", "iz", "uz", "üz"]
            for ending in [ending + copula for ending in endings[case] for copula in copulas]:
                if lower(text).endswith(ending):
                    boundary = len(text) - len(ending)
                    if boundary and text[boundary - 1] in "'’":
                        boundary -= 1
                    base, suffix = text[:boundary], text[boundary:]
                    if (len(base) >= 2 or lower(base) == "o") and base[-1].isalpha():
                        candidates.append({"base": base, "suffix": suffix, "case": case,
                                           "lexical_evidence": lower(base) in lexicon[normalize_english(en[key])]})
    rows.append({"previous_key": previous, "previous_english": en[previous], "turkish": text,
                 "missing_key": key, "missing_english": en[key], "relation": relation,
                 "candidates": candidates})
out = ROOT / "reports" / "suffix-candidates.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
with_evidence = [r for r in rows if any(c["lexical_evidence"] for c in r["candidates"])]
print(f"{len(rows)} adjacent-preposition candidates; {len(with_evidence)} have matching noun evidence elsewhere in the local parallel files.")
