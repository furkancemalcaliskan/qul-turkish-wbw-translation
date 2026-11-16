"""Export the correction ledger and preserve unresolved construction concerns."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))
def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

tr = read("turkish-wbw-translation.json")
en = read("english-wbw-translation.json")
changes = read("reports/spelling-changes.json")
changed = {entry["key"]: entry for entry in changes["entries"]}
with (ROOT / "reports/spelling-changes.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["key", "english", "before", "after", "reasons"])
    for entry in changes["entries"]:
        writer.writerow([entry["key"], entry["english"], entry["before"], entry["after"], " | ".join(item["reason"] for item in entry["changes"])])

concerns = []
pattern = re.compile(r"her-ten|her-den|bin-dan|hangi-den|Tur-i-dan|Mescid-i-dan|yürüyen-dan|başka-tan|kötü-dan|bu-den|Salihler-den|da-Salihler|şeyta\)|^-tan$|^\(-tan\)$|^\(-ten\)$|^-dandır$")
for key, value in tr.items():
    if not pattern.search(value):
        continue
    chapter, verse, word = map(int, key.split(":"))
    context = []
    for position in range(max(1, word-1), word+3):
        other = f"{chapter}:{verse}:{position}"
        if other in tr:
            context.append({"key": other, "english": en[other], "turkish": tr[other]})
    concerns.append({
        "key": key, "english": en[key], "turkish": value,
        "status": "requires_construction_review",
        "reason": "Inherited malformed or isolated suffix display, displaced wording, or incomplete pronoun annotation. A spelling-only substitution cannot establish the complete expression and each source role. Review the Arabic position and neighboring Turkish expression before replacing it.",
        "context": context,
    })
write("reports/grammar-construction-review.json", concerns)

current = read("reports/linguistic-review.json")
for entry in current:
    key = entry["key"]
    entry["turkish_before_spelling_review"] = entry["turkish"]
    entry["turkish"] = tr[key]
    entry["spelling_review_changed_value"] = key in changed
    if key in changed:
        entry["history"].append({"manifest": "spelling-changes.json", "reason": "Orthographic changes applied; the previous semantic-review concern is not automatically resolved."})
write("reports/linguistic-review-current.json", current)
print(json.dumps({"correction_entries": len(changed), "construction_review_entries": len(concerns), "semantic_review_entries": len(current)}, indent=2))
