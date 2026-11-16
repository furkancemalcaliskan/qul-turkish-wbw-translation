"""Prepare explicit shared-expression groups for more than two source words."""
import json
import re

from alignment_common import ROOT, load_baseline, lower

en, tr = load_baseline()
groups = []
normalize = lambda value: re.sub(r"^(?:is|are|was|were|will be) ", "", re.sub(r"[\[\]()]", "", value).lower().strip())

def next_key(key, offset=1):
    s, a, w = key.split(":")
    return f"{s}:{a}:{int(w) + offset}"

def add(keys, origins, parts, reason, expected=None):
    expression = "".join(p["text"] for p in parts)
    if expected is not None:
        assert expression == expected, (keys, expression, expected)
    assert any(k not in tr for k in keys)
    assert all(any(p["role"] == k and p["text"].strip() for p in parts) for k in keys)
    groups.append({"members": keys, "expression_origins": origins, "parts": parts,
                   "reason": reason, "status": "reviewed_local_alignment"})

def segmented(keys, origin, spans, reason):
    text = tr[origin].replace("(", "[").replace(")", "]")
    roles = [keys[-1]] * len(text)
    for key, start, end in spans:
        roles[start:end] = [key] * (end - start)
    parts = []
    for char, role in zip(text, roles):
        if parts and parts[-1]["role"] == role:
            parts[-1]["text"] += char
        else:
            parts.append({"text": char, "role": role})
    add(keys, [origin], parts, reason, text)

# Repeated English glosses do not necessarily distinguish separate Arabic
# function words. Apply these only to an existing, visible ablative ending.
for key in sorted(en, key=lambda k: tuple(map(int, k.split(":")))):
    second, third = next_key(key), next_key(key, 2)
    if key not in tr or second not in en or second in tr:
        continue
    raw = tr[key]
    first_gloss, second_gloss = normalize(en[key]), normalize(en[second])
    if first_gloss.startswith(("before", "after", "besides")) and first_gloss == second_gloss:
        match = re.search(r"(?:nden|ndan|den|dan|ten|tan)(?=\s+(?:önce|sonra|başka|ayrı)|$)", raw)
        if match:
            start = match.start()
            if raw[:start].endswith("'"):
                start -= 1
            base = raw[:start]
            if lower(base) in {"be", "se"} and raw[start] == "n":
                start += 1
            segmented([key, second], key, [(key, start, match.end())],
                      "Repeated temporal/besides glosses: expose the overt ablative ending while preserving the complete existing phrase.")
    # Three-word min / dun / noun constructions with the case ending already
    # attached to the noun at the third key.
    if third in tr and "besides" in second_gloss and (first_gloss == "from" or "besides" in first_gloss):
        if raw in {"başka", "başkasına", "başkasını", "başkası", "ayrı", "ayrı olarak"}:
            noun = tr[third].replace("(", "[").replace(")", "]")
            match = re.search(r"(?:nden|ndan|den|dan|ten|tan)$", noun)
            if match:
                boundary = match.start()
                if boundary and noun[boundary - 1] == "'":
                    boundary -= 1
                add([key, second, third], [third, key], [
                    {"text": noun[:boundary], "role": third}, {"text": noun[boundary:], "role": key},
                    {"text": " ", "role": "context"}, {"text": raw, "role": second},
                ], "The ablative ending is stored on the later noun; share the full noun + case + postposition expression.", noun + " " + raw)
    # kull / shay expressions: preserve the actual existing case form.
    if third in en and second_gloss == "every" and normalize(en[third]) == "thing":
        expression = raw
        origins = [key]
        if raw == "her" and third in tr:
            expression = raw + " " + tr[third]
            origins = [key, third]
        if re.fullmatch(r"her ?şey[aeiı]", expression) and (third not in tr or tr[third] in expression):
            her_end = 3
            noun_start = expression.index("şey")
            noun_end = noun_start + 3
            add([key, second, third], origins, [
                {"text": expression[:her_end], "role": second},
                {"text": expression[her_end:noun_start], "role": "context"},
                {"text": "şey", "role": third}, {"text": expression[noun_end:], "role": key},
            ], "Separate the quantifier, noun, and case ending of the existing 'her şey' expression.", expression)

# Explicitly reviewed three-entry constructions. Each boundary is recorded as
# a concrete span in the unchanged original Turkish expression.
for origin, kind in {
    "3:165:12": "copula_case",
    "14:12:11": "case_clause", "15:88:4": "case_clause", "17:73:4": "case_clause", "24:43:31": "case_clause",
    "17:99:10": "case_infinitive", "23:95:2": "case_infinitive", "36:81:7": "case_infinitive",
    "46:33:13": "case_infinitive", "70:41:1": "case_infinitive", "75:4:3": "case_infinitive", "75:40:4": "case_infinitive", "79:18:4": "case_infinitive",
    "19:43:7": "relative_negative", "42:21:8": "relative_negative", "60:12:8": "relative_negative", "90:5:2": "relative_negative", "90:7:2": "relative_negative",
    "17:111:4": "relative_negative",
}.items():
    keys = [origin, next_key(origin), next_key(origin, 2)]
    assert origin in tr and all(k not in tr for k in keys[1:])
    text = tr[origin]
    spans = []
    if kind == "copula_case":
        spans = [(keys[0], len(text) - 3, len(text)), (keys[1], len(text) - 6, len(text) - 3)]
    elif kind in {"case_clause", "case_infinitive"}:
        case = re.search(r"(?:nden|ndan|den|dan|ten|tan|ye|ya|ne|na|yı|yi|a|e)(?=\s+da$|$)", text)
        assert case
        marker = re.search(r"[dt][ıiuü][kğ]|[ae]c[ae][kğ]", text) if kind == "case_clause" else re.search(r"m[ae][kğ]?", text)
        assert marker
        spans = [(keys[0], case.start(), case.end()), (keys[1], marker.start(), marker.end())]
    else:
        negative = re.search(r"m[ae](?=[dt][ıiuü]|y[ae]n|m[ae]|y[ae]c)", text)
        assert negative, origin
        if origin == "17:111:4":
            clause = re.search(r"y[ae]n$", text)
        elif origin == "19:43:7":
            clause = re.search(r"y[ae]n$", text)
        elif origin == "60:12:8":
            clause = re.search(r"m[ae](?=ları$)", text)
        else:
            clause = re.search(r"[dt][ıiuü][kğ]|y[ae]c[ae][kğ]", text)
        assert clause, origin
        spans = [(keys[0], clause.start(), clause.end()), (keys[1], negative.start(), negative.end())]
    segmented(keys, origin, spans, f"Reviewed three-entry {kind} construction; retain original wording and separate its grammatical contributions.")

# One lexical compound in which the adjective precedes the Turkish noun.
segmented(["50:16:12", "50:16:13", "50:16:14"], "50:16:12", [
    ("50:16:12", len("şah damarı"), len("şah damarından")),
    ("50:16:13", len("şah "), len("şah damarı")),
], "The existing 'şah damarı' compound corresponds to jugular + vein, with the comparative ending aligned separately.")

# Correct the two swapped phrase positions in 4:23 before adding the missing
# partners. Keep the inherited wording; its lexical quality is a separate task.
add(["4:23:22", "4:23:23"], ["4:23:26"], [
    {"text": "evleriniz", "role": "4:23:23"}, {"text": "de", "role": "4:23:22"},
    {"text": " bulunan", "role": "context"},
], "Move the existing guardianship phrase from 4:23:26 to its correct source range (4:23:22–23).", tr["4:23:26"])
add(["4:23:26", "4:23:27"], ["4:23:22"], [
    {"text": "birleş", "role": "4:23:27"}, {"text": "tiğ", "role": "4:23:26"},
    {"text": "iniz", "role": "4:23:27"},
], "Move the existing relations phrase from 4:23:22 to its correct source range (4:23:26–27).", tr["4:23:22"])

(ROOT / "reports/complex-alignment-plan.json").write_text(json.dumps(groups, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Complex groups:", len(groups), "Missing members:", sum(k not in tr for g in groups for k in g["members"]))
