"""Apply the recorded alignment manifest and independently verify its scope."""
import hashlib
import json
import re

from alignment_common import ROOT, load_baseline, render

en, baseline = load_baseline()
manifest = json.loads((ROOT / "reports/contextual-alignment-changes.json").read_text(encoding="utf-8"))
updates = {}
for group in manifest["groups"]:
    assert group["before"] == {k: baseline.get(k) for k in group["members"]}
    assert group["shared_expression"] == " ".join(baseline[k].replace("(", "[").replace(")", "]") for k in group["expression_origins"])
    for key in group["members"]:
        assert key not in updates and key in en
        assert group["after"][key] == render(group["parts"], key)
        assert not re.fullmatch(r"\(\d+\)", en[key])
        updates[key] = group["after"][key]
expected = baseline | updates
expected = {k: expected[k] for k in en if k in expected}
assert updates["2:5:4"] == "(Rableri)nden"
assert updates["2:5:5"] == "Rableri(nden)"
assert "2:217:3" not in updates
assert "2:48:4" not in updates
path = ROOT / "turkish-wbw-translation.json"
current = json.loads(path.read_bytes())
assert current == baseline or current == expected, "Unexpected working-tree edits; refusing to overwrite."
output = (json.dumps(expected, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
path.write_bytes(output)
assert json.loads(path.read_bytes()) == expected
assert [k for k in en if k in expected] == list(expected)
assert all(expected[k] == v for k, v in baseline.items() if k not in updates)
assert all(expected[k] == en[k] for k in en if re.fullmatch(r"\(\d+\)", en[k]))
assert len(expected) - len(baseline) == manifest["summary"]["added_keys"]
assert len(en.keys() - expected.keys()) == manifest["summary"]["remaining_missing_keys"]
load_baseline()  # Recheck immutable English bytes after writing Turkish.
result = {"turkish_after_sha256": hashlib.sha256(output).hexdigest(),
          "turkish_entries": len(expected), "checks": "Manifest reconstruction, untouched pairs, markers, reference order, exact example, exclusions, and unchanged English passed."}
(ROOT / "reports/contextual-alignment-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
