"""Find corpus-based spelling candidates; similarity alone never authorizes edits."""
import collections
import json
import re
import sys
import hashlib
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
snapshot_path = ROOT / "reports/spelling-second-pass-start.json"
if snapshot_path.exists():
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    tr = json.loads(subprocess.check_output(["git", "show", snapshot["baseline"]+":turkish-wbw-translation.json"], cwd=ROOT))
    tr.update(snapshot["first_pass_changes"])
    raw = (json.dumps(tr, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    assert hashlib.sha256(raw).hexdigest() == snapshot["turkish_sha256"]
else:
    tr = json.loads((ROOT / "turkish-wbw-translation.json").read_text(encoding="utf-8"))
en = json.loads((ROOT / "english-wbw-translation.json").read_text(encoding="utf-8"))
token = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*")
locations = collections.defaultdict(list)
for key, value in tr.items():
    for word in set(token.findall(value.replace("(", "").replace(")", ""))):
        locations[word].append(key)
repeated = "--repeated" in sys.argv
common = {word for word, keys in locations.items() if len(keys) >= (25 if repeated else 15) and len(word) >= 5}
deletions = collections.defaultdict(set)
for word in common:
    for i in range(len(word)):
        deletions[word[:i]+word[i+1:]].add(word)
rows = []
for word, keys in locations.items():
    if not ((3 <= len(keys) <= 10) if repeated else (len(keys) <= 2)) or len(word) < 5:
        continue
    candidates = set(deletions.get(word, set()))
    for i in range(len(word)):
        shorter = word[:i]+word[i+1:]
        if shorter in common:
            candidates.add(shorter)
        candidates.update(deletions.get(shorter, set()))
    for i in range(len(word)-1):
        swapped = word[:i]+word[i+1]+word[i]+word[i+2:]
        if swapped in common:
            candidates.add(swapped)
    candidates.discard(word)
    if not candidates:
        continue
    row = {"token": word, "occurrences": len(keys),
           "similar_tokens": sorted(candidates, key=lambda item: (-len(locations[item]), item)),
           "entries": [{"key": key, "turkish": tr[key], "english": en[key]} for key in keys],
           "status": "candidate_only_not_a_confirmed_error"}
    rows.append(row)
rows.sort(key=lambda row: (-max(len(locations[item]) for item in row["similar_tokens"]), row["token"]))
filename = "second-review-repeated-candidates.json" if repeated else "second-review-candidates.json"
(ROOT / "reports" / filename).write_text(json.dumps(rows, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print("Candidates:", len(rows))
for row in rows:
    print(row["token"], "=>", ", ".join(row["similar_tokens"][:3]), "|", "; ".join(entry["key"]+" "+entry["turkish"]+" / "+entry["english"] for entry in row["entries"]))
