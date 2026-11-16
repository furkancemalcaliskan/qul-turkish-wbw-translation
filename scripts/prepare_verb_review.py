"""Propose negation spans for local review; do not modify translation files."""
import json
import re
from pathlib import Path
from alignment_common import load_baseline, flat_surface, map_span, make_parts

ROOT = Path(__file__).resolve().parents[1]
en, tr = load_baseline()
tail = re.compile(r"^(?:$|z|[dt][ıiuü]|[dt][ıiuü]ğ|y[ae]c|yor|y[ıiuü]|y[ae]|s[ae]|m$|m[ae]|m[ıiuü]ş|s[ıiuü]n|d[ae]n|[dt][ae]n)")
rows = []
for key in sorted(en.keys() - tr.keys(), key=lambda k: tuple(map(int, k.split(":")))):
    s, a, w = key.split(":")
    previous = f"{s}:{a}:{int(w) - 1}"
    if previous not in tr or not re.search(r"\bnot\b|\bnever\b|\bwithout\b", en[previous], re.I):
        continue
    original = tr[previous]
    surface, text, indexes = flat_surface(original)
    spans = []
    for word in re.finditer(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû]+", text):
        value = word.group().lower()
        if value.startswith(("namaz", "zaman", "tamam", "makam", "imam", "hamam", "kelam", "selam",
                             "rahmet", "nimet", "kıyamet", "hikmet", "hizmet", "hükümet", "ümmet", "kıymet", "ismet", "merhamet", "sermaye")):
            if not value.startswith(("selamla", "tamamla")):
                continue
        if value == "başıma":
            continue
        if value.startswith("değil"):
            spans.append((word.start(), word.start() + 5, "negative_word"))
            continue
        if value.startswith("yok") and value in {"yok", "yoktur", "yoktu", "yoksa"}:
            if not re.match(r"\s+(?:et|ol)", text[word.end():]):
                spans.append((word.start(), word.start() + 3, "negative_word"))
            continue
        options = []
        for match in re.finditer(r"ma|me|mı|mi|mu|mü", value):
            if value.startswith(("hükmet", "hükmed")) and match.start() == 3:
                continue
            if match.group() not in {"ma", "me"} and not re.match(r"y(?:or|[ae]c)", value[match.end():]):
                continue
            if match.start() >= 2 and tail.match(value[match.end():]):
                end = match.end() + (1 if value[match.end():].startswith("z") else 0)
                options.append((word.start() + match.start(), word.start() + end, "negative_suffix"))
        if options:
            selected = options[0]
            if "without" in en[previous].lower() and re.search(r"m[ae][dt][ae]n$", value):
                selected = (selected[0], word.end(), selected[2])
            spans.append(selected)
        elif re.search(r"s[ıiuü]z(?:[ıiuü]n|c[ae])?$", value):
            match = re.search(r"s[ıiuü]z(?:[ıiuü]n|c[ae])?$", value)
            if match.start() >= 2:
                spans.append((word.start() + match.start(), word.end(), "privative_suffix"))
    reason = None
    if f"{s}:{a}:{int(w) + 1}" in en and f"{s}:{a}:{int(w) + 1}" not in tr:
        reason = "Consecutive missing keys require multi-entry review."
    elif not spans:
        reason = "No supported negative suffix or negative word identified."
    elif len(spans) != 1:
        reason = "Multiple possible negative spans require individual review."
    elif previous == "6:48:1":
        reason = "The existing form 'biz gönderimeyi' needs a spelling/meaning review before segmentation."
    elif any(text[start:end] == "yok" for start, end, kind in spans) and not re.search(r"yok(?:tur|tu)\b", text):
        reason = "Existence is encoded lexically, without an independently identifiable suffix."
    # Conjunctions and explicit negative adverbs are also contributions of the
    # source function entry, rather than of the adjacent lexical verb.
    for match in re.finditer(r"\b(?:ve|asla|hiç|sakın)\b", text, re.I):
        spans.append((match.start(), match.end(), "function_word"))
    spans.sort()
    parts = make_parts(surface, [map_span(start, end, indexes, surface) for start, end, kind in spans])
    rows.append({"relation_key": previous, "content_key": key,
                 "relation_english": en[previous], "content_english": en[key],
                 "original_turkish": original, "parts": parts,
                 "case": "negation", "status": "deferred" if reason else "proposed",
                 "reason": reason})
(ROOT / "reports/negation-alignment-plan.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Negation candidates:", len(rows), "Proposed:", sum(r["status"] == "proposed" for r in rows))
