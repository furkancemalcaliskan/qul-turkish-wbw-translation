"""Apply reviewed spelling rules while retaining contextual parentheses."""
import difflib
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from review_turkish_spelling import CANDIDATES, TOKEN
from spelling_construction_cases import construction_cases

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "c9dac12"
PROPER_CASE = re.compile(r"(Musa|İsa|Meryem|İbrahim|İsmail|İshak|Nuh|Yusuf|Yakub|Yakup|Süleyman|Davut|Davud|İsrail|Allah|Harun|Lut|Adem|Salih|Hud|Şuayb|Şuayip|Yunus|İdris|Eyyub|Eyyup|Zekeriyya|Yahya|İlyas|Mikail|Cibril)(a|e|ı|i|u|ü|ya|ye|yı|yi|yu|yü|ın|in|un|ün|nın|nin|nun|nün|dan|den|tan|ten|da|de|ta|te|la|le)")
ALIGNMENT_REPAIRS = {
    "79:40:8": ("0", "(kötü hevesler)den"),
    "79:40:9": ("kötü heves(ler)-", "kötü hevesler(den)"),
    "46:8:10": ("Allah-;-tan", "(Allah)'tan"),
    "46:8:11": ("Allah-;", "Allah('tan)"),
}
FAMILIES = [
    ("Alah", "Allah", "Restore the missing consonant in Allah and its inflected forms."),
    ("Allahınki", "Allah'ınki", "Separate the proper name and its genitive ending with an apostrophe."),
    ("herşey", "her şey", "Separate şey from her, including inflected forms."),
    ("Rabbler", "Rabler", "Remove the duplicated stem consonant before the plural suffix."),
    ("kalbl", "kalpl", "Use the unvoiced stem consonant before a consonant-initial suffix."),
    ("meyva", "meyve", "Use the standard spelling meyve."),
    ("tadd", "tatt", "Use the unvoiced consonant cluster in the tat- verb family."),
    ("tadmış", "tatmış", "Retain the unvoiced stem consonant before -mış."),
    ("azabed", "azap ed", "Write azap and the auxiliary separately; restore the noun spelling."),
    ("azabet", "azap et", "Write azap and the auxiliary separately; restore the noun spelling."),
    ("cihaded", "cihat ed", "Write cihat and the auxiliary separately; restore the noun spelling."),
    ("cihadet", "cihat et", "Write cihat and the auxiliary separately; restore the noun spelling."),
    ("ayırded", "ayırt ed", "Use the standard ayırt etmek compound spelling."),
    ("ayırdet", "ayırt et", "Use the standard ayırt etmek compound spelling."),
    ("andlaş", "antlaş", "Use the standard antlaşma stem spelling."),
    ("andlar", "antlar", "Use the unvoiced consonant of ant before the plural suffix."),
    ("azabl", "azapl", "Use the unvoiced consonant of azap before a consonant-initial suffix."),
    ("nisbet", "nispet", "Use the standard nispet spelling."),
    ("tehdidet", "tehdit et", "Write the auxiliary separately and restore tehdit."),
    ("tehdided", "tehdit ed", "Write the auxiliary separately and restore tehdit."),
    ("lutuf", "lütuf", "Use the standard front-rounded initial vowel in lütuf."),
    ("lutf", "lütf", "Use the standard front-rounded initial vowel in the lütuf family."),
    ("Lutuf", "Lütuf", "Use the standard front-rounded initial vowel in lütuf."),
    ("azadet", "azat et", "Write azat and the auxiliary separately."),
    ("icadet", "icat et", "Write icat and the auxiliary separately."),
]

def read_baseline(name):
    return subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=ROOT)

def edit_surface(raw, start, end, replacement):
    """Edit surface characters, leaving every alignment delimiter in place."""
    positions = [i for i, char in enumerate(raw) if char not in "()"]
    surface = "".join(raw[i] for i in positions)
    old = surface[start:end]
    edits = []
    for kind, a, b, c, d in difflib.SequenceMatcher(None, old, replacement, autojunk=False).get_opcodes():
        if kind == "equal":
            continue
        if b-a == d-c:
            edits.extend((positions[start+a+i], positions[start+a+i]+1, char)
                         for i, char in enumerate(replacement[c:d]))
            continue
        # Keep parentheses between edited characters instead of replacing a raw span.
        indexes = positions[start+a:start+b]
        anchor = positions[start+a] if start+a < len(positions) else len(raw)
        if a == b and replacement[c:d].isspace():
            # A new word-boundary space belongs before an opening delimiter,
            # rather than becoming padding inside the contextual phrase.
            while anchor > 0 and raw[anchor-1] == "(":
                anchor -= 1
        edits.extend((index, index+1, "") for index in indexes)
        edits.append((anchor, anchor, replacement[c:d]))
    # At the same position, remove the old character before inserting its replacement.
    for a, b, value in sorted(edits, key=lambda item: (item[0], item[1]), reverse=True):
        raw = raw[:a] + value + raw[b:]
    return raw

def correct(raw):
    surface = raw.replace("(", "").replace(")", "")
    changes = []
    for match in TOKEN.finditer(surface):
        word = match[0]
        replacement = CANDIDATES.get(word, word)
        reason = "Correct a reviewed spelling, word boundary, or malformed inflection."
        for old, new, explanation in FAMILIES:
            if word.startswith(old):
                suffix = word[len(old):]
                if old == "meyva":
                    suffix = suffix.translate(str.maketrans("aı", "ei"))
                replacement = new + suffix
                reason = explanation
                break
        if word == "lutfi":
            replacement = "lütfu"
        if replacement == word and word.startswith("tad") and (len(word) == 3 or word[3] not in "aeıioöuü"):
            replacement = "tat" + word[3:]
            reason = "Use tat- at word end and before a consonant; preserve tad- before vowels."
        proper = PROPER_CASE.fullmatch(word)
        if proper:
            ending = proper[2]
            if proper[1] == "Allah" and ending == "dan":
                ending = "tan"
            replacement = proper[1] + "'" + ending
            reason = "Separate a reviewed proper name from its case ending with an apostrophe."
        for stem, corrected in [("şahid", "şahit"), ("şehid", "şehit"), ("mücahid", "mücahit"), ("evlad", "evlat"), ("mescid", "mescit"), ("tehdid", "tehdit")]:
            if word.startswith(stem):
                suffix = word[len(stem):]
                if not suffix or suffix[0] not in "aeıioöuü":
                    # Bracketed elisions require a separate construction review.
                    if match.end() < len(surface) and surface[match.end()] == "[":
                        continue
                    replacement = corrected + ("t"+suffix[1:] if suffix.startswith("d") else suffix)
                    reason = "Use the standard unvoiced stem before a consonant or at word end; assimilate a following d-initial suffix."
                break
        if replacement != word:
            changes.append((match.start(), match.end(), replacement, word, reason))
    for start, end, replacement, _, _ in reversed(changes):
        raw = edit_surface(raw, start, end, replacement)
    notes = [{"before": old, "after": new, "reason": reason} for _, _, new, old, reason in changes]
    surface = raw.replace("(", "").replace(")", "")
    for match in reversed(list(re.finditer(r"\b(mı|mi|mu|mü) (dır|dir|dur|dür)\b", surface))):
        replacement = match[1] + match[2]
        raw = edit_surface(raw, match.start(), match.end(), replacement)
        notes.append({"before": match[0], "after": replacement, "reason": "Attach the copular ending to the question particle."})
    if raw == "kalplerinde-mı var?":
        raw = "kalplerinde mi var?"
        notes.append({"reason": "Separate the question particle and use front-vowel harmony."})
    surface = raw.replace("(", "").replace(")", "")
    question_forms = {
        "insanlar-mı": "insanlar mı", "kimseler-mı": "kimseler mi",
        "Zikir-mı": "Zikir mi", "bekliyorlar-mı": "bekliyorlar mı",
        "siz-misiniz": "siz misiniz", "siz-mısınız": "siz misiniz",
        "erkeklere-mi": "erkeklere mi", "şeylere-mi": "şeylere mi",
        "cezalandırılıyorsunuz-mi": "cezalandırılıyorsunuz mu",
        "bizim-mi": "bizim mi", "biz-miyiz": "biz miyiz", "Ba'l'e-mi": "Ba'l'e mi",
        "sizin -mı": "sizin mi", "kendilerinin -mı": "kendilerinin mi",
        "alt-üst": "altüst", "alış-verişi": "alışverişi",
        "ana-baba": "ana baba", "ana-babasını": "ana babasını",
        "anaya-babaya": "anaya babaya", "anana-babana": "anana babana",
        "anamı-babamı": "anamı babamı", "babamı-anamı": "babamı anamı",
        "ve -idiler": "ve idiler", "biz -imişiz": "biz imişiz",
        "pistir-ki": "pistir ki", "indirdik-ki": "indirdik ki",
        "ave ndolsun": "ve andolsun",
        "dedi di": "dedi ki",
    }
    phrase_edits = []
    for old, new in question_forms.items():
        phrase_edits.extend((m.start(), m.end(), new, old) for m in re.finditer(r"(?<!\w)"+re.escape(old)+r"(?!\w)", surface))
    for start, end, new, old in sorted(phrase_edits, reverse=True):
        raw = edit_surface(raw, start, end, new)
        notes.append({"before": old, "after": new, "reason": "Correct a reviewed question-particle boundary, vowel harmony, or compound-word boundary."})
    spaced = re.sub(r" {2,}", " ", raw).strip()
    if spaced != raw:
        notes.append({"reason": "Remove repeated or exterior whitespace."})
    raw = spaced
    for old, new in [("hiç bir", "hiçbir"), ("bir çok", "birçok")]:
        updated = re.sub(r"(?<!\w)"+old+r"(?!\w)", new, raw)
        if updated != raw:
            notes.append({"before": old, "after": new, "reason": "Use the standard indefinite modifier spelling."})
            raw = updated
    return raw, notes

def main():
    source = read_baseline("turkish-wbw-translation.json")
    en_bytes = read_baseline("english-wbw-translation.json")
    assert (ROOT / "english-wbw-translation.json").read_bytes() == en_bytes
    before = json.loads(source)
    en = json.loads(en_bytes)
    groups = construction_cases()
    construction_updates = {}
    for group in groups:
        assert group["before"] == {key: before[key] for key in group["members"]}
        for key in group["members"]:
            assert key not in construction_updates and key not in ALIGNMENT_REPAIRS
            construction_updates[key] = (group["after"][key], group["reason"])
    after = {}
    entries = []
    for key, value in before.items():
        corrected, notes = correct(value)
        if key in ALIGNMENT_REPAIRS:
            expected, corrected = ALIGNMENT_REPAIRS[key]
            assert value == expected
            source_verse = "79:40" if key.startswith("79:") else "46:8"
            chapter, verse = source_verse.split(":")
            notes.append({"category": "alignment_repair", "reason": f"Replace an inherited numeric placeholder or corrupted punctuation with complementary ablative displays. Arabic preposition and noun positions checked at https://corpus.quran.com/wordbyword.jsp?chapter={chapter}&verse={verse}."})
        if key in construction_updates:
            corrected, reason = construction_updates[key]
            notes.append({"category": "construction_repair", "reason": reason})
        after[key] = corrected
        if corrected != value:
            assert not re.fullmatch(r"\(\d+\)", en[key])
            if key not in ALIGNMENT_REPAIRS and key not in construction_updates:
                assert "".join(c for c in value if c in "()[]") == "".join(c for c in corrected if c in "()[]"), key
            assert "()" not in corrected or "()" in value, key
            entries.append({"key": key, "english": en[key], "before": value, "after": corrected, "changes": notes})
    output = (json.dumps(after, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    current = (ROOT / "turkish-wbw-translation.json").read_bytes()
    if current not in (source, output):
        previous = json.loads((ROOT / "reports/spelling-changes.json").read_text(encoding="utf-8"))
        assert previous["baseline"] == BASELINE
        recorded = dict(before)
        for entry in previous["entries"]:
            assert before[entry["key"]] == entry["before"]
            recorded[entry["key"]] = entry["after"]
        recorded_bytes = (json.dumps(recorded, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
        assert current == recorded_bytes, "Unexpected Turkish changes; review before applying."
        assert hashlib.sha256(current).hexdigest() == previous["summary"]["turkish_after_sha256"]
    report = {
        "baseline": BASELINE,
        "scope": "Corpus-wide mechanical scan and reviewed orthographic corrections; not exhaustive semantic or sentence-level grammar certification.",
        "summary": {"changed_entries": len(entries), "added_keys": 0, "removed_keys": 0,
                    "english_sha256": hashlib.sha256(en_bytes).hexdigest(),
                    "turkish_before_sha256": hashlib.sha256(source).hexdigest(),
                    "turkish_after_sha256": hashlib.sha256(output).hexdigest()},
        "entries": entries,
        "construction_groups": groups,
    }
    (ROOT / "reports/spelling-changes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if "--apply" in sys.argv:
        (ROOT / "turkish-wbw-translation.json").write_bytes(output)
    print(json.dumps(report["summary"], indent=2))

if __name__ == "__main__":
    main()
