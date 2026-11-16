"""Reorder Turkish entries by reference order without changing entry text."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
reference = ROOT / "english-wbw-translation.json"
target = ROOT / "turkish-wbw-translation.json"
reference_before = reference.read_bytes()
target_before = target.read_bytes()
en_pairs = json.loads(reference_before, object_pairs_hook=list)
tr_pairs = json.loads(target_before, object_pairs_hook=list)
en, tr = dict(en_pairs), dict(tr_pairs)
assert len(en_pairs) == len(en), "Duplicate reference key"
assert len(tr_pairs) == len(tr), "Duplicate Turkish key"
assert not tr.keys() - en.keys(), "Turkish keys absent from reference"

# Preserve each original key/value line, including its original JSON spelling.
lines = target_before.decode("utf-8").splitlines()
assert lines[0] == "{" and lines[-1] == "}"
entry_lines = {}
for line, (key, value) in zip(lines[1:-1], tr_pairs, strict=True):
    body = line.removesuffix(",")
    assert json.loads("{" + body + "}") == {key: value}
    entry_lines[key] = body
ordered_keys = [key for key in en if key in tr]
result = ("{\n" + ",\n".join(entry_lines[key] for key in ordered_keys) + "\n}\n").encode("utf-8")
assert dict(json.loads(result, object_pairs_hook=list)) == tr
assert list(json.loads(result)) == ordered_keys
target.write_bytes(result)
assert reference.read_bytes() == reference_before
assert json.loads(target.read_bytes()) == tr
print(f"Verified: {len(tr)} unchanged Turkish pairs in reference order.")
print("English SHA-256:", hashlib.sha256(reference_before).hexdigest())
print("Turkish before SHA-256:", hashlib.sha256(target_before).hexdigest())
print("Turkish after SHA-256:", hashlib.sha256(result).hexdigest())
