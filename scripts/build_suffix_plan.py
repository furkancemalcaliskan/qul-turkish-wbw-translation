"""Prepare explicit, reviewable case-ending edits; never edit translations here."""
import json
import re
from collections import Counter
from pathlib import Path

from prepare_suffix_review import ROOT, en, tr, lower, normalize_english

rows = json.loads((ROOT / "reports/suffix-candidates.json").read_text(encoding="utf-8"))
# These endings belong to the lexical noun, not to a connector consonant.
n_final_nouns = {"din", "kin", "bin", "zindan", "insan", "iman", "kurban", "şeytan",
                 "rahman", "zaman", "hayvan", "kur'an", "kuran", "zeytin", "metin",
                 "emin", "miskin", "mü'min", "mümin", "engin", "hazin", "fir'avn", "irin", "gün", "koyun",
                 "kadın", "ekin", "beyin", "zemin", "yakın", "yemin", "hüzün", "dün", "bugün", "bütün", "yakîn", "yakin", "cin"}
non_suffix_texts = {"bir süre", "ile", "onlar ansızın", "çok çetin", "diye", "onun söyleyesin", "hayat boyunca"}
ambiguous_texts = {
    "onlar zaten fitneye", "iki gün içinde", "taşkınlıkları içinde", "bir kayanın içinde",
    "bir rahmetin içine", "ülkeler arasında", "onları oldukları yerde", "onları arkalarından",
    "düşman karşısında", "onun canından önce", "bir nutfe(sperm)den", "zalimlerden olursun", "teslim olmakla",
}
generic_targets = {"every", "all", "are every", "to", "that", "from", "of", "with", "was in"}
operations = []
deferred = []

def parts_for(base, suffix):
    if base.startswith("ve "):
        return [{"text": "ve ", "role": "relation"}, {"text": base[3:], "role": "content"},
                {"text": suffix, "role": "relation"}]
    return [{"text": base, "role": "content"}, {"text": suffix, "role": "relation"}]

for row in rows:
    key = row["missing_key"]
    s, a, w = key.split(":")
    text = row["turkish"]
    candidates = row["candidates"]
    reason = None
    target = normalize_english(row["missing_english"])
    if f"{s}:{a}:{int(w) + 1}" in en and f"{s}:{a}:{int(w) + 1}" not in tr:
        reason = "Consecutive gaps require multi-entry review."
    elif text in non_suffix_texts or text.endswith(" göre") or text.endswith(" sürece"):
        reason = "An apparent final letter sequence is not an identified case ending."
    elif text in ambiguous_texts or any(c in text for c in "()[]"):
        reason = "Existing annotation or a broader phrase requires separate segmentation review."
    elif target in generic_targets:
        reason = "The source target may cover only part of a broader phrase."
    elif row["relation"] == "about" and not any(c["case"] == "ablative" for c in candidates):
        reason = "The proposed ending does not establish the English relation."
    elif not candidates:
        reason = "No supported case-ending boundary identified."
    if reason:
        deferred.append({**row, "reason": reason})
        continue
    evidence = [c for c in candidates if c["lexical_evidence"]]
    chosen = (evidence or candidates)[0]
    # Buffer n belongs with the ending in third-person possessives; in second-
    # person singular forms, the n is part of the possessed noun instead.
    same_case = [c for c in candidates if c["case"] == chosen["case"]]
    for candidate in same_case:
        last = lower(candidate["base"].split()[-1]).strip("'’")
        if last in n_final_nouns:
            chosen = candidate
            break
    else:
        if re.search(r"\b(your|yourself|you)\b", row["missing_english"].lower()) or text.startswith("senin "):
            alternatives = [c for c in same_case if c["base"].endswith("n") and c["suffix"][0] != "n"]
            if alternatives:
                chosen = alternatives[0]
        elif re.search(r"\b(his|her|its|their)\b", row["missing_english"].lower()) or target in {
            "way", "path", "bounty", "favor", "breasts", "people", "punishment", "day", "fire", "book", "tree", "home", "earth"
        }:
            alternatives = [c for c in same_case if c["suffix"].startswith("n") and c["base"][-1] in "ıiuü"]
            if alternatives:
                chosen = alternatives[0]
    # A longer connector ending after a/e generally truncates an n-final noun
    # or participle (e.g. eden + den), rather than revealing a connector n.
    if chosen["case"] in {"ablative", "locative"} and chosen["suffix"].lstrip("'’").startswith("n") and chosen["base"][-1].lower() in "aeoö":
        if lower(chosen["base"].split()[-1]) not in {"o", "bu", "şu"}:
            alternatives = [c for c in same_case if c["base"] == chosen["base"] + "n"]
            if alternatives:
                chosen = alternatives[0]
    if not chosen["lexical_evidence"] and chosen["case"] == "dative" and chosen["suffix"] in {"a", "e"} and chosen["base"].endswith(("d", "t")):
        deferred.append({**row, "reason": "Final letters may instead be a locative ending; do not truncate the noun."})
        continue
    if chosen["case"] == "dative" and chosen["suffix"] in {"a", "e"} and chosen["base"].endswith(("ll", "yl", "nl", "rl", "tl")):
        deferred.append({**row, "reason": "An instrumental ending may have been mistaken for a dative ending."})
        continue
    if text.endswith((" de", " da", " ise")):
        deferred.append({**row, "reason": "A trailing particle requires its own contextual span."})
        continue
    if text in {"Rabbin tarafından", "savaşın şiddetinden"}:
        boundary = max(text.rfind("ndan"), text.rfind("nden"))
        assert boundary >= 0
        chosen = {**chosen, "base": text[:boundary], "suffix": text[boundary:]}
    if text == "bir suyun":
        chosen = {**chosen, "base": "bir su", "suffix": "yun"}
    if text == "altından" and target in {"gold", "ornament"}:
        chosen = {**chosen, "base": "altın", "suffix": "dan"}
    # Longer n-endings must follow a vowel. This also rejects truncated roots.
    if chosen["suffix"].lstrip("'’").startswith("n") and chosen["base"][-1].lower() not in "aeıioöuü":
        deferred.append({**row, "reason": "Connector boundary needs individual review."})
        continue
    if len(chosen["base"].split()[-1]) < 2 and lower(chosen["base"]) != "o":
        deferred.append({**row, "reason": "Proposed noun fragment is too short to establish alignment."})
        continue
    operations.append({
        "relation_key": row["previous_key"], "content_key": key,
        "relation_english": row["previous_english"], "content_english": row["missing_english"],
        "original_turkish": text, "parts": parts_for(chosen["base"], chosen["suffix"]),
        "case": chosen["case"], "lexical_evidence": chosen["lexical_evidence"],
        "status": "proposed",
    })
plan = {"scope": "Noun case endings and case endings on nominalized expressions; local parallel-file review.",
        "operations": operations, "deferred_preposition_candidates": deferred}
path = ROOT / "reports/suffix-alignment-plan.json"
path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Proposed:", len(operations), "Deferred:", len(deferred))
print("By case:", dict(Counter(r["case"] for r in operations)))
