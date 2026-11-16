"""Assemble reviewed boundaries and a complete pending-key inventory."""
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter

from alignment_common import ROOT, BASELINE, load_baseline, render

en, tr = load_baseline()
OUT = ROOT / "reports"
numeric = lambda k: tuple(map(int, k.split(":")))
groups = json.loads((OUT / "complex-alignment-plan.json").read_text(encoding="utf-8"))
used = set()
for group in groups:
    assert not used.intersection(group["members"]), group["members"]
    used.update(group["members"])
    group["category"] = "complex_alignment"

files = ["negation-alignment-plan.json", "clause-alignment-plan.json", "case-supplement-plan.json"]
case_plan = json.loads((OUT / "suffix-alignment-plan.json").read_text(encoding="utf-8"))
rows = case_plan["operations"][:]
deferred = case_plan["deferred_preposition_candidates"][:]
for name in files:
    candidates = json.loads((OUT / name).read_text(encoding="utf-8"))
    rows.extend(r for r in candidates if r["status"] == "proposed")
    deferred.extend(r for r in candidates if r["status"] != "proposed")

semantic_exclusions = {
    "2:48:4": "The existing 'cezalandırılmaz' wording needs a lexical/voice review against 'avail' before treating the missing meaning as already translated.",
}
buckets = {}
for row in rows:
    pair = (row["relation_key"], row["content_key"])
    if row["content_key"] in semantic_exclusions or used.intersection(pair):
        continue
    assert row["content_key"] not in tr and tr[row["relation_key"]] == row["original_turkish"]
    surface = row["original_turkish"].replace("(", "[").replace(")", "]")
    assert "".join(p["text"] for p in row["parts"]) == surface, pair
    bucket = buckets.setdefault(pair, {"surface": surface, "roles": ["content"] * len(surface), "categories": set()})
    index = 0
    for part in row["parts"]:
        for position in range(index, index + len(part["text"])):
            if part["role"] == "relation" or (part["role"] == "context" and bucket["roles"][position] != "relation"):
                bucket["roles"][position] = part["role"]
        index += len(part["text"])
    bucket["categories"].add(row["case"])

for pair, bucket in sorted(buckets.items(), key=lambda item: numeric(item[0][0])):
    assert not used.intersection(pair), pair
    parts = []
    for char, role in zip(bucket["surface"], bucket["roles"]):
        role = {"relation": pair[0], "content": pair[1], "context": "context"}[role]
        if parts and parts[-1]["role"] == role:
            parts[-1]["text"] += char
        else:
            parts.append({"text": char, "role": role})
    groups.append({"members": list(pair), "expression_origins": [pair[0]], "parts": parts,
                   "category": "+".join(sorted(bucket["categories"])),
                   "reason": "Expose reviewed grammatical material and its lexical counterpart in complementary views of the existing Turkish expression.",
                   "status": "reviewed_local_alignment"})
    used.update(pair)

updates = {}
for group in groups:
    expression = "".join(p["text"] for p in group["parts"])
    group["shared_expression"] = expression
    group["before"] = {k: tr.get(k) for k in group["members"]}
    group["english"] = {k: en[k] for k in group["members"]}
    group["after"] = {}
    origin_expression = " ".join(tr[k].replace("(", "[").replace(")", "]") for k in group["expression_origins"])
    assert origin_expression == expression, group["members"]
    for key in group["members"]:
        assert key not in updates
        assert any(p["role"] == key and p["text"].strip() for p in group["parts"]), key
        value = render(group["parts"], key)
        assert value.replace("(", "").replace(")", "") == expression
        assert value.count("(") == value.count(")") and value.count("[") == value.count("]"), key
        group["after"][key] = value
        updates[key] = value

remaining = sorted(en.keys() - tr.keys() - updates.keys(), key=numeric)
reasons = {}
for row in deferred:
    key = row.get("content_key", row.get("missing_key"))
    if key in remaining:
        reasons.setdefault(key, []).append(row["reason"])
pending = []
for key in remaining:
    s, a, w = key.split(":")
    previous = f"{s}:{a}:{int(w) - 1}"
    reason = semantic_exclusions.get(key)
    pending.append({"key": key, "english": en[key], "previous_key": previous,
                    "previous_english": en.get(previous), "previous_turkish": tr.get(previous),
                    "status": "requires_individual_review",
                    "reasons": [reason] if reason else list(dict.fromkeys(reasons.get(key, [
                        "No reviewed shared-expression mapping has been established. Check zero equivalents, phrase boundaries, source positions, spelling, and omitted meanings in ayah context."
                    ])))})

reference_bytes = (ROOT / "english-wbw-translation.json").read_bytes()
baseline_bytes = subprocess.check_output(["git", "show", f"{BASELINE}:turkish-wbw-translation.json"], cwd=ROOT)
summary = {"baseline_commit": BASELINE, "english_sha256": hashlib.sha256(reference_bytes).hexdigest(),
           "turkish_before_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
           "baseline_missing_word_keys": len(en.keys() - tr.keys()),
           "added_keys": len(updates.keys() - tr.keys()),
           "modified_existing_keys": sum(k in tr and tr[k] != v for k, v in updates.items()),
           "remaining_missing_keys": len(remaining), "shared_expression_groups": len(groups),
           "groups_by_category": dict(Counter(g["category"] for g in groups)),
           "review_scope": "Local English/Turkish structural and linguistic alignment; selected Arabic/source checks are documented. This is not a certification of every inherited translation or an exhaustive semantic classification of unresolved gaps."}
manifest = {"summary": summary, "groups": groups}
(OUT / "contextual-alignment-changes.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "alignment-pending.json").write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
buffer = io.StringIO(newline="")
writer = csv.writer(buffer, lineterminator="\n")
writer.writerow(["key", "operation", "english", "before", "after", "group", "category", "reason"])
for number, group in enumerate(groups, 1):
    for key in group["members"]:
        writer.writerow([key, "modify" if key in tr else "add", en[key], tr.get(key, ""), group["after"][key], number, group["category"], group["reason"]])
(OUT / "contextual-alignment-changes.csv").write_text(buffer.getvalue(), encoding="utf-8")
print(json.dumps(summary, indent=2))
