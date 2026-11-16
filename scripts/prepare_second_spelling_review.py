"""Record the second review against the frozen first-pass reconstruction."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def read(name):
    return json.loads((ROOT / name).read_bytes())
snapshot = read("reports/spelling-second-pass-start.json")
before = json.loads(subprocess.check_output(["git", "show", snapshot["baseline"]+":turkish-wbw-translation.json"], cwd=ROOT))
before.update(snapshot["first_pass_changes"])
before_bytes = (json.dumps(before, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
assert hashlib.sha256(before_bytes).hexdigest() == snapshot["turkish_sha256"]
after = read("turkish-wbw-translation.json")
en = read("english-wbw-translation.json")
assert list(before) == list(after) == list(en)
assert hashlib.sha256((ROOT / "english-wbw-translation.json").read_bytes()).hexdigest() == snapshot["english_sha256"]
combined = read("reports/spelling-changes.json")
combined_entries = {entry["key"]: entry for entry in combined["entries"]}
entries = []
for key, value in before.items():
    if value == after[key]:
        continue
    assert combined_entries[key]["after"] == after[key]
    revised = key in snapshot["first_pass_changes"]
    reason = ("Move a previously inserted word-boundary space outside the opening parenthesis; preserve the earlier lexical correction."
              if revised else "Apply the additionally reviewed spelling or grammar correction; see the combined manifest for the exact rule or construction rationale.")
    entries.append({"key": key, "english": en[key], "before": value, "after": after[key],
                    "already_edited_in_first_pass": revised, "reason": reason,
                    "combined_manifest_reasons": combined_entries[key]["changes"]})
report = {
    "first_pass_snapshot": "spelling-second-pass-start.json",
    "candidate_inputs": ["second-review-candidates.json", "second-review-repeated-candidates.json"],
    "scope": "Second spelling/grammar review; corpus similarity only generates candidates and never automatically selects replacements.",
    "summary": {"changed_entries_this_pass": len(entries),
                "previously_edited_entries_reformatted": sum(entry["already_edited_in_first_pass"] for entry in entries),
                "cumulative_changed_entries": len(combined_entries), "added_keys": 0, "removed_keys": 0,
                "turkish_before_sha256": hashlib.sha256(before_bytes).hexdigest(),
                "turkish_after_sha256": hashlib.sha256((ROOT / "turkish-wbw-translation.json").read_bytes()).hexdigest(),
                "english_sha256": snapshot["english_sha256"]},
    "entries": entries,
}
(ROOT / "reports/spelling-second-pass-changes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
with (ROOT / "reports/spelling-second-pass-changes.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.writer(handle)
    writer.writerow(["key", "english", "first_pass_value", "second_pass_value", "previously_edited", "reason"])
    for entry in entries:
        writer.writerow([entry["key"], entry["english"], entry["before"], entry["after"], entry["already_edited_in_first_pass"], entry["reason"]])
print(json.dumps(report["summary"], indent=2))
