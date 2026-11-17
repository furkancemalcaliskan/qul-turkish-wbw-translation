"""Independently verify the first Arabic-led semantic batch and its exact scope."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from audit_resources import MANIFEST, RESOURCES, inventory, read
from report_store import STATE, load, read_report, write_report

ROOT = Path(__file__).resolve().parents[1]
if len(load(STATE)["batches"]) > 1:
    # Compatibility command: later batches require the complete ordered ledger.
    from semantic_review import validate
    validate()
    raise SystemExit(0)
report = read_report("semantic-review-001.json")
assert report["baseline"] == "661144b"
before_raw = subprocess.check_output(["git", "show", report["baseline"]+":turkish-wbw-translation.json"], cwd=ROOT)
before = json.loads(before_raw)
after = read(ROOT / "turkish-wbw-translation.json")
en = read(RESOURCES / "english/english-wbw-translation.json")
ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
assert inventory() == read(MANIFEST)["files"]
assert en == json.loads(subprocess.check_output(["git", "show", "4503cdc:english-wbw-translation.json"], cwd=ROOT))
assert list(after) == list(before) == list(en)
assert len(after) == 83665
assert all(isinstance(value, str) and value.strip() == value and value for value in after.values())
updates = {}
for group in report["groups"]:
    assert group["before"] == {key: before[key] for key in group["members"]}
    assert group["english"] == {key: en[key] for key in group["members"]}
    assert group["arabic"] == {key: ar[key]["text"] for key in group["members"]}
    assert "".join(part["text"] for part in group["parts"]) == group["shared_expression"]
    assert all(part["role"] in [*group["members"], "context"] for part in group["parts"])
    for key in group["members"]:
        assert key not in updates
        value = group["after"][key]
        assert value == after[key] != before[key]
        assert value.replace("(", "").replace(")", "") == group["shared_expression"]
        # Independently recover each source's foreground runs from the display.
        level = 0
        visible = []
        for char in value:
            if char == "(": level += 1
            elif char == ")": level -= 1
            elif level == 0: visible.append(char)
            assert level in (0, 1), key
        expected = "".join(part["text"] for part in group["parts"] if part["role"] == key)
        assert "".join("".join(visible).split()) == "".join(expected.split()), key
        updates[key] = value
assert after == before | updates
assert len(updates) == report["summary"]["changed_values"] == 20
assert len(report["groups"]) == report["summary"]["groups"] == 9
assert {key.rsplit(":", 1)[0] for key in updates} == {"30:43", "39:74", "2:16", "2:17"}
for ayah, records in report["original_contexts"].items():
    expected = sorted((key for key in ar if key.rsplit(":", 1)[0] == ayah), key=lambda key: int(key.split(":")[2]))
    assert [record["location"] for record in records] == expected
    for record in records:
        key = record["location"]
        assert record["arabic"] == ar[key]["text"]
        assert record["english"] == en.get(key)
        assert record["turkish_before"] == before.get(key)
markers = {key: value for key, value in en.items() if re.fullmatch(r"\(\d+\)", value)}
assert len(markers) == 6236 and all(after[key] == value for key, value in markers.items())
for key, value in after.items():
    stack = []
    for char in value:
        if char in "([": stack.append(char)
        elif char in ")]": assert stack and stack.pop() == {")": "(", "]": "["}[char], key
    assert not stack, key
queue = read_report("linguistic-review-current.json")
old_queue = json.loads(subprocess.check_output(["git", "show", report["baseline"]+":reports/linguistic-review-current.json"], cwd=ROOT))
resolved = {key for decision in report["decisions"] for key in decision.get("resolved_semantic_keys", [])}
assert len(queue) == len(old_queue) == 831
assert [entry["key"] for entry in queue] == [entry["key"] for entry in old_queue]
for old, current in zip(old_queue, queue):
    key = current["key"]
    assert current["turkish"] == after[key]
    if key in resolved:
        assert current["status"] == "reviewed_with_changes"
        assert current["history"][:-1] == old["history"]
        assert current["history"][-1]["manifest"] == "semantic-review-001.json"
        assert current["currently_context_only"] is False
    else:
        expected = dict(old)
        expected["turkish"] = after[key]
        assert current == expected, key
assert read_report("grammar-construction-review.json") == []
assert {key for decision in report["decisions"] for key in decision.get("resolved_construction_keys", [])} == {"30:43:12", "39:74:10"}
for key, value in {
    "2:5:4": "(Rableri)nden", "2:5:5": "Rableri(nden)",
    "30:43:12": "onun (geri çevrilmesi yoktur)",
    "30:43:13": "(Allah)'tan", "30:43:14": "Allah('tan)",
    "39:74:9": "yerleşebiliriz", "39:74:10": "(cennet)in (dilediğimiz yerinde)",
    "2:16:2": "(satın al)anlardır", "2:16:10": "(ve doğru yolu bulmuş değil)lerdi",
    "2:17:8": "(çevresinde)kileri", "2:17:16": "(gör)mez(ler)",
}.items():
    assert after[key] == value, key
assert all(after[key] == before[key] for key in after if key.startswith(("2:23:", "2:36:")))
raw = (ROOT / "turkish-wbw-translation.json").read_bytes()
assert raw == (json.dumps(after, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
assert hashlib.sha256(before_raw).hexdigest() == report["summary"]["turkish_before_sha256"]
assert hashlib.sha256(raw).hexdigest() == report["summary"]["turkish_after_sha256"]
result = {"changed_values": len(updates), "revised_ayahs": 4, "groups": 9,
          "exact_scope_and_untouched_values": "passed", "arabic_and_english_provenance": "passed",
          "foreground_source_roles": "passed", "reference_order_and_83665_keys": "passed",
          "ayah_markers_preserved": 6236, "resource_hashes_unchanged": True,
          "english_unchanged_from_initial": True, "current_queue_records": len(queue),
          "pending_semantic_flags": sum(entry["status"] == "requires_semantic_review" for entry in queue),
          "resolved_construction_flags": 2, "remaining_construction_flags": 0,
          "turkish_sha256": hashlib.sha256(raw).hexdigest(),
          "scope": "Verifies this recorded batch; not exhaustive certification of the revised ayahs or the whole translation."}
write_report("semantic-review-001-validation.json", result)
print(json.dumps(result, indent=2))
