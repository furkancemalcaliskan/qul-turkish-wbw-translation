"""Prepare/apply the first bounded Arabic-led review after commit 661144b."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from alignment_common import render
from audit_resources import MANIFEST, RESOURCES, inventory, read
from report_store import STATE, load, read_report, write_report

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "661144b"

def committed(name):
    return subprocess.check_output(["git", "show", f"{BASELINE}:{name}"], cwd=ROOT)

def write(name, value):
    assert name.startswith("reports/")
    write_report(Path(name).name, value)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if any(name != "semantic-review-001" for name in load(STATE)["batches"]):
        parser.error("Later semantic batches exist. This historical first-batch applier must not replace their state; run semantic_review.py to validate the full ledger.")
    original_hashes = read(MANIFEST)["files"]
    assert inventory() == original_hashes
    source = committed("turkish-wbw-translation.json")
    before = json.loads(source)
    english_raw = (RESOURCES / "english/english-wbw-translation.json").read_bytes()
    en = json.loads(english_raw)
    assert (ROOT / "english-wbw-translation.json").read_bytes() == committed("english-wbw-translation.json")
    ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
    groups = []

    def group(identifier, members, parts, reason):
        parts = [{"text": text, "role": role} for text, role in parts]
        groups.append({"id": identifier, "members": members, "before": {key: before[key] for key in members},
                       "parts": parts, "shared_expression": "".join(part["text"] for part in parts),
                       "after": {key: render(parts, key) for key in members}, "reason": reason,
                       "arabic": {key: ar[key]["text"] for key in members}, "english": {key: en[key] for key in members}})

    group("30:43-negated-return", ["30:43:10", "30:43:11", "30:43:12"],
          [("onun", "30:43:12"), (" ", "context"), ("geri çevrilmesi", "30:43:11"), (" ", "context"), ("yoktur", "30:43:10")],
          "Lahu is lam plus a masculine singular pronoun referring to the Day, not the ablative min at the next location. Express the nominal negation as onun geri çevrilmesi yoktur. Turkish uses a possessive nominal phrase for the Arabic pronominal complement. The adjacent min Allah displays remain unchanged; their broader interpretive attachment is not adjudicated here.")
    group("39:74-settling-predicate", ["39:74:9"], [("yerleşebiliriz", "39:74:9")],
          "Natabawwau is a first-person plural imperfect dwelling/settling predicate. Replace the inherited future relative participle with a finite Turkish predicate. The permissive possibility reading is supported by the English may settle and the following freedom to choose a place; this is a contextual Turkish rendering, not a claim that Arabic has a separate can morpheme.")
    group("39:74-partitive-location", ["39:74:10", "39:74:11", "39:74:12", "39:74:13"],
          [("cennet", "39:74:11"), ("in", "39:74:10"), (" ", "context"), ("dilediğimiz", "39:74:13"), (" ", "context"), ("yerinde", "39:74:12")],
          "Min al-jannati with haythu nashau locates the chosen dwelling within Paradise. Use the Turkish part-whole possessive construction cennetin dilediğimiz yerinde: min is represented contextually by the genitive -in, not a universally assigned -den. Retain the existing place and volition wording. This does not change the interpretation of the earlier al-ard / yurda entry.")
    group("2:16-relative-buyers", ["2:16:2", "2:16:3"],
          [("satın al", "2:16:3"), ("anlardır", "2:16:2")],
          "Alladhina is an overt plural relative pronoun. The finite satın aldılar failed to express the nominal relative predicate. Use satın alanlardır, exposing the Turkish relative/plural predicate ending. The Turkish -an relative construction can describe the completed purchase in context; it is not a present-tense reanalysis of Arabic ishtaraw.")
    group("2:16-negative-profit", ["2:16:6", "2:16:7"],
          [("böylece ", "2:16:6"), ("kâr et", "2:16:7"), ("me", "2:16:6"), ("di", "2:16:7")],
          "Fama supplies the connective and negation; rabihat supplies the past profit predicate. Redistribute the retained kâr etmedi phrase with its source roles and make the connective explicit.")
    group("2:16-past-guidance", ["2:16:9", "2:16:10", "2:16:11"],
          [("ve ", "2:16:9"), ("doğru yolu bulmuş", "2:16:11"), (" ", "context"), ("değil", "2:16:9"), ("lerdi", "2:16:10")],
          "Wama negates the plural past copular construction kanu muhtadina. Express that construction as ve doğru yolu bulmuş değillerdi, preserving the guidance meaning without inventing an ability-negation suffix or an independent ablative.")
    group("2:17-illumination-past", ["2:17:7"], [("aydınlattı", "2:17:7")],
          "Adaat is a perfect verb in the falamma narrative clause. Replace the inherited generic present aydınlatır with past aydınlattı; keep the explicit ne zaman ki at 2:17:6.")
    group("2:17-relative-surroundings", ["2:17:8", "2:17:9"],
          [("çevresinde", "2:17:9"), ("kileri", "2:17:8")],
          "Ma is a relative pronoun and hawlahu is a location with a third-person possessor. Use çevresindekileri to express what was around him, exposing the nominalized relative/object ending instead of marking the entire old çevresini as context-only.")
    group("2:17-negative-sight", ["2:17:16", "2:17:17"],
          [("gör", "2:17:17"), ("mez", "2:17:16"), ("ler", "2:17:17")],
          "La negates a plural imperfect seeing predicate, yubṣiruna. Use görmezler rather than the inherited nominal değildir / görenlerden sequence. Do not introduce the additional inability morpheme of göremezler as if it were overt in the source verb.")

    decisions = [
        {"ayah": "30:43", "status": "revised", "resolved_construction_keys": ["30:43:12"],
         "sources": ["https://corpus.quran.com/wordbyword.jsp?chapter=30&verse=43"],
         "limit": "Only the negated return clause is revised; the attachment of min Allah is not uniquely adjudicated."},
        {"ayah": "39:74", "status": "revised", "resolved_construction_keys": ["39:74:10"],
         "sources": ["https://corpus.quran.com/wordbyword.jsp?chapter=39&verse=74", "https://acikkaynakkuran.diyanet.gov.tr/quran/surah/39"],
         "limit": "The selected Turkish partitive/genitive rendering is contextual, not a universal translation of min. Other translations can express the same local relation with a locative construction."},
        {"ayah": "2:16", "status": "revised", "resolved_semantic_keys": ["2:16:2"],
         "sources": ["https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=16", "https://kuran.diyanet.gov.tr/mushaf/kuran-meal-1/bakara-suresi-2/ayet-10/kuran-yolu-meali-5"],
         "limit": "Reviewed the relative buyer predicate and two negative predicates; not a certification of every possible lexical preference in the ayah."},
        {"ayah": "2:17", "status": "revised", "resolved_semantic_keys": ["2:17:8"],
         "sources": ["https://corpus.quran.com/wordbyword.jsp?chapter=2&verse=17"],
         "limit": "Giderdi at 2:17:10 is retained: it can be the past of gidermek, expressing removal, rather than an erroneous translation as went."},
    ]
    follow_up = [
        {"ayah": "2:23", "status": "inspected_not_finalized", "keys": ["2:23:5", "2:23:6", "2:23:7", "2:23:8", "2:23:11", "2:23:15", "2:23:16", "2:23:17"],
         "reason": "Read the local Arabic and both translations. The standalone min before mithlihi may be implicit in the Turkish comparison and must not be automatically expanded as an ablative. The adjacent inherited sana and kulumuz [Muhammed]e construction, plus başka(dan), need their own source-role review before this ayah is marked resolved."},
        {"ayah": "2:36", "status": "inspected_not_finalized", "keys": ["2:36:16", "2:36:18", "2:36:19"],
         "reason": "Read the local Arabic and both translations. Review the nominal dwelling expression mustaqarr and the endpoint relation ila hin together; a bare bir süre may hide the boundary/until contribution. No change is applied to this ayah in this bounded batch."},
    ]
    after = dict(before)
    seen = set()
    for item in groups:
        assert not seen.intersection(item["members"])
        seen.update(item["members"])
        assert all(part["role"] in [*item["members"], "context"] for part in item["parts"])
        assert all(item["after"][key] != before[key] for key in item["members"])
        after.update(item["after"])
    output = (json.dumps(after, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    assert (ROOT / "turkish-wbw-translation.json").read_bytes() in (source, output), "Unexpected Turkish edits."
    contexts = {}
    for ayah in ["30:43", "39:74", "2:16", "2:17", "2:23", "2:36"]:
        contexts[ayah] = [{"location": key, "arabic": value["text"], "english": en.get(key), "turkish_before": before.get(key)}
                          for key, value in ar.items() if key.rsplit(":", 1)[0] == ayah]
        contexts[ayah].sort(key=lambda record: int(record["location"].split(":")[2]))
    report = {"baseline": BASELINE, "scope": "First bounded Arabic-led semantic review; four ayahs revised, two additional ayahs inspected and deferred.",
              "summary": {"changed_values": len(seen), "groups": len(groups), "revised_ayahs": 4,
                          "resolved_construction_flags": 2, "resolved_existing_semantic_flags": 2,
                          "turkish_before_sha256": hashlib.sha256(source).hexdigest(), "turkish_after_sha256": hashlib.sha256(output).hexdigest()},
              "decisions": decisions, "groups": groups, "original_contexts": contexts, "follow_up": follow_up}
    write("reports/semantic-review-001.json", report)
    if args.apply:
        original_queue = committed("reports/linguistic-review-current.json")
        queue = json.loads(original_queue)
        resolved = {key for decision in decisions for key in decision.get("resolved_semantic_keys", [])}
        for entry in queue:
            key = entry["key"]
            entry["turkish"] = after[key]
            if key in resolved:
                entry["status"] = "reviewed_with_changes"
                entry["currently_context_only"] = False
                entry["history"].append({"manifest": "semantic-review-001.json", "reason": "Arabic-led relative-construction review completed for this flagged key; explicit Turkish source contribution restored."})
        assert read_report("linguistic-review-current.json") in (json.loads(original_queue), queue), "Unexpected semantic queue edits."
        original_concerns = committed("reports/grammar-construction-review.json")
        assert read_report("grammar-construction-review.json") in (json.loads(original_concerns), []), "Unexpected construction queue edits."
        (ROOT / "turkish-wbw-translation.json").write_bytes(output)
        write("reports/linguistic-review-current.json", queue)
        write("reports/grammar-construction-review.json", [])
    assert inventory() == original_hashes
    print(json.dumps(report["summary"], indent=2))

if __name__ == "__main__":
    main()
