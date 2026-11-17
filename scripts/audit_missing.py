"""Create a structural inventory; do not infer missing meanings from missing keys."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from report_store import write_report

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
sources = {"english": ROOT / "resources/english/english-wbw-translation.json",
           "turkish": ROOT / "turkish-wbw-translation.json"}
raw = {name: path.read_bytes() for name, path in sources.items()}
data = {}
for name, content in raw.items():
    pairs = json.loads(content, object_pairs_hook=list)
    assert len(pairs) == len(dict(pairs)), f"Duplicate keys in {name}"
    data[name] = dict(pairs)
    assert all(re.fullmatch(r"\d+:\d+:\d+", k) for k in data[name])
    assert all(isinstance(v, str) and v.strip() for v in data[name].values())
en, tr = data["english"], data["turkish"]
numeric = lambda k: tuple(map(int, k.split(":")))
missing = sorted(en.keys() - tr.keys(), key=numeric)
extra = sorted(tr.keys() - en.keys(), key=numeric)

def category(key):
    return "ayah_number" if re.fullmatch(r"\(\d+\)", en[key]) else "word_or_phrase"

counts = Counter(category(k) for k in missing)
by_ayah = defaultdict(list)
for key in sorted(en, key=numeric):
    by_ayah[":".join(key.split(":")[:2])].append(key)
affected = {":".join(k.split(":")[:2]) for k in missing if category(k) == "word_or_phrase"}
OUT.mkdir(exist_ok=True)
summary = {
    "scope": "Structural comparison only; missing keys do not establish missing meanings.",
    "source_sha256": {n: hashlib.sha256(b).hexdigest() for n, b in raw.items()},
    "english_entries": len(en), "turkish_entries": len(tr),
    "missing_keys": len(missing), "missing_by_category": {c: counts[c] for c in ("ayah_number", "word_or_phrase")},
    "extra_turkish_keys": extra,
    "ayahs_with_missing_word_or_phrase_keys": len(affected),
    "missing_by_surah": [
        {"surah": s, **{c: sum(numeric(k)[0] == s and category(k) == c for k in missing)
                        for c in ("ayah_number", "word_or_phrase")}}
        for s in range(1, 115)
    ],
}
contexts = [
    {"ayah": ayah, "entries": [
        {"key": k, "english": en[k], "turkish": tr.get(k),
         "status": "present" if k in tr else "missing_" + category(k)}
        for k in by_ayah[ayah]
    ]}
    for ayah in sorted(affected, key=lambda a: tuple(map(int, a.split(":"))))
]
summary["missing_locations"] = missing
summary["contexts"] = contexts
summary["missing_by_surah"] = [row for row in summary["missing_by_surah"] if row["ayah_number"] or row["word_or_phrase"]]
write_report("missing-summary.json", summary)
assert len(missing) + len(en.keys() & tr.keys()) == len(en)
assert sum(counts.values()) == len(missing)
assert all(path.read_bytes() == raw[name] for name, path in sources.items())
print(json.dumps({k: summary[k] for k in ("english_entries", "turkish_entries", "missing_keys", "missing_by_category", "ayahs_with_missing_word_or_phrase_keys")}, indent=2))
print("Verified: both translation files are byte-for-byte unchanged.")
