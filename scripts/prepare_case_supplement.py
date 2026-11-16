"""Prepare annotated, internal, and alternate-case constructions for review."""
import json
import re
from collections import defaultdict

from alignment_common import ROOT, load_baseline, lower, flat_surface, map_span, make_parts

en, tr = load_baseline()
main = json.loads((ROOT / "reports/suffix-alignment-plan.json").read_text(encoding="utf-8"))
handled = {r["content_key"] for r in main["operations"]}
normalize = lambda s: re.sub(r"^(?:the|a|an) ", "", re.sub(r"\s+", " ", re.sub(r"[\[\]()]", "", s).lower().strip()))
lexicon = defaultdict(set)
for k, v in tr.items():
    if not any(c in v for c in "()[]"):
        lexicon[normalize(en[k])].add(lower(v.strip()))
endings = {
    "ablative": ["nden", "ndan", "den", "dan", "ten", "tan"],
    "locative": ["nde", "nda", "de", "da", "te", "ta"],
    "dative": ["ye", "ya", "ne", "na", "e", "a"],
    "genitive": ["nin", "nın", "nun", "nün", "in", "ın", "un", "ün", "yun"],
    "accusative": ["nı", "ni", "nu", "nü", "yı", "yi", "yu", "yü", "ı", "i", "u", "ü"],
    "instrumental": ["yle", "yla", "le", "la"],
}
supported = {
    "from": {"ablative"}, "of": {"ablative", "genitive"}, "than": {"ablative"},
    "in": {"locative", "dative"}, "on": {"locative", "dative"}, "at": {"locative", "dative"},
    "upon": {"locative", "dative"}, "over": {"locative", "dative"}, "into": {"locative", "dative"},
    "to": {"locative", "dative"}, "for": {"dative", "instrumental"}, "towards": {"dative"},
    "with": {"instrumental"}, "by": {"instrumental"}, "among": {"ablative", "locative"},
    "about": {"ablative"}, "against": {"dative", "ablative"}, "before": {"dative"}, "after": {"ablative"},
}
nouns_n = {"din", "kin", "bin", "gün", "koyun", "zindan", "insan", "iman", "kurban", "şeytan", "rahman", "zaman", "hayvan", "kur'an", "irin", "ben", "sen", "kadın", "ekin", "beyin", "zemin", "yakın", "yemin", "hüzün", "dün", "bugün", "bütün", "yakîn", "yakin", "cin"}
plans = []
for key in sorted(en.keys() - tr.keys(), key=lambda k: tuple(map(int, k.split(":")))):
    if key in handled:
        continue
    s, a, w = key.split(":")
    previous = f"{s}:{a}:{int(w) - 1}"
    if previous not in tr:
        continue
    raw_relation = re.sub(r"[\[\]()]", "", en[previous]).lower().strip()
    relation = re.sub(r"^and ", "", raw_relation)
    copular = bool(re.match(r"^(?:is|are|was|were|will be|am) ", relation))
    relation = re.sub(r"^(?:is|are|was|were|will be|am) ", "", relation)
    relation = re.sub(r"^(?:surely|even|out) ", "", relation)
    relation = {"in to": "into"}.get(relation, relation)
    if relation not in supported:
        continue
    original = tr[previous]
    if normalize(en[previous]) == normalize(en[key]):
        continue
    surface, flat, indexes = flat_surface(original)
    if not flat.strip() or original.count("(") != original.count(")"):
        continue
    core = flat.rstrip()
    if lower(core) == "riba":
        continue
    particle = re.search(r"\s+(?:de|da|ise)$", core)
    if particle:
        core = core[:particle.start()]
    temporal = re.search(r"\s+(?:önce|sonra)\w*$", core)
    internal_from = relation == "from" and normalize(en[key]).startswith(("before", "after")) and temporal
    postposition = relation in {"before", "after"} and temporal
    if temporal:
        core = core[:temporal.start()]
    copula = ""
    adjectival = ""
    if core.endswith("ki") and any(core[:-2].endswith(suffix) for values in endings.values() for suffix in values if len(suffix) > 1):
        adjectival = "ki"
        core = core[:-2]
    match = re.search(r"(?:dır|dir|dur|dür|tır|tir|tur|tür|sınız|siniz|sunuz|sünüz|sın|sin|sun|sün|ım|im|um|üm)$", core)
    if match:
        # A proposed copula must follow an overt case ending, not a noun stem.
        if any(core[:match.start()].endswith(suffix) for values in endings.values() for suffix in values if len(suffix) > 1):
            copula = match.group()
            core = core[:match.start()]
    candidates = []
    for case, suffixes in endings.items():
        for suffix in suffixes:
            if not lower(core).endswith(suffix):
                continue
            boundary = len(core) - len(suffix)
            if boundary and core[boundary - 1] in "'’":
                boundary -= 1
            base = core[:boundary]
            if len(base.strip()) < 2 and lower(base.strip()) != "o":
                continue
            witnessed = lower(base.strip()) in lexicon[normalize(en[key])]
            if not witnessed and not (case in supported[relation] and ("(" in original or temporal or particle or copula or adjectival or relation in {"before", "after"})):
                continue
            if base.rstrip().endswith(("d", "t")) and case == "dative" and not witnessed:
                continue
            if suffix.startswith("n") and lower(base.rstrip()[-1]) not in "aeıioöuü":
                continue
            candidates.append({"case": case, "boundary": boundary, "base": base, "suffix": core[boundary:], "witnessed": witnessed})
    if not candidates:
        continue
    candidates.sort(key=lambda c: (not c["witnessed"], c["case"] not in supported[relation], -len(c["suffix"])))
    chosen = candidates[0]
    same_case = [c for c in candidates if c["case"] == chosen["case"]]
    for candidate in same_case:
        if lower(candidate["base"].strip().split()[-1]) in nouns_n:
            chosen = candidate
            break
    else:
        if re.search(r"\b(your|yourself|you)\b", en[key], re.I) and not internal_from:
            choices = [c for c in same_case if c["base"].endswith("n") and not c["suffix"].lstrip("'’").startswith("n")]
            if choices:
                chosen = choices[0]
        elif chosen["suffix"].lstrip("'’").startswith("n") and chosen["base"].rstrip()[-1] in "aeoö" and lower(chosen["base"].strip()) not in {"o", "bu", "şu"} and chosen["case"] in {"ablative", "locative"}:
            choices = [c for c in same_case if c["base"] == chosen["base"] + "n"]
            if choices:
                chosen = choices[0]
    if internal_from and chosen["case"] != "ablative":
        continue
    if postposition and chosen["case"] != "ablative":
        continue
    # An observed alternate case is a review candidate, not proof that its
    # suffix translates the English preposition in this particular ayah.
    if chosen["case"] not in supported[relation]:
        continue
    if key in {"2:217:3", "17:99:11"}:
        continue
    spans = [(chosen["boundary"], len(core))]
    if adjectival:
        spans.append((len(core), len(core) + len(adjectival)))
    if copular and copula:
        spans.append((len(core), len(core) + len(copula)))
    if postposition:
        spans.append((temporal.start(), temporal.end()))
    if flat.startswith("ve ") and raw_relation.startswith("and "):
        spans.append((0, 2))
    parts = make_parts(surface, [map_span(start, end, indexes, surface) for start, end in spans])
    if original == "şeytan(ın şerri)nden":
        parts = [{"text": "şeytan[ın şerri]", "role": "content"}, {"text": "nden", "role": "relation"}]
    plans.append({"relation_key": previous, "content_key": key, "relation_english": en[previous], "content_english": en[key],
                  "original_turkish": original, "parts": parts, "case": chosen["case"],
                  "lexical_evidence": chosen["witnessed"], "status": "proposed",
                  "reason": "Annotated/internal case construction or an alternate Turkish case with local lexical evidence."})
(ROOT / "reports/case-supplement-plan.json").write_text(json.dumps(plans, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Additional case constructions:", len(plans))
