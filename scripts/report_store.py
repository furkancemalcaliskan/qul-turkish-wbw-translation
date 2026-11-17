"""Keep current review data and validation results in two consolidated JSON files."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
STATE = REPORTS / "review-state.json"
VALIDATION = REPORTS / "validation.json"
STATE_KEYS = {
    "linguistic-review-current.json": "queue",
    "grammar-construction-review.json": "construction_flags",
}
VALIDATION_KEYS = {
    "resource-audit.json": "resources",
    "missing-summary.json": "structure",
    "semantic-review-001-validation.json": "semantic_review_001",
}

def unique(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON key: {key}"
        result[key] = value
    return result

def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)

def save(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2)+"\n").encode("utf-8"))

def read_report(name):
    if name in STATE_KEYS:
        return load(STATE)[STATE_KEYS[name]]
    if name.startswith("semantic-review-") and name.endswith(".json") and not name.endswith("-validation.json"):
        return load(STATE)["batches"][name.removesuffix(".json")]
    if name in VALIDATION_KEYS:
        return load(VALIDATION)[VALIDATION_KEYS[name]]
    raise FileNotFoundError(f"Historical report {name!r} is no longer in the working tree. Read it from its matching Git commit; see PROCESS.md.")

def write_report(name, value):
    if name in STATE_KEYS:
        state = load(STATE)
        state[STATE_KEYS[name]] = value
        save(STATE, state)
    elif name.startswith("semantic-review-") and name.endswith(".json") and not name.endswith("-validation.json"):
        state = load(STATE)
        state["batches"][name.removesuffix(".json")] = value
        save(STATE, state)
    elif name in VALIDATION_KEYS:
        results = load(VALIDATION)
        results[VALIDATION_KEYS[name]] = value
        save(VALIDATION, results)
    else:
        raise ValueError(f"No consolidated destination configured for {name!r}.")
