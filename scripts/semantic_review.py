"""Replay recorded semantic batches and verify exact data and review provenance."""
import hashlib
import json
import re
import subprocess
from collections import Counter

from audit_resources import MANIFEST, RESOURCES, inventory, read
from report_store import ROOT, STATE, VALIDATION, load, save
from alignment_common import render


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def baseline():
    return json.loads(subprocess.check_output(
        ["git", "show", "661144b:turkish-wbw-translation.json"], cwd=ROOT))


def replay(state, through=None):
    current = baseline()
    for name, batch in state["batches"].items():
        assert digest(current) == batch["summary"]["turkish_before_sha256"], name
        touched = set()
        for group in batch["groups"]:
            assert set(group["members"]) == set(group["before"]) == set(group["after"])
            assert not touched.intersection(group["members"]), group["id"]
            assert group["before"] == {key: current[key] for key in group["members"]}
            assert group["reason"].strip()
            touched.update(group["members"])
            current.update(group["after"])
        assert len(touched) == batch["summary"]["changed_values"], name
        assert digest(current) == batch["summary"]["turkish_after_sha256"], name
        if name == through:
            return current
    return current


class ReviewBatch:
    """Build a review from explicit human-selected locations, never bulk-approve a scan."""

    def __init__(self, name, scope):
        self.name, self.scope = name, scope
        self.state = load(STATE)
        self.exists = name in self.state["batches"]
        self.before = replay(self.state)
        assert (ROOT / "turkish-wbw-translation.json").read_bytes() == encoded(self.before)
        self.ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
        self.en = read(RESOURCES / "english/english-wbw-translation.json")
        self.groups, self.decisions, self.touched = [], [], set()
        self.references, self.follow_up = [], []
        self.extra_ayahs = []

    def change(self, identifier, values, reason, parts=None):
        values = {key: value for key, value in values.items() if value != self.before[key]}
        if not values:
            return
        assert not self.touched.intersection(values), identifier
        self.touched.update(values)
        group = {"id": identifier, "members": list(values), "before": {key: self.before[key] for key in values},
                 "after": values, "arabic": {key: self.ar[key]["text"] for key in values},
                 "english": {key: self.en[key] for key in values}, "reason": reason,
                 "source_role_note": "Round parentheses identify shared source context. Current notation excludes square brackets; historical batches retain their original notation for exact replay. No translation keys are added."}
        if parts:
            group.update(parts=parts, shared_expression="".join(part["text"] for part in parts))
        self.groups.append(group)

    def phrase(self, identifier, pieces, reason):
        parts = [{"text": text, "role": key or "context"} for text, key in pieces]
        members = list(dict.fromkeys(part["role"] for part in parts if part["role"] != "context"))
        self.change(identifier, {key: render(parts, key) for key in members}, reason, parts)

    def decide(self, key, reason, retained=False, reassessment=False):
        entry = next(entry for entry in self.state["queue"] if entry["key"] == key)
        assert entry["status"] == "requires_semantic_review" or reassessment, key
        assert key not in {key for decision in self.decisions for key in decision["resolved_semantic_keys"]}
        self.decisions.append({"ayah": key.rsplit(":", 1)[0], "status": "retained" if retained else "revised",
                               "resolved_semantic_keys": [key], "reason": reason,
                               "reassessment": reassessment, "prior_status": entry["status"],
                               "scope": "This flagged construction only; other lexical or interpretive choices in the ayah are not certified."})

    def finish(self, apply=False):
        after = self.before.copy()
        for group in self.groups:
            after.update(group["after"])
        ayahs = list(dict.fromkeys([decision["ayah"] for decision in self.decisions] +
                                  [key.rsplit(":", 1)[0] for key in self.touched] + self.extra_ayahs))
        contexts = {}
        for ayah in ayahs:
            contexts[ayah] = [{"location": key, "arabic": value["text"], "english": self.en.get(key), "turkish_before": self.before.get(key)}
                              for key, value in self.ar.items() if key.rsplit(":", 1)[0] == ayah]
            contexts[ayah].sort(key=lambda record: int(record["location"].split(":")[-1]))
        batch = {"baseline": next(reversed(self.state["batches"])), "scope": self.scope,
                 "summary": {"changed_values": len(self.touched), "groups": len(self.groups), "reviewed_ayahs": len(ayahs),
                             "resolved_existing_semantic_flags": sum(not decision.get("reassessment") for decision in self.decisions),
                             "reassessed_semantic_flags": sum(bool(decision.get("reassessment")) for decision in self.decisions),
                             "turkish_before_sha256": digest(self.before),
                             "turkish_after_sha256": digest(after)},
                 "groups": self.groups, "decisions": self.decisions, "original_contexts": contexts,
                 "comparison_sources": self.references, "follow_up": self.follow_up,
                 "reference_basis": "Original immutable QUL Arabic word records and supplied English, read with local clause context; explicit locations selected individually."}
        print(json.dumps(batch["summary"], indent=2))
        if not apply:
            return
        assert inventory() == read(MANIFEST)["files"]
        self.state["batches"][self.name] = batch
        for decision in self.decisions:
            key = decision["resolved_semantic_keys"][0]
            entry = next(entry for entry in self.state["queue"] if entry["key"] == key)
            entry["status"] = "reviewed_retained" if decision["status"] == "retained" else "reviewed_with_changes"
            entry["history"].append({"manifest": self.name + ".json", "reason": decision["reason"]})
            entry["currently_context_only"] = bool(re.fullmatch(r"\([^()]*\)", after[key]))
        for entry in self.state["queue"]:
            entry["turkish"] = after[entry["key"]]
        save(STATE, self.state)
        (ROOT / "turkish-wbw-translation.json").write_bytes(encoded(after))
        validate()


def validate():
    state = load(STATE)
    en = read(RESOURCES / "english/english-wbw-translation.json")
    ar = read(RESOURCES / "arabic/qpc-hafs-word-by-word.json")
    assert inventory() == read(MANIFEST)["files"]
    assert en == json.loads(subprocess.check_output(
        ["git", "show", "4503cdc:english-wbw-translation.json"], cwd=ROOT))
    current = baseline()
    old_queue = json.loads(subprocess.check_output(
        ["git", "show", "661144b:reports/linguistic-review-current.json"], cwd=ROOT))
    queue_by_key = {entry["key"]: entry for entry in state["queue"]}
    assert len(queue_by_key) == len(old_queue) == len(state["queue"]) == 831
    assert [entry["key"] for entry in state["queue"]] == [entry["key"] for entry in old_queue]
    expected_histories = {entry["key"]: list(entry["history"]) for entry in old_queue}
    expected_status = {entry["key"]: entry["status"] for entry in old_queue}
    for name, batch in state["batches"].items():
        for ayah, records in batch["original_contexts"].items():
            keys = sorted((key for key in ar if key.rsplit(":", 1)[0] == ayah), key=lambda key: int(key.split(":")[-1]))
            assert [record["location"] for record in records] == keys
            for record in records:
                key = record["location"]
                assert record["arabic"] == ar[key]["text"]
                assert record["english"] == en.get(key)
                assert record["turkish_before"] == current.get(key)
        for group in batch["groups"]:
            assert group["english"] == {key: en[key] for key in group["members"]}
            assert group["arabic"] == {key: ar[key]["text"] for key in group["members"]}
            for key in group["members"]:
                assert group["before"][key] != group["after"][key], key
            if "parts" in group:
                assert all(part["role"] == "context" or part["role"] in en for part in group["parts"])
                shared = "".join(part["text"] for part in group["parts"])
                assert shared == group["shared_expression"]
                for key, value in group["after"].items():
                    assert value.replace("(", "").replace(")", "") == shared
                    level, visible = 0, []
                    for char in value:
                        if char == "(": level += 1
                        elif char == ")": level -= 1
                        elif not level: visible.append(char)
                        assert level in (0, 1)
                    expected = "".join(part["text"] for part in group["parts"] if part["role"] == key)
                    assert "".join("".join(visible).split()) == "".join(expected.split()), key
            else:
                assert group.get("source_role_note"), group["id"]
        for decision in batch["decisions"]:
            for key in decision.get("resolved_semantic_keys", []):
                assert expected_status[key] == "requires_semantic_review" or decision.get("reassessment"), key
                if "prior_status" in decision:
                    assert decision["prior_status"] == expected_status[key], key
                status = decision.get("status", "revised")
                expected_status[key] = "reviewed_retained" if status == "retained" else "reviewed_with_changes"
                event = {"manifest": name + ".json", "reason": decision.get("reason", "Arabic-led relative-construction review completed for this flagged key; explicit Turkish source contribution restored.")}
                expected_histories[key].append(event)
        current = replay(state, through=name)
    raw = (ROOT / "turkish-wbw-translation.json").read_bytes()
    assert raw == encoded(current)
    if "semantic-review-012" in state["batches"]:
        assert all("[" not in value and "]" not in value for value in current.values()), "Square delimiters are forbidden in current Turkish values."
    assert list(current) == list(en) and len(current) == 83665
    assert all(isinstance(value, str) and value and value == value.strip() for value in current.values())
    markers = {key: value for key, value in en.items() if re.fullmatch(r"\(\d+\)", value)}
    assert len(markers) == 6236 and all(current[key] == value for key, value in markers.items())
    for key, value in current.items():
        stack = []
        for char in value:
            if char in "([": stack.append(char)
            elif char in ")]": assert stack and stack.pop() == {")": "(", "]": "["}[char], key
        assert not stack, key
    for old, entry in zip(old_queue, state["queue"]):
        key = entry["key"]
        assert entry["history"] == expected_histories[key], key
        assert entry["status"] == expected_status[key], key
        assert entry["turkish"] == current[key], key
        assert entry["english"] == en[key]
        assert entry["turkish_before_spelling_review"] == old["turkish_before_spelling_review"]
        if entry["status"] != "requires_semantic_review":
            assert entry["currently_context_only"] == bool(re.fullmatch(r"\([^()]*\)", current[key]))
    assert state["construction_flags"] == []
    result = {"batches": list(state["batches"]), "exact_replay_and_untouched_values": "passed",
              "arabic_and_english_provenance": "passed", "source_role_and_delimiter_checks": "passed",
              "reference_keys": len(current), "ayah_markers": len(markers), "resource_hashes_unchanged": True,
              "english_reference_pairs_equal_initial": True, "queue_records": len(state["queue"]),
              "queue_statuses": dict(Counter(entry["status"] for entry in state["queue"])),
              "pending_semantic_flags": sum(entry["status"] == "requires_semantic_review" for entry in state["queue"]),
              "net_changed_values_since_baseline": sum(current[key] != value for key, value in baseline().items()),
              "turkish_sha256": digest(current),
              "scope": "Exact recorded changes and decision history; not linguistic certification of unreviewed words or ayahs."}
    results = load(VALIDATION)
    results["semantic_review"] = result
    save(VALIDATION, results)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    validate()
