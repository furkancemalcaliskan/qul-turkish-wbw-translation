"""Copy missing parenthesized ayah numbers from the English reference."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reference = ROOT / "english-wbw-translation.json"
target = ROOT / "turkish-wbw-translation.json"
reference_before = reference.read_bytes()
target_before = target.read_bytes()
en_pairs = json.loads(reference_before, object_pairs_hook=list)
tr_pairs = json.loads(target_before, object_pairs_hook=list)
en, tr = dict(en_pairs), dict(tr_pairs)
assert len(en_pairs) == len(en) and len(tr_pairs) == len(tr)
assert not tr.keys() - en.keys()
additions = {k: v for k, v in en.items() if k not in tr and re.fullmatch(r"\([0-9]+\)", v)}
# Preserve the original text of existing entries.
lines = target_before.decode("utf-8").splitlines()
assert lines[0] == "{" and lines[-1] == "}"
entry_lines = {}
for line, (key, value) in zip(lines[1:-1], tr_pairs, strict=True):
    body = line.removesuffix(",")
    assert json.loads("{" + body + "}") == {key: value}
    entry_lines[key] = body
for key, value in additions.items():
    assert value == f"({key.split(':')[1]})", f"Unexpected ayah number: {key}"
    entry_lines[key] = "  " + json.dumps(key) + ": " + json.dumps(value)
expected = tr | additions
ordered_keys = [k for k in en if k in expected]
result = ("{\n" + ",\n".join(entry_lines[k] for k in ordered_keys) + "\n}\n").encode("utf-8")
assert json.loads(result) == expected
assert list(json.loads(result)) == ordered_keys
target.write_bytes(result)
assert reference.read_bytes() == reference_before
assert json.loads(target.read_bytes()) == expected
report = {
    "operation": "Copy missing ayah-number entries exactly from English; preserve all existing Turkish pairs.",
    "english_sha256": hashlib.sha256(reference_before).hexdigest(),
    "turkish_before_sha256": hashlib.sha256(target_before).hexdigest(),
    "turkish_after_sha256": hashlib.sha256(result).hexdigest(),
    "added_count": len(additions),
    "additions": additions,
}
report_path = ROOT / "reports" / "ayah-number-additions.json"
report_path.parent.mkdir(exist_ok=True)
# Keep the original audit trail when rerunning an already completed operation.
if additions:
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Added {len(additions)} ayah numbers; preserved {len(tr)} existing pairs; total {len(expected)}.")
print("English bytes unchanged. Turkish SHA-256:", report["turkish_after_sha256"])
