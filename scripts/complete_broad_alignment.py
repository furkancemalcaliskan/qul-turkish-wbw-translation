"""Prepare/apply a broader, auditable continuation with explicit zero surfaces.

Run without arguments to inspect the manifest before applying it with --apply.
An entirely parenthesized value explicitly has no independent overt Turkish
surface contribution in this expression; it is not a newly invented suffix.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter, defaultdict

from alignment_common import ROOT, flat_surface, map_span, render, lower

APPLY = argparse.ArgumentParser()
APPLY.add_argument("--apply", action="store_true")
args = APPLY.parse_args()
read = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
committed = lambda name: subprocess.check_output(["git", "show", f"033d895:{name}"], cwd=ROOT)
en_bytes = (ROOT / "english-wbw-translation.json").read_bytes()
assert en_bytes == committed("english-wbw-translation.json")
en = json.loads(en_bytes)
tr = json.loads(committed("turkish-wbw-translation.json"))
continuation = read("reports/continued-alignment-changes.json")
for group in continuation["groups"]:
    assert group["before"] == {k: tr.get(k) for k in group["members"]}
    tr.update(group["after"])
tr = {k: tr[k] for k in en if k in tr}
baseline_bytes = (json.dumps(tr, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
assert hashlib.sha256(baseline_bytes).hexdigest() == continuation["summary"]["turkish_after_sha256"]
original = json.loads(subprocess.check_output(["git", "show", "cf1e80d:turkish-wbw-translation.json"], cwd=ROOT))
historical = read("reports/contextual-alignment-changes.json")["groups"]
previously_aligned = {k for g in historical + continuation["groups"] for k in g["members"]}
groups, used, exclusions = [], set(), []
numeric = lambda k: tuple(map(int, k.split(":")))

def adjacent(key, n):
    s, a, w = key.split(":")
    return f"{s}:{a}:{int(w)+n}"

def norm(value):
    return re.sub(r"\s+", " ", re.sub(r"[\[\]()]", "", value).lower()).strip(" .,;!?:")

def gloss(value):
    value = norm(value)
    value = re.sub(r"^(?:and |the |a |an )", "", value)
    return value

lexicon = defaultdict(set)
for key, value in original.items():
    if "(" not in value and "[" not in value:
        lexicon[gloss(en[key])].add(lower(value).strip(" .;,!?"))

def parts_from_spans(text, key, lexical, spans):
    roles = [lexical] * len(text)
    for start, end in spans:
        roles[start:end] = [key] * (end-start)
    parts = []
    for char, role in zip(text, roles):
        if parts and parts[-1]["role"] == role:
            parts[-1]["text"] += char
        else:
            parts.append({"text": char, "role": role})
    return parts

def add(members, parts, reason, category, origins=None, revised=False):
    assert not used.intersection(members), members
    assert any(k not in tr for k in members)
    expression = "".join(p["text"] for p in parts)
    assert expression.strip()
    zero = [k for k in members if not any(p["role"] == k and p["text"].strip() for p in parts)]
    groups.append({"members": members, "english": {k: en[k] for k in members},
                   "before": {k: tr.get(k) for k in members}, "parts": parts,
                   "shared_expression": expression, "after": {k: render(parts, k) for k in members},
                   "zero_surface_keys": zero, "reason": reason, "category": category,
                   "lexical_revision": revised, "expression_origins": members[:1] if origins is None else origins})
    used.update(members)

prepositions = {
    "of", "from", "in", "to", "on", "for", "with", "towards", "against", "about", "by", "over",
    "among", "during", "out of", "concerning", "through", "at", "within", "upon", "into", "throughout",
    "in to", "because of", "as", "until", "till", "from among", "from among those", "from among them",
    "in comparison to", "added to", "according to", "on him", "is in", "will be in", "is of", "is to",
    "was of", "were of", "was surely of", "will be from", "be surely among", "is on", "were from",
    "of to", "from near", "is with", "will be among", "he will be among", "was surely among",
}
auxiliaries = {"is", "are", "was", "were", "will", "has", "have", "had", "they were", "we were",
    "you were", "he is", "it was", "they used to", "you used to", "we used to", "used to", "they used",
    "have been", "they have been", "you have been", "you would", "i would", "you were to", "they had been",
    "there is", "that was", "already", "verily", "indeed", "is what", "is the one who", "the one who",
    "the one", "those who", "those whom", "who", "whom", "which", "that", "what", "that which",
    "of what", "of that which", "of those who", "to those who", "for those who", "in what", "at what",
    "in that which", "to what", "to that which", "from what", "of those whom", "by that which",
    "so what", "and what", "so whatever", "then those who", "whoever is", "one who", "he who",
    "when", "then when", "and whenever", "whenever", "wherever", "where", "if", "as for", "then soon",
    "that whoever wills", "that your lord", "that my lord", "whether", "even if", "as much as i am able",
}
functions = prepositions | auxiliaries | {"before", "after", "any", "every", "all", "each", "not", "no",
    "never", "and", "or", "but", "except", "besides", "instead of", "other than", "it", "they", "we", "you",
    "he", "this", "those", "that not", "from allah", "before it", "from him", "from us"}
nominal_sources = {"those who", "those whom", "the one who", "the one", "what", "whatever", "who", "whom"}
skip = {"2:48:4", "3:146:3", "6:48:2", "6:143:7", "6:144:5", "39:66:6", "41:24:11",
        "48:16:4", "16:102:3", "23:20:5", "48:25:7", "97:3:6", "2:217:3",
        "3:125:7", "5:107:4", "79:43:4", "62:6:11", "2:236:19", "5:106:43", "42:34:7"}
skip.update({"25:59:8", "32:4:9", "50:38:8", "57:4:7"})
case_suffix = re.compile(r"(?:n[dt][ae]n|[dt][ae]n|n[dt][ae]|[dt][ae]|[ny]?[ıiuü]n|[ny]?[ıiuü]|[ny]?[ae]|[iyuüı]?yl[ae]|l[ae])$")
copula = re.compile(r"(?:[dt][ıiuü]r(?:lar|ler)?|[dt][ıiuü](?:lar|ler|k|m|n|nız|niz)?|ym[ıiuü]ş(?:[ıiuü]z|lar|ler)?|m[ıiuü]ş(?:[ıiuü]z|lar|ler)?)$")
blocked_case = {"musa", "riba", "faiz", "allah", "adem", "hakim", "alim", "dünya", "her", "he", "önce", "sonra", "süre", "şey", "su", "on iki", "altı", "bir", "iki", "üç", "cin"}

for key in sorted(en.keys() - tr.keys(), key=numeric):
    prev, following = adjacent(key, -1), adjacent(key, 1)
    if key in used or key in skip or prev not in tr or prev in used or prev in previously_aligned:
        continue
    if following in en and following not in tr:
        continue
    source, target = norm(en[prev]), norm(en[key])
    base_source = source.removeprefix("and ")
    base_source = re.sub(r"^(?:is|are|was|were) (?=(?:the ones who|the one who|those who|those|the ones)$)", "", base_source)
    base_source = {"the ones who":"those who", "those":"those who", "the ones":"those who"}.get(base_source,base_source)
    raw = tr[prev]
    surface, flat, indexes = flat_surface(raw)
    if target in functions or target.startswith(("before", "after", "besides", "other than", "instead of")):
        continue
    spans = []
    category = None
    evidence = ""
    witnesses = lexicon[gloss(en[key])]
    exact = lower(flat).strip(" .;,!?") in witnesses
    if base_source in prepositions:
        # Phrase-final postpositions are separate overt relational material.
        post = re.search(r"\s+(?:için(?:dir)?|içinde|içine|boyunca|kadar(?:dır)?|göre|karşı(?:lık)?|olarak|ile|adına|açısından|ölçüsünde|yüzünden|dolayı|yanında|sürece|iktidarına)\s*$", flat)
        if post:
            start = post.start() + 1
            spans.append(map_span(start, post.end(), indexes, surface))
            # A preceding case ending belongs to the same relation.
            inner_text = flat[:post.start()]
            inner = re.search(r"(?:n?[dt][ae]n|[ny][ae]|n[ıiuü]n|[ıiuü]n)$", inner_text)
            if inner and inner.start() >= 3 and len(inner_text[:inner.start()].split()[-1]) >= 2 and lower(inner_text) not in blocked_case:
                spans.append(map_span(inner.start(), inner.end(), indexes, surface))
            category, evidence = "nominal_postposition", "Existing postposition and its governed ending"
        else:
            clean = flat.rstrip(" ;,.:!?")
            tail = ""
            cm = copula.search(clean)
            if cm and cm.start() > 2:
                tail, clean = cm.group(), clean[:cm.start()]
            candidates = []
            for start in range(max(1, len(clean)-5), len(clean)):
                end = clean[start:]
                if re.fullmatch(case_suffix, end) and len(clean[:start].strip()) >= 2:
                    stem = clean[:start].rstrip("'")
                    candidates.append((lower(stem) in witnesses, start, stem, end))
            candidates.sort(key=lambda c: (-c[0], -c[1]))
            if lower(clean) in blocked_case or exact:
                candidates = []
            # Unknown lexical stems do not justify peeling an arbitrary final a/e/i.
            supported = [c for c in candidates if c[0] or len(c[3]) >= 2 and re.match(r"(?:n?[dt][ae]|[iyuüı]?yl|[ny]?[ıiuü]n)", c[3])]
            if supported:
                witness, start, stem, ending = supported[0]
                explicit_stems = {"hayata": "hayat", "tağuta": "tağut", "bir mağfirete": "bir mağfiret",
                                  "hüsrandan": "hüsran", "boşa çıkandan": "boşa çıkan"}
                if clean in explicit_stems:
                    start = len(explicit_stems[clean])
                if ending.startswith("n") and lower(stem + "n").split()[-1] in {"din", "gün", "kadın", "insan", "şeytan", "zeytin", "ekin", "koyun", "bütün", "cin", "yakın", "yemin", "zindan"}:
                    start += 1
                elif not witness and start >= 2 and clean[start-1] == "n" and clean[start-2] in "ıiuü" and not target.startswith("your ") and lower(clean[:start]).split()[-1] not in {"din", "gün", "kadın", "insan", "şeytan", "zeytin", "ekin", "koyun", "bütün", "cin", "yakın", "yemin", "zindan"}:
                    start -= 1
                if clean[:start].endswith("'"):
                    start -= 1
                spans.append(map_span(start, len(clean), indexes, surface))
                if tail and re.search(r"\b(?:is|are|was|were|be)\b", source):
                    spans.append(map_span(len(clean), len(clean)+len(tail), indexes, surface))
                category = "nominal_case"
                evidence = "Existing written case form; lexical witness" if witness else "Existing multi-letter relational ending"
            elif exact:
                category, evidence = "zero_surface_relation", "Uninflected lexical expression corroborated elsewhere in the supplied corpus"
        # Avoid mapping a lexical verb to an unrelated nominal function entry.
        if target in {"said", "sends", "says", "desires", "come", "comes", "revealed", "kill", "send", "make"}:
            category = None
    elif base_source == "any":
        match = re.match(r"(?:hiç\s*bir|herhangi bir|bir)\b\s*", flat, re.I)
        if match and match.end() < len(flat):
            spans.append(map_span(match.start(), match.end(), indexes, surface))
            category, evidence = "indefinite_quantifier", "Existing indefinite determiner"
    elif base_source in auxiliaries:
        # A lexical counterpart must already be visible: finite forms, nouns,
        # and nominalized predicates are retained rather than back-translated.
        if not exact and (base_source in {"is", "are", "was", "were", "has", "have", "had", "will"}) and len(flat.strip().split()) == 1 and lower(flat.strip()) in {"allah", "alah", "muhammed", "rabbin"}:
            pass  # Clear displaced proper names; copula can surface elsewhere.
        if base_source in {"when", "then when", "and whenever", "whenever"}:
            marker = re.search(r"(?:[ıiuü]nc[ae]|[dt][ıiuü]ğ[ıiuü](?:m|n|muz|nuz)?|[ae]rken|ken|[ıiuü]p)(?=\b|\s|$)", flat)
            if marker:
                spans.append(map_span(marker.start(), marker.end(), indexes, surface))
        elif base_source in {"wherever", "if", "whether", "even if", "whoever is"}:
            marker = re.search(r"s[ae](?:n[ıiuü]z|lar|ler|m|n)?(?:\s+de|\s+da|\s+mi)?[?!]*$", flat)
            if marker and marker.start() >= 2:
                spans.append(map_span(marker.start(), marker.end(), indexes, surface))
        elif "who" in base_source or base_source in {"what", "which", "that which", "that", "of what", "of that which", "in what", "at what", "in that which", "to what", "to that which", "from what", "so what", "and what", "so whatever"}:
            # Explicit high-confidence participial suffixes, including inherited
            # explanatory parentheses inside the surface expression.
            marker = re.search(r"(?:[dt][ıiuü]ğ|[dt][ıiuü]k|m[ae][kğ])", flat)
            if not marker:
                marker = re.search(r"[ae]n(?=lar|ler|[ıiuü](?:n|m|z|$)|[ae]$|$)", flat)
                if marker and lower(flat) in {"insan", "iman", "zaman", "şeytan", "kervan", "zaten", "hemen", "bazen", "sürekli", "kalblerinde", "içindeki", "verilen müjdenin"}:
                    marker = None
                if marker and (re.search(r"[dt][ae]n$", flat) and marker.start() >= len(flat)-3 or
                               any(lower(flat).startswith(p) for p in ["kusur", "iyilik", "kötülük", "tuzak", "temas", "çevre", "sizin suç", "onun yan", "yararlanm", "size verilen cez", "indirmiş ik", "inanın"])):
                    marker = None
            if marker and marker.start() >= 2:
                end = marker.end()
                if "who" in base_source:
                    end = len(flat)
                spans.append(map_span(marker.start(), end, indexes, surface))
        else:
            marker = copula.search(flat.rstrip(" !?;,."))
            if lower(flat).strip().startswith("va'"):
                marker = None
            if marker and marker.start() >= 2:
                spans.append(map_span(marker.start(), marker.end(), indexes, surface))
        category = "grammatical_predicate" if spans else "zero_surface_function"
        evidence = "Existing grammatical surface retained" if spans else "No separate overt function-word surface in the inherited Turkish expression; lexical wording redistributed"
    if category is None:
        continue
    if source.startswith("and ") and flat.startswith("ve "):
        spans.append(map_span(0, 2, indexes, surface))
    parts = parts_from_spans(surface, prev, key, spans)
    # Do not publish a lexical entry whose entire expression was consumed by
    # an apparent grammatical ending.
    if not any(p["role"] == key and p["text"].strip() for p in parts):
        continue
    add([prev, key], parts, evidence + "; inspect the whole ayah for inherited lexical quality. Case forms reflect the Turkish construction, not a universal dictionary equivalent of the English preposition.", category)

# Further explicit groups are added below after inspecting the generated plan.

for key in sorted(en.keys() - tr.keys(), key=numeric):
    prev, following = adjacent(key, -1), adjacent(key, 1)
    if key in used or prev in used or prev not in tr or prev in previously_aligned or key in skip:
        continue
    source, target = norm(en[prev]), norm(en[key])
    if following in en and following not in tr:
        continue
    raw = tr[prev]
    surface, flat, indexes = flat_surface(raw)
    spans, category, reason = [], None, None
    if target.startswith("before") and source in {"from", "before", "and before", "before it"} and any(w in flat for w in ["önce", "ötedenberi"]):
        marker = re.search(r"den(?=\s|$)", flat)
        if marker:
            spans.append(map_span(marker.start(), marker.end(), indexes, surface))
        if source.startswith("and ") and flat.startswith("ve "):
            spans.append(map_span(0, 2, indexes, surface))
        category, reason = "temporal_idiom", "The temporal expression is overt; Arabic min/qabl may have no separately pronounced Turkish case ending in this construction. Do not invent one."
    elif target in {"every", "each", "all", "all kinds"} and flat.startswith(("her çeşit", "türlü türlü")):
        marker = re.search(r"(?:ten|tan)$", flat)
        if marker:
            spans.append(map_span(marker.start(), marker.end(), indexes, surface))
        category, reason = "quantifier_phrase", "Move the existing quantifier phrase to its source entry, retaining any overt partitive ending separately."
    elif source in {"do", "can", "shall", "shall i", "has", "have not", "are", "is", "may", "will", "then do", "then do not", "do not", "would", "then why don't", "and has there"}:
        match = re.search(r"m[ıiuü](?:y[dt][ıiuü])?(?:s[ıiuü]n[ıiuü]z|s[ıiuü]n|y[ıiuü]m|y[ıiuü]z|lar|ler)?(?:\s*d[ıiuü]r)?[?!]*$", flat)
        if match and match.start() >= 2:
            end = match.end()
            while end > match.start() and flat[end-1] in "?!":
                end -= 1
            spans.append(map_span(match.start(), end, indexes, surface))
            category, reason = "question_particle", "The inherited question particle expresses the interrogative auxiliary; keep the lexical predicate outside its contextual parentheses."
    elif re.search(r"\bnot\b|\bno\b|\bnone\b|\bnothing\b", source):
        negative = re.search(r"\b(?:ne de|ne|yok|değil)(?:tur|tür|tı|ti|muş|miş|sa)?\b", flat)
        if negative and negative.group().startswith(("ne", "yok", "değil")):
            end = negative.end()
            if negative.group().startswith(("yok", "değil")):
                end = negative.start()+ (3 if negative.group().startswith("yok") else 5)
            spans.append(map_span(negative.start(), end, indexes, surface))
            if target in {"is", "there are", "there been"}:
                # Existential yok is indivisible; its conditional/tense tail
                # must not be falsely highlighted as the English copula.
                category, reason = "negative_existential", "Existence and negation are fused lexically in yok. The source copula has no independent surface; its contextual view remains fully parenthesized."
                parts = parts_from_spans(surface, prev, key, spans)
                for part in parts:
                    if part["role"] == key:
                        part["role"] = "context"
                add([prev,key],parts,reason,category)
                continue
            category, reason = "negative_word", "Expose the overt negative word in the existing expression, rather than duplicating the complete negative predicate."
        elif re.search(r"(?:ma|me)(?:z|[dt][ıiuü]|y[ae]c|y[ıiuü]|s[ae]|mış|miş)|m[ıiuü]yor|s[ıiuü]z", flat) and key not in {"9:74:17"}:
            marker = re.search(r"(?:ma|me)(?:z(?=\w)|z$|(?=[dt][ıiuü]|y[ae]c|y[ıiuü]|s[ae]|mış|miş))|m[ıiuü](?=yor)|s[ıiuü]z", flat)
            if marker and marker.start() >= 2:
                spans.append(map_span(marker.start(),marker.end(),indexes,surface))
                for extra in re.finditer(r"\b(?:kimse|hiç|asla|ve)\b", flat):
                    spans.append(map_span(extra.start(),extra.end(),indexes,surface))
                category, reason = "negative_predicate", "The existing negative ending remains overt; a following exception does not justify declaring that ending zero."
        elif re.search(r"\bexcept\b|\bbut\b", norm(en.get(following, ""))) and target not in {"they were", "it", "he", "they", "you", "we were", "we", "it is", "is this", "is it", "am i"}:
            category, reason = "restrictive_zero", "The Arabic/English negative-plus-exception construction is expressed by the separate Turkish restrictive word at the following entry; no negative ending is present in this lexical expression."
        elif source == "and not" and flat.startswith("ve ") and following in tr and any(w in tr[following] for w in ["mez", "maz", "meye", "maya", "değil", "edilmez"]):
            spans.append(map_span(0, 2, indexes, surface))
            category, reason = "negative_conjunction", "The conjunction is overt here; negation is already expressed on the following predicate. Move the displaced lexical item without inventing another negative."
    if category:
        parts = parts_from_spans(surface, prev, key, spans)
        if any(p["role"] == key and p["text"].strip() for p in parts):
            add([prev, key], parts, reason, category)

# Quantifier/demonstrative words can intervene between a preposition and the
# noun carrying its case. The source relation must attach to that later noun.
quantifier_rows = [
    ("2:261:13", "her", "başağı", "nda"),
    ("3:117:4", "bu", "dünya", ""),
    ("4:75:17", "şu", "kent", "ten"),
    ("6:123:3", "her", "kentin", ""),
    ("7:22:19", "bu", "ağaç", "tan"),
    ("7:156:3", "bu", "dünya", "da"),
    ("9:126:5", "her", "yıl", ""),
    ("11:60:2", "bu", "dünya", "da"),
    ("16:30:11", "bu", "dünya", "da"),
    ("17:41:3", "bu", "Kur'an", "'da"),
    ("17:89:4", "bu", "Kur'an", "'da"),
    ("18:54:3", "bu", "Kur'an", "'da"),
    ("22:5:66", "her", "çifti", ""),
    ("25:51:4", "her", "kent", "e"),
    ("28:42:2", "bu", "dünya", "da;"),
    ("30:58:4", "bu", "Kur'an", "'da"),
    ("39:10:9", "bu", "dünya", "da"),
    ("39:27:4", "bu", "Kur'an", "'da"),
    ("39:27:7", "her", "temsili", ""),
    ("41:12:7", "her", "göğ", "e"),
]
for first, determiner, root, ending in quantifier_rows:
    middle, last = adjacent(first, 1), adjacent(first, 2)
    if used.intersection([first,middle,last]):
        continue
    assert tr[first] == determiner and tr[last] == root+ending, (first,tr.get(last))
    # The earliest row has a noun phrase distributed across an additional key;
    # uninflected cases explicitly show a zero surface rather than a fake case.
    parts = [{"text": determiner, "role": middle}, {"text": " ", "role": "context"}, {"text": root, "role": last}]
    if ending:
        parts.append({"text": ending, "role": first})
    add([first,middle,last], parts,
        "The determiner was stored under the preposition while the following noun carries the Turkish case. Preserve the inherited case form, including zero realization where present.",
        "intervening_determiner", [first,last])

# Numerals and periods: the locative relation surfaces on the later day noun.
for first in ["25:59:7", "32:4:8", "50:38:7", "57:4:6"]:
    middle,last = adjacent(first,1),adjacent(first,2)
    assert tr[first] == "altı" and tr[last] == "günde"
    add([first,middle,last],[{"text":"altı","role":middle},{"text":" ","role":"context"},
         {"text":"gün","role":last},{"text":"de","role":first}],
        "The time span is 'altı günde': its numeral, day noun, and locative ending occupy three source positions.","numeral_time_span",[first,last])

# Direct lexical omissions, explicitly introduced rather than claimed as
# redistributions. These retain all surrounding values and record new wording.
def explicit_pair(key, segments, category="explicit_phrase"):
    prev=adjacent(key,-1)
    if key in used or prev in used:
        return
    parts=[{"text":text,"role":prev if owner==0 else key if owner==1 else "context"} for owner,text in segments]
    expression="".join(p["text"] for p in parts)
    assert expression == tr[prev].replace("(","[").replace(")","]"), (key,expression,tr[prev])
    add([prev,key],parts,"Individually inspected phrase or grammatical cluster; preserve its existing wording and record any non-independent source contribution as context.",category)

for key,segments in {
    "9:3:3": [(1,"Allah"),(0,"tan")],
    "9:29:27": [(1,"elleri"),(0,"yle")],
    "10:76:5": [(1,"katımız"),(0,"dan")],
    "11:1:8": [(1,"tarafı"),(0,"ndan")],
    "11:34:11": [(1,"Allah")],
    "11:55:2": [(1,"O'"),(0,"ndan"),(2," "),(1,"başka")],
    "11:78:6": [(0,"ve "),(1,"daha önce")],
    "11:88:27": [(1,"gücümün yettiği"),(0,"nce")],
    "11:107:4": [(1,"dur"),(0,"dukça")],
    "11:108:9": [(1,"dur"),(0,"dukça")],
    "12:21:22": [(1,"yorumu"),(0,"nu")],
    "12:40:4": [(1,"o'nu "),(0,"bırakıp")],
    "12:41:18": [(1,"hakkı"),(0,"nda")],
    "12:100:14": [(1,"önce"),(0,"ki")],
    "14:17:14": [(0,"bunun "),(1,"ardından")],
    "16:35:10": [(1,"O'"),(0,"ndan"),(2," "),(1,"başka")],
    "16:35:19": [(1,"O'"),(0,"nsuz")],
    "16:50:4": [(1,"üstleri"),(0,"ndeki")],
    "16:90:8": [(1,"akraba"),(2,"ya")],
    "17:2:11": [(1,"ben"),(0,"den"),(2," "),(1,"başka")],
    "17:26:3": [(1,"akraba"),(2,"ya")],
    "17:26:7": [(0,"ve "),(1,"yol"),(0,"cu"),(2,"ya")],
    "17:58:15": [(1,"Bu")],
    "18:50:20": [(1,"ben"),(0,"den"),(2," "),(1,"ayrı olarak")],
    "18:58:18": [(1,"o"),(0,"ndan"),(2," "),(1,"başka")],
    "18:76:12": [(1,"benim tarafım"),(0,"dan")],
    "18:90:14": [(1,"ona [güneşe]"),(2," "),(0,"karşı")],
    "18:93:8": [(1,"onların dışı"),(0,"nda")],
    "18:107:7": [(0,"onlar için "),(1,"vardır")],
    "19:17:3": [(1,"onlar"),(0,"la arasına")],
    "19:31:10": [(1,"olduğum"),(2," "),(0,"sürece")],
    "19:37:4": [(1,"kendi araları"),(0,"ndan")],
    "19:64:9": [(0,"ön"),(1,"ümüz"),(2,"de")],
    "21:84:14": [(1,"tarafımız"),(0,"dan")],
    "21:109:6": [(1,"eşit"),(2," "),(0,"biçimde")],
    "22:19:15": [(1,"üstü"),(0,"nden")],
    "23:19:6": [(1,"hurma")],
    "23:40:3": [(1,"az"),(2," "),(0,"sonra")],
    "23:44:6": [(0,"ne "),(1,"zaman")],
    "23:50:10": [(1,"oturmaya uygun")],
    "23:77:7": [(1,"bir azab")],
    "24:30:5": [(1,"bakışları"),(2,"nı")],
    "24:40:9": [(1,"onun üstü"),(0,"nden")],
    "24:40:12": [(1,"onun üstü"),(0,"nden")],
    "24:40:22": [(1,"neredeyse")],
    "24:61:66": [(1,"tarafı"),(0,"ndan")],
    "25:42:2": [(1,"nerdeyse")],
    "27:6:5": [(1,"katı"),(0,"ndan")],
    "27:42:12": [(1,"daha önce")],
    "27:55:6": [(1,"bırakıp")],
    "28:23:13": [(1,"onların gerisi"),(0,"nde")],
    "28:37:9": [(1,"kendisinin yanı"),(0,"ndan")],
    "28:48:5": [(1,"katımız"),(0,"dan")],
    "29:67:10": [(1,"çevreleri"),(0,"nden")],
    "30:38:3": [(1,"akraba"),(2,"ya")],
    "30:38:7": [(0,"ve "),(1,"yol"),(0,"cu"),(2,"ya")],
    "30:42:11": [(1,"önce"),(0,"ki")],
    "32:5:13": [(1,"onun süresi")],
    "32:26:7": [(1,"daha önce"),(0,"ki")],
    "33:6:26": [(1,"bunlar")],
    "33:50:42": [(1,"dışı"),(0,"nda")],
    "35:2:16": [(1,"O'"),(0,"ndan"),(2," "),(1,"sonra")],
    "35:3:11": [(1,"Allah"),(0,"tan"),(2," "),(1,"başka")],
    "38:11:3": [(1,"şura"),(0,"da")],
    "39:20:8": [(1,"üst"),(0,"üste")],
    "41:10:5": [(1,"üstü"),(0,"nden")],
    "41:25:17": [(1,"gelip geçmiş"),(2," "),(0,"olan")],
    "41:43:7": [(1,"söylen"),(0,"miş")],
    "41:52:6": [(1,"tarafı"),(0,"ndan")],
    "43:51:15": [(1,"altım"),(0,"dan")],
    "43:65:4": [(1,"araları"),(0,"ndan"),(2," çıkan")],
    "45:10:2": [(1,"öteleri"),(0,"nden"),(2," de")],
    "45:23:9": [(1,"bir bilgi"),(0,"ye göre")],
    "48:23:5": [(1,"süre"),(0,"gelir")],
    "48:29:17": [(1,"Allah"),(0,"dan")],
    "49:8:3": [(1,"Allah"),(0,"tan")],
    "57:11:3": [(0,"olan "),(1,"kimse")],
    "57:13:26": [(1,"yönü"),(0,"nde")],
}.items():
    explicit_pair(key,segments,"repeated_gloss_phrase")

# Multiple successive source functions can share one predicate. These are
# explicit decompositions, not repeated copies of a guessed translation.
multi_predicates = [
    ("2:236:7", [(2,"henüz dokun"),(1,"ma"),("context","dan")]),
    ("4:72:13", [(2,"bulun"),(1,"ma"),(2,"dım")]),
    ("10:42:9", [(2,"akıl et"),(1,"mi"),(2,"yorlar"),(0,"sa")]),
    ("10:43:9", [(2,"gör"),(1,"mü"),(2,"yorlar"),(0,"sa")]),
    ("22:71:5", [(2,"indir"),(1,"me"),(2,"miş"),("context","tir")]),
    ("25:40:9", [(2,"onu gör"),(0,"mü"),(2,"yorlar"),("context"," "),(0,"mı"),(1,"ydı"),("context","?")]),
    ("3:5:9", [(0,"ve "),(2,"gök"),(1,"te")]),
    ("3:7:15", [(2,"kalbleri"),(1,"nde")]),
    ("4:23:39", [("context","kendi "),(2,"sulbünüz"),(1,"den")]),
    ("20:72:4", [(2,"bize gel"),(1,"en"),(0,"e")]),
    ("23:55:4", [(2,"mal")]),
]
for first,segments in multi_predicates:
    members=[first,adjacent(first,1),adjacent(first,2)]
    if used.intersection(members):
        continue
    parts=[{"text":text,"role":members[role] if isinstance(role,int) else role} for role,text in segments]
    assert "".join(p["text"] for p in parts)==tr[first],first
    add(members,parts,"Explicit multi-entry predicate/phrase decomposition preserves the written expression and keeps each negative, nominal, or case contribution at its own source position.","multi_entry_decomposition")

# Selected Arabic positional checks clarify misleading English glosses. The
# English values remain untouched; reasons document the Arabic contributors.
for key in ["2:79:10", "2:89:5", "2:101:5", "2:103:7", "3:7:40", "3:37:26", "3:78:17", "3:78:22", "4:78:16", "4:78:28", "4:82:7", "8:10:13"]:
    prev=adjacent(key,-1)
    if key in used or prev in used:
        continue
    surface=tr[prev]
    match=re.fullmatch(r"(katı|tarafı)(ndan)(dır)?",surface)
    assert match, (key,surface)
    parts=[{"text":match[1],"role":key},{"text":match[2],"role":prev}]
    if match[3]: parts.append({"text":match[3],"role":"context"})
    add([prev,key],parts,
        "Arabic min is the case relation and 'ind/taraf is the contextual location noun; the English reference may label min '(is)'. Preserve that reference gloss but align the actual source contribution. Selected evidence: Quranic Arabic Corpus 2:79.","source_position_clarification")

explicit_pair("2:60:12",[(1,"on"),(2," "),(0,"iki")],"compound_numeral")

# Supply missing lexical material together with its already-present isolated
# case ending, so the completed display never leaves -den/-dan unattached.
for key,root,ending,prefix in [
    ("3:146:3","bir peygamber","den",""),
    ("6:143:7","keçiler","den","ve "),
    ("6:144:5","sığırlar","dan","ve "),
    ("39:66:6","şükredenler","den",""),
    ("41:24:11","hoşnut edilenler","den",""),
    ("48:16:4","bedevi Araplar","dan",""),
]:
    prev=adjacent(key,-1)
    assert tr[prev].replace("-","") == prefix+ending
    parts=([{"text":prefix,"role":prev}] if prefix else [])+[{"text":root,"role":key},{"text":ending,"role":prev}]
    add([prev,key],parts,"New lexical noun supplied and attached to the existing isolated case ending. The contextual pair now identifies both contributions; this introduces lexical wording rather than claiming the noun was already translated.","new_lexical_with_case",[prev],True)

# Two clear displaced phrases need actual repairs rather than zero labels.
assert tr["75:12:1"]=="Rabbinin" and tr["75:12:2"]=="o gün"
add(["75:12:1","75:12:2","75:12:3"],[{"text":"Rabbin","role":"75:12:2"},
    {"text":"e","role":"75:12:1"},{"text":" ","role":"context"},{"text":"o gün","role":"75:12:3"}],
    "Move 'o gün' to 'that Day', restore the divine-reference noun to 'your Lord', and correct inherited genitive Rabbinin to dative Rabbine for the source relation 'To'.",
    "displacement_and_case_repair",["75:12:1","75:12:2"],True)
assert tr["2:217:2"]=="ayında"
add(["2:217:2","2:217:3"],[{"text":"ay","role":"2:217:3"},{"text":" ","role":"context"},
    {"text":"hakkında","role":"2:217:2"}],
    "Replace the inherited locative phrase with the actual about/month relation. The locative ending must not be mislabeled as 'about'. Selected Arabic positional check: Quranic Arabic Corpus 2:217.",
    "preposition_repair",["2:217:2"],True)

manual_cases = [
    ("2:76:11", "bazısı", "na"), ("2:177:24", "yakınlar", "a"),
    ("2:213:41", "gerçeğ", "e"), ("2:226:4", "kadınları", "na"),
    ("2:235:8", "evlenme isteğiniz", "i"), ("2:238:3", "namazlar", "ı"),
    ("2:243:4", "kimseler", "i"), ("2:258:4", "kimse", "yi"),
    ("2:259:5", "bir kasaba", "ya"), ("3:23:4", "kimseler", "i"),
    ("3:125:14", "melek", "le"), ("3:194:6", "elçileri", "ne"),
    ("4:4:9", "bir kısmı", "nı"), ("4:44:4", "kimseler", "in"),
    ("4:60:4", "kimseler", "i"), ("4:77:4", "kimseler", "i"),
    ("4:107:4", "kimseler", "i"), ("4:149:9", "bir kötülüğ", "ü"),
    ("5:83:15", "gerçekler", "i"), ("5:84:9", "gerçeğ", "e"),
    ("6:143:17", "rahimleri", "nde"), ("6:144:15", "Rahimleri", "nde"),
    ("7:32:11", "rızıklar", "ı"), ("7:185:11", "şeyler", "e"),
    ("8:26:17", "güzel şeyler", "le"), ("8:42:26", "açık delil", "le"),
    ("8:42:31", "açık delil", "le"), ("9:94:16", "sizin haberleriniz", "i"),
    ("11:52:14", "gücünüz", "e"), ("11:53:11", "senin sözün", "le"),
    ("12:6:6", "yorumu", "nu"), ("12:43:20", "bu rü'yam", "ı"),
    ("12:87:5", "Yusuf", "'u"), ("12:101:8", "yorumu", "nu"),
    ("14:28:4", "kimseler", "i"), ("14:46:12", "dağlar", "ı"),
    ("15:47:6", "kin", "i"), ("16:48:4", "şeyler", "i"),
    ("16:59:11", "hakaret", "le"), ("16:72:15", "güzel rızıklar", "la"),
    ("16:80:5", "evleriniz", "i"), ("17:70:11", "güzel rızıklar", "la"),
    ("18:31:12", "bilezikler", "le"), ("19:6:4", "oğulları", "na"),
    ("20:40:8", "biri", "ni"), ("20:113:8", "tehditler", "i"),
    ("21:71:8", "alemler", "e"), ("21:84:7", "derd", "i"),
    ("22:51:4", "eyetlerimiz", "i"), ("23:6:3", "eşleri", ""),
    ("23:9:4", "namazları", "nı"), ("25:27:5", "elleri", "ni"),
    ("26:166:7", "eşleriniz", "i"), ("27:44:11", "bacakları", "nı"),
    ("29:48:7", "Kitap", "tan"), ("30:40:12", "ortaklarınız", "dan"),
    ("31:19:6", "sesin", "i"), ("32:26:9", "kuşaklar", "ı"),
    ("33:59:11", "örtülerin", "i"), ("33:73:10", "inanan erkekler", "i"),
    ("34:6:14", "yolu", "na;"), ("34:11:6", "dokuması", "nı"),
    ("34:12:26", "azab", "ı"), ("34:38:4", "ayetlerimiz", "i"),
    ("35:45:24", "kulları", "nı"), ("40:64:14", "güzel rızıklar", "la"),
    ("42:20:9", "onun ekini", "ni"), ("42:21:7", "din", "i"),
    ("42:30:10", "birçoğu", "nu"), ("45:16:10", "güzel rızıklar", "la"),
    ("48:18:5", "mü'minler", "den"), ("58:22:25", "onların kalbleri", "ne"),
    ("58:8:4", "kimseler", "i"), ("58:14:4", "kimseler", "i"),
    ("59:5:4", "bir hurma ağacı", "nı"), ("59:11:4", "kimseler", "i"),
    ("67:19:4", "uçan kuşlar", "ı"), ("68:32:9", "Rabbimiz", "i"),
    ("68:42:7", "secde", "ye;"), ("70:30:3", "eşleri", ""),
    ("70:34:4", "namazları", "nı"), ("72:26:6", "gizli bilgisi", "ni"),
    ("74:41:2", "suçlular", "ın"), ("75:14:4", "kendi nefsi", "ni"),
]
for key, root, ending in manual_cases:
    prev = adjacent(key,-1)
    if key in used or prev in used:
        continue
    assert tr[prev] == root+ending, (key,tr[prev],root+ending)
    parts = [{"text":root,"role":key}]
    if ending:
        parts.append({"text":ending,"role":prev})
    add([prev,key],parts,
        "Individually inspected noun phrase: retain the written stem and expose its actual Turkish case form. An absent case ending is recorded as a zero surface, not invented.","manual_nominal_boundary")

zero_nominals = [
    "2:249:51", "3:195:11", "4:8:5", "4:23:17", "5:33:20", "6:99:27",
    "6:152:27", "7:38:10", "7:124:5", "7:179:6", "8:53:10", "8:60:6",
    "8:72:27", "9:92:18", "12:20:9", "13:4:7", "18:32:9", "19:43:6",
    "19:74:5", "20:71:17", "21:47:15", "22:23:16", "24:43:25", "26:49:19",
    "28:12:10", "30:39:4", "31:16:8", "31:27:6", "33:4:6", "33:19:15",
    "34:7:7", "34:16:15", "35:33:7", "36:34:5", "37:146:5", "41:29:9",
    "42:36:4", "43:6:4", "43:12:8", "46:27:6", "52:40:6", "59:6:11",
    "61:10:7", "90:14:6", "90:15:3", "90:16:4",
]
for key in zero_nominals:
    prev=adjacent(key,-1)
    if key in used or prev in used:
        continue
    surface=tr[prev].replace("(","[").replace(")","]")
    add([prev,key],[{"text":surface,"role":key}],
        "Individually inspected displaced noun phrase. The source relation has no separate overt form in this inherited Turkish rendering; display its entire phrase as context rather than inventing an ending.","manual_zero_relation")

new_lexical = {
    "3:146:3": "bir peygamber", "6:143:7": "keçiler", "6:144:5": "sığırlar",
    "39:66:6": "şükredenler", "41:24:11": "hoşnut edilenler", "48:16:4": "bedevi Araplar",
    "97:3:6": "ay", "53:59:3": "söze", "80:18:3": "şeyden", "50:7:10": "çiftten",
    "31:10:26": "çiftten", "27:83:5": "ümmetten", "28:75:4": "ümmetten",
    "27:23:8": "şeyden", "24:50:3": "hastalık", "39:47:15": "azabı",
    "54:25:3": "ona", "75:12:3": "o gün", "48:25:7": "Haram'dan", "23:20:5": "Sina'dan",
    "46:28:7": "Allah'tan", "37:156:3": "deliliniz", "68:39:3": "yeminleriniz",
    "68:41:3": "ortakları", "21:108:11": "teslim olanlar mısınız?", "40:47:15": "savabilir misiniz?",
    "32:3:2": "diyorlar mı?", "46:8:3": "onu uydurdu", "17:69:12": "rüzgar",
    "22:28:15": "hayvanların",
}
for key,value in new_lexical.items():
    if key in used:
        continue
    assert key not in tr
    add([key],[{"text":value,"role":key}],
        "New lexical wording supplied for an absent source entry; surrounding inherited wording is retained. This is a translation addition, not a claim that a suffix already expressed this word.",
        "new_lexical_translation", [], True)

# Final review overrides are intentionally explicit: these forms are not
# evidence that a matching letter sequence always identifies a morpheme.
boundary_overrides = {
    "2:59:7": [(1,"söylen"),(0,"en"),(2,"den")],
    "7:162:8": [(1,"söylen"),(0,"en"),(2,"den")],
    "7:158:10": [(0,"o"),(1,"nun"),(2,"dur")],
    "7:188:14": [(1,"bil"),(0,"seydim")],
    "30:28:7": [(1,"sizin için"),(2," var"),(0,"mı dır"),(2,"?")],
    "39:9:15": [(1,"eşit"),(0,"midir"),(2,"?")],
    "6:99:20": [(1,"hurma"),(0,"nın")],
    "7:73:27": [(1,"arzı"),(0,"ndan")],
    "10:27:20": [(1,"bir gece"),(0,"nin")],
    "20:120:9": [(1,"ağacı"),(0,"nı")],
    "10:106:16": [(1,"zalimler"),(0,"den"),(2," olursun")],
    "17:111:19": [(1,"acze düşüp de")],
    "89:8:6": [(1,"ülkeler"),(2," "),(0,"arasında")],
    "9:120:39": [(1,"düşman"),(2," "),(0,"karşısında")],
    "6:135:5": [(1,"imkanınız"),(0,"a"),(2," "),(0,"göre")],
    "34:17:6": [(1,"biz cezalandırır"),(2," "),(0,"mıyız"),(2,"?")],
}
for key,segments in boundary_overrides.items():
    group=next(g for g in groups if key in g["members"])
    prev=adjacent(key,-1)
    parts=[{"text":text,"role":prev if role==0 else key if role==1 else "context"} for role,text in segments]
    assert "".join(p["text"] for p in parts)==group["shared_expression"]
    group["parts"]=parts
    group["after"]={k:render(parts,k) for k in group["members"]}
    group["zero_surface_keys"]=[k for k in group["members"] if not any(p["role"]==k for p in parts)]
    group["reason"]+=" Final local review explicitly corrected the boundary; this override takes precedence over candidate matching."

assert tr["2:143:13"]=="ve yap(ma)dık"
add(["2:143:13","2:143:14"],[{"text":"ve ","role":"2:143:13"},
    {"text":"yap","role":"2:143:14"},{"text":"ma","role":"2:143:13"},{"text":"dık","role":"2:143:14"}],
    "The inherited parentheses already surround the actual negative -ma. Reinterpret this explicitly reviewed grammatical annotation rather than treating its contents as an explanatory note; preserve every letter.",
    "reviewed_grammatical_parentheses")
groups[-1]["origin_normalization"]="Remove inherited grammatical parentheses; retain all letters."

updates = {k: v for group in groups for k, v in group["after"].items()}
expected = tr | updates
expected = {k: expected[k] for k in en if k in expected}
summary = {"baseline": "033d895 plus reports/continued-alignment-changes.json",
           "baseline_missing_keys": len(en.keys()-tr.keys()), "added_keys": len(expected)-len(tr),
           "modified_existing_keys": sum(k in tr and tr[k] != v for k,v in updates.items()),
           "remaining_missing_keys": len(en.keys()-expected.keys()), "groups": len(groups),
           "groups_by_category": dict(Counter(g["category"] for g in groups)),
           "zero_surface_entries": sum(len(g["zero_surface_keys"]) for g in groups),
           "english_sha256": hashlib.sha256(en_bytes).hexdigest(),
           "turkish_before_sha256": hashlib.sha256(baseline_bytes).hexdigest()}
output = (json.dumps(expected, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
summary["turkish_after_sha256"] = hashlib.sha256(output).hexdigest()
for group in groups:
    if not group["lexical_revision"]:
        material=" ".join(tr[k] for k in group["expression_origins"])
        material=(material.replace("(","").replace(")","") if "origin_normalization" in group else
                  material.replace("(","[").replace(")","]"))
        assert material==group["shared_expression"],group["members"]
    for key,value in group["after"].items():
        assert value.replace("(","").replace(")","")==group["shared_expression"]
        assert value.strip()
    group["review_status"]="local_alignment_review_complete; inherited_semantics_not_certified"
    if group["zero_surface_keys"]:
        group["zero_surface_interpretation"]="No independent overt surface identified in the retained expression. Review zero realization versus an inherited omission in full ayah context."
report = {"summary": summary, "groups": groups,
          "review_limit": "Structural and local linguistic review; inherited lexical accuracy is not certified. Fully parenthesized views have no independently identified surface contribution. Zero realization versus inherited omission remains a semantic review task, not a certified absence of meaning."}
(ROOT / "reports/broad-alignment-changes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
buffer=io.StringIO(newline="")
writer=csv.writer(buffer,lineterminator="\n")
writer.writerow(["key","english","operation","before","after","category","zero_surface","lexical_revision","reason"])
for group in groups:
    for key in group["members"]:
        writer.writerow([key,en[key],"modify" if key in tr else "add",tr.get(key,""),group["after"][key],group["category"],
                         key in group["zero_surface_keys"],group["lexical_revision"],group["reason"]])
(ROOT / "reports/broad-alignment-changes.csv").write_text(buffer.getvalue(),encoding="utf-8")
linguistic_review=[]
for group in groups:
    if group["zero_surface_keys"] or group["lexical_revision"]:
        linguistic_review.append({"keys":group["members"],"zero_surface_keys":group["zero_surface_keys"],
            "reason":"Review zero realization versus inherited omission in complete ayah context." if group["zero_surface_keys"] else "Review newly supplied lexical wording or case repair.",
            "lexical_revision":group["lexical_revision"],"status":"requires_semantic_review"})
(ROOT / "reports/broad-linguistic-review.json").write_text(json.dumps(linguistic_review,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if args.apply:
    current = json.loads((ROOT / "turkish-wbw-translation.json").read_bytes())
    assert current == tr or current == expected, "Unexpected working-tree changes."
    assert all(expected[k] == v for k,v in tr.items() if k not in updates)
    assert all(expected[k] == en[k] for k in en if re.fullmatch(r"\(\d+\)",en[k]))
    assert set(expected) <= set(en)
    (ROOT / "turkish-wbw-translation.json").write_bytes(output)
    assert (ROOT / "english-wbw-translation.json").read_bytes() == en_bytes
    earlier_pending={r["key"]:r for r in json.loads(committed("reports/alignment-pending.json"))}
    pending=[]
    for key in sorted(en.keys()-expected.keys(),key=numeric):
        row=earlier_pending[key]
        row["previous_turkish"]=expected.get(row["previous_key"])
        row["context_baseline"]="Current Turkish file after broad alignment"
        pending.append(row)
    assert len(pending)==summary["remaining_missing_keys"]
    (ROOT / "reports/alignment-pending.json").write_text(json.dumps(pending,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(summary, indent=2))
