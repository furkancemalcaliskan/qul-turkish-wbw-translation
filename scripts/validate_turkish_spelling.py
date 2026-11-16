"""Independently reconstruct and verify the spelling-review edit scope."""
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate key: {key}"
        result[key] = value
    return result

def read(name):
    return json.loads((ROOT / name).read_bytes(), object_pairs_hook=unique)

def surface(value):
    return " ".join(value.replace("(", "").replace(")", "").split())

report = read("reports/spelling-changes.json")
before_bytes = subprocess.check_output(["git", "show", report["baseline"]+":turkish-wbw-translation.json"], cwd=ROOT)
before = json.loads(before_bytes, object_pairs_hook=unique)
english_bytes = (ROOT / "english-wbw-translation.json").read_bytes()
assert english_bytes == subprocess.check_output(["git", "show", "4503cdc:english-wbw-translation.json"], cwd=ROOT)
en = read("english-wbw-translation.json")
after = read("turkish-wbw-translation.json")
expected = dict(before)
changed = set()
alignment_keys = {"79:40:8", "79:40:9", "46:8:10", "46:8:11"}
construction_keys = set()
for group in report["construction_groups"]:
    assert group["before"] == {key: before[key] for key in group["members"]}
    assert not construction_keys.intersection(group["members"])
    construction_keys.update(group["members"])
    if "parts" in group:
        phrase = "".join(part["text"] for part in group["parts"])
        assert all(part["role"] in [*group["members"], "context"] for part in group["parts"])
        assert all(group["after"][key].replace("(", "").replace(")", "") == phrase for key in group["members"])
    for key, value in group["after"].items():
        assert after[key] == value
for entry in report["entries"]:
    key = entry["key"]
    assert key not in changed
    changed.add(key)
    assert entry["before"] == before[key]
    assert entry["after"] != before[key]
    assert entry["english"] == en[key]
    assert entry["changes"]
    if key not in alignment_keys and key not in construction_keys:
        assert re.sub(r"[^()\[\]]", "", entry["before"]) == re.sub(r"[^()\[\]]", "", entry["after"]), key
    elif key in alignment_keys:
        assert any(item.get("category") == "alignment_repair" for item in entry["changes"])
    else:
        assert any(item.get("category") == "construction_repair" for item in entry["changes"])
    expected[key] = entry["after"]
assert after == expected
assert list(after) == list(before) == list(en)
assert len(after) == 83665
assert len(changed) == report["summary"]["changed_entries"]
assert report["summary"]["added_keys"] == report["summary"]["removed_keys"] == 0
assert all(isinstance(value, str) and value.strip() == value and value for value in after.values())
assert not any("  " in value or "\ufffd" in value for value in after.values())
markers = {key: value for key, value in en.items() if re.fullmatch(r"\(\d+\)", value)}
assert len(markers) == 6236
assert all(after[key] == value for key, value in markers.items())
assert not any(re.fullmatch(r"\d+", value) for value in after.values())
for key, value in after.items():
    stack = []
    for char in value:
        if char in "([":
            stack.append(char)
        elif char in ")]":
            assert stack and stack.pop() == {")": "(", "]": "["}[char], key
    assert not stack, key
groups = collections.defaultdict(list)
for key, value in before.items():
    groups[(key.rsplit(":", 1)[0], surface(value))].append(key)
for keys in groups.values():
    if set(keys) == {"2:112:12", "2:112:15"}:
        # Identical inherited strings describe separate clauses: existential fear
        # versus a finite grief predicate. They are not complementary views.
        assert after["2:112:12"] == before["2:112:12"] == "ve yoktur"
        assert after["2:112:15"] == "ve (onlar üzül)mez(ler)"
        continue
    if set(keys) == {"2:112:14", "2:112:16"}:
        # A prepositional complement in the fear clause is distinct from hum,
        # the nominative subject of the grief predicate.
        assert after["2:112:14"] == before["2:112:14"] == "onlara"
        assert after["2:112:16"] == "(ve) onlar (üzülmezler)"
        continue
    assert len({surface(after[key]) for key in keys}) == 1, keys
for key, value in {
    "2:5:4": "(Rableri)nden", "2:5:5": "Rableri(nden)",
    "14:34:2": "(her şey)den", "14:34:3": "her şey(den)",
    "55:11:2": "meyve(ler)", "7:22:5": "ağac(ın meyvesin)i",
    "7:29:7": "(her mescit)te", "7:29:9": "(her) mescit(te)",
    "17:15:2": "hidayeti seçerse", "4:5:3": "aklı ermezlere",
    "6:92:15": "inanan(lar)", "31:18:2": "çevirme",
    "30:28:6": "(sizin için var) mıdır(?)", "24:50:1": "kalplerinde mi var?",
    "79:40:8": "(kötü hevesler)den", "79:40:9": "kötü hevesler(den)",
    "46:8:10": "(Allah)'tan", "46:8:11": "Allah('tan)",
    "9:1:2": "(Allah)'tan", "9:1:3": "Allah('tan)",
    "12:4:7": "(rü'yada) gördüm", "18:64:9": "ta'kibederek",
    "97:3:4": "(bin ay)dan", "97:3:6": "(bin) ay(dan)",
    "21:75:6": "salihler(den idi)", "21:76:1": "ve Nuh'u da",
    "80:18:3": "(hangi) şey(den)", "16:99:3": "onun [şeytanın]",
    "2:112:15": "ve (onlar üzül)mez(ler)", "2:112:16": "(ve) onlar (üzülmezler)",
    "2:112:17": "(ve onlar) üzül(mez)ler", "79:24:3": "sizin Rabbinizim",
    "23:52:7": "sizin Rabbinizim", "23:108:2": "sinin",
    "3:121:10": "işitendir", "3:121:11": "bilendir",
    "22:9:11": "ve ona tattıracağız", "39:26:1": "onlara tattırdı",
    "44:49:1": "tat", "38:21:2": "sana geldi (mi)?",
}.items():
    assert after[key] == value, (key, after[key], value)
raw = (ROOT / "turkish-wbw-translation.json").read_bytes()
assert raw == (json.dumps(after, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
for raw_value, label in [(before_bytes, "turkish_before_sha256"), (raw, "turkish_after_sha256"), (english_bytes, "english_sha256")]:
    assert hashlib.sha256(raw_value).hexdigest() == report["summary"][label]
semantic_review = read("reports/linguistic-review-current.json")
assert len(semantic_review) == 831
assert all(entry["turkish"] == after[entry["key"]] for entry in semantic_review)
construction_review = read("reports/grammar-construction-review.json")
assert {entry["key"] for entry in construction_review} == {"30:43:12", "39:74:10"}
assert all(entry["turkish"] == after[entry["key"]] == before[entry["key"]] for entry in construction_review)
snapshot = read("reports/spelling-second-pass-start.json")
first_pass = before | snapshot["first_pass_changes"]
assert hashlib.sha256((json.dumps(first_pass, ensure_ascii=False, indent=2)+"\n").encode("utf-8")).hexdigest() == snapshot["turkish_sha256"]
second_pass = read("reports/spelling-second-pass-changes.json")
second_updates = {}
for entry in second_pass["entries"]:
    key = entry["key"]
    assert key not in second_updates and first_pass[key] == entry["before"]
    assert entry["after"] == after[key] != entry["before"]
    assert entry["english"] == en[key]
    second_updates[key] = entry["after"]
assert after == first_pass | second_updates
assert len(second_updates) == second_pass["summary"]["changed_entries_this_pass"]
assert second_pass["summary"]["turkish_before_sha256"] == snapshot["turkish_sha256"]
assert second_pass["summary"]["turkish_after_sha256"] == hashlib.sha256(raw).hexdigest()
result = {
    "changed_entries": len(changed), "alignment_repair_entries": len(alignment_keys),
    "construction_repair_entries": len(construction_keys),
    "entries_per_translation": len(after), "missing_extra_duplicate_keys": 0,
    "ayah_numbers_preserved": len(markers), "english_unchanged_from_initial": True,
    "exact_reference_order": True, "manifest_reconstruction": "passed",
    "untouched_values_preserved": True, "paired_surfaces_consistent": True,
    "independent_identical_before_strings": [["2:112:12", "2:112:15"], ["2:112:14", "2:112:16"]],
    "delimiters_and_formatting": "passed", "representative_regressions": "passed",
    "bare_numeric_placeholders": 0, "turkish_sha256": hashlib.sha256(raw).hexdigest(),
    "open_construction_flags": len(construction_review), "existing_semantic_review_flags": len(semantic_review),
    "second_pass_changed_entries": len(second_updates), "second_pass_reconstruction": "passed",
    "scope": "Structural verification of recorded spelling and grammar corrections; not exhaustive linguistic certification.",
}
(ROOT / "reports/spelling-validation.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2))
