"""Continue contextual alignment from 033d895 without changing lexical wording.

This batch expands temporal/quantifier groups across an intervening missing key.
Previously aligned clauses are reconstructed from their recorded roles, never
by interpreting arbitrary parentheses in the translation as morphology.
"""
import hashlib
import json
import re
import subprocess
from copy import deepcopy

from alignment_common import ROOT, render

BASE = "033d895"
def committed(name):
    return subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)

reference = committed("english-wbw-translation.json")
assert (ROOT / "english-wbw-translation.json").read_bytes() == reference
en = json.loads(reference)
before_bytes = committed("turkish-wbw-translation.json")
tr = json.loads(before_bytes)
old = json.loads(committed("reports/contextual-alignment-changes.json"))
lookup = {k: g for g in old["groups"] for k in g["members"]}
groups, used = [], set()

def key_at(key, offset):
    s, a, w = key.split(":")
    return f"{s}:{a}:{int(w) + offset}"

def normalized(value):
    return re.sub(r"[\[\]()]", "", value).strip().lower()

def split_case(text):
    match = re.search(r"(?:den|dan|ten|tan)$", text)
    if not match:
        return None
    start = match.start()
    if text == "ondan":
        return 1
    # Third-person possessive connector n belongs with the case ending.
    if text[:start].endswith(("inden", "ından")):
        return None
    if text[:start].endswith(("in", "ın", "un", "ün")) and text[:start] not in {"din", "gün"}:
        start -= 1
    if start and text[start - 1] == "'":
        start -= 1
    return start

def add(members, parts, origins, expression, reason, category):
    assert not used.intersection(members), members
    assert any(k not in tr for k in members)
    assert "".join(p["text"] for p in parts) == expression
    for k in members:
        assert k in en and any(p["role"] == k and p["text"].strip() for p in parts)
    group = {"members": members, "before": {k: tr.get(k) for k in members},
             "english": {k: en[k] for k in members}, "parts": parts,
             "expression_origins": origins, "shared_expression": expression,
             "reason": reason, "category": category,
             "after": {k: render(parts, k) for k in members}}
    assert all(v.replace("(", "").replace(")", "") == expression for v in group["after"].values())
    groups.append(group)
    used.update(members)

for missing in sorted(en.keys() - tr.keys(), key=lambda k: tuple(map(int, k.split(":")))):
    previous, following = key_at(missing, -1), key_at(missing, 1)
    if previous not in tr or following not in tr:
        continue
    gloss, prev_gloss = normalized(en[missing]), normalized(en[previous])
    temporal = gloss in {"before", "after"} and prev_gloss in {"from", "even from", gloss}
    quantifier = gloss == "every" and prev_gloss in {"from", "of", "in", "at"}
    if not temporal and not quantifier:
        continue
    head = tr[previous]
    if temporal and head not in {"sonra", "sonra da", "sonradır", "önce"}:
        continue
    if quantifier and head != "her":
        continue
    prior = lookup.get(following)
    if prior:
        if not temporal or prior["category"] != "clause_link" or len(prior["members"]) != 2:
            continue
        expression = prior["shared_expression"]
        parts = deepcopy(prior["parts"])
        members = [previous, missing] + prior["members"]
        origins = [{"kind": "previous_manifest_group", "members": prior["members"], "expression": expression}]
    else:
        expression = tr[following]
        if normalized(en[following]) in {"that", "what"}:
            continue  # Do not assign an entire predicate to a subordinator.
        if any(c in expression for c in "()[]"):
            continue
        parts = [{"text": expression, "role": following}]
        members = [previous, missing, following]
        origins = [{"kind": "baseline_value", "key": following, "expression": expression}]
    boundary = split_case(expression)
    if boundary is None:
        continue
    if quantifier and prev_gloss in {"in", "at"}:
        continue  # Locative quantifiers are reviewed separately below.
    # Preserve every role in the old clause except the outer ablative ending.
    changed, position = [], 0
    for part in parts:
        end = position + len(part["text"])
        if end <= boundary:
            changed.append(part)
        elif position >= boundary:
            changed.append({"text": part["text"], "role": previous})
        else:
            changed.extend([{"text": part["text"][:boundary-position], "role": part["role"]},
                            {"text": part["text"][boundary-position:], "role": previous}])
        position = end
    changed.extend([{"text": " ", "role": "context"}, {"text": head, "role": missing}])
    if quantifier:
        changed = [{"text": head, "role": missing}, {"text": " ", "role": "context"}] + changed[:-2]
        shared = head + " " + expression
        origins.insert(0, {"kind": "baseline_value", "key": previous, "expression": head})
    else:
        shared = expression + " " + head
        origins.append({"kind": "baseline_value", "key": previous, "expression": head})
    add(members, changed, origins, shared,
        "The outer ablative ending supplies the first source relation; the postposition or quantifier was stored at that relation's key. Retain any established inner clause roles.",
        "temporal_expansion" if temporal else "quantifier_expansion")

# Explicit locally inspected locative quantifier expressions.
for first, noun, root, ending in [
    ("7:29:7", "mescidde", "mescid", "de"),
    ("8:56:7", "defasında", "defası", "nda"),
    ("26:225:4", "vadide", "vadi", "de"),
]:
    middle, last = key_at(first, 1), key_at(first, 2)
    assert tr[first] == "her" and tr[last] == noun and root + ending == noun
    add([first, middle, last], [{"text": "her", "role": middle}, {"text": " ", "role": "context"},
        {"text": root, "role": last}, {"text": ending, "role": first}],
        [{"kind": "baseline_value", "key": first, "expression": "her"},
         {"kind": "baseline_value", "key": last, "expression": noun}], "her " + noun,
        "Expose the locative ending, quantifier, and noun in their existing Turkish order.", "locative_quantifier")

for first in ["3:28:25", "5:48:43", "5:105:12", "11:4:1"]:
    last = key_at(first, 1)
    raw = tr[first]
    prefix = "ve " if raw.startswith("ve ") else ""
    assert raw == prefix + "Allah'adır" and en[last] == "Allah"
    parts = ([{"text": prefix, "role": first}] if prefix else []) + [
        {"text": "Allah", "role": last}, {"text": "'a", "role": first}, {"text": "dır", "role": "context"}]
    add([first, last], parts, [{"kind": "baseline_value", "key": first, "expression": raw}], raw,
        "Separate the overt dative from the divine name; the copular ending remains shared context rather than being labeled as the preposition.", "proper_name_dative")

first, last = "12:66:8", "12:66:9"
assert tr[first] == "Allah adına"
add([first, last], [{"text": "Allah", "role": last}, {"text": " ", "role": "context"},
    {"text": "adına", "role": first}], [{"kind": "baseline_value", "key": first, "expression": tr[first]}], tr[first],
    "The existing oath expression has a separate postposition; expose it without inventing a case ending.", "oath_expression")

updates = {k: v for g in groups for k, v in g["after"].items()}
for group in groups:
    assert " ".join(o["expression"] for o in group["expression_origins"]) == group["shared_expression"]
expected = tr | updates
expected = {k: expected[k] for k in en if k in expected}
path = ROOT / "turkish-wbw-translation.json"
current = json.loads(path.read_bytes())
assert current == tr or current == expected, "Unexpected edits; refusing overwrite."
assert all(expected[k] == v for k, v in tr.items() if k not in updates)
assert all(expected[k] == v for k, v in tr.items() if re.fullmatch(r"\(\d+\)", en[k]))
output = (json.dumps(expected, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
summary = {"baseline_commit": BASE, "added_keys": len(expected) - len(tr),
           "modified_existing_keys": sum(k in tr and tr[k] != v for k, v in updates.items()),
           "groups": len(groups), "remaining_missing_keys": len(en.keys() - expected.keys()),
           "english_sha256": hashlib.sha256(reference).hexdigest(),
           "turkish_before_sha256": hashlib.sha256(before_bytes).hexdigest(),
           "turkish_after_sha256": hashlib.sha256(output).hexdigest()}
path.write_bytes(output)
assert (ROOT / "english-wbw-translation.json").read_bytes() == reference
(ROOT / "reports/continued-alignment-changes.json").write_text(json.dumps({"summary": summary, "groups": groups}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
pending = json.loads(committed("reports/alignment-pending.json"))
pending = [r for r in pending if r["key"] not in expected]
for row in pending:
    row["previous_turkish"] = expected.get(row["previous_key"])
    row["context_baseline"] = "Current Turkish file after the continued-alignment batch"
assert {r["key"] for r in pending} == en.keys() - expected.keys()
(ROOT / "reports/alignment-pending.json").write_text(json.dumps(pending, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assert updates["2:109:9"] == "(imanınızdan) sonra"
assert updates["2:109:8"] == "(imanınız)dan (sonra)"
assert "3:89:6" not in updates  # Joint subordinator interpretation deferred.
assert "58:3:12" not in updates  # A missing predicate still needs joint review.
print(json.dumps(summary, indent=2))
