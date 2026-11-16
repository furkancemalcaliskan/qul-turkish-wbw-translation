"""Propose clause and copula boundaries for review, without editing sources."""
import json
import re
from pathlib import Path
from alignment_common import load_baseline, flat_surface, map_span

ROOT = Path(__file__).resolve().parents[1]
en, tr = load_baseline()
relative_sources = {
    "that", "what", "which", "who", "whom", "those who", "those whom", "the one who", "is the one who",
    "of what", "from what", "for what", "in what", "to what", "with what", "about what", "above what",
    "that not", "lest", "when", "while", "before", "after", "of that which", "that which", "what not", "to", "whatever", "whoever",
}
blocked = ("insan", "zaman", "mekan", "mekân", "şeytan", "rahman", "hayvan", "kervan", "oğlan",
           "namaz", "iman", "sadık", "sandık", "sandığ", "artık", "nimet", "rahmet", "kıyamet", "ümmet",
           "ganimet", "hükme", "hükmü", "hizmet", "hikmet", "merhamet", "kıymet", "tamam", "sermaye",
           "imkan", "imkân", "kimse", "temas", "çevre", "kusur", "iyilik", "neden",
           "neredeyse", "zaten", "hemen", "bazen", "öğlen", "iken", "evren", "düşman", "nişan", "sultan", "hükümran", "önce", "sonra")
nominal = re.compile(r"[dt][ıiuü][kğ]|[ae]c[ae][kğ]|m[ae][kğ]|m[ae]")
participle = re.compile(r"[ae]n")
conditional = re.compile(r"s[ae](?=n|m|l|$)")
plans = []
infinitive_heads = {
    "set", "be", "ask", "render", "marry", "accept", "lighten", "go", "reject", "mislead", "destroy", "afflict",
    "cause", "believe", "send", "drive", "justify", "deceive", "extinguish", "strive", "punish", "purify", "advise",
    "let", "hinder", "join", "offer", "collapse", "scale", "worship", "come", "assert", "take", "remember", "bestow",
    "strike", "make", "exchange", "bear", "carry", "get", "change", "eat", "pass", "proceed", "return", "feed", "complete", "do",
}

def make_parts(text, spans):
    mask = [False] * len(text)
    for start, end in spans:
        mask[start:end] = [True] * (end - start)
    parts = []
    for char, primary in zip(text, mask):
        role = "relation" if primary else "content"
        if parts and parts[-1]["role"] == role:
            parts[-1]["text"] += char
        else:
            parts.append({"text": char, "role": role})
    return parts

for key in sorted(en.keys() - tr.keys(), key=lambda k: tuple(map(int, k.split(":")))):
    s, a, w = key.split(":")
    previous = f"{s}:{a}:{int(w) - 1}"
    if previous not in tr:
        continue
    source_original = re.sub(r"[\[\]()]", "", en[previous]).lower().strip()
    source = re.sub(r"^and ", "", source_original)
    if source not in {"is the one who", "the one who"}:
        source = re.sub(r"^(?:is|are|was|were|will be) (?=what|that|who)", "", source)
    source = {"whatever": "what", "whoever": "who"}.get(source, source)
    if source == "to":
        lexical = re.sub(r"[\[\]()]", "", en[key]).lower().strip()
        if lexical.split()[0] not in infinitive_heads:
            continue
    original = tr[previous]
    surface, text, indexes = flat_surface(original)
    spans = []
    kind = None
    if source in relative_sources:
        options = []
        for word in re.finditer(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû]+", text):
            value = word.group().lower()
            if value.startswith(blocked):
                if not (value.startswith(("tamamla", "selamla")) or (value.startswith("sandığ") and re.search(r"claim|think|assum|suppos", en[key], re.I))):
                    continue
            markers = [m for m in nominal.finditer(value) if m.start() >= 2]
            overt = [m for m in markers if m.group().startswith(("d", "t")) or "c" in m.group()]
            overt = [m for m in overt if not (m.end() == len(value) and m.group().startswith(("d", "t")))]
            overt = [m for m in overt if not ("c" in m.group() and m.group().endswith("k") and re.match(r"s[ıiuü]n", value[m.end():]))]
            if overt:
                markers = [overt[0]]
            else:
                markers = [m for m in markers if m.group().startswith("m") and (
                    len(m.group()) > 2 or re.match(r"^(?:$|[sn][ıiuüae]|[ıiuü]|n$|m$|m[ıiuü]z|lar|ler|y[aeıiuü]|[dt][ae]n|[dt][ae]|ğ)", value[m.end():])
                )]
                infinitives = [m for m in markers if len(m.group()) == 3 and m.group().startswith("m")]
                if infinitives:
                    markers = [infinitives[-1]]
            # Prefer an overt participle for person/thing relative pronouns.
            relative = []
            for m in participle.finditer(value):
                if m.start() < 2:
                    continue
                stem = value[:m.start()]
                remaining = value[m.end():]
                if stem.endswith("m") and stem not in {"em", "göm", "yum", "um"}:
                    continue
                if value.endswith("ken") or not re.match(r"^(?:$|lar|ler|[ıiuü](?:$|n|m|z|y|d|t)|n[ıiuüae]|[ae]$|[dt]|s[ıiuü]n)", remaining):
                    continue
                if stem.endswith("d") and not stem.endswith(("ed", "gid")):
                    continue
                if stem.endswith("t") and not re.search(r"(?:[aeıioöuü]t|[rl]t|yont)$", stem):
                    continue
                relative.append(m)
            negative_participle = markers and markers[0].group() in {"ma", "me"} and re.match(r"y[ae]n", value[markers[0].end():])
            prefer_relative = source in {"who", "whom", "those who", "those whom", "the one who", "is the one who", "which", "what"} and not overt
            if (not markers or negative_participle or prefer_relative) and source in {"who", "whom", "those who", "those whom", "the one who", "is the one who", "which", "what", "that"} and relative:
                selected = relative[-1]
                if source != "that" or re.fullmatch(r"(?:lar|ler)?[ıiuüae]?", value[selected.end():]):
                    markers = [selected]
            if not markers:
                markers = [m for m in conditional.finditer(value) if m.start() >= 2]
            condition = re.search(r"s[ae](?=(?:n[ıiuü]z|lar|ler|m|n)?$)", value)
            if condition and (condition.start() >= 3 or value[:condition.start()] in {"ol", "et", "de"}) and source not in {"who", "whom", "those who", "those whom", "the one who", "is the one who", "which"}:
                markers = [condition]
            if markers:
                marker = markers[0]
                priority = 3 if overt else (2 if marker.group().startswith("m") else 1)
                options.append((priority, word, marker))
            if source in {"when", "while"}:
                temporal = re.search(r"(?:[ıiuü]nc[ae]|ken)$", value)
                if temporal and temporal.start() >= 2:
                    options.append((4, word, temporal))
        if options:
            _, word, marker = max(options, key=lambda option: (option[0], option[1].start()))
            start, end = word.start() + marker.start(), word.start() + marker.end()
            if marker.group()[0] in "ae" and start >= 2 and text[start - 1] == "y" and text[start - 2] in "aeıioöuü" and word.group()[:marker.start()] not in {"yay", "say", "koy", "duy", "uy", "oy", "kay", "soy", "doy"}:
                start -= 1
            if source in {"who", "whom", "those who", "those whom", "the one who", "is the one who"}:
                end = word.end()
            spans.append((start, end))
            if source.split()[0] in {"of", "from", "for", "in", "to", "with", "about", "above"}:
                suffix = re.search(r"(?:n[dt][ae]n|[dt][ae]n|n[dt][ae]|[dt][ae]|y[ae]|n[ae])$", text)
                if suffix and suffix.start() >= end:
                    spans.append((suffix.start(), len(text)))
            if source == "to":
                match = re.search(r"\biçin\b", text)
                if match:
                    spans.append((match.start(), match.end()))
            for match in re.finditer(r"\b(?:zaman|sonra|önce|için)\b", text):
                if source in {"when", "before", "after", "lest"}:
                    spans.append((match.start(), match.end()))
            kind = "clause_link"
    elif source in {"is", "are", "was", "were", "am", "will be"}:
        suffix = re.search(r"(?:dır|dir|dur|dür|tır|tir|tur|tür)$", text)
        if suffix and suffix.start() >= 2:
            spans.append((suffix.start(), suffix.end()))
            kind = "copula"
    if source not in relative_sources and source not in {"is", "are", "was", "were", "am", "will be"}:
        continue
    reason = None
    if f"{s}:{a}:{int(w) + 1}" in en and f"{s}:{a}:{int(w) + 1}" not in tr:
        reason = "Consecutive missing keys require multi-entry review."
    elif not spans:
        reason = "No supported overt clause-link or copula suffix identified."
    elif source == re.sub(r"[\[\]()]", "", en[key]).lower().strip():
        reason = "Repeated English glosses require a separate semantic alignment decision."
    elif source in {"is", "are", "was", "were", "am", "will be"} and re.sub(r"[\[\]()]", "", en[key]).lower().strip() in {"from", "of", "over", "on", "near", "in", "to"}:
        reason = "Two grammatical entries sharing a contextual noun require multi-part review."
    if text.startswith("ve ") and source_original.startswith("and ") and spans:
        spans.append((0, 2))
    if key == "4:23:27":
        reason = "The Turkish guardianship and relations clauses are assigned to swapped source positions; a suffix-only edit would preserve the wrong alignment."
    plans.append({"relation_key": previous, "content_key": key,
                  "relation_english": en[previous], "content_english": en[key],
                  "original_turkish": original, "parts": make_parts(surface, [map_span(start, end, indexes, surface) for start, end in spans]),
                  "case": kind or "unidentified", "status": "deferred" if reason else "proposed", "reason": reason})
(ROOT / "reports/clause-alignment-plan.json").write_text(json.dumps(plans, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Clause/copula candidates:", len(plans), "Proposed:", sum(r["status"] == "proposed" for r in plans))
