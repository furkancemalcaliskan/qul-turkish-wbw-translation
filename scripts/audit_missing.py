"""Create a structural inventory; do not infer missing meanings from missing keys."""
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports"
sources = {name: ROOT / f"{name}-wbw-translation.json" for name in ("english", "turkish")}
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
(OUT / "missing-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
buffer = io.StringIO(newline="")
writer = csv.writer(buffer, lineterminator="\n")
writer.writerow(["key", "category", "english", "previous_key", "previous_turkish", "next_key", "next_turkish", "review_status"])
for key in missing:
    keys = by_ayah[":".join(key.split(":")[:2])]
    index = keys.index(key)
    previous = next((k for k in reversed(keys[:index]) if k in tr), "")
    following = next((k for k in keys[index + 1:] if k in tr), "")
    writer.writerow([key, category(key), en[key], previous, tr.get(previous, ""), following, tr.get(following, ""), "not_reviewed"])
(OUT / "missing-keys.csv").write_text(buffer.getvalue(), encoding="utf-8")
contexts = [
    {"ayah": ayah, "entries": [
        {"key": k, "english": en[k], "turkish": tr.get(k),
         "status": "present" if k in tr else "missing_" + category(k)}
        for k in by_ayah[ayah]
    ]}
    for ayah in sorted(affected, key=lambda a: tuple(map(int, a.split(":"))))
]
(OUT / "missing-word-contexts.json").write_text(json.dumps(contexts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assert len(missing) + len(en.keys() & tr.keys()) == len(en)
assert sum(counts.values()) == len(missing)
assert all(path.read_bytes() == raw[name] for name, path in sources.items())
print(json.dumps({k: summary[k] for k in ("english_entries", "turkish_entries", "missing_keys", "missing_by_category", "ayahs_with_missing_word_or_phrase_keys")}, indent=2))
print("Verified: both translation files are byte-for-byte unchanged.")
